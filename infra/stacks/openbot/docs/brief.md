# CopilotKit/OpenBot — Controlled Install Brief

**Prepared:** 2026-09-26 20:08 AEST  
**Scope:** Read-only discovery / controlled transfer notes. No secrets written and no host mutation in this plan.

## Repo and pin

Repo: https://github.com/CopilotKit/OpenBot  
Default branch: `main`  
Prior discovery pin: `3c73cf00efba46122dfd0447485e2b61f1d6a2cd` (2026-09-24 AEST); durable release is v0.0.15 with digest in `container-images-v0.0.15.json`. License MIT. Homepage: https://www.copilotkit.ai/openbot

## Official install paths

- Desktop app for local trial.
- One-container server deployment: app/API combined on container :3001, `EMBEDDED_POSTGRES=on`, volume `/var/lib/postgresql`; pin a release tag/digest.
- Clone + Bun/Compose for product/tenant changes; Bun 1.3+, Docker Compose, optional supervisor, agent-computer, agent-bot, langgraph, routines worker.

## Target decision

aurora-01, Tailscale-only, Google OAuth, one-container, host loopback `127.0.0.1:3020:3001`, Serve HTTPS :3020, no Funnel. Do not use host 3001 (Uptime Kuma) or ondemand ports 3010–3015. Leave `OPENBOT_SINGLE_USER` unset/false.

## Prerequisite matrix

Docker/Compose and Postgres are required for local clone/compose; Bun and Node are useful for clone path; Intelligence project/key and model provider key are required for usable Bots. Disk and CPU were adequate on the shared box but memory is shared and may pressure under concurrent browsers. Agents must not provision secrets or SSH aurora-01.

## Sanitized env key groups

Required: `DATABASE_URL` unless embedded, `KEY_ENCRYPTION_KEY`, `INTELLIGENCE_API_URL`, `INTELLIGENCE_GATEWAY_WS_URL`, `INTELLIGENCE_API_KEY`. Model: `OPENAI_API_KEY` or Anthropic/Google provider trio, `BOT_PROVIDER`, `BOT_MODEL`. OAuth: `BETTER_AUTH_URL`, `BETTER_AUTH_SECRET`, `TRUSTED_ORIGINS`, `INITIAL_ADMIN_EMAILS`, and provider client pair. Generated/advanced: `COMPUTER_TOKEN`, `SUPERVISOR_TOKEN`, `MANAGED_AGENT_TOKEN`, `AGENT_TOOL_TOKEN`, `WORKER_SHARED_SECRET`, `MANAGED_AGENT_AG_UI_URL`, `COMPOSIO_API_KEY`, `AGENT_ENDPOINT_ALLOWED_HOSTS`.

Never paste browser-session tokens, OAuth values, or egress proxy secrets into chat or git. Filled env files are excluded; only placeholders belong in examples.

## Acceptance hints

Gateway resolves target, evaluates fail-closed policy, writes audit first, then acts. Credentials are encrypted/write-only and redacted from audit. Check `/api/copilotkit/info`, `/api/capabilities`, UI title, `/admin/audit`, `/admin/boundaries`, and `/admin/credentials` on a running instance.

## Risks and gates

OpenBot is alpha; pin releases. One-container lacks per-Bot supervisor and routine worker. Shared browser/logins are possible. No public exposure, Funnel, host port conflicts, destructive Docker steps, or secret writes without Aaron approval. The durable pack records the later live aurora-01 status in `STATUS-2026-10-03.md`.
