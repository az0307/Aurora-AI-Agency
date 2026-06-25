import { useState, useEffect, useCallback, useRef } from "react";

const PHASES = [
  { id: "scope", label: "SCOPE", icon: "🔒", color: "#6366f1", skill: "scope-guard" },
  { id: "recon", label: "RECON", icon: "🔍", color: "#3b82f6", skill: "recon-osint" },
  { id: "vuln", label: "VULN", icon: "⚡", color: "#f59e0b", skill: "vuln-analysis" },
  { id: "exploit", label: "EXPLOIT", icon: "💥", color: "#ef4444", skill: "exploit-dev" },
  { id: "post", label: "POST", icon: "🎯", color: "#8b5cf6", skill: "post-exploit" },
  { id: "report", label: "REPORT", icon: "📋", color: "#10b981", skill: "red-team-report" },
];

const SEVERITY_COLORS = {
  critical: "#dc2626",
  high: "#f97316",
  medium: "#eab308",
  low: "#3b82f6",
  info: "#6b7280",
};

const INITIAL_STATE = {
  engagement: null,
  activePhase: null,
  findings: [],
  hosts: [],
  timeline: [],
  stats: { toolCalls: 0, scopeChecks: 0, scopeBlocked: 0 },
  hexstrikeStatus: "unknown",
};

export default function KaliDashboard() {
  const [state, setState] = useState(INITIAL_STATE);
  const [view, setView] = useState("dashboard");
  const [newEngagement, setNewEngagement] = useState({
    id: `ENG-${new Date().toISOString().slice(0, 10).replace(/-/g, "")}`,
    client: "",
    type: "external",
    target: "",
    inScope: "",
    outScope: "",
    authorization: "",
  });
  const timelineRef = useRef(null);

  // Load from persistent storage
  useEffect(() => {
    (async () => {
      try {
        const saved = await window.storage.get("kali-engagement");
        if (saved?.value) {
          setState(JSON.parse(saved.value));
        }
      } catch { /* first run */ }
    })();
  }, []);

  // Save to persistent storage on state change
  useEffect(() => {
    if (state.engagement) {
      (async () => {
        try {
          await window.storage.set("kali-engagement", JSON.stringify(state));
        } catch { /* storage unavailable */ }
      })();
    }
  }, [state]);

  const addTimelineEntry = useCallback((entry) => {
    setState((s) => ({
      ...s,
      timeline: [
        { id: Date.now(), timestamp: new Date().toISOString(), ...entry },
        ...s.timeline,
      ].slice(0, 200),
    }));
  }, []);

  const addFinding = useCallback((finding) => {
    setState((s) => ({
      ...s,
      findings: [
        { id: `VULN-${String(s.findings.length + 1).padStart(3, "0")}`, ...finding },
        ...s.findings,
      ],
    }));
  }, []);

  const setPhase = useCallback((phaseId) => {
    setState((s) => ({ ...s, activePhase: phaseId }));
    addTimelineEntry({ phase: phaseId, action: "phase_started", detail: `Entered ${phaseId} phase` });
  }, [addTimelineEntry]);

  const initEngagement = useCallback(() => {
    if (!newEngagement.target) return;
    setState({
      ...INITIAL_STATE,
      engagement: { ...newEngagement, startedAt: new Date().toISOString() },
      activePhase: "scope",
      timeline: [{
        id: Date.now(),
        timestamp: new Date().toISOString(),
        phase: "scope",
        action: "engagement_init",
        detail: `Engagement ${newEngagement.id} initialized — target: ${newEngagement.target}`,
      }],
    });
    setView("dashboard");
  }, [newEngagement]);

  const resetEngagement = useCallback(async () => {
    setState(INITIAL_STATE);
    try { await window.storage.delete("kali-engagement"); } catch {}
  }, []);

  const severityCounts = state.findings.reduce((acc, f) => {
    acc[f.severity] = (acc[f.severity] || 0) + 1;
    return acc;
  }, {});

  // If no engagement, show setup
  if (!state.engagement && view !== "setup") {
    return (
      <div style={styles.container}>
        <Header hexStatus={state.hexstrikeStatus} />
        <div style={styles.emptyState}>
          <div style={{ fontSize: "48px", marginBottom: "16px" }}>💀</div>
          <div style={{ fontSize: "18px", fontWeight: 700, marginBottom: "8px", color: "#e2e8f0" }}>
            No Active Engagement
          </div>
          <div style={{ fontSize: "13px", color: "#64748b", marginBottom: "24px" }}>
            Initialize an engagement to begin testing
          </div>
          <button onClick={() => setView("setup")} style={styles.primaryBtn}>
            🔥 NEW ENGAGEMENT
          </button>
        </div>
      </div>
    );
  }

  if (view === "setup") {
    return (
      <div style={styles.container}>
        <Header hexStatus={state.hexstrikeStatus} />
        <div style={{ padding: "20px" }}>
          <div style={styles.sectionTitle}>NEW ENGAGEMENT</div>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <Input label="ENGAGEMENT ID" value={newEngagement.id} onChange={(v) => setNewEngagement((s) => ({ ...s, id: v }))} />
            <Input label="CLIENT" value={newEngagement.client} onChange={(v) => setNewEngagement((s) => ({ ...s, client: v }))} placeholder="Company name" />
            <Input label="PRIMARY TARGET *" value={newEngagement.target} onChange={(v) => setNewEngagement((s) => ({ ...s, target: v }))} placeholder="example.com or 10.0.0.0/24" />
            <div>
              <div style={styles.label}>TYPE</div>
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                {["external", "webapp", "internal", "redteam", "ctf"].map((t) => (
                  <button key={t} onClick={() => setNewEngagement((s) => ({ ...s, type: t }))}
                    style={{ ...styles.chip, background: newEngagement.type === t ? "#dc2626" : "#1e293b", borderColor: newEngagement.type === t ? "#dc2626" : "#334155" }}>
                    {t.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
            <TextArea label="IN-SCOPE" value={newEngagement.inScope} onChange={(v) => setNewEngagement((s) => ({ ...s, inScope: v }))} placeholder="*.example.com&#10;10.0.0.0/24" rows={3} />
            <TextArea label="EXCLUDED" value={newEngagement.outScope} onChange={(v) => setNewEngagement((s) => ({ ...s, outScope: v }))} placeholder="mail.example.com&#10;prod-db.example.com" rows={2} />
            {newEngagement.type !== "ctf" && (
              <TextArea label="AUTHORIZATION *" value={newEngagement.authorization} onChange={(v) => setNewEngagement((s) => ({ ...s, authorization: v }))} placeholder="Written authorization reference..." rows={2} />
            )}
            <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
              <button onClick={initEngagement} disabled={!newEngagement.target} style={{ ...styles.primaryBtn, flex: 1, opacity: newEngagement.target ? 1 : 0.4 }}>
                INITIALIZE
              </button>
              <button onClick={() => setView("dashboard")} style={{ ...styles.secondaryBtn, flex: 0 }}>CANCEL</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <Header hexStatus={state.hexstrikeStatus} engagementId={state.engagement.id} />

      {/* Phase Pipeline */}
      <div style={styles.pipeline}>
        {PHASES.map((p, i) => {
          const isActive = state.activePhase === p.id;
          const isPast = PHASES.findIndex((x) => x.id === state.activePhase) > i;
          return (
            <button key={p.id} onClick={() => setPhase(p.id)}
              style={{
                ...styles.phaseBtn,
                background: isActive ? `${p.color}22` : isPast ? `${p.color}11` : "transparent",
                borderColor: isActive ? p.color : isPast ? `${p.color}44` : "#1e293b",
                color: isActive ? p.color : isPast ? `${p.color}99` : "#475569",
                boxShadow: isActive ? `0 0 12px ${p.color}33` : "none",
              }}>
              <span style={{ fontSize: "14px" }}>{p.icon}</span>
              <span style={{ fontSize: "9px", fontWeight: 700, letterSpacing: "0.08em" }}>{p.label}</span>
            </button>
          );
        })}
      </div>

      {/* Stats Row */}
      <div style={styles.statsRow}>
        <StatCard label="TARGET" value={state.engagement.target} color="#e2e8f0" />
        <StatCard label="TYPE" value={state.engagement.type.toUpperCase()} color="#6366f1" />
        <StatCard label="FINDINGS" value={state.findings.length} color="#f59e0b" />
        <StatCard label="HOSTS" value={state.hosts.length || "—"} color="#3b82f6" />
      </div>

      {/* Severity Bar */}
      {state.findings.length > 0 && (
        <div style={{ padding: "0 16px", marginBottom: "12px" }}>
          <div style={{ display: "flex", borderRadius: "6px", overflow: "hidden", height: "8px" }}>
            {["critical", "high", "medium", "low", "info"].map((sev) => {
              const count = severityCounts[sev] || 0;
              if (!count) return null;
              const pct = (count / state.findings.length) * 100;
              return <div key={sev} style={{ width: `${pct}%`, background: SEVERITY_COLORS[sev], transition: "width 0.3s" }} />;
            })}
          </div>
          <div style={{ display: "flex", gap: "12px", marginTop: "6px" }}>
            {["critical", "high", "medium", "low", "info"].map((sev) => {
              const count = severityCounts[sev] || 0;
              if (!count) return null;
              return (
                <div key={sev} style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "10px", color: SEVERITY_COLORS[sev] }}>
                  <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: SEVERITY_COLORS[sev] }} />
                  {count} {sev}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab Content */}
      <div style={styles.tabs}>
        {["findings", "timeline", "hosts"].map((tab) => (
          <button key={tab} onClick={() => setView(tab)}
            style={{ ...styles.tab, borderBottomColor: view === tab ? "#dc2626" : "transparent", color: view === tab ? "#e2e8f0" : "#64748b" }}>
            {tab.toUpperCase()}
          </button>
        ))}
      </div>

      <div style={{ padding: "12px 16px", flex: 1, overflow: "auto" }}>
        {view === "findings" && <FindingsView findings={state.findings} />}
        {view === "timeline" && <TimelineView timeline={state.timeline} ref={timelineRef} />}
        {view === "hosts" && <HostsView hosts={state.hosts} />}
      </div>

      {/* Quick Actions */}
      <div style={styles.quickActions}>
        <button onClick={() => addFinding({ severity: "critical", title: "Sample Critical Finding", asset: state.engagement.target, tool: "nuclei", cve: "CVE-2024-XXXXX" })} style={styles.actionBtn}>
          + Finding
        </button>
        <button onClick={() => addTimelineEntry({ phase: state.activePhase, action: "tool_run", detail: "Manual tool execution logged" })} style={styles.actionBtn}>
          + Log Entry
        </button>
        <button onClick={resetEngagement} style={{ ...styles.actionBtn, borderColor: "#dc262644", color: "#dc2626" }}>
          Reset
        </button>
      </div>
    </div>
  );
}

// --- Sub Components ---

function Header({ hexStatus, engagementId }) {
  return (
    <div style={styles.header}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <div style={{ fontSize: "18px" }}>💀</div>
        <div>
          <div style={{ fontWeight: 800, fontSize: "13px", letterSpacing: "0.06em", color: "#f1f5f9" }}>KALI AGENT</div>
          {engagementId && <div style={{ fontSize: "9px", color: "#94a3b8", letterSpacing: "0.1em" }}>{engagementId}</div>}
        </div>
      </div>
      <div style={{
        fontSize: "9px", fontWeight: 700, letterSpacing: "0.08em",
        padding: "3px 8px", borderRadius: "4px",
        background: hexStatus === "online" ? "#16a34a22" : "#47556922",
        color: hexStatus === "online" ? "#4ade80" : "#94a3b8",
        border: `1px solid ${hexStatus === "online" ? "#16a34a44" : "#33415544"}`,
      }}>
        HEX {hexStatus === "online" ? "LIVE" : "—"}
      </div>
    </div>
  );
}

function StatCard({ label, value, color }) {
  return (
    <div style={styles.statCard}>
      <div style={{ fontSize: "9px", color: "#64748b", letterSpacing: "0.1em", fontWeight: 600 }}>{label}</div>
      <div style={{ fontSize: "14px", fontWeight: 800, color, marginTop: "2px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {value}
      </div>
    </div>
  );
}

function FindingsView({ findings }) {
  if (!findings.length) return <div style={styles.empty}>No findings yet — run vuln-analysis</div>;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      {findings.map((f) => (
        <div key={f.id} style={{ ...styles.card, borderLeft: `3px solid ${SEVERITY_COLORS[f.severity]}` }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ fontSize: "11px", fontWeight: 700, color: "#e2e8f0" }}>{f.id}</div>
            <div style={{ fontSize: "9px", fontWeight: 700, color: SEVERITY_COLORS[f.severity], textTransform: "uppercase", letterSpacing: "0.08em" }}>
              {f.severity}
            </div>
          </div>
          <div style={{ fontSize: "12px", color: "#cbd5e1", marginTop: "4px" }}>{f.title}</div>
          <div style={{ display: "flex", gap: "12px", marginTop: "6px", fontSize: "10px", color: "#64748b" }}>
            {f.cve && <span>{f.cve}</span>}
            {f.asset && <span>{f.asset}</span>}
            {f.tool && <span>via {f.tool}</span>}
          </div>
        </div>
      ))}
    </div>
  );
}

const TimelineView = ({ timeline }) => {
  if (!timeline.length) return <div style={styles.empty}>Timeline empty</div>;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
      {timeline.map((entry) => {
        const phase = PHASES.find((p) => p.id === entry.phase);
        return (
          <div key={entry.id} style={{ display: "flex", gap: "8px", fontSize: "11px", padding: "6px 0", borderBottom: "1px solid #1e293b11" }}>
            <div style={{ width: "60px", color: "#475569", fontSize: "10px", flexShrink: 0 }}>
              {new Date(entry.timestamp).toLocaleTimeString("en-AU", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
            </div>
            <div style={{ width: "16px", fontSize: "12px", flexShrink: 0 }}>{phase?.icon || "⚙️"}</div>
            <div style={{ color: "#94a3b8", flex: 1 }}>{entry.detail}</div>
          </div>
        );
      })}
    </div>
  );
};

function HostsView({ hosts }) {
  if (!hosts.length) return <div style={styles.empty}>No hosts compromised — run post-exploit</div>;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      {hosts.map((h, i) => (
        <div key={i} style={styles.card}>
          <div style={{ fontSize: "12px", fontWeight: 700, color: "#e2e8f0" }}>{h.hostname || h.ip}</div>
          <div style={{ fontSize: "10px", color: "#64748b", marginTop: "4px" }}>{h.access || "Unknown access level"}</div>
        </div>
      ))}
    </div>
  );
}

function Input({ label, value, onChange, placeholder }) {
  return (
    <div>
      <div style={styles.label}>{label}</div>
      <input value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder}
        style={styles.input} />
    </div>
  );
}

function TextArea({ label, value, onChange, placeholder, rows = 3 }) {
  return (
    <div>
      <div style={styles.label}>{label}</div>
      <textarea value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} rows={rows}
        style={{ ...styles.input, resize: "vertical", minHeight: `${rows * 22}px` }} />
    </div>
  );
}

// --- Styles ---
const styles = {
  container: {
    fontFamily: "'IBM Plex Mono', 'JetBrains Mono', 'Fira Code', monospace",
    background: "#080b11",
    color: "#cbd5e1",
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    maxWidth: "100%",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 16px",
    borderBottom: "1px solid #1e293b",
    background: "linear-gradient(180deg, #0f1319 0%, #080b11 100%)",
  },
  pipeline: {
    display: "flex",
    gap: "4px",
    padding: "12px 16px",
    borderBottom: "1px solid #1e293b11",
  },
  phaseBtn: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "2px",
    padding: "8px 4px",
    borderRadius: "6px",
    border: "1px solid",
    cursor: "pointer",
    fontFamily: "inherit",
    transition: "all 0.2s",
  },
  statsRow: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "6px",
    padding: "12px 16px",
  },
  statCard: {
    background: "#0f1319",
    borderRadius: "6px",
    padding: "8px 10px",
    border: "1px solid #1e293b",
  },
  tabs: {
    display: "flex",
    borderBottom: "1px solid #1e293b",
    padding: "0 16px",
  },
  tab: {
    padding: "8px 12px",
    fontSize: "10px",
    fontWeight: 700,
    letterSpacing: "0.1em",
    background: "none",
    border: "none",
    borderBottom: "2px solid",
    cursor: "pointer",
    fontFamily: "inherit",
    transition: "all 0.15s",
  },
  card: {
    background: "#0f1319",
    borderRadius: "6px",
    padding: "10px 12px",
    border: "1px solid #1e293b",
  },
  empty: {
    textAlign: "center",
    color: "#475569",
    fontSize: "12px",
    padding: "32px 0",
  },
  emptyState: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    flex: 1,
    padding: "60px 20px",
  },
  quickActions: {
    display: "flex",
    gap: "6px",
    padding: "12px 16px",
    borderTop: "1px solid #1e293b",
  },
  actionBtn: {
    flex: 1,
    padding: "8px",
    borderRadius: "6px",
    border: "1px solid #334155",
    background: "#0f1319",
    color: "#94a3b8",
    fontSize: "10px",
    fontWeight: 600,
    fontFamily: "inherit",
    cursor: "pointer",
  },
  primaryBtn: {
    padding: "12px 24px",
    borderRadius: "8px",
    border: "none",
    background: "linear-gradient(135deg, #dc2626, #991b1b)",
    color: "#fff",
    fontSize: "12px",
    fontWeight: 700,
    letterSpacing: "0.08em",
    cursor: "pointer",
    fontFamily: "inherit",
  },
  secondaryBtn: {
    padding: "12px 16px",
    borderRadius: "8px",
    border: "1px solid #334155",
    background: "#1e293b",
    color: "#94a3b8",
    fontSize: "12px",
    fontWeight: 600,
    cursor: "pointer",
    fontFamily: "inherit",
  },
  sectionTitle: {
    fontSize: "11px",
    fontWeight: 800,
    letterSpacing: "0.12em",
    color: "#dc2626",
    marginBottom: "16px",
  },
  label: {
    fontSize: "9px",
    fontWeight: 700,
    letterSpacing: "0.1em",
    color: "#64748b",
    marginBottom: "4px",
  },
  input: {
    width: "100%",
    padding: "8px 10px",
    borderRadius: "6px",
    border: "1px solid #334155",
    background: "#0f1319",
    color: "#e2e8f0",
    fontSize: "12px",
    fontFamily: "inherit",
    outline: "none",
    boxSizing: "border-box",
  },
  chip: {
    padding: "5px 10px",
    borderRadius: "4px",
    border: "1px solid",
    color: "#e2e8f0",
    fontSize: "10px",
    fontWeight: 600,
    fontFamily: "inherit",
    cursor: "pointer",
    letterSpacing: "0.05em",
  },
};
