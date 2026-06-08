import { useState } from "react";

const SAMPLE_ORDERS = [
  {
    orderId: "KP-2026-001",
    customerName: "Priya Sharma",
    address: "42, Anna Nagar, 2nd Street",
    city: "Chennai",
    state: "Tamil Nadu",
    pincode: "600040",
    phone: "9876543210",
    products: [
      { name: "White Courier Covers 10x12", qty: "200 pcs" }
    ],
    courier: "ST Courier",
    date: "07 Jun 2026"
  },
  {
    orderId: "KP-2026-002",
    customerName: "Ravi Kumar",
    address: "15, MG Road, Indiranagar",
    city: "Bangalore",
    state: "Karnataka",
    pincode: "560038",
    phone: "9845123456",
    products: [
      { name: "Pink Courier Covers 8x10", qty: "100 pcs" },
      { name: "White Courier Covers 10x12", qty: "200 pcs" },
      { name: "Shipping Labels 4cut A4", qty: "2 packs" }
    ],
    courier: "DTDC",
    date: "07 Jun 2026"
  },
  {
    orderId: "KP-2026-003",
    customerName: "Meena Textiles",
    address: "Plot 7, Sector 15, Dwarka",
    city: "New Delhi",
    state: "Delhi",
    pincode: "110078",
    phone: "9711234567",
    products: [
      { name: "Custom White Covers 12x16", qty: "500 pcs" },
      { name: "Honeycomb Paper Roll 10mtr", qty: "3 rolls" },
      { name: "Thermal Labels 100x150mm", qty: "1 roll" },
      { name: "Packing Covers 9.5x11.5", qty: "100 pcs" },
    ],
    courier: "India Post",
    date: "07 Jun 2026"
  }
];

function ShippingLabel({ order }) {
  const isMulti = order.products.length > 1;

  return (
    <div style={{
      width: 384,
      height: 576,
      border: "2px solid #000",
      fontFamily: "'Courier New', monospace",
      background: "#fff",
      display: "flex",
      flexDirection: "column",
      overflow: "hidden",
      boxShadow: "0 4px 20px rgba(0,0,0,0.3)"
    }}>

      {/* FROM */}
      <div style={{ padding: "10px 12px 8px", borderBottom: "2px solid #000" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div style={{ fontSize: 16, fontWeight: 900, letterSpacing: 2 }}>KITPAK</div>
            <div style={{ fontSize: 9, color: "#333" }}>SARAVANA TRADING</div>
            <div style={{ fontSize: 8.5, color: "#555" }}>55C, Valayangadu Main Road</div>
            <div style={{ fontSize: 8.5, color: "#555" }}>Kumar Nagar South, Tirupur - 641605</div>
            <div style={{ fontSize: 8.5, color: "#555" }}>Ph: 83004 75706</div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 8, color: "#777", marginBottom: 2 }}>ORDER ID</div>
            <div style={{ fontSize: 12, fontWeight: 900 }}>{order.orderId}</div>
            <div style={{ fontSize: 8, color: "#777", marginTop: 4 }}>DATE</div>
            <div style={{ fontSize: 9, fontWeight: 700 }}>{order.date}</div>
          </div>
        </div>
      </div>

      {/* TO */}
      <div style={{ padding: "10px 12px 8px", borderBottom: "2px solid #000", flex: isMulti ? "0 0 auto" : 1 }}>
        <div style={{ fontSize: 8, fontWeight: 700, color: "#555", letterSpacing: 2, marginBottom: 5 }}>DELIVER TO:</div>
        <div style={{ fontSize: 15, fontWeight: 900, textTransform: "uppercase", marginBottom: 3 }}>
          {order.customerName}
        </div>
        <div style={{ fontSize: 11, color: "#222", lineHeight: 1.55 }}>{order.address}</div>
        <div style={{ fontSize: 11, color: "#222" }}>{order.city} - {order.pincode}</div>
        <div style={{ fontSize: 11, color: "#222" }}>{order.state}</div>
        <div style={{ fontSize: 12, fontWeight: 700, marginTop: 5 }}>Ph: {order.phone}</div>
      </div>

      {/* PRODUCTS */}
      <div style={{ padding: "10px 12px", borderBottom: "2px solid #000", background: "#fff", flex: 1 }}>
        <div style={{ fontSize: 9, fontWeight: 700, color: "#000", letterSpacing: 2, marginBottom: 8, borderBottom: "2px solid #000", paddingBottom: 4 }}>
          {isMulti ? `PACKING LIST — ${order.products.length} ITEMS` : "PACKING LIST"}
        </div>

        {order.products.map((p, i) => (
          <div key={i} style={{
            display: "flex", justifyContent: "space-between",
            alignItems: "center",
            padding: "6px 0",
            borderBottom: i < order.products.length - 1 ? "1px solid #000" : "none"
          }}>
            <div style={{ fontSize: isMulti ? 12 : 14, color: "#000", fontWeight: 800, flex: 1, lineHeight: 1.3 }}>{p.name}</div>
            <div style={{
              fontSize: isMulti ? 13 : 15, fontWeight: 900,
              color: "#000",
              border: "1.5px solid #000",
              padding: "2px 10px", borderRadius: 4, marginLeft: 10,
              flexShrink: 0, letterSpacing: 1
            }}>{p.qty}</div>
          </div>
        ))}
      </div>

      {/* FOOTER */}
      <div style={{
        padding: "7px 12px",
        borderTop: "2px solid #000",
        background: "#fff",
        display: "flex", justifyContent: "space-between", alignItems: "center"
      }}>
        <div style={{ fontSize: 10, color: "#000", fontWeight: 900, letterSpacing: 1 }}>KITPAK.IN</div>
        <div style={{ fontSize: 9, color: "#000" }}>Handle with care</div>
        <div style={{
          fontSize: 10, color: "#000", fontWeight: 900,
          border: "1.5px solid #000", padding: "2px 8px", borderRadius: 4
        }}>{order.courier}</div>
      </div>
    </div>
  );
}

export default function LabelDemo() {
  const [selected, setSelected] = useState(0);

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0a0a0a, #1a1a2e)",
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      padding: "24px 16px",
      fontFamily: "'Segoe UI', system-ui, sans-serif"
    }}>
      <style>{`
        @keyframes fadeUp{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}
        @media print{body *{visibility:hidden;}#print-label,#print-label *{visibility:visible;}#print-label{position:fixed;top:0;left:0;}}
      `}</style>

      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 20 }}>
        <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 11, letterSpacing: 2, marginBottom: 6 }}>KITPAK — SHIPPING LABEL MOCKUP</div>
        <div style={{ color: "#fff", fontSize: 20, fontWeight: 800 }}>4×6 Thermal Label — No Barcode</div>
        <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 11, marginTop: 4 }}>Switch between single & multiple product orders</div>
      </div>

      {/* Order tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap", justifyContent: "center" }}>
        {SAMPLE_ORDERS.map((o, i) => (
          <button key={i} onClick={() => setSelected(i)} style={{
            padding: "7px 14px", borderRadius: 20, border: "none",
            background: selected === i ? "#25D366" : "rgba(255,255,255,0.08)",
            color: selected === i ? "#fff" : "rgba(255,255,255,0.5)",
            fontSize: 11, fontWeight: 700, cursor: "pointer", transition: "all 0.2s"
          }}>
            {o.products.length === 1 ? "1 Product" : `${o.products.length} Products`} — {o.courier}
          </button>
        ))}
      </div>

      {/* Label */}
      <div style={{ animation: "fadeUp 0.3s ease", marginBottom: 20 }} id="print-label">
        <ShippingLabel order={SAMPLE_ORDERS[selected]} />
      </div>

      {/* Info chips */}
      <div style={{
        background: "rgba(255,255,255,0.05)",
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: 12, padding: "10px 20px",
        display: "flex", gap: 24, marginBottom: 16
      }}>
        {[["Size", "4×6 inches"], ["Barcode", "Removed ✅"], ["Printer", "Thermal"], ["Courier", "Auto-assigned"]].map(([l, v]) => (
          <div key={l} style={{ textAlign: "center" }}>
            <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 9, letterSpacing: 1 }}>{l}</div>
            <div style={{ color: "#fff", fontSize: 11, fontWeight: 700, marginTop: 2 }}>{v}</div>
          </div>
        ))}
      </div>

      <button onClick={() => window.print()} style={{
        padding: "10px 28px", borderRadius: 10,
        background: "#25D366", border: "none",
        color: "#fff", fontSize: 13, fontWeight: 700, cursor: "pointer"
      }}>🖨️ Print This Label</button>

      <div style={{ marginTop: 12, color: "rgba(255,255,255,0.2)", fontSize: 10 }}>
        Switch tabs above to see how multiple products appear on one label
      </div>
    </div>
  );
}
