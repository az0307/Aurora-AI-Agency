# OpenBot — Operations Runbook (Plan-Only)

**Prepared:** 2026-09-26 20:09 AEST  
**Pin:** CopilotKit/OpenBot `main` @ `3c73cf00efba46122dfd0447485e2b61f1d6a2cd`  
**Scope:** Documentation only. Do not execute stop/start/upgrade on any host until Aaron approves the install target and explicitly says yes to destructive steps.

Paths:
- **B — one-container** (aurora-01 style): `ghcr.io/copilotkit/openbot:<tag|digest>`
- **C — clone + compose** (lab): repo checkout + `bash scripts/start.sh` / `stop.sh`

---

## Safety gates (HARD)

1. **Aaron yes before** destructive migrations, upgrades, volume deletes, `docker rm` of data volumes, or rollback that rewrites schema.
2. **Never public expose** — bind published ports to loopback or private Tailscale only; put TLS in front of non-localhost; do not publish agent-computer / supervisor / Postgres beyond loopback.
3. **Never `OPENBOT_SINGLE_USER=true` on shared or Tailscale-reachable hosts** without Aaron acknowledging the upstream boot warning: anyone on that network is administrator. Prefer OAuth (Google / Microsoft / Okta) + `INITIAL_ADMIN_EMAILS`.
4. **Never write secret values** into agent-managed files or chat — KEY names only; Aaron fills values on the target host.
5. **Pin releases** — prefer version tag + digest from release `container-images.json`, not floating `latest`, on durable hosts.
6. Production refuses example `KEY_ENCRYPTION_KEY` and `AGENT_COMPUTER_ALLOW_PRIVATE_HOSTS` under `NODE_ENV=production`.

---

## Start

### Path C (clone + compose)

```sh
# Prerequisites: .env filled by Aaron; Bun 1.3+; Docker Compose
bun install                    # first time / after pull
bash scripts/start.sh
# Opens app http://127.0.0.1:3010 — API http://127.0.0.1:3001
```

What start does (summary): compose up → migrate → health waits → API → routine worker → app → licence check.

Logs: `<repo>/.logs/` (`server.log`, `app.log`, `worker.log`, `migrate.log`, …).

### Path B (one-container)

```sh
# Prefer pin from release asset (see Upgrade). Example shape only:
docker run -d --name openbot \\
  -p 127.0.0.1:3001:3001 \\
  --env-file .env \\
  -e EMBEDDED_POSTGRES=on \\
  -v openbot-data:/var/lib/postgresql \\
  ghcr.io/copilotkit/openbot:<tag-or-digest>

# UI+API: http://127.0.0.1:3001  (not 3010)
```

Notes:
- Mount **`/var/lib/postgresql`** (parent), never `.../data`.
- Leave `MANAGED_AGENT_AG_UI_URL` **unset** unless a Bot endpoint is reachable from this container (laptop default `http://localhost:4201/ag-ui` must be cleared for path B).
- `COMPUTER_TOKEN` can be auto-generated inside the image if unset.
- No supervisor / no in-image routine worker — see Routines under validation.md.

External DB variant: omit `EMBEDDED_POSTGRES`; set `DATABASE_URL` (pgvector enabled); run migrate Job **before** serving traffic (Aaron yes):

```sh
docker run --rm --env-file .env --entrypoint sh ghcr.io/copilotkit/openbot:<pin> \\
  -c "cd /app/server && bun scripts/migrate.ts"
```

---

## Stop

### Path C

```sh
bash scripts/stop.sh
# Optional: bash scripts/stop.sh --keep-computers   # leave per-Bot Chromiums signed-in
```

Order: app → routine worker → API → `docker compose down` → remove supervisor-labeled Bot computers (unless `--keep-computers`).

**Volumes are not deleted** — Postgres, agent workspace, and browser profiles persist.

### Path B

```sh
docker stop openbot
# or: docker kill <id>
# Data remains in volume openbot-data unless explicitly removed (DESTRUCTIVE — Aaron yes)
```

---

## Backup

### Path B — embedded Postgres

| Item | Detail |
| --- | --- |
| Docker volume name | typically `openbot-data` (as in `-v openbot-data:/var/lib/postgresql`) |
| Mount inside container | `/var/lib/postgresql` (cluster under `data/` subdirectory) |
| Backup approach | `docker stop` then volume backup, **or** `pg_dump` via `docker exec` if tools exist in image — prefer stop+volume archive for consistency |
| Also back up | Host `.env` (Aaron-held secrets store — not in git); any egress.env |

Example volume archive pattern (PLAN — Aaron yes; adjust volume name via `docker volume ls`):

```sh
docker stop openbot
docker run --rm -v openbot-data:/var/lib/postgresql -v "$PWD:/backup" alpine \\
  tar czf /backup/openbot-pg-$(date +%Y%m%d).tgz -C /var/lib/postgresql .
docker start openbot
```

### Path C — compose Postgres

| Item | Detail |
| --- | --- |
| Named volume | `postgres-data` → `/var/lib/postgresql/data` in `postgres` service |
| Other volumes | `agent-workspace`, `agent-profiles` (and optional SPIRE volumes) |
| Project prefix | Compose prefixes with project name (default often `openbot_postgres-data`) — confirm with `docker volume ls` |
| Logical dump | `docker compose exec -T postgres pg_dump -U openbot openbot > backup.sql` |

Also retain: `.env`, optional `egress.env`, tenant package if customized (`TENANT_PACKAGE_DIR`).

**Doc gap:** Upstream does not publish a first-class backup script; volume/`pg_dump` procedures above are operator-derived from deployment.md + compose volume names.

---

## Upgrade

### Pinning

1. Prefer a **GitHub Release** tag (e.g. `v0.0.x`).
2. Download `container-images.json` from that release; deploy **digest references**, not moving tags:

```sh
gh release download vX.Y.Z --pattern container-images.json
# Path B:
docker run ... "$(jq -r .images.openbot.reference container-images.json)"
```

3. Optional attestation: `gh attestation verify oci://ghcr.io/copilotkit/openbot:vX.Y.Z -R CopilotKit/OpenBot`
4. Source pin for this plan tree: SHA `3c73cf00efba46122dfd0447485e2b61f1d6a2cd` (voice/UX commit on main). Reconcile to nearest release tag before production.

### Path B procedure (Aaron yes before migrate/cutover)

1. Backup volume / DB.
2. Pull new digest/tag.
3. If external DB: run migrate with `--entrypoint sh` **before** new traffic.
4. If embedded: migrations run on container start — still backup first.
5. Stop old container; start new with **same** volume mount and env.
6. Run validation.md checks.

### Path C procedure (Aaron yes)

1. Backup `postgres-data` (+ profiles/workspace if needed).
2. `git fetch` / checkout release tag or pinned SHA.
3. `bun install`
4. `bash scripts/stop.sh` then `bash scripts/start.sh` (start reapplies migrate via compose).
5. Or pull prebuilt images via `container-images.json` + `IMAGE_PULL_POLICY=missing` (see releasing.md) to avoid local builds.

**Alpha warning:** expect breaking changes; read CHANGELOG `## X.Y.Z` before upgrading.

---

## Rollback

1. **Aaron yes.**
2. Restore previous image digest / git SHA.
3. Restore DB volume or `pg_dump` from backup taken **before** upgrade (schema may not be forward-compatible downward).
4. Do **not** assume newer migrations reverse automatically — if schema advanced, restore backup rather than “migrate down” (no documented down-migration runbook upstream).
5. Re-run validation.md smoke checks.

Path B rollback = same `docker run` with prior `container-images.json` reference + restored volume.  
Path C rollback = prior git pin + restored `postgres-data`.

---

## Sign-in

### Lab — single-user (laptop / disposable only)

- `.env.example` ships `OPENBOT_SINGLE_USER=true` → every request is one admin; no OAuth client needed.
- **Allowed** on true localhost.
- **Private / Tailscale / VPN / `.local`:** upstream **allows start** but prints a **boot warning** — anyone on that network is admin. Aaron must acknowledge before using this on aurora-01 / Tailscale.
- **Public `OPENBOT_PUBLIC_URL` / `OPENBOT_APP_URL` / routed `TRUSTED_ORIGINS`:** upstream **refuses to start** with single-user.

### Shared / aurora-01 — OAuth (required posture)

1. **Delete** `OPENBOT_SINGLE_USER` (or leave unset).
2. Set all of:
   - `BETTER_AUTH_URL` — API origin (callbacks), e.g. `https://openbot.example` or `http://127.0.0.1:3001`
   - `BETTER_AUTH_SECRET` — `openssl rand -base64 32` (≥32 chars)
   - `TRUSTED_ORIGINS` — app origin (path C often `http://localhost:3010`; path B often same as API)
   - `INITIAL_ADMIN_EMAILS` — required; re-read each sign-in; nothing else grants first admin
3. Configure **any one** (or more) of:
   - Google — callback `{BETTER_AUTH_URL}/api/auth/callback/google`
   - Microsoft — `.../callback/microsoft` (+ prefer directory GUID over `common` for staff-only)
   - Okta — `.../callback/okta` + `OKTA_OAUTH_ISSUER`
4. Restart. Optional later: Admin → Identity providers for company SAML/OIDC by email domain.
5. Put **TLS** in front of non-localhost (Secure cookies; secure context).

Half-configured providers refuse at startup (e.g. client id without secret, short secret).

### Desktop organization mode (out of scope for B/C server plan)

`OPENBOT_ORGANIZATION_AUTH_URL` points desktop at a company OpenBot authority; separate from Intelligence keys. Listed for completeness only.

---

## Routines / attachment cull (path B ops extras)

Not started by the one-container entrypoint. Outside scheduler must run (same image, `--entrypoint sh`):

- Routines sweep: `cd /app/server && bun scripts/fire-routines.ts` — needs **full** server env + `SERVER_INTERNAL_URL` + `WORKER_SHARED_SECRET`
- Staged attachments: `cd /app/server && bun scripts/cull-staged-attachments.ts` — needs primarily `DATABASE_URL` (optional age hours arg). Without it, per-person 32 unsent / 8 MiB ceiling can permanently block attaches.

Helm chart CronJobs cover both on Kubernetes; bare `docker run` does not.

---

## Quick reference — ports

| Service | Path C (host) | Path B |
| --- | --- | --- |
| App | 3010 | 3001 (combined) |
| API | 3001 | 3001 |
| agent-computer | 4100 loopback | internal 4100 unpublished |
| agent-bot | 4200 | not in image |
| agent-langgraph | 4201 | not in image |
| supervisor | 4500→4300 | not in image |
| Postgres | 5432 loopback | embedded loopback inside container |

---

## Incident notes (from upstream refusal messages)

| Symptom | Likely cause |
| --- | --- |
| Missing Intelligence vars | `INTELLIGENCE_API_KEY` / URLs |
| No identity provider | Set OAuth or lab `OPENBOT_SINGLE_USER` |
| Example encryption key in prod | Rotate `KEY_ENCRYPTION_KEY` |
| Model credential missing | Provider key for configured Bot |
| Port held by non-OpenBot | Change `APP_PORT` / `SERVER_PORT` or stop stranger |
| 502 after “successful” deploy | Volume mounted on `.../data` with `lost+found` — remount parent |
| Routines never fire | No worker / CronJob; check `/routines` sweep banner |
| Tool calls “no results” | Stale `AGENT_TOOL_TOKEN` after regenerate — restart Bots/server |

Until Aaron picks a host, treat every command in this file as **PLAN-ONLY**.

## Port constraint (CoS 2026-09-27)

On aurora-01, Tailscale `:3001` is **Uptime Kuma** (Serve). OpenBot must use Tailscale-only **`:3010`** (or next free). Never public/Funnel. Map container 3001→host 3010 if using one-container image.
