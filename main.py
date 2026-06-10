from flask import Flask, request, jsonify
import os
import json
from dotenv import load_dotenv
from claude_service import get_claude_reply, extract_order_details
from wati_service import send_whatsapp_message, send_product_images
from pi_service import generate_pi_text
from image_service import get_images_from_message

load_dotenv()

app = Flask(__name__)

conversation_history = {}

OWNER_NUMBER = "918300475706"

# ─── Team keyword commands ───────────────────────────────────
def handle_team_command(phone: str, message: str) -> bool:
    msg = message.strip().upper()

    if msg.startswith("CONFIRM "):
        customer_phone = message.strip().split(" ", 1)[1].strip().replace("+", "").replace(" ", "")
        if not customer_phone.startswith("91"):
            customer_phone = "91" + customer_phone
        confirmation_msg = (
            "Great news! Your payment has been verified and confirmed. "
            "Your order is now being processed. "
            "We will share the dispatch and tracking details shortly. "
            "Thank you for choosing KITPAK!"
        )
        send_whatsapp_message(customer_phone, confirmation_msg)
        send_whatsapp_message(OWNER_NUMBER, f"Done! Confirmation sent to {customer_phone}.")
        print(f"[KITPAK] Order confirmed for {customer_phone}")
        return True

    if msg.startswith("DISPATCH "):
        parts = message.strip().split(" ", 2)
        if len(parts) >= 2:
            customer_phone = parts[1].strip().replace("+", "").replace(" ", "")
            if not customer_phone.startswith("91"):
                customer_phone = "91" + customer_phone
            tracking = parts[2].strip() if len(parts) > 2 else "Will be updated shortly"
            dispatch_msg = (
                f"Your order has been dispatched!\n\n"
                f"Tracking Number: {tracking}\n\n"
                f"You can track your order using the above number. "
                f"Expected delivery in 3-5 business days. "
                f"Thank you for choosing KITPAK!"
            )
            send_whatsapp_message(customer_phone, dispatch_msg)
            send_whatsapp_message(OWNER_NUMBER, f"Done! Dispatch details sent to {customer_phone}.")
            print(f"[KITPAK] Dispatch sent to {customer_phone}")
            return True

    if msg.startswith("CANCEL "):
        customer_phone = message.strip().split(" ", 1)[1].strip().replace("+", "").replace(" ", "")
        if not customer_phone.startswith("91"):
            customer_phone = "91" + customer_phone
        cancel_msg = (
            "We regret to inform you that your order could not be processed. "
            "Please contact us for further assistance. "
            "We apologise for the inconvenience."
        )
        send_whatsapp_message(customer_phone, cancel_msg)
        send_whatsapp_message(OWNER_NUMBER, f"Done! Cancellation sent to {customer_phone}.")
        print(f"[KITPAK] Order cancelled for {customer_phone}")
        return True

    if msg == "HELP":
        help_msg = (
            "KITPAK Team Commands:\n\n"
            "CONFIRM <phone> — Confirm payment and order\n"
            "DISPATCH <phone> <tracking> — Send dispatch details\n"
            "CANCEL <phone> — Cancel order\n\n"
            "Example:\n"
            "CONFIRM 9876543210\n"
            "DISPATCH 9876543210 ST123456789"
        )
        send_whatsapp_message(OWNER_NUMBER, help_msg)
        return True

    return False


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print(f"[KITPAK] Payload: {data}")

        if not data:
            return jsonify({'status': 'no data'}), 200

        phone = (data.get('waId') or data.get('from') or '')

        message_text = ''
        if data.get('text') and isinstance(data.get('text'), dict):
            message_text = data['text'].get('body', '')
        elif data.get('text') and isinstance(data.get('text'), str):
            message_text = data['text']
        elif data.get('body'):
            message_text = data['body']

        message_text = message_text.strip()

        if not phone or not message_text:
            return jsonify({'status': 'ignored'}), 200

        msg_type = data.get('type', 'text')

        # ── Team command from owner number ──
        if phone == OWNER_NUMBER:
            if handle_team_command(phone, message_text):
                return jsonify({'status': 'ok'}), 200

        # ── Handle image/document — logo/payment screenshot ──
        if msg_type in ['image', 'document', 'video']:
            if phone not in conversation_history:
                conversation_history[phone] = []
            conversation_history[phone].append({
                'role': 'user',
                'content': '[Customer sent a file — could be logo or payment screenshot]'
            })
            history = conversation_history[phone][-20:]
            reply = get_claude_reply(history)
            conversation_history[phone].append({'role': 'assistant', 'content': reply})
            send_whatsapp_message(phone, reply)

            alert_msg = (
                f"Payment screenshot received from {data.get('senderName', phone)} ({phone}).\n"
                f"Please verify and reply:\n"
                f"CONFIRM {phone[-10:]}"
            )
            send_whatsapp_message(OWNER_NUMBER, alert_msg)
            print(f"[KITPAK] File received from {phone} — owner alerted")
            return jsonify({'status': 'ok'}), 200

        if msg_type not in ['text', '']:
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

        send_whatsapp_message(phone, reply)
        print(f"[KITPAK] Replied to {phone}: {reply[:80]}")

        # ── Generate PI if needed ──
        if 'GENERATE_PI:' in reply:
            try:
                order = extract_order_details(history)
                if order:
                    pi_text = generate_pi_text(order)
                    send_whatsapp_message(phone, pi_text)
                    print(f"[KITPAK] PI sent to {phone}")
            except Exception as e:
                print(f"[KITPAK] PI generation error: {e}")

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
