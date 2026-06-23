# MCP Server for AutoBoros

## What this is

A minimal Model Context Protocol server that exposes filesystem, shell, and database tools to n8n workflows and local agents.

## Run

```bash
python mcp_server.py
```

## Tools

| Tool | Description |
|------|-------------|
| `file_read` | Read any file in the workspace |
| `file_write` | Write content to a file |
| `shell_exec` | Run shell commands (30s timeout) |
| `db_query` | Read-only SQL against the local DB |

## n8n Integration

Use the MCP node or HTTP Request node to call `http://localhost:3001` (when wrapped with an HTTP bridge).

## Security

- Paths are resolved and checked against `$HOME`
- Shell commands have a 30-second timeout
- `db_query` is read-only in this implementation
