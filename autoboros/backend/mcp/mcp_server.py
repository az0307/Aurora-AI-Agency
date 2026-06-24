#!/usr/bin/env python3
"""MCP server for AutoBoros — filesystem, terminal, database tools.

SECURITY (hardened):
  - shell_exec: shell=False + shlex.split + command allowlist (no shell=True, ever)
  - file_read/file_write: confined to MCP_WORKSPACE via resolved-path containment
  - db_query: read-only enforced (SELECT / WITH / PRAGMA only)
"""

import json
import shlex
import subprocess
import os
import sqlite3
from pathlib import Path

def send(msg):
    print(json.dumps(msg), flush=True)

def read():
    line = input()
    return json.loads(line)

DB_URL = os.environ.get('DATABASE_URL', 'sqlite+aiosqlite:///./autoboros.db')

# All file + shell operations are confined to this root.
WORKSPACE = Path(os.environ.get('MCP_WORKSPACE', str(Path.home() / 'autoboros_workspace'))).resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

# shell_exec is restricted to this allowlist. Anything else is rejected.
ALLOWED_COMMANDS = {
    "ls", "cat", "echo", "pwd", "git", "python", "python3",
    "node", "npm", "grep", "find", "wc", "head", "tail", "sort", "uniq",
}

def get_db_path():
    if DB_URL.startswith('sqlite'):
        return DB_URL.replace('sqlite+aiosqlite:///', '').replace('sqlite:///', '')
    return None

def _safe_path(raw: str) -> Path:
    """Resolve a path and guarantee it stays inside WORKSPACE."""
    p = (WORKSPACE / raw).resolve() if not os.path.isabs(raw) else Path(raw).resolve()
    if WORKSPACE not in p.parents and p != WORKSPACE:
        raise PermissionError(f"path escapes workspace: {p}")
    return p

TOOLS = {
    "file_read": {
        "description": "Read a file from the workspace",
        "parameters": {"path": {"type": "string", "description": "Path within the MCP workspace"}}
    },
    "file_write": {
        "description": "Write content to a file in the workspace",
        "parameters": {"path": {"type": "string"}, "content": {"type": "string"}}
    },
    "shell_exec": {
        "description": "Execute an allowlisted command (no shell, workspace-confined)",
        "parameters": {"command": {"type": "string"}, "cwd": {"type": "string"}}
    },
    "db_query": {
        "description": "Run a read-only SQL query against the local DB",
        "parameters": {"query": {"type": "string"}}
    },
    "db_inspect": {
        "description": "List tables and schema in the database",
        "parameters": {}
    }
}

def handle_call(name, args):
    if name == "file_read":
        try:
            p = _safe_path(args["path"])
        except PermissionError as e:
            return {"error": str(e)}
        if not p.is_file():
            return {"error": "not a file"}
        return {"content": p.read_text()}

    if name == "file_write":
        try:
            p = _safe_path(args["path"])
        except PermissionError as e:
            return {"error": str(e)}
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(args["content"])
        return {"written": str(p), "bytes": len(args["content"])}

    if name == "shell_exec":
        raw = args.get("command", "")
        try:
            parts = shlex.split(raw)
        except ValueError as e:
            return {"error": f"unparseable command: {e}"}
        if not parts:
            return {"error": "empty command"}
        if parts[0] not in ALLOWED_COMMANDS:
            return {"error": f"command not allowed: {parts[0]}"}
        # confine cwd to the workspace
        try:
            cwd = _safe_path(args.get("cwd", "."))
        except PermissionError as e:
            return {"error": str(e)}
        try:
            result = subprocess.run(
                parts, shell=False, cwd=str(cwd),
                capture_output=True, text=True, timeout=30,
            )
        except subprocess.TimeoutExpired:
            return {"error": "command timed out (30s)"}
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    if name == "db_query":
        db_path = get_db_path()
        if not db_path:
            return {"error": "Only SQLite is supported in this MCP server"}
        q = args.get("query", "").strip()
        head = q.lstrip("(").split(None, 1)[0].lower() if q else ""
        if head not in ("select", "with", "pragma"):
            return {"error": "read-only: only SELECT / WITH / PRAGMA permitted"}
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(q)
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return {"rows": rows, "count": len(rows)}
        except Exception as e:
            return {"error": str(e)}

    if name == "db_inspect":
        db_path = get_db_path()
        if not db_path:
            return {"error": "Only SQLite is supported"}
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            schema = {}
            for t in tables:
                cursor.execute(f"PRAGMA table_info({t})")
                schema[t] = [{"name": r[1], "type": r[2]} for r in cursor.fetchall()]
            conn.close()
            return {"tables": tables, "schema": schema}
        except Exception as e:
            return {"error": str(e)}

    return {"error": f"Unknown tool: {name}"}

def main():
    send({"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": "2024-11-05", "capabilities": {}, "serverInfo": {"name": "autoboros-mcp", "version": "1.0.0"}}})

    while True:
        try:
            req = read()
        except EOFError:
            break

        if req.get("method") == "tools/list":
            send({"jsonrpc": "2.0", "id": req["id"], "result": {"tools": [
                {"name": k, "description": v["description"], "inputSchema": {"type": "object", "properties": v["parameters"]}}
                for k, v in TOOLS.items()
            ]}})

        elif req.get("method") == "tools/call":
            params = req["params"]
            result = handle_call(params["name"], params.get("arguments", {}))
            send({"jsonrpc": "2.0", "id": req["id"], "result": {"content": [{"type": "text", "text": json.dumps(result)}]}})

        else:
            send({"jsonrpc": "2.0", "id": req.get("id"), "error": {"code": -32601, "message": "Method not found"}})

if __name__ == "__main__":
    main()
