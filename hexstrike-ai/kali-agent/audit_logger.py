"""
AuditLogger — JSONL compliance logging for Kali Agent
Drop into HexStrike's app.py or import as module.
AutoBoros.ai | 2026-03-27
"""

import json
import hashlib
import os
from datetime import datetime, timezone
from typing import Optional


class AuditLogger:
    """Append-only JSONL audit trail for all security engagement activities."""

    def __init__(self, engagement_id: str, base_dir: str = "/tmp/pentest"):
        self.engagement_id = engagement_id
        self.base_dir = os.path.join(base_dir, engagement_id)
        os.makedirs(self.base_dir, exist_ok=True)

        # Log file paths
        self.master_log = os.path.join(self.base_dir, "audit.jsonl")
        self.scope_log = os.path.join(self.base_dir, "scope_audit.jsonl")
        self.exploit_log = os.path.join(self.base_dir, "exploitation_log.jsonl")
        self.findings_log = os.path.join(self.base_dir, "findings_log.jsonl")

        # Counter for unique IDs
        self._counter = 0

    def _next_id(self) -> str:
        self._counter += 1
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"LOG-{ts}-{self._counter:04d}"

    def _write(self, filepath: str, entry: dict):
        """Append a single JSON line to the specified log file."""
        entry["id"] = self._next_id()
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        entry["engagement_id"] = self.engagement_id
        try:
            with open(filepath, "a") as f:
                f.write(json.dumps(entry, default=str) + "\n")
        except OSError as e:
            print(f"[AUDIT ERROR] Failed to write to {filepath}: {e}")

    def log_tool_execution(
        self,
        skill: str,
        tool: str,
        action: str,
        target: str,
        command: str,
        result_summary: str,
        output_file: Optional[str] = None,
        phase: str = "recon",
        operator: str = "az",
        approval: str = "auto",
        duration_seconds: Optional[int] = None,
        severity: str = "info",
    ):
        """Log a tool execution event to the master audit trail."""
        entry = {
            "phase": phase,
            "skill": skill,
            "tool": tool,
            "action": action,
            "target": target,
            "command": command,
            "result_summary": result_summary,
            "output_file": output_file,
            "output_hash": self.hash_file(output_file) if output_file else None,
            "operator": operator,
            "approval": approval,
            "duration_seconds": duration_seconds,
            "severity": severity,
        }
        self._write(self.master_log, entry)

        # Also write to phase-specific logs
        if phase == "exploitation":
            self._write(self.exploit_log, entry)

    def log_finding(
        self,
        finding_id: str,
        severity: str,
        title: str,
        affected_asset: str,
        cve: Optional[str] = None,
        cvss: Optional[float] = None,
        tool: str = "manual",
        status: str = "confirmed",
    ):
        """Log a discovered vulnerability finding."""
        entry = {
            "finding_id": finding_id,
            "severity": severity,
            "title": title,
            "affected_asset": affected_asset,
            "cve": cve,
            "cvss": cvss,
            "tool": tool,
            "status": status,
        }
        self._write(self.findings_log, entry)
        self._write(self.master_log, {**entry, "action": "finding_discovered", "phase": "vuln_scan"})

    def log_scope_check(self, target: str, allowed: bool, reason: str, requesting_tool: str = "unknown"):
        """Log a scope validation check."""
        entry = {
            "action": "scope_check",
            "target": target,
            "allowed": allowed,
            "reason": reason,
            "requesting_tool": requesting_tool,
        }
        self._write(self.scope_log, entry)
        self._write(self.master_log, {**entry, "phase": "scope_validation"})

    def log_exploitation_attempt(
        self,
        target: str,
        finding_id: str,
        method: str,
        result: str,
        access_gained: Optional[str] = None,
        operator: str = "az",
    ):
        """Log an exploitation attempt (requires operator approval)."""
        entry = {
            "action": "exploitation_attempt",
            "phase": "exploitation",
            "target": target,
            "finding_id": finding_id,
            "method": method,
            "result": result,
            "access_gained": access_gained,
            "operator": operator,
            "approval": "operator_confirmed",
        }
        self._write(self.exploit_log, entry)
        self._write(self.master_log, entry)

    def log_lateral_movement(
        self,
        source_host: str,
        dest_host: str,
        method: str,
        credential_type: str,
        result: str,
        operator: str = "az",
    ):
        """Log lateral movement between hosts."""
        entry = {
            "action": "lateral_movement",
            "phase": "post_exploit",
            "source_host": source_host,
            "dest_host": dest_host,
            "method": method,
            "credential_type": credential_type,
            "result": result,
            "operator": operator,
            "approval": "operator_confirmed",
        }
        self._write(self.master_log, entry)

    @staticmethod
    def hash_file(filepath: str) -> Optional[str]:
        """SHA256 hash of a file for integrity verification."""
        if not filepath or not os.path.exists(filepath):
            return None
        sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return f"sha256:{sha256.hexdigest()}"
        except OSError:
            return None

    def generate_timeline(self) -> str:
        """Generate human-readable engagement timeline from audit log."""
        if not os.path.exists(self.master_log):
            return "No audit entries found."

        lines = []
        with open(self.master_log, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    ts = entry.get("timestamp", "?")[:19]
                    phase = entry.get("phase", "?").upper()
                    tool = entry.get("tool", entry.get("action", "?"))
                    target = entry.get("target", "?")
                    summary = entry.get("result_summary", entry.get("reason", ""))
                    lines.append(f"[{ts}] {phase:20s} | {tool:15s} → {target:30s} | {summary}")
                except json.JSONDecodeError:
                    continue
        return "\n".join(lines) if lines else "No entries parsed."

    def get_stats(self) -> dict:
        """Return engagement statistics from the audit log."""
        stats = {
            "total_actions": 0,
            "scope_checks": 0,
            "scope_violations": 0,
            "tools_used": set(),
            "targets_touched": set(),
            "findings": 0,
            "exploitation_attempts": 0,
        }
        if not os.path.exists(self.master_log):
            return {k: (list(v) if isinstance(v, set) else v) for k, v in stats.items()}

        with open(self.master_log, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    stats["total_actions"] += 1
                    if entry.get("action") == "scope_check":
                        stats["scope_checks"] += 1
                        if not entry.get("allowed", True):
                            stats["scope_violations"] += 1
                    if entry.get("tool"):
                        stats["tools_used"].add(entry["tool"])
                    if entry.get("target"):
                        stats["targets_touched"].add(entry["target"])
                    if entry.get("action") == "finding_discovered":
                        stats["findings"] += 1
                    if entry.get("action") == "exploitation_attempt":
                        stats["exploitation_attempts"] += 1
                except json.JSONDecodeError:
                    continue

        return {k: (sorted(list(v)) if isinstance(v, set) else v) for k, v in stats.items()}

    def export_for_report(self) -> dict:
        """Export structured data for red-team-report skill consumption."""
        return {
            "engagement_id": self.engagement_id,
            "log_directory": self.base_dir,
            "timeline": self.generate_timeline(),
            "stats": self.get_stats(),
            "log_files": {
                "master": self.master_log,
                "scope": self.scope_log,
                "exploitation": self.exploit_log,
                "findings": self.findings_log,
            },
        }
