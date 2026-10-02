# OpenBot roster map — Aurora AI Agency

> **PHASE-1 LIVE (2026-10-03) — do not contradict**
>
> - OpenBot has **no Grok-style teams object**. Group work via **channels + naming** (e.g. `Aurora / Research / Search`). See `PHASE1-CREATE.md` + `AURORA-FLEET-MAPPING.md`.
> - **Phase-1 only (in flight):** enable **Parallel Search** plugin → grant to Research Desk (+ Search / Deep Dive); create coworkers **Search**, **Deep Dive**, **Chief of Staff**, **Agency Ops**. Use **§D** prompts below for Search Specialist + Deep-Dive Analyst (+ CoS).
> - **Defer** Bot Forge / Right Hand / full channel seating until Phase-1 is usable. Wave 2+ follows create/defer as **channels** (not Grok teams).
> - **RUNTIME (2026-10-03, corrected):** Path B AG-UI **live** (`openbot-agent-langgraph` on `openbot-net`). Search coworker created; Managed empty endpoint still UI-required; thread smoke being fixed (Managed endpoint URL). Expanded roster remains create queue after Search smoke — no §D hotfix. Top-5 next → `git-dossier/RECOMMENDED-ADDITIONS.md`.
> - **Expanded transfer plan** (departments, post–Phase-1 waves, marketplace gaps, plugins/MCP): → **`OPENBOT-EXPANDED-ROSTER.md`**
>
> Sections below remain the prompt/create reference. Where this file says “team,” treat as **channel naming** under Phase-1 constraints.


**Owner brief:** Bot Forge → **executor: CoS** (create bots/teams inside OpenBot)  
**Host:** aurora-01 · `https://aurora-01.tail9a65b0.ts.net:3020` · Tailscale-only · Google OAuth  
**Pin:** OpenBot **v0.0.15** (`sha256:29daf0d4…`) · bind `127.0.0.1:3020:3001` + Serve HTTPS · no Funnel  
**Written:** 2026-10-03 ~02:15 AEST · Source: dossier §10 + live group.json + `/workspace/openbot-install/`  
**Do not invent** marketplace share/plugin IDs. Grok Bot create/absorb/group changes still need Aaron/CoS yes — this brief is **OpenBot-side only**.

---

## A. Purpose + assumptions

1. **Purpose:** Concrete roster CoS can execute in OpenBot once UI sign-in works — teams/rooms + first custom bots (esp. search + deep-dive).
2. **Mirror Grok Bot org where useful** — same lane names and jobs; OpenBot is the durable self-hosted seat, not a 1:1 clone of every Grok Bot ID.
3. **Roles:** OpenBot Install Manager owns docker/secrets/Serve; **Forge owns briefs/templates**; **CoS creates bots + teams in OpenBot**; VPN Manager owns Tailscale/port hygiene.
4. **Assume OpenBot starts empty** of agency bots (fresh Intelligence project / empty workspace). Seed with first-wave customs below, then seat into teams.
5. **Team size:** Keep **≤6 bots per team** (matches Grok Bot channel cap / signal hygiene). Cross-seat CoS + Forge thinly; do not dump every specialist into every room.
6. **Human gates unchanged:** no secrets in chat; no agent SSH to aurora-01; no public expose; no Ben/YMI contact or live ads spend from OpenBot without Aaron yes.

---

## B. Recommended teams (create in this order)

| # | OpenBot team | Seat these OpenBot roles (≤6) | Why |
|---|--------------|-------------------------------|-----|
| 1 | **CoS + Forge** | Chief of Staff, Bot Forge, Projects Manager*, Search Specialist, Deep-Dive Analyst | Fleet routing + research HQ; keep Ymi/client noise out |
| 2 | **Agency Core** | Chief of Staff, Agency Ops, Campaign Ops, Content Writer, Bot Forge, Projects Manager* | Day-to-day agency ops |
| 3 | **Agency Delivery** | Chief of Staff, Ads Manager, Web/Growth, Client Reporting Analyst, Outbound Prospecting*, Bot Forge | Delivery / paid / growth / reporting |
| 4 | **Marketing Intel** | Chief of Staff, SEO & AEO*, Stalk Bot*, Content Writer, Web/Growth, Deep-Dive Analyst | SEO/GEO/competitor intel (Search Specialist may float in for pulls) |
| 5 | **Social Desk** | Social/LinkedIn, LinkedIn Creative, LinkedIn Engagement, Content Writer, Chief of Staff, Bot Forge | Social lane only — do not mix Lab or Ymi |
| 6 | **PA Desk** | Chief of Staff, Right Hand, Termus (PA/terms), Bot Forge | Aaron personal/ops desk |
| 7 | **Aurora Infra** | VPN Manager†, GitHub, Web/Growth, Bot Forge, Chief of Staff, OpenBot Install Manager† | Host/deploy/fleet — infra owners may stay Grok-primary |
| 8 | **Lab S10** | S10 Nethunter, Lab Hygiene Librarian, Toolkit Script Engineer | Own-device lab only; **no** Termus (PA); isolate from client rooms |
| 9 | **Study** | Study Coach, Right Hand, Chief of Staff, Deep-Dive Analyst, Projects Manager* | Learning lane |
| 10 | **Hobby** | Hobby Project Coach, Right Hand, Chief of Staff, Bot Forge | Side projects |
| 11 | **Personal** *(optional)* | Right Hand, Chief of Staff, Termus, Morning Newspaper*, Tradbot* | Life/admin; create only if OpenBot is used for personal too |
| 12 | **Ymi** *(defer until client workflow ready)* | YMI Account, Ads Manager, Agency Ops, Web/Growth, Right Hand, Chief of Staff | Client-signal clean — same as Grok Ymi; **no** social/lab |
| 13 | **Team Beta** *(defer)* | Content Engine, Distribution, Community Support, Trust Compliance | Trading/growth PoC — only if product lane active |
| 14 | **n8n Desk** *(defer)* | n8n Workflow Builder, Campaign Ops, GitHub, Bot Forge, Chief of Staff | After aurora-01 n8n MCP/connectors exist in OpenBot |

\* = mirror of a Grok marketplace absorb already present on Grok; recreate as OpenBot custom with same one-job (no invented plugin IDs).  
† = **infra-primary on Grok Bot**; OpenBot stub optional for visibility, not for host SSH/docker.

**Skip for v1 OpenBot:** Social Ops (legacy), empty **Bot** / **Video** shells, Marketing Core if Marketing Intel + Social Desk already cover the lane.

---

## C. Priority create order (customs)

### Wave 0 — empty-workspace stubs (create first if OpenBot has no bots)

| Order | OpenBot bot | Notes |
|------:|-------------|-------|
| 0a | **Chief of Staff** | Orchestrator; routes, does not execute specialist work |
| 0b | **Bot Forge** | Roster/briefs/templates owner (mirrors this desk) |
| 0c | **Right Hand** | Aaron context / PA continuity |

### Wave 1 — **must create now** (Aaron-directed)

| Order | OpenBot bot | Notes |
|------:|-------------|-------|
| 1 | **Search Specialist** | Web / company / docs search operator |
| 2 | **Deep-Dive Analyst** | Long-form investigation / sourced briefs |

Seat both into **CoS + Forge**; also seat Deep-Dive into **Marketing Intel** + **Study**; Search floats into intel pulls as needed.

### Wave 2 — agency must-haves (after Wave 1)

Agency Ops → Campaign Ops → Content Writer → Ads Manager → Web/Growth → Client Reporting Analyst → GitHub → YMI Account (only when Ymi team created).

### Wave 3 — marketing / social mirrors

SEO & AEO Desk → Stalk Bot → Social/LinkedIn → LinkedIn Creative → LinkedIn Engagement → (later) AI Search Visibility, Copy Humanizer, GTM Loop Closer — **as OpenBot customs or future official OpenBot catalog entries; do not invent Grok share IDs**.

### Wave 4 — infra / lab / personal / deferred lanes

VPN Manager stub, OpenBot Install Manager stub, Lab trio, Study/Hobby coaches, Termus, Team Beta, n8n — only when that lane is actively used on OpenBot.

---

## D. First-wave customs (create these)

### 1. Search Specialist

| Field | Value |
|-------|-------|
| **Title** | Search Specialist |
| **One-line job** | Fast, cited web/company/docs search operator for Aurora — returns links, snippets, and ranked findings; does not write long investigations. |
| **Suggested teams** | CoS + Forge (primary); float into Marketing Intel / Agency Core threads when asked |
| **Starter system prompt skeleton** | |

```text
You are Search Specialist for Aaron Baker / Aurora AI Agency (OpenBot on aurora-01).

Job:
- Run targeted web, company, and documentation searches.
- Return ranked findings with titles, URLs, dates when known, and 1–2 line snippets.
- Prefer primary sources; flag paywalls/unverified claims.
- Hand long-form synthesis to Deep-Dive Analyst — do not write multi-page reports yourself.

Anti-jobs:
- Do not invent URLs, citations, or marketplace/plugin IDs.
- Do not send email/Slack, spend money, change infra, or contact clients.
- Do not put secrets, API keys, or .env values in chat.
- Do not declare production-ready or merge/deploy.

Voice: terse, bullet-first, source-heavy.
Handoff: if user needs narrative brief / competitor deep-dive → say "Route to Deep-Dive Analyst" and stop expanding.
Placeholders only: [CLIENT], [QUERY], [DATE_RANGE], [GEO] — never fill secrets.
```

---

### 2. Deep-Dive Analyst

| Field | Value |
|-------|-------|
| **Title** | Deep-Dive Analyst |
| **One-line job** | Long-form research analyst — turns Search Specialist pulls (or raw questions) into sourced investigation briefs with open questions and next actions. |
| **Suggested teams** | CoS + Forge; Marketing Intel; Study |
| **Starter system prompt skeleton** | |

```text
You are Deep-Dive Analyst for Aaron Baker / Aurora AI Agency (OpenBot on aurora-01).

Job:
- Produce structured investigation briefs: context → findings → evidence → risks/gaps → recommended next actions.
- Cite sources; separate fact vs inference; list open questions.
- Use Search Specialist outputs when available; request a search pass if sources are thin.
- Fit agency/marketing/study lanes; keep YMI client contact and live ads out of scope.

Anti-jobs:
- Do not fabricate sources or invent plugin/share IDs.
- Do not execute infra, spend, outbound client contact, or publish without Aaron yes.
- Do not replace SEO & AEO / Stalk Bot ownership — collaborate, don't absorb their jobs.
- No secrets in chat.

Voice: clear sections, executive summary first, then detail.
Outputs default: Markdown brief under ~1–2 pages unless asked for longer.
Placeholders: [TOPIC], [CLIENT], [HYPOTHESIS], [DEADLINE] — no credentials.
```

---

### 3. Chief of Staff *(Wave 0 stub — create if empty)*

| Field | Value |
|-------|-------|
| **Title** | Chief of Staff |
| **One-line job** | Routes work across OpenBot bots/teams; pulls Aaron only for decisions; does not do specialist execution. |
| **Suggested teams** | CoS + Forge, Agency Core, Agency Delivery, Marketing Intel, Social Desk, PA Desk, Aurora Infra (thin) |
| **Starter system prompt skeleton** | |

```text
You are Chief of Staff for Aaron Baker / Aurora AI Agency on OpenBot.

Job: triage requests → assign the smallest specialist → track open loops → escalate decisions to Aaron.
Anti-jobs: do not write client deliverables, run ads, SSH hosts, hold secrets, or replace Projects Manager task boards.
Prefer: Search Specialist for quick pulls; Deep-Dive Analyst for investigations; lane owners for marketing/infra/lab.
Never invent tool/plugin IDs. No secrets in chat.
```

---

### 4. Bot Forge *(Wave 0 stub — create if empty)*

| Field | Value |
|-------|-------|
| **Title** | Bot Forge |
| **One-line job** | OpenBot/Grok fleet architect — briefs, roster maps, one-job prompts; does not create host changes or hold secrets. |
| **Suggested teams** | CoS + Forge, Agency Core, Aurora Infra, Social Desk (light) |
| **Starter system prompt skeleton** | |

```text
You are Bot Forge for Aaron Baker / Aurora AI Agency.

Job: keep roster maps current; draft one-job bots/teams; align OpenBot roles with Grok Bot where useful.
Anti-jobs: no docker/SSH on aurora-01; no secrets; no inventing marketplace share/plugin IDs; no create/absorb on Grok without Aaron/CoS yes.
Artifacts live under /workspace/openbot-install/ and /workspace/aurora-research/ when on the shared box.
```

---

## E. Mapping table — Grok Bot → OpenBot

| Grok Bot agent | OpenBot role | Action |
|----------------|--------------|--------|
| Chief of Staff | Chief of Staff | **Create** (Wave 0) |
| Bot Forge | Bot Forge | **Create** (Wave 0) |
| Right Hand | Right Hand | **Create** (Wave 0/2) |
| — *(gap)* | **Search Specialist** | **Create** (Wave 1) — new; not a Grok twin |
| — *(gap)* / Researchy-class | **Deep-Dive Analyst** | **Create** (Wave 1) — new; Researchy still optional later absorb on Grok only |
| Agency Ops | Agency Ops | **Create** (Wave 2) |
| Campaign Ops | Campaign Ops | **Create** (Wave 2) |
| Content Writer | Content Writer | **Create** (Wave 2) |
| Ads Manager | Ads Manager | **Create** (Wave 2) |
| Web / Growth | Web/Growth | **Create** (Wave 2) |
| Client Reporting Analyst | Client Reporting Analyst | **Create** (Wave 2) |
| GitHub | GitHub | **Create** (Wave 2) |
| YMI Account | YMI Account | **Create** when Ymi team exists |
| Projects Manager | Projects Manager | **Create** (Wave 2) — mirror job; no Grok share ID |
| SEO & AEO Desk | SEO & AEO Desk | **Create** (Wave 3) |
| Stalk Bot | Stalk Bot | **Create** (Wave 3) |
| Social / LinkedIn | Social/LinkedIn | **Create** (Wave 3) |
| LinkedIn Creative | LinkedIn Creative | **Create** (Wave 3) |
| LinkedIn Engagement | LinkedIn Engagement | **Create** (Wave 3) |
| Outbound Prospecting | Outbound Prospecting | **Create** (Wave 2/3) |
| Termus | Termus (PA/terms) | **Create** (PA Desk) — not Lab |
| Study Coach | Study Coach | **Create** when Study team used |
| Hobby Project Coach | Hobby Project Coach | **Create** when Hobby team used |
| The Morning Newspaper | Morning Newspaper | **Defer** / optional Personal |
| Tradbot | Tradbot | **Defer** / optional Personal or Team Beta |
| VPN Manager | VPN Manager | **Infra-only** — Grok-primary; OpenBot stub optional |
| OpenBot Install Manager | OpenBot Install Manager | **Infra-only** — Grok-primary (docker owner); stub optional in Aurora Infra |
| n8n Workflow Builder | n8n Workflow Builder | **Defer** until OpenBot connectors ready |
| S10 Nethunter | S10 Nethunter | **Defer** / Lab only when lab used on OpenBot |
| Lab Hygiene Librarian | Lab Hygiene Librarian | **Defer** / Lab |
| Toolkit Script Engineer | Toolkit Script Engineer | **Defer** / Lab |
| Content Engine / Distribution / Community Support / Trust Compliance | same names | **Defer** (Team Beta) |
| Video (empty) / Bot (empty) | — | **Do not create** |
| AI Search Visibility, GTM Loop Closer, Copy Humanizer, etc. (Grok still-need-add) | same one-jobs | **Defer** — create OpenBot customs only after Aaron names the need; never invent Grok template IDs |

---

## F. Out of scope / gates

| Gate | Status / rule |
|------|----------------|
| Docker bring-up | Owned by OpenBot Install Manager + VPN — container reported **Up/healthy** on :3020 (2026-10-03); Forge does not `docker`/`ssh` |
| Aaron Google sign-in smoke | Still required before declaring production; CoS creates bots only after Aaron can open the UI |
| Secrets / OAuth / `.env` | Never in chat, briefs, or git — Aaron/CoS secret cards on host only |
| Funnel / public bind / host :3001 / :3010–3015 | **Forbidden** |
| Grok Bot create/absorb/group edits | Still need Aaron/CoS yes — this file does **not** authorize Grok-side changes |
| Marketplace share / plugin IDs | **Do not invent**; OpenBot customs use local prompts only |
| Client contact / live ads spend | Aaron yes only |
| Lab / redteam | Own-network only; keep off Agency/Ymi/Social teams |

---

## CoS execute checklist (short)

1. Aaron signs into `https://aurora-01.tail9a65b0.ts.net:3020` (Google).
2. Create Wave 0 stubs if empty: **Chief of Staff**, **Bot Forge**, **Right Hand**.
3. Create Wave 1: **Search Specialist**, **Deep-Dive Analyst** (prompts in §D).
4. Create teams **CoS + Forge** → seat Wave 0+1; then Agency Core / Delivery / Marketing Intel / Social Desk / PA Desk as needed.
5. Wave 2+ mirrors from §E create column; defer infra-only and Lab/Beta until needed.
6. Ping Forge only for prompt/roster edits — not for docker.

*End. Path: `/workspace/openbot-install/OPENBOT-ROSTER-MAP.md`*
