---
name: scope-guard
description: >
  Runtime scope enforcement and legal authorization validation for penetration
  testing engagements. Use this skill BEFORE any active security tool execution.
  Trigger whenever: a new target is introduced, engagement scope is defined,
  rules of engagement are discussed, authorization needs checking, scope
  boundaries need validation, an IP or domain needs checking against allowed
  ranges, "is this in scope", "can I scan this", "check scope", "rules of
  engagement", "RoE", "scope validation", "authorization check", "legal check",
  "engagement boundaries", or any time a security tool is about to touch a target.
  This skill is the mandatory gate — no recon, scanning, exploitation, or
  post-exploitation should proceed without scope-guard confirming authorization.
  Also trigger for: CIDR range validation, domain wildcard scope, time window
  enforcement, excluded host checking, or "add to scope" / "remove from scope".
compatibility:
  tools: [bash, python]
  skills: [recon-osint, vuln-analysis, exploit-dev, post-exploit]
---

# Scope Guard — Authorization & Scope Enforcement

## Overview

Mandatory pre-execution gate for all security testing activities. Validates
that targets are within authorized scope, engagement is within time windows,
and rules of engagement are being followed. No active tool should run without
scope-guard approval.

## Why This Exists

Running security tools against unauthorized targets is a criminal offense in
most jurisdictions (AU: Criminal Code Act 1995 s477-478, US: CFAA, UK: CMA 1990).
This skill exists to prevent accidental or intentional out-of-scope testing.

## Quick Start — Scope Definition

### Step 1 — Capture Engagement Authorization
Before any testing, the operator MUST provide:

```json
{
  "engagement": {
    "id": "ENG-2026-001",
    "client": "Example Corp",
    "type": "external_pentest | web_app | internal | red_team | ctf",
    "authorization": "Written authorization obtained — reference: [doc_id]",
    "tester": "Az / AutoBoros.ai",
    "start_date": "2026-03-17",
    "end_date": "2026-03-31",
    "time_window": "09:00-17:00 AEST | 24/7 | custom",
    "emergency_contact": "client-security@example.com"
  },
  "scope": {
    "in_scope": {
      "domains": ["*.example.com", "api.example.com"],
      "ip_ranges": ["203.0.113.0/24", "198.51.100.10"],
      "urls": ["https://app.example.com/*"],
      "ports": "all | 1-65535 | 80,443,8080"
    },
    "out_of_scope": {
      "domains": ["mail.example.com", "production-db.example.com"],
      "ip_ranges": ["203.0.113.250/32"],
      "notes": "Do not test production database. Do not perform DoS."
    },
    "rules_of_engagement": [
      "No denial of service testing",
      "No social engineering without separate approval",
      "Stop testing if production impact detected",
      "Report critical findings within 24 hours"
    ]
  }
}
```

### Step 2 — Validate a Target Before Tool Execution

Every skill in the pentest chain must call scope-guard before running:

```python
import ipaddress
import fnmatch
import re
from datetime import datetime, timezone

class ScopeGuard:
    def __init__(self, scope_config: dict):
        self.config = scope_config
        self.in_scope_nets = [
            ipaddress.ip_network(r, strict=False) 
            for r in scope_config["scope"]["in_scope"].get("ip_ranges", [])
        ]
        self.out_scope_nets = [
            ipaddress.ip_network(r, strict=False)
            for r in scope_config["scope"]["out_of_scope"].get("ip_ranges", [])
        ]
        self.in_scope_domains = scope_config["scope"]["in_scope"].get("domains", [])
        self.out_scope_domains = scope_config["scope"]["out_of_scope"].get("domains", [])

    def check_ip(self, ip: str) -> dict:
        """Check if an IP is within authorized scope."""
        addr = ipaddress.ip_address(ip)
        # Check exclusions first
        for net in self.out_scope_nets:
            if addr in net:
                return {"allowed": False, "reason": f"{ip} is EXCLUDED from scope ({net})"}
        # Check inclusions
        for net in self.in_scope_nets:
            if addr in net:
                return {"allowed": True, "reason": f"{ip} is within scope ({net})"}
        return {"allowed": False, "reason": f"{ip} is NOT in any authorized scope range"}

    def check_domain(self, domain: str) -> dict:
        """Check if a domain is within authorized scope."""
        # Check exclusions first
        for pattern in self.out_scope_domains:
            if fnmatch.fnmatch(domain, pattern) or domain == pattern:
                return {"allowed": False, "reason": f"{domain} is EXCLUDED from scope"}
        # Check inclusions
        for pattern in self.in_scope_domains:
            if fnmatch.fnmatch(domain, pattern) or domain == pattern:
                return {"allowed": True, "reason": f"{domain} matches scope pattern {pattern}"}
        return {"allowed": False, "reason": f"{domain} is NOT in authorized scope"}

    def check_time_window(self) -> dict:
        """Check if current time is within engagement window."""
        now = datetime.now(timezone.utc)
        start = datetime.fromisoformat(self.config["engagement"]["start_date"])
        end = datetime.fromisoformat(self.config["engagement"]["end_date"])
        if now.date() < start.date():
            return {"allowed": False, "reason": "Engagement has not started yet"}
        if now.date() > end.date():
            return {"allowed": False, "reason": "Engagement window has expired"}
        return {"allowed": True, "reason": "Within engagement time window"}

    def validate(self, target: str) -> dict:
        """Full validation — call this before every tool execution."""
        time_check = self.check_time_window()
        if not time_check["allowed"]:
            return time_check
        try:
            return self.check_ip(target)
        except ValueError:
            return self.check_domain(target)
```

### Step 3 — Enforcement in Practice

**Before recon-osint runs:**
```
scope-guard.validate("example.com") → {allowed: true}
scope-guard.validate("mail.example.com") → {allowed: false, reason: "EXCLUDED"}
```

**Before vuln-analysis scans:**
```
scope-guard.validate("203.0.113.10") → {allowed: true}
scope-guard.validate("10.0.0.1") → {allowed: false, reason: "NOT in scope"}
```

**Before exploit-dev executes:**
```
scope-guard.validate(target) → must return allowed: true
scope-guard.check_time_window() → must return allowed: true
```

## Approval Escalation Matrix

| Action | Approval Required |
|--------|-------------------|
| Passive recon (DNS, whois, OSINT) | Scope check only |
| Active scanning (nmap, nuclei) | Scope check + time window |
| Exploitation (metasploit, sqlmap) | Scope + operator confirmation |
| Lateral movement to new host | Scope + per-host operator confirmation |
| Credential brute force | Scope + rate limit confirmation |
| Social engineering | Separate written authorization |
| Wireless testing | Physical presence + authorization |
| DoS/stress testing | Separate written authorization |

## Audit Integration

Every scope check MUST be logged:
```json
{
  "timestamp": "2026-03-17T10:00:00Z",
  "action": "scope_check",
  "target": "203.0.113.10",
  "result": "allowed",
  "tool_requesting": "nmap",
  "operator": "az",
  "engagement_id": "ENG-2026-001"
}
```

Log to: `/tmp/pentest/{engagement_id}/scope_audit.jsonl`

## CTF / Lab Mode

For CTF platforms (HackTheBox, TryHackMe, PentesterLab), scope-guard can
operate in relaxed mode:

```json
{
  "engagement": {
    "type": "ctf",
    "platform": "hackthebox",
    "authorization": "Platform ToS accepted"
  },
  "scope": {
    "in_scope": {
      "ip_ranges": ["10.10.10.0/24"],
      "notes": "CTF lab — all targets on this subnet are authorized"
    },
    "out_of_scope": { "ip_ranges": [], "domains": [] }
  }
}
```

## Output Checklist

- [ ] Engagement authorization documented before any testing
- [ ] Scope definition captured (in-scope + out-of-scope)
- [ ] Time window validated
- [ ] Every target checked before tool execution
- [ ] All scope checks logged to audit trail
- [ ] Out-of-scope attempts blocked and logged
- [ ] Operator informed of any scope violations immediately
