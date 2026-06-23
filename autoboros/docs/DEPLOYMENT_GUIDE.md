# AutoBoros Deployment Guide

## Option A: Fly.io (Recommended)

### 1. Prerequisites
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh
fly auth login
```

### 2. Create app + volume
```bash
fly apps create autoboros
fly volumes create autoboros_data --region iad --size 1
```

### 3. Set secrets
```bash
fly secrets set SECRET_KEY=$(openssl rand -base64 32)
fly secrets set AB_PASSWORD=$(openssl rand -base64 24)
fly secrets set DATABASE_URL="postgresql+asyncpg://..."
fly secrets set N8N_API_KEY="..."
fly secrets set N8N_BASE_URL="https://your-n8n.fly.dev"
fly secrets set MCP_SERVER_URL="https://your-mcp.fly.dev"
```

### 4. Deploy
```bash
fly deploy --ha=false
```

### 5. Cockpit build
Set repo variables in GitHub:
- `VITE_API_URL=https://autoboros.fly.dev/api/v1`
- `VITE_WS_URL=wss://autoboros.fly.dev/ws`

Push to `main` → GitHub Actions builds SPA → deploys to Pages (or serve from Fly via staticfiles).

---

## Option B: Single VPS (Docker Compose)

```bash
# On your server
git clone <repo>
cd autoboros
cp .env.example .env  # fill in
make dev              # db + api + n8n + vite
```

---

## Option C: Railway / Render

1. Connect GitHub repo
2. Add environment variables from `.env.example`
3. Set build command: `pip install -r requirements.txt && cd autoboros-cockpit && npm ci && npm run build`
4. Start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
