# image_service.py
# KITPAK — Product image catalogue
# Maps product categories to reference image filenames in 

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

# Keyword mapping — used to match customer messages to product image sets
KEYWORD_MAP = {
    "white cover": "white_cover",
    "white courier": "white_cover",
    "plain cover": "white_cover",
    "black cover": "colour_cover_black",
    "pink cover": "colour_cover_pink",
    "purple cover": "colour_cover_purple",
    "colour cover": "colour_cover",
    "color cover": "colour_cover",
    "custom printed white": "custom_printed_white",
    "custom white": "custom_printed_white",
    "custom printed colour": "custom_printed_colour",
    "custom printed color": "custom_printed_colour",
    "custom colour": "custom_printed_colour",
    "custom color": "custom_printed_colour",
    "printed cover": "custom_printed_white",
    "transparent": "transparent_cover",
    "meesho": "meesho_cover",
    "amazon": "amazon_cover",
    "flipkart": "flipkart_cover",
    "paper bag": "paper_bag_kraft",
    "kraft": "paper_bag_kraft",
    "honeycomb roll": "honeycomb_roll",
    "honeycomb paper roll": "honeycomb_roll",
    "honeycomb sleeve": "honeycomb_sleeve",
    "thermal label roll": "thermal_label_roll",
    "thermal roll": "thermal_label_roll",
    "label roll": "thermal_label_roll",
    "thermal label a4": "thermal_label_a4",
    "a4 label": "thermal_label_a4",
    "4 cut": "thermal_label_a4",
}


def get_images_for_product(product_key: str) -> list:
    """Return list of image filenames for a given product key."""
    return PRODUCT_IMAGES.get(product_key, [])


def get_product_key_from_message(message: str) -> str | None:
    """Match a customer message to a product image key."""
    message_lower = message.lower()
    for keyword, product_key in KEYWORD_MAP.items():
        if keyword in message_lower:
            return product_key
    return None


def get_images_from_message(message: str) -> list:
    """Convenience: get image filenames directly from a customer message."""
    product_key = get_product_key_from_message(message)
    if product_key:
        return get_images_for_product(product_key)
    return []
