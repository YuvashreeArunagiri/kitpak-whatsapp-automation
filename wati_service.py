import requests
import os


def send_whatsapp_message(phone: str, message: str) -> bool:
    """
    Send a WhatsApp message to a customer via the WATI API.

    Args:
        phone   : Customer's WhatsApp number (e.g. "919876543210")
        message : Text message to send

    Returns:
        True if sent successfully, False otherwise
    """
    wati_api_url   = os.environ.get('WATI_API_URL', '').rstrip('/')
    wati_api_token = os.environ.get('WATI_API_TOKEN', '')

    if not wati_api_url or not wati_api_token:
        print("[KITPAK] ⚠️  WATI credentials missing in .env — message not sent.")
        return False

    url = f"{wati_api_url}/api/v1/sendSessionMessage/{phone}"

    headers = {
        'Authorization': f'Bearer {wati_api_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        'messageText': message
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            print(f"[KITPAK] ✅ Message sent to {phone}")
            return True
        else:
            print(f"[KITPAK] ❌ WATI error {response.status_code}: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"[KITPAK] ❌ WATI request timed out for {phone}")
        return False
    except Exception as e:
        print(f"[KITPAK] ❌ Error sending message: {e}")
        return False
