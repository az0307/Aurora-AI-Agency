"""
Git-Backed Persistent State Manager
Saves Orchestra Town state to git for version tracking and recovery.
"""

import json
import subprocess
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class GitStateManager:
    """
    Manages persistent state backed by git.
    All state changes are tracked with commits for full history.
    """

    def __init__(self, state_dir: str = None, repo_dir: str = None):
        base = Path(__file__).parent.parent
        self.state_dir = Path(state_dir) if state_dir else base / "state"
        self.repo_dir = Path(repo_dir) if repo_dir else base.parent.parent
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # State files
        self.files = {
            "town": self.state_dir / "town.json",
            "tasks": self.state_dir / "tasks.json",
            "messages": self.state_dir / "messages.json",
            "auth": self.state_dir / "auth.json",
            "executions": self.state_dir / "executions.json",
            "config": self.state_dir / "config.json",
        }

        self._ensure_gitignore()

    def _ensure_gitignore(self):
        """Ensure sensitive files are in .gitignore"""
        gitignore = self.state_dir / ".gitignore"
        ignore_patterns = ["auth.json", "*.secret", "*.key"]
        if not gitignore.exists():
            gitignore.write_text("\n".join(ignore_patterns) + "\n")

    def save(self, key: str, data: Dict, auto_commit: bool = False) -> bool:
        """Save state data to file"""
        if key not in self.files:
            self.files[key] = self.state_dir / f"{key}.json"

        try:
            state_file = self.files[key]
            state_file.write_text(json.dumps(data, indent=2, default=str))

            if auto_commit:
                self._git_commit(f"State update: {key}")
            return True
        except Exception as e:
            print(f"Error saving state {key}: {e}")
            return False

    def load(self, key: str) -> Optional[Dict]:
        """Load state data from file"""
        state_file = self.files.get(key)
        if not state_file:
            state_file = self.state_dir / f"{key}.json"

        if state_file.exists():
            try:
                return json.loads(state_file.read_text())
            except json.JSONDecodeError:
                return None
        return None

    def save_snapshot(self, label: str = None) -> str:
        """Save a complete snapshot of all state"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "label": label or f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "states": {}
        }

        for key, filepath in self.files.items():
            if filepath.exists():
                try:
                    snapshot["states"][key] = json.loads(filepath.read_text())
                except json.JSONDecodeError:
                    pass

        snapshot_file = self.state_dir / f"snapshot_{snapshot['label']}.json"
        snapshot_file.write_text(json.dumps(snapshot, indent=2, default=str))
        return str(snapshot_file)

    def load_snapshot(self, snapshot_path: str) -> bool:
        """Restore state from a snapshot"""
        path = Path(snapshot_path)
        if not path.exists():
            return False

        try:
            snapshot = json.loads(path.read_text())
            for key, data in snapshot.get("states", {}).items():
                self.save(key, data)
            return True
        except Exception:
            return False

    def get_history(self, key: str = None, limit: int = 10) -> List[Dict]:
        """Get git history for state files"""
        try:
            if key and key in self.files:
                target = str(self.files[key])
            else:
                target = str(self.state_dir)

            result = subprocess.run(
                ["git", "log", f"--max-count={limit}", "--oneline",
                 "--format=%H|%s|%ai", "--", target],
                capture_output=True, text=True,
                cwd=str(self.repo_dir)
            )

            history = []
            for line in result.stdout.strip().split("\n"):
                if line and "|" in line:
                    parts = line.split("|", 2)
                    history.append({
                        "hash": parts[0],
                        "message": parts[1] if len(parts) > 1 else "",
                        "date": parts[2] if len(parts) > 2 else ""
                    })
            return history
        except Exception:
            return []

    def _git_commit(self, message: str):
        """Create a git commit for state changes"""
        try:
            subprocess.run(
                ["git", "add", str(self.state_dir)],
                capture_output=True, cwd=str(self.repo_dir)
            )
            subprocess.run(
                ["git", "commit", "-m", f"[orchestra-state] {message}",
                 "--", str(self.state_dir)],
                capture_output=True, cwd=str(self.repo_dir)
            )
        except Exception:
            pass

    def list_snapshots(self) -> List[Dict]:
        """List available snapshots"""
        snapshots = []
        for f in sorted(self.state_dir.glob("snapshot_*.json")):
            try:
                data = json.loads(f.read_text())
                snapshots.append({
                    "file": str(f),
                    "label": data.get("label", f.stem),
                    "timestamp": data.get("timestamp"),
                    "states": list(data.get("states", {}).keys())
                })
            except Exception:
                pass
        return snapshots

    def get_stats(self) -> Dict:
        """Get state storage statistics"""
        total_size = 0
        file_stats = {}
        for key, filepath in self.files.items():
            if filepath.exists():
                size = filepath.stat().st_size
                total_size += size
                file_stats[key] = {
                    "size_bytes": size,
                    "exists": True,
                    "modified": datetime.fromtimestamp(
                        filepath.stat().st_mtime
                    ).isoformat()
                }
            else:
                file_stats[key] = {"exists": False}

        return {
            "state_dir": str(self.state_dir),
            "total_size_bytes": total_size,
            "files": file_stats,
            "snapshots": len(list(self.state_dir.glob("snapshot_*.json"))),
            "history_entries": len(self.get_history(limit=50))
        }
