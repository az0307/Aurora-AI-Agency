"""
Model Context Protocol (MCP) Integration Layer
Connects Orchestra Town to external data sources and tools via MCP standard
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class MCPResourceType(Enum):
    """Types of MCP resources"""
    FILE_SYSTEM = "file_system"
    DATABASE = "database"
    API = "api"
    WEB = "web"
    CUSTOM = "custom"


class MCPTool:
    """Represents an MCP tool/capability"""

    def __init__(self, name: str, description: str, schema: Dict):
        self.name = name
        self.description = description
        self.schema = schema  # JSON schema for parameters
        self.enabled = True
        self.usage_count = 0
        self.last_used = None

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.schema,
            "enabled": self.enabled,
            "usage_count": self.usage_count,
            "last_used": self.last_used
        }


class MCPServer:
    """MCP Server connection"""

    def __init__(self, name: str, server_type: MCPResourceType, config: Dict):
        self.id = f"mcp_{name}_{datetime.now().timestamp()}"
        self.name = name
        self.server_type = server_type
        self.config = config
        self.connected = False
        self.tools: Dict[str, MCPTool] = {}
        self.resources: List[Dict] = []

    def connect(self) -> bool:
        """Connect to MCP server"""
        # Integration point for actual MCP connection
        self.connected = True
        return True

    def disconnect(self):
        """Disconnect from MCP server"""
        self.connected = False

    def list_tools(self) -> List[MCPTool]:
        """List available tools from this server"""
        return list(self.tools.values())

    def call_tool(self, tool_name: str, params: Dict) -> Dict:
        """Call an MCP tool"""
        tool = self.tools.get(tool_name)
        if not tool:
            return {"error": f"Tool {tool_name} not found"}

        tool.usage_count += 1
        tool.last_used = datetime.now().isoformat()

        # Integration point for actual tool execution
        return {
            "status": "ready_for_integration",
            "tool": tool_name,
            "params": params,
            "server": self.name,
            "message": "MCP tool call configured - ready to integrate with actual MCP SDK"
        }

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "server_type": self.server_type.value,
            "connected": self.connected,
            "tools": [tool.to_dict() for tool in self.tools.values()],
            "resource_count": len(self.resources)
        }


class MCPManager:
    """
    Manages MCP connections and integrations
    Central hub for Model Context Protocol interactions
    """

    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.initialize_default_servers()

    def initialize_default_servers(self):
        """Initialize default MCP servers"""

        # File system MCP server
        fs_server = MCPServer(
            "filesystem",
            MCPResourceType.FILE_SYSTEM,
            {
                "description": "Local file system access via MCP",
                "capabilities": ["read", "write", "search", "watch"]
            }
        )
        fs_server.tools["read_file"] = MCPTool(
            "read_file",
            "Read file contents",
            {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "encoding": {"type": "string", "default": "utf-8"}
                },
                "required": ["path"]
            }
        )
        fs_server.tools["write_file"] = MCPTool(
            "write_file",
            "Write file contents",
            {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        )
        fs_server.tools["search_files"] = MCPTool(
            "search_files",
            "Search for files",
            {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "directory": {"type": "string"}
                },
                "required": ["pattern"]
            }
        )
        self.servers[fs_server.id] = fs_server

        # Database MCP server
        db_server = MCPServer(
            "database",
            MCPResourceType.DATABASE,
            {
                "description": "Database access via MCP",
                "capabilities": ["query", "insert", "update", "schema"]
            }
        )
        db_server.tools["execute_query"] = MCPTool(
            "execute_query",
            "Execute SQL query",
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "params": {"type": "array"}
                },
                "required": ["query"]
            }
        )
        db_server.tools["get_schema"] = MCPTool(
            "get_schema",
            "Get database schema",
            {
                "type": "object",
                "properties": {
                    "table": {"type": "string"}
                }
            }
        )
        self.servers[db_server.id] = db_server

        # Web/API MCP server
        web_server = MCPServer(
            "web",
            MCPResourceType.WEB,
            {
                "description": "Web and API access via MCP",
                "capabilities": ["fetch", "search", "browse"]
            }
        )
        web_server.tools["fetch_url"] = MCPTool(
            "fetch_url",
            "Fetch content from URL",
            {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "method": {"type": "string", "default": "GET"},
                    "headers": {"type": "object"}
                },
                "required": ["url"]
            }
        )
        web_server.tools["web_search"] = MCPTool(
            "web_search",
            "Search the web",
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "num_results": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        )
        self.servers[web_server.id] = web_server

        # Git MCP server
        git_server = MCPServer(
            "git",
            MCPResourceType.CUSTOM,
            {
                "description": "Git operations via MCP",
                "capabilities": ["read_repo", "commit", "diff", "log"]
            }
        )
        git_server.tools["git_status"] = MCPTool(
            "git_status",
            "Get git repository status",
            {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"}
                }
            }
        )
        git_server.tools["git_diff"] = MCPTool(
            "git_diff",
            "Get git diff",
            {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"},
                    "file": {"type": "string"}
                }
            }
        )
        self.servers[git_server.id] = git_server

    def add_server(self, server: MCPServer):
        """Add a new MCP server"""
        self.servers[server.id] = server

    def get_server(self, server_id: str) -> Optional[MCPServer]:
        """Get MCP server by ID"""
        return self.servers.get(server_id)

    def list_servers(self) -> List[MCPServer]:
        """List all MCP servers"""
        return list(self.servers.values())

    def get_all_tools(self) -> List[Dict]:
        """Get all available MCP tools across all servers"""
        tools = []
        for server in self.servers.values():
            for tool in server.list_tools():
                tools.append({
                    "server": server.name,
                    "server_id": server.id,
                    "tool": tool.to_dict()
                })
        return tools

    def execute_tool(self, server_id: str, tool_name: str, params: Dict) -> Dict:
        """Execute an MCP tool"""
        server = self.get_server(server_id)
        if not server:
            return {"error": f"Server {server_id} not found"}

        if not server.connected:
            server.connect()

        return server.call_tool(tool_name, params)

    def get_stats(self) -> Dict:
        """Get MCP usage statistics"""
        total_tools = sum(len(s.tools) for s in self.servers.values())
        total_usage = sum(
            tool.usage_count
            for server in self.servers.values()
            for tool in server.tools.values()
        )

        return {
            "total_servers": len(self.servers),
            "total_tools": total_tools,
            "total_tool_calls": total_usage,
            "servers_by_type": {
                rt.value: len([s for s in self.servers.values() if s.server_type == rt])
                for rt in MCPResourceType
            }
        }

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "servers": [server.to_dict() for server in self.servers.values()],
            "stats": self.get_stats()
        }


# Integration configuration for actual MCP SDK
MCP_INTEGRATION_CONFIG = {
    "sdk": {
        "name": "MCP Python SDK",
        "import": "from mcp import Server, Tool",
        "documentation": "https://modelcontextprotocol.io/docs/python-sdk",
        "status": "ready_for_integration"
    },
    "claude_integration": {
        "method": "Claude Desktop MCP integration",
        "config_file": "~/Library/Application Support/Claude/claude_desktop_config.json",
        "documentation": "https://docs.anthropic.com/claude/docs/mcp",
        "status": "ready_for_integration"
    },
    "server_examples": {
        "filesystem": {
            "package": "@modelcontextprotocol/server-filesystem",
            "config": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
            }
        },
        "github": {
            "package": "@modelcontextprotocol/server-github",
            "config": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {"GITHUB_TOKEN": "<token>"}
            }
        },
        "postgres": {
            "package": "@modelcontextprotocol/server-postgres",
            "config": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://..."]
            }
        }
    },
    "directory": {
        "url": "https://github.com/modelcontextprotocol/servers",
        "count": "75+ official servers available",
        "categories": ["databases", "web", "files", "git", "apis", "custom"]
    }
}
