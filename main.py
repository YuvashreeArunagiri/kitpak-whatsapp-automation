from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os
import io
import json
import base64
import urllib.request
from dotenv import load_dotenv
from claude_service import get_claude_reply, extract_order_details, classify_image, extract_payment_info
from wati_service import send_whatsapp_message, send_product_images, send_whatsapp_pdf
from pi_service import generate_pi_text, generate_pi_pdf
from image_service import get_images_from_message
from mockup_service import generate_mockup, get_mockup_caption
from sheets_service import append_daily_report, append_order_to_sheet
import threading
import time

load_dotenv()

app = Flask(__name__)

conversation_history = {}
processed_message_ids = set()  # Track processed message IDs to prevent duplicates
pending_orders = {}  # phone -> {'total': amount, 'pi_number': str} — set when PI is generated

def daily_report_scheduler():
    """Background thread — sends daily report to Google Sheets at 6 PM."""
    while True:
        now = datetime.now()
        # Check if it's 6 PM (18:00)
        if now.hour == 18 and now.minute == 0:
            print("[KITPAK] Sending daily report to Google Sheets...")
            append_daily_report(conversation_history)
            send_whatsapp_message(OWNER_NUMBER, f"Daily report sent to Google Sheets. Total conversations today: {len(conversation_history)}")
            time.sleep(61)  # sleep 61 seconds to avoid double-sending
        time.sleep(30)  # check every 30 seconds

# Start scheduler in background
scheduler_thread = threading.Thread(target=daily_report_scheduler, daemon=True)
scheduler_thread.start()
pending_logo = {}        # phone -> logo bytes (waiting for bag colour confirmation)
custom_order_state = {}  # phone -> {colour, size, qty}

OWNER_NUMBER = "918300475706"
KITPAK_UPI_ID = os.environ.get("KITPAK_UPI_ID", "9489501487@okbizaxis")


# ─── Team keyword commands ───────────────────────────────────
def handle_team_command(phone: str, message: str) -> bool:
    msg = message.strip().upper()

    if msg.startswith("CONFIRM "):
        customer_phone = message.strip().split(" ", 1)[1].strip().replace("+", "").replace(" ", "")
        if not customer_phone.startswith("91"):
            customer_phone = "91" + customer_phone
        send_whatsapp_message(customer_phone,
            "Great news! Your payment has been verified and confirmed. "
            "Your order is now being processed. "
            "We will share the dispatch and tracking details shortly. "
            "Thank you for choosing KITPAK!")
        send_whatsapp_message(OWNER_NUMBER, f"Done! Confirmation sent to {customer_phone}.")
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
            send_whatsapp_message(OWNER_NUMBER, f"Done! Dispatch details sent to {customer_phone}.")
        return True

    if msg.startswith("CANCEL "):
        customer_phone = message.strip().split(" ", 1)[1].strip().replace("+", "").replace(" ", "")
        if not customer_phone.startswith("91"):
            customer_phone = "91" + customer_phone
        send_whatsapp_message(customer_phone,
            "We regret to inform you that your order could not be processed. "
            "Please contact us for further assistance. "
            "We apologise for the inconvenience.")
        send_whatsapp_message(OWNER_NUMBER, f"Done! Cancellation sent to {customer_phone}.")
        return True

    if msg == "HELP":
        send_whatsapp_message(OWNER_NUMBER,
            "KITPAK Team Commands:\n\n"
            "CONFIRM <phone> — Confirm payment and order\n"
            "DISPATCH <phone> <tracking> — Send dispatch details\n"
            "CANCEL <phone> — Cancel order\n\n"
            "Example:\n"
            "CONFIRM 9876543210\n"
            "DISPATCH 9876543210 ST123456789")
        return True

    return False


def download_wati_file(file_url: str) -> bytes:
    """Download a file from WATI media URL."""
    wati_api_token = os.environ.get('WATI_API_TOKEN', '')
    
    # Try with requests library (handles redirects better)
    try:
        response = requests.get(
            file_url,
            headers={
                'Authorization': f'Bearer {wati_api_token}',
                'Accept': '*/*'
            },
            timeout=15,
            allow_redirects=True
        )
        if response.status_code == 200:
            return response.content
        print(f"[KITPAK] File download status: {response.status_code}")
    except Exception as e:
        print(f"[KITPAK] File download error (requests): {e}")

    # Try without auth header
    try:
        response = requests.get(file_url, timeout=15, allow_redirects=True)
        if response.status_code == 200:
            return response.content
        print(f"[KITPAK] File download (no auth) status: {response.status_code}")
    except Exception as e:
        print(f"[KITPAK] File download error (no auth): {e}")

    # Try with urllib as fallback
    try:
        req = urllib.request.Request(
            file_url,
            headers={
                'Authorization': f'Bearer {wati_api_token}',
                'User-Agent': 'Mozilla/5.0'
            }
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read()
    except Exception as e:
        print(f"[KITPAK] File download error (urllib): {e}")

    return None


def is_likely_logo(data: dict) -> bool:
    """Check if the incoming file is likely a logo (image or PDF)."""
    msg_type = data.get('type', '')
    if msg_type == 'image':
        return True
    if msg_type == 'document':
        mime = (data.get('document') or {}).get('mimeType', '')
        filename = (data.get('document') or {}).get('fileName', '').lower()
        if 'pdf' in mime or filename.endswith('.pdf'):
            return True
        if 'image' in mime or filename.endswith(('.png', '.jpg', '.jpeg')):
            return True
    return False


def is_likely_payment(data: dict) -> bool:
    """Check if the incoming file is likely a payment screenshot."""
    msg_type = data.get('type', '')
    if msg_type == 'image':
        # If customer has an active order (GENERATE_PI was recently sent), treat as payment
        return True
    return False


def get_bag_colour_from_history(phone: str) -> str:
    """Extract bag colour from conversation history."""
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

        # ── Only process incoming customer messages ──
        event_type = data.get('eventType', '')
        owner = data.get('owner', False)

        if owner:
            return jsonify({'status': 'ignored'}), 200
        if event_type != 'message':
            return jsonify({'status': 'ignored'}), 200

        # ── Deduplicate — ignore already processed message IDs ──
        message_id = data.get('id', '') or data.get('whatsappMessageId', '')
        if message_id and message_id in processed_message_ids:
            print(f"[KITPAK] Duplicate message ignored: {message_id}")
            return jsonify({'status': 'ignored'}), 200
        if message_id:
            processed_message_ids.add(message_id)
            # Keep set size manageable
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

            # Get file URL — WATI stores it in 'data' field directly
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

            # Determine file extension and mime type
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

            # Download file
            file_bytes = download_wati_file(file_url) if file_url else None

            if file_bytes:
                # PDFs are always logos — skip vision classification
                if ext == '.pdf':
                    file_type = 'logo'
                    print(f"[KITPAK] PDF file received — treating as logo")
                else:
                    # Use Claude vision to classify image
                    file_type = classify_image(file_bytes, mime_type)
                    print(f"[KITPAK] File classified as: {file_type}")

                if file_type == 'logo':
                    # Check if customer asked for mockup
                    history_text = ' '.join([m.get('content','') for m in conversation_history.get(phone, [])])
                    wants_mockup = any(word in history_text.lower() for word in ['mockup', 'mock up', 'sample', 'preview', 'design', 'custom print', 'printed cover', 'custom cover'])

                    if wants_mockup:
                        bag_colour = get_bag_colour_from_history(phone)
                        logo_path = f"/tmp/logo_{phone}{ext}"
                        with open(logo_path, 'wb') as f_out:
                            f_out.write(file_bytes)
                        try:
                            mockup_bytes = generate_mockup(logo_path, bag_colour=bag_colour)
                            send_whatsapp_pdf(phone, mockup_bytes, filename="KITPAK_Mockup.png",
                                caption="Here is your mockup for reference. Please let us know if you would like to proceed.")
                            print(f"[KITPAK] Mockup sent to {phone}")
                            conversation_history[phone].append({'role': 'user', 'content': '[Customer sent their logo file — mockup generated and sent]'})
                        except Exception as e:
                            print(f"[KITPAK] Mockup error: {e}")
                            conversation_history[phone].append({'role': 'user', 'content': '[Customer sent their logo file]'})
                    else:
                        conversation_history[phone].append({'role': 'user', 'content': '[Customer sent their logo/design file]'})

                    reply = get_claude_reply(conversation_history[phone][-20:])
                    conversation_history[phone].append({'role': 'assistant', 'content': reply})
                    send_whatsapp_message(phone, reply)

                else:
                    # Payment screenshot
                    print(f"[KITPAK] Payment screenshot received from {phone}")
                    conversation_history[phone].append({'role': 'user', 'content': '[Customer sent a payment screenshot]'})
                    send_whatsapp_message(phone,
                        "Thank you! We have received your payment screenshot. "
                        "Our team will verify and confirm your order shortly.")

                    sender_name = data.get('senderName', phone)

                    # Verify payment amount against expected order total
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

                    send_whatsapp_message(OWNER_NUMBER, alert_msg)

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

        conversation_history[phone].append({
            'role': 'user',
            'content': message_text
        })

        history = conversation_history[phone][-20:]
        time.sleep(10)  # Natural delay before replying
        reply = get_claude_reply(history)

        conversation_history[phone].append({
            'role': 'assistant',
            'content': reply
        })

        # ── Send product images if this is a product enquiry ──
        images = get_images_from_message(message_text)
        if images:
            send_product_images(phone, images)
            print(f"[KITPAK] Product images sent to {phone}")

        # ── Send text reply — hide GENERATE_PI line from customer ──
        if 'GENERATE_PI:' in reply:
            # Send a clean confirmation message to customer instead of raw GENERATE_PI
            send_whatsapp_message(phone, "Thank you! Generating your invoice now, please wait a moment.")
        else:
            send_whatsapp_message(phone, reply)
        print(f"[KITPAK] Replied to {phone}: {reply[:80]}")

        # ── Generate and send PI as PDF ──
        if 'GENERATE_PI:' in reply:
            try:
                order = extract_order_details(reply)
                if order:
                    pdf_bytes = generate_pi_pdf(order)
                    pdf_sent = send_whatsapp_pdf(
                        phone,
                        pdf_bytes,
                        filename="KITPAK_ProformaInvoice.pdf",
                        caption="Here is your Proforma Invoice. Please pay via UPI and share the payment screenshot to confirm your order."
                    )
                    # Store order total for payment verification later
                    order_total = sum(i['qty'] * i['rate'] for i in order.get('items', []))
                    pending_orders[phone] = {'total': order_total}
                    print(f"[KITPAK] Pending order total for {phone}: Rs.{order_total}")

                    # Log order to Google Sheets
                    try:
                        append_order_to_sheet(phone, order)
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
                    send_whatsapp_message(OWNER_NUMBER, f"PI generation failed for {phone} — please send manually.")
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


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'KITPAK Abimanyu is live!'}), 200


@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'KITPAK Abimanyu is live!'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
