import { useState, useEffect, useCallback, useMemo } from "react";

/**
 * BloodHound Attack Path Visualizer
 * Renders Active Directory attack paths from BloodHound JSON data
 * or manual attack chain definitions.
 * 
 * Supports: ShortestPath, owned principals, domain admin paths
 */

const NODE_TYPES = {
  User: { icon: "👤", color: "#3b82f6", shape: "circle" },
  Group: { icon: "👥", color: "#8b5cf6", shape: "circle" },
  Computer: { icon: "🖥️", color: "#10b981", shape: "rect" },
  Domain: { icon: "🏛️", color: "#f59e0b", shape: "diamond" },
  GPO: { icon: "📋", color: "#6366f1", shape: "rect" },
  OU: { icon: "📁", color: "#64748b", shape: "rect" },
  Unknown: { icon: "❓", color: "#94a3b8", shape: "circle" },
};

const EDGE_TYPES = {
  MemberOf: { color: "#3b82f6", label: "MemberOf", dashed: false },
  AdminTo: { color: "#ef4444", label: "AdminTo", dashed: false },
  HasSession: { color: "#f97316", label: "HasSession", dashed: true },
  CanRDP: { color: "#10b981", label: "CanRDP", dashed: false },
  CanPSRemote: { color: "#10b981", label: "PSRemote", dashed: false },
  GenericAll: { color: "#dc2626", label: "GenericAll", dashed: false },
  GenericWrite: { color: "#dc2626", label: "GenericWrite", dashed: false },
  WriteDacl: { color: "#dc2626", label: "WriteDacl", dashed: false },
  WriteOwner: { color: "#dc2626", label: "WriteOwner", dashed: false },
  ForceChangePassword: { color: "#f97316", label: "ForceChgPwd", dashed: false },
  AddMember: { color: "#8b5cf6", label: "AddMember", dashed: false },
  DCSync: { color: "#dc2626", label: "DCSync", dashed: false },
  GetChanges: { color: "#dc2626", label: "GetChanges", dashed: false },
  GetChangesAll: { color: "#dc2626", label: "GetChangesAll", dashed: false },
  Owns: { color: "#f59e0b", label: "Owns", dashed: false },
  Contains: { color: "#64748b", label: "Contains", dashed: true },
  GpLink: { color: "#6366f1", label: "GpLink", dashed: true },
  AllExtendedRights: { color: "#dc2626", label: "AllExtRights", dashed: false },
  SQLAdmin: { color: "#ef4444", label: "SQLAdmin", dashed: false },
  ReadLAPSPassword: { color: "#f97316", label: "ReadLAPS", dashed: false },
  YOURCOMPROMISE: { color: "#dc2626", label: "COMPROMISED", dashed: false },
};

const DEMO_PATH = {
  nodes: [
    { id: "user1", name: "JSMITH@CORP.LOCAL", type: "User", owned: true },
    { id: "comp1", name: "WS01.CORP.LOCAL", type: "Computer", owned: true },
    { id: "user2", name: "SVC_BACKUP@CORP.LOCAL", type: "User", owned: true },
    { id: "group1", name: "BACKUP OPERATORS@CORP.LOCAL", type: "Group" },
    { id: "comp2", name: "DC01.CORP.LOCAL", type: "Computer" },
    { id: "group2", name: "DOMAIN ADMINS@CORP.LOCAL", type: "Group", highValue: true },
    { id: "domain1", name: "CORP.LOCAL", type: "Domain", highValue: true },
  ],
  edges: [
    { source: "user1", target: "comp1", type: "HasSession" },
    { source: "comp1", target: "user2", type: "HasSession" },
    { source: "user2", target: "group1", type: "MemberOf" },
    { source: "group1", target: "comp2", type: "AdminTo" },
    { source: "comp2", target: "group2", type: "DCSync" },
    { source: "group2", target: "domain1", type: "AdminTo" },
  ],
  metadata: {
    title: "Shortest Path to Domain Admin",
    hops: 6,
    startNode: "JSMITH@CORP.LOCAL",
    endNode: "DOMAIN ADMINS@CORP.LOCAL",
  },
};

export default function BloodHoundViz() {
  const [pathData, setPathData] = useState(DEMO_PATH);
  const [selectedNode, setSelectedNode] = useState(null);
  const [jsonInput, setJsonInput] = useState("");
  const [showImport, setShowImport] = useState(false);
  const [layout, setLayout] = useState("horizontal"); // horizontal | vertical

  const nodePositions = useMemo(() => {
    const positions = {};
    const nodes = pathData.nodes;
    const isHoriz = layout === "horizontal";
    const count = nodes.length;
    const spacing = isHoriz ? 160 : 120;
    const cross = isHoriz ? 200 : 280;

    nodes.forEach((node, i) => {
      // Slight vertical wave for visual interest
      const wave = Math.sin(i * 0.8) * 25;
      positions[node.id] = {
        x: isHoriz ? 80 + i * spacing : cross + wave,
        y: isHoriz ? cross + wave : 60 + i * spacing,
      };
    });
    return positions;
  }, [pathData.nodes, layout]);

  const svgWidth = useMemo(() => {
    if (layout === "horizontal") return Math.max(600, pathData.nodes.length * 160 + 100);
    return 600;
  }, [pathData.nodes.length, layout]);

  const svgHeight = useMemo(() => {
    if (layout === "vertical") return Math.max(400, pathData.nodes.length * 120 + 100);
    return 420;
  }, [pathData.nodes.length, layout]);

  const handleImport = useCallback(() => {
    try {
      const data = JSON.parse(jsonInput);
      if (data.nodes && data.edges) {
        setPathData(data);
        setShowImport(false);
        setJsonInput("");
      }
    } catch {
      alert("Invalid JSON — needs {nodes: [...], edges: [...]}");
    }
  }, [jsonInput]);

  return (
    <div style={{
      fontFamily: "'IBM Plex Mono', 'JetBrains Mono', monospace",
      background: "#080b11",
      color: "#cbd5e1",
      borderRadius: "12px",
      border: "1px solid #1e293b",
      overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        padding: "12px 16px", borderBottom: "1px solid #1e293b",
        background: "linear-gradient(180deg, #0f1319, #080b11)",
      }}>
        <div>
          <div style={{ fontSize: "12px", fontWeight: 800, letterSpacing: "0.06em", color: "#f1f5f9" }}>
            🩸 ATTACK PATH
          </div>
          <div style={{ fontSize: "9px", color: "#64748b", letterSpacing: "0.08em", marginTop: "2px" }}>
            {pathData.metadata?.title || "BloodHound Visualization"}
          </div>
        </div>
        <div style={{ display: "flex", gap: "6px" }}>
          <button onClick={() => setLayout(l => l === "horizontal" ? "vertical" : "horizontal")}
            style={btnStyle}>
            {layout === "horizontal" ? "↕" : "↔"}
          </button>
          <button onClick={() => setShowImport(!showImport)} style={btnStyle}>
            {showImport ? "✕" : "📥"}
          </button>
        </div>
      </div>

      {/* Import panel */}
      {showImport && (
        <div style={{ padding: "12px 16px", borderBottom: "1px solid #1e293b", background: "#0f131966" }}>
          <div style={{ fontSize: "10px", color: "#64748b", marginBottom: "6px", fontWeight: 600 }}>
            PASTE BLOODHOUND JSON or CUSTOM PATH
          </div>
          <textarea value={jsonInput} onChange={(e) => setJsonInput(e.target.value)}
            placeholder='{"nodes": [...], "edges": [...]}'
            rows={4}
            style={{
              width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid #334155",
              background: "#0f172a", color: "#e2e8f0", fontSize: "11px", fontFamily: "inherit",
              resize: "vertical", boxSizing: "border-box",
            }} />
          <button onClick={handleImport} style={{ ...btnStyle, marginTop: "6px", width: "100%" }}>
            LOAD PATH
          </button>
        </div>
      )}

      {/* SVG Visualization */}
      <div style={{ overflowX: "auto", padding: "8px" }}>
        <svg width={svgWidth} height={svgHeight} viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          style={{ display: "block", margin: "0 auto" }}>
          <defs>
            {Object.entries(EDGE_TYPES).map(([type, config]) => (
              <marker key={type} id={`arrow-${type}`} viewBox="0 0 10 6" refX="10" refY="3"
                markerWidth="8" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 3 L 0 6 z" fill={config.color} />
              </marker>
            ))}
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          </defs>

          {/* Edges */}
          {pathData.edges.map((edge, i) => {
            const from = nodePositions[edge.source];
            const to = nodePositions[edge.target];
            if (!from || !to) return null;
            const config = EDGE_TYPES[edge.type] || { color: "#475569", label: edge.type, dashed: false };
            const midX = (from.x + to.x) / 2;
            const midY = (from.y + to.y) / 2;
            const dx = to.x - from.x;
            const dy = to.y - from.y;
            const len = Math.sqrt(dx * dx + dy * dy);
            const nx = dx / len;
            const ny = dy / len;
            const startX = from.x + nx * 28;
            const startY = from.y + ny * 28;
            const endX = to.x - nx * 28;
            const endY = to.y - ny * 28;

            return (
              <g key={i}>
                <line x1={startX} y1={startY} x2={endX} y2={endY}
                  stroke={config.color} strokeWidth="2" strokeOpacity="0.7"
                  strokeDasharray={config.dashed ? "6,3" : "none"}
                  markerEnd={`url(#arrow-${edge.type})`} />
                <rect x={midX - 30} y={midY - 8} width="60" height="16" rx="3"
                  fill="#080b11" fillOpacity="0.9" stroke={config.color} strokeWidth="0.5" />
                <text x={midX} y={midY + 3} textAnchor="middle"
                  fill={config.color} fontSize="7" fontFamily="inherit" fontWeight="600">
                  {config.label}
                </text>
              </g>
            );
          })}

          {/* Nodes */}
          {pathData.nodes.map((node) => {
            const pos = nodePositions[node.id];
            if (!pos) return null;
            const config = NODE_TYPES[node.type] || NODE_TYPES.Unknown;
            const isSelected = selectedNode === node.id;
            const isOwned = node.owned;
            const isHighValue = node.highValue;

            return (
              <g key={node.id} onClick={() => setSelectedNode(isSelected ? null : node.id)}
                style={{ cursor: "pointer" }}>
                {/* Glow ring for owned / high-value */}
                {(isOwned || isHighValue) && (
                  <circle cx={pos.x} cy={pos.y} r="30"
                    fill="none" stroke={isOwned ? "#dc2626" : "#f59e0b"}
                    strokeWidth="1.5" strokeDasharray="4,3" opacity="0.5" filter="url(#glow)" />
                )}
                {/* Node circle */}
                <circle cx={pos.x} cy={pos.y} r={isSelected ? "26" : "22"}
                  fill={isSelected ? `${config.color}33` : "#0f1319"}
                  stroke={config.color} strokeWidth={isSelected ? "3" : "2"} />
                {/* Icon */}
                <text x={pos.x} y={pos.y + 1} textAnchor="middle" dominantBaseline="middle"
                  fontSize="16">{config.icon}</text>
                {/* Owned badge */}
                {isOwned && (
                  <g>
                    <circle cx={pos.x + 18} cy={pos.y - 18} r="7" fill="#dc2626" />
                    <text x={pos.x + 18} y={pos.y - 15} textAnchor="middle" fontSize="8" fill="#fff">☠</text>
                  </g>
                )}
                {/* High-value badge */}
                {isHighValue && !isOwned && (
                  <g>
                    <circle cx={pos.x + 18} cy={pos.y - 18} r="7" fill="#f59e0b" />
                    <text x={pos.x + 18} y={pos.y - 15} textAnchor="middle" fontSize="8" fill="#fff">★</text>
                  </g>
                )}
                {/* Label */}
                <text x={pos.x} y={pos.y + 36} textAnchor="middle"
                  fill="#94a3b8" fontSize="8" fontFamily="inherit" fontWeight="600">
                  {node.name.length > 20 ? node.name.slice(0, 18) + "…" : node.name}
                </text>
                {/* Type label */}
                <text x={pos.x} y={pos.y + 46} textAnchor="middle"
                  fill="#475569" fontSize="7" fontFamily="inherit">
                  {node.type}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend */}
      <div style={{
        display: "flex", flexWrap: "wrap", gap: "8px", padding: "8px 16px",
        borderTop: "1px solid #1e293b", fontSize: "9px",
      }}>
        <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
          <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#dc2626", display: "inline-block" }} />
          <span style={{ color: "#dc2626" }}>Owned</span>
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
          <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#f59e0b", display: "inline-block" }} />
          <span style={{ color: "#f59e0b" }}>High Value</span>
        </span>
        {Object.entries(NODE_TYPES).slice(0, 4).map(([type, config]) => (
          <span key={type} style={{ display: "flex", alignItems: "center", gap: "3px", color: "#64748b" }}>
            {config.icon} {type}
          </span>
        ))}
      </div>

      {/* Selected node details */}
      {selectedNode && (() => {
        const node = pathData.nodes.find((n) => n.id === selectedNode);
        if (!node) return null;
        const inEdges = pathData.edges.filter((e) => e.target === selectedNode);
        const outEdges = pathData.edges.filter((e) => e.source === selectedNode);
        return (
          <div style={{
            padding: "12px 16px", borderTop: "1px solid #1e293b", background: "#0f131966",
          }}>
            <div style={{ fontSize: "11px", fontWeight: 700, color: "#e2e8f0" }}>
              {NODE_TYPES[node.type]?.icon} {node.name}
            </div>
            <div style={{ fontSize: "10px", color: "#64748b", marginTop: "4px" }}>
              Type: {node.type} {node.owned ? "| ☠ OWNED" : ""} {node.highValue ? "| ★ HIGH VALUE" : ""}
            </div>
            {inEdges.length > 0 && (
              <div style={{ fontSize: "10px", color: "#94a3b8", marginTop: "6px" }}>
                ← Inbound: {inEdges.map((e) => `${pathData.nodes.find((n) => n.id === e.source)?.name?.split("@")[0]} (${e.type})`).join(", ")}
              </div>
            )}
            {outEdges.length > 0 && (
              <div style={{ fontSize: "10px", color: "#94a3b8", marginTop: "2px" }}>
                → Outbound: {outEdges.map((e) => `${pathData.nodes.find((n) => n.id === e.target)?.name?.split("@")[0]} (${e.type})`).join(", ")}
              </div>
            )}
          </div>
        );
      })()}

      {/* Stats footer */}
      <div style={{
        display: "flex", justifyContent: "space-between", padding: "8px 16px",
        borderTop: "1px solid #1e293b", fontSize: "9px", color: "#475569",
      }}>
        <span>{pathData.nodes.length} nodes · {pathData.edges.length} edges · {pathData.metadata?.hops || pathData.edges.length} hops</span>
        <span>{pathData.nodes.filter((n) => n.owned).length} owned · {pathData.nodes.filter((n) => n.highValue).length} high-value</span>
      </div>
    </div>
  );
}

const btnStyle = {
  padding: "4px 10px",
  borderRadius: "4px",
  border: "1px solid #334155",
  background: "#1e293b",
  color: "#94a3b8",
  fontSize: "11px",
  fontFamily: "inherit",
  cursor: "pointer",
};
