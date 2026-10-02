# VPN Manager — OpenBot handoff

**Updated:** 2026-10-03 (CoS week bring-up)
**Target URL:** `https://aurora-01.tail9a65b0.ts.net:3020`
**Health:** `curl -sS http://127.0.0.1:3020/api/capabilities`

## Ship (first bring-up)
1. Copy mode-600 env from Grok box:
   `/workspace/Aurora-AI-Agency/infra/stacks/openbot/openbot.env`
   → aurora-01 `/opt/aurora/stacks/openbot/openbot.env` (mkdir -p, chmod 600)
2. On aurora-01 run `/workspace/openbot-install/aurora-01-runpack.sh` **or** docker run from `aurora-01-docker-run.md` (digest pinned).
3. Serve (no Funnel): `tailscale serve --bg --https=3020 http://127.0.0.1:3020`
4. Health check as above.

## Recreate after env change
```bash
# on aurora-01 — re-scp openbot.env first, then:
docker rm -f openbot
# re-run runpack OR:
docker run -d --name openbot --restart unless-stopped \\
  -p 127.0.0.1:3020:3001 --env-file /opt/aurora/stacks/openbot/openbot.env \\
  -e EMBEDDED_POSTGRES=on -v openbot-data:/var/lib/postgresql \\
  ghcr.io/copilotkit/openbot@sha256:29daf0d4f80ec6ff851ad2a5d82736ff3d49d3ff37f6acfde69ffdecd82b28dd
# Serve usually persists; re-add if missing:
tailscale serve --bg --https=3020 http://127.0.0.1:3020
```

## Auth (box as of 2026-10-03)
| Key | Status |
| --- | --- |
| `GOOGLE_OAUTH_CLIENT_ID` | **SET** on box openbot.env + secrets.env |
| `GOOGLE_OAUTH_CLIENT_SECRET` | **SET** |
| `INITIAL_ADMIN_EMAILS` | **SET** = `REPLACE_WITH_AARON_GOOGLE_EMAIL` |
| Redirect URI | `https://aurora-01.tail9a65b0.ts.net:3020/api/auth/callback/google` |

If host env is stale vs box → re-scp then recreate. Do not paste secret values in chat.

## Never
- Chat paste of secrets
- Bind host 3001 / 3010–3015
- Funnel / public ports
- `OPENBOT_SINGLE_USER=true`

## Path B AG-UI sidecar (HOLD until Aaron yes)

1. After Install Manager runs `prepare-agui-env.sh` on the box:
   - ship `/workspace/Aurora-AI-Agency/infra/stacks/openbot/openbot.env`
   - and `…/agent-langgraph.env`
   → aurora-01 `/opt/aurora/stacks/openbot/` (both 600)
2. On aurora-01 run `/workspace/openbot-install/aurora-01-agui-runpack.sh` (or copy script first).
3. Confirm: `docker ps` shows `openbot` + `openbot-agent-langgraph`; `curl -sS http://127.0.0.1:3020/api/capabilities` 200; Serve :3020 still ON.
4. Do **not** publish 4201; do **not** Funnel.
