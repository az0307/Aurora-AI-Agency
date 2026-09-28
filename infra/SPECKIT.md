# Spec-driven development with GitHub Spec Kit

For anything bigger than a quick fix, write the spec first. Spec Kit (github/spec-kit) gives a
CLI (`specify`) and a set of agent slash-commands that turn an idea into a constitution → spec →
plan → task list → implementation, all as files in the repo.

## Install
```sh
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git   # or: uvx specify-cli
specify init --here                 # scaffold into this repo; confirm flags with: specify init --help
```
- On the box / a Claude Code session: run it in `~/Aurora-AI-Agency`.
- On Termux: install `uv` first (`pip install uv`), then the same.
- Agent integration: `specify init` asks which agent (Claude, Copilot, …). Pick Claude Code.

> **Version note (checked 2026-09-27):** current Spec Kit names its commands `/speckit-constitution`,
> `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement` (a `/speckit-converge`
> and `bug`/`assess` extensions exist). Older docs use a dot (`/speckit.specify`). Confirm the exact
> names your version installs with `specify --help`; the flow below is the same either way.

## The flow (with an Aurora example)
Feature: **nightly off-box backups of n8n + Postgres to object storage** (the real gap in `CATALOG.md`).
1. **constitution** — one-time; ours is in `.specify/memory/constitution.md` (the hard rules).
2. **specify** — describe *what* and *why*: "Every night, encrypt the n8n dump + volumes and push to
   S3-compatible storage; restorable in one command; keys never in the repo." → `specs/NNN-offbox-backup/spec.md`.
3. **clarify / plan** — *how*: restic + rclone in an on-demand stack, a systemd timer, creds in `secrets.env`.
4. **tasks** — Spec Kit breaks the plan into `tasks.md`; mirror the durable ones into `infra/tasks.yaml`.
5. **implement** — build it, following the constitution (pin images, loopback, `.env.example` only, test).

## How specs relate to the rest
- `infra/DESIGN.md` — the standing architecture a spec must fit.
- `infra/tasks.yaml` — the machine-readable backlog agents pick from.
- `.specify/memory/constitution.md` — the rules every spec inherits.

## Fanning work out to parallel agents
One task per agent, each on its own branch/worktree, **one owner per file** (agents must not edit the
same file). Give each agent the task's `id`, its `files`, and its `acceptance` from `tasks.yaml`. Merge
via PR; the reviewer (or the PR steward) checks each against the constitution.
