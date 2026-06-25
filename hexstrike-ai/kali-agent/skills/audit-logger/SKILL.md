---
name: audit-logger
description: >
  Security engagement audit logging, evidence chain management, and compliance
  trail for penetration testing. Use this skill whenever the user mentions
  audit log, audit trail, engagement logging, evidence collection, chain of
  custody, compliance logging, pentest logging, tool execution logging,
  JSONL log, activity log, forensic evidence, engagement timeline, or any
  request to log, track, or document security testing activities.
  Also trigger for: "log this action", "create audit trail", "evidence chain",
  "what did we do", "engagement timeline", "export activity log", or when
  any other security skill needs to record its actions for compliance.
  This skill is called BY other skills — it is the universal logging layer.
compatibility:
  tools: [bash, python]
  skills: [scope-guard, recon-osint, vuln-analysis, exploit-dev, post-exploit, red-team-report]
---

# Audit Logger Skill

## Overview

Universal audit logging layer for all Kali Agent security activities. Every tool
execution, scope check, finding, and operator decision is recorded in append-only
JSONL format. Provides engagement timeline reconstruction and compliance evidence.

## Log Format (JSONL — one JSON object per line)

```json
{
  "id": "LOG-2026031710000001",
  "timestamp": "2026-03-17T10:00:00.000Z",
  "engagement_id": "ENG-2026-001",
  "phase": "recon | vuln_scan | exploitation | post_exploit | reporting",
  "skill": "recon-osint",
  "tool": "nmap",
  "action": "port_scan",
  "target": "203.0.113.10",
  "scope_check": { "allowed": true, "reason": "Within 203.0.113.0/24" },
  "operator": "az",
  "command": "nmap -sV --top-ports 1000 203.0.113.10",
  "result_summary": "Found 5 open ports: 22,80,443,3306,8080",
  "output_file": "/tmp/pentest/example.com/nmap_initial.xml",
  "output_hash": "sha256:abc123...",
  "severity": "info | low | medium | high | critical",
  "duration_seconds": 45,
  "approval": "auto | operator_confirmed | pending"
}
```

## Log File Locations

```
/tmp/pentest/{engagement_id}/
├── audit.jsonl              ← Master audit log (all activities)
├── scope_audit.jsonl        ← Scope checks only
├── exploitation_log.jsonl   ← Exploitation attempts only
├── findings_log.jsonl       ← Discovered findings only
└── timeline.md              ← Human-readable engagement timeline
```

## Core Instructions

### Logging Functions

```python
import json
import hashlib
from datetime import datetime, timezone

LOG_DIR = "/tmp/pentest/{engagement_id}"

def log_action(engagement_id: str, entry: dict):
    """Append an audit log entry."""
    entry["id"] = f"LOG-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[:20]}"
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    entry["engagement_id"] = engagement_id
    
    log_path = f"/tmp/pentest/{engagement_id}/audit.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

def hash_output(filepath: str) -> str:
    """SHA256 hash of tool output for integrity verification."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"

def generate_timeline(engagement_id: str) -> str:
    """Generate human-readable timeline from audit log."""
    log_path = f"/tmp/pentest/{engagement_id}/audit.jsonl"
    timeline = []
    with open(log_path, "r") as f:
        for line in f:
            entry = json.loads(line)
            timeline.append(
                f"[{entry['timestamp']}] {entry['phase'].upper()} | "
                f"{entry['tool']} → {entry['target']} | "
                f"{entry.get('result_summary', 'N/A')}"
            )
    return "\n".join(timeline)
```

### What Gets Logged

| Event | Logged By | Required Fields |
|-------|-----------|-----------------|
| Scope definition | scope-guard | engagement metadata, scope ranges |
| Scope check | scope-guard | target, result, requesting tool |
| Tool execution | all skills | tool, command, target, output_file |
| Finding discovered | vuln-analysis | severity, CVE, affected asset |
| Exploitation attempt | exploit-dev | target, method, result, approval |
| Session established | post-exploit | session type, access level, host |
| Lateral movement | post-exploit | source host, dest host, method |
| Credential cracked | credential-attack | hash type, method (NOT the password) |
| Report generated | red-team-report | report path, sections, format |

### Integrity Verification

Every tool output file gets hashed at creation. To verify:
```bash
# Verify file integrity
sha256sum /tmp/pentest/{target}/nmap_initial.xml
# Compare with hash stored in audit.jsonl
```

## Output Checklist

- [ ] Audit log initialized at engagement start
- [ ] Every tool execution recorded with command and output hash
- [ ] Scope checks logged separately for quick compliance review
- [ ] Exploitation attempts logged with operator approval status
- [ ] No sensitive data (passwords, PII) in log entries
- [ ] Timeline exportable for report appendix
