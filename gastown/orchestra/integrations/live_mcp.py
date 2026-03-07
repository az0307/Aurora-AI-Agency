"""
Live MCP Server Implementations
Actual working tool implementations for filesystem, git, and web operations.
"""

import os
import json
import glob
import subprocess
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class LiveFilesystemServer:
    """Live filesystem operations via MCP-compatible interface"""

    def __init__(self, allowed_dirs: List[str] = None):
        self.allowed_dirs = allowed_dirs or [os.getcwd()]
        self.name = "filesystem"
        self.connected = True

    def _is_allowed(self, path: str) -> bool:
        """Check if path is within allowed directories"""
        real_path = os.path.realpath(path)
        return any(
            real_path.startswith(os.path.realpath(d))
            for d in self.allowed_dirs
        )

    def read_file(self, path: str, encoding: str = "utf-8") -> Dict:
        """Read file contents"""
        if not self._is_allowed(path):
            return {"error": f"Access denied: {path} is outside allowed directories"}

        try:
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
            return {
                "status": "success",
                "path": path,
                "content": content,
                "size": len(content),
                "encoding": encoding
            }
        except FileNotFoundError:
            return {"error": f"File not found: {path}"}
        except Exception as e:
            return {"error": str(e)}

    def write_file(self, path: str, content: str) -> Dict:
        """Write content to file"""
        if not self._is_allowed(path):
            return {"error": f"Access denied: {path} is outside allowed directories"}

        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return {
                "status": "success",
                "path": path,
                "bytes_written": len(content)
            }
        except Exception as e:
            return {"error": str(e)}

    def search_files(self, pattern: str, directory: str = None) -> Dict:
        """Search for files matching pattern"""
        search_dir = directory or self.allowed_dirs[0]
        if not self._is_allowed(search_dir):
            return {"error": f"Access denied: {search_dir}"}

        try:
            matches = glob.glob(
                os.path.join(search_dir, "**", pattern),
                recursive=True
            )
            return {
                "status": "success",
                "pattern": pattern,
                "directory": search_dir,
                "matches": matches[:100],  # Limit results
                "total": len(matches)
            }
        except Exception as e:
            return {"error": str(e)}

    def list_directory(self, path: str) -> Dict:
        """List directory contents"""
        if not self._is_allowed(path):
            return {"error": f"Access denied: {path}"}

        try:
            entries = []
            for entry in os.scandir(path):
                entries.append({
                    "name": entry.name,
                    "is_dir": entry.is_dir(),
                    "size": entry.stat().st_size if entry.is_file() else 0,
                    "modified": datetime.fromtimestamp(
                        entry.stat().st_mtime
                    ).isoformat()
                })
            return {
                "status": "success",
                "path": path,
                "entries": sorted(entries, key=lambda e: (not e["is_dir"], e["name"]))
            }
        except Exception as e:
            return {"error": str(e)}

    def call_tool(self, tool_name: str, params: Dict) -> Dict:
        """Route tool calls"""
        handlers = {
            "read_file": lambda p: self.read_file(p.get("path", ""), p.get("encoding", "utf-8")),
            "write_file": lambda p: self.write_file(p.get("path", ""), p.get("content", "")),
            "search_files": lambda p: self.search_files(p.get("pattern", "*"), p.get("directory")),
            "list_directory": lambda p: self.list_directory(p.get("path", ".")),
        }
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        return handler(params)


class LiveGitServer:
    """Live git operations via MCP-compatible interface"""

    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or os.getcwd()
        self.name = "git"
        self.connected = True

    def _run_git(self, args: List[str]) -> Dict:
        """Run a git command"""
        try:
            result = subprocess.run(
                ["git"] + args,
                capture_output=True, text=True,
                cwd=self.repo_path,
                timeout=30
            )
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.returncode != 0 else None,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Git command timed out"}
        except Exception as e:
            return {"error": str(e)}

    def git_status(self, repo_path: str = None) -> Dict:
        """Get git status"""
        old_path = self.repo_path
        if repo_path:
            self.repo_path = repo_path
        result = self._run_git(["status", "--porcelain"])
        self.repo_path = old_path

        if "error" in result and result.get("status") != "success":
            return result

        files = []
        for line in result.get("output", "").split("\n"):
            if line.strip():
                status_code = line[:2].strip()
                filename = line[3:].strip()
                files.append({"status": status_code, "file": filename})

        return {
            "status": "success",
            "repo_path": repo_path or self.repo_path,
            "files": files,
            "clean": len(files) == 0
        }

    def git_diff(self, repo_path: str = None, file: str = None) -> Dict:
        """Get git diff"""
        args = ["diff"]
        if file:
            args.append(file)

        old_path = self.repo_path
        if repo_path:
            self.repo_path = repo_path
        result = self._run_git(args)
        self.repo_path = old_path
        return result

    def git_log(self, limit: int = 10, oneline: bool = True) -> Dict:
        """Get git log"""
        args = ["log", f"--max-count={limit}"]
        if oneline:
            args.append("--oneline")
        return self._run_git(args)

    def git_branch(self) -> Dict:
        """Get current branch info"""
        current = self._run_git(["branch", "--show-current"])
        branches = self._run_git(["branch", "--list"])
        return {
            "status": "success",
            "current": current.get("output", ""),
            "branches": [
                b.strip().lstrip("* ")
                for b in branches.get("output", "").split("\n")
                if b.strip()
            ]
        }

    def call_tool(self, tool_name: str, params: Dict) -> Dict:
        """Route tool calls"""
        handlers = {
            "git_status": lambda p: self.git_status(p.get("repo_path")),
            "git_diff": lambda p: self.git_diff(p.get("repo_path"), p.get("file")),
            "git_log": lambda p: self.git_log(p.get("limit", 10)),
            "git_branch": lambda p: self.git_branch(),
        }
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        return handler(params)


class LiveWebServer:
    """Live web operations via MCP-compatible interface"""

    def __init__(self):
        self.name = "web"
        self.connected = True

    def fetch_url(self, url: str, method: str = "GET",
                  headers: Dict = None) -> Dict:
        """Fetch content from URL"""
        try:
            req = urllib.request.Request(url, method=method)
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)
            req.add_header("User-Agent", "OrchestraTown/1.0")

            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode("utf-8", errors="replace")
                return {
                    "status": "success",
                    "url": url,
                    "status_code": response.status,
                    "content": content[:10000],  # Limit content size
                    "content_type": response.headers.get("Content-Type", ""),
                    "truncated": len(content) > 10000
                }
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}", "url": url}
        except urllib.error.URLError as e:
            return {"error": f"URL error: {e.reason}", "url": url}
        except Exception as e:
            return {"error": str(e), "url": url}

    def call_tool(self, tool_name: str, params: Dict) -> Dict:
        """Route tool calls"""
        handlers = {
            "fetch_url": lambda p: self.fetch_url(
                p.get("url", ""), p.get("method", "GET"), p.get("headers")
            ),
        }
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        return handler(params)


class LiveMCPManager:
    """
    Manages live MCP server instances with actual tool implementations.
    Drop-in replacement for the mock MCPManager.
    """

    def __init__(self, repo_path: str = None):
        base = Path(__file__).parent.parent.parent.parent
        self.repo_path = repo_path or str(base)

        self.servers = {
            "filesystem": LiveFilesystemServer(
                allowed_dirs=[self.repo_path]
            ),
            "git": LiveGitServer(self.repo_path),
            "web": LiveWebServer(),
        }

        self.call_log: List[Dict] = []

    def execute_tool(self, server_name: str, tool_name: str,
                     params: Dict) -> Dict:
        """Execute a tool on a live server"""
        server = self.servers.get(server_name)
        if not server:
            return {"error": f"Server '{server_name}' not found"}

        start = datetime.now()
        result = server.call_tool(tool_name, params)
        duration = (datetime.now() - start).total_seconds()

        self.call_log.append({
            "server": server_name,
            "tool": tool_name,
            "params": {k: str(v)[:100] for k, v in params.items()},
            "success": "error" not in result,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat()
        })

        return result

    def get_all_tools(self) -> List[Dict]:
        """List all available tools across servers"""
        tools = []
        tool_map = {
            "filesystem": ["read_file", "write_file", "search_files", "list_directory"],
            "git": ["git_status", "git_diff", "git_log", "git_branch"],
            "web": ["fetch_url"],
        }
        for server_name, tool_names in tool_map.items():
            for tool_name in tool_names:
                tools.append({
                    "server": server_name,
                    "tool": tool_name,
                    "live": True
                })
        return tools

    def get_stats(self) -> Dict:
        """Get usage statistics"""
        success = sum(1 for c in self.call_log if c["success"])
        return {
            "total_calls": len(self.call_log),
            "successful": success,
            "failed": len(self.call_log) - success,
            "servers": {
                name: {"connected": s.connected, "name": s.name}
                for name, s in self.servers.items()
            },
            "tools_available": len(self.get_all_tools()),
            "recent_calls": self.call_log[-10:]
        }

    def to_dict(self) -> Dict:
        return {
            "servers": {
                name: {"name": s.name, "connected": s.connected}
                for name, s in self.servers.items()
            },
            "stats": self.get_stats()
        }
