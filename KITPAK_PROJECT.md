# 📦 KITPAK — WhatsApp Automation Project
> Last Updated: June 2026
> Project Owner: KITPAK (Founder — Owner's Wife)
> ⚠️ This project is exclusively for KITPAK. Never mix with PICKNPACK or any other business.

---

## 🏢 Business Overview

| Field | Details |
|---|---|
| **Business Name** | KITPAK |
| **Products** | Plain & Custom Printed Mailer Bags |
| **Colours** | White, Pink, Purple, Black |
| **Delivery** | Pan India |
| **Order Channels** | WhatsApp + Shopify Website |
| **Platform** | Shopify |
| **Language** | Tamil, English, Tanglish |

---

## 📦 Products

### Plain Mailer Bags
- Available in: White, Pink, Purple, Black
- Sizes & prices: ⏳ To be filled tomorrow

### Custom Printed Mailer Bags (Logo Printing)
- Available in all 4 colours
- **Single colour print** → MOQ 100 pcs
- **Multi colour print** → MOQ 500 pcs
- Pricing: Based on size, quantity & print complexity

---

## ✅ Features to Build

### 🤖 WhatsApp Bot (Core)
- [x] Claude AI integration with KITPAK system prompt
- [x] Tamil / English / Tanglish auto-detection
- [x] Tanglish examples baked into prompt
- [x] Plain & custom bag order flow
- [x] Colour & size selection
- [x] Order collection (name, address, pincode, qty, GST)
- [ ] Stock availability check before confirming order
- [ ] Human handoff trigger (angry customer / complex query)
- [ ] Repeat customer recognition & personalised greeting
- [ ] COD / bank transfer payment option handling
- [ ] Business hours expectation setting

### 🎙️ Voice Notes
- [ ] Groq Whisper API integration (free tier)
- [ ] Tamil + English + Tanglish transcription
- [ ] Transcribed text passed to Claude as normal message

### 🖼️ Mockup Generator
- [ ] Python + Pillow image processing
- [ ] Blank bag templates (White, Pink, Purple, Black)
- [ ] Customer logo placement at specified position
- [ ] Single colour treatment for < 500 pcs
- [ ] Multi colour for 500+ pcs
- [ ] Diagonal watermark on every mockup:
      "This mockup is for representation purposes only.
       Final print may vary. Not to be replicated or reproduced."
- [ ] WhatsApp caption disclaimer added automatically
- [ ] Customer approval flow → triggers PI generation
- [ ] Change request flow → collect feedback → redo mockup

### 💳 Proforma Invoice + UPI QR
- [ ] Auto PI generation (PDF) on order confirmation
- [ ] KITPAK branding on invoice header
- [ ] GST calculation (18%)
- [ ] Free shipping above threshold
- [ ] UPI QR code generation (exact order amount)
- [ ] PI + QR sent to customer via WATI
- [ ] Proper GST Tax Invoice (post payment, for GST customers)
- [ ] UTR collection after payment
- [ ] Payment confirmation notification to owner

### 📊 Google Sheets Order Tracker
- [ ] Live row added for every confirmed order
- [ ] Columns: Order ID, Date, Customer, Phone, Product,
              Colour, Size, Qty, Amount, Payment Status,
              UTR, Special Instructions, Preferred Courier,
              AWB, Courier, Tracking Status, Dispatch Date
- [ ] Colour coding: 🟡 Pending · 🟢 Paid · 🔵 Dispatched
- [ ] Separate tabs: KITPAK Orders / KITPAK Custom Orders
- [ ] Daily automatic backup

### 🚚 Shipping & Tracking
- [ ] AWB entry in sheet → auto WhatsApp to customer
- [ ] Courier-specific tracking link generation:
      Delhivery, DTDC, BlueDart, Xpressbees, Ekart, India Post
- [ ] Pincode serviceability check against uploaded list
- [ ] Courier preference flag to owner (if customer mentions it)
- [ ] Special instructions column in sheet
- [ ] Owner WhatsApp alert for pincode/courier mismatch
- [ ] Delivery status messages:
      Dispatched → Out for Delivery → Delivered

### 🔔 Owner Notifications
- [ ] Instant alert for every new order
- [ ] Instant alert for every payment received
- [ ] Courier preference / special instruction alerts
- [ ] Pincode mismatch alerts
- [ ] EOD summary at 9PM:
      Orders today / Revenue / Pending payments / Ready to dispatch

### 📅 Follow-up Automation
- [ ] Day 1 follow-up for enquiries without order
- [ ] Day 3 follow-up with gentle urgency
- [ ] Stop follow-up if customer places order
- [ ] WATI pre-approved template messages for follow-ups
- [ ] Reorder reminder (X days after last order)

### 🔄 Outbound / Re-engagement
- [ ] WATI template: Welcome old clients to new number
- [ ] WATI template: Follow-up on open enquiry
- [ ] WATI template: Restock alert
- [ ] WATI template: Festive offers
- [ ] WATI template: Payment reminder
- [ ] WATI template: Order dispatched update
- [ ] Import old client numbers into WATI

### 🛍️ Shopify Chat Widget
- [ ] Floating AI chat widget (bottom right)
- [ ] Claude integration with KITPAK prompt
- [ ] Live product fetch from Shopify Storefront API
- [ ] Add to cart via Shopify API
- [ ] Push to checkout with pre-filled cart
- [ ] Abandoned cart detection
- [ ] Abandoned cart → WhatsApp follow-up via WATI

---

## ❓ Data Still Needed (Collect Tomorrow)

### Section 1 — Business Basics
- [ ] KITPAK UPI ID
- [ ] Business address for invoice
- [ ] GSTIN number (if registered)
- [ ] Owner WhatsApp number for alerts
- [ ] Existing WhatsApp API provider name & credentials
- [ ] Google account for Sheets

### Section 2 — Products & Pricing
- [ ] Bag sizes (cm) for Small, Medium, Large, XL
- [ ] Price per piece for each size
- [ ] Bulk pricing tiers & discount %
- [ ] Shipping charges policy & free shipping threshold
- [ ] Sample order available? Price?
- [ ] COD available?
- [ ] Bank transfer accepted? Account details?
- [ ] Payment due timeline after PI sent

### Section 3 — Stock Management
- [ ] How stock is tracked (Google Sheets preferred)
- [ ] Current stock levels per colour & size
- [ ] Low stock alert threshold

### Section 4 — Custom Orders
- [ ] Production timeline (days)
- [ ] Design proof turnaround time
- [ ] Extra charge for logo printing per pc?
- [ ] Accepted logo formats (PNG, PDF, AI?)
- [ ] Logo position on bag (centre / top / bottom?)
- [ ] Mockup — one colour or per colour variant?

### Section 5 — Mockup Templates
- [ ] Blank bag image — White
- [ ] Blank bag image — Pink
- [ ] Blank bag image — Purple
- [ ] Blank bag image — Black
- [ ] Single colour mockup sample
- [ ] Multi colour mockup sample
- [ ] Exact disclaimer text for watermark

### Section 6 — Returns & Complaints
- [ ] Return policy (days & conditions)
- [ ] Who handles complaints?
- [ ] Refund method (UPI / store credit?)

### Section 7 — Courier & Shipping
- [ ] Couriers used regularly
- [ ] Pincode serviceability Excel file
- [ ] Average delivery days by zone
- [ ] Who handles shipping?

### Section 8 — Human Handoff
- [ ] Trigger words/situations for handoff
- [ ] Owner WhatsApp for handoff
- [ ] Business hours for human support

### Section 9 — Repeat Customers
- [ ] Reorder reminder — how many days after last order?
- [ ] Special discount for repeat customers?

---

## 🗂️ File Structure (Final)

```
kitpak-whatsapp-automation/
├── main.py                  # Flask webhook server
├── claude_service.py        # Claude AI + KITPAK system prompt
├── wati_service.py          # WATI API — send messages & media
├── invoice_service.py       # PI + GST invoice PDF generator
├── qr_service.py            # UPI QR code generator
├── mockup_service.py        # Logo placement + watermark
├── sheets_service.py        # Google Sheets order tracker
├── tracking_service.py      # AWB + courier tracking
├── followup_service.py      # Day 1 & Day 3 automation
├── scheduler.py             # EOD summary + reorder reminders
├── stock_service.py         # Stock availability check
├── pincode_service.py       # Courier pincode serviceability
├── shopify_widget/
│   ├── widget.js            # Floating chat widget
│   └── shopify_api.js       # Cart + checkout integration
├── templates/
│   ├── bags/                # Blank bag mockup images
│   └── invoice_template.html
├── data/
│   ├── pincodes.xlsx        # Courier serviceability list
│   └── stock.json           # Current stock levels
├── requirements.txt
├── render.yaml
├── .env.example
└── README.md
```

---

## 🚀 Deployment

- **Backend:** Render.com (free tier → upgrade when volume grows)
- **Database:** Google Sheets (orders) + SQLite (conversation history)
- **Voice:** Groq Whisper API (free)
- **AI:** Anthropic Claude Sonnet (claude-sonnet-4-20250514)
- **WhatsApp:** WATI (existing API number)
- **Website:** Shopify (existing store)

---

## 📅 Build Phases

| Phase | Features | Status |
|---|---|---|
| **Phase 1** | Core bot, Tamil/English, order flow, PI, QR | 🔨 Building tomorrow |
| **Phase 2** | Voice notes, mockup generator, Google Sheets | 🔨 Building tomorrow |
| **Phase 3** | Tracking, follow-ups, stock check, handoff | 🔨 Building tomorrow |
| **Phase 4** | Shopify widget, abandoned cart, outbound | 📅 After Phase 1-3 live |
| **Phase 5** | Reorder reminders, reviews, referrals | 📅 Phase 2 rollout |

---

## ⚠️ Important Notes

- This project is **KITPAK only** — never mix with PICKNPACK
- All API keys stored in `.env` — never in code or chat
- Mockup watermark mandatory on every image sent
- Single colour print only for < 500 pcs custom orders
- Multi colour available for 500+ pcs only
- Bot replies in customer's language — Tamil / English / Tanglish
- Human handoff must be seamless — customer should not feel abandoned
