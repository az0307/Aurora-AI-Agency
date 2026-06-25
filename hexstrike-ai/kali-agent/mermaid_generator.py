"""
Mermaid Attack Path Generator for Kali Agent
Converts engagement audit trail and findings into Mermaid.js diagrams
for inclusion in pentest reports.

AutoBoros.ai | 2026-03-27
"""

import json
import re
from typing import Optional


SEVERITY_COLORS = {
    "critical": "#dc2626",
    "high": "#f97316",
    "medium": "#eab308",
    "low": "#3b82f6",
    "info": "#6b7280",
}

NODE_STYLES = {
    "internet": 'fill:#e0e0e0,stroke:#333,stroke-width:2px,color:#000',
    "initial_access": 'fill:#f97316,stroke:#c2410c,stroke-width:2px,color:#fff',
    "compromised": 'fill:#dc2626,stroke:#991b1b,stroke-width:2px,color:#fff',
    "domain_admin": 'fill:#7c3aed,stroke:#5b21b6,stroke-width:2px,color:#fff',
    "data": 'fill:#9333ea,stroke:#6b21a8,stroke-width:2px,color:#fff',
    "target": 'fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff',
}


def generate_attack_path_diagram(
    attack_path: list[str],
    title: str = "Attack Path",
    direction: str = "LR",
) -> str:
    """
    Generate a Mermaid flowchart from a list of attack path steps.

    Args:
        attack_path: List of step descriptions (strings)
        title: Diagram title
        direction: LR (left-to-right) or TD (top-down)

    Returns:
        Mermaid diagram string
    """
    if not attack_path:
        return "graph LR\n    A[\"No attack path data\"]"

    lines = [f"graph {direction}"]
    nodes = []

    for i, step in enumerate(attack_path):
        node_id = chr(65 + i) if i < 26 else f"N{i}"
        clean_step = step.replace('"', "'").strip()

        # Determine node style based on keywords
        style = "target"
        step_lower = step.lower()
        if i == 0 or "internet" in step_lower:
            style = "internet"
        elif any(w in step_lower for w in ["rce", "exploit", "initial access", "shell"]):
            style = "initial_access"
        elif any(w in step_lower for w in ["root", "admin", "system", "nt authority"]):
            style = "compromised"
        elif any(w in step_lower for w in ["domain admin", "da", "enterprise admin", "dcsync"]):
            style = "domain_admin"
        elif any(w in step_lower for w in ["database", "pii", "data", "exfil", "sensitive"]):
            style = "data"

        nodes.append({"id": node_id, "label": clean_step, "style": style})

    # Build nodes and edges
    for i, node in enumerate(nodes):
        lines.append(f'    {node["id"]}["{node["label"]}"]')

    lines.append("")

    for i in range(len(nodes) - 1):
        lines.append(f'    {nodes[i]["id"]} --> {nodes[i+1]["id"]}')

    lines.append("")

    # Apply styles
    for node in nodes:
        style_str = NODE_STYLES.get(node["style"], NODE_STYLES["target"])
        lines.append(f'    style {node["id"]} {style_str}')

    return "\n".join(lines)


def generate_findings_diagram(findings: list, direction: str = "TD") -> str:
    """
    Generate a Mermaid diagram showing finding relationships and severity.

    Args:
        findings: List of finding dicts with severity, title, affected_asset
        direction: TD (top-down) or LR

    Returns:
        Mermaid diagram string
    """
    if not findings:
        return "graph TD\n    A[\"No findings\"]"

    lines = [f"graph {direction}"]
    lines.append('    ROOT["Target Assessment"]')

    # Group by severity
    by_severity = {}
    for f in findings:
        sev = f.get("severity", "info")
        by_severity.setdefault(sev, []).append(f)

    node_idx = 0
    for sev in ["critical", "high", "medium", "low", "info"]:
        if sev not in by_severity:
            continue

        sev_id = f"SEV_{sev.upper()}"
        count = len(by_severity[sev])
        lines.append(f'    {sev_id}["{sev.upper()} ({count})"]')
        lines.append(f'    ROOT --> {sev_id}')

        for finding in by_severity[sev][:5]:  # Cap at 5 per severity for readability
            fid = f"F{node_idx}"
            title = finding.get("title", "Unknown")[:40]
            lines.append(f'    {fid}["{title}"]')
            lines.append(f'    {sev_id} --> {fid}')
            node_idx += 1

    # Style severity nodes
    lines.append("")
    for sev in ["critical", "high", "medium", "low", "info"]:
        if sev in by_severity:
            color = SEVERITY_COLORS[sev]
            lines.append(f'    style SEV_{sev.upper()} fill:{color},stroke:#333,color:#fff')

    return "\n".join(lines)


def generate_lateral_movement_diagram(
    movements: list[dict],
    direction: str = "LR",
) -> str:
    """
    Generate a Mermaid diagram showing lateral movement between hosts.

    Args:
        movements: List of dicts with source_host, dest_host, method
        direction: LR or TD

    Returns:
        Mermaid diagram string
    """
    if not movements:
        return "graph LR\n    A[\"No lateral movement data\"]"

    lines = [f"graph {direction}"]
    hosts = set()

    for m in movements:
        src = m.get("source_host", "?").replace(".", "_")
        dst = m.get("dest_host", "?").replace(".", "_")
        method = m.get("method", "unknown")
        hosts.add((src, m.get("source_host", "?")))
        hosts.add((dst, m.get("dest_host", "?")))

    # Define nodes
    for host_id, host_label in hosts:
        lines.append(f'    {host_id}["{host_label}"]')

    lines.append("")

    # Define edges
    for m in movements:
        src = m.get("source_host", "?").replace(".", "_")
        dst = m.get("dest_host", "?").replace(".", "_")
        method = m.get("method", "?")
        lines.append(f'    {src} -->|"{method}"| {dst}')

    # Style all nodes
    lines.append("")
    for host_id, _ in hosts:
        lines.append(f'    style {host_id} {NODE_STYLES["compromised"]}')

    return "\n".join(lines)


def generate_from_audit_log(audit_log_path: str) -> dict:
    """
    Generate all diagrams from an engagement audit log.

    Args:
        audit_log_path: Path to audit.jsonl file

    Returns:
        Dict with diagram strings for each type
    """
    entries = []
    try:
        with open(audit_log_path, "r") as f:
            entries = [json.loads(line) for line in f if line.strip()]
    except (FileNotFoundError, json.JSONDecodeError):
        return {"error": f"Cannot read {audit_log_path}"}

    # Extract attack path from exploitation + lateral movement events
    attack_steps = []
    for e in entries:
        if e.get("action") == "exploitation_attempt" and e.get("result") == "success":
            attack_steps.append(
                f'{e.get("target", "?")} compromised via {e.get("method", "?")}'
            )
        elif e.get("action") == "lateral_movement" and e.get("result") == "success":
            attack_steps.append(
                f'{e.get("source_host", "?")} → {e.get("dest_host", "?")} ({e.get("method", "?")})'
            )

    # Extract findings
    findings = [
        e for e in entries
        if e.get("action") == "finding_discovered"
    ]

    # Extract lateral movements
    movements = [
        e for e in entries
        if e.get("action") == "lateral_movement"
    ]

    return {
        "attack_path": generate_attack_path_diagram(
            attack_steps or ["No exploitation data in audit log"],
            title="Attack Path from Audit Log",
        ),
        "findings_tree": generate_findings_diagram(findings),
        "lateral_movement": generate_lateral_movement_diagram(movements),
        "stats": {
            "total_entries": len(entries),
            "attack_steps": len(attack_steps),
            "findings": len(findings),
            "lateral_movements": len(movements),
        },
    }
