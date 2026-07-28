# Aurora Infrastructure — VPS Hosting Strategy

> Decision document + runnable setup for hosting Aurora AI Agency, AutoBoros, Y.M.I
> Roofing, self-hosted automation, and AI-agent workloads.
> Last reviewed: **2026-07-28**. Prices exclude VAT/GST and move — re-check before buying.

## TL;DR

- **Hetzner is the hub** (work + clients + n8n + agents). It has the **best MCP for Claude
  to manage** (full provisioning, ~104 tools), the best 2026 price-performance on its
  **CX/CAX** lines, and a **Singapore** region — the closest of the three to Australia.
- **Oracle Cloud Free** = a **disposable personal lab** only. Its Always-Free ARM was cut
  to 2 OCPU / 12 GB in June 2026 and idle instances get reclaimed — never put client data
  or anything you depend on here.
- **Hostinger** = optional, only if you want a *managed, hand-holdy* box for your own work
  and commit to a long term (its headline price renews 140–232% higher). Otherwise a second
  Hetzner Project beats it on both price and Claude-manageability.
- **Zapier can't be self-hosted.** Your self-hosted "Zapier" is **n8n** (already in use),
  optionally **Activepieces**. Zapier stays a cloud connector.
- **Control plane** for everything: **Dokploy**. **Expose nothing directly** — reach
  dashboards through **Cloudflare Tunnel + Access**.

See [`STACK.md`](./STACK.md) for the full software catalog, [`TERMINAL.md`](./TERMINAL.md)
for the smart-terminal cockpit, [`AGENTS.md`](./AGENTS.md) for the AI-agent CLIs, and
[`runbooks/DAY1.md`](./runbooks/DAY1.md) to stand a box up.

---

## Provider comparison (price + capability + MCP for Claude)

| | **Hetzner** (CX/CAX) | **Hostinger** (KVM) | **Oracle** (Always Free) |
|---|---|---|---|
| Entry price | CX22 ~€4.35/mo (2 vCPU / 4 GB / 40 GB); CAX21 ARM ~€6–7 (4 vCPU / 8 GB) | KVM2 ~$8.99/mo *intro* (2 vCPU / 8 GB) | **$0** |
| The price trap | CPX/CCX (dedicated vCPU) rose **144–176%** in 2026 → **use CX/CAX** | intro price **renews +140–232%** | reclaims idle instances |
| APAC latency | **Singapore** (~90–100 ms to Sydney) | SG/AU-region options | region-dependent |
| **MCP for Claude** | **Full provisioning** (~104 tools: create/destroy servers, firewalls, volumes, networks) — **best** | **Official** first-party MCP, but **lifecycle-only** (list/start/stop/restart + metrics) | OCI MCP exists; OCI is complex — **weakest** to drive |
| Backups | snapshots + Storage Box | snapshots | limited |
| Best at | price-performance + Claude-managed IaC | managed simplicity for one box | free disposable sandbox |

**Why Hetzner as the hub:** the "which has the best API/MCP for Claude to manage the setup
and running" question has a clear answer — Hetzner. Community MCP servers expose the full
Cloud API (provision, resize, firewall, snapshot, destroy), so Claude can build and operate
the fleet end-to-end, not just power-cycle it. Hostinger's official MCP is convenient but
can only *operate* an already-created box. Oracle's OCI is powerful but the hardest surface
for an agent to drive reliably.

---

## Workload → placement

| Workload | Where | Sizing | Notes |
|---|---|---|---|
| **n8n** (self-hosted "Zapier", incl. Y.M.I lead-capture + AutoBoros workflows) | Hetzner **Singapore** | CX22 / CAX21 | Behind Cloudflare Tunnel; restrict CORS from `*` |
| **AutoBoros backend** (FastAPI + MCP + Postgres) | Hetzner | CAX21 (4 vCPU / 8 GB) | Already Docker/compose-ready in `autoboros/backend/` |
| **AI-agent sandbox** (Claude Code, TARS, Kimi, OpenCode, OpenHands, Aider, Goose, Crush) | Hetzner (own box or Oracle lab) | CAX21+ | Hosted-API model backends → CPU box is enough |
| **Y.M.I Roofing site** (static) | **Cloudflare Pages** (not a VPS) | — | Sydney edge = lowest AU latency; already the deploy target |
| **Personal experiments / throwaway agent runs** | **Oracle Free** | 2 OCPU / 12 GB ARM | Disposable; no client data |
| **Your own managed box** (optional) | Hostinger *or* 2nd Hetzner Project | KVM2 / CX22 | Only pick Hostinger for managed simplicity + long term |
| **Client isolation** | **separate Hetzner Project per client** | per-need | Own API token + firewall = blast-radius control |

---

## Indicative monthly cost

| Scenario | Boxes | ~Monthly |
|---|---|---|
| **Lean** (everything on one box + free lab) | 1× Hetzner CX22 + Oracle Free | **~€4–5** |
| **Recommended** (agency box + client box + free lab) | 2× Hetzner CAX21 + Oracle Free | **~€12–15** |
| **+ managed personal box** | above + Hostinger KVM2 (long term) | **+~$9** |

Plus near-zero extras: Cloudflare (Pages/Tunnel/Access free tiers), Storage Box or R2 for
backups (a few € / cents). Static site hosting stays free on Cloudflare Pages.

---

## MCP management model (how Claude runs this)

Claude manages the fleet through MCP servers configured per provider — see
[`mcp/.mcp.json.example`](./mcp/.mcp.json.example):

- **Hetzner MCP** (stdio) → provision, resize, firewall, snapshot, destroy. The primary
  control surface. Scope a token per Hetzner Project so Claude's blast radius = one client.
- **Hostinger official MCP** (optional) → lifecycle + metrics on a managed box.
- **Oracle** → OCI CLI/MCP only if needed; treat the free box as cattle, rebuild from
  `cloud-init.yaml` rather than nursing it.

Day-to-day *inside* a box, Claude drives **Dokploy** (deploys, logs, TLS) and the
docker-compose stacks in [`stacks/`](./stacks/). Reproducibility comes from
`hetzner/cloud-init.yaml` + `hetzner/main.tf.example` so any box is rebuildable from code.

---

## Security baseline (non-negotiables)

1. **Expose nothing directly.** Put Dokploy, n8n, and every dashboard behind **Cloudflare
   Tunnel + Access (Zero-Trust SSO)**. Ideally the VPS firewall opens *no* inbound ports
   except what the tunnel needs. This is the single biggest win for a solo operator.
2. **SSH:** key-only, no password, non-root sudo user, fail2ban/CrowdSec (baked into
   `cloud-init.yaml`), unattended security upgrades.
3. **Secrets:** never commit them — `.example` files only (matches the repo's `.env.example`
   convention). Use Infisical (self-hosted) or Docker secrets for anything real.
4. **Backups:** restic + rclone **off-box** (Hetzner Storage Box or Cloudflare R2) **plus**
   Hetzner snapshots. Test a restore — see [`runbooks/BACKUP.md`](./runbooks/BACKUP.md).
5. **Client isolation:** a separate Hetzner Project (own token + firewall) per client.

---

## Things easy to overlook (called out on purpose)

- **AU data residency (Y.M.I / Privacy Act, APPs):** n8n on Singapore is fine, but disclose
  offshore processing in the privacy policy and keep PII in n8n minimal. The public site
  stays on Cloudflare's Sydney edge regardless.
- **Staging vs prod:** keep a throwaway staging stack (the Oracle lab is perfect) so agent
  experiments never touch client data.
- **Reproducible rebuild:** everything here is code — a lost box is `terraform apply` +
  `cloud-init` away, not a weekend.
- **Cost guardrails:** avoid Hetzner CPX/CCX (post-2026 price hikes); watch Hostinger
  renewal pricing; Oracle "free" reclaims idle ARM instances.
- **Container updates:** prefer Renovate/manual over blind Watchtower auto-pulls on prod.

---

## Sources

- [InfoQ — Oracle halves free-tier Ampere limits (2026)](https://www.infoq.com/news/2026/07/oracle-cloud-free-tier-limits/)
- [Hetzner — new Singapore location](https://www.hetzner.com/news/new-location-singapore/)
- [Hetzner 2026 price changes (CPX/CCX +144–176%)](https://wz-it.com/en/blog/hetzner-price-increase-june-2026-cpx-ccx-alternatives/)
- [Hetzner CX22 pricing 2026](https://vpsfor.dev/posts/hetzner-cx22-pricing-2026/)
- [Hostinger VPS pricing + real renewal costs](https://hostadvice.com/hosting-company/hostinger-reviews/vps-pricing/)
- [Hetzner MCP server for Claude Code](https://github.com/nityeshaga/hetzner-mcp-server)
- [Hostinger official API MCP server](https://www.hostinger.com/support/11079316-hostinger-api-mcp-server/)
- [Zapier is cloud-only / self-hosted alternatives](https://use-apify.com/blog/zapier-alternatives-2026)
- [Dokploy vs Coolify (2026 PaaS comparison)](https://introserv.com/blog/dokploy-vs-coolify-complete-comparison-of-the-best-self-hosted-paas-platforms-for-vps-and-dedicated-servers-2026/)
