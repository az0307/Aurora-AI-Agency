---
name: box-health
description: Check and maintain aurora-01. Use when the user asks if the box is healthy, wants a report, a backup, to prune disk, to upgrade a stack, or a completion snapshot.
---
# Health & maintenance

- **Health:** `aurora check` (read-only ✓/✗) or `aurora maintain report` (health + upkeep, safe to
  paste — no secret values).
- **Backup:** `aurora maintain backup` (n8n dump + volumes + configs, 7 kept on-box). Off-box is a
  separate task (restic → object storage).
- **Disk:** `aurora maintain prune` (unused images/cache only — never volumes).
- **Upgrade:** `aurora maintain upgrade <stack>` (backs up first, recreates only running services).
- **Snapshot ("this works"):** `aurora maintain snapshot` after a clean report.
- **Tune once:** `aurora maintain tune` (swap, Docker log limits, timers, lazydocker/btop).

Interpreting: red ✗ names the fix; RAM/disk warnings mean stop an on-demand stack. Never disable a
check or push an empty commit to make something look green.
