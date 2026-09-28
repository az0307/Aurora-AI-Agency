---
name: provision-box
description: Provision or re-ship the Aurora box. Use when the user wants to create aurora-01, re-ship infra/secrets to it, or is setting up the Hetzner/Hostinger VPS. Covers the budget guard, the token-stays-local rule, and --ship-only.
---
# Provision / re-ship the box

The server likely **already exists** — do not re-provision to change config; use `--ship-only`.

1. **Existing box (usual case):** `AURORA_HOST=aurora-01 ./bootstrap.sh --ship-only` — re-copies
   `infra/` + `secrets.env`, no provider token, no API call, no cost.
2. **New box only:** `./bootstrap.sh --dry-run` (shows live price, refuses over AUD $39), then
   `./bootstrap.sh` and type `y`. Default provider Hetzner CX33 nbg1; `VPS_PROVIDER=hostinger` alt.

Rules: provider tokens (HCLOUD_TOKEN/HOSTINGER_API_TOKEN) **stay on the phone/session**, never on
the box. Never print secret values. A purchase needs the human's explicit confirmation. The
Hetzner MCP is operator-side only — never enable it on the box it manages.
Verify after: `aurora maintain report` (or `check.sh`).
