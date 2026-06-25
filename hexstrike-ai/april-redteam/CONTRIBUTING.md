# CONTRIBUTING — April 2026 Red Team Stack

Community contributions welcome. Read before submitting.

---

## What We Accept

✅ New playbooks for attack categories not yet covered
✅ Updated tool versions and install instructions
✅ New Claude Code skills (`.md` format in `skills/`)
✅ Bug fixes in shell scripts or Python MCP servers
✅ Docker/container improvements
✅ Documentation improvements
✅ New wordlist references and resources
✅ Integration configs for new MCP-compatible AI tools

❌ Malicious tools, code designed for unauthorized access
❌ Real credentials, API keys, or personal data
❌ PoC exploits without explicit authorized-use disclaimers
❌ Anything that violates GitHub's terms of service

---

## Pull Request Process

1. **Fork** the repo
2. **Branch** off `main`: `git checkout -b feature/your-feature`
3. **Test** your changes locally
4. **No loot directory** — ensure `.gitignore` is respected
5. **No secrets** — run `git diff` and check for API keys
6. **PR description** — explain what, why, and how you tested it

---

## Adding a Playbook

```
playbooks/[attack-type].md

Structure:
# PLAYBOOK: [TITLE]
# April 2026 Red Team Stack
# [One line description]

---

## Overview / Context

## Prerequisites

## Phase 1 — ...
## Phase 2 — ...
## ...

## Evidence Collection (loot/ structure)

## Quick Reference

---

*April 2026 | [context]*
```

---

## Adding a Claude Code Skill

```
skills/[skill-name].md

Structure:
# SKILL: [skill-name]
# Description
# Triggered when: [phrases]

## Trigger Phrases

## Authorization Gate (if applicable)

## Workflow A — ...
## Workflow B — ...

## Integration with Stack

## Cost Notes
```

---

## Coding Standards

**Shell scripts:**
- `set -euo pipefail` at top
- `shellcheck` must pass
- Color variables: `RED GRN YLW BLU NC`
- Functions: `log()` `warn()` `err()`

**Python:**
- Type hints where practical
- FastMCP pattern for all MCP servers
- Async where performance matters
- All subprocess calls via `kali_exec()` pattern

**Markdown:**
- Use fenced code blocks with language tags
- Tables for comparisons
- Section headers with `---` separators

---

## Security Disclosure

If you find a security issue IN THIS REPO (not in third-party tools):
- Do NOT open a public issue
- Email: [0x4m4's contact via GitHub profile]
- Include: description, reproduction steps, impact assessment

---

*This stack is for authorized security research only. By contributing, you agree that your contributions are for legitimate, authorized use.*
