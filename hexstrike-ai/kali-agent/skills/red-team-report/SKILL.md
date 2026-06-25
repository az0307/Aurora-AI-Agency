---
name: red-team-report
description: >
  Generate professional penetration testing and red team engagement reports
  from structured findings data. Use this skill whenever the user mentions
  pentest report, red team report, security assessment report, vulnerability
  report, executive summary for pentest, technical findings report, remediation
  report, compliance report, security audit deliverable, engagement report,
  final deliverable, or "write up the findings". Also trigger for: report
  template, finding write-up, risk matrix, CVSS summary table, attack
  narrative, attack chain documentation, remediation roadmap, re-test
  recommendations, or any request to produce a written deliverable from
  security testing data. This is the final phase of a pentest engagement —
  trigger after post-exploit completes, or standalone when the operator
  has findings data and needs a formatted report.
  Can produce Word (.docx), PDF, Markdown, or HTML report formats.
compatibility:
  tools: [bash, python]
  mcps: [hexstrike]
  skills: [recon-osint, vuln-analysis, exploit-dev, post-exploit, ai-agent-orchestration, docx, pdf]
---

# RedTeamReport Skill

## Overview

Generates professional penetration testing reports from structured engagement
data. Produces both executive summaries (for leadership) and technical details
(for remediation teams). Includes risk matrices, attack path narratives,
finding write-ups with evidence, and prioritized remediation roadmaps.

## Prerequisites

- Engagement data from one or more prior phases (recon, vuln, exploit, post-exploit)
- Engagement metadata: client name, scope, dates, methodology, tester names
- For .docx output: use the `docx` skill (read its SKILL.md first)
- For .pdf output: use the `pdf` skill (read its SKILL.md first)

## Core Instructions

### Step 1 — Collect All Engagement Data

Ingest structured output from prior skills:
```
/tmp/pentest/{target}/recon_output.json
/tmp/pentest/{target}/vuln_output.json
/tmp/pentest/{target}/exploit_output.json
/tmp/pentest/{target}/post_exploit_output.json
/tmp/pentest/{target}/exploitation_log.txt
```

If data is incomplete, work with what's available. Flag missing sections.

### Step 2 — Report Structure

Generate the report with this standard structure:

```
1.  Cover Page
    - Report title, client name, engagement dates
    - Classification: CONFIDENTIAL
    - Assessor: {tester_name} / {company}

2.  Executive Summary (1-2 pages)
    - Engagement overview (scope, methodology, dates)
    - Overall risk rating (Critical / High / Medium / Low)
    - Key findings summary (top 3-5 findings in business language)
    - Strategic recommendations (3-5 bullet points)
    - Attack path narrative (non-technical story of the compromise)

3.  Methodology
    - Testing approach (PTES / OWASP / NIST / MITRE ATT&CK)
    - Tools used (from engagement data)
    - Scope and limitations
    - Rules of engagement summary

4.  Risk Summary
    - Finding severity distribution (table + chart data)
    - Risk matrix (likelihood × impact)
    - CVSS score distribution

5.  Detailed Findings
    For each finding (sorted by severity):
    ┌─────────────────────────────────────┐
    │ Finding ID: VULN-001                │
    │ Title: Remote Code Execution in...  │
    │ Severity: Critical (CVSS 9.8)      │
    │ CVE: CVE-2024-XXXXX                │
    │ Affected Asset: blog.example.com    │
    │                                     │
    │ Description:                        │
    │ [Technical explanation]             │
    │                                     │
    │ Impact:                             │
    │ [Business impact in plain English]  │
    │                                     │
    │ Evidence:                           │
    │ [Screenshots, command output]       │
    │                                     │
    │ Remediation:                        │
    │ [Specific fix steps]               │
    │                                     │
    │ References:                         │
    │ [CVE link, vendor advisory, CWE]   │
    └─────────────────────────────────────┘

6.  Attack Path Narrative
    - Step-by-step story of the full attack chain
    - Visual: attack flow diagram (Mermaid or text-based)
    - Timeline of exploitation activities

7.  Remediation Roadmap
    - Immediate (0-7 days): Critical findings
    - Short-term (1-4 weeks): High findings
    - Medium-term (1-3 months): Medium findings
    - Long-term (3-6 months): Hardening and architecture

8.  Appendices
    - A: Full tool output references (file paths)
    - B: Scope documentation
    - C: Methodology details
    - D: Re-test recommendations and timeline
```

### Step 3 — Executive Summary Writing Guidelines

The executive summary is the most-read section. Write it for a non-technical audience:

- Lead with business impact, not technical details
- Use risk language: "An attacker could access customer payment data"
- Quantify where possible: "3 of 5 web applications had critical vulnerabilities"
- Include the attack narrative as a story: "Starting from the public internet, 
  the assessor was able to gain administrative access to the customer database
  within 4 hours, demonstrating that a motivated attacker could achieve the same"
- End with clear, actionable strategic recommendations

### Step 4 — Finding Write-Up Quality Standards

Each finding must include:
- **Reproducible steps** — another tester can verify
- **Evidence** — output, screenshots, or logs (reference file paths)
- **Business context** — why this matters beyond the CVSS score
- **Specific remediation** — not just "patch it" but exact versions/configs
- **CWE mapping** — Common Weakness Enumeration reference
- **MITRE ATT&CK mapping** — technique IDs where applicable

### Step 5 — Output Generation

**For Markdown (.md) — fastest, use for drafts:**
Generate directly as structured Markdown.

**For Word (.docx) — client deliverable:**
Load the `docx` skill SKILL.md, then generate using python-docx:
- Professional formatting with heading styles
- Table of contents
- Finding severity color coding
- Page numbers and headers
- Cover page with client branding placeholder

**For PDF — final sealed deliverable:**
Load the `pdf` skill SKILL.md, then generate from the .docx or directly.

**For HTML — interactive version:**
Generate as single-page HTML with:
- Collapsible finding sections
- Severity filter controls
- Attack path diagram (Mermaid.js)

## HexStrike MCP Integration

```
Tool: generate_report
Args: {
  "findings": [{finding_objects}],
  "target": "example.com",
  "scope": "External network penetration test"
}
Returns: { report_markdown: "...", report_path: "/tmp/pentest/.../report.md" }
```

Uses GLM-4.5 on HexStrike for initial draft generation, then Sonnet for
editorial review and executive summary refinement.

## Attack Path Diagram Template

Generate with Mermaid syntax:
```mermaid
graph LR
    A["Internet"] -->|"RCE CVE-2024-XXX"| B["web01 www-data"]
    B -->|"SUID privesc"| C["web01 root"]
    C -->|"SSH key reuse"| D["db01 admin"]
    D -->|"DB access"| E["Customer PII"]
    
    style A fill:#e0e0e0
    style B fill:#ff9800
    style C fill:#f44336
    style D fill:#f44336
    style E fill:#9c27b0
```

## Output Format

The skill produces one or more files:

```
/tmp/pentest/{target}/reports/
├── {target}_pentest_report.md        # Full Markdown report
├── {target}_pentest_report.docx      # Word deliverable (if requested)
├── {target}_pentest_report.pdf       # PDF deliverable (if requested)
├── {target}_executive_summary.md     # Standalone exec summary
└── {target}_remediation_roadmap.md   # Standalone remediation plan
```

## Quality Checklist (Review Before Delivery)

- [ ] Executive summary readable by non-technical leadership
- [ ] All findings have reproducible steps and evidence references
- [ ] CVSS scores verified and consistent
- [ ] Remediation is specific (versions, configs, not just "patch")
- [ ] Attack path narrative tells a coherent story
- [ ] No actual sensitive data from target in report (proof only)
- [ ] Engagement scope and methodology documented
- [ ] Remediation roadmap has realistic timelines
- [ ] Report classified as CONFIDENTIAL
- [ ] Spell-checked and professionally formatted
- [ ] CWE and MITRE ATT&CK mappings included where applicable
- [ ] Report saved to /tmp/pentest/{target}/reports/
- [ ] Operator has reviewed report before client delivery
