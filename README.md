# 📦 KITPAK — WhatsApp Automation Bot

An AI-powered WhatsApp assistant for **KITPAK** that handles customer queries,
shares product pricing, collects order details, and tries to close sales —
all automatically, 24/7, even when your system is off.

> ⚠️ **Note:** This bot is built exclusively for **KITPAK**.
> Do not confuse or mix this with any other business.

---

## 🏗️ How It Works

```
Customer messages KITPAK on WhatsApp
        ↓
WATI receives it (always on ☁️)
        ↓
WATI calls this webhook server (hosted on Render ☁️)
        ↓
Claude AI reads the message + conversation history
        ↓
Claude replies in Tamil / English / Tanglish
        ↓
Reply sent back to customer via WATI
```

Everything runs in the cloud — **your phone or laptop never needs to be on.**

---

## 📁 Project Files

| File | Purpose |
|------|---------|
| `main.py` | Flask webhook server — receives messages from WATI |
| `claude_service.py` | Claude AI integration + KITPAK system prompt |
| `wati_service.py` | Sends replies back via WATI API |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for your secret keys |
| `render.yaml` | One-click deploy config for Render.com |

---

## 🚀 Setup Guide (Step by Step)

### Step 1 — Sign Up for WATI
1. Go to [wati.io](https://wati.io) and create an account
2. Connect your **KITPAK WhatsApp Business number**
3. From the WATI dashboard, go to **API → Access Token** and copy your token
4. Also note your **API URL** (e.g. `https://live-mt-server.wati.io/123456`)

---

### Step 2 — Get Your Anthropic API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an API key and copy it

---

### Step 3 — Deploy to Render (Free)
1. Push this project to a **GitHub repository**
2. Go to [render.com](https://render.com) and sign up (free, no credit card needed)
3. Click **New → Web Service** → connect your GitHub repo
4. Render will auto-detect `render.yaml` and configure everything
5. Add your environment variables in Render dashboard:
   - `ANTHROPIC_API_KEY` → your Anthropic key
   - `WATI_API_URL` → your WATI API URL
   - `WATI_API_TOKEN` → your WATI token
6. Click **Deploy** — Render gives you a live URL like:
   `https://kitpak-whatsapp-bot.onrender.com`

---

### Step 4 — Connect Webhook in WATI
1. In WATI dashboard → **Settings → Webhook**
2. Set the Webhook URL to:
   `https://kitpak-whatsapp-bot.onrender.com/webhook`
3. Save — done! ✅

---

### Step 5 — Update Your Product Catalogue
Open `claude_service.py` and update the **PRODUCT CATALOGUE & PRICING** section
with your actual KITPAK product sizes and prices.

---

## ✅ Test It

1. Send a WhatsApp message to your KITPAK number
2. The bot should reply within a few seconds
3. Check Render logs if something doesn't work:
   Render Dashboard → your service → **Logs**

---

## 🔧 Customisation Tips

- **Add new products** → Edit the product catalogue in `claude_service.py`
- **Change bot personality** → Edit the system prompt in `claude_service.py`
- **Add more languages** → Update the LANGUAGE RULES section in the prompt
- **Connect to a database** → Replace the in-memory `conversation_history` dict
  in `main.py` with Redis or SQLite for persistence across restarts

---

## ⚠️ Important Notes

- The free tier of Render **sleeps after 15 minutes of inactivity** — the first
  message after sleep may take ~30 seconds. Upgrade to a paid plan (₹500/mo)
  to avoid this.
- Never commit your `.env` file to GitHub — keep your API keys secret.
- This bot is for **KITPAK only** — not for any other business.

---

## 📞 Support

For help setting this up, contact the person who built this project.
