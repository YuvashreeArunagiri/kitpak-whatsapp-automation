import { useState } from "react";

const ORDERS = [
  { id: "KP-2026-001", customer: "Priya Sharma", city: "Chennai", pincode: "600040", state: "Tamil Nadu", address: "42, Anna Nagar, 2nd Street", phone: "9876543210", products: [{ name: "White Courier Covers 10x12", qty: "200 pcs" }], courier: "ST Courier", date: "07 Jun 2026", status: "Paid" },
  { id: "KP-2026-002", customer: "Ravi Kumar", city: "Bangalore", pincode: "560038", state: "Karnataka", address: "15, MG Road, Indiranagar", phone: "9845123456", products: [{ name: "Pink Covers 8x10", qty: "100 pcs" }, { name: "Shipping Labels A4", qty: "2 packs" }], courier: "DTDC", date: "07 Jun 2026", status: "Paid" },
  { id: "KP-2026-003", customer: "Meena Textiles", city: "New Delhi", pincode: "110078", state: "Delhi", address: "Plot 7, Sector 15, Dwarka", phone: "9711234567", products: [{ name: "Custom White Covers 12x16", qty: "500 pcs" }, { name: "Honeycomb Roll 10mtr", qty: "3 rolls" }], courier: "India Post", date: "07 Jun 2026", status: "Paid" },
  { id: "KP-2026-004", customer: "Lakshmi Stores", city: "Coimbatore", pincode: "641001", state: "Tamil Nadu", address: "23, RS Puram, Main Road", phone: "9942123456", products: [{ name: "Purple Covers 10x12", qty: "100 pcs" }], courier: "ST Courier", date: "07 Jun 2026", status: "Paid" },
  { id: "KP-2026-005", customer: "Arjun Exports", city: "Hyderabad", pincode: "500032", state: "Telangana", address: "8-2-120, Banjara Hills", phone: "9848012345", products: [{ name: "Meesho Transparent 10x12", qty: "200 pcs" }, { name: "Packing Covers 9.5x11.5", qty: "100 pcs" }], courier: "DTDC", date: "07 Jun 2026", status: "Paid" },
  { id: "KP-2026-006", customer: "Vijay Fashion", city: "Madurai", pincode: "625001", state: "Tamil Nadu", address: "45, Bypass Road, SS Colony", phone: "9944567890", products: [{ name: "Black Covers 12x14", qty: "300 pcs" }], courier: "ST Courier", date: "07 Jun 2026", status: "Paid" },
  { id: "KP-2026-007", customer: "Kochi Crafts", city: "Kochi", pincode: "682001", state: "Kerala", address: "12, MG Road, Ernakulam", phone: "9847123456", products: [{ name: "White Covers 6x8", qty: "500 pcs" }, { name: "Thermal Labels 100x150", qty: "1 roll" }, { name: "Honeycomb Sleeve 20cm", qty: "100 pcs" }], courier: "DTDC", date: "07 Jun 2026", status: "Paid" },
  { id: "KP-2026-008", customer: "Sunrise Traders", city: "Jaipur", pincode: "302001", state: "Rajasthan", address: "56, MI Road, Sindhi Camp", phone: "9829012345", products: [{ name: "White Covers 10x14", qty: "200 pcs" }], courier: "India Post", date: "07 Jun 2026", status: "Paid" },
  { id: "KP-2026-009", customer: "Nila Boutique", city: "Tirupur", pincode: "641604", state: "Tamil Nadu", address: "7, New Street, Avinashi Road", phone: "9943456789", products: [{ name: "Custom Pink Covers 8x10", qty: "100 pcs" }], courier: "ST Courier", date: "07 Jun 2026", status: "Paid" },
  { id: "KP-2026-010", customer: "Mumbai Mart", city: "Mumbai", pincode: "400001", state: "Maharashtra", address: "34, Colaba Causeway, Fort", phone: "9820123456", products: [{ name: "White Covers 14x18", qty: "100 pcs" }, { name: "Flipkart Covers SB2", qty: "200 pcs" }], courier: "India Post", date: "07 Jun 2026", status: "Paid" },
];

const COURIER_COLORS = {
  "ST Courier": "#25D366",
  "DTDC": "#f59e0b",
  "India Post": "#38bdf8",
};

function ShippingLabel({ order }) {
  return (
    <div style={{
      width: 384, height: 576,
      border: "2px solid #000",
      fontFamily: "'Courier New', monospace",
      background: "#fff",
      display: "flex", flexDirection: "column",
      overflow: "hidden", pageBreakAfter: "always"
    }}>
      {/* FROM */}
      <div style={{ padding: "10px 12px 8px", borderBottom: "2px solid #000" }}>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <div>
            <div style={{ fontSize: 16, fontWeight: 900, letterSpacing: 2 }}>KITPAK</div>
            <div style={{ fontSize: 9, color: "#333" }}>SARAVANA TRADING</div>
            <div style={{ fontSize: 8, color: "#555" }}>55C, Valayangadu Main Road, Kumar Nagar South</div>
            <div style={{ fontSize: 8, color: "#555" }}>Tirupur - 641605 · Ph: 83004 75706</div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 8, color: "#777" }}>ORDER ID</div>
            <div style={{ fontSize: 12, fontWeight: 900 }}>{order.id}</div>
            <div style={{ fontSize: 8, color: "#777", marginTop: 3 }}>DATE</div>
            <div style={{ fontSize: 9, fontWeight: 700 }}>{order.date}</div>
          </div>
        </div>
      </div>

      {/* TO */}
      <div style={{ padding: "10px 12px 8px", borderBottom: "2px solid #000" }}>
        <div style={{ fontSize: 8, fontWeight: 700, color: "#555", letterSpacing: 2, marginBottom: 4 }}>DELIVER TO:</div>
        <div style={{ fontSize: 15, fontWeight: 900, textTransform: "uppercase", marginBottom: 3 }}>{order.customer}</div>
        <div style={{ fontSize: 11, color: "#222", lineHeight: 1.55 }}>{order.address}</div>
        <div style={{ fontSize: 11, color: "#222" }}>{order.city} - {order.pincode}</div>
        <div style={{ fontSize: 11, color: "#222" }}>{order.state}</div>
        <div style={{ fontSize: 12, fontWeight: 700, marginTop: 5 }}>Ph: {order.phone}</div>
      </div>

      {/* PRODUCTS */}
      <div style={{ padding: "10px 12px", borderBottom: "2px solid #000", background: "#fff", flex: 1 }}>
        <div style={{ fontSize: 9, fontWeight: 700, color: "#000", letterSpacing: 2, marginBottom: 8, borderBottom: "2px solid #000", paddingBottom: 4 }}>
          {order.products.length > 1 ? `PACKING LIST — ${order.products.length} ITEMS` : "PACKING LIST"}
        </div>
        {order.products.map((p, i) => (
          <div key={i} style={{
            display: "flex", justifyContent: "space-between", alignItems: "center",
            padding: "6px 0", borderBottom: i < order.products.length - 1 ? "1px solid #000" : "none"
          }}>
            <div style={{ fontSize: order.products.length > 1 ? 12 : 14, color: "#000", fontWeight: 800, flex: 1, lineHeight: 1.3 }}>{p.name}</div>
            <div style={{ fontSize: order.products.length > 1 ? 13 : 15, fontWeight: 900, color: "#000", border: "1.5px solid #000", padding: "2px 10px", borderRadius: 4, marginLeft: 10, flexShrink: 0, letterSpacing: 1 }}>{p.qty}</div>
          </div>
        ))}
      </div>

      {/* FOOTER */}
      <div style={{ padding: "7px 12px", borderTop: "2px solid #000", background: "#fff", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ fontSize: 10, color: "#000", fontWeight: 900, letterSpacing: 1 }}>KITPAK.IN</div>
        <div style={{ fontSize: 9, color: "#000" }}>Handle with care</div>
        <div style={{ fontSize: 10, color: "#000", fontWeight: 900, border: "1.5px solid #000", padding: "2px 8px", borderRadius: 4 }}>{order.courier}</div>
      </div>
    </div>
  );
}

export default function BulkLabelPrint() {
  const [selected, setSelected] = useState(new Set());
  const [view, setView] = useState("select"); // select | preview
  const [filterCourier, setFilterCourier] = useState("All");

  const toggleOrder = (id) => {
    const next = new Set(selected);
    next.has(id) ? next.delete(id) : next.add(id);
    setSelected(next);
  };

  const selectAll = () => setSelected(new Set(ORDERS.map(o => o.id)));
  const clearAll = () => setSelected(new Set());

  const selectByCourier = (courier) => {
    const ids = ORDERS.filter(o => o.courier === courier).map(o => o.id);
    setSelected(new Set(ids));
  };

  const filteredOrders = filterCourier === "All" ? ORDERS : ORDERS.filter(o => o.courier === filterCourier);
  const selectedOrders = ORDERS.filter(o => selected.has(o.id));

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0a0a0a, #1a1a2e)",
      fontFamily: "'Segoe UI', system-ui, sans-serif",
      padding: "20px 16px"
    }}>
      <style>{`
        @keyframes fadeUp{from{opacity:0;transform:translateY(6px);}to{opacity:1;transform:translateY(0);}}
        .order-row:hover{background:rgba(255,255,255,0.06)!important;}
        @media print{
          #screen-ui{display:none;}
          #print-area{display:block!important;}
          .label-page{page-break-after:always;}
        }
      `}</style>

      {/* Print area - hidden on screen */}
      <div id="print-area" style={{ display: "none" }}>
        {selectedOrders.map(o => (
          <div key={o.id} className="label-page">
            <ShippingLabel order={o} />
          </div>
        ))}
      </div>

      {/* Screen UI */}
      <div id="screen-ui">
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 20 }}>
          <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 11, letterSpacing: 2, marginBottom: 4 }}>KITPAK — DAILY DISPATCH</div>
          <div style={{ color: "#fff", fontSize: 22, fontWeight: 800 }}>Bulk Shipping Label Print</div>
          <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 11, marginTop: 4 }}>Select orders → Print all labels in one go</div>
        </div>

        {/* Stats */}
        <div style={{ display: "flex", gap: 10, justifyContent: "center", marginBottom: 16, flexWrap: "wrap" }}>
          {[
            { label: "Today's Orders", value: ORDERS.length, color: "#fff" },
            { label: "Selected", value: selected.size, color: "#25D366" },
            { label: "ST Courier", value: ORDERS.filter(o => o.courier === "ST Courier").length, color: "#25D366" },
            { label: "DTDC", value: ORDERS.filter(o => o.courier === "DTDC").length, color: "#f59e0b" },
            { label: "India Post", value: ORDERS.filter(o => o.courier === "India Post").length, color: "#38bdf8" },
          ].map(s => (
            <div key={s.label} style={{
              background: "rgba(255,255,255,0.05)", borderRadius: 10,
              padding: "8px 16px", textAlign: "center"
            }}>
              <div style={{ color: s.color, fontSize: 18, fontWeight: 800 }}>{s.value}</div>
              <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 10 }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 8, justifyContent: "center", marginBottom: 16, flexWrap: "wrap" }}>
          {["select", "preview"].map(v => (
            <button key={v} onClick={() => setView(v)} style={{
              padding: "7px 18px", borderRadius: 20, border: "none",
              background: view === v ? "#25D366" : "rgba(255,255,255,0.08)",
              color: view === v ? "#fff" : "rgba(255,255,255,0.5)",
              fontSize: 12, fontWeight: 700, cursor: "pointer"
            }}>{v === "select" ? "📋 Select Orders" : `🖨️ Preview Labels (${selected.size})`}</button>
          ))}
        </div>

        {view === "select" && (
          <div style={{ maxWidth: 720, margin: "0 auto", animation: "fadeUp 0.3s ease" }}>
            {/* Quick select buttons */}
            <div style={{ display: "flex", gap: 8, marginBottom: 12, flexWrap: "wrap" }}>
              <button onClick={selectAll} style={{ padding: "6px 14px", borderRadius: 16, border: "none", background: "#25D366", color: "#fff", fontSize: 11, fontWeight: 700, cursor: "pointer" }}>Select All ({ORDERS.length})</button>
              <button onClick={clearAll} style={{ padding: "6px 14px", borderRadius: 16, border: "none", background: "rgba(255,255,255,0.1)", color: "#fff", fontSize: 11, cursor: "pointer" }}>Clear All</button>
              <button onClick={() => selectByCourier("ST Courier")} style={{ padding: "6px 14px", borderRadius: 16, border: "1px solid #25D366", background: "transparent", color: "#25D366", fontSize: 11, cursor: "pointer" }}>ST Courier Only</button>
              <button onClick={() => selectByCourier("DTDC")} style={{ padding: "6px 14px", borderRadius: 16, border: "1px solid #f59e0b", background: "transparent", color: "#f59e0b", fontSize: 11, cursor: "pointer" }}>DTDC Only</button>
              <button onClick={() => selectByCourier("India Post")} style={{ padding: "6px 14px", borderRadius: 16, border: "1px solid #38bdf8", background: "transparent", color: "#38bdf8", fontSize: 11, cursor: "pointer" }}>India Post Only</button>
            </div>

            {/* Order list */}
            <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: 14, overflow: "hidden", border: "1px solid rgba(255,255,255,0.08)" }}>
              {/* Header row */}
              <div style={{ display: "grid", gridTemplateColumns: "40px 1fr 1fr 1fr 80px", padding: "10px 14px", background: "rgba(255,255,255,0.06)", gap: 8 }}>
                {["", "Customer", "Location", "Courier", "Items"].map(h => (
                  <div key={h} style={{ color: "rgba(255,255,255,0.4)", fontSize: 10, fontWeight: 700, letterSpacing: 1 }}>{h}</div>
                ))}
              </div>

              {ORDERS.map((order, i) => (
                <div key={order.id} className="order-row" onClick={() => toggleOrder(order.id)} style={{
                  display: "grid", gridTemplateColumns: "40px 1fr 1fr 1fr 80px",
                  padding: "12px 14px", gap: 8,
                  borderTop: "1px solid rgba(255,255,255,0.05)",
                  cursor: "pointer",
                  background: selected.has(order.id) ? "rgba(37,211,102,0.08)" : "transparent",
                  transition: "background 0.15s"
                }}>
                  {/* Checkbox */}
                  <div style={{
                    width: 20, height: 20, borderRadius: 5,
                    border: `2px solid ${selected.has(order.id) ? "#25D366" : "rgba(255,255,255,0.2)"}`,
                    background: selected.has(order.id) ? "#25D366" : "transparent",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    color: "#fff", fontSize: 12, fontWeight: 900, flexShrink: 0
                  }}>
                    {selected.has(order.id) ? "✓" : ""}
                  </div>

                  {/* Customer */}
                  <div>
                    <div style={{ color: "#fff", fontSize: 12, fontWeight: 600 }}>{order.customer}</div>
                    <div style={{ color: "rgba(255,255,255,0.3)", fontSize: 10 }}>{order.id}</div>
                  </div>

                  {/* Location */}
                  <div>
                    <div style={{ color: "rgba(255,255,255,0.7)", fontSize: 11 }}>{order.city}</div>
                    <div style={{ color: "rgba(255,255,255,0.3)", fontSize: 10 }}>{order.pincode} · {order.state}</div>
                  </div>

                  {/* Courier */}
                  <div>
                    <div style={{
                      display: "inline-block", padding: "2px 8px", borderRadius: 10,
                      fontSize: 10, fontWeight: 700,
                      background: `${COURIER_COLORS[order.courier]}20`,
                      color: COURIER_COLORS[order.courier] || "#fff",
                      border: `1px solid ${COURIER_COLORS[order.courier]}40`
                    }}>{order.courier}</div>
                  </div>

                  {/* Items */}
                  <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 11 }}>
                    {order.products.length} item{order.products.length > 1 ? "s" : ""}
                  </div>
                </div>
              ))}
            </div>

            {/* Print button */}
            {selected.size > 0 && (
              <div style={{ marginTop: 16, display: "flex", gap: 10, justifyContent: "center", animation: "fadeUp 0.2s ease" }}>
                <button onClick={() => setView("preview")} style={{
                  padding: "12px 28px", borderRadius: 10,
                  background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)",
                  color: "#fff", fontSize: 13, fontWeight: 700, cursor: "pointer"
                }}>👁️ Preview {selected.size} Labels</button>
                <button onClick={() => window.print()} style={{
                  padding: "12px 28px", borderRadius: 10,
                  background: "#25D366", border: "none",
                  color: "#fff", fontSize: 13, fontWeight: 700, cursor: "pointer",
                  boxShadow: "0 4px 16px rgba(37,211,102,0.3)"
                }}>🖨️ Print {selected.size} Labels Now</button>
              </div>
            )}
          </div>
        )}

        {view === "preview" && (
          <div style={{ animation: "fadeUp 0.3s ease" }}>
            {selected.size === 0 ? (
              <div style={{ textAlign: "center", color: "rgba(255,255,255,0.4)", padding: 40 }}>
                No orders selected. Go back and select orders to preview.
              </div>
            ) : (
              <>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 16, justifyContent: "center", marginBottom: 20 }}>
                  {selectedOrders.map(order => (
                    <div key={order.id} style={{ transform: "scale(0.65)", transformOrigin: "top center", marginBottom: -200 }}>
                      <ShippingLabel order={order} />
                    </div>
                  ))}
                </div>
                <div style={{ textAlign: "center", marginTop: 20 }}>
                  <button onClick={() => window.print()} style={{
                    padding: "12px 32px", borderRadius: 10,
                    background: "#25D366", border: "none",
                    color: "#fff", fontSize: 14, fontWeight: 700, cursor: "pointer",
                    boxShadow: "0 4px 16px rgba(37,211,102,0.3)"
                  }}>🖨️ Print All {selected.size} Labels</button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
