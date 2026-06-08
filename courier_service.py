# ─────────────────────────────────────────────
# KITPAK — Courier Assignment Service
# Auto-assigns courier based on delivery state
# ─────────────────────────────────────────────

from config import STATE_COURIER_MAP, COURIER_TRACKING_URLS


def get_courier_for_state(state: str) -> str:
    """
    Returns the assigned courier based on delivery state.
    Tamil Nadu → ST Courier
    Karnataka, Kerala, Andhra Pradesh, Telangana → DTDC
    All others → India Post
    """
    state = state.strip().title()
    return STATE_COURIER_MAP.get(state, STATE_COURIER_MAP["DEFAULT"])


def get_tracking_url(courier: str, awb: str) -> str:
    """
    Returns the tracking URL for a given courier and AWB number.
    """
    template = COURIER_TRACKING_URLS.get(courier, "")
    if template:
        return template.replace("{awb}", awb)
    return ""


def get_courier_from_pincode(pincode: str) -> str:
    """
    Basic pincode-to-state mapping for auto courier assignment.
    Extend this with full pincode DB or API later.
    """
    pincode = str(pincode).strip()

    if not pincode or len(pincode) != 6:
        return "India Post"

    prefix = int(pincode[:3])

    # Tamil Nadu: 600–643
    if 600 <= prefix <= 643:
        return "ST Courier"

    # Karnataka: 560–591
    if 560 <= prefix <= 591:
        return "DTDC"

    # Kerala: 670–695
    if 670 <= prefix <= 695:
        return "DTDC"

    # Andhra Pradesh: 500–535 (shared with Telangana)
    if 500 <= prefix <= 535:
        return "DTDC"

    # Telangana: 500–509
    if 500 <= prefix <= 509:
        return "DTDC"

    # All others → India Post
    return "India Post"


def build_dispatch_summary(order: dict, awb: str) -> str:
    """
    Builds the WhatsApp tracking message to send to customer after dispatch.
    """
    courier = order.get("courier", "India Post")
    tracking_url = get_tracking_url(courier, awb)

    msg = f"""📦 Your KITPAK order has been dispatched!

🚚 Courier: {courier}
🔢 Tracking ID: {awb}
"""
    if tracking_url:
        msg += f"🔗 Track here: {tracking_url}\n"

    msg += "\nExpected delivery: 3–7 business days\n\nFor any questions, reply to this message 😊"
    return msg


def build_owner_courier_alert(order: dict) -> str:
    """
    Builds WhatsApp alert to owner when customer mentions a courier preference.
    """
    return f"""⚠️ KITPAK Courier Alert

Order: {order.get('invoice_no', 'N/A')}
Customer: {order.get('name', 'N/A')}
Pincode: {order.get('pincode', 'N/A')}
Auto-assigned courier: {order.get('courier', 'N/A')}

Special instruction from customer:
"{order.get('special_instructions', 'N/A')}"

Please review before dispatch!"""
