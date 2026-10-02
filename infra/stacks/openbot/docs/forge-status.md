# OpenBot — Bot Forge status (HISTORICAL — superseded)

> **Superseded 2026-10-03 by `STATUS-2026-10-03.md`.**  
> This file was plan-only as of 2026-09-27 08:09 AEST. Host ship + OAuth fill happened later; do not treat “Nothing installed” as current.


**Refreshed:** 2026-09-27 08:09 AEST  
**Scope:** Plan only. **Nothing installed.** No Docker install on this box, no clone with secrets, no `.env` secrets written by agents, no public expose, no Funnel, no Tailscale SSH to aurora-01, no destructive changes.

## Decision LOCKED (Aaron / CoS)

| Field | Locked value |
| --- | --- |
| Host | **aurora-01** (`aurora-01.tail9a65b0.ts.net` / `100.75.44.47`) — **do not SSH** |
| Path | **one-container** (`ghcr.io/copilotkit/openbot` + `EMBEDDED_POSTGRES=on`) |
| Publish | **Tailscale-only host port 3020** (prefer) — map `127.0.0.1:3020:3001` + Serve HTTPS |
| Avoid | **3001** (Uptime Kuma), **3010–3015** (ondemand browserless) |
| Never | Host **3001** (Uptime Kuma Serve), public bind, **Funnel** |
| Auth | **Google OAuth** — **NOT** `OPENBOT_SINGLE_USER` |
| Install | **Not started** — awaiting Aaron secrets + explicit yes on host |

Shape only (Aaron runs on aurora-01 when ready):

```sh
docker run -d --name openbot \\
  -p 127.0.0.1:3020:3001 \\
  --env-file .env \\
  -e EMBEDDED_POSTGRES=on \\
  -v openbot-data:/var/lib/postgresql \\
  ghcr.io/copilotkit/openbot@sha256:29daf0d4f80ec6ff851ad2a5d82736ff3d49d3ff37f6acfde69ffdecd82b28dd
# Tailscale Serve HTTPS → loopback :3020 only; NEVER Funnel / public; NEVER 3010 (ondemand)
# BETTER_AUTH_URL / TRUSTED_ORIGINS / OPENBOT_*_URL must match the Serve origin on :3020
```

`recommended_port`: **3020**  
`port_conflict_note`: **3001** = Uptime Kuma; **3010–3015** = ondemand. OpenBot prefer **3020** + Serve.

## Installed

- **Nothing.**

## Refreshed pin

| Field | Value |
| --- | --- |
| Prior pin | `3c73cf00efba46122dfd0447485e2b61f1d6a2cd` (2026-09-24 04:18 AEST) |
| **New main HEAD** | `1ac9c35b393152e8d7e76c2331b8d5b584ba0e13` — 2026-09-27 06:11 AEST — Tell the server which run of a browser the shared computer is on (#265) |
| Newer than prior? | **Yes** |
| Latest release | **v0.0.15** @ `50c4bc5974f476961906232a5c594ac32e681450` (behind main HEAD) |
| Image pin | `ghcr.io/copilotkit/openbot@sha256:29daf0d4f80ec6ff851ad2a5d82736ff3d49d3ff37f6acfde69ffdecd82b28dd` (also `:v0.0.15`) |
| Docs | Prefer **tag + digest** from release `container-images.json` over floating `:latest` on durable hosts |

## Box blockers (this shared agent box)

- Docker CLI/Compose **missing**; daemon **unreachable** (OK if install is aurora-01-only)
- Bun **1.4.2** OK; ports 3001/3010/4100/4200/4201/4500/5432 **free** here
- Disk ~**110 GB** free; mem available ~**5.8 GB** / 15.6 GB
- Host Postgres **missing** here

## Aurora notes found

**Yes** — infra paths exist; no dedicated OpenBot stack under `/opt/aurora/stacks` yet.

- `/workspace/Aurora-AI-Agency/infra/INVENTORY.md` — `/opt/aurora`; monitoring **3001** Uptime Kuma
- `/workspace/Aurora-AI-Agency/infra/SERVICES.md` — `3001 | Uptime Kuma`
- `/workspace/Aurora-AI-Agency/infra/stacks/monitoring/docker-compose.yml` — `127.0.0.1:3001:3001`
- `/workspace/Aurora-AI-Agency/infra/SETUP.md` — stacks `/opt/aurora/stacks`; zero public ports after lock-down
- `/workspace/Aurora-AI-Agency/infra/secrets.env.example` — OpenBot key **placeholders** only
- `/workspace/Aurora-AI-Agency/infra/stacks/hermes/README.md` — port 3000 clash note vs OpenBot/Dokploy
- `/workspace/aurora-run/02-start-stacks.sh` — `TS_HOST=aurora-01.tail9a65b0.ts.net`
- `/workspace/aurora-run/stack-start.log` — `HOST_TS_IP=100.75.44.47`
- `/workspace/aurora-research/FLEET-BASE-INSTALL-PLAN.md` — OpenBot Install Manager brief

## Human gates still required

1. Aaron fills secrets **on aurora-01** (never in chat/agent files): `INTELLIGENCE_API_KEY`, model key, `KEY_ENCRYPTION_KEY`, `BETTER_AUTH_SECRET`, Google OAuth client id/secret, `BETTER_AUTH_URL` / `TRUSTED_ORIGINS` / `OPENBOT_PUBLIC_URL` / `OPENBOT_APP_URL` for Tailscale Serve on **:3020**, `INITIAL_ADMIN_EMAILS`. Leave `OPENBOT_SINGLE_USER` unset/false.
2. Aaron **yes** before `docker pull`/`docker run`, volume create, or Tailscale Serve change.
3. No agent SSH to aurora-01; no Funnel; no public expose; never bind host **3001**.
4. Confirm **3020** free on aurora-01 (VPN Manager); never steal 3010–3015 ondemand ports.

**Status:** `plan_only_decision_locked_awaiting_secrets`
