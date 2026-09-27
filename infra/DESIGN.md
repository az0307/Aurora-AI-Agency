# Aurora infra — architecture & design

The standing design of the phone-managed agent box. Specs (see `SPECKIT.md`) must fit this;
where they change it, update this file in the same PR.

## Goals / non-goals
- **Goals:** one always-on box that runs the agency's automation (n8n), agents (Hermes,
  OpenCode, Claude Code, OpenBot) and a model router — driven entirely from a phone, cheaply,
  privately, and reproducibly from this repo.
- **Non-goals:** a Kubernetes cluster; multi-tenant hosting; anything internet-facing beyond a
  future Cloudflare Tunnel for one webhook; running the AutoBoros/HexStrike SPVs here.

## Constraints
- **Budget** ≤ AUD $39/mo (Hetzner CX33 ≈ $16). **Operator has no laptop** — phone (Termux) +
  Claude Code sessions only. **RAM 8 GB** → staged startup. **Privacy:** client PII off free
  tiers; EU storage disclosed (APP 8).

## Components (all on aurora-01, Hetzner CX33, nbg1)
```
Phone (Termux/RDP) ──Tailscale──┐
                                ▼
  ┌───────────────────────── aurora-01 ─────────────────────────┐
  │  assistant(8600)  dashboard(3002)  admin/Dockge(5001)        │  ← GUIs, tailnet-only
  │  Hermes(9119) ── router/LiteLLM(4000) ── OpenBot(3020)       │  ← agents + model gateway
  │  n8n(5678)+Postgres   Playwright(8931)   Kuma(3001) Dozzle   │  ← automation, browser, monitoring
  │  every port bound 127.0.0.1; tailscale serve exposes on tailnet only │
  └─────────────────────────────────────────────────────────────┘
                                │  outbound only
                                ▼
        Model providers (OpenRouter / Anthropic / Gemini / Kimi / HF)
```

## Trust boundaries & network
- Provider firewall: inbound SSH + UDP 41641 (Tailscale) only; SSH removed after Tailscale is up.
- Host ufw mirrors that. All service ports are loopback; the tailnet is the only way in.
- No Funnel (that would be public). The router's host port is loopback, so OpenBot reaches it
  over the private `aurora-llm` Docker network instead.

## Data flows
- **Chat/voice/image:** phone → Hermes (Telegram) → router → provider; replies back on Telegram.
- **Assistant task box:** console → nginx `/intake` → n8n `assistant-intake` → router → Telegram.
- **YMI lead:** website form → n8n webhook → Google Sheet + Telegram alert (Cloudflare Tunnel planned).

## Secrets model
Bitwarden → hidden Termux prompt → `secrets.env` (600) → `bootstrap.sh --ship-only` copies it to
`/opt/aurora/secrets.env` (root, 600) → `stacks-up.sh` fans values into each stack's `.env`
(600, values never printed). Provider tokens stay on the phone.

## Provisioning & recovery
- `bootstrap.sh` (phone/session) → `hetzner/provision.sh` (or `hostinger/`) → cloud-init → ships
  `infra/` + secrets. `--ship-only` re-ships to an existing box with no provider call.
- **Rebuild:** re-run bootstrap → `aurora update` → `aurora up`. **Lockout:** Hetzner web console.
- **Backups:** nightly `aurora maintain backup` (n8n dump + volumes + configs, 7 kept on-box).
  Off-box (restic → object storage) is the open gap.

## Failure modes
- Model provider down → router fallback chains. Box OOM → swap + staged startup + RAM warnings.
- Container data safe on re-ship (chown skips container-owned dirs). n8n on Postgres 16 → migrate
  to 17 via dump/restore (documented in `server/README.md`), not a tag bump.

## Decisions (ADR-style)
- **2026-09-25 Hetzner over Hostinger** — twice the vCPU for the price, hourly billing, cleanest API/MCP for an agent. Trade-off: EU latency.
- **LiteLLM router** as the single model gateway — one endpoint, fallback chains, spend control, keeps provider keys in one place.
- **Tailscale over public ingress** — zero public ports; phones reach everything privately.
- **Provider MCP operator-side only** — it can delete servers, so never on the box it manages.
- **Staged deployment** — the 8 GB box starts one stack at a time.

## Open questions
- Off-box backups (restic target?). Cloudflare Tunnel for the YMI webhook. Postgres 17 migration
  timing. Whether to pin `N8N_IMAGE_TAG` now (yes — see STANDARDS).
