import { useState, useEffect, useCallback, useMemo } from "react";

const SEV = { critical: "#dc2626", high: "#f97316", medium: "#eab308", low: "#3b82f6", info: "#6b7280" };
const STORAGE_KEY = "kali-vuln-kb";

export default function VulnKnowledgeBase() {
  const [entries, setEntries] = useState([]);
  const [search, setSearch] = useState("");
  const [filterSev, setFilterSev] = useState(null);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ cve: "", title: "", severity: "high", product: "", version: "", description: "", remediation: "", tags: "", exploitAvail: false, kev: false, epss: "", engagementId: "" });
  const [sortBy, setSortBy] = useState("date");

  useEffect(() => {
    (async () => {
      try { const r = await window.storage.get(STORAGE_KEY); if (r?.value) setEntries(JSON.parse(r.value)); } catch {}
    })();
  }, []);

  const save = useCallback(async (data) => {
    try { await window.storage.set(STORAGE_KEY, JSON.stringify(data)); } catch {}
  }, []);

  const addEntry = useCallback(() => {
    if (!form.title) return;
    const entry = { ...form, id: `KB-${Date.now()}`, addedAt: new Date().toISOString(), tags: form.tags.split(",").map(t => t.trim()).filter(Boolean) };
    const updated = [entry, ...entries];
    setEntries(updated);
    save(updated);
    setForm({ cve: "", title: "", severity: "high", product: "", version: "", description: "", remediation: "", tags: "", exploitAvail: false, kev: false, epss: "", engagementId: "" });
    setShowAdd(false);
  }, [form, entries, save]);

  const deleteEntry = useCallback((id) => {
    const updated = entries.filter(e => e.id !== id);
    setEntries(updated);
    save(updated);
  }, [entries, save]);

  const filtered = useMemo(() => {
    let result = entries;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(e => e.title.toLowerCase().includes(q) || e.cve?.toLowerCase().includes(q) || e.product?.toLowerCase().includes(q) || e.tags?.some(t => t.toLowerCase().includes(q)));
    }
    if (filterSev) result = result.filter(e => e.severity === filterSev);
    if (sortBy === "severity") {
      const order = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
      result = [...result].sort((a, b) => (order[a.severity] || 5) - (order[b.severity] || 5));
    }
    return result;
  }, [entries, search, filterSev, sortBy]);

  const stats = useMemo(() => {
    const s = {};
    entries.forEach(e => { s[e.severity] = (s[e.severity] || 0) + 1; });
    return s;
  }, [entries]);

  const u = (f) => (v) => setForm(p => ({ ...p, [f]: v }));

  return (
    <div style={cx.root}>
      <div style={cx.header}>
        <div>
          <div style={{ fontSize: "13px", fontWeight: 800, color: "#f1f5f9", letterSpacing: "0.04em" }}>🧠 VULNERABILITY KB</div>
          <div style={{ fontSize: "9px", color: "#64748b" }}>{entries.length} entries — persists across sessions</div>
        </div>
        <button onClick={() => setShowAdd(!showAdd)} style={{ ...cx.btn, background: showAdd ? "#dc262622" : "#1e293b", borderColor: showAdd ? "#dc2626" : "#334155", color: showAdd ? "#dc2626" : "#94a3b8" }}>
          {showAdd ? "✕" : "+ ADD"}
        </button>
      </div>

      {/* Stats bar */}
      {entries.length > 0 && (
        <div style={{ display: "flex", gap: "6px", padding: "8px 12px", borderBottom: "1px solid #1e293b" }}>
          {["critical", "high", "medium", "low", "info"].map(sv => {
            const n = stats[sv] || 0;
            if (!n) return null;
            return (
              <button key={sv} onClick={() => setFilterSev(filterSev === sv ? null : sv)} style={{
                ...cx.btn, fontSize: "8px",
                background: filterSev === sv ? SEV[sv] + "22" : "transparent",
                borderColor: filterSev === sv ? SEV[sv] : "#1e293b",
                color: SEV[sv],
              }}>
                {n} {sv.slice(0, 4)}
              </button>
            );
          })}
          <div style={{ flex: 1 }} />
          <button onClick={() => setSortBy(s => s === "date" ? "severity" : "date")} style={{ ...cx.btn, fontSize: "8px" }}>
            ↕ {sortBy === "date" ? "Date" : "Severity"}
          </button>
        </div>
      )}

      {/* Search */}
      <div style={{ padding: "8px 12px" }}>
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search CVE, title, product, tag..."
          style={{ ...cx.input, background: "#0f172a" }} />
      </div>

      {/* Add form */}
      {showAdd && (
        <div style={{ padding: "0 12px 12px", borderBottom: "1px solid #1e293b" }}>
          <div style={{ display: "flex", gap: "4px", marginBottom: "6px" }}>
            {["critical", "high", "medium", "low", "info"].map(sv => (
              <button key={sv} onClick={() => u("severity")(sv)} style={{
                ...cx.btn, flex: 1, fontSize: "8px",
                background: form.severity === sv ? SEV[sv] : "#1e293b",
                borderColor: form.severity === sv ? SEV[sv] : "#334155",
                color: "#fff",
              }}>{sv.slice(0, 4).toUpperCase()}</button>
            ))}
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px", marginBottom: "4px" }}>
            <In l="CVE" v={form.cve} c={u("cve")} ph="CVE-2024-XXXXX" />
            <In l="Product" v={form.product} c={u("product")} ph="WordPress" />
          </div>
          <In l="Title *" v={form.title} c={u("title")} ph="RCE via file upload" />
          <div style={{ height: "4px" }} />
          <In l="Tags (comma-sep)" v={form.tags} c={u("tags")} ph="rce, wordpress, plugin, file-upload" />
          <div style={{ height: "4px" }} />
          <div style={{ display: "flex", gap: "8px", marginTop: "4px", marginBottom: "6px" }}>
            <label style={cx.check}><input type="checkbox" checked={form.exploitAvail} onChange={e => u("exploitAvail")(e.target.checked)} style={{ accentColor: "#dc2626" }} /> Exploit available</label>
            <label style={cx.check}><input type="checkbox" checked={form.kev} onChange={e => u("kev")(e.target.checked)} style={{ accentColor: "#f59e0b" }} /> On CISA KEV</label>
            <In l="EPSS" v={form.epss} c={u("epss")} ph="0.87" />
          </div>
          <button onClick={addEntry} disabled={!form.title} style={{ ...cx.primaryBtn, width: "100%", opacity: form.title ? 1 : 0.4 }}>
            ADD TO KNOWLEDGE BASE
          </button>
        </div>
      )}

      {/* Entries */}
      <div style={{ flex: 1, overflow: "auto", padding: "8px 12px" }}>
        {filtered.length === 0 && <div style={{ textAlign: "center", color: "#334155", fontSize: "11px", padding: "24px" }}>{entries.length === 0 ? "Knowledge base empty — add your first finding" : "No matches"}</div>}
        <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
          {filtered.map(e => (
            <div key={e.id} style={{ ...cx.card, borderLeft: `3px solid ${SEV[e.severity]}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                    <span style={{ fontSize: "8px", fontWeight: 800, color: SEV[e.severity], letterSpacing: "0.06em" }}>{e.severity.toUpperCase()}</span>
                    {e.cve && <span style={{ fontSize: "9px", color: "#64748b" }}>{e.cve}</span>}
                    {e.exploitAvail && <span style={{ fontSize: "7px", background: "#dc262622", color: "#dc2626", padding: "1px 4px", borderRadius: "2px" }}>EXPLOIT</span>}
                    {e.kev && <span style={{ fontSize: "7px", background: "#f59e0b22", color: "#f59e0b", padding: "1px 4px", borderRadius: "2px" }}>KEV</span>}
                  </div>
                  <div style={{ fontSize: "11px", fontWeight: 600, color: "#e2e8f0", marginTop: "3px" }}>{e.title}</div>
                  {e.product && <div style={{ fontSize: "9px", color: "#64748b", marginTop: "2px" }}>{e.product}{e.version ? ` ${e.version}` : ""}</div>}
                  {e.tags?.length > 0 && (
                    <div style={{ display: "flex", gap: "3px", marginTop: "4px", flexWrap: "wrap" }}>
                      {e.tags.map((t, i) => <span key={i} style={{ fontSize: "7px", background: "#1e293b", color: "#94a3b8", padding: "1px 5px", borderRadius: "3px" }}>{t}</span>)}
                    </div>
                  )}
                </div>
                <button onClick={() => deleteEntry(e.id)} style={{ background: "none", border: "none", color: "#33415566", cursor: "pointer", fontSize: "12px", padding: "0 0 0 8px" }}>×</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div style={{ padding: "6px 12px", borderTop: "1px solid #1e293b", display: "flex", justifyContent: "space-between", fontSize: "8px", color: "#334155" }}>
        <span>Showing {filtered.length} of {entries.length}</span>
        <button onClick={async () => { if (confirm("Reset KB?")) { setEntries([]); try { await window.storage.delete(STORAGE_KEY); } catch {} } }} style={{ background: "none", border: "none", color: "#dc262644", cursor: "pointer", fontSize: "8px", fontFamily: "inherit" }}>Reset</button>
      </div>
    </div>
  );
}

function In({ l, v, c, ph }) {
  return (
    <div>
      {l && <div style={{ fontSize: "7px", fontWeight: 700, color: "#475569", letterSpacing: "0.08em", marginBottom: "2px" }}>{l}</div>}
      <input value={v} onChange={e => c(e.target.value)} placeholder={ph} style={cx.input} />
    </div>
  );
}

const cx = {
  root: { fontFamily: "'IBM Plex Mono', monospace", background: "#080b11", color: "#cbd5e1", height: "100%", display: "flex", flexDirection: "column" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 12px", borderBottom: "1px solid #1e293b", background: "linear-gradient(180deg, #0f1319, #080b11)" },
  input: { width: "100%", padding: "6px 8px", borderRadius: "4px", border: "1px solid #334155", background: "#0f1319", color: "#e2e8f0", fontSize: "10px", fontFamily: "inherit", outline: "none", boxSizing: "border-box" },
  card: { background: "#0f1319", borderRadius: "5px", padding: "8px 10px", border: "1px solid #1e293b" },
  btn: { padding: "4px 8px", borderRadius: "4px", border: "1px solid #334155", background: "#1e293b", color: "#94a3b8", fontSize: "9px", fontWeight: 600, fontFamily: "inherit", cursor: "pointer" },
  primaryBtn: { padding: "8px", borderRadius: "5px", border: "none", background: "linear-gradient(135deg, #dc2626, #991b1b)", color: "#fff", fontSize: "10px", fontWeight: 700, cursor: "pointer", fontFamily: "inherit" },
  check: { display: "flex", alignItems: "center", gap: "4px", fontSize: "9px", color: "#94a3b8", cursor: "pointer" },
};
