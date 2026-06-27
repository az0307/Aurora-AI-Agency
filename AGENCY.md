# Aurora AI Agency — Agency & Clients

> The single reference for **who Aurora is**, **what we sell**, and **who we deliver for**.
> Technical per-subsystem documentation lives in [`CLAUDE.md`](./CLAUDE.md); this file is the
> business-facing definition.

---

## 1. What Aurora AI Agency is

**Aurora AI Agency** is the public-facing, client-delivery arm of the Ouroboros group. We are an
AI-native automation and software agency based in **Australia**. We design, build, and operate
production systems for clients — websites, lead-generation funnels, AI chatbots, multi-agent
automation, and security tooling — and we run our own products that power that delivery.

"AI-native" means automation is the default, not an add-on: every engagement is wired into our own
orchestration engine (AutoBoros) so that agents do the repetitive work and humans approve the
judgement calls.

### Positioning in one line

> We build the automated, AI-driven systems a modern small-to-mid business needs to capture leads,
> serve customers, and run operations — then we keep them running.

### Where Aurora sits in the group

```
Ouroboros Foundation Ltd Pty            (AU holding company)
├── Ouroboros AI Innovations Pte Ltd    (Singapore — R&D)
├── Ouroboros Technologies LLC          (Delaware — US market / IP)
└── SPVs per vertical
    ├── Aurora AI Agency   ← PUBLIC FACE — client delivery (this repo)
    ├── AutoBoros          ← ENGINE — n8n orchestration, MCP mesh, multi-agent
    ├── UltronOmega / HexStrike ← SECURITY — red team, pentest, Kali integration
    └── Meta Umbrella v3.0 ← GOVERNANCE — SOPs, compliance, legal
```

- **Brand / web:** [autoboros.ai](https://autoboros.ai) · [autoborosai.com.au](https://autoborosai.com.au)
- **Primary contact:** Aaron Baker — aaron221048@gmail.com

---

## 2. What we offer (service lines)

| # | Service line | What the client gets | Built on |
|---|--------------|----------------------|----------|
| 1 | **Lead-gen websites** | A fast, SEO-ready static or dynamic site with an online enquiry form that pipes leads straight into a CRM/automation. | Cloudflare Pages, Workers, n8n |
| 2 | **AI chatbots & customer flows** | Branded chatbot (web / Messenger / Instagram) trained on the client's voice, with FAQ, lead capture, and human handoff. | ManyChat, n8n, LLM agents |
| 3 | **Multi-agent automation** | Back-office automation run on the L0–L4 approval ladder — agents draft, humans approve, operations get faster. | AutoBoros (FastAPI + n8n + MCP) |
| 4 | **Operator dashboards** | Real-time cockpit/dashboard to watch jobs, approvals, audit trail, and analytics. | React 19 cockpit, Nexus dashboard |
| 5 | **Security testing** | Authorised red-team / pentest engagements with live Kali tooling and structured reporting. | HexStrike AI |
| 6 | **Client portal** | A login where each client sees their jobs, deliverables, and invoices in one place. | Next.js client-portal |

---

## 3. Our clients

> Status legend: **Live** = in production · **In delivery** = actively being built · **Onboarding** = signed/scoping.

### Y.M.I Roofing — *In delivery*

| | |
|---|---|
| **Contact** | Ben Breheny (Director) |
| **Business** | Melbourne roof tiling specialist — new roofs, repairs, re-bedding & pointing, ridge capping, inspections |
| **Registration** | ACN 695 710 055 (ABN to be confirmed) |
| **Vertical** | Local trades |
| **Engagement** | Lead-generation website + ops automation package |

**Deliverables**
- Production website — [`ymiroofing.com.au`](https://github.com/az0307/ymiroofing.com.au) repo (deployable site) · design source in [`ymi-roofing/site`](./ymi-roofing/site).
- Lead-capture pipeline: website form → Cloudflare Worker proxy → n8n → Google Sheets CRM + Twilio SMS.
- Review machine, missed-call follow-up, maintenance reminders (n8n workflows in the `ymiroofing` repo).
- ManyChat chatbot spec, SEO tracking setup, invoice + welcome-letter templates ([`ymi-roofing/ops`](./ymi-roofing/ops)).

**Open before go-live:** replace the website `WEBHOOK_URL` placeholder with the deployed Worker URL,
set the n8n secret, point DNS, confirm ABN + BPC registration number, supply real roofing photos.

### Evermystic — *In delivery*

| | |
|---|---|
| **Contact** | Stefan (brand owner) |
| **Business** | Brand / content business (mystical / lifestyle brand) |
| **Vertical** | Content & e-commerce / DTC brand |
| **Engagement** | AI brand-voice chatbot + automated content & ops SOPs |

**Deliverables**
- Brand-voice + policy extraction, FAQ generation in Stefan's tone, welcome flow + fallback copy,
  intent keyword map — run as a 6-phase SOP on the AutoBoros cockpit (seeded as the `Evermystic`
  client in [`autoboros/backend/app/routers/seed.py`](./autoboros/backend/app/routers/seed.py)).
- Evermystic Haiku Executor tool ([`evermystic/tools`](./evermystic/tools)).

> Evermystic is the canonical demo/reference client used to seed the AutoBoros cockpit — it is both a
> real engagement and the showcase dataset for the product.

### Prospective / template

- **Pentest prospects** — the HexStrike external-network pentest proposal
  ([`hexstrike-ai/proposals`](./hexstrike-ai/proposals)) is a reusable template (placeholder client
  "Acme Corp Pty Ltd", 7-day PTES engagement, $8,000 AUD + GST). Replace client details per engagement.

---

## 4. Internal products (what powers delivery)

These are Aurora's own systems, not client deliverables. They live across several repos.

| Product | Repo / path | Role |
|---------|-------------|------|
| **AutoBoros** | [`autoboros/`](./autoboros) · [`AutoBoros.AI-`](https://github.com/az0307/AutoBoros.AI-) | The automation engine — FastAPI + n8n + MCP + React cockpit, L0–L4 job ladder. |
| **AutoBoros cockpit** | [`autoboros/cockpit`](./autoboros/cockpit) · [`autoboros-cockpit/`](./autoboros-cockpit) | Operator UI for the engine. |
| **Nexus dashboard** | [`autoborosai-dashboard`](https://github.com/az0307/autoborosai-dashboard) | Next.js enterprise dashboard for monitoring multi-agent systems. |
| **autoborosai.com** | [`AutoborosAi.com`](https://github.com/az0307/AutoborosAi.com) | Public marketing site + app (React + Hono). |
| **HexStrike AI** | [`hexstrike-ai/`](./hexstrike-ai) | Red-team platform with live Kali integration. |
| **Gastown** | [`gastown/`](./gastown) | Internal CLI — scaffolds projects from natural language. |
| **Client portal** | [`client-portal/`](./client-portal) | Next.js + Clerk portal where clients see jobs / deliverables / invoices. |
| **Creator Hub** | [`creator-hub`](https://github.com/az0307/creator-hub) | Agency creator/automation toolkit (n8n + Docker). |
| **Meta Automation Hub** | [`meta-automation-hub`](https://github.com/az0307/meta-automation-hub) | Governance / SOP layer (Ω6). |
| **KaliShare / kali-backup-system** | [`KaliShare`](https://github.com/az0307/kalishare) · [`kali-backup-system`](https://github.com/az0307/kali-backup-system) | Security home-lab tooling and backups. |

---

## 5. How an engagement runs

1. **Intake & scope** — capture the client's goal, define the deliverable, agree price.
2. **Build** — work happens in the client's repo (or an Aurora subsystem), automated where possible.
3. **Wire automation** — connect the deliverable into AutoBoros / n8n so leads and ops flow without manual steps.
4. **Launch** — deploy (Cloudflare Pages / Vercel / Fly.io), point DNS, set secrets, verify the funnel end-to-end.
5. **Operate** — monitor via the cockpit / Nexus dashboard; client sees status in the client portal.

---

*Maintained by Aurora AI Agency. Last reviewed 2026-06-27. If a client or product changes status,
update this file and the corresponding repo README.*
