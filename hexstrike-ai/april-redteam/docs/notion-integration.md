# NOTION INTEGRATION — Red Team Stack
# April 2026 | AutoBoros / Az Command Center
# Sync pentest findings → Notion databases

---

## Overview

Connect the red team stack to Az's existing Notion setup:
- Az Command Center: `2f337887-0577-81a0-9b20-ca46e9754137`
- AutoBoros Command Center: `23c37887-0577-8107-ad14-f824899b91bd`

Sync flow:
```
loot/[MISSION]/findings.md → Notion Task Tracker
loot/[MISSION]/report.md   → Notion Document
Mission notes              → Notion Agent Activity Log
CVE watches                → Notion Dispatch Engine
```

---

## Setup

The Notion MCP server is already connected in your Claude setup.
No additional install needed.

**Key Notion MCP patterns (from your established conventions):**
```
- Use data_source_id with collection:// prefix for database pages
- Checkboxes: __YES__ / __NO__
- JSON array strings for multi-select
- Date properties: split into date:prop:start / date:prop:is_datetime
```

---

## WORKFLOW 1 — Create Engagement in Notion

```
Using Notion MCP, create a new page under Az Command Center
for engagement [MISSION_NAME]:

Parent: 2f337887-0577-81a0-9b20-ca46e9754137 (Az Command Center)

Properties:
  Title: "[MISSION_NAME] — Pentest Engagement"
  Type: Security Assessment
  Status: Active
  Target: [TARGET_DOMAIN]
  Start Date: [TODAY]
  
Content:
  # [MISSION_NAME]
  
  ## Authorization
  [AUTH_REFERENCE]
  
  ## Scope
  [SCOPE]
  
  ## Active Findings
  [Will be populated as engagement progresses]
  
  ## Notes
  [Running notes]
```

---

## WORKFLOW 2 — Sync Finding to Notion Task Tracker

When a finding is confirmed, sync to Notion:

```
Using Notion MCP, add task to Task Tracker database for:

Finding: [FINDING_TITLE]
Severity: [CRITICAL/HIGH/MEDIUM/LOW]
Asset: [AFFECTED_URL_OR_IP]
CVSS: [SCORE]
Status: Open
Engagement: [MISSION_NAME]
Due: [REMEDIATION_DATE]
Notes: [BRIEF_DESCRIPTION]

Tags: Security, Pentest, [SEVERITY]
```

**Claude Code prompt pattern:**
```python
# After confirming a finding:
notion_task = f"""
Using the Notion MCP, create a task in the Task Tracker:
- Title: "[SEVERITY] — {finding_title}"
- Status: "Open"
- Priority: {"Urgent" if severity == "Critical" else "High" if severity == "High" else "Normal"}
- Notes: {brief_description}
- Label: "Security Finding"
- Add to project: {mission_name}
"""
```

---

## WORKFLOW 3 — Daily Brief Integration

Add pentest status to the AutoBoros Dispatch Engine:

```
Using Notion MCP, add status update to Dispatch Log:

Type: Security Status
Content: >
  [MISSION_NAME] engagement — Day [N]
  Findings: [X] Critical, [Y] High, [Z] Medium
  Completed: Recon, Enum, Vuln Scan
  Active: Exploitation phase
  Next: [NEXT_STEP]
  Blockers: [ANY_BLOCKERS]
Energy: 🔴 High Focus Required
```

---

## WORKFLOW 4 — Export Report to Notion

After completing the engagement:

```
Using Notion MCP, create a document under Az Command Center:

Title: "Pentest Report — [CLIENT_NAME] — [DATE]"
Parent: 2f337887-0577-81a0-9b20-ca46e9754137
Icon: 🔴

Content: [FULL REPORT CONTENT from loot/[MISSION]/report.md]

Tag: Confidential, Client Report, [YEAR]
```

---

## WORKFLOW 5 — CVE Watch → Notion

Connect the AutoGPT CVE monitoring to Notion:

```
When AutoGPT detects a new CVE affecting client tech stack:

Using Notion MCP, create urgent task:
- Title: "⚠️ NEW CVE: [CVE_ID] — Affects [CLIENT]"
- Status: "Urgent"
- Notes: "CVSS: [SCORE] | Affected: [PRODUCT_VERSION] | PoC Available: [YES/NO]"
- Due: Tomorrow
- Priority: Urgent (if CVSS >= 9.0) or High (7.0-8.9)

Notify via Dispatch Engine.
```

---

## Notion Page IDs Quick Reference

```
Az Command Center:        2f337887-0577-81a0-9b20-ca46e9754137
AutoBoros Command Center: 23c37887-0577-8107-ad14-f824899b91bd
Task Tracker:             [From your existing setup — search for it]
Agent Activity Log:       [From your existing setup]
Dispatch Log:             [From your existing setup]
```

**To find database IDs:**
```
Using Notion MCP:
Search for "Task Tracker" database
Then: notion-fetch [URL] → look for collection:// data-source-id
```

---

## Automation Script

Add to `scripts/` — runs after each engagement phase:

```bash
#!/usr/bin/env bash
# sync-to-notion.sh — Sync findings to Notion
# Usage: ./scripts/sync-to-notion.sh [MISSION]

MISSION="$1"
FINDINGS="loot/${MISSION}/findings.md"

if [[ ! -f "$FINDINGS" ]]; then
    echo "No findings.md found for mission: $MISSION"
    exit 1
fi

# Count findings by severity
CRITICAL=$(grep -c "^### \[F.*Critical" "$FINDINGS" 2>/dev/null || echo 0)
HIGH=$(grep -c "^### \[F.*High" "$FINDINGS" 2>/dev/null || echo 0)
MEDIUM=$(grep -c "^### \[F.*Medium" "$FINDINGS" 2>/dev/null || echo 0)

echo "Findings: ${CRITICAL} Critical, ${HIGH} High, ${MEDIUM} Medium"
echo "Use Claude Code with Notion MCP to sync these to your Command Center"
echo ""
echo "Prompt:"
echo "---"
cat << PROMPT
Using Notion MCP, update the pentest engagement page for ${MISSION}:
Add status update: ${CRITICAL} Critical, ${HIGH} High, ${MEDIUM} Medium findings found.
Create tasks for all Critical findings in Task Tracker.
PROMPT
```

---

## Notes on Notion MCP Patterns

From your established patterns:

```python
# Creating database pages — ALWAYS use data_source_id not database_id for multi-source DBs
parent = {"data_source_id": "collection://[ID]"}

# Checkbox values
"completed": "__YES__"  # or "__NO__"

# Date properties
"date:Due Date:start": "2026-04-22"
"date:Due Date:is_datetime": 0

# Multi-select (JSON string)
"Tags": '["Security", "Pentest", "Critical"]'

# Properties named 'id' or 'url' need prefix
"userDefined:URL": "https://..."
```

---

*April 2026 | Notion integration — connect red team work to your command center*
