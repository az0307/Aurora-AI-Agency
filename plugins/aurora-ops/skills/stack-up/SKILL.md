---
name: stack-up
description: Bring Docker stacks up on the 8 GB box, staged. Use when the user wants to start router, n8n, hermes, openbot, assistant, dashboard, admin, monitoring, computer, or the whole box.
---
# Staged stack startup

The box has 8 GB — start one stack at a time, never all at once.
- Whole core set: `aurora up` (starts each, skips any missing a secret).
- One stack: `aurora start <name>` → `stacks-up.sh <name>`, which fills the stack's `.env` from
  `/opt/aurora/secrets.env` (values never printed, files 600) and waits for a health check.
- Order: `router` → `n8n` → `hermes` → `assistant` → `dashboard`/`monitoring` → `computer`.
- Heavy (needs 16 GB, don't co-run): Ollama, the computer-use desktop, OpenBot alongside either.

Client PII must only reach paid router chains, never a `-free` chain. If a start fails, read the
health-check line and `aurora logs <container>`. Confirm with `aurora status`.
