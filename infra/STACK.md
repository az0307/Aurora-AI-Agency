# Software Stack — what to install and why

Everything below is **open-source and self-hostable** unless flagged. **Bold = default
pick**; the rest are documented alternatives so you can swap without re-researching.
All web-facing services sit **behind Cloudflare Tunnel + Access** — see
[`runbooks/DAY1.md`](./runbooks/DAY1.md).

## The layers at a glance

| Layer | Default pick | Why it wins | Alternatives |
|---|---|---|---|
| Control plane / PaaS | **Dokploy** | Cleanest UI, built-in monitoring, Git deploys, Traefik + auto-TLS, free | Coolify (most features), CapRover, Dockge (compose-only), Portainer |
| Reverse proxy / TLS | **Traefik** (bundled in Dokploy) | Auto Let's Encrypt, dynamic routing | Caddy (used by the standalone n8n stack), Nginx Proxy Manager |
| Automation ("self-hosted Zapier") | **n8n** + Postgres | You already run it; huge node library; fair-code | Activepieces (closest Zapier-style UI), Node-RED, Huginn |
| Metrics | **Beszel** | Ultra-light, agent + hub, per-container | Netdata (deep), Grafana + Prometheus (heavy) |
| Uptime + status page | **Uptime Kuma** | Dead-simple checks + public status page | Gatus, Healthchecks.io (self-host) |
| Live container logs | **Dozzle** | Zero-config log viewer in the browser | Grafana Loki + Promtail (retention/search) |
| Push alerts → phone | **ntfy** (self-hosted) | Free push to your phone; wire Kuma + Beszel to it | Gotify, Apprise |
| Start-page dashboard | **Homepage** | Single pane over all services + widgets | Homarr, Glance, Dashy |
| Databases | **Postgres**, **Redis** | Standard; Dokploy can provision both | (per-app) |
| Secrets | **Infisical** (self-hosted) | UI + API + CLI, rotation | SOPS + age, Docker secrets, `.env` (never committed) |
| Backups | **restic** + **rclone** off-box | Encrypted, dedup, to R2/Storage Box | Hetzner snapshots (fast same-provider), Borgmatic |
| Private access | **Cloudflare Tunnel + Access** | No open inbound ports; SSO in front | Tailscale, Netbird (self-host), WireGuard |
| Edge security | **CrowdSec** | Modern crowd-sourced IPS | fail2ban (baseline in cloud-init), Authentik/Authelia SSO |
| Container updates | **Renovate** / manual | Reviewable PRs, no surprise breakage | Watchtower (auto-pull; use cautiously, non-prod) |
| Web terminal (headless) | **ttyd** + Zellij | Browser SSH tile behind Access | Wave (remote mode), Wetty, Sshwifty |
| Git / CI (optional) | keep **GitHub** | Already your remote | Gitea/Forgejo + Woodpecker (fully self-host) |

## What actually runs where

- **Base (every box, via `cloud-init.yaml`):** hardened Ubuntu, non-root sudo user, key-only
  SSH, ufw, fail2ban, unattended-upgrades, Docker + compose plugin, shell sugar (see
  [`TERMINAL.md`](./TERMINAL.md)), then Dokploy bootstrap.
- **Agency box (Hetzner):** Dokploy → n8n stack, monitoring stack, dashboard, AutoBoros
  backend. Cloudflare Tunnel for ingress.
- **Client box (Hetzner, separate Project):** Dokploy + that client's stack only.
- **Personal lab (Oracle Free):** disposable — agent experiments, OpenHands sandbox, staging.

## Deploy order (once a box is up)

1. **Dokploy** (from `cloud-init` or its installer) — your control plane.
2. **Cloudflare Tunnel** connector — so nothing is exposed directly.
3. **Monitoring stack** (`stacks/monitoring/`) — Beszel + Uptime Kuma + Dozzle + ntfy.
4. **n8n stack** (`stacks/n8n/`) — the automation engine.
5. **Homepage** (`stacks/dashboard/`) — one link to everything.
6. **Agents** (`stacks/agents/`, optional) — OpenHands sandboxed runtime.

## Notes / gotchas

- **Dokploy owns TLS and deploys** where possible; the standalone `n8n` compose (with Caddy)
  is the fallback for a box *without* Dokploy.
- **n8n CORS:** the repo flags a wildcard `*` for Y.M.I — set `N8N_CORS_ALLOW_ORIGIN` to the
  real domain(s) once live.
- **Beszel/Kuma → ntfy:** both support webhook/ntfy notifications; point them at the
  self-hosted ntfy topic so alerts hit your phone.
- **Backups first, features second:** stand up `restic` before you put anything you'd miss on
  a box. See [`runbooks/BACKUP.md`](./runbooks/BACKUP.md).
- **Image pinning for production:** the compose stacks use readable tags (`:latest`, `:2`,
  `:16-alpine`) so the templates stay easy to read. Tags are mutable — before running these in
  production, pin each image to a reviewed version **plus its `@sha256:…` digest** and update
  those digests through scheduled **Renovate** PRs (rather than pulling `:latest` blindly).
