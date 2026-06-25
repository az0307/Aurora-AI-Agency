# PLAYBOOK: ThreatGPT — AI Threat Modeling with STRIDE-GPT
# April 2026 Red Team Stack
# Tool: mrwadams/stride-gpt | Web UI: localhost:8501
# Use: Pre-engagement planning + Post-engagement reporting

---

## What Threat Modeling Adds to a Pentest

Most pentesters skip threat modeling — they go straight to scanning.
This is a mistake. Threat modeling before you start:

1. **Focuses your attack surface** — you know what assets matter most
2. **Reveals architectural weaknesses** before touching a single tool
3. **Improves report quality** — findings map to pre-agreed threat scenarios
4. **Justifies your findings** — client can't argue a finding is "low risk"
   when it was already identified as a critical threat pre-engagement

STRIDE-GPT automates the threat model generation in ~5 minutes.
A manual threat model takes a senior consultant 2-4 hours.

---

## STRIDE Methodology Refresher

```
S — Spoofing         Who/what is claiming to be something it's not?
T — Tampering        What data or code can be modified by an attacker?
R — Repudiation      Can attackers deny actions they took?
I — Info Disclosure  What sensitive data can be accessed without auth?
D — Denial of Service What can be crashed, throttled, or exhausted?
E — Elevation of Privilege What can be done without proper authorization?
```

---

## Setup

```bash
cd stride-gpt
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY=sk-...
# OR
export ANTHROPIC_API_KEY=sk-ant-...

# Launch UI
streamlit run app.py
# Opens: http://localhost:8501

# Or run headless for MCP integration:
python3 -m stride_gpt_mcp
```

**Docker (via our docker-compose.yml):**
```bash
docker compose up -d stride-gpt
# UI at http://localhost:8501
```

---

## PHASE 1 — PRE-ENGAGEMENT THREAT MODEL

Run this BEFORE the active pentest begins.
Input comes from: client kickoff call + public OSINT.

### Input Template

```
Application Name: [APP_NAME]
Application Type: [Web App / Mobile App / API / Microservices / Internal Tool]

Tech Stack:
  Frontend: [React / Vue / Angular / None]
  Backend:  [Node.js / Django / Laravel / Spring Boot / .NET]
  Database: [PostgreSQL / MySQL / MongoDB / Redis / Elasticsearch]
  Auth:     [JWT / Sessions / OAuth2 / SAML / API Keys]
  Cloud:    [AWS / GCP / Azure / On-prem / Hybrid]

Internet-facing: [Yes / No / Partially]

Data processed:
  - [PII — name, email, DOB]
  - [Financial — credit cards, bank details]
  - [Health — medical records]
  - [Credentials — passwords, tokens]
  - [IP — proprietary business data]

Authentication: [MFA enabled? / SSO? / Password policy?]

Key integrations: [Stripe / Twilio / Salesforce / Active Directory / etc.]

Known security controls: [WAF / IDS / SIEM / DLP / etc.]
```

### Claude Code Invocation

```
Using stride-gpt MCP, generate a full STRIDE threat model for:

Application: [APP_NAME]
Tech: [STACK]
[paste full input template]

For each STRIDE category, produce:
- Specific threats relevant to this architecture
- CVSS estimated severity
- Likelihood (High/Medium/Low)
- Suggested mitigations
- Pentest validation approach (how I'll test this)

Save output to: loot/[MISSION]/threat_model_pre.md
```

### Expected Output Structure

```markdown
# STRIDE Threat Model — [APP_NAME]
Generated: [DATE] | Pre-engagement

## S — SPOOFING THREATS

### S1: JWT Token Forgery
**Severity:** High | **CVSS:** 8.1
**Description:** If JWT signing secret is weak or algorithm is 'none',
attacker can forge tokens for any user account.
**Likelihood:** Medium (common in Node.js apps with default configs)
**Mitigation:** Strong secret (256-bit), enforce RS256/ES256, validate iss/aud
**Pentest Test:** Modify JWT alg field to 'none'; try weak secret brute-force

### S2: OAuth State Parameter Missing
**Severity:** High | **CVSS:** 7.4
**Description:** CSRF on OAuth flow allows account takeover via redirect
**Likelihood:** Medium
**Mitigation:** Implement and validate state parameter
**Pentest Test:** Initiate OAuth, intercept, remove state, observe behavior

## T — TAMPERING THREATS
[...]
```

---

## PHASE 2 — DURING-PENTEST THREAT CORRELATION

As you find vulnerabilities, validate them against the threat model.

### Claude Code Prompt

```
I found this vulnerability during the pentest:
[VULN_DESCRIPTION]
[EVIDENCE]

Check: does this match any of our pre-engagement STRIDE threats?
Read: loot/[MISSION]/threat_model_pre.md

If match found:
- Note which threat scenario was confirmed
- Update severity if actual impact differs from predicted
- Document: threat ID → finding ID mapping

If no match found:
- Add as a NEW threat to the model (we missed it)
- Note why our model didn't anticipate it

Update: loot/[MISSION]/threat_model_correlation.md
```

---

## PHASE 3 — POST-ENGAGEMENT THREAT MODEL UPDATE

After all testing is complete, update the threat model with findings.

### Claude Code Prompt

```
Using stride-gpt MCP, generate a post-engagement threat model update.

Pre-engagement model: loot/[MISSION]/threat_model_pre.md
Confirmed findings: loot/[MISSION]/findings.md
False negatives: threats we predicted but didn't find (good controls)
False positives: threats we found that weren't predicted (gaps)

Generate:
1. VALIDATED THREATS — confirmed by pentest evidence
2. MITIGATED THREATS — present but controls working
3. NEW THREATS — not in original model, discovered during test
4. COVERAGE GAPS — threats we couldn't test (time, scope, etc.)

Save: loot/[MISSION]/threat_model_final.md
This becomes Section 3 of the final pentest report.
```

---

## PHASE 4 — CLIENT DELIVERABLE

The threat model makes your report stand out from generic pentest reports.

### Report Structure with Threat Model

```
1. Executive Summary
2. Threat Model (STRIDE) — pre-agreed threat scenarios
   2a. Validated threats (found → HIGH PRIORITY FIX)
   2b. Mitigated threats (controls working → MAINTAIN)
   2c. New threats (not anticipated → RISK ACCEPTED or FIX)
3. Technical Findings (matched to threat model where possible)
4. Risk Register (threat × likelihood × impact matrix)
5. Remediation Roadmap
6. Conclusion
```

---

## Quick Threat Model Templates

### Web Application (Standard)

```bash
agpt_threat_model_prompt="
App: B2B SaaS web application
Stack: React frontend, Node.js/Express backend, PostgreSQL, JWT auth
Cloud: AWS (EC2, RDS, S3, CloudFront)
Internet-facing: Yes (public)
Data: Customer PII, financial transaction records
Auth: Username/password + JWT, no MFA currently
Integrations: Stripe payments, SendGrid email, Twilio SMS
Users: ~50,000 business customers + their end users (~500k)
Known controls: CloudFlare WAF, AWS GuardDuty
"
```

### Internal Corporate App

```bash
agpt_threat_model_prompt="
App: Internal HR portal
Stack: .NET Core, MSSQL, Active Directory auth (SAML)
Network: Internal only (no internet exposure)
Data: Employee records, salary, performance reviews, medical info
Auth: SSO via AD, no MFA for internal users
Integrations: Active Directory, SharePoint, email
Users: 500 internal employees
Known controls: Network segmentation, AD group policies
"
```

### API / Microservices

```bash
agpt_threat_model_prompt="
App: REST API serving mobile apps (iOS + Android)
Stack: Python/FastAPI, MongoDB, Redis cache, API key auth
Cloud: GCP (GKE, Cloud SQL, Cloud Storage)
Internet-facing: Yes (public API)
Data: User location, health metrics, personal preferences
Auth: API keys + OAuth2 for user sessions
Integrations: Google Maps API, Apple Health, Fitbit
Users: 2M mobile app users
Known controls: Rate limiting, API gateway (Kong)
"
```

---

## Integration: ThreatGPT + VulnGPT + HexStrike

Full intelligence-led workflow:

```
Pre-engagement:
  stride-gpt → threat model → identifies highest-risk components

Reconnaissance:
  hexstrike → confirms tech stack matches threat model assumptions
  vulngpt → CVE intelligence on confirmed tech versions

Testing:
  hexstrike + kali-mcp → test each STRIDE threat systematically
  pentestgpt → autonomous coverage of remaining attack surface

Reporting:
  stride-gpt → final threat model with findings correlated
  skills/report-generator.md → assemble full report
```

---

## Cost Notes

STRIDE-GPT runs a single threat model generation per invocation.
Typical cost per model:
- ~5k-15k tokens input + ~3k-8k tokens output
- Sonnet: ~$0.05-0.10 per model
- Opus: ~$0.25-0.50 per model (better narrative quality)

Generate pre-engagement with Sonnet, final post-engagement with Opus.
Total threat modeling cost per engagement: ~$0.30-1.00.

---

*April 2026 | Threat model first — attack second — report with evidence*
