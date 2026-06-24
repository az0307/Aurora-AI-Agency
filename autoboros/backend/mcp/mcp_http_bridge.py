#!/usr/bin/env python3
"""HTTP bridge for MCP tools — n8n calls this, it calls the stdio MCP server."""

import json
import subprocess
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()
app = FastAPI(title="AutoBoros MCP Bridge")

MCP_SCRIPT = Path(__file__).parent / "mcp_server.py"

def call_mcp_tool(name: str, arguments: dict):
    """Call the stdio MCP server for a single tool invocation."""
    proc = subprocess.Popen(
        ["python3", str(MCP_SCRIPT)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Send initialize
    init = {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "bridge", "version": "1.0"}}}
    proc.stdin.write(json.dumps(init) + "\n")
    proc.stdin.flush()
    proc.stdout.readline()  # ignore init response

    # Call tool
    call = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
    proc.stdin.write(json.dumps(call) + "\n")
    proc.stdin.flush()

    response = json.loads(proc.stdout.readline())
    proc.stdin.close()
    proc.wait(timeout=5)

    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])

    # Parse text content
    content = response["result"]["content"]
    text = content[0]["text"] if content else "{}"
    return json.loads(text)

class ToolRequest(BaseModel):
    name: str
    arguments: dict = {}

@app.post("/call")
async def call_tool(req: ToolRequest):
    logger.info("mcp_call", tool=req.name)
    result = call_mcp_tool(req.name, req.arguments)
    return result

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
