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
        'Content-Type': 'application/json'
    }

    # Send session message
    url = f"{wati_api_url}/api/v1/sendSessionMessage/{phone}"
    
    # Try both payload formats
    payload = {'messageText': message.strip()}

    try:
        response = requests.post(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers=headers,
            timeout=10
        )
        print(f"[KITPAK] WATI response: {response.status_code} - {response.text[:300]}")

        if response.status_code == 200:
            result = response.json()
            if result.get('result') == True:
                print(f"[KITPAK] ✅ Message delivered to {phone}")
                return True
            else:
                print(f"[KITPAK] ⚠️ WATI accepted but result=false: {result.get('info')}")
                # Try alternative endpoint
                return _try_alternative_send(wati_api_url, wati_api_token, phone, message)
        else:
            print(f"[KITPAK] ❌ WATI error {response.status_code}")
            return False

    except Exception as e:
        print(f"[KITPAK] ❌ Error: {e}")
        return False


def _try_alternative_send(base_url: str, token: str, phone: str, message: str) -> bool:
    """Try alternative WATI send endpoint."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Try v2 endpoint
    url = f"{base_url}/api/v2/sendSessionMessage/{phone}"
    payload = {'messageText': message.strip()}
    
    try:
        response = requests.post(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers=headers,
            timeout=10
        )
        print(f"[KITPAK] Alt send response: {response.status_code} - {response.text[:200]}")
        return response.status_code == 200
    except Exception as e:
        print(f"[KITPAK] Alt send error: {e}")
        return False
