import { useState, useRef, useEffect } from "react";

const SYSTEM_PROMPT = `You are a KITPAK WhatsApp sales assistant. Your job is to collect order details and confirm the order.

KITPAK sells mailer bags:
Plain Bags (White/Pink/Purple/Black):
  Small (20×14cm) ₹8/pc | Medium (30×20cm) ₹12/pc | Large (40×30cm) ₹16/pc | XL (50×40cm) ₹22/pc | Min 50 pcs
Custom Logo Print: 100-499 pcs = single colour | 500+ pcs = multi colour

Collect in order: product type (plain/custom), colour, size, quantity, name, pincode+address, GST (optional).
Once you have ALL details, end your reply with this exact JSON block on a new line:
ORDER_READY:{"name":"...","phone":"","address":"...","pincode":"...","product":"...","colour":"...","size":"...","qty":0,"pricePerPc":0,"isCustom":false,"gst":""}

LANGUAGE: Match customer's language — Tamil, English or Tanglish. Keep replies short and friendly.
If they write Tamil or Tanglish, reply warmly in that style.`;

const formatINR = (n) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);
const nowTime = () => new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true });
const today = () => new Date().toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
const dueDate = () => new Date(Date.now() + 2 * 86400000).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
const invNo = () => `KP-${Date.now().toString().slice(-6)}`;

const DEMO_MESSAGES = [
  { role: "user", text: "Hi, I need 200 pink medium mailer bags", time: "10:01 AM" },
  { role: "bot", text: "Hey! Pink medium bags (30×20cm) — great choice 😊\n\n200 pcs × ₹12 = *₹2,400*\n\nPlain or custom logo print?", time: "10:01 AM" },
  { role: "user", text: "Plain is fine", time: "10:02 AM" },
  { role: "bot", text: "Perfect! To process your order I need:\n\n1. Your full name\n2. Delivery address & pincode\n3. GST number (optional)\n\nPlease share these 😊", time: "10:02 AM" },
  { role: "user", text: "Priya Sharma, 42 Anna Nagar Chennai 600040, no GST", time: "10:03 AM" },
];

const DEMO_ORDER = {
  name: "Priya Sharma",
  phone: "9876543210",
  address: "42, Anna Nagar, Chennai - 600040, Tamil Nadu",
  pincode: "600040",
  product: "Pink Plain Mailer Bags",
  colour: "Pink",
  size: "Medium (30×20 cm)",
  qty: 200,
  pricePerPc: 12,
  isCustom: false,
  gst: ""
};

function ChatBubble({ msg }) {
  const isUser = msg.role === "user";
  return (
    <div style={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", marginBottom: 6, animation: "fadeUp 0.2s ease" }}>
      <div style={{
        maxWidth: "80%",
        background: isUser ? "#DCF8C6" : "#fff",
        borderRadius: isUser ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
        padding: "8px 11px 5px",
        boxShadow: "0 1px 2px rgba(0,0,0,0.1)"
      }}>
        <div style={{ fontSize: 13, color: "#111", lineHeight: 1.5 }}>
          {msg.text.split("\n").map((line, i, arr) => (
            <span key={i}>
              {line.split(/(\*[^*]+\*)/).map((p, j) =>
                p.startsWith("*") && p.endsWith("*") ? <strong key={j}>{p.slice(1,-1)}</strong> : p
              )}
              {i < arr.length - 1 && <br />}
            </span>
          ))}
        </div>
        <div style={{ fontSize: 10, color: "#999", textAlign: "right", marginTop: 3, display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 3 }}>
          {msg.time} {isUser && <span style={{ color: "#34B7F1" }}>✓✓</span>}
        </div>
      </div>
    </div>
  );
}

function Invoice({ order, invoiceNo }) {
  const subtotal = order.qty * order.pricePerPc;
  const gst = Math.round(subtotal * 0.18);
  const shipping = subtotal >= 999 ? 0 : 99;
  const total = subtotal + gst + shipping;
  const upiLink = `upi://pay?pa=kitpak@okaxis&pn=KITPAK&am=${total}&cu=INR&tn=${invoiceNo}`;
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(upiLink)}&bgcolor=ffffff&color=075E54&margin=8`;

  return (
    <div style={{ background: "#fff", borderRadius: 16, overflow: "hidden", boxShadow: "0 8px 32px rgba(0,0,0,0.2)" }}>
      {/* Header */}
      <div style={{ background: "linear-gradient(135deg, #1a1a2e, #0f3460)", padding: "20px 22px", display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: "linear-gradient(135deg, #25D366, #075E54)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, fontWeight: 900, color: "#fff" }}>K</div>
            <span style={{ color: "#fff", fontSize: 18, fontWeight: 800, letterSpacing: 1 }}>KITPAK</span>
          </div>
          <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 10 }}>📍 Coimbatore, Tamil Nadu · Pan India</div>
          <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 10 }}>📞 +91 98765 43210</div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ background: "rgba(37,211,102,0.15)", border: "1px solid rgba(37,211,102,0.3)", borderRadius: 6, padding: "3px 10px", color: "#25D366", fontSize: 10, fontWeight: 700, marginBottom: 6 }}>PROFORMA INVOICE</div>
          <div style={{ color: "#fff", fontWeight: 700, fontSize: 12 }}>{invoiceNo}</div>
          <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 10 }}>Date: {today()}</div>
          <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 10 }}>Due: {dueDate()}</div>
        </div>
      </div>

      <div style={{ padding: "16px 22px" }}>
        {/* Bill To */}
        <div style={{ background: "#f8f9ff", borderRadius: 8, padding: "10px 14px", marginBottom: 14, borderLeft: "3px solid #1a1a2e" }}>
          <div style={{ fontSize: 9, fontWeight: 700, color: "#999", letterSpacing: 1, marginBottom: 5 }}>BILL TO</div>
          <div style={{ fontWeight: 700, fontSize: 13, color: "#111" }}>{order.name}</div>
          <div style={{ color: "#555", fontSize: 11, marginTop: 2 }}>{order.address}</div>
          {order.gst && <div style={{ color: "#555", fontSize: 11 }}>GSTIN: {order.gst}</div>}
        </div>

        {/* Table */}
        <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: 14 }}>
          <thead>
            <tr style={{ background: "#1a1a2e" }}>
              {["Item", "Size", "Qty", "Rate", "Amount"].map(h => (
                <th key={h} style={{ padding: "7px 8px", color: "#fff", fontSize: 10, fontWeight: 700, textAlign: h === "Item" ? "left" : "right" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ padding: "10px 8px", fontSize: 11, color: "#111" }}>
                <div style={{ fontWeight: 600 }}>{order.product}</div>
                {order.isCustom && <div style={{ fontSize: 9, color: "#25D366", fontWeight: 700 }}>✦ Custom Logo</div>}
              </td>
              <td style={{ padding: "10px 8px", fontSize: 11, color: "#555", textAlign: "right" }}>{order.size}</td>
              <td style={{ padding: "10px 8px", fontSize: 11, color: "#555", textAlign: "right" }}>{order.qty}</td>
              <td style={{ padding: "10px 8px", fontSize: 11, color: "#555", textAlign: "right" }}>₹{order.pricePerPc}</td>
              <td style={{ padding: "10px 8px", fontSize: 12, fontWeight: 700, color: "#111", textAlign: "right" }}>{formatINR(subtotal)}</td>
            </tr>
          </tbody>
        </table>

        {/* Totals + QR */}
        <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
          <div style={{ flex: 1 }}>
            {[["Subtotal", formatINR(subtotal)], ["GST (18%)", formatINR(gst)], ["Shipping", shipping === 0 ? "FREE 🎉" : formatINR(shipping)]].map(([l, v]) => (
              <div key={l} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", borderBottom: "1px dashed #eee", fontSize: 11, color: "#555" }}>
                <span>{l}</span><span style={{ color: l === "Shipping" && shipping === 0 ? "#25D366" : "#111" }}>{v}</span>
              </div>
            ))}
            <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", fontSize: 15, fontWeight: 800, color: "#1a1a2e", borderTop: "2px solid #1a1a2e", marginTop: 2 }}>
              <span>TOTAL</span><span>{formatINR(total)}</span>
            </div>
          </div>

          <div style={{ background: "#f8f9ff", borderRadius: 10, padding: "10px", textAlign: "center", minWidth: 100 }}>
            <img src={qrUrl} alt="UPI QR" style={{ width: 80, height: 80, borderRadius: 6 }} />
            <div style={{ fontSize: 9, fontWeight: 700, color: "#1a1a2e", marginTop: 4 }}>Scan & Pay</div>
            <div style={{ fontSize: 9, color: "#999" }}>kitpak@okaxis</div>
            <div style={{ fontSize: 12, fontWeight: 800, color: "#25D366", marginTop: 2 }}>{formatINR(total)}</div>
          </div>
        </div>

        {/* Instructions */}
        <div style={{ background: "#fff8e1", borderRadius: 8, padding: "10px 12px", marginTop: 12, border: "1px solid #ffe082" }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: "#f57c00", marginBottom: 3 }}>📲 Payment Instructions</div>
          <div style={{ fontSize: 10, color: "#555", lineHeight: 1.7 }}>
            1. Scan QR with GPay / PhonePe / Paytm<br />
            2. Pay exactly <strong>{formatINR(total)}</strong><br />
            3. Share UTR / transaction ID to confirm order<br />
            4. Dispatch within 2–3 business days ✅
          </div>
        </div>

        <div style={{ textAlign: "center", marginTop: 10, fontSize: 9, color: "#bbb" }}>
          Thank you for choosing KITPAK! 📦 · Computer generated invoice
        </div>
      </div>
    </div>
  );
}

function PaymentGateway({ order, invoiceNo, onPaid, onBack }) {
  const subtotal = order.qty * order.pricePerPc;
  const total = subtotal + Math.round(subtotal * 0.18) + (subtotal >= 999 ? 0 : 99);
  const upiLink = `upi://pay?pa=kitpak@okaxis&pn=KITPAK&am=${total}&cu=INR&tn=${invoiceNo}`;
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(upiLink)}&bgcolor=ffffff&color=075E54&margin=10`;
  const [utr, setUtr] = useState("");
  const [confirming, setConfirming] = useState(false);
  const [method, setMethod] = useState("qr");

  const confirm = async () => {
    if (!utr.trim()) return;
    setConfirming(true);
    await new Promise(r => setTimeout(r, 1800));
    onPaid(utr);
  };

  return (
    <div style={{ background: "#fff", borderRadius: 16, overflow: "hidden", boxShadow: "0 8px 32px rgba(0,0,0,0.2)" }}>
      {/* Header */}
      <div style={{ background: "linear-gradient(135deg, #075E54, #128C7E)", padding: "16px 20px", display: "flex", alignItems: "center", gap: 10 }}>
        <button onClick={onBack} style={{ background: "rgba(255,255,255,0.15)", border: "none", borderRadius: 8, padding: "4px 10px", color: "#fff", fontSize: 12, cursor: "pointer" }}>← Back</button>
        <div style={{ flex: 1, textAlign: "center" }}>
          <div style={{ color: "#fff", fontWeight: 800, fontSize: 15 }}>KITPAK Payment</div>
          <div style={{ color: "rgba(255,255,255,0.7)", fontSize: 11 }}>Invoice {invoiceNo}</div>
        </div>
        <div style={{ background: "rgba(255,255,255,0.15)", borderRadius: 8, padding: "4px 10px" }}>
          <div style={{ color: "#fff", fontWeight: 800, fontSize: 14 }}>{formatINR(total)}</div>
        </div>
      </div>

      <div style={{ padding: "20px" }}>
        {/* Method tabs */}
        <div style={{ display: "flex", gap: 8, marginBottom: 18 }}>
          {[["qr", "📱 UPI QR"], ["upi", "🔗 UPI ID"], ["bank", "🏦 Bank"]].map(([m, label]) => (
            <button key={m} onClick={() => setMethod(m)} style={{
              flex: 1, padding: "8px", borderRadius: 8, border: "none",
              background: method === m ? "#075E54" : "#f0f0f0",
              color: method === m ? "#fff" : "#555",
              fontSize: 11, fontWeight: 700, cursor: "pointer",
              transition: "all 0.2s"
            }}>{label}</button>
          ))}
        </div>

        {method === "qr" && (
          <div style={{ textAlign: "center" }}>
            <div style={{ display: "inline-block", padding: 12, background: "#f8f9ff", borderRadius: 16, border: "2px solid #e0e7ff", marginBottom: 12 }}>
              <img src={qrUrl} alt="UPI QR" style={{ width: 180, height: 180, display: "block", borderRadius: 8 }} />
            </div>
            <div style={{ color: "#555", fontSize: 12, marginBottom: 4 }}>Scan with any UPI app</div>
            <div style={{ display: "flex", justifyContent: "center", gap: 12, marginBottom: 16 }}>
              {["GPay", "PhonePe", "Paytm", "BHIM"].map(app => (
                <div key={app} style={{ fontSize: 10, color: "#999", textAlign: "center" }}>
                  <div style={{ width: 32, height: 32, background: "#f0f0f0", borderRadius: 8, margin: "0 auto 2px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16 }}>
                    {app === "GPay" ? "G" : app === "PhonePe" ? "P" : app === "Paytm" ? "P" : "B"}
                  </div>
                  {app}
                </div>
              ))}
            </div>
          </div>
        )}

        {method === "upi" && (
          <div style={{ textAlign: "center", padding: "10px 0" }}>
            <div style={{ background: "#f8f9ff", borderRadius: 12, padding: "16px", marginBottom: 16 }}>
              <div style={{ fontSize: 11, color: "#999", marginBottom: 4 }}>UPI ID</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: "#075E54", letterSpacing: 1 }}>kitpak@okaxis</div>
              <div style={{ fontSize: 12, color: "#555", marginTop: 4 }}>Amount: <strong>{formatINR(total)}</strong></div>
            </div>
            <div style={{ color: "#555", fontSize: 12 }}>Open your UPI app → Send money → Enter above ID & amount</div>
          </div>
        )}

        {method === "bank" && (
          <div style={{ background: "#f8f9ff", borderRadius: 12, padding: "14px", marginBottom: 16 }}>
            {[["Account Name", "KITPAK"], ["Account No", "XXXX XXXX 1234"], ["IFSC", "HDFC0001234"], ["Bank", "HDFC Bank"], ["Amount", formatINR(total)]].map(([l, v]) => (
              <div key={l} style={{ display: "flex", justifyContent: "space-between", padding: "5px 0", borderBottom: "1px solid #e8e8e8", fontSize: 12 }}>
                <span style={{ color: "#999" }}>{l}</span>
                <span style={{ fontWeight: 700, color: l === "Amount" ? "#075E54" : "#111" }}>{v}</span>
              </div>
            ))}
          </div>
        )}

        {/* UTR input */}
        <div style={{ background: "#f8f9ff", borderRadius: 12, padding: "14px", border: "1px solid #e0e7ff" }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: "#1a1a2e", marginBottom: 8 }}>
            ✅ Paid? Enter your UTR / Transaction ID
          </div>
          <input
            value={utr}
            onChange={e => setUtr(e.target.value)}
            placeholder="e.g. T2406123456789"
            style={{
              width: "100%", padding: "10px 12px",
              borderRadius: 8, border: "1px solid #ddd",
              fontSize: 13, fontFamily: "inherit",
              boxSizing: "border-box", marginBottom: 10
            }}
          />
          <button onClick={confirm} disabled={!utr.trim() || confirming} style={{
            width: "100%", padding: "12px",
            background: utr.trim() && !confirming ? "linear-gradient(135deg, #25D366, #075E54)" : "#ccc",
            border: "none", borderRadius: 8,
            color: "#fff", fontSize: 13, fontWeight: 700,
            cursor: utr.trim() && !confirming ? "pointer" : "default",
            transition: "all 0.2s"
          }}>
            {confirming ? "Verifying..." : "Confirm Payment →"}
          </button>
        </div>
      </div>
    </div>
  );
}

function SuccessScreen({ order, invoiceNo, utr }) {
  const subtotal = order.qty * order.pricePerPc;
  const total = subtotal + Math.round(subtotal * 0.18) + (subtotal >= 999 ? 0 : 99);
  return (
    <div style={{ background: "#fff", borderRadius: 16, overflow: "hidden", boxShadow: "0 8px 32px rgba(0,0,0,0.2)", textAlign: "center" }}>
      <div style={{ background: "linear-gradient(135deg, #25D366, #075E54)", padding: "30px 20px" }}>
        <div style={{ fontSize: 56, marginBottom: 8, animation: "bounce 0.5s ease" }}>🎉</div>
        <div style={{ color: "#fff", fontSize: 20, fontWeight: 800 }}>Payment Confirmed!</div>
        <div style={{ color: "rgba(255,255,255,0.8)", fontSize: 13, marginTop: 4 }}>{formatINR(total)} received</div>
      </div>
      <div style={{ padding: "20px" }}>
        {[
          ["Invoice", invoiceNo],
          ["Customer", order.name],
          ["Product", `${order.colour} ${order.size}`],
          ["Quantity", `${order.qty} pcs`],
          ["UTR / Txn ID", utr],
          ["Status", "✅ Confirmed"]
        ].map(([l, v]) => (
          <div key={l} style={{ display: "flex", justifyContent: "space-between", padding: "7px 0", borderBottom: "1px solid #f0f0f0", fontSize: 12 }}>
            <span style={{ color: "#999" }}>{l}</span>
            <span style={{ fontWeight: 700, color: l === "Status" ? "#25D366" : "#111" }}>{v}</span>
          </div>
        ))}
        <div style={{ background: "#f8f9ff", borderRadius: 10, padding: "12px", marginTop: 14, border: "1px solid #e0e7ff" }}>
          <div style={{ fontSize: 12, color: "#555", lineHeight: 1.7 }}>
            📦 Your order is confirmed!<br />
            🚚 Dispatch within 2–3 business days<br />
            📱 You'll receive tracking details on WhatsApp<br />
            💬 Questions? Reply to this WhatsApp chat
          </div>
        </div>
        <div style={{ marginTop: 14, color: "#999", fontSize: 11 }}>
          A notification has been sent to KITPAK team ✅
        </div>
      </div>
    </div>
  );
}

export default function KitpakFullDemo() {
  const [screen, setScreen] = useState("chat"); // chat | invoice | payment | success
  const [messages, setMessages] = useState(DEMO_MESSAGES);
  const [botTyping, setBotTyping] = useState(false);
  const [orderReady, setOrderReady] = useState(false);
  const [order] = useState(DEMO_ORDER);
  const [invoiceNo] = useState(invNo());
  const [utr, setUtrState] = useState("");
  const [input, setInput] = useState("");
  const [history, setHistory] = useState([
    ...DEMO_MESSAGES.map(m => ({ role: m.role === "bot" ? "assistant" : "user", content: m.text }))
  ]);
  const bottomRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, botTyping]);

  // Show order ready button after demo messages
  useEffect(() => {
    const t = setTimeout(() => setOrderReady(true), 800);
    return () => clearTimeout(t);
  }, []);

  const sendMessage = async (text) => {
    if (!text.trim() || botTyping) return;
    const userMsg = { role: "user", text, time: nowTime() };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setBotTyping(true);
    const newHistory = [...history, { role: "user", content: text }];
    try {
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: "claude-sonnet-4-20250514", max_tokens: 400, system: SYSTEM_PROMPT, messages: newHistory })
      });
      const data = await res.json();
      const raw = data.content?.[0]?.text || "";
      const cleanText = raw.replace(/ORDER_READY:.*$/s, "").trim();
      setMessages(prev => [...prev, { role: "bot", text: cleanText || "Order confirmed! Generating your invoice...", time: nowTime() }]);
      setHistory([...newHistory, { role: "assistant", content: raw }]);
      if (raw.includes("ORDER_READY:")) setOrderReady(true);
    } catch {
      setMessages(prev => [...prev, { role: "bot", text: "Error. Try again!", time: nowTime() }]);
    }
    setBotTyping(false);
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0a0a0a, #1a1a2e, #0f3460)",
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      padding: "20px", fontFamily: "'Segoe UI', system-ui, sans-serif"
    }}>
      <style>{`
        @keyframes fadeUp { from { opacity:0;transform:translateY(8px); } to { opacity:1;transform:translateY(0); } }
        @keyframes bounce { 0%,60%,100% { transform:translateY(0); } 30% { transform:translateY(-8px); } }
        @keyframes pulse { 0%,100%{opacity:1;}50%{opacity:0.4;} }
        textarea:focus,input:focus{outline:none;}
        textarea{resize:none;}
        ::-webkit-scrollbar{width:3px;}
        ::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.15);border-radius:2px;}
      `}</style>

      {/* Top label */}
      <div style={{ textAlign: "center", marginBottom: 14 }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "rgba(37,211,102,0.1)", border: "1px solid rgba(37,211,102,0.2)", borderRadius: 20, padding: "5px 14px", marginBottom: 6 }}>
          <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#25D366", animation: "pulse 2s infinite" }} />
          <span style={{ color: "#25D366", fontSize: 11, fontWeight: 700, letterSpacing: 1 }}>KITPAK — Full Order Demo</span>
        </div>
        {/* Step indicator */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 4 }}>
          {[["chat", "💬 Chat"], ["invoice", "📄 Invoice"], ["payment", "💳 Pay"], ["success", "✅ Done"]].map(([s, label], i) => (
            <div key={s} style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <div style={{
                padding: "3px 10px", borderRadius: 12, fontSize: 10, fontWeight: 700,
                background: screen === s ? "#25D366" : "rgba(255,255,255,0.08)",
                color: screen === s ? "#fff" : "rgba(255,255,255,0.3)",
                transition: "all 0.3s"
              }}>{label}</div>
              {i < 3 && <span style={{ color: "rgba(255,255,255,0.2)", fontSize: 10 }}>→</span>}
            </div>
          ))}
        </div>
      </div>

      <div style={{ width: "100%", maxWidth: 400 }}>
        {/* CHAT SCREEN */}
        {screen === "chat" && (
          <div style={{ background: "#111", borderRadius: 24, overflow: "hidden", boxShadow: "0 32px 64px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.06)", display: "flex", flexDirection: "column", height: 580 }}>
            {/* WA Header */}
            <div style={{ background: "#075E54", padding: "10px 14px", display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: "50%", background: "linear-gradient(135deg,#25D366,#128C7E)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 15, fontWeight: 900, color: "#fff" }}>K</div>
              <div style={{ flex: 1 }}>
                <div style={{ color: "#fff", fontWeight: 700, fontSize: 13 }}>KITPAK</div>
                <div style={{ color: "rgba(255,255,255,0.6)", fontSize: 10 }}>📦 Bot Active · Typically replies instantly</div>
              </div>
              <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#25D366", animation: "pulse 2s infinite" }} />
            </div>

            {/* Messages */}
            <div style={{ flex: 1, overflowY: "auto", padding: "10px 10px 6px", background: "#ECE5DD", backgroundImage: "radial-gradient(circle at 1px 1px,rgba(0,0,0,0.03) 1px,transparent 0)", backgroundSize: "18px 18px" }}>
              {messages.map((m, i) => <ChatBubble key={i} msg={m} />)}
              {botTyping && (
                <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: 6 }}>
                  <div style={{ background: "#fff", borderRadius: "16px 16px 16px 4px", padding: "10px 14px", display: "flex", gap: 4, boxShadow: "0 1px 2px rgba(0,0,0,0.1)" }}>
                    {[0,1,2].map(i => <div key={i} style={{ width: 7, height: 7, borderRadius: "50%", background: "#25D366", animation: `bounce 1.2s infinite`, animationDelay: `${i*0.2}s` }} />)}
                  </div>
                </div>
              )}
              {orderReady && (
                <div style={{ textAlign: "center", margin: "10px 0", animation: "fadeUp 0.4s ease" }}>
                  <div style={{ color: "#888", fontSize: 10, marginBottom: 8 }}>— Order details collected ✅ —</div>
                  <button onClick={() => setScreen("invoice")} style={{
                    background: "linear-gradient(135deg,#25D366,#075E54)",
                    border: "none", borderRadius: 20, padding: "10px 24px",
                    color: "#fff", fontSize: 13, fontWeight: 700, cursor: "pointer",
                    boxShadow: "0 4px 16px rgba(37,211,102,0.4)"
                  }}>📄 Generate Invoice & Payment →</button>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div style={{ background: "#F0F0F0", padding: "7px 10px 10px", display: "flex", alignItems: "flex-end", gap: 8 }}>
              <div style={{ flex: 1, background: "#fff", borderRadius: 22, padding: "7px 12px", boxShadow: "0 1px 3px rgba(0,0,0,0.08)" }}>
                <textarea value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(input); } }} placeholder="Continue the conversation..." rows={1} style={{ width: "100%", border: "none", fontSize: 13, color: "#111", background: "transparent", fontFamily: "inherit", lineHeight: 1.4, maxHeight: 60, overflowY: "auto", boxSizing: "border-box" }} />
              </div>
              <button onClick={() => sendMessage(input)} disabled={!input.trim() || botTyping} style={{ width: 40, height: 40, borderRadius: "50%", background: input.trim() && !botTyping ? "#25D366" : "#ccc", border: "none", cursor: input.trim() && !botTyping ? "pointer" : "default", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, transition: "all 0.2s" }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="white"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg>
              </button>
            </div>
          </div>
        )}

        {/* INVOICE SCREEN */}
        {screen === "invoice" && (
          <div style={{ animation: "fadeUp 0.3s ease" }}>
            <Invoice order={order} invoiceNo={invoiceNo} />
            <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
              <button onClick={() => setScreen("chat")} style={{ flex: 1, padding: "11px", background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 10, color: "#fff", fontSize: 12, fontWeight: 600, cursor: "pointer" }}>← Back to Chat</button>
              <button onClick={() => setScreen("payment")} style={{ flex: 2, padding: "11px", background: "linear-gradient(135deg,#25D366,#075E54)", border: "none", borderRadius: 10, color: "#fff", fontSize: 13, fontWeight: 700, cursor: "pointer", boxShadow: "0 4px 16px rgba(37,211,102,0.3)" }}>💳 Proceed to Payment →</button>
            </div>
          </div>
        )}

        {/* PAYMENT SCREEN */}
        {screen === "payment" && (
          <div style={{ animation: "fadeUp 0.3s ease" }}>
            <PaymentGateway order={order} invoiceNo={invoiceNo} onPaid={(u) => { setUtrState(u); setScreen("success"); }} onBack={() => setScreen("invoice")} />
          </div>
        )}

        {/* SUCCESS SCREEN */}
        {screen === "success" && (
          <div style={{ animation: "fadeUp 0.3s ease" }}>
            <SuccessScreen order={order} invoiceNo={invoiceNo} utr={utr} />
            <button onClick={() => { setScreen("chat"); setMessages(DEMO_MESSAGES); setHistory(DEMO_MESSAGES.map(m => ({ role: m.role === "bot" ? "assistant" : "user", content: m.text }))); setOrderReady(true); }} style={{ width: "100%", marginTop: 10, padding: "11px", background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 10, color: "#fff", fontSize: 12, fontWeight: 600, cursor: "pointer" }}>
              🔄 Start New Demo
            </button>
          </div>
        )}
      </div>

      <div style={{ marginTop: 14, color: "rgba(255,255,255,0.2)", fontSize: 11 }}>
        KITPAK WhatsApp Automation · Full Flow Demo
      </div>
    </div>
  );
}
