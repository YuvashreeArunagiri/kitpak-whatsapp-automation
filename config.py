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
    "upi_id"            : "",              # ⏳ Share UPI ID to complete
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
