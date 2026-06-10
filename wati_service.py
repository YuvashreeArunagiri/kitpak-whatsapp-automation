import requests
import os

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/YuvashreeArunagiri/kitpak-whatsapp-automation/main"

def send_whatsapp_message(phone: str, message: str) -> bool:
    wati_api_url   = os.environ.get('WATI_API_URL', '').rstrip('/')
    wati_api_token = os.environ.get('WATI_API_TOKEN', '')
    if not wati_api_url or not wati_api_token:
        print("[KITPAK] WATI credentials missing")
        return False
    if not message or not message.strip():
        print("[KITPAK] Empty message — not sending")
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
            if result.get('result') in [True, 'success'] or result.get('ok') == True:
                print(f"[KITPAK] Message sent to {phone}")
                return True
    except Exception as e:
        print(f"[KITPAK] Method 1 error: {e}")
    # Method 2 — sendSessionMessage with JSON body
    try:
        url = f"{wati_api_url}/api/v1/sendSessionMessage/{phone}"
        payload = {"messageText": message_clean}
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"[KITPAK] Method 2 response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            result = response.json()
            if result.get('result') in [True, 'success'] or result.get('ok') == True:
                print(f"[KITPAK] Message sent to {phone}")
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
            print(f"[KITPAK] Method 3 sent to {phone}")
            return True
    except Exception as e:
        print(f"[KITPAK] Method 3 error: {e}")
    print(f"[KITPAK] All methods failed for {phone}")
    return False


def send_whatsapp_image(phone: str, image_filename: str, caption: str = "") -> bool:
    """Send an image from GitHub raw URL via WATI."""
    wati_api_url   = os.environ.get('WATI_API_URL', '').rstrip('/')
    wati_api_token = os.environ.get('WATI_API_TOKEN', '')
    if not wati_api_url or not wati_api_token:
        print("[KITPAK] WATI credentials missing")
        return False

    image_url = f"{GITHUB_RAW_BASE}/{image_filename}"
    headers = {
        'Authorization': f'Bearer {wati_api_token}',
        'Content-Type': 'application/json'
    }

    # Method 1 — sendSessionFile
    try:
        url = f"{wati_api_url}/api/v1/sendSessionFile/{phone}"
        payload = {
            "url": image_url,
            "caption": caption,
            "mimeType": "image/jpeg" if image_filename.endswith(('.jpg', '.jpeg')) else "image/png"
        }
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"[KITPAK] Image send response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            print(f"[KITPAK] Image sent to {phone}: {image_filename}")
            return True
    except Exception as e:
        print(f"[KITPAK] Image send error: {e}")

    # Method 2 — sendMedia
    try:
        url = f"{wati_api_url}/api/v1/sendMedia/{phone}"
        payload = {
            "mediaUrl": image_url,
            "caption": caption,
            "type": "image"
        }
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"[KITPAK] Image method 2 response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            print(f"[KITPAK] Image sent via method 2 to {phone}")
            return True
    except Exception as e:
        print(f"[KITPAK] Image method 2 error: {e}")

    print(f"[KITPAK] Image send failed for {phone}")
    return False


def send_product_images(phone: str, image_filenames: list, caption: str = "") -> bool:
    """Send up to 2 product reference images to customer."""
    if not image_filenames:
        return False
    sent = False
    for filename in image_filenames[:2]:  # max 2 images
        result = send_whatsapp_image(phone, filename, caption)
        if result:
            sent = True
        caption = ""  # caption only on first image
    return sent
