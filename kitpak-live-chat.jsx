import { useState, useRef, useEffect } from "react";

const KITPAK_SYSTEM_PROMPT = `You are a friendly WhatsApp sales assistant for KITPAK — a packaging supplies business.

⚠️ CRITICAL: You represent KITPAK ONLY. Never mention any other business.

ABOUT KITPAK:
- Business: KITPAK | Legal: SARAVANA TRADING
- Address: 55C, Valayangadu Main Road, Kumar Nagar South, Tirupur - 641605
- GSTIN: 33ATTPG0334P2ZD
- Delivery: Pan India — FREE SHIPPING on all products
- Payment: UPI ONLY (GPay, PhonePe, Paytm, BHIM) — No COD, No bank transfer
- All prices include GST

COURIER RULES (never tell customer, just use internally):
- Tamil Nadu → ST Courier
- Karnataka, Kerala, Andhra Pradesh, Telangana → DTDC  
- All other states → India Post

FULL PRODUCT CATALOGUE (All prices incl. GST, Free Shipping):

1. COURIER COVERS — WHITE (50 microns, pack of 100):
   6x8"=₹230 | 8x10"=₹290 | 10x12"=₹320 | 10x14"=₹360 | 12x14"=₹460 | 12x16"=₹560 | 14x18"=₹860 | 16x20"=₹1060 | 20x23"=₹1260
   Pack of 1000: 6x8"=₹2150 | 8x10"=₹2750 | 10x12"=₹3050 | 10x14"=₹3450 | 12x14"=₹4250 | 12x16"=₹5350 | 14x18"=₹8350 | 16x20"=₹10350 | 20x23"=₹12350

2. COURIER COVERS — COLOUR — Pink/Purple/Black (50 microns, pack of 100):
   6x8"=₹340 | 8x10"=₹380 | 10x12"=₹530 | 12x14"=₹610 | 12x16"=₹680
   Pack of 1000: 6x8"=₹3200 | 8x10"=₹3600 | 10x12"=₹5200 | 12x14"=₹5900 | 12x16"=₹6600

3. COURIER COVERS — KRAFT/BROWN (50 microns, pack of 100):
   9x11"=₹440 | 11x14"=₹580 | 15x18"=₹880

4. MEESHO TRANSPARENT COVERS (50 microns, Non-POD, pack of 100):
   8x10"=₹300 | 9x10"=₹340 | 10x12"=₹370 | 10x14"=₹450 | 12x14"=₹540 | 12x16"=₹580

5. FLIPKART COURIER COVERS — TRANSPARENT (50 microns, pack of 100):
   SB1(6x8")=₹290 | SB2.5(8x11")=₹360 | SB2(10x13")=₹430 | SB3(12x15.5")=₹630 | SB3.5(14x18")=₹690

6. AMAZON COURIER COVERS (50 microns, pack of 100):
   8x11"=₹320 | 10x12"=₹360 | 12x16"=₹520

7. PACKING COVERS — TRANSPARENT (50 microns):
   Pack of 100: 5.5x7.5"=₹140 | 7.5x9.5"=₹190 | 9.5x11.5"=₹240 | 11.5x13.5"=₹320
   Pack of 500: 5.5x7.5"=₹490 | 7.5x9.5"=₹870 | 9.5x11.5"=₹1250 | 11.5x13.5"=₹1600

8. CUSTOM PRINTED COVERS — WHITE (POD):
   100 pcs: 6x8"=₹1000 | 8x10"=₹1090 | 10x12"=₹1120 | 10x14"=₹1160 | 12x14"=₹1260 | 12x16"=₹1360 | 14x18"=₹1660 | 16x20"=₹1860 | 20x23"=₹2060
   1000 pcs: 6x8"=₹5999 | 8x10"=₹6999 | 10x12"=₹7999 | 10x14"=₹8899 | 12x14"=₹9999 | 12x16"=₹10999 | 14x18"=₹11999 | 16x20"=₹13499 | 20x23"=₹17999

9. CUSTOM PRINTED COVERS — COLOUR/POD (Pink/Purple/Black):
   100 pcs: 6x8"=₹1140 | 8x10"=₹1190 | 10x12"=₹1330 | 12x14"=₹1410 | 12x16"=₹1510
   1000 pcs: 6x8"=₹6999 | 8x10"=₹7199 | 10x12"=₹8999 | 12x14"=₹11499 | 12x16"=₹11999

10. SHIPPING LABEL — 4cut A4 (100 sheets): ₹399
11. THERMAL LABEL — 100x150mm (400 labels/roll): ₹419
12. HONEYCOMB PAPER ROLL (Brown Kraft, GSM80, 15" wide):
    10mtrs=₹250 | 10mtrs x3=₹599 | 100mtrs x2=₹1999 | Bulk orders get special discount
13. HONEYCOMB PAPER SLEEVE (Brown Kraft, pack of 100):
    10cm=₹400 | 15cm=₹600 | 20cm=₹800 | 22.5cm=₹1000 | 30cm=₹1200 | 40cm=₹1600 | 45cm=₹1800 | 90cm=₹3600

ORDERING GOAL — CLOSE IN CHAT:
1. Greet warmly, understand what they need
2. Ask: product type → colour/variant → size → quantity
3. Share pricing clearly
4. Collect: Full Name, Address & Pincode, GST (optional)
5. For custom/POD → ask to share logo (PNG/PDF)
6. Confirm order → say team will share UPI payment details

LANGUAGE RULES:
- Pure Tamil → reply in Tamil
- Pure English → reply in English
- Tanglish → warm friendly Tanglish
- Use Tamil script, not transliteration
- Keep replies short & mobile-friendly (max 5 lines)

PAYMENT: UPI ONLY. If asked for COD or bank transfer → "We accept UPI only — GPay, PhonePe, Paytm or BHIM 😊"`;

const SUGGESTIONS = [
  { label: "English", text: "Hi, what courier covers do you have?" },
  { label: "Tamil", text: "வணக்கம், விலை என்ன?" },
  { label: "Tanglish", text: "Bro pink colour cover price என்ன? 100 pcs வேணும்" },
  { label: "Flipkart", text: "Flipkart covers SB2 price what?" },
  { label: "Custom", text: "Custom logo cover போட முடியுமா?" },
  { label: "Honeycomb", text: "Honeycomb paper roll price என்ன?" },
  { label: "Amazon", text: "Amazon courier covers available ah?" },
  { label: "Bulk", text: "1000 pcs white cover 10x12 price?" },
];

const nowTime = () => new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true });

function formatText(text) {
  return text.split("\n").map((line, i, arr) => (
    <span key={i}>
      {line.split(/(\*[^*]+\*)/).map((p, j) =>
        p.startsWith("*") && p.endsWith("*") ? <strong key={j}>{p.slice(1,-1)}</strong> : p
      )}
      {i < arr.length - 1 && <br />}
    </span>
  ));
}

export default function KitpakLiveChatV2() {
  const [messages, setMessages] = useState([{
    role: "bot",
    text: "👋 வணக்கம்! Welcome to *KITPAK* 📦\n\nWe supply courier covers, custom printed covers, shipping labels, packing covers & honeycomb paper — Pan India with FREE shipping!\n\nHow can I help you today? 😊",
    time: nowTime()
  }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return;
    setShowSuggestions(false);
    const userMsg = { role: "user", text: text.trim(), time: nowTime() };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    const newHistory = [...history, { role: "user", content: text.trim() }];
    try {
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 400,
          system: KITPAK_SYSTEM_PROMPT,
          messages: newHistory
        })
      });
      const data = await res.json();
      const reply = data.content?.[0]?.text || "Sorry, something went wrong!";
      setMessages(prev => [...prev, { role: "bot", text: reply, time: nowTime() }]);
      setHistory([...newHistory, { role: "assistant", content: reply }]);
    } catch {
      setMessages(prev => [...prev, { role: "bot", text: "Connection error. Try again!", time: nowTime() }]);
    }
    setLoading(false);
  };

  const reset = () => {
    setMessages([{
      role: "bot",
      text: "👋 வணக்கம்! Welcome to *KITPAK* 📦\n\nWe supply courier covers, custom printed covers, shipping labels, packing covers & honeycomb paper — Pan India with FREE shipping!\n\nHow can I help you today? 😊",
      time: nowTime()
    }]);
    setHistory([]);
    setInput("");
    setShowSuggestions(true);
    setLoading(false);
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0f3460 100%)",
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      padding: "20px", fontFamily: "'Segoe UI', system-ui, sans-serif"
    }}>
      <style>{`
        @keyframes fadeUp { from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);} }
        @keyframes bounce { 0%,60%,100%{transform:translateY(0);}30%{transform:translateY(-5px);} }
        @keyframes pulse { 0%,100%{opacity:1;}50%{opacity:0.4;} }
        textarea{resize:none;} textarea:focus{outline:none;}
        ::-webkit-scrollbar{width:3px;}
        ::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.15);border-radius:2px;}
        .sug-btn:hover{background:rgba(37,211,102,0.2)!important;transform:translateY(-1px);}
      `}</style>

      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 14 }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "rgba(37,211,102,0.1)", border: "1px solid rgba(37,211,102,0.2)", borderRadius: 20, padding: "5px 16px", marginBottom: 6 }}>
          <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#25D366", animation: "pulse 2s infinite" }} />
          <span style={{ color: "#25D366", fontSize: 11, fontWeight: 700, letterSpacing: 1 }}>KITPAK — Live Bot Demo · Real Claude AI</span>
        </div>
        <div style={{ color: "rgba(255,255,255,0.3)", fontSize: 11 }}>Full product catalogue loaded · Tamil / English / Tanglish</div>
      </div>

      {/* Phone */}
      <div style={{
        width: "100%", maxWidth: 400,
        background: "#111", borderRadius: 28,
        overflow: "hidden",
        boxShadow: "0 40px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.08)",
        display: "flex", flexDirection: "column", height: 620
      }}>
        {/* WA Header */}
        <div style={{ background: "#075E54", padding: "10px 14px", display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 38, height: 38, borderRadius: "50%", background: "linear-gradient(135deg,#25D366,#128C7E)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, fontWeight: 900, color: "#fff" }}>K</div>
          <div style={{ flex: 1 }}>
            <div style={{ color: "#fff", fontWeight: 700, fontSize: 14 }}>KITPAK</div>
            <div style={{ color: "rgba(255,255,255,0.6)", fontSize: 10 }}>📦 Packaging Supplies · 13 Products · Free Shipping</div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#25D366", animation: "pulse 2s infinite" }} />
            <button onClick={reset} style={{ background: "rgba(255,255,255,0.15)", border: "none", borderRadius: 6, padding: "3px 8px", color: "#fff", fontSize: 10, cursor: "pointer", fontWeight: 600 }}>Reset</button>
          </div>
        </div>

        {/* Messages */}
        <div style={{
          flex: 1, overflowY: "auto", padding: "10px 10px 6px",
          background: "#ECE5DD",
          backgroundImage: "radial-gradient(circle at 1px 1px,rgba(0,0,0,0.03) 1px,transparent 0)",
          backgroundSize: "18px 18px"
        }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start", marginBottom: 6, animation: "fadeUp 0.2s ease" }}>
              <div style={{
                maxWidth: "80%",
                background: msg.role === "user" ? "#DCF8C6" : "#fff",
                borderRadius: msg.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                padding: "8px 11px 5px",
                boxShadow: "0 1px 2px rgba(0,0,0,0.1)"
              }}>
                <div style={{ fontSize: 13.5, color: "#111", lineHeight: 1.5 }}>{formatText(msg.text)}</div>
                <div style={{ fontSize: 10, color: "#999", textAlign: "right", marginTop: 3, display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 3 }}>
                  {msg.time} {msg.role === "user" && <span style={{ color: "#34B7F1" }}>✓✓</span>}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: 6, animation: "fadeUp 0.2s ease" }}>
              <div style={{ background: "#fff", borderRadius: "16px 16px 16px 4px", padding: "10px 14px", display: "flex", gap: 4, boxShadow: "0 1px 2px rgba(0,0,0,0.1)" }}>
                {[0,1,2].map(i => <div key={i} style={{ width: 7, height: 7, borderRadius: "50%", background: "#25D366", animation: `bounce 1.2s infinite`, animationDelay: `${i*0.2}s` }} />)}
              </div>
            </div>
          )}

          {/* Suggestions */}
          {showSuggestions && (
            <div style={{ marginTop: 10 }}>
              <div style={{ fontSize: 10, color: "#888", textAlign: "center", marginBottom: 8 }}>💬 Try these messages</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6, justifyContent: "center" }}>
                {SUGGESTIONS.map((s, i) => (
                  <button key={i} className="sug-btn" onClick={() => sendMessage(s.text)} style={{
                    background: "rgba(37,211,102,0.08)",
                    border: "1px solid rgba(37,211,102,0.3)",
                    borderRadius: 16, padding: "5px 10px",
                    fontSize: 11, color: "#075E54",
                    cursor: "pointer", fontWeight: 600,
                    transition: "all 0.2s"
                  }}>{s.label}</button>
                ))}
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div style={{ background: "#F0F0F0", padding: "7px 10px 10px", display: "flex", alignItems: "flex-end", gap: 8, borderTop: "1px solid rgba(0,0,0,0.06)" }}>
          <div style={{ flex: 1, background: "#fff", borderRadius: 22, padding: "8px 14px", boxShadow: "0 1px 3px rgba(0,0,0,0.08)", display: "flex", alignItems: "center" }}>
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(input); } }}
              placeholder="Type in English, Tamil or Tanglish..."
              rows={1}
              style={{ flex: 1, border: "none", fontSize: 13.5, color: "#111", background: "transparent", fontFamily: "inherit", lineHeight: 1.4, maxHeight: 80, overflowY: "auto", boxSizing: "border-box", width: "100%" }}
            />
          </div>
          <button onClick={() => sendMessage(input)} disabled={!input.trim() || loading} style={{
            width: 42, height: 42, borderRadius: "50%",
            background: input.trim() && !loading ? "#25D366" : "#ccc",
            border: "none", cursor: input.trim() && !loading ? "pointer" : "default",
            display: "flex", alignItems: "center", justifyContent: "center",
            flexShrink: 0, transition: "all 0.2s",
            boxShadow: input.trim() && !loading ? "0 2px 8px rgba(37,211,102,0.4)" : "none"
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="white"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg>
          </button>
        </div>
      </div>

      <div style={{ marginTop: 12, color: "rgba(255,255,255,0.2)", fontSize: 10, textAlign: "center" }}>
        KITPAK · SARAVANA TRADING · Tirupur · Pan India Free Shipping
      </div>
    </div>
  );
}
