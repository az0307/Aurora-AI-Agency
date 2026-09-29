# MEGA: one block that brings everything up

Paste **Block A** into Termux on the phone. Tailscale must be on.

Every step is safe to re-run:
- A stack that's missing a key is skipped, and the script tells you which key.
- Nothing is bought.
- No secret is printed.

Then paste **Block B** into the Claude session that Block A opens on the server.

## Block A: Termux (phone)

```sh
# ── 1. Phone: latest kit + all home-screen buttons ──────────────────────────────────────
git -C ~/aurora pull --ff-only && aurora widgets

# ── 2. Server: update, then Tailscale → router → Hermes → OpenBot, panel, start page, check
ssh -t aurora-01 'aurora update && aurora ai
  bash /opt/aurora/stacks-up.sh assistant
  bash /opt/aurora/stacks-up.sh dashboard
  bash /opt/aurora/check.sh'

# ── 3. Remember the box's tailnet name (for the widgets) and open the control panel ────────
TS=$(ssh aurora-01 'docker exec tailscale tailscale status --json 2>/dev/null || tailscale status --json' \
     | jq -r .Self.DNSName | sed 's/\.$//')
echo "$TS" > ~/.aurora_ts && echo "Control panel: https://$TS:8600" && termux-open-url "https://$TS:8600"

# ── 4. Claude Code ON the server, linked to the Claude app → Code ───────────────────────────
aurora claude
```

Troubleshooting:
- **`jq` missing** → `pkg install jq`.
- **The panel says "network n8n_default not found"** → `ssh -t aurora-01 aurora start n8n`, then re-run step 2.
- **HTTPS / certificate error** → turn on MagicDNS + HTTPS Certificates at
  login.tailscale.com/admin/dns.

## Block B: paste into the server's Claude session

```text
You are the operator for aurora-01 (Aurora AI Agency). The repo is ~/Aurora-AI-Agency and the live
tree is /opt/aurora. Read these first: CLAUDE.md, infra/HERMES-OPENBOT.md, infra/SETUP.md,
infra/KEYS.md and infra/tasks.yaml.

GOAL: every stack healthy and every link working. Work through this list and don't stop at the
first failure:
1. `bash /opt/aurora/check.sh` → fix every ✗ you can fix on the box.
2. `aurora ai` → Tailscale, router, Hermes and OpenBot healthy. `aurora links` shows OPENBOT and TELEGRAM.
3. `bash /opt/aurora/stacks-up.sh assistant` and `... dashboard`. Then open http://127.0.0.1:8600 and
   http://127.0.0.1:3002 with the Playwright browser, click every tile, and report each one as
   up / down / wrong link.
4. Hermes: `docker exec hermes hermes doctor`. Fix what it reports, then send the Telegram bot a test
   message only if I confirm.
5. n8n: confirm the six aurora workflows exist and assistant-intake is Active (tasks T005/T006).
6. `aurora maintain report`. Summarise RAM and disk, and whether the off-box backup is set up.
7. Update infra/tasks.yaml statuses to match reality, commit on a branch, push, and open a PR.

RULES (hard):
- Never print, echo, cat or log a secret value. Refer to keys by NAME only. Secrets live only in
  /opt/aurora/secrets.env (root, 600) and per-stack .env files (600).
- Never use Tailscale Funnel and never publish a port on 0.0.0.0. Tailnet (`tailscale serve`) or
  loopback only.
- Client personal information stays on paid model chains, never a `-free` chain.
- Ask me first before anything that costs money, deletes data, rotates a key, or messages a real person.
- If a key is missing, say which one and where it comes from (KEYS.md). Don't invent values.
- Each step ends with: what you ran, what you saw, and what's still broken.
```

## One-liners to keep

| Do | Termux |
|---|---|
| Everything above, again | re-paste Block A |
| Just start the agents | `ssh -t aurora-01 aurora ai` |
| Every link | `ssh -t aurora-01 aurora links` |
| Health check | `ssh -t aurora-01 bash /opt/aurora/check.sh` |
| Hermes in Telegram / OpenBot / dashboard | `aurora tg` / `aurora openbot` / `aurora hdash` |
| Claude on the server | `aurora claude` (or the **claude-server** widget) |
| The menu | `a` |
