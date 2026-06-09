# ═══════════════════════════════════════════════
# KITPAK — FINAL BUSINESS CONFIGURATION
# Last Updated: June 2026
# ⚠️ This config is for KITPAK only.
#    Never mix with PICKNPACK or Melo Industry.
# ═══════════════════════════════════════════════

BUSINESS_CONFIG = {

    # ─── Brand ───
    "brand_name"        : "KITPAK",
    "legal_name"        : "SARAVANA TRADING",

    # ─── Address ───
    "address_line1"     : "55C, Valayangadu Main Road",
    "address_line2"     : "Kumar Nagar South",
    "city"              : "Tirupur",
    "pincode"           : "641605",
    "state"             : "Tamil Nadu",
    "full_address"      : "55C, Valayangadu Main Road, Kumar Nagar South, Tirupur - 641605, Tamil Nadu",

    # ─── Tax ───
    "gstin"             : "33ATTPG0334P2ZD",
    "gst_rate"          : 0.18,

    # ─── Contact ───
    "whatsapp_current"  : "83004 75706",   # Current number (will change)
    "whatsapp_api"      : "",              # ⏳ New API number — update before go-live

    # ─── Payment (UPI ONLY) ───
    "upi_id"            : "9489501487@okbizaxis",
    "upi_name"          : "SARAVANA TRADING",
    "bank_transfer"     : False,           # NOT OFFERED
    "cod"               : False,           # NOT OFFERED
    "payment_note"      : "UPI only — GPay, PhonePe, Paytm, BHIM",

    # ─── Shipping ───
    "free_shipping"     : True,            # FREE on all orders Pan India
    "shipping_charge"   : 0,

    # ─── Invoice ───
    "invoice_prefix"    : "KP",
    "invoice_footer"    : "Thank you for choosing KITPAK! | SARAVANA TRADING | Tirupur",

    # ─── Notifications ───
    "owner_whatsapp"      : "8300475706",   # Confirmed
    "eod_summary_time"  : "21:00",        # 9PM daily summary

    # ─── Website ───
    "shopify_url"       : "",             # ⏳ Add Shopify store URL

    # ─── Follow-up ───
    "followup_day1"     : 1,              # Day 1 follow-up if no order
    "followup_day3"     : 3,              # Day 3 follow-up if no order
}

# ═══════════════════════════════════════════════
# COURIER RULES
# ═══════════════════════════════════════════════

COURIER_RULES = {
    "ST Courier" : {
        "states"  : ["Tamil Nadu"],
        "pincode_range" : (600, 643),
    },
    "DTDC" : {
        "states"  : ["Karnataka", "Kerala", "Andhra Pradesh", "Telangana"],
        "pincode_range" : [(560, 591), (670, 695), (500, 535)],
    },
    "India Post" : {
        "states"  : "ALL OTHER STATES",
    }
}

STATE_COURIER_MAP = {
    "Tamil Nadu"        : "ST Courier",
    "TN"                : "ST Courier",
    "Karnataka"         : "DTDC",
    "KA"                : "DTDC",
    "Kerala"            : "DTDC",
    "KL"                : "DTDC",
    "Andhra Pradesh"    : "DTDC",
    "AP"                : "DTDC",
    "Telangana"         : "DTDC",
    "TS"                : "DTDC",
    "DEFAULT"           : "India Post",
}

COURIER_TRACKING_URLS = {
    "ST Courier"  : "https://www.stcourier.com/tracking?awb={awb}",
    "DTDC"        : "https://www.dtdc.in/tracking/tracking_results.asp?TrkType=awb&strCnno={awb}",
    "India Post"  : "https://www.indiapost.gov.in/_layouts/15/dop.portal.tracking/trackconsignment.aspx",
}

# ═══════════════════════════════════════════════
# PAYMENT
# ═══════════════════════════════════════════════

PAYMENT_CONFIG = {
    "accepted_methods"  : ["UPI"],
    "upi_apps"         : ["GPay", "PhonePe", "Paytm", "BHIM"],
    "bank_transfer"     : False,
    "cod"               : False,
}

# ═══════════════════════════════════════════════
# CUSTOM / POD PRINTING RULES
# ═══════════════════════════════════════════════

CUSTOM_PRINT_RULES = {
    "single_colour_min_qty"  : 100,
    "single_colour_max_qty"  : 14999,
    "multi_colour_min_qty"   : 15000,
    "mockup_disclaimer"     : "This mockup is for representation purposes only. Final print may vary slightly. Not to be replicated or reproduced.",
    "accepted_logo_formats" : ["PNG", "PDF", "AI", "SVG"],
    "proof_turnaround"      : "24 hours",
}

# ═══════════════════════════════════════════════
# CUSTOMISATION ELIGIBILITY
# ═══════════════════════════════════════════════

CUSTOMISABLE_PRODUCTS = [
    "Courier Covers — White",
    "Courier Covers — Colour (Pink/Purple/Black)",
]

NON_CUSTOMISABLE_PRODUCTS = [
    "Meesho Transparent Covers",      # Cannot be customised
    "Flipkart Courier Covers",        # Cannot be customised
    "Amazon Courier Covers",          # Cannot be customised
    "Courier Covers — Kraft/Brown",   # Cannot be customised
    "Packing Covers — Transparent",   # Cannot be customised
    "Shipping Label",                 # Cannot be customised
    "Thermal Label",                  # Cannot be customised
    "Honeycomb Paper Roll",           # Cannot be customised
    "Honeycomb Paper Sleeve",         # Cannot be customised
]

CUSTOMISATION_NOTE = """
Custom logo printing is available ONLY on:
  ✅ White Courier Covers
  ✅ Colour Courier Covers (Pink / Purple / Black)

NOT available on:
  ❌ Meesho Transparent Covers
  ❌ Flipkart Courier Covers
  ❌ Amazon Courier Covers
  ❌ Any other products
"""

# ═══════════════════════════════════════════════
# BULK PRICING — 5000+ COVERS (MOQ 5000)
# All prices per piece in ₹ — GST & transport extra
# ═══════════════════════════════════════════════

BULK_PRICING_5000 = {

    "plain_white": {
        "moq": 5000,
        "note": "Price per piece. GST & transport extra.",
        "sizes": {
            "6x8":   1.50, "8x10":  1.90, "9x12":  1.90,
            "10x12": 2.20, "10x14": 2.40, "12x14": 2.90,
            "12x16": 3.40, "14x18": 6.00, "16x20": 7.25,
            "20x24": 8.00
        }
    },

    "colour_cover": {
        "moq": 5000,
        "note": "Price per piece. GST & transport extra.",
        "sizes": {
            "6x8":   2.20, "8x10":  2.40, "10x12": 3.20,
            "12x14": 4.10, "12x16": 4.60
        }
    },

    "amazon": {
        "moq": 5000,
        "note": "Price per piece. GST & transport extra.",
        "sizes": {
            "8x11":  1.90, "10x12": 2.20, "12x16": 3.20
        }
    },

    "flipkart_transparent": {
        "moq": 5000,
        "note": "Price per piece. GST & transport extra.",
        "sizes": {
            "SB1 (6x8)":      1.90, "SB2.5 (8x11)": 2.50,
            "SB2 (10x13)":    3.20, "SB3 (12x15.5)": 4.50,
            "SB3.5 (14x18)":  5.10
        }
    },

    "meesho_transparent": {
        "moq": 5000,
        "note": "Price per piece. GST & transport extra.",
        "sizes": {
            "8x10 (TP-02)":  1.80, "9x10 (TP-15)":  1.95,
            "10x12 (TP-04)": 2.20, "10x14 (TP-05)": 2.50,
            "12x14 (TP-00)": 3.00, "12x16 (TP-06)": 3.30
        }
    },

    "plain_paper_bag": {
        "moq": 5000,
        "note": "Price per piece. GST & transport extra.",
        "sizes": {
            "9x11": 3.00, "11x14": 4.40, "15x18": 6.50
        }
    },

    "transparent_cover": {
        "moq": 5000,
        "note": "Price per pack. GST & transport extra.",
        "sizes": {
            "5.5x7.5":   60, "7.5x9.5":   65,
            "9.5x11.5": 100, "11.5x13.5": 160
        }
    },

    "honeycomb_roll": {
        "moq": "15 rolls+",
        "note": "Price per roll. GST & transport extra.",
        "sizes": {
            "10mtr": 110, "100mtr": 525
        }
    },

    # Custom Printed White Covers — 5000 pcs
    # Formula: (1000 pcs price × 2) − 10%
    "custom_printed_white": {
        "moq": 5000,
        "note": "Price per 1000 pcs. GST & transport extra. Above 5000 → forward to team.",
        "sizes": {
            "6x8":   10798, "8x10":  12598, "10x12": 14398,
            "10x14": 16018, "12x14": 17998, "12x16": 19798,
            "14x18": 21598, "16x20": 24298, "20x23": 32398
        }
    },
}

# ═══════════════════════════════════════════════
# BULK FORWARD TO TEAM RULES
# ═══════════════════════════════════════════════

FORWARD_TO_TEAM_BULK = {
    "custom_printed_colour": "Above 1000 pcs → Forward to team",
    "honeycomb_sleeve":      "Any bulk order → Forward to team",
    "shipping_label_a4":     "Any bulk order → Forward to team",
    "above_5000_custom":     "Above 5000 pcs custom white → Forward to team",
}
