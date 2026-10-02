# OpenBot — Post-Install Validation Checklist

**Prepared:** 2026-09-26 20:09 AEST  
**Pin:** CopilotKit/OpenBot `main` @ `3c73cf00efba46122dfd0447485e2b61f1d6a2cd`  
**Scope:** Plan-only. Steps marked **REQUIRES RUNNING INSTANCE** wait for Aaron-approved target and Aaron-provisioned secrets.

Legend: **PLAN-ONLY** means do not execute; **REQUIRES RUNNING INSTANCE** means curl/UI against live OpenBot. Path B is one-container (combined app/API on :3001); Path C is clone + compose (app :3010, API :3001).

## 0. Pre-flight

- Install target: **Done** — aurora-01 :3020 + Serve; OAuth SET 2026-09-27.
- Docker/Compose: PLAN-ONLY until host approved.
- `.env`: KEY names filled by Aaron; no secret values in chat/files agents write.
- Pin image tag/digest, never floating `latest` for durable hosts.
- Auth: OAuth for shared/aurora-01; never single-user on shared/Tailscale without explicit acknowledgement.

## 1. Startup identity and capabilities

Path C `scripts/start.sh` should bring up compose, migrate, verify `agent_profiles`/`agent_preferences`, start API/worker/app, and wait for OpenBot identity. Path B with `EMBEDDED_POSTGRES=on` runs migrations on start; use `/var/lib/postgresql` parent volume. External DB migrations are a release step with `--entrypoint sh`.

```sh
curl -fsS --max-time 8 http://127.0.0.1:3001/api/copilotkit/info
curl -s http://127.0.0.1:3001/api/capabilities
curl -fsS --max-time 3 http://127.0.0.1:3001/ | grep -qi OpenBot
```

Expect `licenseStatus` valid and `mode` intelligence. Path C health: :4100/health, :4200/health (unless Anthropic-only), :4201/health, and app :3010. Path B browser :4100 is internal and unpublished.

## 2. Health summary

| Surface | Path C | Path B | Expected |
|---|---|---|---|
| API identity | :3001/api/copilotkit/info | same | licenseStatus valid |
| Capabilities | :3001/api/capabilities | same | mode intelligence |
| App | :3010 | :3001 | OpenBot title |
| agent-computer | :4100/health | internal | 2xx |
| agent-bot | :4200/health | N/A | 2xx if started |
| agent-langgraph | :4201/health | internal/not in base image | 2xx if configured |
| supervisor | :4500→:4300/health | N/A | 2xx if used |

## 3. Coworkers and channels

**REQUIRES RUNNING INSTANCE — UI:** `/agents` (Path C `http://127.0.0.1:3010/agents`; Path B `http://127.0.0.1:3001/agents`). Confirm list loads, create/edit/duplicate/hide/delete/launch work, and a channel opens at `/channel/:id`. Optional AG-UI endpoint and write-only auth header must validate. Prefer UI; no public REST agent-list curl is documented.

## 4. Browser and audit

Open `/` and `/bot`; ask for a public fact or browser activity. Accept only when transcript shows tool/browser activity and Activity reflects actions. Open `/admin/audit`; expect permitted/refused/failed rows, named refusal rules, and redacted secrets. Add a deny rule under `/admin/boundaries`, retry, and verify refused/no side effect.

## 5. Fail-closed policy

Deny precedes allow; missing/empty allow permits nothing; malformed `AGENT_COMPUTER_POLICY` refuses startup; `enforce` blocks and `dry-run` records. Keep computer/supervisor/Postgres loopback/private and unpublished.

## 6. Credentials, plugins, skills, routines

`/admin/credentials` is write-only encrypted; values must never return in UI/API/audit. `KEY_ENCRYPTION_KEY` must be non-example in production. `/admin/plugins` catalogue includes Drive/Notion; Composio requires env key; unknown/custom tools are writes. `/skills` and `/admin/skills` are instructions, not capabilities. Routines need grants plus worker: floor 15 minutes, 20 enabled/person, 10 failures disable; Path B needs external worker with full env, `SERVER_INTERNAL_URL`, and `WORKER_SHARED_SECRET`.

Worker probe (never log Bearer):
```sh
curl -sS -o /dev/null -w '%{http_code}\n' -X POST http://127.0.0.1:3001/internal/routines/run -H 'Authorization: Bearer <WORKER_SHARED_SECRET>' -H 'Content-Type: application/json' --data '{}'
```
Expect 400 for matching secret/empty body; 401/404 indicates misconfiguration/old build.

## 7. Auth and exposure

Shared/aurora-01: `OPENBOT_SINGLE_USER` absent, OAuth configured, sign-in screen works, TLS terminates non-localhost. Public URL plus single-user must refuse startup. No public/Funnel exposure and no host :4201 publish.

## Pass/fail template

```text
Date (AEST):
Host/path:
Pin:
Migrations OK: [ ]
/api/copilotkit/info valid: [ ]
/api/capabilities intelligence: [ ]
/agents and channel: [ ]
Browser action + audit: [ ]
Boundaries fail-closed: [ ]
Credentials write-only: [ ]
Plugins/skills/routines: [ ]
Auth and public exposure: [ ]
```
