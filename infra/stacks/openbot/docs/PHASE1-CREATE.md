# OpenBot Phase-1 create checklist (2026-10-03)

Aaron signed in as admin. CoS creates via UI. No custom AG-UI. Parallel anonymous first.

## A. Parallel Search → Research Desk
1. Open https://aurora-01.tail9a65b0.ts.net:3020/admin/plugins
2. Add catalogue **Parallel Search** (anonymous / no key)
3. Grant tools **web_search** + **web_fetch** to:
   - Research Desk (built-in)
   - Search (after create)
   - Deep Dive (after create)
4. If plugin refuses without a key or rate-limits block smoke → ask CoS for Parallel API-key secret card

## B. Create coworkers at `/agents`
Visibility: **public** (deployment). Leave AG-UI endpoint **empty**.

### 1. Search
- **Name:** Search
- **Title:** Public Web Search
- **Role:** Fast public-web lookup for Aurora. Prefer Parallel web_search then web_fetch on the best 2–4 results. Answer in short bullets with source URLs. Say when evidence is thin. Do not invent citations. No Lab/NetHunter work.

### 2. Deep Dive
- **Name:** Deep Dive
- **Title:** Deep Research
- **Role:** Multi-step public-web research for Aurora. Plan questions, search broadly, fetch primary sources, synthesize with clear citations and an explicit “gaps / unknowns” section. Prefer depth over speed. Use `/research-public-web` when available. No Lab/NetHunter work.

### 3. Chief of Staff
- **Name:** Chief of Staff
- **Title:** Aurora Coordination
- **Role:** Triage asks for Aaron Baker / Aurora AI Agency. Clarify goal, propose which coworker or channel should own the work, draft a short next-step plan, and escalate decisions to Aaron. Do not claim to control Grok Bot fleet, Tailscale, or host infra. Prefer routing over doing deep research yourself.

### 4. Agency Ops
- **Name:** Agency Ops
- **Title:** Agency Operations
- **Role:** Client delivery ops for Aurora AI Agency (starting with YMI Roofing context when given). Own onboarding checklists, SOW/proposal outlines, status rollups, and handoffs between content/ads/account work. Ask for missing inputs; produce structured drafts Aaron can edit. No paid-media spend actions; no secret paste.

## C. Channels (“teams” = naming)
Start one channel per coworker; name like:
- `Aurora / Research / Search`
- `Aurora / Research / Deep Dive`
- `Aurora / Core / Chief of Staff`
- `Aurora / Agency / Ops`

## D. Smoke
1. In Research Desk or Search channel: ask for a public fact with citations
2. Confirm audit/plugin calls look sane under `/admin/audit` if anything fails
3. Ping IM when Phase-1 usable → Wave 2 mapping from AURORA-FLEET-MAPPING.md

## Out of scope Phase-1
Lab/NetHunter bots; full 52-bot clone; custom AG-UI; Grok-style teams; Parallel paid key unless blocked
