# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**Aurora-AI-Agency** is a monorepo containing two independent subsystems:

| Subsystem | Path | Description |
|-----------|------|-------------|
| **gastown** | `gastown/` | Zero-dependency Python 3 CLI — generates project scaffolding from natural language |
| **hexstrike-ai** | `hexstrike-ai/` | AI-native red team platform — live Kali Linux integration via SSH-over-WebSocket |

There is no shared code, test suite, linter, build system, or CI/CD pipeline across either subsystem.

---

## gastown

### What it does

Takes a natural language description (e.g. `"REST API for users"`) and generates a full directory tree with boilerplate files for one of 7 detected project types. Zero external dependencies — pure Python 3 stdlib only.

### Commands

```bash
# Interactive mode (prompts for input)
python3 gastown/project_generator.py

# Pass description directly
python3 gastown/project_generator.py "web app for task management"

# Specify output directory (default: ./generated_project)
python3 gastown/project_generator.py "REST API for users" -o ~/output-dir

# Validate syntax without running
python3 -m py_compile gastown/project_generator.py
```

### Architecture

Single file: `gastown/project_generator.py` (~843 lines). No modules, no packages, no dependencies.

#### `ProjectGenerator` class — key flow

```
User input (idea string)
  → _detect_project_type()       keyword matching → one of 7 types
  → _get_structure_template()    nested dict: path → content
  → _create_structure()          recursive mkdir + write_text
```

#### Project type detection (`_detect_project_type`)

Detection is substring matching on the lowercased idea string. **First match wins** (order matters):

| Type | Trigger keywords |
|------|-----------------|
| `web_frontend` | web, website, frontend, react, vue, angular |
| `api_backend` | api, backend, server, rest, graphql |
| `cli_tool` | cli, command, tool, script |
| `ml_project` | ml, machine learning, ai, model, neural |
| `data_project` | data, analytics, pipeline, etl |
| `mobile_app` | mobile, app, ios, android |
| `general` | *(fallback — no keywords matched)* |

#### Structure template format (`_get_structure_template`)

Returns a nested `dict`. Keys ending in `/` are directories; values are either another `dict` (subdirectory), a string (file content from a stub method), or `""` (empty placeholder like `.gitkeep`).

#### Stub methods (`_stub_*`)

50+ methods that each return a boilerplate string for one file type. Naming convention: `_stub_<filetype>()`. All generated files include `# TODO` / `// TODO` comments as guidance.

**JavaScript/Node stubs:** `_stub_react_component`, `_stub_css`, `_stub_helpers`, `_stub_index_js`, `_stub_html`, `_stub_test`, `_stub_package_json`, `_stub_gitignore_node`, `_stub_route`, `_stub_controller`, `_stub_model`, `_stub_middleware`, `_stub_db_config`, `_stub_app_js`, `_stub_env`, `_stub_react_native_screen`, `_stub_navigation`, `_stub_theme`

**Python stubs:** `_stub_py_command`, `_stub_py_helpers`, `_stub_py_main`, `_stub_py_test`, `_stub_requirements`, `_stub_setup_py`, `_stub_gitignore_python`, `_stub_notebook`, `_stub_ml_model`, `_stub_preprocess`, `_stub_train`, `_stub_requirements_ml`, `_stub_extract`, `_stub_transform`, `_stub_load`, `_stub_general_main`, `_stub_yaml_config`, `_stub_sql_schema`

**Docs:** `_stub_readme`, `_stub_design_doc`, `_stub_gitignore_general`

#### CLI entry point (`main`)

Uses `argparse`. Positional `idea` arg is optional — omitting it triggers an interactive prompt. `-o / --output` sets output directory (default: `./generated_project`). Exits with code 1 if idea is empty.

#### Generated structures by type

| Type | Tech stack | Key files |
|------|-----------|-----------|
| `web_frontend` | React | src/components/, src/styles/, public/index.html, package.json |
| `api_backend` | Express/Node | src/routes/, src/controllers/, src/models/, src/middleware/, .env.example |
| `cli_tool` | Python | src/commands/, src/utils/, setup.py, requirements.txt |
| `ml_project` | Python/Jupyter | data/raw/, data/processed/, notebooks/, src/models/, src/preprocessing/ |
| `data_project` | Python/SQL | data/, src/pipeline/ (extract/transform/load), sql/schema.sql, config.yaml |
| `mobile_app` | React Native | src/screens/, src/components/, src/navigation/, assets/ |
| `general` | Python | src/main.py, tests/, docs/design.md |

---

## hexstrike-ai

### What it does

AI-native red team platform with live Kali Linux integration. The backend runs on a Kali box and exposes security tools via HTTP+SSE and WebSocket; the frontend (React/Vite/xterm.js) deploys to Vercel and connects over WSS.

### Architecture

```
Browser → Vercel (React/Vite/xterm.js)
               ↓ WSS / HTTPS
         Nginx Proxy (Kali)
               ↓
      HexStrike API :3001  (Express + ssh2 + SSE)
               ↓                    ↓
       Kali Linux tools        FastMCP :8889
       (7 tool routes)        (hexstrike_mcp.py)
```

### Backend (`hexstrike-ai/server/index.ts`)

TypeScript/Express server. Key design decisions:

- **`shell: false` everywhere** — all subprocess calls use `spawn(cmd, args[])`, never `exec` with shell interpolation for untrusted input
- **Command allowlist** — `ALLOWED_CMDS = Set(['nmap','masscan','nikto','sqlmap','hashcat','msfvenom','msfconsole'])`; any other command is rejected
- **Argument sanitization** — `sanitizeArg()` blocks shell metacharacters (`;`, `&&`, `|`, backticks, `$()`, redirects)
- **IP allowlist** — optional `ALLOWED_IPS` env var; all requests from unlisted IPs return 403

#### HTTP endpoints

| Route | Method | Tool | Notes |
|-------|--------|------|-------|
| `/health` | GET | — | Returns `{ok: true, ts}` |
| `/status` | GET | — | Checks which tools are installed via `which` |
| `/tools/nmap` | POST | nmap | Returns XML output; body: `{target, flags?, ports?}` |
| `/tools/nmap/stream` | POST | nmap | SSE streaming; same body |
| `/tools/masscan` | POST | masscan | body: `{target, ports?, rate?}` |
| `/tools/nikto` | POST | nikto | body: `{target}` |
| `/tools/nikto/stream` | POST | nikto | SSE |
| `/tools/sqlmap` | POST | sqlmap | body: `{url, level?, risk?}` |
| `/tools/sqlmap/stream` | POST | sqlmap | SSE |
| `/tools/hashcat` | POST | hashcat | body: `{hash, wordlist?, mode?}` |
| `/tools/hashcat/stream` | POST | hashcat | SSE |
| `/tools/msfvenom` | POST | msfvenom | body: `{platform?, arch?, payload?, lhost, lport?, format?}` |
| `/tools/msfvenom/stream` | POST | msfvenom | SSE |
| `/mcp/invoke` | POST | MCP bridge | Forwards to FastMCP at `HEXSTRIKE_MCP_URL` |

#### WebSocket endpoints

- `/ws` — general message bus; broadcasts messages to all other connected clients
- `/ssh` — SSH-over-WebSocket proxy; query params: `host`, `port`, `username`, `cols`, `rows`; supports resize events via `{type: "resize", rows, cols}` JSON message

#### Backend environment variables

```
PORT=3001
KALI_SSH_HOST=localhost
KALI_SSH_PORT=22
KALI_SSH_USER=kali
KALI_SSH_PASS=           # optional; key-based auth preferred
KALI_SSH_KEY=/home/kali/.ssh/id_rsa
HEXSTRIKE_MCP_URL=http://localhost:8889
FRONTEND_URL=*           # CORS origin
ALLOWED_IPS=             # comma-separated; empty = allow all
```

### Frontend

Deployed to Vercel via `vercel.json`. Built with Vite from `hexstrike-ai/frontend/` (directory not yet checked in — only the build config exists in the repo).

**Vercel environment variables** (set as Vercel secrets):

| Variable | Secret name |
|----------|------------|
| `VITE_BACKEND_URL` | `@hexstrike_backend_url` |
| `VITE_KALI_HOST` | `@hexstrike_kali_host` |
| `VITE_KALI_SSH_PORT` | `@hexstrike_kali_ssh_port` |
| `VITE_KALI_USER` | `@hexstrike_kali_user` |
| `VITE_SHODAN_KEY` | `@hexstrike_shodan_key` |
| `VITE_VT_KEY` | `@hexstrike_vt_key` |
| `VITE_GN_KEY` | `@hexstrike_gn_key` |
| `VITE_GITHUB_TOKEN` | `@hexstrike_github_token` |

### Deployment

**Backend (Kali Linux):**
```bash
sudo bash hexstrike-ai/scripts/setup-kali.sh
# Installs: nmap, masscan, nikto, sqlmap, hashcat, metasploit, ttyd, cloudflared, Node 20
# Creates systemd services: hexstrike-api (port 3001), hexstrike-ttyd (port 7681)
# Edit /opt/hexstrike/.env before starting the API service
systemctl restart hexstrike-api
```

**Frontend (Vercel):**
```bash
cd hexstrike-ai/frontend
npm install && npm run build
vercel deploy --prod
```

**Tunnel (expose Kali to internet):**
```bash
cloudflared tunnel --url http://localhost:3001
```

---

## Repository layout

```
Aurora-AI-Agency/
├── CLAUDE.md                         ← this file
├── README.md                         ← placeholder (AI Studio banner)
├── .gitignore                        ← Python bytecode only (__pycache__, *.pyc)
├── vercel.json                       ← Vercel config for hexstrike frontend
├── gastown/
│   ├── README.md
│   └── project_generator.py          ← entire gastown app (~843 lines)
└── hexstrike-ai/
    ├── README.md
    ├── server/
    │   └── index.ts                  ← entire backend (~257 lines)
    └── scripts/
        └── setup-kali.sh             ← one-shot Kali provisioning script
```

## Development conventions

- **gastown** has no test suite, no linter, no build step. Validate with `python3 -m py_compile`.
- **hexstrike-ai backend** is TypeScript but has no `tsconfig.json` or build step in the repo — the setup script runs it via `ts-node/esm/transpile-only`.
- Neither subsystem uses environment-specific branching or feature flags.
- All subprocess execution in the backend must go through `safeSpawn()` — never add `exec()` with string interpolation for user-supplied input.
- When adding a new tool route to the backend, add the command name to `ALLOWED_CMDS` and implement a `sanitizeArg`-aware call through `safeSpawn` or `streamSSE`.
