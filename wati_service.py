import requests
import os


def send_whatsapp_message(phone: str, message: str) -> bool:
    wati_api_url   = os.environ.get('WATI_API_URL', '').rstrip('/')
    wati_api_token = os.environ.get('WATI_API_TOKEN', '')

    if not wati_api_url or not wati_api_token:
        print("[KITPAK] ⚠️ WATI credentials missing")
        return False

    headers = {
        'Authorization': f'Bearer {wati_api_token}',
        'Content-Type': 'application/json'
    }

    # Step 1 — Send the message
    url = f"{wati_api_url}/api/v1/sendSessionMessage/{phone}"
    payload = {'messageText': message}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"[KITPAK] WATI response: {response.status_code} - {response.text[:300]}")

        if response.status_code == 200:
            print(f"[KITPAK] ✅ Message sent to {phone}")

            # Step 2 — Try to unassign from agent
            try:
                # Method 1: unassign operator
                unassign_url = f"{wati_api_url}/api/v1/unassignOperator/{phone}"
                r1 = requests.post(unassign_url, headers=headers, timeout=5)
                print(f"[KITPAK] Unassign attempt 1: {r1.status_code}")
            except Exception as e:
                print(f"[KITPAK] Unassign 1 error: {e}")

            try:
                # Method 2: assign to empty operator
                assign_url = f"{wati_api_url}/api/v1/assignOperator/{phone}"
                r2 = requests.post(assign_url, json={"operatorEmail": ""}, headers=headers, timeout=5)
                print(f"[KITPAK] Unassign attempt 2: {r2.status_code}")
            except Exception as e:
                print(f"[KITPAK] Unassign 2 error: {e}")

            return True
        else:
            print(f"[KITPAK] ❌ WATI error {response.status_code}: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"[KITPAK] ❌ Timeout for {phone}")
        return False
    except Exception as e:
        print(f"[KITPAK] ❌ Error: {e}")
        return False
