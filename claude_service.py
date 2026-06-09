"""
KITPAK — Proforma Invoice Generator
Generates a text-based PI to send via WhatsApp
"""
from datetime import datetime, timedelta
import os

UPI_ID = os.environ.get('KITPAK_UPI_ID', '9489501487@okbizaxis')

def generate_pi_text(order: dict) -> str:
    """
    Generates a WhatsApp-friendly Proforma Invoice text.
    
    order = {
        'customer_name': str,
        'phone': str,
        'address': str,
        'pincode': str,
        'state': str,
        'gstin': str (optional),
        'items': [{'desc': str, 'qty': int, 'rate': float}]
    }
    """
    today = datetime.now()
    valid_until = today + timedelta(days=7)
    pi_number = f"KITPAK/PI/{today.strftime('%Y%m%d%H%M')}"

    total = sum(item['qty'] * item['rate'] for item in order['items'])

    lines = []
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("KITPAK — PROFORMA INVOICE")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"PI No: {pi_number}")
    lines.append(f"Date: {today.strftime('%d %b %Y')}")
    lines.append(f"Valid until: {valid_until.strftime('%d %b %Y')}")
    lines.append("")
    lines.append("FROM:")
    lines.append("SARAVANA TRADING (KITPAK)")
    lines.append("55C, Valayangadu Main Road")
    lines.append("Kumar Nagar South, Tirupur - 641605")
    lines.append("GSTIN: 33ATTPG0334P2ZD")
    lines.append("")
    lines.append("TO:")
    lines.append(order['customer_name'])
    lines.append(order['address'])
    lines.append(f"Pincode: {order['pincode']}")
    if order.get('state'):
        lines.append(order['state'])
    lines.append(f"Ph: {order['phone']}")
    if order.get('gstin'):
        lines.append(f"GSTIN: {order['gstin']}")
    else:
        lines.append("GST: Not applicable")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("ITEMS:")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")

    for i, item in enumerate(order['items'], 1):
        amount = item['qty'] * item['rate']
        lines.append(f"{i}. {item['desc']}")
        lines.append(f"   {item['qty']} pcs x ₹{item['rate']:.2f} = ₹{amount:.2f}")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"Shipping: FREE")
    lines.append(f"GST: Included")
    lines.append(f"TOTAL: ₹{total:,.2f}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("PAYMENT:")
    lines.append(f"UPI ID: {UPI_ID}")
    lines.append(f"Amount: ₹{total:,.2f}")
    lines.append("")
    lines.append("Pay via GPay / PhonePe / Paytm / BHIM")
    lines.append("After payment, please share the UTR number.")
    lines.append("")
    lines.append("Thank you for choosing KITPAK!")
    lines.append("KITPAK.IN | info@kitpak.in | 83004 75706")

    return "\n".join(lines)
