# Day-1 runbook — stand up a box

Goal: from nothing to a hardened box running Dokploy + n8n, reachable only through
Cloudflare, manageable by Claude. ~30–45 min.

## 0. Prereqs
- SSH keypair (`ssh-keygen -t ed25519`).
- Hetzner account + a **Project** (one per client). Create an API token in that Project.
- A domain on **Cloudflare** (Y.M.I already uses Cloudflare).

## 1. Provision the box
**Option A — Claude via MCP:** configure `mcp/.mcp.json.example` → `.mcp.json` with your
Hetzner token, then ask Claude to create a `cax21` in `sin` (Singapore) using
`hetzner/cloud-init.yaml` as user-data.

**Option B — Terraform:**
```sh
cd infra/hetzner
cp main.tf.example main.tf
export TF_VAR_hcloud_token=...        # your Project token
export TF_VAR_ssh_public_key="$(cat ~/.ssh/id_ed25519.pub)"
terraform init && terraform apply
```
Put your public key into `cloud-init.yaml` (`<YOUR_SSH_PUBLIC_KEY>`) before applying.

## 2. Verify the base
```sh
ssh aurora@<server_ipv4>       # key-only; root login is disabled
sudo ufw status                # 22/80/443 allowed, default deny incoming
docker version                 # engine up, user in docker group
```
Shell sugar (fish + starship + zoxide + atuin + zellij + thefuck) is already installed.

## 3. Install the control plane (Dokploy)
If you didn't set `INSTALL_DOKPLOY=true` in cloud-init:
```sh
curl -sSL https://dokploy.com/install.sh | sh
```
Dokploy UI is on :3000 — **do not** open it on ufw. Reach it via the tunnel (next step).

## 4. Cloudflare Tunnel + Access (expose nothing directly)
1. In Cloudflare Zero Trust → **Tunnels** → create a tunnel, install `cloudflared` on the box
   (or run it as a container).
2. Add public hostnames routing to local ports, e.g.
   `dokploy.example.com → localhost:3000`, `n8n.example.com → localhost:5678`,
   `dash.example.com → localhost:3000` (Homepage).
3. In **Access** → add an application policy (email allowlist / OTP) for each hostname.
4. Once the tunnel works, tighten ufw: `sudo ufw deny 80 && sudo ufw deny 443` if *all*
   ingress goes through the tunnel.

## 5. Deploy the stacks
Either through Dokploy (recommended — it adds TLS + Git deploys) or directly:
```sh
# monitoring first, so you can see everything else come up
cd infra/stacks/monitoring && docker compose up -d
# n8n (self-hosted Zapier)
cd ../n8n && cp .env.example .env && $EDITOR .env && docker compose up -d
# start-page
cd ../dashboard && docker compose up -d
# agents (optional, sandboxed)
cd ../agents && cp .env.example .env && $EDITOR .env && docker compose up -d
```

## 6. Smoke test
```sh
curl -I https://n8n.example.com/healthz     # 200 through the tunnel
```
- n8n UI loads (behind Access + basic auth).
- Beszel + Uptime Kuma show the host; add an **ntfy** notifier so alerts hit your phone.
- In Claude Code, ask it to list your Hetzner servers → confirms the MCP loop.

## 7. Before you rely on it
- Set up **backups** → [`BACKUP.md`](./BACKUP.md).
- Restrict **n8n CORS** to the real domain (Y.M.I open item).
- Save the **n8n encryption key** somewhere safe (losing it = unreadable stored creds).
