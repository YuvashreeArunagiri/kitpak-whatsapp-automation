"""
KITPAK — Google Sheets Daily Report Service
Sends a daily summary of orders and enquiries to Google Sheets at 6 PM.
"""

import os
import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = '1MTTNafD-WyWsvQrRw0seRGqtO35E25O2s91m5yVDN8I'
TOKEN_FILE = 'google_token.json'
CREDENTIALS_FILE = 'google_credentials.json'


def get_sheets_service():
    """Authenticate and return Google Sheets service."""
    creds = None

    # Load existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('sheets', 'v4', credentials=creds)


def append_daily_report(conversation_history: dict):
    """
    Generates and appends daily report to Google Sheet.
    Called at 6 PM every day.
    """
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        today = datetime.now().strftime('%d %b %Y')
        now = datetime.now().strftime('%I:%M %p')

        # Count stats from conversation history
        total_conversations = len(conversation_history)
        orders_placed = 0
        enquiries = 0

        for phone, history in conversation_history.items():
            has_pi = any('GENERATE_PI:' in msg.get('content', '') for msg in history)
            if has_pi:
                orders_placed += 1
            else:
                enquiries += 1

        # Prepare row
        row = [today, now, total_conversations, orders_placed, enquiries, '']

        # Check if header exists, add if not
        result = sheet.values().get(spreadsheetId=SHEET_ID, range='Sheet1!A1:F1').execute()
        values = result.get('values', [])
        if not values:
            header = [['Date', 'Time', 'Total Conversations', 'Orders Placed', 'Enquiries Only', 'Notes']]
            sheet.values().update(
                spreadsheetId=SHEET_ID,
                range='Sheet1!A1',
                valueInputOption='RAW',
                body={'values': header}
            ).execute()

        # Append data row
        sheet.values().append(
            spreadsheetId=SHEET_ID,
            range='Sheet1!A:F',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': [row]}
        ).execute()

        print(f"[KITPAK] Daily report sent to Google Sheets: {today}")
        return True

    except Exception as e:
        print(f"[KITPAK] Google Sheets error: {e}")
        return False


def append_order_to_sheet(phone: str, order: dict):
    """
    Appends a single order to the Orders sheet immediately when placed.
    """
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        now = datetime.now().strftime('%d %b %Y %I:%M %p')

        items_str = ', '.join([f"{i['desc']} x{i['qty']}" for i in order.get('items', [])])
        total = sum(i['qty'] * i['rate'] for i in order.get('items', []))

        row = [
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

        # Check/add header for Orders sheet
        try:
            result = sheet.values().get(spreadsheetId=SHEET_ID, range='Orders!A1:J1').execute()
            values = result.get('values', [])
        except:
            values = []

        if not values:
            header = [['Date', 'Customer Name', 'Phone', 'Address', 'Pincode', 'State', 'Items', 'Total', 'GSTIN', 'Status']]
            sheet.values().update(
                spreadsheetId=SHEET_ID,
                range='Orders!A1',
                valueInputOption='RAW',
                body={'values': header}
            ).execute()

        sheet.values().append(
            spreadsheetId=SHEET_ID,
            range='Orders!A:J',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': [row]}
        ).execute()

        print(f"[KITPAK] Order logged to Google Sheets for {phone}")
        return True

    except Exception as e:
        print(f"[KITPAK] Google Sheets order log error: {e}")
        return False
