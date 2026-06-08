from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from claude_service import get_claude_reply
from wati_service import send_whatsapp_message

load_dotenv()

app = Flask(__name__)

# In-memory conversation history per customer (phone -> message list)
# This keeps context so the bot remembers the conversation
conversation_history = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    """WATI sends incoming customer messages here."""
    data = request.json

    try:
        # Extract phone number and message from WATI payload
        phone = data.get('waId') or data.get('from', '')
        message_text = (data.get('text') or data.get('body') or '').strip()

        # Ignore empty messages or status updates
        if not phone or not message_text:
            return jsonify({'status': 'ignored'}), 200

        print(f"[KITPAK] Message from {phone}: {message_text}")

        # Build conversation history for this customer
        if phone not in conversation_history:
            conversation_history[phone] = []

        conversation_history[phone].append({
            'role': 'user',
            'content': message_text
        })

        # Keep last 20 messages to stay within token limits
        history = conversation_history[phone][-20:]

        # Get Claude's reply
        reply = get_claude_reply(history)

        # Save Claude's reply to history
        conversation_history[phone].append({
            'role': 'assistant',
            'content': reply
        })

        # Send the reply back to customer via WATI
        send_whatsapp_message(phone, reply)

        print(f"[KITPAK] Replied to {phone}: {reply[:80]}...")
        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        print(f"[KITPAK] Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint — used by Render to confirm server is alive."""
    return jsonify({
        'status': 'running',
        'bot': 'KITPAK WhatsApp Assistant ✅'
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[KITPAK] Bot starting on port {port}...")
    app.run(host='0.0.0.0', port=port)
