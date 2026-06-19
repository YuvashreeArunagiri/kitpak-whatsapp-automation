from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os
import io
import json
import re
import base64
import urllib.request
from dotenv import load_dotenv
from claude_service import get_claude_reply, extract_order_details, classify_image, extract_payment_info
from wati_service import send_whatsapp_message, send_whatsapp_template, send_product_images, send_whatsapp_pdf
from pi_service import generate_pi_text, generate_pi_pdf
from image_service import get_images_from_message, get_product_key_from_message, get_images_for_product, get_price_chart_images, is_price_request
from sheets_service import append_daily_report, append_order_to_sheet, append_handoff_to_sheet, append_bulk_enquiry_to_sheet, generate_order_id
import threading
import time

load_dotenv()

app = Flask(__name__)

conversation_history = {}
processed_message_ids = set()
pending_orders = {}  # phone -> {'total': amount}

# Words that indicate the customer wants to see a photo/picture of a product
PICTURE_REQUEST_WORDS = ['picture', 'photo', 'photos', 'pictures', 'image', 'images', 'reference', 'sample', 'pic ', 'pics']

# Phrases that indicate Claude handed off to the team
HANDOFF_PHRASES = [
    'our team will get in touch',
    'our team will contact you',
    'our team will reach out',
    'our team will call you',
    'our team will get back',
    'our team will prepare the mockup',
    'our team will prepare a mockup',
    'team will prepare the mockup',
    'team will prepare a mockup',
    'our team will send you',
    'our team will share',
]

# Keywords that suggest bulk order context
BULK_KEYWORDS = ['5000', '10000', '15000', '20000', '50000', '1 lakh', 'bulk order', 'large order', 'bulk quantity']
CUSTOM_BULK_KEYWORDS = ['above 1000', 'more than 1000', '2000', '3000', '4000', '5000']


def daily_report_scheduler():
    """Background thread — sends daily report to Google Sheets at 6 PM IST."""
    from datetime import timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    while True:
        now = datetime.now(IST)
        if now.hour == 18 and now.minute == 0:
            print("[KITPAK] Sending daily report to Google Sheets...")
            append_daily_report(conversation_history)
            send_owner_alert(f"Daily report sent to Google Sheets. Total conversations today: {len(conversation_history)}")
            time.sleep(61)
        time.sleep(30)

scheduler_thread = threading.Thread(target=daily_report_scheduler, daemon=True)
scheduler_thread.start()

pending_logo = {}
custom_order_state = {}

OWNER_NUMBER = "918300475706"
KITPAK_UPI_ID = os.environ.get("KITPAK_UPI_ID", "9489501487@okbizaxis")
SHEET_AUTOMATION_SECRET = os.environ.get('SHEET_AUTOMATION_SECRET', '')


def send_owner_alert(message: str) -> bool:
    """
    Send alert to owner. Tries session message first,
    falls back to kitpak_owner_alert template if session expired.
    """
    sent = send_whatsapp_message(OWNER_NUMBER, message)
    if sent:
        return True
    print(f"[KITPAK] Session message failed for owner — trying template fallback")
    sent = send_whatsapp_template(OWNER_NUMBER, "kitpak_owner_alert", [message])
    return sent


def extract_context_from_history(phone: str) -> dict:
    """
    Extract useful context (name, product, quantity, state) from conversation history.
    Used for logging handoffs and bulk enquiries.
    """
    history = conversation_history.get(phone, [])
    full_text = ' '.join([m.get('content', '') for m in history]).lower()

    # Extract customer name (look for name patterns in history)
    customer_name = ''
    for msg in history:
        content = msg.get('content', '')
        # Name is usually in user messages after address sharing
        if msg.get('role') == 'user' and len(content) > 3 and '\n' not in content and len(content) < 50:
            # Heuristic: short user messages before address block might be the name
            pass

    # Extract quantity mentioned
    quantity = ''
    qty_match = re.search(r'(\d[\d,]*)\s*(pcs|pieces|nos|units|rolls|sleeves)', full_text)
    if qty_match:
        quantity = qty_match.group(1).replace(',', '')

    # Extract product keywords
    product = ''
    product_keywords = [
        'white cover', 'colour cover', 'color cover', 'black cover', 'pink cover', 'purple cover',
        'custom printed', 'printed cover', 'honeycomb', 'kraft', 'paper bag', 'thermal label',
        'amazon', 'flipkart', 'meesho', 'transparent cover', 'mailer bag', 'courier cover'
    ]
    for kw in product_keywords:
        if kw in full_text:
            product = kw
            break

    # Extract state (look for common Indian states in history)
    state = ''
    states = ['tamil nadu', 'karnataka', 'kerala', 'andhra pradesh', 'telangana', 'maharashtra',
              'delhi', 'gujarat', 'rajasthan', 'uttar pradesh', 'west bengal', 'punjab']
    for s in states:
        if s in full_text:
            state = s.title()
            break

    return {
        'customer_name': customer_name,
        'product': product,
        'quantity': quantity,
        'state': state
    }


def is_bulk_enquiry(phone: str, message_text: str, reply: str) -> tuple:
    """
    Detect if this is a bulk enquiry based on conversation context.
    Returns (is_bulk: bool, reason: str)
    """
    full_history = ' '.join([m.get('content', '') for m in conversation_history.get(phone, [])]).lower()

    # Check for quantities — with or without unit suffix
    is_custom = 'custom' in full_history and ('printed' in full_history or 'print' in full_history)
    qty_patterns = [
        r'(\d[\d,]*)\s*(pcs|pieces|nos|units|covers|bags|rolls|sleeves)',
        r'(\d{4,})',
    ]
    for pattern in qty_patterns:
        for match in re.finditer(pattern, full_history):
            try:
                qty = int(match.group(1).replace(',', ''))
                if qty > 5000:
                    return True, f"Bulk quantity: {qty} pcs"
                if is_custom and qty > 1000:
                    return True, f"Custom print bulk order: {qty} pcs"
            except ValueError:
                pass

    # Check for bulk keywords in message or history
    for kw in BULK_KEYWORDS:
        if kw in full_history or kw in message_text.lower():
            return True, f"Bulk keyword detected: '{kw}'"

    # Check for custom print above 1000
    if 'custom' in full_history and ('printed' in full_history or 'print' in full_history):
        for kw in CUSTOM_BULK_KEYWORDS:
            if kw in full_history:
                return True, f"Custom print bulk order: quantity '{kw}'"

    return False, ''


def is_handoff(reply: str) -> bool:
    """Check if Claude's reply is a team-handoff response."""
    reply_lower = reply.lower()
    return any(phrase in reply_lower for phrase in HANDOFF_PHRASES)


# ─── Team keyword commands ───────────────────────────────────
def handle_team_command(phone: str, message: str) -> bool:
    msg = message.strip().upper()

    if msg.startswith("CONFIRM "):
        # Payment confirmation now ONLY happens via Google Sheet (OrderTracking tab).
        # This WhatsApp command is disabled to prevent premature confirmation messages.
        send_owner_alert(
            "Note: CONFIRM via WhatsApp is disabled. "
            "Please update Payment Status to CONFIRMED in the OrderTracking Google Sheet instead — "
            "this will automatically send the confirmation message to the customer.")
        return True

    if msg.startswith("DISPATCH "):
        parts = message.strip().split(" ", 2)
        if len(parts) >= 2:
            customer_phone = parts[1].strip().replace("+", "").replace(" ", "")
            if not customer_phone.startswith("91"):
                customer_phone = "91" + customer_phone
            tracking = parts[2].strip() if len(parts) > 2 else "Will be updated shortly"
            send_whatsapp_message(customer_phone,
                f"Your order has been dispatched!\n\n"
                f"Tracking Number: {tracking}\n\n"
                f"You can track your order using the above number. "
                f"Expected delivery in 3-5 business days. "
                f"Thank you for choosing KITPAK!")
            send_owner_alert(f"Done! Dispatch details sent to {customer_phone}.")
        return True

    if msg.startswith("CANCEL "):
        customer_phone = message.strip().split(" ", 1)[1].strip().replace("+", "").replace(" ", "")
        if not customer_phone.startswith("91"):
            customer_phone = "91" + customer_phone
        send_whatsapp_message(customer_phone,
            "We regret to inform you that your order could not be processed. "
            "Please contact us for further assistance. "
            "We apologise for the inconvenience.")
        send_owner_alert(f"Done! Cancellation sent to {customer_phone}.")
        return True

    if msg == "HELP":
        send_owner_alert(
            "KITPAK Team Commands:\n\n"
            "Payment confirmation: Update Payment Status to CONFIRMED in the OrderTracking Google Sheet (NOT via WhatsApp)\n"
            "DISPATCH <phone> <tracking> — Send dispatch details\n"
            "CANCEL <phone> — Cancel order\n\n"
            "Example:\n"
            "DISPATCH 9876543210 ST123456789")
        return True

    return False


def download_wati_file(file_url: str) -> bytes:
    """Download a file from WATI media URL."""
    wati_api_token = os.environ.get('WATI_API_TOKEN', '')

    try:
        response = requests.get(
            file_url,
            headers={'Authorization': f'Bearer {wati_api_token}', 'Accept': '*/*'},
            timeout=15,
            allow_redirects=True
        )
        if response.status_code == 200:
            return response.content
        print(f"[KITPAK] File download status: {response.status_code}")
    except Exception as e:
        print(f"[KITPAK] File download error (requests): {e}")

    try:
        response = requests.get(file_url, timeout=15, allow_redirects=True)
        if response.status_code == 200:
            return response.content
        print(f"[KITPAK] File download (no auth) status: {response.status_code}")
    except Exception as e:
        print(f"[KITPAK] File download error (no auth): {e}")

    try:
        req = urllib.request.Request(
            file_url,
            headers={'Authorization': f'Bearer {wati_api_token}', 'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read()
    except Exception as e:
        print(f"[KITPAK] File download error (urllib): {e}")

    return None


def get_bag_colour_from_history(phone: str) -> str:
    history = conversation_history.get(phone, [])
    for msg in reversed(history):
        content = msg.get('content', '').lower()
        for colour in ['black', 'pink', 'purple', 'white']:
            if colour in content:
                return colour
    return 'white'


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print(f"[KITPAK] Payload: {data}")

        if not data:
            return jsonify({'status': 'no data'}), 200

        phone = (data.get('waId') or data.get('from') or '')
        msg_type = data.get('type', 'text')

        message_text = ''
        if data.get('text') and isinstance(data.get('text'), dict):
            message_text = data['text'].get('body', '')
        elif data.get('text') and isinstance(data.get('text'), str):
            message_text = data['text']
        elif data.get('body'):
            message_text = data['body']
        message_text = message_text.strip()

        if not phone:
            return jsonify({'status': 'ignored'}), 200

        event_type = data.get('eventType', '')
        owner = data.get('owner', False)

        if owner:
            return jsonify({'status': 'ignored'}), 200
        if event_type != 'message':
            return jsonify({'status': 'ignored'}), 200

        # ── Stop bot if conversation is assigned to a human agent ──
        assigned_id = data.get('assignedId')
        operator_name = data.get('operatorName')
        if assigned_id or operator_name:
            print(f'[KITPAK] Conversation assigned to human ({operator_name or assigned_id}) — bot skipping')
            return jsonify({'status': 'ignored_assigned'}), 200

        # ── Ignore stale/replayed messages (older than 2 minutes) ──
        msg_timestamp = data.get('timestamp')
        if msg_timestamp:
            try:
                age_seconds = time.time() - int(msg_timestamp)
                if age_seconds > 300:
                    print(f"[KITPAK] Ignoring stale message (age {int(age_seconds)}s): {data.get('text')}")
                    return jsonify({'status': 'ignored_stale'}), 200
            except (ValueError, TypeError):
                pass

        # ── Deduplicate ──
        message_id = data.get('id', '') or data.get('whatsappMessageId', '')
        if message_id and message_id in processed_message_ids:
            print(f"[KITPAK] Duplicate message ignored: {message_id}")
            return jsonify({'status': 'ignored'}), 200
        if message_id:
            processed_message_ids.add(message_id)
            if len(processed_message_ids) > 1000:
                processed_message_ids.clear()

        # ── Team command from owner number ──
        if phone == OWNER_NUMBER and message_text:
            if handle_team_command(phone, message_text):
                return jsonify({'status': 'ok'}), 200

        # ── Handle file uploads (logo or payment screenshot) ──
        if msg_type in ['image', 'document']:
            if phone not in conversation_history:
                conversation_history[phone] = []

            file_url = None
            if msg_type == 'image':
                file_url = (data.get('data') or
                           (data.get('image') or {}).get('link') or
                           (data.get('image') or {}).get('url'))
            elif msg_type == 'document':
                file_url = (data.get('data') or
                           (data.get('document') or {}).get('link') or
                           (data.get('document') or {}).get('url'))
            print(f"[KITPAK] File URL: {file_url}")

            ext = '.jpg'
            mime_type = 'image/jpeg'
            if msg_type == 'document':
                fname = (data.get('document') or {}).get('fileName', 'file.jpg').lower()
                if fname.endswith('.pdf'):
                    ext = '.pdf'
                    mime_type = 'application/pdf'
                elif fname.endswith('.png'):
                    ext = '.png'
                    mime_type = 'image/png'
                else:
                    ext = '.jpg'
                    mime_type = 'image/jpeg'

            file_bytes = download_wati_file(file_url) if file_url else None

            if file_bytes:
                if ext == '.pdf':
                    file_type = 'logo'
                    print(f"[KITPAK] PDF file received — treating as logo")
                else:
                    file_type = classify_image(file_bytes, mime_type)
                    print(f"[KITPAK] File classified as: {file_type}")

                if file_type == 'unknown':
                    # Cannot classify — ask customer
                    conversation_history[phone].append({'role': 'user', 'content': '[Customer sent a file — type unclear]'})
                    send_whatsapp_message(phone,
                        "Could you let me know — is this a reference image of the product you want, or your logo/design file for printing?")
                elif file_type == 'logo':
                    history_text = ' '.join([m.get('content', '') for m in conversation_history.get(phone, [])])
                    wants_mockup = any(word in history_text.lower() for word in ['mockup', 'mock up', 'sample', 'preview', 'design', 'custom print', 'printed cover', 'custom cover'])

                    conversation_history[phone].append({'role': 'user', 'content': '[Customer sent their logo/design file]'})
                    reply = get_claude_reply(conversation_history[phone][-20:])
                    conversation_history[phone].append({'role': 'assistant', 'content': reply})
                    send_whatsapp_message(phone, reply)

                    if wants_mockup:
                        sender_name = data.get('senderName', phone)
                        send_owner_alert(
                            f"Mockup request from {sender_name} ({phone}). "
                            f"Customer has sent their logo/design file — please prepare the mockup and share it with them.")
                        print(f"[KITPAK] Mockup request alerted to owner for {phone}")
                        # Log to HandoffConversations
                        try:
                            append_handoff_to_sheet(
                                phone=phone,
                                customer_name=sender_name,
                                reason='Custom print request — logo file received',
                                last_message='[Customer sent logo/design file]'
                            )
                        except Exception as e:
                            print(f"[KITPAK] Handoff log error (logo): {e}")

                else:
                    print(f"[KITPAK] Payment screenshot received from {phone}")
                    conversation_history[phone].append({'role': 'user', 'content': '[Customer sent a payment screenshot]'})
                    send_whatsapp_message(phone,
                        "Thank you! We have received your payment screenshot. "
                        "Our team will verify and confirm your order shortly.")

                    sender_name = data.get('senderName', phone)
                    payment_info = extract_payment_info(file_bytes, mime_type)
                    extracted_amount = payment_info.get('amount')
                    extracted_upi = payment_info.get('upi_id')
                    pay_status = payment_info.get('status', 'unclear')
                    expected_total = pending_orders.get(phone, {}).get('total')

                    warning_lines = []
                    if expected_total is not None and extracted_amount is not None:
                        if abs(float(extracted_amount) - float(expected_total)) > 0.5:
                            warning_lines.append(f"AMOUNT MISMATCH: Expected Rs.{expected_total:,.2f} but screenshot shows Rs.{extracted_amount:,.2f}")
                    if extracted_upi and KITPAK_UPI_ID not in extracted_upi and extracted_upi not in KITPAK_UPI_ID:
                        warning_lines.append(f"UPI ID MISMATCH: Payment appears to be sent to {extracted_upi}, not our UPI ID")
                    if pay_status in ['failed', 'pending']:
                        warning_lines.append(f"PAYMENT STATUS: Screenshot shows '{pay_status}' — may not be a successful payment")
                    if extracted_amount is None and pay_status == 'unclear':
                        warning_lines.append("Could not read payment details from screenshot — please verify manually")

                    alert_msg = (
                        f"Payment screenshot received from {sender_name} ({phone}).\n"
                        f"Detected amount: Rs.{extracted_amount if extracted_amount is not None else 'Not detected'}\n"
                        f"Expected amount: Rs.{expected_total:,.2f}\n" if expected_total is not None else
                        f"Payment screenshot received from {sender_name} ({phone}).\n"
                        f"Detected amount: Rs.{extracted_amount if extracted_amount is not None else 'Not detected'}\n"
                    )

                    if warning_lines:
                        alert_msg += "\n⚠️ WARNING:\n" + "\n".join(warning_lines) + "\n"
                        alert_msg += f"\nPlease verify carefully before confirming.\nCONFIRM {phone[-10:]}"
                    else:
                        alert_msg += f"\nLooks OK. Please verify and reply:\nCONFIRM {phone[-10:]}"

                    send_owner_alert(alert_msg)

            else:
                send_whatsapp_message(phone, "I had trouble opening that file. Could you please send it again?")

            return jsonify({'status': 'ok'}), 200

        # ── Ignore non-text messages ──
        if msg_type not in ['text', '']:
            return jsonify({'status': 'ignored'}), 200

        if not message_text:
            return jsonify({'status': 'ignored'}), 200

        print(f"[KITPAK] Message from {phone}: {message_text}")

        if phone not in conversation_history:
            conversation_history[phone] = []

        conversation_history[phone].append({'role': 'user', 'content': message_text})

        history = conversation_history[phone][-20:]
        time.sleep(10)
        reply = get_claude_reply(history)

        conversation_history[phone].append({'role': 'assistant', 'content': reply})

        # ── Send price chart image if customer is asking for pricing ──
        if is_price_request(message_text):
            price_images = get_price_chart_images(message_text)
            if price_images:
                send_product_images(phone, price_images)
                print(f"[KITPAK] Price chart image sent to {phone}")

        # ── Send product images if this is a product enquiry or picture request ──
        images = get_images_from_message(message_text)
        picture_requested = any(word in message_text.lower() for word in PICTURE_REQUEST_WORDS)
        matched_via_history = False

        if not images and picture_requested:
            for past_msg in reversed(conversation_history[phone][:-1][-6:]):
                past_product = get_product_key_from_message(past_msg.get('content', ''))
                if past_product:
                    images = get_images_for_product(past_product)
                    matched_via_history = True
                    break

        if images:
            send_product_images(phone, images)
            print(f"[KITPAK] Product images sent to {phone}")

        # ── Send text reply ──
        if 'GENERATE_PI:' in reply:
            send_whatsapp_message(phone, "Thank you! Generating your invoice now, please wait a moment.")
        elif images and matched_via_history:
            friendly_reply = "Here you go! Let me know if you need anything else."
            send_whatsapp_message(phone, friendly_reply)
            conversation_history[phone][-1]['content'] = friendly_reply
        else:
            send_whatsapp_message(phone, reply)
        print(f"[KITPAK] Replied to {phone}: {reply[:80]}")

        # ── Log handoff / bulk enquiry to Google Sheets ──
        if is_handoff(reply):
            sender_name = data.get('senderName', '')
            ctx = extract_context_from_history(phone)
            full_history_text = ' '.join([m.get('content', '') for m in conversation_history.get(phone, [])]).lower()

            # Check if this is a bulk enquiry
            bulk, bulk_reason = is_bulk_enquiry(phone, message_text, reply)
            if bulk:
                try:
                    append_bulk_enquiry_to_sheet(
                        phone=phone,
                        customer_name=sender_name or ctx['customer_name'],
                        product=ctx['product'],
                        quantity=ctx['quantity'],
                        state=ctx['state'],
                        reason=bulk_reason
                    )
                    print(f"[KITPAK] Bulk enquiry logged for {phone}: {bulk_reason}")
                except Exception as e:
                    print(f"[KITPAK] Bulk enquiry log error: {e}")
            else:
                # General handoff — check both message and full history for reason
                try:
                    reason = 'General team handoff'
                    check_text = (message_text + ' ' + full_history_text).lower()
                    if any(w in check_text for w in ['call', 'phone', 'speak', 'talk', 'contact']):
                        reason = 'Customer requested callback'
                    elif any(w in check_text for w in ['return', 'refund', 'damage', 'wrong']):
                        reason = 'Return/Refund request'
                    elif any(w in check_text for w in ['mockup', 'design', 'logo', 'custom print', 'printed cover', 'custom cover']):
                        reason = 'Custom print request'
                    elif any(w in check_text for w in ['kraft', 'paper bag', 'paper cover']):
                        reason = 'Custom kraft/paper bag enquiry'
                    elif any(w in check_text for w in ['honeycomb sleeve', 'sleeve']):
                        reason = 'Honeycomb sleeve enquiry'

                    append_handoff_to_sheet(
                        phone=phone,
                        customer_name=sender_name or ctx['customer_name'],
                        reason=reason,
                        last_message=message_text
                    )
                    print(f"[KITPAK] Handoff logged for {phone}: {reason}")
                except Exception as e:
                    print(f"[KITPAK] Handoff log error: {e}")

        # ── Generate and send PI as PDF ──
        if 'GENERATE_PI:' in reply:
            try:
                order = extract_order_details(reply)
                if order:
                    order_id = generate_order_id(phone)
                    order['order_id'] = order_id
                    pdf_bytes = generate_pi_pdf(order)
                    pdf_sent = send_whatsapp_pdf(
                        phone,
                        pdf_bytes,
                        filename=f"KITPAK_{order_id}.pdf",
                        caption=f"Here is your Proforma Invoice ({order_id}). Please pay via UPI and share the payment screenshot to confirm your order."
                    )
                    order_total = sum(i['qty'] * i['rate'] for i in order.get('items', []))
                    pending_orders[phone] = {'total': order_total, 'order_id': order_id}
                    print(f"[KITPAK] Order {order_id} for {phone}: Rs.{order_total}")

                    try:
                        append_order_to_sheet(phone, order, order_id)
                    except Exception as se:
                        print(f"[KITPAK] Sheets logging error: {se}")

                    if not pdf_sent:
                        pi_text = generate_pi_text(order)
                        send_whatsapp_message(phone, pi_text)
                        print(f"[KITPAK] PI sent as text fallback to {phone}")
                    else:
                        print(f"[KITPAK] PI PDF sent to {phone}")
                else:
                    send_whatsapp_message(phone, "Sorry, I had trouble generating your invoice. Our team will send it to you shortly.")
                    send_owner_alert(f"PI generation failed for {phone} — please send manually.")
            except Exception as e:
                print(f"[KITPAK] PI generation error: {e}")
                import traceback
                traceback.print_exc()

        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        print(f"[KITPAK] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/sheet-notify', methods=['POST'])
def sheet_notify():
    """
    Receives notification requests from Google Sheets Apps Script automation.
    Uses approved WhatsApp templates — works outside the 24-hour session window.
    """
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'no data'}), 400

        if SHEET_AUTOMATION_SECRET and data.get('secret') != SHEET_AUTOMATION_SECRET:
            print("[KITPAK] Sheet-notify: unauthorized request (bad secret)")
            return jsonify({'status': 'error', 'message': 'unauthorized'}), 401

        msg_type = data.get('type')
        phone = str(data.get('phone') or '').strip().replace('+', '').replace(' ', '')
        if phone.endswith('.0'):
            phone = phone[:-2]
        if not phone:
            return jsonify({'status': 'error', 'message': 'missing phone'}), 400
        if not phone.startswith('91'):
            phone = '91' + phone

        customer_name = data.get('customer_name', 'Customer')

        if msg_type == 'payment':
            sent = send_whatsapp_template(phone, 'kitpak_payment_confirmed', [customer_name])
            if not sent:
                sent = send_whatsapp_message(phone,
                    f"Hi {customer_name},\n\n"
                    f"We have received your payment successfully. "
                    f"Your order is now being processed and will be dispatched shortly.\n\n"
                    f"Thank you for choosing KITPAK."
                )

        elif msg_type == 'dispatch':
            tracking = data.get('tracking_number', '')
            courier = data.get('courier_partner', '')
            sent = send_whatsapp_template(phone, 'kitpak_dispatch_notification', [customer_name, courier, tracking])
            if not sent:
                sent = send_whatsapp_message(phone,
                    f"Hi {customer_name},\n\n"
                    f"Your KITPAK order has been dispatched.\n"
                    f"Courier Partner: {courier}\n"
                    f"Tracking Number: {tracking}\n\n"
                    f"You can track your shipment using the above tracking number.\n\n"
                    f"Thank you for choosing KITPAK."
                )
        else:
            return jsonify({'status': 'error', 'message': 'unknown type'}), 400

        print(f"[KITPAK] Sheet-notify ({msg_type}) to {phone}: {'sent' if sent else 'failed'}")
        return jsonify({'status': 'ok' if sent else 'error'}), (200 if sent else 500)

    except Exception as e:
        print(f"[KITPAK] Sheet-notify error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/daily-report', methods=['GET', 'POST'])
def trigger_daily_report():
    try:
        print("[KITPAK] Daily report triggered via cron")
        success = append_daily_report(conversation_history)
        if success:
            send_owner_alert(f"Daily report sent to Google Sheets. Total conversations today: {len(conversation_history)}")
            return jsonify({'status': 'ok', 'message': 'Daily report sent'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send report'}), 500
    except Exception as e:
        print(f"[KITPAK] Daily report trigger error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'KITPAK Abimanyu is live!'}), 200


@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'KITPAK Abimanyu is live!'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
