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


def send_whatsapp_template(phone: str, template_name: str, parameters: list) -> bool:
    """
    Send an approved WhatsApp template message via WATI.
    Works outside the 24-hour session window.
    parameters: list of strings, one per {{n}} placeholder in the template body.
    """
    wati_api_url   = os.environ.get('WATI_API_URL', '').rstrip('/')
    wati_api_token = os.environ.get('WATI_API_TOKEN', '')
    if not wati_api_url or not wati_api_token:
        print("[KITPAK] WATI credentials missing")
        return False

    headers = {
        'Authorization': f'Bearer {wati_api_token}',
        'Content-Type': 'application/json'
    }

    # Build parameter list in WATI format
    wati_params = [{"name": str(i + 1), "value": str(p)} for i, p in enumerate(parameters)]

    payload = {
        "template_name": template_name,
        "broadcast_name": template_name,
        "parameters": wati_params
    }

    try:
        url = f"{wati_api_url}/api/v1/sendTemplateMessage/{phone}"
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"[KITPAK] Template '{template_name}' response: {response.status_code} - {response.text[:300]}")
        if response.status_code == 200:
            result = response.json()
            if result.get('result') in [True, 'success'] or result.get('ok') == True:
                print(f"[KITPAK] Template message sent to {phone}")
                return True
            # Some WATI versions return 200 even on success without result=True
            if 'error' not in response.text.lower() and 'fail' not in response.text.lower():
                print(f"[KITPAK] Template likely sent to {phone}")
                return True
    except Exception as e:
        print(f"[KITPAK] Template send error: {e}")

    print(f"[KITPAK] Template send failed for {phone}")
    return False


def send_whatsapp_image(phone: str, image_filename: str, caption: str = "") -> bool:
    """Download image from GitHub and send to customer via WATI multipart upload."""
    wati_api_url   = os.environ.get('WATI_API_URL', '').rstrip('/')
    wati_api_token = os.environ.get('WATI_API_TOKEN', '')
    if not wati_api_url or not wati_api_token:
        print("[KITPAK] WATI credentials missing")
        return False

    image_url = f"{GITHUB_RAW_BASE}/{image_filename}"
    mime_type = "image/jpeg" if image_filename.endswith(('.jpg', '.jpeg')) else "image/png"

    # Download image from GitHub first
    try:
        img_response = requests.get(image_url, timeout=15)
        if img_response.status_code != 200:
            print(f"[KITPAK] Image download failed: {img_response.status_code} for {image_url}")
            return False
        image_bytes = img_response.content
    except Exception as e:
        print(f"[KITPAK] Image download error: {e}")
        return False

    headers = {'Authorization': f'Bearer {wati_api_token}'}

    # Method 1 — multipart upload via sendSessionFile
    try:
        url = f"{wati_api_url}/api/v1/sendSessionFile/{phone}"
        files = {'file': (image_filename, image_bytes, mime_type)}
        data = {'caption': caption} if caption else {}
        response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
        print(f"[KITPAK] Image send response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            result = response.json()
            if result.get('result') != False:
                print(f"[KITPAK] Image sent to {phone}: {image_filename}")
                return True
    except Exception as e:
        print(f"[KITPAK] Image send error: {e}")

    # Method 2 — sendFile endpoint
    try:
        url = f"{wati_api_url}/api/v1/sendFile/{phone}"
        files = {'file': (image_filename, image_bytes, mime_type)}
        data = {'caption': caption} if caption else {}
        response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
        print(f"[KITPAK] Image method 2 response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            print(f"[KITPAK] Image sent via method 2 to {phone}")
            return True
    except Exception as e:
        print(f"[KITPAK] Image method 2 error: {e}")

    print(f"[KITPAK] Image send failed for {phone}: {image_filename}")
    return False


def send_product_images(phone: str, image_filenames: list, caption: str = "") -> bool:
    """Send up to 2 product reference images to customer."""
    if not image_filenames:
        return False
    sent = False
    for filename in image_filenames[:2]:
        result = send_whatsapp_image(phone, filename, caption)
        if result:
            sent = True
        caption = ""
    return sent


def send_whatsapp_pdf(phone: str, pdf_bytes: bytes, filename: str = "KITPAK_PI.pdf", caption: str = "") -> bool:
    """Send a PDF or image file via WATI using multipart upload."""
    wati_api_url   = os.environ.get('WATI_API_URL', '').rstrip('/')
    wati_api_token = os.environ.get('WATI_API_TOKEN', '')
    if not wati_api_url or not wati_api_token:
        print("[KITPAK] WATI credentials missing")
        return False

    fn_lower = filename.lower()
    if fn_lower.endswith('.png'):
        mime_type = 'image/png'
    elif fn_lower.endswith('.jpg') or fn_lower.endswith('.jpeg'):
        mime_type = 'image/jpeg'
    else:
        mime_type = 'application/pdf'

    headers = {'Authorization': f'Bearer {wati_api_token}'}

    # Method 1 — multipart upload
    try:
        url = f"{wati_api_url}/api/v1/sendSessionFile/{phone}"
        files = {'file': (filename, pdf_bytes, mime_type)}
        data = {'caption': caption} if caption else {}
        response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
        print(f"[KITPAK] PDF send response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            print(f"[KITPAK] PDF sent to {phone}")
            return True
    except Exception as e:
        print(f"[KITPAK] PDF send error: {e}")

    # Method 2 — sendFile endpoint
    try:
        url = f"{wati_api_url}/api/v1/sendFile/{phone}"
        files = {'file': (filename, pdf_bytes, mime_type)}
        data = {'caption': caption} if caption else {}
        response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
        print(f"[KITPAK] PDF method 2 response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            print(f"[KITPAK] PDF sent via method 2 to {phone}")
            return True
    except Exception as e:
        print(f"[KITPAK] PDF method 2 error: {e}")

    print(f"[KITPAK] PDF send failed for {phone}")
    return False
