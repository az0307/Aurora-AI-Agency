# Recommended additions — fleet bot input

**Updated:** 2026-10-03 ~02:27 AEST  
**Context:** Path B AG-UI **already LIVE**. Search coworker **created** but **thread init failing**. Prefer fix Search/Deep Dive runtime before bulk Wave 2 customs.

Placeholder for Bot Forge / CoS / VPN / Right Hand input. Edit freely; keep **no secrets**.

---

## Bot Forge Top 5 (priority order)

1. **Deep Dive on Research Desk** — make Deep Dive the primary research seat on Research Desk (grants + channel); prefer this over more Search clones until Search thread-init is fixed.
2. **Channel `Aurora / Agency Core` + Agency Ops skill** — channel naming + standing skill for Agency Ops / CoS routing (not a Grok “team”).
3. **Channel `Aurora / Mentor-Study` + Study Coach skill** — mentor/study lane; Study Coach one-job skill (Sydney TZ plans, quizzes, source-linked summaries; never submit as Aaron).
4. **Channel `Aurora / Client-YMI` + YMI Account skill** — client-signal clean; holds: **no Ben contact**, **no live ads** without Aaron yes.
5. **Plugins:** Notion → Google Drive → then Gmail / Calendar / GitHub (Composio apps after key already in env).

**Source docs (Forge):** `OPENBOT-EXPANDED-ROSTER.md`, `OPENBOT-ROSTER-MAP.md`, `PHASE1-CREATE.md`, `PLUGIN-CATALOGUE-v0.0.15.md`, `AURORA-FLEET-MAPPING.md`, `STATUS-2026-10-03.md`.

---

## Right Hand — recommended seating (do / skip)

### Do

| Seat / skill | One-line |
|--------------|----------|
| **Life Continuity Desk** | Cross-day continuity for Aaron priorities, open loops, and “what was I doing” without owning specialist work |
| **Open-Loop / Decision PA** | Capture decisions pending Aaron; draft options; never send/spend/commit |
| **Mentor & Study spaced-review** | Spaced-review prompts paired with Mentor-Study / Study Coach |
| **Household Admin** (pair **Tradbot**) | Household/ops admin drafts; pair with Tradbot lane — no finance publish |
| **Weekly Personal Board** | Weekly personal board pack (wins, blockers, next week) — drafts only |

### Skip

- Extra **YMI** twin under Right Hand (use Client-YMI channel + YMI Account skill)
- Extra **ads** twin under Right Hand (use Ads Manager in Agency Delivery — drafts only)
- Extra **Right Hand twin** / duplicate PA shells

---

## VPN / Infra — keep vs next

### Keep

- Tailscale **Serve** :3020 (no Funnel)
- Path B sidecar on `openbot-net` (`openbot-agent-langgraph` internal :4201)
- Image **pins** by digest (v0.0.15 / langgraph digest in runpack)
- Hermes **untouched**; **no** Hermes↔OpenBot bridge this week

### Next (ordered)

1. Confirm managed URL `http://openbot-agent-langgraph:4201/ag-ui` present in host openbot.env
2. If create/thread **refuses private host**: set `AGENT_ENDPOINT_ALLOWED_HOSTS=openbot-agent-langgraph:4201` → recreate **openbot only** (leave langgraph up)
3. Enable **Composio** apps in UI (Gmail / Calendar / GitHub first) — key already in env
4. **Google Drive** plugin OAuth redirect: `https://aurora-01.tail9a65b0.ts.net:3020/api/plugins/oauth/callback`
5. **Routines** that fire need `WORKER_SHARED_SECRET` + worker process (grants alone insufficient)
6. No Hermes bridge
7. Keep pin images; no floating `:latest` without Aaron yes

### Repo / sync hygiene

- Branch: **`infra/openbot-transfer-dossier-2026-10-03`**
- Sync **runbooks + docs only**; **exclude** filled `*.env` / `secrets.env` / oauth credential files
- Track **`*.env.example`** stubs only (placeholders, no real keys)

---

## Still open (fleet input welcome)

- [ ] Root cause + fix for Search thread init
- [ ] Confirm one Phase-1 managed coworker fully runnable end-to-end
- [ ] Whether Parallel requires image bump vs browser-only research
- [ ] Wave 2A timing (Study Coach + YMI Account) after Top 5
