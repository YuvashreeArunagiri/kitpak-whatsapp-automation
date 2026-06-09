from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from claude_service import get_claude_reply
from wati_service import send_whatsapp_message

load_dotenv()

app = Flask(__name__)

conversation_history = {}

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

        send_whatsapp_message(phone, reply)
        print(f"[KITPAK] Replied to {phone}: {reply[:80]}")

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
