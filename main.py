import os
import time
import re
import threading
import requests
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify

from claude_service import get_claude_reply, classify_image
from wati_service import send_whatsapp_message, send_whatsapp_template, send_product_images
from sheets_service import append_handoff_to_sheet, append_bulk_enquiry_to_sheet, append_daily_report
from image_service import get_images_from_message, get_product_key_from_message, get_images_for_product, get_price_chart_images, is_price_request

app = Flask(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

# ── In-memory state ──
conversation_history = {}   # phone -> list of messages
processed_message_ids = set()  # dedup set

OWNER_PHONE = os.environ.get('OWNER_PHONE', '918300475706')
KITPAK_UPI_ID = os.environ.get('KITPAK_UPI_ID', '9489501487@okbizaxis')
SHEET_AUTOMATION_SECRET = os.environ.get('SHEET_AUTOMATION_SECRET', 'kitpak_secret_8847xyz')
WATI_API_URL = os.environ.get('WATI_API_URL', '').rstrip('/')
WATI_API_TOKEN = os.environ.get('WATI_API_TOKEN', '')

PICTURE_REQUEST_WORDS = [
    'photo', 'photos', 'picture', 'pictures', 'image', 'images',
    'pic', 'pics', 'show me', 'send me', 'can you send', 'share image',
    'product image', 'cover image', 'bag image', 'see the', 'look like'
]

HANDOFF_PHRASES = [
    'our team will get in touch',
    'our team will contact you',
    'our team will reach out',
    'our team will call you',
    'our team will get back',
    'our team will prepare the mockup',
    'our team will prepare a mockup',
    'our team will send you',
    'our team will share',
    'team will get in touch',
]

BULK_KEYWORDS = [
    '5000', '6000', '7000', '8000', '9000', '10000', '15000', '20000',
    '50000', '1 lakh', 'bulk order', 'large order', 'bulk quantity'
]


# ── Helper: send owner alert ──
def send_owner_alert(message: str):
    try:
        send_whatsapp_template(
            OWNER_PHONE,
            'kitpak_owner_alert',
            [{'name': 'body', 'text': message}]
        )
    except Exception as e:
        print(f"[KITPAK] Owner alert error: {e}")


# ── Helper: extract context from conversation history ──
def extract_context_from_history(phone: str) -> dict:
    ctx = {'customer_name': '', 'product': 'courier covers', 'quantity': 'Not specified', 'state': 'Not specified'}
    for msg in conversation_history.get(phone, []):
        content = msg.get('content', '').lower()
        for product in ['white cover', 'colour cover', 'black cover', 'pink cover', 'purple cover',
                        'honeycomb', 'label', 'thermal', 'meesho', 'flipkart', 'amazon', 'kraft', 'paper bag']:
            if product in content:
                ctx['product'] = product
                break
        qty_match = re.search(r'\b(\d+)\s*(pcs|pieces|covers|bags|rolls)?\b', content)
        if qty_match:
            ctx['quantity'] = qty_match.group(1) + ' pcs'
        for state in ['tamil nadu', 'karnataka', 'kerala', 'delhi', 'maharashtra', 'gujarat']:
            if state in content:
                ctx['state'] = state.title()
                break
    return ctx


# ── Helper: check if reply is a handoff ──
def is_handoff(reply: str) -> bool:
    reply_lower = reply.lower()
    return any(phrase in reply_lower for phrase in HANDOFF_PHRASES)


# ── Helper: check if bulk enquiry ──
def is_bulk_enquiry(phone: str, message_text: str, reply: str) -> tuple:
    full_history = ' '.join([m.get('content', '') for m in conversation_history.get(phone, [])]).lower()
    qty_patterns = [
        r'(\d[\d,]*)\s*(pcs|pieces|nos|units|covers|bags|rolls|sleeves)',
        r'\b(\d{4,})\b',
    ]
    for pattern in qty_patterns:
        for match in re.finditer(pattern, full_history):
            try:
                qty = int(match.group(1).replace(',', ''))
                if qty >= 5000:
                    return True, f"Bulk quantity: {qty} pcs"
            except ValueError:
                pass
    for kw in BULK_KEYWORDS:
        if kw in full_history or kw in message_text.lower():
            return True, f"Bulk keyword detected: '{kw}'"
    return False, ''


# ── Handle owner commands ──
def handle_owner_command(message: str) -> bool:
    msg = message.strip().upper()

    if msg == "HELP":
        send_owner_alert(
            "KITPAK Team Commands:\n\n"
            "Payment confirmation: Update Payment Status to CONFIRMED in the OrderTracking Google Sheet\n"
            "DISPATCH <phone> <tracking> — Send dispatch details\n"
            "CANCEL <phone> — Cancel order\n\n"
            "Example:\n"
            "DISPATCH 9876543210 ST123456789")
        return True

    if msg.startswith("CONFIRM "):
        send_owner_alert(
            "Note: CONFIRM via WhatsApp is disabled. "
            "Please update Payment Status to CONFIRMED in the OrderTracking Google Sheet instead.")
        return True

    if msg.startswith("DISPATCH "):
        parts = message.strip().split(" ", 2)
        if len(parts) < 3:
            send_owner_alert("Usage: DISPATCH <phone> <tracking_number>")
            return True
        customer_phone = parts[1].strip().replace("+", "").replace(" ", "")
        tracking = parts[2].strip()
        if not customer_phone.startswith("91"):
            customer_phone = "91" + customer_phone
        send_whatsapp_template(
            customer_phone,
            'kitpak_dispatch_notification',
            [
                {'name': 'body', 'text': 'Customer'},
                {'name': 'body', 'text': 'our courier partner'},
                {'name': 'body', 'text': tracking}
            ]
        )
        send_owner_alert(f"Dispatch notification sent to {customer_phone}. Tracking: {tracking}")
        return True

    if msg.startswith("CANCEL "):
        customer_phone = msg.split(" ", 1)[1].strip().replace("+", "").replace(" ", "")
        if not customer_phone.startswith("91"):
            customer_phone = "91" + customer_phone
        send_whatsapp_message(customer_phone,
            "We're sorry to inform you that your order has been cancelled. "
            "Please contact us if you have any questions. Thank you for choosing KITPAK.")
        send_owner_alert(f"Cancellation sent to {customer_phone}.")
        return True

    return False


# ── /webhook ──
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({'status': 'no data'}), 200

    # Filter: only process incoming customer messages
    event_type = data.get('eventType', '')
    owner = data.get('owner', True)

    if owner:
        return jsonify({'status': 'ignored'}), 200
    if event_type != 'message':
        return jsonify({'status': 'ignored'}), 200

    # Stop bot if conversation assigned to human agent
    assigned_id = data.get('assignedId')
    operator_name = data.get('operatorName')
    if assigned_id or operator_name:
        print(f"[KITPAK] Conversation assigned to human ({operator_name or assigned_id}) — bot skipping")
        return jsonify({'status': 'ignored_assigned'}), 200

    # Deduplication
    msg_id = data.get('id', '')
    if msg_id in processed_message_ids:
        print(f"[KITPAK] Duplicate message ignored: {msg_id}")
        return jsonify({'status': 'duplicate'}), 200
    processed_message_ids.add(msg_id)
    if len(processed_message_ids) > 1000:
        processed_message_ids.clear()

    # Stale message filter
    try:
        timestamp = int(data.get('timestamp', 0))
        age_seconds = time.time() - timestamp
        if age_seconds > 300:
            print(f"[KITPAK] Ignoring stale message (age {int(age_seconds)}s): {data.get('text')}")
            return jsonify({'status': 'ignored_stale'}), 200
    except Exception:
        pass

    phone = data.get('waId', '')
    message_text = data.get('text', '') or ''
    msg_type = data.get('type', 'text')
    sender_name = data.get('senderName', '')

    print(f"[KITPAK] Message from {phone}: {message_text}")

    # Owner commands
    if phone == OWNER_PHONE.lstrip('91') or phone == OWNER_PHONE:
        if handle_owner_command(message_text):
            return jsonify({'status': 'owner_command'}), 200

    # Init conversation history
    if phone not in conversation_history:
        conversation_history[phone] = []

    # ── Handle file/image uploads ──
    if msg_type in ['image', 'document', 'video'] or (msg_type == 'text' and data.get('data')):
        file_url = data.get('data')
        if file_url and isinstance(file_url, str) and file_url.startswith('http'):
            try:
                headers = {'Authorization': f'Bearer {WATI_API_TOKEN}'}
                file_response = requests.get(file_url, headers=headers, timeout=15)
                if file_response.status_code == 200:
                    file_bytes = file_response.content
                    content_type = file_response.headers.get('Content-Type', 'image/jpeg')
                    mime_type = content_type.split(';')[0].strip()

                    file_type = classify_image(file_bytes, mime_type)
                    print(f"[KITPAK] File classified as: {file_type}")

                    if file_type == 'unknown':
                        conversation_history[phone].append({
                            'role': 'user',
                            'content': '[Customer sent a file — type unclear]'
                        })
                        send_whatsapp_message(phone,
                            "Could you let me know — is this a reference image of the product you want, or your logo/design file for printing?")
                    else:
                        # Logo/design file received
                        conversation_history[phone].append({
                            'role': 'user',
                            'content': '[Customer sent a logo/design file]'
                        })
                        send_owner_alert(
                            f"Logo/design file received from {sender_name} ({phone}). "
                            f"Please check WhatsApp and follow up with the customer.")
                        reply = get_claude_reply(conversation_history[phone])
                        conversation_history[phone].append({'role': 'assistant', 'content': reply})
                        send_whatsapp_message(phone, reply)
                        print(f"[KITPAK] Replied to {phone}: {reply[:80]}")
            except Exception as e:
                print(f"[KITPAK] File handling error: {e}")
        return jsonify({'status': 'ok'}), 200

    # ── Handle text messages ──
    if not message_text.strip():
        return jsonify({'status': 'ignored_empty'}), 200

    conversation_history[phone].append({'role': 'user', 'content': message_text})

    # Send price chart image if customer asks for pricing
    price_requested = is_price_request(message_text)
    if price_requested:
        price_images = get_price_chart_images(message_text)
        if price_images:
            send_product_images(phone, price_images)
            print(f"[KITPAK] Price chart image sent to {phone}")
    else:
        # Send product images if picture requested
        images = get_images_from_message(message_text)
        picture_requested = any(word in message_text.lower() for word in PICTURE_REQUEST_WORDS)
        if not images and picture_requested:
            for past_msg in reversed(conversation_history[phone][:-1][-6:]):
                past_product = get_product_key_from_message(past_msg.get('content', ''))
                if past_product:
                    images = get_images_for_product(past_product)
                    break
        if images:
            send_product_images(phone, images)
            print(f"[KITPAK] Product images sent to {phone}")

    # Get Claude reply
    try:
        reply = get_claude_reply(conversation_history[phone])
    except Exception as e:
        print(f"[KITPAK] Error: {e}")
        reply = "Our team will get in touch with you shortly."

    conversation_history[phone].append({'role': 'assistant', 'content': reply})

    # Send reply
    print(f"[KITPAK] Sending message length: {len(reply)}")
    send_whatsapp_message(phone, reply)
    print(f"[KITPAK] Replied to {phone}: {reply[:80]}")

    # Log handoff to Google Sheets
    if is_handoff(reply):
        full_history_text = ' '.join([m.get('content', '') for m in conversation_history.get(phone, [])]).lower()
        bulk, bulk_reason = is_bulk_enquiry(phone, message_text, reply)

        if bulk:
            try:
                ctx = extract_context_from_history(phone)
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
            try:
                reason = 'General team handoff'
                check_text = (message_text + ' ' + full_history_text).lower()
                if any(w in check_text for w in ['call', 'phone', 'speak', 'talk', 'contact']):
                    reason = 'Customer requested callback'
                elif any(w in check_text for w in ['return', 'refund', 'damage', 'wrong']):
                    reason = 'Return/Refund request'
                elif any(w in check_text for w in ['printed', 'print', 'logo', 'design', 'custom']):
                    reason = 'Custom print request'
                elif any(w in check_text for w in ['kraft', 'paper bag', 'paper cover']):
                    reason = 'Paper bag enquiry'
                elif any(w in check_text for w in ['honeycomb sleeve', 'sleeve']):
                    reason = 'Honeycomb sleeve enquiry'
                append_handoff_to_sheet(
                    phone=phone,
                    customer_name=sender_name,
                    reason=reason,
                    last_message=message_text
                )
                print(f"[KITPAK] Handoff logged for {phone}: {reason}")
            except Exception as e:
                print(f"[KITPAK] Handoff log error: {e}")

    return jsonify({'status': 'ok'}), 200


# ── /sheet-notify ── (triggered by Apps Script for payment/dispatch)
@app.route('/sheet-notify', methods=['POST'])
def sheet_notify():
    data = request.json
    if not data:
        return jsonify({'status': 'no data'}), 400

    secret = data.get('secret', '')
    if secret != SHEET_AUTOMATION_SECRET:
        return jsonify({'status': 'unauthorized'}), 403

    notify_type = data.get('type', '')
    phone = str(data.get('phone', '')).strip()
    customer_name = data.get('customer_name', 'Customer')

    if not phone.startswith('91'):
        phone = '91' + phone

    if notify_type == 'payment':
        send_whatsapp_template(
            phone,
            'kitpak_payment_confirmed',
            [{'name': 'body', 'text': customer_name}]
        )
        print(f"[KITPAK] Payment confirmed sent to {phone}")

    elif notify_type == 'dispatch':
        tracking = data.get('tracking_number', '')
        courier = data.get('courier_partner', 'our courier partner')
        send_whatsapp_template(
            phone,
            'kitpak_dispatch_notification',
            [
                {'name': 'body', 'text': customer_name},
                {'name': 'body', 'text': courier},
                {'name': 'body', 'text': tracking}
            ]
        )
        print(f"[KITPAK] Dispatch notification sent to {phone}")

    return jsonify({'status': 'ok'}), 200


# ── /health ──
@app.route('/health', methods=['GET', 'HEAD'])
def health():
    return jsonify({'status': 'KITPAK bot is live', 'timestamp': datetime.now(IST).isoformat()}), 200


# ── /daily-report ──
@app.route('/daily-report', methods=['GET', 'POST'])
def daily_report():
    append_daily_report(conversation_history)
    send_owner_alert(f"Daily report sent to Google Sheets. Total conversations today: {len(conversation_history)}")
    return jsonify({'status': 'ok', 'conversations': len(conversation_history)}), 200


# ── Daily report scheduler ──
def daily_report_scheduler():
    while True:
        now = datetime.now(IST)
        if now.hour == 18 and now.minute == 0:
            print("[KITPAK] Sending daily report...")
            append_daily_report(conversation_history)
            send_owner_alert(f"Daily report sent. Total conversations today: {len(conversation_history)}")
            time.sleep(61)
        time.sleep(30)


if __name__ == '__main__':
    t = threading.Thread(target=daily_report_scheduler, daemon=True)
    t.start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
