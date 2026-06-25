# SKILL: report-generator
# Generates professional penetration test reports from loot/ findings
# Triggered when: "generate report", "write report", "document findings"

## Trigger Phrases
- "generate report for [mission]"
- "write up the findings"
- "create pentest report"
- "document what we found"
- "export findings to report"
- "prepare client deliverable"

---

## WORKFLOW A — Full Automated Report Generation

```bash
# Step 1: Initialize report from template
./scripts/generate-report.sh [MISSION_NAME]
# Creates: loot/[MISSION]/report.md (skeleton)
# Creates: loot/[MISSION]/REPORT_PROMPT.md (Claude Code prompt)

# Step 2: In Claude Code — run the generated prompt
# (reads findings.md, mission.md, threat model, scan results)
# Populates all sections automatically
```

**What the automated pass produces:**
- Executive summary (board-level language, no jargon)
- Risk rating with justification
- Scope confirmation from mission.md
- STRIDE threat model correlation (pre vs post-engagement)
- Technical findings (each with CVSS, PoC steps, fix code)
- Risk register (findings × likelihood × impact)
- Remediation roadmap with timeline and effort estimates
- Verification scripts (automated re-test proof of fix)

---

## WORKFLOW B — Section-by-Section with Claude Code

For full control over each section:

### Executive Summary

```
Write the executive summary for this pentest report.
Audience: non-technical board members.
Data: loot/[MISSION]/findings.md + loot/[MISSION]/mission.md

Requirements:
- 200-300 words maximum
- No technical jargon (no CVE numbers, no "SQL injection")
- Lead with: overall risk rating and one-sentence bottom line
- 2nd paragraph: what an attacker could actually DO (business terms)
  e.g. "steal customer payment data" not "exploit SQLi in /api/login"
- 3rd paragraph: top 3 positive security observations
- End with: urgency statement tied to specific deadline/risk

Risk rating: [CRITICAL/HIGH/MEDIUM/LOW] based on:
  Critical: active exploitation possible, data at risk NOW
  High: exploitation likely within days, significant data risk
  Medium: exploitation requires skill/time, moderate impact
  Low: theoretical risk, minor impact

Output: section 1 of loot/[MISSION]/report.md
```

### Technical Finding Write-Up

```
Write a professional finding write-up for this vulnerability.
Format: follows loot/REPORT_TEMPLATE.md Section 5 structure.

Finding data:
  Title: [FROM findings.md]
  Asset: [FROM findings.md]
  CVSS: [FROM findings.md]
  Tool: [FROM findings.md]
  Screenshot: [PATH]
  Notes: [RAW NOTES FROM findings.md]

Requirements:
  Description: 2-3 sentences, explain root cause to developer who wrote it
  Business Impact: quantify if possible ($, customer records, systems affected)
  Steps to Reproduce: exact HTTP request or command sequence
  Evidence: reference screenshot path
  Remediation (immediate): specific code or config fix — not generic advice
  Remediation (long-term): architectural recommendation
  Verification: copy-paste test script that confirms fix
  References: OWASP + CWE + CVE if applicable

Write the finding clearly enough that a junior developer
can understand and fix it without asking follow-up questions.
```

### Risk Register

```
Build the risk register for this engagement.

Findings: [PASTE findings.md content]

For each finding, assess:
  Likelihood: probability attacker exploits this in next 12 months
    High: known exploit, automated tool available
    Medium: requires skill but motivation exists
    Low: complex, niche knowledge required

  Business Impact:
    High: data breach, ransomware, compliance violation
    Medium: service degradation, reputational damage
    Low: information disclosure, minor functionality loss

  Risk Score = Likelihood × Impact
    Critical = High × High
    High = High × Medium OR Medium × High
    Medium = Medium × Medium OR Low × High
    Low = Low × Low or Low × Medium

Output: markdown table sorted by risk score descending
Include: recommended owner (Dev/SecOps/IT/CISO) and target date
```

### Remediation Roadmap

```
Create a prioritized remediation roadmap.

Findings: [LIST with severity and effort estimate]
Client context: [TECH STACK, TEAM SIZE if known]

Structure:
  IMMEDIATE (this week):
    - Critical findings only
    - Specific actions with effort estimate
    - Who owns it (role, not name)

  SHORT-TERM (30 days):
    - High findings
    - Architectural improvements triggered by findings

  MEDIUM-TERM (90 days):
    - Medium findings
    - Security program improvements

  ONGOING:
    - Low findings
    - Monitoring and detection improvements

For each action: be specific enough that a developer can start
immediately without scheduling a meeting.
```

---

## WORKFLOW C — Report Quality Check

After generating the report, run this quality check:

```
Review this pentest report for quality issues:
[PASTE FULL REPORT]

Check:
1. Executive summary: Is it free of jargon? Could a CEO understand it?
2. Every finding: Does it have all required fields?
   (CVSS, steps to reproduce, evidence reference, specific fix)
3. Remediation: Is every fix actionable, or is any advice generic?
   Flag any: "implement input validation" (too vague)
   Keep any: "add parameterized query: cursor.execute(query, (param,))"
4. Tone: Professional throughout? No casual language?
5. Consistency: Do severity ratings match the risk register?
6. Missing: Is anything referenced but not provided?
   (missing screenshots, evidence paths that don't exist)

Output: list of specific edits needed before delivery
```

---

## WORKFLOW D — Findings Severity Calibration

Before finalizing, calibrate severity ratings:

```
Review these finding severity ratings for accuracy and consistency.
Use CVSS v3.1 base score as the primary metric.

[PASTE FINDINGS LIST WITH ASSIGNED SEVERITIES]

For each finding, verify:
  - CVSS vector string is correct
  - Base score matches assigned severity label
    9.0-10.0 = Critical
    7.0-8.9  = High
    4.0-6.9  = Medium
    0.1-3.9  = Low

Re-rate any that are miscalibrated.
Note any where business context changes the effective risk
(e.g. a Medium CVE on a payment processing endpoint = High effective risk).

Output: corrected severity list with justification for any changes
```

---

## Report Formatting Conventions

```markdown
# Section hierarchy:
# 1. Executive Summary         (H1)
## Technical Findings           (H2)
### Finding 1: [TITLE]          (H3)
#### Steps to Reproduce         (H4)

# Severity labels: always bold + color-coded
**🔴 Critical** / **🟠 High** / **🟡 Medium** / **🟢 Low**

# Code blocks: always language-tagged
```http
POST /api/login HTTP/1.1
```

# Evidence references: always relative paths
![SQL Injection Proof](screenshots/f1_sqli_auth_bypass.png)

# CVSS vectors: always in inline code
CVSS v3.1: `AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H` = 10.0 Critical
```

---

## Export Options

```bash
# Markdown → PDF (via pandoc)
pandoc loot/[MISSION]/report.md -o loot/[MISSION]/report.pdf \
  --pdf-engine=wkhtmltopdf \
  --css=docs/report.css

# Markdown → DOCX (for client edits)
pandoc loot/[MISSION]/report.md -o loot/[MISSION]/report.docx

# Encrypt for delivery
gpg --symmetric --cipher-algo AES256 loot/[MISSION]/report.pdf
# Send .gpg file — share password via separate channel (phone)
```

---

## Cost Notes

- Executive summary: ~3k tokens Opus output → ~$0.23
- 10-finding technical report: ~15k tokens Opus output → ~$1.13
- Full report (all sections): ~$1.50–3.00 total
- Re-generation after feedback: ~$0.50–1.00

Use Sonnet for first draft, Opus for final polish pass:
- Sonnet draft: $0.40
- Opus polish: $0.80
- Total: $1.20 vs $3.00 Opus-only
