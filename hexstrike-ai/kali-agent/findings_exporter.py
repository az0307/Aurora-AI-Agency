"""
Findings Exporter for Kali Agent
Exports vulnerability findings to multiple formats for ticket systems and reporting.

Supported formats:
  - CSV (spreadsheet import)
  - Jira (bulk import JSON)
  - Linear (API-ready JSON)
  - Markdown table (report appendix)
  - SARIF (Static Analysis Results Interchange Format)

AutoBoros.ai | 2026-03-27
"""

import csv
import io
import json
import os
from datetime import datetime, timezone
from typing import Optional


SEVERITY_MAP_JIRA = {
    "critical": "Highest",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    "info": "Lowest",
}

SEVERITY_MAP_LINEAR = {
    "critical": 1,  # Urgent
    "high": 2,      # High
    "medium": 3,    # Medium
    "low": 4,       # Low
    "info": 0,      # No priority
}


def export_csv(findings: list, output_path: Optional[str] = None) -> str:
    """
    Export findings to CSV format.
    Returns CSV string or writes to file if output_path provided.
    """
    fieldnames = [
        "ID", "Severity", "CVSS", "CVE", "Title",
        "Affected Asset", "Tool", "CWE", "MITRE ATT&CK",
        "Description", "Remediation", "Status", "Evidence",
    ]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for f in findings:
        writer.writerow({
            "ID": f.get("id", ""),
            "Severity": f.get("severity", "").upper(),
            "CVSS": f.get("cvss", ""),
            "CVE": f.get("cve", ""),
            "Title": f.get("title", ""),
            "Affected Asset": f.get("affected_asset", f.get("asset", "")),
            "Tool": f.get("tool", ""),
            "CWE": f.get("cwe", ""),
            "MITRE ATT&CK": ", ".join(f.get("mitre_attack", [])) if isinstance(f.get("mitre_attack"), list) else f.get("mitre_attack", ""),
            "Description": f.get("description", ""),
            "Remediation": f.get("remediation", ""),
            "Status": f.get("status", "confirmed"),
            "Evidence": f.get("evidence", "")[:200],
        })

    csv_str = output.getvalue()
    if output_path:
        with open(output_path, "w", newline="") as fh:
            fh.write(csv_str)
    return csv_str


def export_jira_bulk(findings: list, project_key: str = "SEC", output_path: Optional[str] = None) -> str:
    """
    Export findings as Jira bulk import JSON.
    Each finding becomes a Jira issue with type=Bug.
    """
    issues = []
    for f in findings:
        issue = {
            "fields": {
                "project": {"key": project_key},
                "issuetype": {"name": "Bug"},
                "summary": f"[{f.get('severity', 'info').upper()}] {f.get('title', 'Untitled')}",
                "description": _build_jira_description(f),
                "priority": {"name": SEVERITY_MAP_JIRA.get(f.get("severity", "info"), "Medium")},
                "labels": [
                    "pentest",
                    "security",
                    f.get("severity", "info"),
                    f"tool-{f.get('tool', 'manual')}",
                ],
            }
        }
        if f.get("cve"):
            issue["fields"]["labels"].append(f["cve"])
        issues.append(issue)

    result = {"issueUpdates": issues}
    json_str = json.dumps(result, indent=2)

    if output_path:
        with open(output_path, "w") as fh:
            fh.write(json_str)
    return json_str


def _build_jira_description(finding: dict) -> str:
    """Build Jira-formatted description from finding."""
    parts = []
    parts.append(f"h3. {finding.get('title', 'Untitled')}")
    parts.append("")

    if finding.get("cve"):
        parts.append(f"*CVE:* {finding['cve']}")
    if finding.get("cvss"):
        parts.append(f"*CVSS:* {finding['cvss']}")
    if finding.get("affected_asset") or finding.get("asset"):
        parts.append(f"*Affected Asset:* {finding.get('affected_asset', finding.get('asset', ''))}")
    if finding.get("cwe"):
        parts.append(f"*CWE:* {finding['cwe']}")

    parts.append("")
    if finding.get("description"):
        parts.append(f"h4. Description")
        parts.append(finding["description"])
        parts.append("")

    if finding.get("evidence"):
        parts.append("h4. Evidence")
        parts.append(f"{{code}}{finding['evidence']}{{code}}")
        parts.append("")

    if finding.get("remediation"):
        parts.append("h4. Remediation")
        parts.append(finding["remediation"])

    return "\n".join(parts)


def export_linear(findings: list, team_id: str = "", output_path: Optional[str] = None) -> str:
    """
    Export findings as Linear-compatible issue creation payloads.
    Returns JSON array of issue objects for Linear GraphQL API.
    """
    issues = []
    for f in findings:
        issue = {
            "title": f"[{f.get('severity', 'info').upper()}] {f.get('title', 'Untitled')}",
            "description": _build_markdown_description(f),
            "priority": SEVERITY_MAP_LINEAR.get(f.get("severity", "info"), 0),
            "labels": ["pentest", "security", f.get("severity", "info")],
        }
        if team_id:
            issue["teamId"] = team_id
        issues.append(issue)

    json_str = json.dumps(issues, indent=2)
    if output_path:
        with open(output_path, "w") as fh:
            fh.write(json_str)
    return json_str


def _build_markdown_description(finding: dict) -> str:
    """Build Markdown description for Linear/GitHub issues."""
    parts = []
    parts.append(f"## {finding.get('title', 'Untitled')}")
    parts.append("")

    meta = []
    if finding.get("severity"):
        meta.append(f"**Severity:** {finding['severity'].upper()}")
    if finding.get("cvss"):
        meta.append(f"**CVSS:** {finding['cvss']}")
    if finding.get("cve"):
        meta.append(f"**CVE:** {finding['cve']}")
    if finding.get("affected_asset") or finding.get("asset"):
        meta.append(f"**Asset:** {finding.get('affected_asset', finding.get('asset', ''))}")
    if finding.get("tool"):
        meta.append(f"**Tool:** {finding['tool']}")
    if finding.get("cwe"):
        meta.append(f"**CWE:** {finding['cwe']}")

    parts.append(" | ".join(meta))
    parts.append("")

    if finding.get("description"):
        parts.append("### Description")
        parts.append(finding["description"])
        parts.append("")

    if finding.get("evidence"):
        parts.append("### Evidence")
        parts.append(f"```\n{finding['evidence']}\n```")
        parts.append("")

    if finding.get("remediation"):
        parts.append("### Remediation")
        parts.append(finding["remediation"])

    return "\n".join(parts)


def export_markdown_table(findings: list, output_path: Optional[str] = None) -> str:
    """Export findings as a Markdown table for report appendices."""
    lines = [
        "| # | Severity | CVSS | CVE | Title | Asset | Tool | Status |",
        "|---|----------|------|-----|-------|-------|------|--------|",
    ]

    for i, f in enumerate(findings, 1):
        lines.append(
            f"| {i} "
            f"| **{f.get('severity', '?').upper()}** "
            f"| {f.get('cvss', '—')} "
            f"| {f.get('cve', '—')} "
            f"| {f.get('title', 'Untitled')[:50]} "
            f"| {f.get('affected_asset', f.get('asset', '—'))[:30]} "
            f"| {f.get('tool', '—')} "
            f"| {f.get('status', 'confirmed')} |"
        )

    md_str = "\n".join(lines)
    if output_path:
        with open(output_path, "w") as fh:
            fh.write(md_str)
    return md_str


def export_sarif(findings: list, tool_name: str = "kali-agent", output_path: Optional[str] = None) -> str:
    """
    Export findings in SARIF 2.1.0 format.
    Compatible with GitHub Security tab, Azure DevOps, and other SARIF consumers.
    """
    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": tool_name,
                    "version": "1.0.0",
                    "informationUri": "https://github.com/0x4m4/kali-agent",
                    "rules": [],
                }
            },
            "results": [],
        }],
    }

    severity_to_sarif = {
        "critical": "error",
        "high": "error",
        "medium": "warning",
        "low": "note",
        "info": "note",
    }

    rules_seen = set()
    run = sarif["runs"][0]

    for f in findings:
        rule_id = f.get("cve") or f.get("cwe") or f.get("id", "unknown")

        if rule_id not in rules_seen:
            run["tool"]["driver"]["rules"].append({
                "id": rule_id,
                "name": f.get("title", "Unknown"),
                "shortDescription": {"text": f.get("title", "Unknown")},
                "fullDescription": {"text": f.get("description", "")},
                "help": {"text": f.get("remediation", ""), "markdown": f.get("remediation", "")},
                "defaultConfiguration": {
                    "level": severity_to_sarif.get(f.get("severity", "info"), "note"),
                },
            })
            rules_seen.add(rule_id)

        result = {
            "ruleId": rule_id,
            "level": severity_to_sarif.get(f.get("severity", "info"), "note"),
            "message": {"text": f.get("description", f.get("title", ""))},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": f.get("affected_asset", f.get("asset", "unknown")),
                    }
                }
            }],
        }
        if f.get("evidence"):
            result["message"]["text"] += f"\n\nEvidence: {f['evidence'][:500]}"

        run["results"].append(result)

    json_str = json.dumps(sarif, indent=2)
    if output_path:
        with open(output_path, "w") as fh:
            fh.write(json_str)
    return json_str


def export_all(
    findings: list,
    output_dir: str,
    engagement_id: str = "ENG-XXXX",
    jira_project: str = "SEC",
    linear_team: str = "",
) -> dict:
    """
    Export findings to all supported formats at once.
    Returns dict of {format: filepath}.
    """
    os.makedirs(output_dir, exist_ok=True)
    prefix = f"{engagement_id}_findings"

    paths = {}
    paths["csv"] = os.path.join(output_dir, f"{prefix}.csv")
    export_csv(findings, paths["csv"])

    paths["jira"] = os.path.join(output_dir, f"{prefix}_jira.json")
    export_jira_bulk(findings, jira_project, paths["jira"])

    paths["linear"] = os.path.join(output_dir, f"{prefix}_linear.json")
    export_linear(findings, linear_team, paths["linear"])

    paths["markdown"] = os.path.join(output_dir, f"{prefix}.md")
    export_markdown_table(findings, paths["markdown"])

    paths["sarif"] = os.path.join(output_dir, f"{prefix}.sarif")
    export_sarif(findings, output_path=paths["sarif"])

    return paths
