# MCP servers — local, remote, and Desktop Commander

MCP servers give an AI app extra tools. There are two kinds:

- **Local**: a program that runs on the same machine as the AI app (`command` + `args`).
  It can touch that machine's files, shell, Docker, etc.
- **Remote**: a hosted service reached over HTTPS (`type: http` + `url`). It needs a token
  header or a one-time OAuth sign-in. Nothing to install.

Every package, version and URL here was checked against npm/PyPI and probed with a live MCP
`initialize` on 2026-09-24.

## Which file goes where

| File | For | Put it at |
|---|---|---|
| [`.mcp.json.example`](./.mcp.json.example) | **Claude Code** (laptop or server) | copy to `.mcp.json` in the project folder (git-ignored); keys come from your shell env |
| [`claude_desktop_config.json.example`](./claude_desktop_config.json.example) | **Claude Desktop** app (laptop) | merge into Claude Desktop's config file (path is inside the file), restart Claude |
| [`../stacks/hermes/config.yaml.example`](../stacks/hermes/config.yaml.example) | **Hermes** (the chat bot) | `mcp_servers:` section, already filled |

## The servers

| Server | Kind | What it gives | Key / sign-in | Where to run it |
|---|---|---|---|---|
| **desktop-commander** | local | terminal + file editing, process control | none | **laptop only** (see warning) |
| filesystem | local | read/write in the folders you list | none | laptop, server (workspace dir only) |
| memory | local | long-term memory as a small knowledge graph | none | anywhere |
| sequential-thinking | local | step-by-step reasoning scratchpad | none | anywhere |
| git | local | git operations in the workspace | none | server |
| fetch | local | fetch web pages | none | anywhere |
| playwright | local | drive a browser | none | laptop, server |
| docker | local | start/stop containers | Docker access | **server** |
| postgres | local | query n8n/scratch DBs (restricted mode) | `POSTGRES_DSN` | server |
| n8n | local | author + validate n8n workflows | `N8N_API_URL`, `N8N_API_KEY` (optional) | anywhere |
| hetzner | local | create/resize/destroy servers | `HETZNER_API_TOKEN` | **laptop** (keep the token off the server) |
| hostinger | local | optional, Hostinger boxes | `HOSTINGER_API_TOKEN` | laptop |
| **context7** | remote | current library/API docs | optional `CONTEXT7_API_KEY` | anywhere |
| **github** | remote | repos, PRs, issues, Actions | `GITHUB_PAT` | anywhere |
| **huggingface** | remote | search/read models, datasets, Spaces | optional `HF_TOKEN` | anywhere |
| **zapier** | remote | 9,000+ apps | `ZAPIER_MCP_TOKEN_CLAUDE` (one server **per** client) | anywhere |
| **composio** | remote | 1000+ apps | `COMPOSIO_CONSUMER_KEY` | anywhere |
| **notion** | remote | your Notion | OAuth sign-in (`/mcp`) | laptop |
| **linear** | remote | Linear issues (optional) | OAuth sign-in (`/mcp`) | laptop |

## Desktop Commander — set it up safely

It lets the AI run **any shell command** and edit files on your laptop. Useful, and powerful.

1. Claude Desktop: merge `claude_desktop_config.json.example`, restart Claude.
   Claude Code: it's already in `.mcp.json.example`.
2. Open a **new, separate chat** and say:
   - "Set Desktop Commander `telemetryEnabled` to false."
   - "Set `allowedDirectories` to `["/Users/YOU/Projects"]`." (**never** an empty list: that means
     the whole disk.)
   - Optionally: "Add `rm`, `sudo`, `dd`, `mkfs`, `shutdown` to `blockedCommands`."
3. Know the limit: `allowedDirectories` only fences the **file** tools. Terminal commands can
   still reach any file. Keep an eye on what it runs, and don't install it on the server
   (Hermes already has its own sandboxed shell there).

## Keys

Keep them in Bitwarden, and export them in your shell (or `infra/secrets.env` for the server):

```
GITHUB_PAT=            # github.com/settings/personal-access-tokens/new (fine-grained, only what you need)
CONTEXT7_API_KEY=      # optional: context7.com/dashboard
HF_TOKEN=              # already used by the router
ZAPIER_MCP_TOKEN_CLAUDE=   # a separate Zapier MCP server for Claude Code (Hermes has its own)
COMPOSIO_CONSUMER_KEY= # already used by Hermes
N8N_API_URL= / N8N_API_KEY=  # n8n → Settings → n8n API
HETZNER_API_TOKEN=     # laptop only
```

Claude Code: `claude mcp list` shows what connected; `/mcp` inside a session signs in to the
OAuth ones (Notion, Linear). Claude Desktop: Settings → Connectors shows remote ones.
