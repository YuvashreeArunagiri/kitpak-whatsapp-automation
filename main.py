from flask import Flask, request, jsonify
import os
import io
import json
import base64
import urllib.request
from dotenv import load_dotenv
from claude_service import get_claude_reply, extract_order_details, classify_image
from wati_service import send_whatsapp_message, send_product_images, send_whatsapp_pdf
from pi_service import generate_pi_text, generate_pi_pdf
from image_service import get_images_from_message
from mockup_service import generate_mockup, get_mockup_caption

load_dotenv()

app = Flask(__name__)

conversation_history = {}
pending_logo = {}        # phone -> logo bytes (waiting for bag colour confirmation)
custom_order_state = {}  # phone -> {colour, size, qty}

OWNER_NUMBER = "918300475706"


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
    try:
        req = urllib.request.Request(file_url, headers={'Authorization': f'Bearer {wati_api_token}'})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read()
    except Exception as e:
        print(f"[KITPAK] File download error: {e}")
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

        # ── Ignore outgoing messages sent by the bot itself ──
        event_type = data.get('eventType', '')
        owner = data.get('owner', False)
        status = data.get('statusString', '')
        if owner or event_type in ['message_sent', 'outgoing'] or status in ['SENT', 'DELIVERED', 'READ']:
            return jsonify({'status': 'ignored'}), 200

        # ── Team command from owner number ──
        if phone == OWNER_NUMBER and message_text:
            if handle_team_command(phone, message_text):
                return jsonify({'status': 'ok'}), 200

        # ── Handle file uploads (logo or payment screenshot) ──
        if msg_type in ['image', 'document']:
            if phone not in conversation_history:
                conversation_history[phone] = []

            # Try to get file URL from payload
            file_url = None
            if msg_type == 'image':
                file_url = (data.get('image') or {}).get('link') or (data.get('image') or {}).get('url')
            elif msg_type == 'document':
                file_url = (data.get('document') or {}).get('link') or (data.get('document') or {}).get('url')

            # Check conversation context — are we in a custom order flow?
            history_text = ' '.join([m.get('content','') for m in conversation_history.get(phone, [])])
            in_custom_order = any(word in history_text.lower() for word in ['logo', 'custom print', 'custom cover', 'printed cover', 'your design'])
            pi_pending = 'GENERATE_PI:' in history_text

            if in_custom_order and not pi_pending and file_url:
                # This is a logo — generate mockup
                print(f"[KITPAK] Logo received from {phone} — generating mockup")
                file_bytes = download_wati_file(file_url)

                if file_bytes:
                    # Detect bag colour from conversation
                    bag_colour = get_bag_colour_from_history(phone)

                    # Save logo to temp file
                    ext = '.png'
                    if msg_type == 'document':
                        fname = (data.get('document') or {}).get('fileName', 'logo.png').lower()
                        if fname.endswith('.pdf'):
                            ext = '.pdf'
                        elif fname.endswith('.jpg') or fname.endswith('.jpeg'):
                            ext = '.jpg'

                    logo_path = f"/tmp/logo_{phone}{ext}"
                    with open(logo_path, 'wb') as f:
                        f.write(file_bytes)

                    try:
                        mockup_bytes = generate_mockup(logo_path, bag_colour=bag_colour)
                        caption = get_mockup_caption()
                        # Send mockup as image
                        send_whatsapp_pdf(phone, mockup_bytes, filename="KITPAK_Mockup.png", caption=caption)
                        print(f"[KITPAK] Mockup sent to {phone}")

                        conversation_history[phone].append({
                            'role': 'user',
                            'content': '[Customer sent their logo file]'
                        })
                        reply = get_claude_reply(conversation_history[phone][-20:])
                        conversation_history[phone].append({'role': 'assistant', 'content': reply})
                        send_whatsapp_message(phone, reply)
                    except Exception as e:
                        print(f"[KITPAK] Mockup error: {e}")
                        conversation_history[phone].append({
                            'role': 'user',
                            'content': '[Customer sent their logo file]'
                        })
                        reply = get_claude_reply(conversation_history[phone][-20:])
                        conversation_history[phone].append({'role': 'assistant', 'content': reply})
                        send_whatsapp_message(phone, reply)
                else:
                    # Could not download file
                    conversation_history[phone].append({
                        'role': 'user',
                        'content': '[Customer sent a file but it could not be downloaded]'
                    })
                    send_whatsapp_message(phone, "I received your file but had trouble opening it. Could you please send it again?")

            else:
                # Treat as payment screenshot
                print(f"[KITPAK] Payment screenshot received from {phone}")
                conversation_history[phone].append({
                    'role': 'user',
                    'content': '[Customer sent a payment screenshot]'
                })
                send_whatsapp_message(phone,
                    "Thank you! We have received your payment screenshot. "
                    "Our team will verify the payment and confirm your order shortly.")

                # Alert owner
                sender_name = data.get('senderName', phone)
                send_whatsapp_message(OWNER_NUMBER,
                    f"Payment screenshot received from {sender_name} ({phone}).\n"
                    f"Please verify and reply:\n"
                    f"CONFIRM {phone[-10:]}")

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
