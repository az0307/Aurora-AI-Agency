# OpenBot stack (on-demand)

CopilotKit OpenBot for aurora-01. Canonical wrapper repo: `az0307/openbot`.

**Port:** `127.0.0.1:3020` → container `3001` (host 3001 is Uptime Kuma).
**RAM:** do not run this next to Ollama or the computer-use desktop on the CX33.

```sh
cd /opt/aurora/stacks/openbot
cp .env.example .env && chmod 600 .env && nano .env
docker compose up -d
curl -sS http://127.0.0.1:3020/api/capabilities
```

`INTELLIGENCE_API_KEY` is the `cpk-...` value from `npx copilotkit@latest project select`.
Generate `KEY_ENCRYPTION_KEY` with `openssl rand -base64 32`.
