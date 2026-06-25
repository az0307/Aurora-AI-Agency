"""
Notion Findings Sync for Kali Agent
Pushes pentest findings to a Notion database for tracking and client collaboration.

Uses the Notion MCP connector already available in Claude.ai.
This module generates the structured payloads — Claude calls the MCP.

AutoBoros.ai | 2026-03-27
"""

import json
from datetime import datetime, timezone
from typing import Optional


SEVERITY_EMOJI = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🔵",
    "info": "⚪",
}

SEVERITY_COLOR = {
    "critical": "red",
    "high": "orange",
    "medium": "yellow",
    "low": "blue",
    "info": "gray",
}

STATUS_OPTIONS = ["New", "Confirmed", "Exploited", "Reported", "Remediated", "Retest", "Closed"]


def generate_database_schema(engagement_id: str) -> dict:
    """
    Generate a Notion database schema for pentest findings.
    Use with Notion MCP: notion-create-database

    The schema creates a database with properties for:
    - Finding ID, severity, CVSS, CVE, title, asset, tool, status, etc.
    """
    return {
        "title": f"Pentest Findings — {engagement_id}",
        "description": f"Vulnerability findings from engagement {engagement_id}",
        "schema": {
            "Finding ID": {"type": "title"},
            "Severity": {
                "type": "select",
                "options": [
                    {"name": "Critical", "color": "red"},
                    {"name": "High", "color": "orange"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "blue"},
                    {"name": "Info", "color": "gray"},
                ],
            },
            "CVSS": {"type": "number", "format": "number"},
            "CVE": {"type": "rich_text"},
            "Title": {"type": "rich_text"},
            "Affected Asset": {"type": "rich_text"},
            "Tool": {"type": "rich_text"},
            "CWE": {"type": "rich_text"},
            "Status": {
                "type": "select",
                "options": [{"name": s, "color": "default"} for s in STATUS_OPTIONS],
            },
            "Description": {"type": "rich_text"},
            "Remediation": {"type": "rich_text"},
            "Evidence": {"type": "rich_text"},
            "MITRE ATT&CK": {"type": "rich_text"},
            "Priority Score": {"type": "number", "format": "number"},
            "Date Found": {"type": "date"},
            "Engagement": {"type": "rich_text"},
        },
    }


def finding_to_notion_page(finding: dict, engagement_id: str = "") -> dict:
    """
    Convert a single finding to Notion page creation payload.
    Use with Notion MCP: notion-create-pages
    """
    sev = finding.get("severity", "info").capitalize()
    finding_id = finding.get("id", finding.get("finding_id", "VULN-???"))

    properties = {
        "Finding ID": {"title": [{"text": {"content": finding_id}}]},
        "Severity": {"select": {"name": sev}},
        "Title": {"rich_text": [{"text": {"content": finding.get("title", "Untitled")[:2000]}}]},
        "Affected Asset": {"rich_text": [{"text": {"content": finding.get("affected_asset", finding.get("asset", ""))[:2000]}}]},
        "Tool": {"rich_text": [{"text": {"content": finding.get("tool", "manual")[:200]}}]},
        "Status": {"select": {"name": finding.get("status", "New").capitalize()}},
        "Date Found": {"date": {"start": datetime.now(timezone.utc).strftime("%Y-%m-%d")}},
    }

    if finding.get("cvss"):
        properties["CVSS"] = {"number": finding["cvss"]}
    if finding.get("cve"):
        properties["CVE"] = {"rich_text": [{"text": {"content": finding["cve"]}}]}
    if finding.get("cwe"):
        properties["CWE"] = {"rich_text": [{"text": {"content": finding["cwe"]}}]}
    if finding.get("description"):
        properties["Description"] = {"rich_text": [{"text": {"content": finding["description"][:2000]}}]}
    if finding.get("remediation"):
        properties["Remediation"] = {"rich_text": [{"text": {"content": finding["remediation"][:2000]}}]}
    if finding.get("evidence"):
        properties["Evidence"] = {"rich_text": [{"text": {"content": finding["evidence"][:2000]}}]}
    if finding.get("priority_score"):
        properties["Priority Score"] = {"number": finding["priority_score"]}
    if engagement_id:
        properties["Engagement"] = {"rich_text": [{"text": {"content": engagement_id}}]}

    mitre = finding.get("mitre_attack", [])
    if mitre:
        mitre_str = ", ".join(mitre) if isinstance(mitre, list) else str(mitre)
        properties["MITRE ATT&CK"] = {"rich_text": [{"text": {"content": mitre_str}}]}

    return {"properties": properties}


def findings_to_notion_batch(findings: list, engagement_id: str = "") -> list:
    """
    Convert all findings to Notion page payloads for batch creation.
    Returns list of page creation payloads.
    """
    return [finding_to_notion_page(f, engagement_id) for f in findings]


def generate_engagement_summary_page(engagement: dict, findings: list, stats: dict) -> dict:
    """
    Generate a Notion page summarizing the entire engagement.
    Use with Notion MCP: notion-create-pages
    """
    severity_counts = {}
    for f in findings:
        sev = f.get("severity", "info")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    summary_text = (
        f"# Penetration Test Summary — {engagement.get('id', 'N/A')}\n\n"
        f"**Client:** {engagement.get('client', 'N/A')}\n"
        f"**Target:** {engagement.get('target', 'N/A')}\n"
        f"**Type:** {engagement.get('type', 'N/A')}\n"
        f"**Dates:** {engagement.get('start_date', '?')} → {engagement.get('end_date', '?')}\n"
        f"**Tester:** {engagement.get('tester', 'N/A')}\n\n"
        f"## Findings Summary\n\n"
        f"- 🔴 Critical: {severity_counts.get('critical', 0)}\n"
        f"- 🟠 High: {severity_counts.get('high', 0)}\n"
        f"- 🟡 Medium: {severity_counts.get('medium', 0)}\n"
        f"- 🔵 Low: {severity_counts.get('low', 0)}\n"
        f"- ⚪ Info: {severity_counts.get('info', 0)}\n"
        f"- **Total:** {len(findings)}\n\n"
        f"## Engagement Stats\n\n"
        f"- Tool calls: {stats.get('total_actions', 'N/A')}\n"
        f"- Scope checks: {stats.get('scope_checks', 'N/A')}\n"
        f"- Scope violations blocked: {stats.get('scope_violations', 'N/A')}\n"
        f"- Exploitation attempts: {stats.get('exploitation_attempts', 'N/A')}\n"
    )

    return {
        "title": f"Engagement Summary — {engagement.get('id', 'N/A')}",
        "content": summary_text,
    }


def generate_sync_instructions(engagement_id: str, findings: list) -> str:
    """
    Generate natural language instructions for Claude to sync findings to Notion.
    Claude reads these and calls the Notion MCP tools.
    """
    instructions = [
        f"## Sync {len(findings)} findings to Notion",
        "",
        "### Step 1: Create the findings database",
        f"Use `notion-create-database` with this schema:",
        f"```json",
        json.dumps(generate_database_schema(engagement_id), indent=2),
        f"```",
        "",
        "### Step 2: Create finding pages",
        f"For each of the {len(findings)} findings below, use `notion-create-pages`:",
        "",
    ]

    for f in findings:
        page = finding_to_notion_page(f, engagement_id)
        sev = f.get("severity", "?")
        title = f.get("title", "?")
        instructions.append(f"**{SEVERITY_EMOJI.get(sev, '❓')} {f.get('id', '?')}: {title}**")

    instructions.extend([
        "",
        "### Step 3: Create engagement summary page",
        "Create a summary page with the overall stats and link to the database.",
    ])

    return "\n".join(instructions)
