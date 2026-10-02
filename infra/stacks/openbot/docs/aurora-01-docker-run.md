# aurora-01 OpenBot bring-up (gated)

**Locked path:** one-container on aurora-01 · Google OAuth · no public/Funnel · no host `:3001` (Uptime Kuma).

**Port (reconcile):** CoS initially said `:3010`, but `/opt/aurora` ondemand stack already uses **`127.0.0.1:3010`** (browserless) through **`:3015`**. **Locked host port: 3020** (CoS confirmed 2026-10-03). Do not steal ondemand ports.

**Bind story (canonical):** loopback + Tailscale Serve HTTPS (matches Kuma/monitoring). Not `100.75.44.47:PORT` publish.

```text
docker:  -p 127.0.0.1:3020:3001
serve:   tailscale serve --bg --https=3020 http://127.0.0.1:3020
URL:     https://aurora-01.tail9a65b0.ts.net:3020
```

(If Serve HTTPS port mapping differs on this Tailscale version, VPN Manager sets the exact `tailscale serve` line; auth URLs must match the Serve origin.)

## Preconditions
1. VPN Manager: Docker healthy; chosen host port free; Serve rule private-only (no Funnel)
2. `.env` from `aurora-01.env.template` with Serve HTTPS origins in `BETTER_AUTH_URL` / `TRUSTED_ORIGINS` / `OPENBOT_*_URL`
3. Google OAuth redirect: `https://aurora-01.tail9a65b0.ts.net:<PORT>/api/auth/callback/google`
4. CoS secret cards landed; Aaron yes before first `docker run`

## Suggested run (on aurora-01)

```bash
docker pull ghcr.io/copilotkit/openbot@sha256:29daf0d4f80ec6ff851ad2a5d82736ff3d49d3ff37f6acfde69ffdecd82b28dd
docker run -d --name openbot \\
  --restart unless-stopped \\
  -p 127.0.0.1:3020:3001 \\
  --env-file /path/to/openbot.env \\
  -e EMBEDDED_POSTGRES=on \\
  -v openbot-data:/var/lib/postgresql \\
  ghcr.io/copilotkit/openbot@sha256:29daf0d4f80ec6ff851ad2a5d82736ff3d49d3ff37f6acfde69ffdecd82b28dd
```

Pin `:v0.0.15` / that digest (not floating `:latest` on a durable host).

## After start
- `curl -sS http://127.0.0.1:3020/api/capabilities` (on host)
- Phone UI: Serve HTTPS URL on Reno/S10 over Tailscale
- Follow `validation.md`

## Hard no
- Public Hetzner ports / Tailscale Funnel
- `OPENBOT_SINGLE_USER=true`
- Host `:3001` (Kuma) or `:3010–3015` (ondemand)
