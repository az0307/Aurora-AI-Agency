# OpenBot — Sanitized Environment Checklist

**Prepared:** 2026-09-26 20:09 AEST  
**Rule:** KEY names only. Never invent, paste, or store secret values in this plan tree or chat. Aaron fills values on the chosen host; agents do not run login or write secrets.

## A. Server start

- `DATABASE_URL` (omit with `EMBEDDED_POSTGRES=on`)
- `KEY_ENCRYPTION_KEY` (`openssl rand -base64 32`)
- `INTELLIGENCE_API_URL`
- `INTELLIGENCE_GATEWAY_WS_URL`
- `INTELLIGENCE_API_KEY` (`cpk-...` from Aaron/Intelligence)

## B. Model

Use one provider path: `OPENAI_API_KEY` and optional `OPENAI_BASE_URL`; or `ANTHROPIC_API_KEY` + `BOT_PROVIDER` + `BOT_MODEL`; or `GOOGLE_API_KEY` plus provider/model. Optional: `AGENT_BOT_MODEL`, `BOT_RESPONSES_API`, `BOT_REASONING_EFFORT`, provider base URLs. Never paste ChatGPT/Claude browser-session tokens.

## C. Auth

Lab only: `OPENBOT_SINGLE_USER` (unsafe on shared/Tailscale/public). OAuth mode: `BETTER_AUTH_URL`, `BETTER_AUTH_SECRET`, `TRUSTED_ORIGINS`, `INITIAL_ADMIN_EMAILS`, and one provider pair such as `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` (or Microsoft/Okta). Optional email-domain allow list.

## D. Generated / managed

`COMPUTER_TOKEN`, `SUPERVISOR_TOKEN`, `MANAGED_AGENT_TOKEN`, `AGENT_TOOL_TOKEN`, `WORKER_SHARED_SECRET`, `MANAGED_AGENT_AG_UI_URL`. Path B leaves managed URL unset unless a reachable sidecar exists; sidecar uses internal `http://openbot-agent-langgraph:4201/ag-ui`.

## E. URLs and deployment

`PORT` / `SERVER_PORT`, `APP_PORT`, `OPENBOT_PUBLIC_URL`, `OPENBOT_APP_URL`, `DEPLOYMENT_ID`, `TENANT_PACKAGE_DIR`, `COPILOTKIT_LICENSE_TOKEN`, `EMBEDDED_POSTGRES`, `SERVER_INTERNAL_URL`.

## F. Computers/policy

`AGENT_COMPUTER_URL`, `COMPUTER_SUPERVISOR_URL`, `COMPUTER_RUNTIME`, `COMPUTER_SANDBOX`, `COMPUTER_BROWSER_MODE`, `AGENT_COMPUTER_POLICY`, `AGENT_COMPUTER_ALLOW_PRIVATE_HOSTS`, `AGENT_ENDPOINT_ALLOWED_HOSTS`, timeout and shell-environment keys. Policy is fail-closed; malformed JSON refuses startup. Egress proxy keys belong in uncommitted `egress.env`.

## G. Features

`COMPOSIO_API_KEY`, `OPENBOT_GENERATIVE_UI`, `AUDIT_RETENTION_DAYS`, transcription/voice keys. For durable aurora-01: real encryption/auth keys, OAuth, embedded DB or managed DB, digest pin, loopback bind + Tailscale Serve; no public :3001 or Funnel.

## Explicit non-goals

Do not run `copilotkit login` / `project select` for Aaron, write `.env` with values on the shared box, or echo secret values into chat or JSON.
