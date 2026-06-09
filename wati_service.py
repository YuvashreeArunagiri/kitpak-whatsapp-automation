import requests
import os
import json


def send_whatsapp_message(phone: str, message: str) -> bool:
    wati_api_url   = os.environ.get('WATI_API_URL', '').rstrip('/')
    wati_api_token = os.environ.get('WATI_API_TOKEN', '')

    if not wati_api_url or not wati_api_token:
        print("[KITPAK] ⚠️ WATI credentials missing")
        return False

    if not message or not message.strip():
        print("[KITPAK] ⚠️ Empty message — not sending")
        return False

    headers = {
        'Authorization': f'Bearer {wati_api_token}',
        'Content-Type': 'application/json; charset=utf-8'
    }

    message_clean = message.strip()
    print(f"[KITPAK] Sending message length: {len(message_clean)}")

    # Method 1 — sendSessionMessage with query param
    try:
        url = f"{wati_api_url}/api/v1/sendSessionMessage/{phone}?messageText={requests.utils.quote(message_clean)}"
        response = requests.post(url, headers=headers, timeout=10)
        print(f"[KITPAK] Method 1 response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            result = response.json()
            if result.get('result') == True:
                print(f"[KITPAK] ✅ Message sent to {phone}")
                return True
    except Exception as e:
        print(f"[KITPAK] Method 1 error: {e}")

    # Method 2 — sendSessionMessage with JSON body
    try:
        url = f"{wati_api_url}/api/v1/sendSessionMessage/{phone}"
        payload = {"messageText": message_clean}
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=10
        )
        print(f"[KITPAK] Method 2 response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            result = response.json()
            if result.get('result') == True:
                print(f"[KITPAK] ✅ Message sent to {phone}")
                return True
    except Exception as e:
        print(f"[KITPAK] Method 2 error: {e}")

    # Method 3 — sendText endpoint
    try:
        url = f"{wati_api_url}/api/v1/sendText/{phone}"
        payload = {"messageText": message_clean}
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"[KITPAK] Method 3 response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            print(f"[KITPAK] ✅ Method 3 sent to {phone}")
            return True
    except Exception as e:
        print(f"[KITPAK] Method 3 error: {e}")

    print(f"[KITPAK] ❌ All methods failed for {phone}")
    return False
