import { useState, useEffect, useCallback, useMemo } from "react";

const PHASES = [
  { id: "scope", label: "SCOPE", icon: "🔒", color: "#6366f1" },
  { id: "recon", label: "RECON", icon: "🔍", color: "#3b82f6" },
  { id: "vuln", label: "VULN", icon: "⚡", color: "#f59e0b" },
  { id: "exploit", label: "EXPLOIT", icon: "💥", color: "#ef4444" },
  { id: "post", label: "POST", icon: "🎯", color: "#8b5cf6" },
  { id: "report", label: "REPORT", icon: "📋", color: "#10b981" },
];

const SEV = { critical: "#dc2626", high: "#f97316", medium: "#eab308", low: "#3b82f6", info: "#6b7280" };

const INIT = { engagement: null, phase: null, findings: [], hosts: [], timeline: [], hexStatus: "unknown" };

export default function KaliDashboard() {
  const [s, setS] = useState(INIT);
  const [view, setView] = useState("dashboard");
  const [form, setForm] = useState({ id: `ENG-${new Date().toISOString().slice(0,10).replace(/-/g,"")}`, client: "", target: "", type: "external", scope: "", exclude: "", auth: "" });
  const [addForm, setAddForm] = useState({ severity: "high", title: "", asset: "", cve: "", tool: "" });
  const [showAdd, setShowAdd] = useState(false);

  useEffect(() => { (async () => { try { const r = await window.storage.get("kali-dash"); if (r?.value) setS(JSON.parse(r.value)); } catch {} })(); }, []);
  useEffect(() => { if (s.engagement) { (async () => { try { await window.storage.set("kali-dash", JSON.stringify(s)); } catch {} })(); } }, [s]);

  const addTimeline = useCallback((e) => setS(p => ({ ...p, timeline: [{ id: Date.now(), ts: new Date().toISOString(), ...e }, ...p.timeline].slice(0, 150) })), []);

  const addFinding = useCallback(() => {
    if (!addForm.title) return;
    const id = `VULN-${String(s.findings.length + 1).padStart(3, "0")}`;
    setS(p => ({ ...p, findings: [{ id, ...addForm }, ...p.findings] }));
    addTimeline({ phase: s.phase, action: "finding", detail: `${addForm.severity.toUpperCase()}: ${addForm.title}` });
    setAddForm({ severity: "high", title: "", asset: "", cve: "", tool: "" });
    setShowAdd(false);
  }, [addForm, s.findings.length, s.phase, addTimeline]);

  const addHost = useCallback((hostname, ip, access) => {
    setS(p => ({ ...p, hosts: [...p.hosts, { hostname, ip, access, ts: new Date().toISOString() }] }));
    addTimeline({ phase: "post", action: "host_compromised", detail: `${hostname} (${ip}) — ${access}` });
  }, [addTimeline]);

  const setPhase = useCallback((id) => {
    setS(p => ({ ...p, phase: id }));
    addTimeline({ phase: id, action: "phase_start", detail: `Entered ${id} phase` });
  }, [addTimeline]);

  const init = useCallback(() => {
    if (!form.target) return;
    setS({ ...INIT, engagement: { ...form, startedAt: new Date().toISOString() }, phase: "scope",
      timeline: [{ id: Date.now(), ts: new Date().toISOString(), phase: "scope", action: "init", detail: `${form.id} — target: ${form.target}` }] });
    setView("dashboard");
  }, [form]);

  const reset = useCallback(async () => { setS(INIT); try { await window.storage.delete("kali-dash"); } catch {} }, []);

  const sevCounts = useMemo(() => s.findings.reduce((a, f) => { a[f.severity] = (a[f.severity] || 0) + 1; return a; }, {}), [s.findings]);
  const totalFindings = s.findings.length;

  if (!s.engagement && view !== "setup") {
    return (
      <div style={cx.root}>
        <Hdr />
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", flex: 1, padding: "40px 20px", gap: "16px" }}>
          <div style={{ fontSize: "56px", filter: "drop-shadow(0 0 20px #dc262644)" }}>💀</div>
          <div style={{ fontSize: "16px", fontWeight: 800, color: "#f1f5f9", letterSpacing: "0.04em" }}>KALI AGENT</div>
          <div style={{ fontSize: "11px", color: "#475569" }}>No active engagement</div>
          <button onClick={() => setView("setup")} style={cx.primaryBtn}>🔥 NEW ENGAGEMENT</button>
        </div>
      </div>
    );
  }

  if (view === "setup") {
    return (
      <div style={cx.root}>
        <Hdr />
        <div style={{ padding: "16px", display: "flex", flexDirection: "column", gap: "10px" }}>
          <div style={{ fontSize: "10px", fontWeight: 800, letterSpacing: "0.12em", color: "#dc2626" }}>NEW ENGAGEMENT</div>
          <In l="ID" v={form.id} c={v => setForm(p => ({ ...p, id: v }))} />
          <In l="CLIENT" v={form.client} c={v => setForm(p => ({ ...p, client: v }))} ph="Company" />
          <In l="TARGET *" v={form.target} c={v => setForm(p => ({ ...p, target: v }))} ph="example.com" />
          <div>
            <div style={cx.label}>TYPE</div>
            <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
              {["external", "webapp", "internal", "redteam", "ctf"].map(t => (
                <button key={t} onClick={() => setForm(p => ({ ...p, type: t }))}
                  style={{ ...cx.chip, background: form.type === t ? "#dc2626" : "#1e293b", borderColor: form.type === t ? "#dc2626" : "#334155" }}>{t}</button>
              ))}
            </div>
          </div>
          <Ta l="IN-SCOPE" v={form.scope} c={v => setForm(p => ({ ...p, scope: v }))} ph={"*.example.com\n10.0.0.0/24"} r={2} />
          <Ta l="EXCLUDED" v={form.exclude} c={v => setForm(p => ({ ...p, exclude: v }))} ph="mail.example.com" r={2} />
          {form.type !== "ctf" && <Ta l="AUTHORIZATION *" v={form.auth} c={v => setForm(p => ({ ...p, auth: v }))} ph="Written auth ref..." r={2} />}
          {form.type === "ctf" && <div style={{ background: "#16a34a15", border: "1px solid #16a34a33", borderRadius: "6px", padding: "8px 12px", fontSize: "10px", color: "#4ade80" }}>🏁 CTF Mode — relaxed scope</div>}
          <div style={{ display: "flex", gap: "6px", marginTop: "4px" }}>
            <button onClick={init} disabled={!form.target} style={{ ...cx.primaryBtn, flex: 1, opacity: form.target ? 1 : 0.4 }}>LAUNCH</button>
            <button onClick={() => setView("dashboard")} style={cx.secBtn}>✕</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={cx.root}>
      <Hdr eid={s.engagement.id} target={s.engagement.target} />

      {/* Phase pipeline */}
      <div style={{ display: "flex", gap: "3px", padding: "10px 12px" }}>
        {PHASES.map((p, i) => {
          const active = s.phase === p.id;
          const past = PHASES.findIndex(x => x.id === s.phase) > i;
          return (
            <button key={p.id} onClick={() => setPhase(p.id)} style={{
              flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: "1px",
              padding: "6px 2px", borderRadius: "6px", cursor: "pointer", fontFamily: "inherit",
              border: `1.5px solid ${active ? p.color : past ? p.color + "44" : "#1e293b"}`,
              background: active ? p.color + "18" : "transparent",
              color: active ? p.color : past ? p.color + "88" : "#475569",
              boxShadow: active ? `0 0 10px ${p.color}22` : "none",
              transition: "all 0.15s",
            }}>
              <span style={{ fontSize: "13px" }}>{p.icon}</span>
              <span style={{ fontSize: "8px", fontWeight: 700, letterSpacing: "0.06em" }}>{p.label}</span>
            </button>
          );
        })}
      </div>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: "4px", padding: "0 12px 8px" }}>
        <Stat l="FINDINGS" v={totalFindings} c="#f59e0b" />
        <Stat l="CRITICAL" v={sevCounts.critical || 0} c="#dc2626" />
        <Stat l="HIGH" v={sevCounts.high || 0} c="#f97316" />
        <Stat l="HOSTS" v={s.hosts.length} c="#8b5cf6" />
      </div>

      {/* Severity bar */}
      {totalFindings > 0 && (
        <div style={{ padding: "0 12px 8px" }}>
          <div style={{ display: "flex", borderRadius: "4px", overflow: "hidden", height: "6px" }}>
            {["critical", "high", "medium", "low", "info"].map(sv => {
              const n = sevCounts[sv] || 0;
              if (!n) return null;
              return <div key={sv} style={{ width: `${(n / totalFindings) * 100}%`, background: SEV[sv] }} />;
            })}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: "flex", borderBottom: "1px solid #1e293b", padding: "0 12px" }}>
        {["findings", "timeline", "hosts"].map(t => (
          <button key={t} onClick={() => setView(t)} style={{
            padding: "6px 10px", fontSize: "9px", fontWeight: 700, letterSpacing: "0.08em",
            background: "none", border: "none", fontFamily: "inherit", cursor: "pointer",
            borderBottom: `2px solid ${view === t ? "#dc2626" : "transparent"}`,
            color: view === t ? "#e2e8f0" : "#475569",
          }}>{t.toUpperCase()}</button>
        ))}
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: "auto", padding: "10px 12px" }}>
        {view === "findings" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            {!s.findings.length && <div style={cx.empty}>No findings — run vuln-analysis</div>}
            {s.findings.map(f => (
              <div key={f.id} style={{ ...cx.card, borderLeft: `3px solid ${SEV[f.severity]}` }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontSize: "10px", fontWeight: 700, color: "#e2e8f0" }}>{f.id}</span>
                  <span style={{ fontSize: "8px", fontWeight: 800, color: SEV[f.severity], letterSpacing: "0.06em" }}>{f.severity.toUpperCase()}</span>
                </div>
                <div style={{ fontSize: "11px", color: "#cbd5e1", marginTop: "3px" }}>{f.title}</div>
                <div style={{ display: "flex", gap: "8px", marginTop: "4px", fontSize: "9px", color: "#475569" }}>
                  {f.cve && <span>{f.cve}</span>}
                  {f.asset && <span>{f.asset}</span>}
                  {f.tool && <span>via {f.tool}</span>}
                </div>
              </div>
            ))}
          </div>
        )}
        {view === "timeline" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
            {!s.timeline.length && <div style={cx.empty}>Timeline empty</div>}
            {s.timeline.map(e => {
              const ph = PHASES.find(p => p.id === e.phase);
              return (
                <div key={e.id} style={{ display: "flex", gap: "6px", fontSize: "10px", padding: "4px 0", borderBottom: "1px solid #1e293b0a" }}>
                  <span style={{ width: "50px", color: "#334155", fontSize: "9px", flexShrink: 0 }}>
                    {new Date(e.ts).toLocaleTimeString("en-AU", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                  </span>
                  <span style={{ width: "14px", fontSize: "11px", flexShrink: 0 }}>{ph?.icon || "⚙️"}</span>
                  <span style={{ color: "#94a3b8", flex: 1 }}>{e.detail}</span>
                </div>
              );
            })}
          </div>
        )}
        {view === "hosts" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            {!s.hosts.length && <div style={cx.empty}>No hosts compromised</div>}
            {s.hosts.map((h, i) => (
              <div key={i} style={cx.card}>
                <div style={{ fontSize: "11px", fontWeight: 700, color: "#e2e8f0" }}>{h.hostname || h.ip}</div>
                <div style={{ fontSize: "10px", color: "#475569", marginTop: "2px" }}>{h.access}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add finding modal */}
      {showAdd && (
        <div style={{ position: "absolute", bottom: 50, left: 12, right: 12, background: "#0f1319", border: "1px solid #334155", borderRadius: "8px", padding: "12px", zIndex: 10, boxShadow: "0 -4px 20px #00000066" }}>
          <div style={{ fontSize: "9px", fontWeight: 700, color: "#dc2626", letterSpacing: "0.1em", marginBottom: "8px" }}>ADD FINDING</div>
          <div style={{ display: "flex", gap: "4px", marginBottom: "6px" }}>
            {["critical", "high", "medium", "low", "info"].map(sv => (
              <button key={sv} onClick={() => setAddForm(p => ({ ...p, severity: sv }))}
                style={{ ...cx.chip, fontSize: "8px", flex: 1, background: addForm.severity === sv ? SEV[sv] : "#1e293b", borderColor: addForm.severity === sv ? SEV[sv] : "#334155", color: "#fff" }}>
                {sv.slice(0, 4).toUpperCase()}
              </button>
            ))}
          </div>
          <In l="TITLE *" v={addForm.title} c={v => setAddForm(p => ({ ...p, title: v }))} ph="SQL Injection in /search" />
          <div style={{ height: "4px" }} />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px" }}>
            <In l="ASSET" v={addForm.asset} c={v => setAddForm(p => ({ ...p, asset: v }))} ph="app.example.com" />
            <In l="CVE" v={addForm.cve} c={v => setAddForm(p => ({ ...p, cve: v }))} ph="CVE-2024-XXXXX" />
          </div>
          <div style={{ height: "4px" }} />
          <In l="TOOL" v={addForm.tool} c={v => setAddForm(p => ({ ...p, tool: v }))} ph="sqlmap" />
          <div style={{ display: "flex", gap: "4px", marginTop: "8px" }}>
            <button onClick={addFinding} disabled={!addForm.title} style={{ ...cx.primaryBtn, flex: 1, padding: "8px", fontSize: "10px", opacity: addForm.title ? 1 : 0.4 }}>ADD</button>
            <button onClick={() => setShowAdd(false)} style={{ ...cx.secBtn, padding: "8px", fontSize: "10px" }}>✕</button>
          </div>
        </div>
      )}

      {/* Bottom bar */}
      <div style={{ display: "flex", gap: "4px", padding: "8px 12px", borderTop: "1px solid #1e293b" }}>
        <button onClick={() => setShowAdd(!showAdd)} style={{ ...cx.actBtn, flex: 2, background: showAdd ? "#dc262622" : "#0f1319", borderColor: showAdd ? "#dc2626" : "#334155" }}>
          {showAdd ? "✕ Cancel" : "+ Finding"}
        </button>
        <button onClick={() => {
          const host = prompt("Hostname:");
          const ip = prompt("IP:");
          const access = prompt("Access level:");
          if (host && ip) addHost(host, ip, access || "unknown");
        }} style={{ ...cx.actBtn, flex: 1 }}>+ Host</button>
        <button onClick={reset} style={{ ...cx.actBtn, flex: 0, borderColor: "#dc262633", color: "#dc2626" }}>🗑</button>
      </div>
    </div>
  );
}

function Hdr({ eid, target }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 12px", borderBottom: "1px solid #1e293b", background: "linear-gradient(180deg, #0f1319, #080b11)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <span style={{ fontSize: "18px", filter: "drop-shadow(0 0 6px #dc262644)" }}>💀</span>
        <div>
          <div style={{ fontWeight: 800, fontSize: "12px", letterSpacing: "0.05em", color: "#f1f5f9" }}>KALI AGENT</div>
          {eid && <div style={{ fontSize: "8px", color: "#64748b", letterSpacing: "0.08em" }}>{eid}{target ? ` → ${target}` : ""}</div>}
        </div>
      </div>
    </div>
  );
}

function Stat({ l, v, c }) {
  return (
    <div style={{ background: "#0f1319", borderRadius: "5px", padding: "6px 8px", border: "1px solid #1e293b" }}>
      <div style={{ fontSize: "8px", color: "#475569", letterSpacing: "0.08em", fontWeight: 600 }}>{l}</div>
      <div style={{ fontSize: "16px", fontWeight: 800, color: c, marginTop: "1px" }}>{v}</div>
    </div>
  );
}

function In({ l, v, c, ph }) {
  return (
    <div>
      <div style={cx.label}>{l}</div>
      <input value={v} onChange={e => c(e.target.value)} placeholder={ph || ""} style={cx.input} />
    </div>
  );
}

function Ta({ l, v, c, ph, r = 3 }) {
  return (
    <div>
      <div style={cx.label}>{l}</div>
      <textarea value={v} onChange={e => c(e.target.value)} placeholder={ph} rows={r} style={{ ...cx.input, resize: "vertical", minHeight: `${r * 20}px` }} />
    </div>
  );
}

const cx = {
  root: { fontFamily: "'IBM Plex Mono', 'JetBrains Mono', monospace", background: "#080b11", color: "#cbd5e1", height: "100%", display: "flex", flexDirection: "column", position: "relative", overflow: "hidden" },
  label: { fontSize: "8px", fontWeight: 700, letterSpacing: "0.1em", color: "#475569", marginBottom: "3px" },
  input: { width: "100%", padding: "7px 9px", borderRadius: "5px", border: "1px solid #334155", background: "#0f172a", color: "#e2e8f0", fontSize: "11px", fontFamily: "inherit", outline: "none", boxSizing: "border-box" },
  card: { background: "#0f1319", borderRadius: "5px", padding: "8px 10px", border: "1px solid #1e293b" },
  chip: { padding: "4px 8px", borderRadius: "4px", border: "1px solid", color: "#e2e8f0", fontSize: "9px", fontWeight: 600, fontFamily: "inherit", cursor: "pointer" },
  empty: { textAlign: "center", color: "#334155", fontSize: "11px", padding: "24px 0" },
  primaryBtn: { padding: "10px 20px", borderRadius: "6px", border: "none", background: "linear-gradient(135deg, #dc2626, #991b1b)", color: "#fff", fontSize: "11px", fontWeight: 700, letterSpacing: "0.08em", cursor: "pointer", fontFamily: "inherit" },
  secBtn: { padding: "10px 14px", borderRadius: "6px", border: "1px solid #334155", background: "#1e293b", color: "#94a3b8", fontSize: "11px", fontWeight: 600, cursor: "pointer", fontFamily: "inherit" },
  actBtn: { padding: "7px 8px", borderRadius: "5px", border: "1px solid #334155", background: "#0f1319", color: "#94a3b8", fontSize: "9px", fontWeight: 600, fontFamily: "inherit", cursor: "pointer" },
};
