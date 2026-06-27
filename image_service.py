# image_service.py
# KITPAK — Product image catalogue
# Maps product categories to reference image filenames in images/ folder

PRODUCT_IMAGES = {

    "white_cover": [
        "white_cover_1.png",
        "white_cover_2.png",
        "white_cover_3.png",
    ],

    "colour_cover_black": [
        "black_cover_1.png",
        "black_cover_2.png",
    ],

    "colour_cover_pink": [
        "pink_cover_1.png",
        "pink_cover_2.png",
    ],

    "colour_cover_purple": [
        "purple_cover_1.png",
        "purple_cover_2.png",
    ],

    "colour_cover": [
        "black_cover_1.png",
        "pink_cover_1.png",
        "purple_cover_1.png",
    ],

    "custom_printed_white": [
        "custom_white_1.png",
        "custom_white_2.png",
        "custom_white_3.png",
        "custom_white_4.jpg",
        "custom_white_5.jpg",
        "custom_white_6.jpg",
    ],

    "custom_printed_colour": [
        "custom_colour_1.png",
        "custom_colour_2.png",
        "custom_colour_3.png",
        "custom_colour_4.png",
        "custom_colour_5.jpg",
        "custom_colour_6.jpg",
    ],

    "transparent_cover": [
        "transparent_cover_1.jpg",
    ],

    "meesho_cover": [
        "meesho_cover_1.jpg",
    ],

    "amazon_cover": [
        "amazon_cover_1.png",
    ],

    "flipkart_cover": [
        "flipkart_cover_1.jpg",
    ],

    "paper_bag_kraft": [
        "paper_cover_kraft_1.jpg",
    ],

    "honeycomb_roll": [
        "honeycomb_roll_1.png",
        "honeycomb_roll_2.png",
        "honeycomb_roll_3.png",
        "honeycomb_roll_4.jpg",
    ],

    "honeycomb_sleeve": [
        "honeycomb_sleeve_1.jpg",
        "honeycomb_sleeve_2.jpg",
        "honeycomb_sleeve_3.png",
        "honeycomb_sleeve_4.png",
    ],

    "thermal_label_roll": [
        "thermal_label_roll_1.jpg",
        "thermal_label_roll_2.jpg",
    ],

    "thermal_label_a4": [
        "thermal_label_a4_1.jpg",
        "thermal_label_a4_2.jpg",
        "thermal_label_a4_3.jpg",
    ],
}

# Keyword mapping — comprehensive, covers all common customer phrasings
KEYWORD_MAP = {
    # ── White courier covers ──
    "white cover": "white_cover",
    "white courier": "white_cover",
    "white bag": "white_cover",
    "white mailer": "white_cover",
    "plain cover": "white_cover",
    "plain white": "white_cover",
    "courier cover": "white_cover",
    "courier bag": "white_cover",
    "mailer bag": "white_cover",
    "mailer cover": "white_cover",
    "packing cover": "white_cover",
    "packing bag": "white_cover",
    "shipping cover": "white_cover",
    "shipping bag": "white_cover",
    "dispatch cover": "white_cover",
    "dispatch bag": "white_cover",
    "poly bag": "white_cover",
    "polybag": "white_cover",
    "flap cover": "white_cover",
    "d2c bag": "white_cover",
    "ecommerce bag": "white_cover",
    "e-commerce bag": "white_cover",
    "delivery bag": "white_cover",
    "delivery cover": "white_cover",
    "tamper proof": "white_cover",
    "tamper evident": "white_cover",

    # ── Colour covers ──
    "black cover": "colour_cover_black",
    "black bag": "colour_cover_black",
    "black courier": "colour_cover_black",
    "black mailer": "colour_cover_black",
    "pink cover": "colour_cover_pink",
    "pink bag": "colour_cover_pink",
    "pink courier": "colour_cover_pink",
    "pink mailer": "colour_cover_pink",
    "purple cover": "colour_cover_purple",
    "purple bag": "colour_cover_purple",
    "purple courier": "colour_cover_purple",
    "purple mailer": "colour_cover_purple",
    "colour cover": "colour_cover",
    "color cover": "colour_cover",
    "coloured cover": "colour_cover",
    "colored cover": "colour_cover",
    "colour bag": "colour_cover",
    "color bag": "colour_cover",
    "coloured bag": "colour_cover",
    "colored bag": "colour_cover",
    "colour mailer": "colour_cover",
    "color mailer": "colour_cover",

    # ── Custom printed white ──
    "custom printed white": "custom_printed_white",
    "custom white": "custom_printed_white",
    "printed white cover": "custom_printed_white",
    "printed cover": "custom_printed_white",
    "custom print": "custom_printed_white",
    "custom printing": "custom_printed_white",
    "logo cover": "custom_printed_white",
    "logo bag": "custom_printed_white",
    "logo printed": "custom_printed_white",
    "brand cover": "custom_printed_white",
    "brand bag": "custom_printed_white",
    "branded cover": "custom_printed_white",
    "branded bag": "custom_printed_white",
    "design cover": "custom_printed_white",
    "design bag": "custom_printed_white",

    # ── Custom printed colour ──
    "custom printed colour": "custom_printed_colour",
    "custom printed color": "custom_printed_colour",
    "custom colour": "custom_printed_colour",
    "custom color": "custom_printed_colour",
    "printed colour": "custom_printed_colour",
    "printed color": "custom_printed_colour",
    "custom black": "custom_printed_colour",
    "custom pink": "custom_printed_colour",
    "custom purple": "custom_printed_colour",

    # ── Transparent covers ──
    "transparent": "transparent_cover",
    "transparent cover": "transparent_cover",
    "transparent bag": "transparent_cover",
    "clear cover": "transparent_cover",
    "clear bag": "transparent_cover",
    "polythene": "transparent_cover",
    "poly cover": "transparent_cover",

    # ── Meesho ──
    "meesho": "meesho_cover",
    "meesho cover": "meesho_cover",
    "meesho bag": "meesho_cover",

    # ── Amazon ──
    "amazon": "amazon_cover",
    "amazon cover": "amazon_cover",
    "amazon bag": "amazon_cover",
    "amazon mailer": "amazon_cover",

    # ── Flipkart ──
    "flipkart": "flipkart_cover",
    "flipkart cover": "flipkart_cover",
    "flipkart bag": "flipkart_cover",

    # ── Paper / Kraft bags ──
    "paper bag": "paper_bag_kraft",
    "kraft": "paper_bag_kraft",
    "kraft bag": "paper_bag_kraft",
    "kraft paper": "paper_bag_kraft",
    "paper cover": "paper_bag_kraft",
    "brown bag": "paper_bag_kraft",
    "brown paper": "paper_bag_kraft",
    "eco bag": "paper_bag_kraft",
    "eco friendly bag": "paper_bag_kraft",
    "grocery bag": "paper_bag_kraft",
    "shopping bag": "paper_bag_kraft",

    # ── Honeycomb roll ──
    "honeycomb roll": "honeycomb_roll",
    "honeycomb paper": "honeycomb_roll",
    "honeycomb paper roll": "honeycomb_roll",
    "honeycomb wrap": "honeycomb_roll",
    "honeycomb wrapping": "honeycomb_roll",
    "bubble wrap alternative": "honeycomb_roll",

    # ── Honeycomb sleeve ──
    "honeycomb sleeve": "honeycomb_sleeve",
    "honeycomb sleeves": "honeycomb_sleeve",
    "bottle sleeve": "honeycomb_sleeve",
    "glass sleeve": "honeycomb_sleeve",

    # ── Thermal label roll ──
    "thermal label roll": "thermal_label_roll",
    "thermal roll": "thermal_label_roll",
    "label roll": "thermal_label_roll",
    "thermal label": "thermal_label_roll",
    "shipping label": "thermal_label_roll",
    "label": "thermal_label_roll",
    "labels": "thermal_label_roll",
    "order label": "thermal_label_roll",
    "order slip": "thermal_label_roll",
    "packing slip": "thermal_label_roll",
    "dispatch label": "thermal_label_roll",
    "barcode label": "thermal_label_roll",
    "barcode sticker": "thermal_label_roll",
    "sticker label": "thermal_label_roll",
    "address label": "thermal_label_roll",
    "waybill": "thermal_label_roll",
    "way bill": "thermal_label_roll",
    "printing label": "thermal_label_roll",
    "print label": "thermal_label_roll",
    "courier label": "thermal_label_roll",
    "100x150": "thermal_label_roll",
    "4x6 label": "thermal_label_roll",

    # ── Thermal label A4 ──
    "thermal label a4": "thermal_label_a4",
    "a4 label": "thermal_label_a4",
    "4 cut": "thermal_label_a4",
    "a4 sheet": "thermal_label_a4",
    "label sheet": "thermal_label_a4",
    "a4 sticker": "thermal_label_a4",
}


def get_images_for_product(product_key: str) -> list:
    """Return list of image filenames for a given product key."""
    return PRODUCT_IMAGES.get(product_key, [])


def get_product_key_from_message(message: str) -> str | None:
    """Match a customer message to a product image key.
    Tries longer keywords first to avoid partial matches."""
    message_lower = message.lower()
    # Sort by keyword length descending — longer/more specific matches first
    sorted_keywords = sorted(KEYWORD_MAP.keys(), key=len, reverse=True)
    for keyword in sorted_keywords:
        if keyword in message_lower:
            return KEYWORD_MAP[keyword]
    return None


def get_images_from_message(message: str) -> list:
    """Convenience: get image filenames directly from a customer message."""
    product_key = get_product_key_from_message(message)
    if product_key:
        return get_images_for_product(product_key)
    return []

# ═══════════════════════════════════════════════════════════
# PRICE CHART IMAGES — sent when customer asks for price/rate
# ═══════════════════════════════════════════════════════════

PRICE_CHART_IMAGES = {
    "white_cover_100": ["white_cover_price_100.png"],
    "white_cover_1000": ["white_cover_price_1000.png"],
    "colour_cover_100": ["colour_cover_price_100.png"],
    "colour_cover_1000": ["colour_cover_price_1000.png"],
    "kraft_bag": ["kraft_bag_price.png"],
    "packing_cover_100": ["packing_cover_price_100.png"],
    "packing_cover_500": ["packing_cover_price_500.png"],
    "honeycomb_roll": ["honeycomb_roll_price.png"],
    "honeycomb_sleeve": ["honeycomb_sleeve_price.png"],
    "thermal_label_roll": ["thermal_label_roll_price.png"],
    "thermal_label_a4": ["thermal_label_a4_price.png"],
    "custom_white_100": ["custom_white_price_100.png"],
    "custom_white_1000": ["custom_white_price_1000.png"],
    "custom_colour_100": ["custom_colour_price_100.png"],
    "custom_colour_1000": ["custom_colour_price_1000.png"],
    "meesho": ["meesho_price.png"],
    "flipkart": ["flipkart_price.png"],
    "amazon": ["amazon_price.png"],
}

# Words that indicate the customer wants pricing/rate info (not product photos)
PRICE_REQUEST_WORDS = ["price", "rate", "cost", "how much", "price list", "rate list", "pricing", "charges"]


def get_price_chart_key(message: str) -> str | None:
    """Match a customer message to a price chart key based on product + MOQ context."""
    message_lower = message.lower()

    is_custom = any(w in message_lower for w in ["custom", "print", "logo", "design"])
    is_colour = any(w in message_lower for w in ["colour", "color", "black", "pink", "purple"])
    is_1000 = "1000" in message_lower or "bulk" in message_lower
    is_500 = "500" in message_lower

    if "meesho" in message_lower:
        return "meesho"
    if "flipkart" in message_lower:
        return "flipkart"
    if "amazon" in message_lower:
        return "amazon"
    if "kraft" in message_lower or "paper bag" in message_lower:
        return "kraft_bag"
    if "honeycomb roll" in message_lower or "honeycomb paper roll" in message_lower:
        return "honeycomb_roll"
    if "honeycomb sleeve" in message_lower:
        return "honeycomb_sleeve"
    if "thermal label roll" in message_lower or "label roll" in message_lower:
        return "thermal_label_roll"
    if "a4" in message_lower and "label" in message_lower:
        return "thermal_label_a4"
    if "packing cover" in message_lower or "transparent" in message_lower:
        return "packing_cover_500" if is_500 else "packing_cover_100"

    if is_custom and is_colour:
        return "custom_colour_1000" if is_1000 else "custom_colour_100"
    if is_custom:
        return "custom_white_1000" if is_1000 else "custom_white_100"
    if is_colour:
        return "colour_cover_1000" if is_1000 else "colour_cover_100"
    if "cover" in message_lower or "courier" in message_lower or "bag" in message_lower:
        return "white_cover_1000" if is_1000 else "white_cover_100"

    # Default — no product context found, send white cover 100 pcs as default
    return "white_cover_100"


def get_price_chart_images(message: str) -> list:
    """Get price chart image filenames for a customer's pricing query."""
    key = get_price_chart_key(message)
    if key:
        return PRICE_CHART_IMAGES.get(key, [])
    return []


def is_price_request(message: str) -> bool:
    """Check if a message is asking for price/rate information."""
    message_lower = message.lower()
    return any(word in message_lower for word in PRICE_REQUEST_WORDS)
