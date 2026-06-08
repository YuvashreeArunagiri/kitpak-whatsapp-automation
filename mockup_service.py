"""
KITPAK — Mockup Generator Service
Places customer logo on bag template and adds watermark disclaimer.
"""

from PIL import Image, ImageDraw, ImageFont
import os
import io

# ─── Config ───────────────────────────────────────────────
BAGS_DIR = os.path.join(os.path.dirname(__file__), "templates", "bags")

BAG_TEMPLATES = {
    "white":  os.path.join(BAGS_DIR, "bag_white.png"),
    "pink":   os.path.join(BAGS_DIR, "bag_pink.png"),
    "purple": os.path.join(BAGS_DIR, "bag_purple.png"),
    "black":  os.path.join(BAGS_DIR, "bag_black.png"),
}

DISCLAIMER_TEXT = "For representation purposes only. Not to be replicated or reproduced."

# Logo placement config (based on sample mockup)
LOGO_SIZE_RATIO   = 0.38   # Logo width = 38% of bag width
LOGO_CENTER_X     = 0.50   # Horizontally centred
LOGO_CENTER_Y     = 0.42   # Slightly above centre vertically


def generate_mockup(
    logo_path: str,
    bag_colour: str = "white",
    output_path: str = None
) -> bytes:
    """
    Places customer logo on bag template with watermark.
    
    Args:
        logo_path   : Path to customer's logo file (PNG/JPG)
        bag_colour  : white / pink / purple / black
        output_path : Optional path to save the mockup

    Returns:
        PNG bytes of the generated mockup
    """

    bag_colour = bag_colour.lower().strip()
    if bag_colour not in BAG_TEMPLATES:
        bag_colour = "white"

    # Load bag template
    bag = Image.open(BAG_TEMPLATES[bag_colour]).convert("RGBA")
    bag_w, bag_h = bag.size

    # Load customer logo
    logo = Image.open(logo_path).convert("RGBA")
    logo_w, logo_h = logo.size

    # Resize logo — 38% of bag width
    target_w = int(bag_w * LOGO_SIZE_RATIO)
    ratio = target_w / logo_w
    target_h = int(logo_h * ratio)
    logo = logo.resize((target_w, target_h), Image.LANCZOS)

    # Calculate logo position — centred
    logo_x = int(bag_w * LOGO_CENTER_X) - target_w // 2
    logo_y = int(bag_h * LOGO_CENTER_Y) - target_h // 2

    # Paste logo onto bag
    mockup = bag.copy()
    mockup.paste(logo, (logo_x, logo_y), logo)

    # Add diagonal watermark
    mockup = _add_watermark(mockup, DISCLAIMER_TEXT)

    # Convert to RGB for JPEG output
    output = mockup.convert("RGB")

    # Save or return bytes
    if output_path:
        output.save(output_path, "PNG", quality=95)

    buf = io.BytesIO()
    output.save(buf, format="PNG", quality=95)
    return buf.getvalue()


def _add_watermark(image: Image.Image, text: str) -> Image.Image:
    """Adds a diagonal watermark across the image."""

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    w, h = image.size

    # Try to load a font, fall back to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font = ImageFont.load_default()

    # Draw watermark text diagonally — 3 times across the bag
    for i in range(3):
        x = w * 0.1 + i * (w * 0.3)
        y = h * 0.55 + i * (h * 0.05)
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 80))

    # Also add a single bold line across the centre
    draw.text(
        (w * 0.08, h * 0.72),
        "⚠ " + text,
        font=font,
        fill=(0, 0, 0, 100)
    )

    # Composite overlay onto image
    watermarked = Image.alpha_composite(image.convert("RGBA"), overlay)
    return watermarked


def get_mockup_caption() -> str:
    """Returns the WhatsApp caption to send with the mockup."""
    return (
        "Please find your logo mockup for reference.\n\n"
        "Note: This is for representation purposes only. "
        "Final print colours and placement may vary slightly. "
        "This mockup is not to be replicated or reproduced.\n\n"
        "Please confirm if you would like to proceed with this design, "
        "or let us know if you need any changes."
    )
