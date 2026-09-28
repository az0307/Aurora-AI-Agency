# AGENTS.md — working in this repo (for any coding agent)

Open convention read by Codex, Cursor, Gemini CLI, OpenCode, Aider, etc. **`CLAUDE.md` is the
detailed source of truth**; this is the short version plus the rules that must not be broken.

## What this repo is
Aurora AI Agency's client-delivery + self-hosting monorepo. Independent subsystems, no shared
build: `client-portal/` (Next.js 14 + Clerk + Prisma + Stripe), `ymi-roofing/` (static client
site + ops docs), `site/` (static marketing), `infra/` (the phone-managed Hetzner box + Docker
stacks + operator tools), `evermystic/`, `_empire/`.

## Hard rules (never break)
- **Secrets:** never commit real secrets — only `.env.example` / `secrets.env.example`. Provider
  tokens (Hetzner/Hostinger) never ship to the server. Never print a secret value.
- **Client PII** (e.g. Y.M.I Roofing leads) goes only through the router's **paid** chains,
  never a `-free` chain. Uncensored models only in `uncensored*` chains.
- **Scope:** this repo is agency + client work only. Do not re-add the AutoBoros engine or the
  HexStrike security platform — they are separate SPVs/repos.
- **Money & destructive actions** wait for the operator's explicit confirmation (typed `buy`
  for a VPS purchase; `aurora kali` and agent actions stay operator-driven).
- **Internet-facing images are pinned**; services bind `127.0.0.1` and are reached over Tailscale.
- **ACL / Privacy Act** compliance in `ymi-roofing` site copy must stay intact.

## Where things are
- Hosting + stacks + operator tools: `infra/` (see `infra/CLAUDE.md` isn't separate — read root `CLAUDE.md`).
- Design & architecture: `infra/DESIGN.md`. Backlog: `infra/tasks.yaml`. Standards/pins: `infra/server/STANDARDS.md`.
- Spec-driven workflow: `infra/SPECKIT.md`. Add-on catalog: `infra/CATALOG.md`.
- Plugin/skills for Claude Code: `plugins/aurora-ops/` + marketplace `.claude-plugin/marketplace.json`.

## Validate before you push
- Shell: `bash -n <script>` on every changed `.sh`.
- Router chains: `python3 infra/stacks/router/check-chains.py`.
- n8n workflows: JSON must parse; import-test with `n8n import:workflow` (lands inactive — activate in the UI).
- client-portal: `cd client-portal && npm run lint` (and `npm run build` for real changes).
- Compose: `docker compose config` in the stack dir.

## Spec-driven workflow (bigger changes)
Use GitHub Spec Kit: constitution → specify → plan → tasks → implement. Details and the
Aurora constitution: `infra/SPECKIT.md` and `.specify/memory/constitution.md`. Fan independent
tasks from `infra/tasks.yaml` out to parallel agents — one task per agent, its own branch, one
owner per file.
