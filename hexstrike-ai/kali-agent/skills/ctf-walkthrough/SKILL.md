---
name: ctf-walkthrough
description: >
  Generate structured CTF walkthrough writeups from engagement data, findings,
  and attack paths. Use this skill whenever the user mentions CTF writeup,
  walkthrough, write-up, CTF solution, box writeup, challenge writeup,
  HackTheBox writeup, TryHackMe writeup, "write up this box", "document
  how I solved", "create a walkthrough for", or any request to document a
  CTF/lab solution in educational format.
  Also trigger for: "writeup for HTB", "THM walkthrough", "document the
  attack path", "how did we solve this", or when red-team-report is called
  with engagement type CTF.
  Produces clean Markdown writeups with technique explanations, command
  output, and learning notes — suitable for blog posts or portfolio.
compatibility:
  tools: [bash, python]
  skills: [red-team-report, recon-osint, vuln-analysis, exploit-dev, post-exploit, audit-logger]
---

# CTF Walkthrough Generator

## Overview

Generates structured, educational CTF writeups from engagement data. Unlike
the red-team-report skill (client deliverable), this skill produces learning-
focused documentation with technique explanations and teaching notes.

## Output Structure

```markdown
# [Box Name] — [Platform] Writeup

**Difficulty:** Easy / Medium / Hard / Insane
**OS:** Linux / Windows
**IP:** 10.10.10.X
**Skills:** [list of techniques used]

---

## Reconnaissance

### Port Scan
[nmap output + explanation of what each port/service means]

### Service Enumeration
[Detail each interesting service found]

## Foothold

### Vulnerability Discovery
[How the vuln was found, what tool, what it means]

### Exploitation
[Step-by-step with commands and output]
[Explain WHY this works, not just WHAT to type]

## Privilege Escalation

### Enumeration
[LinPEAS/WinPEAS output analysis]

### Escalation Path
[Technique used, MITRE ATT&CK reference]
[Commands with explanation]

## Post-Exploitation

### Flags
- User flag: `[hash]` (location: /home/user/user.txt)
- Root flag: `[hash]` (location: /root/root.txt)

## Key Takeaways

1. [What technique was learned]
2. [What tool was practiced]
3. [What concept was reinforced]

## MITRE ATT&CK Mapping

| Technique | ID | Phase |
|-----------|------|-------|
| [name] | T[xxxx] | [phase] |
```

## Core Instructions

### Step 1 — Collect Data

Ingest from these sources (in priority order):
1. Audit log: `/tmp/pentest/{engagement_id}/audit.jsonl`
2. Findings log: `/tmp/pentest/{engagement_id}/findings_log.jsonl`
3. Tool outputs: `/tmp/pentest/{engagement_id}/*.txt` / `*.xml` / `*.json`
4. Operator notes (from conversation context)
5. Scope config for engagement metadata

### Step 2 — Structure the Writeup

Map engagement phases to writeup sections:
- recon-osint → Reconnaissance section
- vuln-analysis → Vulnerability Discovery section
- exploit-dev → Exploitation / Foothold section
- post-exploit → Privilege Escalation section
- credential-attack → if hashes were cracked, include in Exploitation or PrivEsc

### Step 3 — Write with Teaching Intent

For each technique used, include:
1. **What** — the command that was run
2. **Why** — why this technique was chosen
3. **How** — how the output was interpreted
4. **Learn** — what concept this teaches

Example:
```markdown
### SUID Binary Exploitation

We found the `find` binary with the SUID bit set:

```bash
find / -perm -4000 2>/dev/null
# Output: /usr/bin/find (among others)
```

The SUID bit means this binary runs with the owner's privileges (root)
regardless of who executes it. Since `find` has an `-exec` flag, we can
spawn a shell as root:

```bash
find . -exec /bin/bash -p \;
```

The `-p` flag preserves the effective UID, giving us a root shell.

**MITRE ATT&CK:** T1068 — Exploitation for Privilege Escalation
**GTFOBins:** https://gtfobins.github.io/gtfobins/find/
```

### Step 4 — Add Context

Include where relevant:
- Links to relevant CVE pages
- GTFOBins references for SUID/capability exploits
- HackTricks references for techniques
- Alternative approaches that could have worked
- What defensive measures would have prevented the attack

### Step 5 — Output

Generate as Markdown file:
```
/tmp/pentest/{engagement_id}/reports/{box_name}_writeup.md
```

For blog-ready format, also generate with frontmatter:
```yaml
---
title: "Box Name — Platform Writeup"
date: 2026-04-03
tags: [ctf, hackthebox, linux, privesc]
difficulty: medium
---
```

## Output Checklist

- [ ] All phases documented (recon → foothold → privesc → flags)
- [ ] Every command includes explanation of WHY, not just WHAT
- [ ] Tool output shown (trimmed to relevant sections)
- [ ] MITRE ATT&CK techniques mapped
- [ ] Alternative approaches mentioned
- [ ] Key takeaways section with learning points
- [ ] Flags documented (user + root if applicable)
- [ ] Writeup suitable for blog/portfolio publication
