import { useState, useCallback } from "react";

const STEPS = [
  { id: "company", label: "Company" },
  { id: "scope", label: "Scope" },
  { id: "details", label: "Details" },
  { id: "review", label: "Review" },
];

const ENGAGEMENT_TYPES = [
  { id: "external", label: "External Network Pentest", desc: "Test internet-facing infrastructure", price: "$5,000–$15,000", days: "5–10" },
  { id: "webapp", label: "Web Application Assessment", desc: "OWASP Top 10 testing of web apps", price: "$4,000–$12,000", days: "3–7" },
  { id: "internal", label: "Internal Network Pentest", desc: "Test from inside the network", price: "$8,000–$20,000", days: "5–10" },
  { id: "redteam", label: "Red Team Engagement", desc: "Full adversary simulation", price: "$15,000–$50,000", days: "10–20" },
  { id: "wireless", label: "Wireless Security Assessment", desc: "WiFi and wireless testing", price: "$3,000–$8,000", days: "2–5" },
  { id: "cloud", label: "Cloud Security Review", desc: "AWS/Azure/GCP config audit", price: "$5,000–$15,000", days: "3–7" },
];

const METHODOLOGIES = [
  { id: "ptes", label: "PTES", desc: "Penetration Testing Execution Standard" },
  { id: "owasp", label: "OWASP", desc: "OWASP Testing Guide v4.2" },
  { id: "nist", label: "NIST SP 800-115", desc: "Technical Guide to Information Security Testing" },
  { id: "mitre", label: "MITRE ATT&CK", desc: "Adversary Tactics, Techniques, and Common Knowledge" },
];

export default function ClientIntake() {
  const [step, setStep] = useState(0);
  const [data, setData] = useState({
    company: "", contact: "", email: "", phone: "",
    type: "", methodology: "ptes",
    targets: "", excludes: "", webApps: "",
    timeWindow: "business_hours", startDate: "", duration: "",
    objectives: "", compliance: "", previousTests: "",
    socialEngineering: false, dosPermitted: false, physicalAccess: false,
    notes: "",
  });
  const [exported, setExported] = useState(false);

  const u = (field) => (val) => setData(d => ({ ...d, [field]: val }));
  const next = () => setStep(s => Math.min(s + 1, STEPS.length - 1));
  const prev = () => setStep(s => Math.max(s - 1, 0));

  const selectedType = ENGAGEMENT_TYPES.find(t => t.id === data.type);

  const exportJSON = useCallback(() => {
    const scope = {
      engagement: {
        id: `ENG-${new Date().toISOString().slice(0,10).replace(/-/g,"")}`,
        client: data.company,
        contact: data.contact,
        email: data.email,
        type: data.type,
        methodology: data.methodology,
        start_date: data.startDate,
        duration: data.duration,
        time_window: data.timeWindow,
      },
      scope: {
        in_scope: { targets: data.targets.split("\n").filter(Boolean) },
        out_of_scope: { targets: data.excludes.split("\n").filter(Boolean) },
        web_applications: data.webApps.split("\n").filter(Boolean),
        rules_of_engagement: [
          !data.dosPermitted && "No denial-of-service testing",
          !data.socialEngineering && "No social engineering without separate approval",
          !data.physicalAccess && "No physical access testing",
          "Stop testing immediately if production impact detected",
          "Report critical findings within 24 hours",
        ].filter(Boolean),
      },
      objectives: data.objectives,
      compliance: data.compliance,
      notes: data.notes,
    };
    navigator.clipboard?.writeText(JSON.stringify(scope, null, 2));
    setExported(true);
    setTimeout(() => setExported(false), 2000);
  }, [data]);

  return (
    <div style={cx.root}>
      <div style={cx.header}>
        <div>
          <div style={{ fontSize: "13px", fontWeight: 800, letterSpacing: "0.04em", color: "#f1f5f9" }}>
            PENTEST SCOPE QUESTIONNAIRE
          </div>
          <div style={{ fontSize: "9px", color: "#64748b", marginTop: "2px" }}>
            Aurora AI Agency — Client Intake
          </div>
        </div>
      </div>

      {/* Progress */}
      <div style={{ display: "flex", padding: "12px 16px", gap: "4px" }}>
        {STEPS.map((s, i) => (
          <div key={s.id} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: "4px" }}>
            <div style={{
              width: "100%", height: "3px", borderRadius: "2px",
              background: i <= step ? "#dc2626" : "#1e293b",
              transition: "background 0.3s",
            }} />
            <span style={{ fontSize: "8px", fontWeight: 600, color: i <= step ? "#dc2626" : "#475569", letterSpacing: "0.06em" }}>
              {s.label.toUpperCase()}
            </span>
          </div>
        ))}
      </div>

      <div style={{ padding: "0 16px 16px", flex: 1, overflow: "auto" }}>
        {/* Step 1: Company */}
        {step === 0 && (
          <div style={cx.section}>
            <div style={cx.sTitle}>COMPANY INFORMATION</div>
            <Field l="Company Name *" v={data.company} c={u("company")} ph="Acme Corp Pty Ltd" />
            <Field l="Primary Contact *" v={data.contact} c={u("contact")} ph="Jane Smith" />
            <Field l="Email *" v={data.email} c={u("email")} ph="jane@acme.com.au" />
            <Field l="Phone" v={data.phone} c={u("phone")} ph="+61 3 XXXX XXXX" />
          </div>
        )}

        {/* Step 2: Scope */}
        {step === 1 && (
          <div style={cx.section}>
            <div style={cx.sTitle}>ENGAGEMENT SCOPE</div>
            <div style={cx.subLabel}>Select engagement type:</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginBottom: "12px" }}>
              {ENGAGEMENT_TYPES.map(t => (
                <button key={t.id} onClick={() => u("type")(t.id)} style={{
                  ...cx.card,
                  borderColor: data.type === t.id ? "#dc2626" : "#1e293b",
                  background: data.type === t.id ? "#dc262611" : "#0f1319",
                  textAlign: "left", cursor: "pointer",
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: "11px", fontWeight: 700, color: data.type === t.id ? "#dc2626" : "#e2e8f0" }}>{t.label}</span>
                    <span style={{ fontSize: "9px", color: "#10b981" }}>{t.price}</span>
                  </div>
                  <div style={{ fontSize: "9px", color: "#64748b", marginTop: "2px" }}>{t.desc} — {t.days} days typical</div>
                </button>
              ))}
            </div>
            <Area l="In-Scope Targets *" v={data.targets} c={u("targets")} ph={"*.acme.com.au\n203.0.113.0/24\nhttps://app.acme.com.au"} r={3} />
            <Area l="Excluded Targets" v={data.excludes} c={u("excludes")} ph={"mail.acme.com.au\nproduction-db.acme.com.au"} r={2} />
            {(data.type === "webapp" || data.type === "external") && (
              <Area l="Web Applications (URLs)" v={data.webApps} c={u("webApps")} ph={"https://app.acme.com.au\nhttps://api.acme.com.au"} r={2} />
            )}
          </div>
        )}

        {/* Step 3: Details */}
        {step === 2 && (
          <div style={cx.section}>
            <div style={cx.sTitle}>ENGAGEMENT DETAILS</div>
            <div style={cx.subLabel}>Methodology:</div>
            <div style={{ display: "flex", gap: "4px", flexWrap: "wrap", marginBottom: "10px" }}>
              {METHODOLOGIES.map(m => (
                <button key={m.id} onClick={() => u("methodology")(m.id)} style={{
                  ...cx.chip,
                  background: data.methodology === m.id ? "#3b82f6" : "#1e293b",
                  borderColor: data.methodology === m.id ? "#3b82f6" : "#334155",
                }}>{m.label}</button>
              ))}
            </div>

            <div style={cx.subLabel}>Testing Window:</div>
            <div style={{ display: "flex", gap: "4px", marginBottom: "10px" }}>
              {[
                { id: "business_hours", label: "Business Hours" },
                { id: "after_hours", label: "After Hours" },
                { id: "24_7", label: "24/7" },
              ].map(w => (
                <button key={w.id} onClick={() => u("timeWindow")(w.id)} style={{
                  ...cx.chip, flex: 1,
                  background: data.timeWindow === w.id ? "#3b82f6" : "#1e293b",
                  borderColor: data.timeWindow === w.id ? "#3b82f6" : "#334155",
                }}>{w.label}</button>
              ))}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px" }}>
              <Field l="Preferred Start Date" v={data.startDate} c={u("startDate")} ph="2026-04-14" />
              <Field l="Duration (days)" v={data.duration} c={u("duration")} ph={selectedType?.days || "5"} />
            </div>

            <Area l="Testing Objectives" v={data.objectives} c={u("objectives")} ph="Identify vulnerabilities, test incident response, validate patching..." r={2} />
            <Area l="Compliance Requirements" v={data.compliance} c={u("compliance")} ph="PCI DSS, ISO 27001, Essential Eight..." r={2} />
            <Field l="Previous Pentest Date" v={data.previousTests} c={u("previousTests")} ph="Never / 2025-06 / Annual" />

            <div style={cx.subLabel}>Special Permissions:</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              {[
                { key: "socialEngineering", label: "Social engineering / phishing permitted" },
                { key: "dosPermitted", label: "Denial-of-service / stress testing permitted" },
                { key: "physicalAccess", label: "Physical access testing permitted" },
              ].map(p => (
                <label key={p.key} style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "10px", color: "#94a3b8", cursor: "pointer" }}>
                  <input type="checkbox" checked={data[p.key]} onChange={e => u(p.key)(e.target.checked)}
                    style={{ accentColor: "#dc2626" }} />
                  {p.label}
                </label>
              ))}
            </div>

            <Area l="Additional Notes" v={data.notes} c={u("notes")} ph="Any other requirements, constraints, or context..." r={2} />
          </div>
        )}

        {/* Step 4: Review */}
        {step === 3 && (
          <div style={cx.section}>
            <div style={cx.sTitle}>REVIEW & EXPORT</div>
            <div style={{ ...cx.card, marginBottom: "8px" }}>
              <Row l="Company" v={data.company} />
              <Row l="Contact" v={`${data.contact} — ${data.email}`} />
              <Row l="Type" v={selectedType?.label || data.type} />
              <Row l="Methodology" v={METHODOLOGIES.find(m => m.id === data.methodology)?.label} />
              <Row l="Window" v={data.timeWindow.replace(/_/g, " ")} />
              <Row l="Start" v={data.startDate || "TBD"} />
              <Row l="Duration" v={data.duration ? `${data.duration} days` : "TBD"} />
              {selectedType && <Row l="Est. Price" v={selectedType.price} color="#10b981" />}
            </div>
            <div style={{ ...cx.card, marginBottom: "8px" }}>
              <div style={{ fontSize: "9px", fontWeight: 700, color: "#64748b", marginBottom: "4px" }}>IN-SCOPE</div>
              <div style={{ fontSize: "10px", color: "#e2e8f0", whiteSpace: "pre-wrap" }}>{data.targets || "—"}</div>
            </div>
            {data.excludes && (
              <div style={{ ...cx.card, marginBottom: "8px", borderLeftColor: "#dc2626", borderLeftWidth: "2px" }}>
                <div style={{ fontSize: "9px", fontWeight: 700, color: "#dc2626", marginBottom: "4px" }}>EXCLUDED</div>
                <div style={{ fontSize: "10px", color: "#e2e8f0", whiteSpace: "pre-wrap" }}>{data.excludes}</div>
              </div>
            )}
            <div style={{ ...cx.card, marginBottom: "8px" }}>
              <div style={{ fontSize: "9px", fontWeight: 700, color: "#64748b", marginBottom: "4px" }}>RULES OF ENGAGEMENT</div>
              <div style={{ fontSize: "10px", color: "#94a3b8" }}>
                {!data.dosPermitted && "• No DoS testing\n"}
                {!data.socialEngineering && "• No social engineering\n"}
                {!data.physicalAccess && "• No physical access testing\n"}
                • Stop if production impact detected{"\n"}
                • Report critical findings within 24hrs
              </div>
            </div>
            <button onClick={exportJSON} style={{
              ...cx.primaryBtn, width: "100%",
              background: exported ? "#16a34a" : "linear-gradient(135deg, #dc2626, #991b1b)",
            }}>
              {exported ? "✓ COPIED TO CLIPBOARD" : "📋 EXPORT SCOPE CONFIG (JSON)"}
            </button>
            <div style={{ fontSize: "8px", color: "#475569", textAlign: "center", marginTop: "6px" }}>
              Paste the JSON into Claude to initialize scope-guard
            </div>
          </div>
        )}
      </div>

      {/* Nav */}
      <div style={{ display: "flex", gap: "6px", padding: "12px 16px", borderTop: "1px solid #1e293b" }}>
        {step > 0 && <button onClick={prev} style={cx.secBtn}>← BACK</button>}
        <div style={{ flex: 1 }} />
        {step < STEPS.length - 1 && (
          <button onClick={next} style={{ ...cx.primaryBtn, opacity: step === 0 && !data.company ? 0.4 : 1 }}>
            NEXT →
          </button>
        )}
      </div>
    </div>
  );
}

function Field({ l, v, c, ph }) {
  return (
    <div style={{ marginBottom: "8px" }}>
      <div style={cx.label}>{l}</div>
      <input value={v} onChange={e => c(e.target.value)} placeholder={ph} style={cx.input} />
    </div>
  );
}

function Area({ l, v, c, ph, r = 3 }) {
  return (
    <div style={{ marginBottom: "8px" }}>
      <div style={cx.label}>{l}</div>
      <textarea value={v} onChange={e => c(e.target.value)} placeholder={ph} rows={r}
        style={{ ...cx.input, resize: "vertical", minHeight: `${r * 20}px` }} />
    </div>
  );
}

function Row({ l, v, color }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", padding: "3px 0", fontSize: "10px" }}>
      <span style={{ color: "#64748b" }}>{l}</span>
      <span style={{ color: color || "#e2e8f0", fontWeight: 600 }}>{v}</span>
    </div>
  );
}

const cx = {
  root: { fontFamily: "'IBM Plex Mono', monospace", background: "#080b11", color: "#cbd5e1", height: "100%", display: "flex", flexDirection: "column" },
  header: { padding: "12px 16px", borderBottom: "1px solid #1e293b", background: "linear-gradient(180deg, #0f1319, #080b11)" },
  section: { display: "flex", flexDirection: "column" },
  sTitle: { fontSize: "10px", fontWeight: 800, letterSpacing: "0.1em", color: "#dc2626", marginBottom: "12px" },
  subLabel: { fontSize: "9px", fontWeight: 700, color: "#64748b", letterSpacing: "0.08em", marginBottom: "6px" },
  label: { fontSize: "8px", fontWeight: 700, letterSpacing: "0.1em", color: "#475569", marginBottom: "3px" },
  input: { width: "100%", padding: "7px 9px", borderRadius: "5px", border: "1px solid #334155", background: "#0f172a", color: "#e2e8f0", fontSize: "11px", fontFamily: "inherit", outline: "none", boxSizing: "border-box" },
  card: { background: "#0f1319", borderRadius: "6px", padding: "10px 12px", border: "1px solid #1e293b" },
  chip: { padding: "5px 10px", borderRadius: "4px", border: "1px solid", color: "#e2e8f0", fontSize: "9px", fontWeight: 600, fontFamily: "inherit", cursor: "pointer" },
  primaryBtn: { padding: "10px 20px", borderRadius: "6px", border: "none", background: "linear-gradient(135deg, #dc2626, #991b1b)", color: "#fff", fontSize: "10px", fontWeight: 700, letterSpacing: "0.06em", cursor: "pointer", fontFamily: "inherit" },
  secBtn: { padding: "10px 16px", borderRadius: "6px", border: "1px solid #334155", background: "#1e293b", color: "#94a3b8", fontSize: "10px", fontWeight: 600, cursor: "pointer", fontFamily: "inherit" },
};
