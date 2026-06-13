"""
KITPAK — Google Sheets logging via Apps Script Web App
No OAuth needed — uses a deployed Apps Script web app URL.
"""

import os
import requests
from datetime import datetime

# Set this to your deployed Apps Script web app URL (ends in /exec)
APPS_SCRIPT_URL = os.environ.get('GOOGLE_SHEETS_WEBHOOK_URL', '')


def append_order_to_sheet(phone: str, order: dict):
    """Appends a single order to the Orders sheet via Apps Script."""
    if not APPS_SCRIPT_URL:
        print("[KITPAK] GOOGLE_SHEETS_WEBHOOK_URL not set — skipping sheet log")
        return False

    try:
        now = datetime.now().strftime('%d %b %Y %I:%M %p')
        items_str = ', '.join([f"{i['desc']} x{i['qty']}" for i in order.get('items', [])])
        total = sum(i['qty'] * i['rate'] for i in order.get('items', []))

        payload = {
            "sheet": "Orders",
            "header": ["Date", "Customer Name", "Phone", "Address", "Pincode", "State", "Items", "Total", "GSTIN", "Status"],
            "row": [
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
        }

        response = requests.post(APPS_SCRIPT_URL, json=payload, timeout=15)
        print(f"[KITPAK] Sheets response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            print(f"[KITPAK] Order logged to Google Sheets for {phone}")
            return True
        return False

    except Exception as e:
        print(f"[KITPAK] Google Sheets order log error: {e}")
        return False


def append_daily_report(conversation_history: dict):
    """Appends daily summary to Sheet1 via Apps Script."""
    if not APPS_SCRIPT_URL:
        print("[KITPAK] GOOGLE_SHEETS_WEBHOOK_URL not set — skipping daily report")
        return False

    try:
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

        payload = {
            "sheet": "Sheet1",
            "header": ["Date", "Time", "Total Conversations", "Orders Placed", "Enquiries Only", "Notes"],
            "row": [today, now, total_conversations, orders_placed, enquiries, '']
        }

        response = requests.post(APPS_SCRIPT_URL, json=payload, timeout=15)
        print(f"[KITPAK] Daily report response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            print(f"[KITPAK] Daily report sent to Google Sheets: {today}")
            return True
        return False

    except Exception as e:
        print(f"[KITPAK] Google Sheets error: {e}")
        return False
