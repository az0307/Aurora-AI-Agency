"""
ScopeGuard — Runtime scope enforcement for Kali Agent
Drop into HexStrike's app.py or import as module.
AutoBoros.ai | 2026-03-27
"""

import ipaddress
import fnmatch
import json
import os
from datetime import datetime, timezone, date
from typing import Optional


class ScopeGuard:
    """Validates targets against authorized engagement scope before tool execution."""

    def __init__(self, scope_config: dict):
        self.config = scope_config
        self.engagement = scope_config.get("engagement", {})
        scope = scope_config.get("scope", {})
        in_scope = scope.get("in_scope", {})
        out_scope = scope.get("out_of_scope", {})

        # Parse IP ranges
        self.in_scope_nets = [
            ipaddress.ip_network(r, strict=False)
            for r in in_scope.get("ip_ranges", [])
        ]
        self.out_scope_nets = [
            ipaddress.ip_network(r, strict=False)
            for r in out_scope.get("ip_ranges", [])
        ]

        # Domain patterns
        self.in_scope_domains = in_scope.get("domains", [])
        self.out_scope_domains = out_scope.get("domains", [])

        # Allowed URLs
        self.in_scope_urls = in_scope.get("urls", [])

        # Engagement dates
        self.start_date = self._parse_date(self.engagement.get("start_date"))
        self.end_date = self._parse_date(self.engagement.get("end_date"))

        # Engagement directory
        eid = self.engagement.get("id", "unknown")
        self.log_dir = f"/tmp/pentest/{eid}"
        os.makedirs(self.log_dir, exist_ok=True)

    @staticmethod
    def _parse_date(d: Optional[str]) -> Optional[date]:
        if not d:
            return None
        try:
            return datetime.fromisoformat(d).date()
        except (ValueError, TypeError):
            return None

    def check_ip(self, ip: str) -> dict:
        """Check if an IP address is within authorized scope."""
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return {"allowed": False, "reason": f"'{ip}' is not a valid IP address"}

        # Exclusions take priority
        for net in self.out_scope_nets:
            if addr in net:
                return {
                    "allowed": False,
                    "reason": f"{ip} is EXCLUDED from scope (matches {net})",
                    "target": ip,
                    "check_type": "ip",
                }

        # Check inclusions
        for net in self.in_scope_nets:
            if addr in net:
                return {
                    "allowed": True,
                    "reason": f"{ip} is within authorized scope ({net})",
                    "target": ip,
                    "check_type": "ip",
                }

        return {
            "allowed": False,
            "reason": f"{ip} is NOT in any authorized scope range",
            "target": ip,
            "check_type": "ip",
        }

    def check_domain(self, domain: str) -> dict:
        """Check if a domain is within authorized scope."""
        domain = domain.lower().strip()

        # Exclusions first
        for pattern in self.out_scope_domains:
            if fnmatch.fnmatch(domain, pattern.lower()) or domain == pattern.lower():
                return {
                    "allowed": False,
                    "reason": f"{domain} is EXCLUDED from scope (matches {pattern})",
                    "target": domain,
                    "check_type": "domain",
                }

        # Check inclusions
        for pattern in self.in_scope_domains:
            if fnmatch.fnmatch(domain, pattern.lower()) or domain == pattern.lower():
                return {
                    "allowed": True,
                    "reason": f"{domain} matches authorized scope pattern '{pattern}'",
                    "target": domain,
                    "check_type": "domain",
                }

        return {
            "allowed": False,
            "reason": f"{domain} is NOT in authorized scope",
            "target": domain,
            "check_type": "domain",
        }

    def check_time_window(self) -> dict:
        """Check if current time is within engagement window."""
        today = datetime.now(timezone.utc).date()

        if self.start_date and today < self.start_date:
            return {
                "allowed": False,
                "reason": f"Engagement starts {self.start_date} — not yet active",
            }
        if self.end_date and today > self.end_date:
            return {
                "allowed": False,
                "reason": f"Engagement ended {self.end_date} — window expired",
            }
        return {"allowed": True, "reason": "Within engagement time window"}

    def validate(self, target: str) -> dict:
        """
        Full validation — call this before EVERY tool execution.
        Accepts IP, domain, or URL. Returns {allowed: bool, reason: str}.
        """
        # Time window check
        time_check = self.check_time_window()
        if not time_check["allowed"]:
            self._log_check(target, time_check)
            return time_check

        # Strip protocol/path for URL targets
        clean_target = target
        if "://" in target:
            from urllib.parse import urlparse
            parsed = urlparse(target)
            clean_target = parsed.hostname or target

        # Try IP first, fall back to domain
        try:
            ipaddress.ip_address(clean_target)
            result = self.check_ip(clean_target)
        except ValueError:
            result = self.check_domain(clean_target)

        self._log_check(target, result)
        return result

    def _log_check(self, target: str, result: dict):
        """Log every scope check to JSONL audit trail."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "engagement_id": self.engagement.get("id", "unknown"),
            "action": "scope_check",
            "target": target,
            "allowed": result["allowed"],
            "reason": result["reason"],
        }
        log_path = os.path.join(self.log_dir, "scope_audit.jsonl")
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError:
            pass  # Don't fail tool execution if logging fails

    def is_ctf_mode(self) -> bool:
        """Check if engagement is a CTF/lab (relaxed guardrails)."""
        return self.engagement.get("type", "").lower() in ("ctf", "lab", "hackthebox", "tryhackme")

    def get_scope_summary(self) -> str:
        """Human-readable scope summary for display."""
        in_s = self.config.get("scope", {}).get("in_scope", {})
        out_s = self.config.get("scope", {}).get("out_of_scope", {})
        lines = [
            f"Engagement: {self.engagement.get('id', 'N/A')}",
            f"Client: {self.engagement.get('client', 'N/A')}",
            f"Type: {self.engagement.get('type', 'N/A')}",
            f"Window: {self.start_date} → {self.end_date}",
            f"In-scope domains: {', '.join(in_s.get('domains', []))}",
            f"In-scope IPs: {', '.join(in_s.get('ip_ranges', []))}",
            f"Excluded domains: {', '.join(out_s.get('domains', []))}",
            f"Excluded IPs: {', '.join(out_s.get('ip_ranges', []))}",
        ]
        return "\n".join(lines)


# --- Factory for quick setup ---

def load_scope_from_file(path: str) -> ScopeGuard:
    """Load scope config from a JSON file."""
    with open(path, "r") as f:
        config = json.load(f)
    return ScopeGuard(config)


def create_ctf_scope(target_range: str, platform: str = "hackthebox") -> ScopeGuard:
    """Quick CTF/lab scope — everything in the target range is authorized."""
    return ScopeGuard({
        "engagement": {
            "id": f"CTF-{datetime.now().strftime('%Y%m%d')}",
            "client": platform,
            "type": "ctf",
            "authorization": f"Platform ToS accepted — {platform}",
            "start_date": "2020-01-01",
            "end_date": "2099-12-31",
        },
        "scope": {
            "in_scope": {"ip_ranges": [target_range], "domains": ["*"]},
            "out_of_scope": {"ip_ranges": [], "domains": []},
        },
    })
