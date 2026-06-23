# AutoBoros Backend v2

Real-time agentic orchestration layer for the AutoBoros Cockpit.

## Architecture

```
┌─────────────┐     WebSocket      ┌─────────────────┐
│  Cockpit    │◄──────────────────►│  FastAPI        │
│  (React)    │   JWT auth         │  + WebSocket    │
└─────────────┘                    └────────┬────────┘
       │ POST /jobs/{id}/action            │
       │                                   │
       │                              ┌────┴────┐
       │                              │PostgreSQL│
       │                              │(hot state)│
       │                              └────┬────┘
       │                                   │
       │                         ┌─────────┴─────────┐
       │                         │      n8n          │
       │                         │  (workflows)      │
       │                         └─────────┬─────────┘
       │                                   │
       │                    ┌──────────────┴──────────────┐
       │                    │     MCP HTTP Bridge (3001)    │
       │                    │  ┌─────────────────────────┐  │
       │                    │  │  MCP stdio server       │  │
       │                    │  │  • file_read/write      │  │
       │                    │  │  • shell_exec           │  │
       │                    │  │  • db_query/inspect     │  │
       │                    │  └─────────────────────────┘  │
       │                    └───────────────────────────────┘
       │
       └──────────────────────────────────────────────────────►
              WebSocket push: job_updated, activity_new
```

## Quick Start

```bash
# 1. Clone and enter
cd autoboros-backend

# 2. Set secrets
cp .env.example .env
# Edit .env: SECRET_KEY=$(openssl rand -hex 32), AB_PASSWORD=your_password, N8N_API_KEY=$(openssl rand -hex 16)

# 3. Start everything
docker compose up -d

# 4. API: http://localhost:8000
# 5. n8n:  http://localhost:5678 (admin/admin)
# 6. MCP:  http://localhost:3001
```

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/login` | Login with password → JWT |
| GET | `/api/v1/auth/me` | Get current user |

### Jobs (JWT required)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/jobs` | List all jobs |
| POST | `/api/v1/jobs` | Create a job |
| GET | `/api/v1/jobs/{id}` | Get a job |
| PATCH | `/api/v1/jobs/{id}` | Update a job |
| POST | `/api/v1/jobs/{id}/action` | Execute action |
| DELETE | `/api/v1/jobs/{id}` | Delete a job |

### Activity (JWT required)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/activity` | List activity feed |

### WebSocket
| URL | Auth |
|-----|------|
| `ws://localhost:8000/api/v1/ws?token=<JWT>` | Query param |

### n8n (API key required)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/n8n/callback` | Workflow completion |
| POST | `/api/v1/n8n/webhook` | Generic inbound |

### MCP Bridge
| Method | Path | Description |
|--------|------|-------------|
| POST | `/call` | Invoke any MCP tool |
| GET | `/health` | Health check |

## WebSocket Events

| Event | Direction | Payload |
|-------|-----------|---------|
| `job_created` | Server → Client | Full job object |
| `job_updated` | Server → Client | Full job object |
| `job_deleted` | Server → Client | `{id, t}` |
| `activity_new` | Server → Client | Full activity object |

## Authentication

### Frontend
```bash
curl -X POST http://localhost:8000/api/v1/auth/login   -H "Content-Type: application/json"   -d '{"password":"autoboros"}'
# Returns: {"token":"...","user":{"id":"operator","name":"Operator"}}
```

### n8n
Set header `X-N8N-Key: <N8N_API_KEY>` on all callback/webhook requests.

## MCP Tools

| Tool | Description |
|------|-------------|
| `file_read` | Read any file in workspace |
| `file_write` | Write content to file |
| `shell_exec` | Run shell commands (30s timeout) |
| `db_query` | Read-only SQL against local DB |
| `db_inspect` | List tables and schema |

## Development

```bash
# Local (SQLite)
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
# Edit .env for SQLite
uvicorn app.main:app --reload

# Tests
pytest
```

## Deployment

### Docker Compose (production)
```bash
# Set strong secrets in .env
docker compose up -d
```

### Standalone
```bash
docker build -t autoboros-backend .
docker run -p 8000:8000 -e DATABASE_URL=... -e SECRET_KEY=... autoboros-backend
```

## n8n Workflow Setup

1. Import `n8n/workflows/example_approval.json`
2. Configure webhook URL: `http://api:8000/api/v1/n8n/callback`
3. Set HTTP Request header: `X-N8N-Key: <your N8N_API_KEY>`
4. Trigger from Cockpit → FastAPI → n8n → MCP → n8n → FastAPI → WebSocket → Cockpit
