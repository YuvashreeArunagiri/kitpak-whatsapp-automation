"""
KITPAK — Proforma Invoice Generator
Generates a professional PDF PI with UPI QR code, branded with KITPAK colors and logo.
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

# KITPAK Brand Colors
DARK_TEAL = "#2C4A52"
ORANGE = "#F47B20"
WHITE = "#FFFFFF"
LIGHT_GRAY = "#F5F6F7"
MID_GRAY = "#888888"
DARK_GRAY = "#444444"

# Path to logo — place kitpak_logo.png in the project root
LOGO_PATH = os.path.join(os.path.dirname(__file__), "kitpak_logo.png")


def generate_upi_qr(upi_id, amount, size=150):
    """Generate UPI QR code — tries live API first, falls back to pattern."""
    upi_str = f"upi://pay?pa={upi_id}&pn=SARAVANA+TRADING&am={amount:.2f}&cu=INR"

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

    # ── HEADER ──────────────────────────────────────────────
    c.setFillColor(colors.HexColor(DARK_TEAL))
    c.rect(0, H-45*mm, W, 45*mm, fill=1, stroke=0)

    # Orange accent bar on left
    c.setFillColor(colors.HexColor(ORANGE))
    c.rect(0, H-45*mm, 4*mm, 45*mm, fill=1, stroke=0)

    # Logo image (falls back to text if not found)
    logo_drawn = False
    if os.path.exists(LOGO_PATH):
        try:
            logo = ImageReader(LOGO_PATH)
            c.drawImage(logo, 10*mm, H-40*mm, 45*mm, 30*mm, preserveAspectRatio=True, mask='auto')
            logo_drawn = True
        except Exception:
            pass

    if not logo_drawn:
        c.setFillColor(colors.HexColor(ORANGE))
        c.setFont("Helvetica-Bold", 24)
        c.drawString(10*mm, H-20*mm, "K")
        c.setFillColor(colors.HexColor(WHITE))
        c.setFont("Helvetica-Bold", 24)
        c.drawString(21*mm, H-20*mm, "itpak")

    # Company info
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.HexColor("#aaaaaa"))
    c.drawString(10*mm, H-36*mm, "SARAVANA TRADING")
    c.drawString(10*mm, H-41*mm, "55C, Valayangadu Main Road, Kumar Nagar South, Tirupur - 641603")

    # PI title on right
    c.setFillColor(colors.HexColor(WHITE))
    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(W-10*mm, H-16*mm, "PROFORMA INVOICE")

    # Orange underline for title
    c.setStrokeColor(colors.HexColor(ORANGE))
    c.setLineWidth(1.5)
    c.line(W-80*mm, H-18*mm, W-10*mm, H-18*mm)

    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.HexColor("#cccccc"))
    c.drawRightString(W-10*mm, H-24*mm, f"PI No: {pi_number}")
    c.drawRightString(W-10*mm, H-30*mm, f"Date: {today.strftime('%d %b %Y')}")
    c.drawRightString(W-10*mm, H-36*mm, f"Valid Until: {valid_until.strftime('%d %b %Y')}")
    c.drawRightString(W-10*mm, H-42*mm, f"GSTIN: 33ATTPG0334P2ZD")

    y = H - 53*mm

    # ── FROM / TO BOXES ───────────────────────────────────────
    box_h = 36*mm

    # FROM box
    c.setFillColor(colors.HexColor(LIGHT_GRAY))
    c.rect(10*mm, y-box_h, 88*mm, box_h, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(ORANGE))
    c.rect(10*mm, y-box_h, 3*mm, box_h, fill=1, stroke=0)

    c.setFillColor(colors.HexColor(DARK_TEAL))
    c.setFont("Helvetica-Bold", 7)
    c.drawString(15*mm, y-6*mm, "FROM")
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(15*mm, y-13*mm, "SARAVANA TRADING (KITPAK)")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor(DARK_GRAY))
    c.drawString(15*mm, y-19*mm, "55C, Valayangadu Main Road")
    c.drawString(15*mm, y-24*mm, "Kumar Nagar South, Tirupur - 641603")
    c.drawString(15*mm, y-29*mm, "info@kitpak.in  |  83004 75706")
    c.drawString(15*mm, y-34*mm, "GSTIN: 33ATTPG0334P2ZD")

    # TO box
    c.setFillColor(colors.HexColor(LIGHT_GRAY))
    c.rect(103*mm, y-box_h, 97*mm, box_h, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(DARK_TEAL))
    c.rect(103*mm, y-box_h, 3*mm, box_h, fill=1, stroke=0)

    c.setFillColor(colors.HexColor(DARK_TEAL))
    c.setFont("Helvetica-Bold", 7)
    c.drawString(108*mm, y-6*mm, "BILL TO")
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(108*mm, y-13*mm, order['customer_name'])
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor(DARK_GRAY))
    c.drawString(108*mm, y-19*mm, order.get('address', ''))
    c.drawString(108*mm, y-24*mm, f"{order.get('city','')} - {order.get('pincode','')}  |  {order.get('state','')}")
    c.drawString(108*mm, y-29*mm, f"Ph: {order['phone']}")
    c.drawString(108*mm, y-34*mm, order.get('gstin') or "GST: Not Applicable")

    y -= box_h + 6*mm

    # ── TABLE ──────────────────────────────────────────────────
    c.setFillColor(colors.HexColor(DARK_TEAL))
    c.rect(10*mm, y-8*mm, W-20*mm, 8*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(WHITE))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(13*mm, y-5.5*mm, "#")
    c.drawString(22*mm, y-5.5*mm, "DESCRIPTION")
    c.drawRightString(128*mm, y-5.5*mm, "QTY")
    c.drawRightString(158*mm, y-5.5*mm, "RATE (Rs.)")
    c.drawRightString(W-10*mm, y-5.5*mm, "AMOUNT (Rs.)")
    y -= 8*mm

    for i, item in enumerate(order['items']):
        amount = item['qty'] * item['rate']
        bg = colors.white if i % 2 == 0 else colors.HexColor(LIGHT_GRAY)
        c.setFillColor(bg)
        c.rect(10*mm, y-9*mm, W-20*mm, 9*mm, fill=1, stroke=0)
        c.setFillColor(colors.HexColor(MID_GRAY))
        c.setFont("Helvetica", 8)
        c.drawString(13*mm, y-6*mm, str(i+1))
        c.setFillColor(colors.HexColor(DARK_GRAY))
        c.setFont("Helvetica", 8.5)
        c.drawString(22*mm, y-6*mm, item['desc'][:65])
        c.drawRightString(128*mm, y-6*mm, str(item['qty']))
        c.drawRightString(158*mm, y-6*mm, f"{item['rate']:.2f}")
        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(colors.HexColor(DARK_TEAL))
        c.drawRightString(W-10*mm, y-6*mm, f"{amount:,.2f}")
        y -= 9*mm

    y -= 4*mm

    # Totals
    c.setFillColor(colors.HexColor(LIGHT_GRAY))
    c.rect(118*mm, y-22*mm, W-128*mm, 22*mm, fill=1, stroke=0)
    c.setFont("Helvetica", 9); c.setFillColor(colors.HexColor(DARK_GRAY))
    c.drawString(121*mm, y-8*mm, "Shipping")
    c.setFillColor(colors.HexColor(ORANGE)); c.setFont("Helvetica-Bold", 9)
    c.drawRightString(W-10*mm, y-8*mm, "FREE")
    c.setFont("Helvetica", 9); c.setFillColor(colors.HexColor(DARK_GRAY))
    c.drawString(121*mm, y-16*mm, "GST")
    c.setFillColor(colors.HexColor(ORANGE)); c.setFont("Helvetica-Bold", 9)
    c.drawRightString(W-10*mm, y-16*mm, "Included")

    # Total box
    c.setFillColor(colors.HexColor(DARK_TEAL))
    c.rect(118*mm, y-32*mm, W-128*mm, 10*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(WHITE)); c.setFont("Helvetica-Bold", 10)
    c.drawString(121*mm, y-28*mm, "TOTAL PAYABLE")
    c.setFillColor(colors.HexColor(ORANGE)); c.setFont("Helvetica-Bold", 12)
    c.drawRightString(W-10*mm, y-28*mm, f"Rs. {total:,.2f}")

    y -= 40*mm

    # ── PAYMENT SECTION ──────────────────────────────────────────
    c.setFillColor(colors.HexColor("#EEF7F0"))
    c.rect(10*mm, y-46*mm, W-20*mm, 46*mm, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(ORANGE))
    c.setLineWidth(1.5)
    c.rect(10*mm, y-46*mm, W-20*mm, 46*mm, fill=0, stroke=1)

    c.setFillColor(colors.HexColor(DARK_TEAL))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(15*mm, y-8*mm, "PAYMENT DETAILS")
    c.setStrokeColor(colors.HexColor(ORANGE))
    c.setLineWidth(1)
    c.line(15*mm, y-10*mm, 70*mm, y-10*mm)

    c.setFont("Helvetica", 8.5); c.setFillColor(colors.HexColor(DARK_GRAY))
    c.drawString(15*mm, y-17*mm, "Pay via UPI: GPay / PhonePe / Paytm / BHIM")
    c.setFont("Helvetica-Bold", 14); c.setFillColor(colors.HexColor(ORANGE))
    c.drawString(15*mm, y-26*mm, UPI_ID)
    c.setFont("Helvetica-Bold", 11); c.setFillColor(colors.HexColor(DARK_TEAL))
    c.drawString(15*mm, y-34*mm, f"Amount: Rs. {total:,.2f}")
    c.setFont("Helvetica", 7.5); c.setFillColor(colors.HexColor(MID_GRAY))
    c.drawString(15*mm, y-40*mm, "After payment, share the UTR / transaction screenshot to confirm your order.")
    c.drawString(15*mm, y-45*mm, "Scan QR code with any UPI app to pay instantly.")

    # QR code
    qr_buf = generate_upi_qr(UPI_ID, total)
    qr_img = ImageReader(qr_buf)
    c.drawImage(qr_img, W-58*mm, y-46*mm, 42*mm, 42*mm)
    c.setFont("Helvetica-Bold", 7); c.setFillColor(colors.HexColor(ORANGE))
    c.drawCentredString(W-37*mm, y-48*mm, "Scan to Pay")

    y -= 54*mm

    # ── NOTE ────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor("#FFF8E1"))
    c.rect(10*mm, y-18*mm, W-20*mm, 18*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(ORANGE))
    c.rect(10*mm, y-18*mm, 3*mm, 18*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(DARK_TEAL)); c.setFont("Helvetica-Bold", 8)
    c.drawString(15*mm, y-6*mm, "Note:")
    c.setFont("Helvetica", 8); c.setFillColor(colors.HexColor(DARK_GRAY))
    c.drawString(30*mm, y-6*mm, "Payment via UPI only. Custom printed covers take 10-14 days for delivery,")
    c.drawString(15*mm, y-12*mm, "other products dispatched on the same day if ordered before 6 PM.")
    c.drawString(15*mm, y-17*mm, "This is a computer generated document.")

    # ── FOOTER ──────────────────────────────────────────────────
    c.setFillColor(colors.HexColor(DARK_TEAL))
    c.rect(0, 0, W, 13*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(ORANGE))
    c.rect(0, 0, W, 1.5*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#aaaaaa")); c.setFont("Helvetica", 7.5)
    c.drawCentredString(W/2, 5*mm, "KITPAK.IN  |  info@kitpak.in  |  83004 75706  |  SARAVANA TRADING, Tirupur - 641603")

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
        "Note: Custom printed covers take 10-14 days for delivery,",
        "other products dispatched same day if ordered before 6 PM.",
        "",
        "KITPAK | info@kitpak.in | 83004 75706"
    ]
    return "\n".join(lines)
