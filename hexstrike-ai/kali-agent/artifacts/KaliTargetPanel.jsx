import { useState, useCallback } from "react";

const ENGAGEMENT_TYPES = [
  { id: "external", label: "External Network Pentest", icon: "🌐" },
  { id: "webapp", label: "Web Application Assessment", icon: "🕸️" },
  { id: "internal", label: "Internal Network Pentest", icon: "🏢" },
  { id: "redteam", label: "Red Team Engagement", icon: "🎯" },
  { id: "ctf", label: "CTF / Lab Environment", icon: "🏁" },
];

const METHODOLOGIES = [
  { id: "ptes", label: "PTES", full: "Penetration Testing Execution Standard" },
  { id: "owasp", label: "OWASP", full: "OWASP Testing Guide v4.2" },
  { id: "nist", label: "NIST", full: "NIST SP 800-115" },
  { id: "mitre", label: "MITRE", full: "MITRE ATT&CK Framework" },
  { id: "custom", label: "Custom", full: "Custom Methodology" },
];

const PHASES = [
  { id: "recon", label: "Recon", skill: "recon-osint", color: "#3b82f6" },
  { id: "vuln", label: "Vuln Scan", skill: "vuln-analysis", color: "#f59e0b" },
  { id: "exploit", label: "Exploit", skill: "exploit-dev", color: "#ef4444" },
  { id: "post", label: "Post-Exploit", skill: "post-exploit", color: "#8b5cf6" },
  { id: "report", label: "Report", skill: "red-team-report", color: "#10b981" },
];

export default function KaliTargetPanel() {
  const [target, setTarget] = useState("");
  const [scopeBoundaries, setScopeBoundaries] = useState("");
  const [excludedTargets, setExcludedTargets] = useState("");
  const [engagementType, setEngagementType] = useState("external");
  const [methodology, setMethodology] = useState("ptes");
  const [authorization, setAuthorization] = useState("");
  const [engagementId, setEngagementId] = useState(
    `ENG-${new Date().toISOString().slice(0, 10).replace(/-/g, "")}`
  );
  const [selectedPhases, setSelectedPhases] = useState(
    new Set(["recon", "vuln", "exploit", "post", "report"])
  );
  const [hexstrikeStatus, setHexstrikeStatus] = useState("unknown");
  const [scopeValid, setScopeValid] = useState(null);
  const [isLaunching, setIsLaunching] = useState(false);

  const togglePhase = useCallback((phaseId) => {
    setSelectedPhases((prev) => {
      const next = new Set(prev);
      if (next.has(phaseId)) next.delete(phaseId);
      else next.add(phaseId);
      return next;
    });
  }, []);

  const checkHexstrike = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:8888/health", { signal: AbortSignal.timeout(3000) });
      setHexstrikeStatus(res.ok ? "online" : "error");
    } catch {
      setHexstrikeStatus("offline");
    }
  }, []);

  const buildScopeConfig = useCallback(() => {
    const scopeLines = scopeBoundaries.split("\n").map((s) => s.trim()).filter(Boolean);
    const excludeLines = excludedTargets.split("\n").map((s) => s.trim()).filter(Boolean);
    const ipRegex = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\/\d{1,2})?$/;

    return {
      engagement: {
        id: engagementId,
        client: target.split(".").slice(-2).join(".") || "target",
        type: engagementType,
        authorization: authorization || "Pending — operator must confirm",
        tester: "Az / AutoBoros.ai",
        start_date: new Date().toISOString().slice(0, 10),
        end_date: new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10),
      },
      scope: {
        in_scope: {
          domains: scopeLines.filter((s) => !ipRegex.test(s)),
          ip_ranges: scopeLines.filter((s) => ipRegex.test(s)),
          urls: [],
        },
        out_of_scope: {
          domains: excludeLines.filter((s) => !ipRegex.test(s)),
          ip_ranges: excludeLines.filter((s) => ipRegex.test(s)),
        },
      },
    };
  }, [target, scopeBoundaries, excludedTargets, engagementType, authorization, engagementId]);

  const handleLaunch = useCallback(() => {
    if (!target.trim()) return;
    if (!authorization.trim() && engagementType !== "ctf") {
      setScopeValid(false);
      return;
    }
    setScopeValid(true);
    setIsLaunching(true);
    const config = buildScopeConfig();
    const phases = PHASES.filter((p) => selectedPhases.has(p.id));
    const playbook = phases.map((p, i) => ({
      step: i + 1,
      skill: p.skill,
      label: p.label,
    }));

    console.log("Kali Agent Launch:", { config, playbook });
    // Integration point: dispatch to Curator / executePlaybook()
    setTimeout(() => setIsLaunching(false), 2000);
  }, [target, authorization, engagementType, buildScopeConfig, selectedPhases]);

  const isCTF = engagementType === "ctf";

  return (
    <div style={{
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
      background: "linear-gradient(135deg, #0a0a0a 0%, #111827 50%, #0f172a 100%)",
      color: "#e2e8f0",
      borderRadius: "12px",
      border: "1px solid #1e293b",
      overflow: "hidden",
      maxWidth: "640px",
    }}>
      {/* Header */}
      <div style={{
        background: "linear-gradient(90deg, #dc2626 0%, #991b1b 100%)",
        padding: "16px 20px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ fontSize: "20px" }}>💀</span>
          <div>
            <div style={{ fontWeight: 700, fontSize: "14px", letterSpacing: "0.05em" }}>
              KALI AGENT
            </div>
            <div style={{ fontSize: "10px", opacity: 0.8, letterSpacing: "0.1em" }}>
              ENGAGEMENT CONFIGURATION
            </div>
          </div>
        </div>
        <button
          onClick={checkHexstrike}
          style={{
            background: hexstrikeStatus === "online" ? "#16a34a" : hexstrikeStatus === "offline" ? "#dc2626" : "#475569",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            padding: "4px 10px",
            fontSize: "10px",
            cursor: "pointer",
            fontFamily: "inherit",
          }}
        >
          HexStrike: {hexstrikeStatus === "unknown" ? "CHECK" : hexstrikeStatus.toUpperCase()}
        </button>
      </div>

      {/* Body */}
      <div style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "16px" }}>
        {/* Engagement ID */}
        <Field label="ENGAGEMENT ID">
          <input
            value={engagementId}
            onChange={(e) => setEngagementId(e.target.value)}
            style={inputStyle}
          />
        </Field>

        {/* Target */}
        <Field label="PRIMARY TARGET" required>
          <input
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="e.g. example.com, 10.0.0.0/24, https://app.example.com"
            style={inputStyle}
          />
        </Field>

        {/* Scope Boundaries */}
        <Field label="IN-SCOPE TARGETS" sublabel="One per line — domains, IPs, CIDRs">
          <textarea
            value={scopeBoundaries}
            onChange={(e) => setScopeBoundaries(e.target.value)}
            placeholder={"*.example.com\napi.example.com\n203.0.113.0/24"}
            rows={3}
            style={{ ...inputStyle, resize: "vertical", minHeight: "60px" }}
          />
        </Field>

        {/* Excluded */}
        <Field label="OUT-OF-SCOPE / EXCLUDED" sublabel="One per line">
          <textarea
            value={excludedTargets}
            onChange={(e) => setExcludedTargets(e.target.value)}
            placeholder={"mail.example.com\nproduction-db.example.com"}
            rows={2}
            style={{ ...inputStyle, resize: "vertical", minHeight: "44px" }}
          />
        </Field>

        {/* Engagement Type */}
        <Field label="ENGAGEMENT TYPE">
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
            {ENGAGEMENT_TYPES.map((t) => (
              <button
                key={t.id}
                onClick={() => setEngagementType(t.id)}
                style={{
                  ...chipStyle,
                  background: engagementType === t.id ? "#dc2626" : "#1e293b",
                  borderColor: engagementType === t.id ? "#dc2626" : "#334155",
                }}
              >
                {t.icon} {t.label}
              </button>
            ))}
          </div>
        </Field>

        {/* Methodology */}
        <Field label="METHODOLOGY">
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
            {METHODOLOGIES.map((m) => (
              <button
                key={m.id}
                onClick={() => setMethodology(m.id)}
                title={m.full}
                style={{
                  ...chipStyle,
                  background: methodology === m.id ? "#2563eb" : "#1e293b",
                  borderColor: methodology === m.id ? "#2563eb" : "#334155",
                }}
              >
                {m.label}
              </button>
            ))}
          </div>
        </Field>

        {/* Phases */}
        <Field label="PHASES TO EXECUTE">
          <div style={{ display: "flex", gap: "4px" }}>
            {PHASES.map((p) => (
              <button
                key={p.id}
                onClick={() => togglePhase(p.id)}
                style={{
                  flex: 1,
                  padding: "8px 4px",
                  borderRadius: "6px",
                  border: `2px solid ${selectedPhases.has(p.id) ? p.color : "#334155"}`,
                  background: selectedPhases.has(p.id) ? `${p.color}22` : "#0f172a",
                  color: selectedPhases.has(p.id) ? p.color : "#64748b",
                  fontSize: "10px",
                  fontFamily: "inherit",
                  cursor: "pointer",
                  fontWeight: 600,
                  textAlign: "center",
                }}
              >
                {p.label}
              </button>
            ))}
          </div>
        </Field>

        {/* Authorization */}
        {!isCTF && (
          <Field label="AUTHORIZATION / RULES OF ENGAGEMENT" required>
            <textarea
              value={authorization}
              onChange={(e) => { setAuthorization(e.target.value); setScopeValid(null); }}
              placeholder="Written authorization reference, rules of engagement, time windows, restrictions..."
              rows={3}
              style={{
                ...inputStyle,
                resize: "vertical",
                minHeight: "60px",
                borderColor: scopeValid === false ? "#dc2626" : "#334155",
              }}
            />
            {scopeValid === false && (
              <div style={{ color: "#dc2626", fontSize: "11px", marginTop: "4px" }}>
                ⚠️ Authorization required before engagement can launch
              </div>
            )}
          </Field>
        )}

        {isCTF && (
          <div style={{
            background: "#16a34a15",
            border: "1px solid #16a34a44",
            borderRadius: "8px",
            padding: "10px 14px",
            fontSize: "11px",
            color: "#4ade80",
          }}>
            🏁 CTF Mode — Relaxed scope enforcement. Platform ToS accepted.
          </div>
        )}

        {/* Launch */}
        <button
          onClick={handleLaunch}
          disabled={!target.trim() || isLaunching}
          style={{
            width: "100%",
            padding: "14px",
            borderRadius: "8px",
            border: "none",
            background: isLaunching
              ? "#475569"
              : "linear-gradient(90deg, #dc2626, #991b1b)",
            color: "#fff",
            fontFamily: "inherit",
            fontSize: "13px",
            fontWeight: 700,
            letterSpacing: "0.1em",
            cursor: target.trim() && !isLaunching ? "pointer" : "not-allowed",
            opacity: target.trim() ? 1 : 0.5,
            transition: "all 0.2s",
          }}
        >
          {isLaunching ? "INITIALIZING ENGAGEMENT..." : "🔥 LAUNCH KALI AGENT"}
        </button>
      </div>
    </div>
  );
}

function Field({ label, sublabel, required, children }) {
  return (
    <div>
      <div style={{
        fontSize: "10px",
        fontWeight: 700,
        letterSpacing: "0.1em",
        color: "#94a3b8",
        marginBottom: "6px",
      }}>
        {label}
        {required && <span style={{ color: "#dc2626", marginLeft: "4px" }}>*</span>}
        {sublabel && (
          <span style={{ fontWeight: 400, opacity: 0.6, marginLeft: "8px" }}>
            {sublabel}
          </span>
        )}
      </div>
      {children}
    </div>
  );
}

const inputStyle = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: "6px",
  border: "1px solid #334155",
  background: "#0f172a",
  color: "#e2e8f0",
  fontSize: "13px",
  fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
  outline: "none",
  boxSizing: "border-box",
};

const chipStyle = {
  padding: "6px 10px",
  borderRadius: "6px",
  border: "1px solid",
  color: "#e2e8f0",
  fontSize: "11px",
  fontFamily: "'JetBrains Mono', monospace",
  cursor: "pointer",
  transition: "all 0.15s",
};
