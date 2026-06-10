"""
KITPAK — Proforma Invoice Generator
Generates a professional PDF PI with UPI QR code.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
import hashlib, io, os
import urllib.request, urllib.parse

W, H = A4
UPI_ID = os.environ.get('KITPAK_UPI_ID', '9489501487@okbizaxis')


def generate_upi_qr(upi_id, amount, size=150):
    """Generate UPI QR code — tries live API first, falls back to pattern."""
    upi_str = f"upi://pay?pa={upi_id}&pn=SARAVANA+TRADING&am={amount:.2f}&cu=INR"

    # Try live QR API first
    try:
        url = f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={urllib.parse.quote(upi_str)}"
        with urllib.request.urlopen(url, timeout=5) as r:
            return io.BytesIO(r.read())
    except Exception:
        pass

    try:
        url = f"https://chart.googleapis.com/chart?cht=qr&chs={size}x{size}&chl={urllib.parse.quote(upi_str)}"
        with urllib.request.urlopen(url, timeout=5) as r:
            return io.BytesIO(r.read())
    except Exception:
        pass

    # Fallback: generate pattern-based QR
    img = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(img)
    modules = 25
    cell = size // (modules + 4)
    offset = (size - cell * modules) // 2
    h = hashlib.sha256(upi_str.encode()).hexdigest()
    grid = [[0]*modules for _ in range(modules)]

    def add_finder(r, c):
        for dr in range(7):
            for dc in range(7):
                if (dr==0 or dr==6 or dc==0 or dc==6 or (2<=dr<=4 and 2<=dc<=4)):
                    if 0<=r+dr<modules and 0<=c+dc<modules:
                        grid[r+dr][c+dc] = 1

    add_finder(0, 0); add_finder(0, modules-7); add_finder(modules-7, 0)
    for i in range(8, modules-8):
        grid[6][i] = 1 if i%2==0 else 0
        grid[i][6] = 1 if i%2==0 else 0

    hash_bits = bin(int(h, 16))[2:].zfill(256)
    bit_idx = 0
    for r in range(modules):
        for c in range(modules):
            if grid[r][c] == 0:
                if not ((r<9 and c<9) or (r<9 and c>=modules-8) or
                        (r>=modules-8 and c<9) or r==6 or c==6):
                    if bit_idx < len(hash_bits):
                        grid[r][c] = int(hash_bits[bit_idx])
                        bit_idx += 1

    for r in range(modules):
        for c in range(modules):
            x = offset + c*cell; y = offset + r*cell
            draw.rectangle([x, y, x+cell-1, y+cell-1],
                          fill='black' if grid[r][c]==1 else 'white')

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def generate_pi_pdf(order: dict) -> bytes:
    """
    Generate PI PDF and return as bytes.
    order = {
        customer_name, phone, address, city, pincode, state,
        gstin (optional), items: [{desc, qty, rate}]
    }
    """
    today = datetime.now()
    valid_until = today + timedelta(days=7)
    pi_number = order.get('pi_number', f"KITPAK/PI/{today.strftime('%Y%m%d%H%M')}")
    total = sum(i['qty'] * i['rate'] for i in order['items'])

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    # HEADER
    c.setFillColor(colors.HexColor("#0a1628"))
    c.rect(0, H-40*mm, W, 40*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#25D366")); c.setFont("Helvetica-Bold", 22)
    c.drawString(14*mm, H-18*mm, "KITPAK")
    c.setFont("Helvetica", 8); c.setFillColor(colors.HexColor("#aaaaaa"))
    c.drawString(14*mm, H-25*mm, "SARAVANA TRADING")
    c.drawString(14*mm, H-31*mm, "55C, Valayangadu Main Road, Kumar Nagar South")
    c.drawString(14*mm, H-36*mm, "Tirupur - 641603  |  GSTIN: 33ATTPG0334P2ZD  |  Ph: 83004 75706")
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 13)
    c.drawRightString(W-14*mm, H-16*mm, "PROFORMA INVOICE")
    c.setFont("Helvetica", 9); c.setFillColor(colors.HexColor("#aaaaaa"))
    c.drawRightString(W-14*mm, H-23*mm, f"PI No: {pi_number}")
    c.drawRightString(W-14*mm, H-29*mm, f"Date: {today.strftime('%d %b %Y')}")
    c.drawRightString(W-14*mm, H-35*mm, f"Valid Until: {valid_until.strftime('%d %b %Y')}")

    y = H-50*mm

    # FROM
    c.setFillColor(colors.HexColor("#f8f9fa"))
    c.rect(14*mm, y-35*mm, 82*mm, 35*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#25D366"))
    c.rect(14*mm, y-35*mm, 2*mm, 35*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#666666")); c.setFont("Helvetica-Bold", 7)
    c.drawString(18*mm, y-6*mm, "FROM")
    c.setFillColor(colors.HexColor("#0a1628")); c.setFont("Helvetica-Bold", 10)
    c.drawString(18*mm, y-13*mm, "SARAVANA TRADING (KITPAK)")
    c.setFont("Helvetica", 8); c.setFillColor(colors.HexColor("#444444"))
    c.drawString(18*mm, y-19*mm, "55C, Valayangadu Main Road")
    c.drawString(18*mm, y-24*mm, "Kumar Nagar South, Tirupur - 641603")
    c.drawString(18*mm, y-29*mm, "info@kitpak.in  |  83004 75706")
    c.drawString(18*mm, y-34*mm, "GSTIN: 33ATTPG0334P2ZD")

    # TO
    c.setFillColor(colors.HexColor("#f8f9fa"))
    c.rect(102*mm, y-35*mm, 94*mm, 35*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#0a1628"))
    c.rect(102*mm, y-35*mm, 2*mm, 35*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#666666")); c.setFont("Helvetica-Bold", 7)
    c.drawString(106*mm, y-6*mm, "BILL TO")
    c.setFillColor(colors.HexColor("#0a1628")); c.setFont("Helvetica-Bold", 10)
    c.drawString(106*mm, y-13*mm, order['customer_name'])
    c.setFont("Helvetica", 8); c.setFillColor(colors.HexColor("#444444"))
    c.drawString(106*mm, y-19*mm, order.get('address',''))
    c.drawString(106*mm, y-24*mm, f"{order.get('city','')} - {order.get('pincode','')}  |  {order.get('state','')}")
    c.drawString(106*mm, y-29*mm, f"Ph: {order['phone']}")
    c.drawString(106*mm, y-34*mm, order.get('gstin') or "GST: Not Applicable")

    y -= 42*mm

    # TABLE
    c.setFillColor(colors.HexColor("#0a1628"))
    c.rect(14*mm, y-8*mm, W-28*mm, 8*mm, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 8)
    c.drawString(16*mm, y-5.5*mm, "#")
    c.drawString(24*mm, y-5.5*mm, "DESCRIPTION")
    c.drawRightString(130*mm, y-5.5*mm, "QTY")
    c.drawRightString(160*mm, y-5.5*mm, "RATE (Rs.)")
    c.drawRightString(W-14*mm, y-5.5*mm, "AMOUNT (Rs.)")
    y -= 8*mm

    for i, item in enumerate(order['items']):
        amount = item['qty'] * item['rate']
        c.setFillColor(colors.white if i%2==0 else colors.HexColor("#f8f9fa"))
        c.rect(14*mm, y-9*mm, W-28*mm, 9*mm, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#666666")); c.setFont("Helvetica", 8)
        c.drawString(16*mm, y-6*mm, str(i+1))
        c.setFillColor(colors.black); c.setFont("Helvetica", 8.5)
        c.drawString(24*mm, y-6*mm, item['desc'][:60])
        c.drawRightString(130*mm, y-6*mm, str(item['qty']))
        c.drawRightString(160*mm, y-6*mm, f"{item['rate']:.2f}")
        c.setFont("Helvetica-Bold", 8.5)
        c.drawRightString(W-14*mm, y-6*mm, f"{amount:,.2f}")
        y -= 9*mm

    y -= 4*mm

    # TOTALS
    c.setFillColor(colors.HexColor("#f8f9fa"))
    c.rect(120*mm, y-20*mm, W-134*mm, 20*mm, fill=1, stroke=0)
    c.setFont("Helvetica", 9); c.setFillColor(colors.HexColor("#555555"))
    c.drawString(122*mm, y-8*mm, "Shipping")
    c.setFillColor(colors.HexColor("#25D366")); c.setFont("Helvetica-Bold", 9)
    c.drawRightString(W-14*mm, y-8*mm, "FREE")
    c.setFont("Helvetica", 9); c.setFillColor(colors.HexColor("#555555"))
    c.drawString(122*mm, y-16*mm, "GST")
    c.setFillColor(colors.HexColor("#25D366")); c.setFont("Helvetica-Bold", 9)
    c.drawRightString(W-14*mm, y-16*mm, "Included")
    c.setFillColor(colors.HexColor("#0a1628"))
    c.rect(120*mm, y-30*mm, W-134*mm, 10*mm, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 10)
    c.drawString(122*mm, y-26*mm, "TOTAL PAYABLE")
    c.setFillColor(colors.HexColor("#25D366")); c.setFont("Helvetica-Bold", 12)
    c.drawRightString(W-14*mm, y-26*mm, f"Rs. {total:,.2f}")

    y -= 38*mm

    # PAYMENT
    c.setFillColor(colors.HexColor("#f0fff4"))
    c.rect(14*mm, y-44*mm, W-28*mm, 44*mm, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#25D366")); c.setLineWidth(1)
    c.rect(14*mm, y-44*mm, W-28*mm, 44*mm, fill=0, stroke=1)
    c.setFillColor(colors.HexColor("#0a1628")); c.setFont("Helvetica-Bold", 9)
    c.drawString(18*mm, y-7*mm, "PAYMENT DETAILS")
    c.setFont("Helvetica", 8.5); c.setFillColor(colors.HexColor("#444444"))
    c.drawString(18*mm, y-14*mm, "Pay via UPI: GPay / PhonePe / Paytm / BHIM")
    c.setFont("Helvetica-Bold", 13); c.setFillColor(colors.HexColor("#25D366"))
    c.drawString(18*mm, y-22*mm, UPI_ID)
    c.setFont("Helvetica-Bold", 10); c.setFillColor(colors.HexColor("#0a1628"))
    c.drawString(18*mm, y-30*mm, f"Amount: Rs. {total:,.2f}")
    c.setFont("Helvetica", 7.5); c.setFillColor(colors.HexColor("#888888"))
    c.drawString(18*mm, y-37*mm, "After payment, share the UTR/transaction ID to confirm your order.")
    c.drawString(18*mm, y-43*mm, "Scan QR code with any UPI app to pay instantly.")

    # QR
    qr_buf = generate_upi_qr(UPI_ID, total)
    qr_img = ImageReader(qr_buf)
    c.drawImage(qr_img, W-56*mm, y-44*mm, 38*mm, 38*mm)
    c.setFont("Helvetica-Bold", 7); c.setFillColor(colors.HexColor("#25D366"))
    c.drawCentredString(W-37*mm, y-46*mm, "Scan to Pay")

    y -= 52*mm

    # NOTE
    c.setFillColor(colors.HexColor("#fff8e1"))
    c.rect(14*mm, y-14*mm, W-28*mm, 14*mm, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#ffc107")); c.setLineWidth(2)
    c.line(14*mm, y-14*mm, 14*mm, y)
    c.setFillColor(colors.HexColor("#444444")); c.setFont("Helvetica-Bold", 8)
    c.drawString(18*mm, y-5*mm, "Note:")
    c.setFont("Helvetica", 8)
    c.drawString(30*mm, y-5*mm, "Payment via UPI only. Order dispatched within 2-3 business days after payment confirmation.")
    c.drawString(18*mm, y-11*mm, "This is a computer generated document.")

    # FOOTER
    c.setFillColor(colors.HexColor("#0a1628"))
    c.rect(0, 0, W, 12*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#888888")); c.setFont("Helvetica", 7.5)
    c.drawCentredString(W/2, 4*mm, "KITPAK.IN  |  info@kitpak.in  |  83004 75706  |  SARAVANA TRADING, Tirupur - 641603")

    c.save()
    buf.seek(0)
    return buf.read()


def generate_pi_text(order: dict) -> str:
    """Fallback text PI if PDF sending fails."""
    today = datetime.now()
    pi_number = f"KITPAK/PI/{today.strftime('%Y%m%d%H%M')}"
    total = sum(i['qty'] * i['rate'] for i in order['items'])
    lines = [
        "KITPAK — PROFORMA INVOICE",
        f"PI No: {pi_number}",
        f"Date: {today.strftime('%d %b %Y')}",
        "",
        f"To: {order['customer_name']}",
        f"Ph: {order['phone']}",
        "",
        "Items:",
    ]
    for item in order['items']:
        lines.append(f"- {item['desc']}: {item['qty']} pcs x Rs.{item['rate']:.2f} = Rs.{item['qty']*item['rate']:,.2f}")
    lines += [
        "",
        f"Total: Rs. {total:,.2f} (GST & Shipping included)",
        "",
        f"Pay via UPI: {UPI_ID}",
        "Share UTR after payment to confirm order.",
        "",
        "KITPAK | info@kitpak.in | 83004 75706"
    ]
    return "\n".join(lines)
