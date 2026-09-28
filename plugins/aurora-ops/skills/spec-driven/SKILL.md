---
name: spec-driven
description: Run a bigger change spec-first with GitHub Spec Kit and fan tasks to parallel agents. Use when the user wants to plan/build a sizeable feature on the box, or mentions specs, tasks.yaml, or parallel agents.
---
# Spec-driven change

For anything bigger than a quick fix: constitution → specify → plan → tasks → implement.
- Details + install: `infra/SPECKIT.md`. Rules every spec inherits: `.specify/memory/constitution.md`.
- Standing architecture the spec must fit: `infra/DESIGN.md`.
- Backlog to pick from / add to: `infra/tasks.yaml` (each task has id, files, acceptance).

Parallelising: one task per agent, its own branch, **one owner per file** (never two agents in the
same file). Hand each agent its task `id`, `files`, and `acceptance`. Merge via PR; check each
against the constitution. Keep docs + `tasks.yaml` updated in the same PR.
