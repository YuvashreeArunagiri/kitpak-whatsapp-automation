"""
KITPAK — Google Sheets logging via Apps Script Web App
No OAuth needed — uses a deployed Apps Script web app URL.
"""
import os
import re
import requests
from datetime import datetime

APPS_SCRIPT_URL = os.environ.get('GOOGLE_SHEETS_WEBHOOK_URL', '')


def _post_to_sheet(sheet_name: str, header: list, row: list) -> bool:
    """Generic helper to append a row to any sheet via Apps Script."""
    if not APPS_SCRIPT_URL:
        print("[KITPAK] GOOGLE_SHEETS_WEBHOOK_URL not set — skipping sheet log")
        return False
    try:
        payload = {
            "sheet": sheet_name,
            "header": header,
            "row": row
        }
        response = requests.post(APPS_SCRIPT_URL, json=payload, timeout=15)
        print(f"[KITPAK] Sheets ({sheet_name}) response: {response.status_code} - {response.text[:200]}")
        return response.status_code == 200
    except Exception as e:
        print(f"[KITPAK] Sheets ({sheet_name}) error: {e}")
        return False


def generate_order_id(phone: str) -> str:
    """Generate a unique order ID based on timestamp and last 4 digits of phone."""
    now = datetime.now()
    return f"KP-{now.strftime('%y%m%d')}-{phone[-4:]}"


def append_order_to_sheet(phone: str, order: dict, order_id: str = '') -> bool:
    """Appends a confirmed order to the Orders sheet with Order ID."""
    now = datetime.now().strftime('%d %b %Y %I:%M %p')
    items_str = ', '.join([f"{i['desc']} x{i['qty']}" for i in order.get('items', [])])
    total = sum(i['qty'] * i['rate'] for i in order.get('items', []))
    return _post_to_sheet(
        sheet_name="Orders",
        header=["Order ID", "Date", "Customer Name", "Phone", "Address", "Pincode", "State", "Items", "Total", "GSTIN", "Status"],
        row=[
            order_id,
            now,
            order.get('customer_name', ''),
            phone,
            order.get('address', ''),
            order.get('pincode', ''),
            order.get('state', ''),
            items_str,
            f"Rs. {total:,.2f}",
            order.get('gstin', ''),
            'Pending Payment'
        ]
    )


def append_handoff_to_sheet(phone: str, customer_name: str, reason: str, last_message: str) -> bool:
    """
    Logs a team-handoff conversation to the HandoffConversations sheet.
    Columns: Date | Customer Phone | Customer Name | Reason | Last Message | Status | Notes
    """
    now = datetime.now().strftime('%d %b %Y %I:%M %p')
    return _post_to_sheet(
        sheet_name="HandoffConversations",
        header=["Date", "Customer Phone", "Customer Name", "Reason", "Last Message", "Status", "Notes"],
        row=[
            now,
            phone,
            customer_name or '',
            reason,
            last_message[:200] if last_message else '',
            'Pending Follow-up',
            ''
        ]
    )


def append_bulk_enquiry_to_sheet(phone: str, customer_name: str, product: str, quantity: str, state: str, reason: str) -> bool:
    """
    Logs a bulk enquiry to the BulkEnquiries sheet.
    Columns: Date | Customer Phone | Customer Name | Product Interest | Quantity | State | Reason | Status | Notes
    """
    now = datetime.now().strftime('%d %b %Y %I:%M %p')
    return _post_to_sheet(
        sheet_name="BulkEnquiries",
        header=["Date", "Customer Phone", "Customer Name", "Product Interest", "Quantity", "State", "Reason", "Status", "Notes"],
        row=[
            now,
            phone,
            customer_name or '',
            product or 'Not specified',
            quantity or 'Not specified',
            state or 'Not specified',
            reason,
            'Pending Follow-up',
            ''
        ]
    )


def append_daily_report(conversation_history: dict) -> bool:
    """Appends daily summary to Sheet1 via Apps Script."""
    today = datetime.now().strftime('%d %b %Y')
    now = datetime.now().strftime('%I:%M %p')
    total_conversations = len(conversation_history)
    orders_placed = 0
    enquiries = 0
    for phone, history in conversation_history.items():
        has_pi = any('GENERATE_PI:' in msg.get('content', '') for msg in history)
        if has_pi:
            orders_placed += 1
        else:
            enquiries += 1
    return _post_to_sheet(
        sheet_name="Sheet1",
        header=["Date", "Time", "Total Conversations", "Orders Placed", "Enquiries Only", "Notes"],
        row=[today, now, total_conversations, orders_placed, enquiries, '']
    )
