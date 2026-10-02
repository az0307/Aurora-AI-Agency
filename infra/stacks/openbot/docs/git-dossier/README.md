# OpenBot transfer dossier (durable pack)

**Updated:** 2026-10-03 ~02:27 AEST (Australia/Sydney)  
**Host / URL:** https://aurora-01.tail9a65b0.ts.net:3020 (Tailscale Serve, **no Funnel**)  
**Pin:** `ghcr.io/copilotkit/openbot@sha256:29daf0d4…` (= v0.0.15)  
**Git home:** Aurora-AI-Agency branch `infra/openbot-transfer-dossier-2026-10-03` → `infra/stacks/openbot/docs/`

## Current state (authoritative)

| Item | Status |
|------|--------|
| OpenBot container | **LIVE** · Up healthy · `127.0.0.1:3020→3001` · capabilities 200 · `mode=intelligence` · Google OAuth · Aaron signed in |
| Path B AG-UI | **LIVE** · `openbot-agent-langgraph` on `openbot-net` · :4201 **internal only** · `MANAGED_AGENT_AG_UI_URL` + token set |
| Composio | Env key **SET** (UI apps still to enable) |
| Search coworker | **Created** — thread init **failing** (investigate AGENT_ENDPOINT / private-host allow) |
| Parallel Search plugin | **Absent** on v0.0.15 pin — use Research Desk + browser until upgrade |
| Hermes | Untouched · **no** Hermes↔OpenBot bridge this week |
| Secrets in git | **Never** — only `*.env.example` + docs |

## Plugins (v0.0.15 catalogue)

- **Safe now:** Notion (DCR, no env secret), Skills, Routines *grants* (firing needs worker), Research Desk / built-ins
- **Needs setup:** Google Drive (OAuth client + redirect `…/api/plugins/oauth/callback`), Composio apps in UI after key, Routines worker (`WORKER_SHARED_SECRET`)
- **Not on pin:** Parallel Search

## Phase-1 / product next

1. Fix Search thread-init (managed URL + `AGENT_ENDPOINT_ALLOWED_HOSTS` if refuse private host → recreate **openbot only**)
2. CoS smoke: one Phase-1 managed coworker runnable (Deep Dive on Research Desk preferred per Bot Forge Top 5)
3. Channels + skills: Agency Core, Mentor-Study, Client-YMI (see `RECOMMENDED-ADDITIONS.md`)
4. Plugins order: Notion → Google Drive → Gmail/Calendar/GitHub via Composio
5. Remaining Phase-1 (Deep Dive, CoS, Agency Ops) + Wave 2 from roster

## Source docs (box)

| Path | Role |
|------|------|
| `/workspace/openbot-install/STATUS-2026-10-03.md` | Live status snapshot |
| `PATH-B-AGUI-RUNPACK.md` | Path B architecture (executed; some HOLD wording stale) |
| `COWORKER-RUNTIME-BLOCKER.md` | Custom-create blocker → Path B fix |
| `PHASE1-CREATE.md` | UI create checklist |
| `OPENBOT-EXPANDED-ROSTER.md` / `OPENBOT-ROSTER-MAP.md` | Fleet transfer plan |
| `git-dossier/SUPERPOWERS-STANDOUTS.md` | Tier S/A/B superpowers + standouts |
| `PLUGIN-CATALOGUE-v0.0.15.md` | Catalogue + limits (env presence section may lag STATUS) |
| `VPN-HANDOFF.md` | VPN ship/recreate (Path B section may lag LIVE) |
| `fleet-transfer/ROSTER-WAVE1.md` | Wave 1 names |
| `git-dossier/` | This pack |

## Anti-jobs

No secrets in chat/YAML/git; no Funnel; no publish :4201; no image upgrade without Aaron yes; no Ben/YMI contact; no live ads spend.
