# SKILL: threat-hunt
# Proactive threat hunting — find attacker presence in target environment
# Triggered when: "hunt", "IOC", "indicators", "check for compromise", "APT"

## Trigger Phrases
- "hunt for threats in [environment]"
- "check for indicators of compromise"
- "look for IOCs: [list]"
- "is [environment] compromised"
- "hunt for [technique] activity"
- "check MITRE ATT&CK [technique]"

## Overview
Threat hunting flips the pentester mindset:
Instead of attacking, you're looking for evidence that someone else already did.
Common during red team exercises where blue team awareness is being tested,
and during post-engagement cleanup verification.

---

## WORKFLOW A — Windows Event Log Hunting (via Kali MCP → Windows)

```bash
# Requires: access to Windows system logs or SIEM export

# Suspicious PowerShell execution
kali_exec("python3 -c \"
import subprocess
# If connected to Windows via evil-winrm or similar:
# Get PowerShell history
cmd = 'type C:\\\\Users\\\\*\\\\AppData\\\\Roaming\\\\Microsoft\\\\Windows\\\\PowerShell\\\\PSReadLine\\\\ConsoleHost_history.txt'
\"")

# Event Log queries (if WinRM/RDP access)
# Event ID 4624 = Logon, 4625 = Failed logon, 4688 = Process create
# 4698/4702 = Scheduled task create/modify
# 4720/4722/4724/4728 = Account creation/enable/password reset/group add
# 7045 = New service installed
# 1102 = Security log cleared (VERY suspicious)

# Via Python + winrm (from Kali):
kali_write_file("/tmp/hunt_events.ps1", """
# Hunt for suspicious activity
$suspiciousEvents = @(
    Get-WinEvent -FilterHashtable @{LogName='Security';Id=4625} -MaxEvents 100,  # Failed logons
    Get-WinEvent -FilterHashtable @{LogName='Security';Id=4688} -MaxEvents 100,  # Process creation
    Get-WinEvent -FilterHashtable @{LogName='Security';Id=1102} -MaxEvents 10    # Log cleared
)

foreach ($event in $suspiciousEvents) {
    [PSCustomObject]@{
        TimeCreated = $event.TimeCreated
        EventId = $event.Id
        Message = $event.Message | Select-String 'Account Name|Process Name|Subject' | Select-Object -First 3
    }
}
""")
```

---

## WORKFLOW B — Linux Log Hunting

```bash
# Auth log analysis — failed logins, sudo usage, SSH
kali_exec("cat /var/log/auth.log | grep -E 'Failed|Invalid|ROOT|sudo' | tail -100")
kali_exec("last | head -30")  # Recent logins
kali_exec("lastb | head -30")  # Failed logins

# Cron backdoors
kali_exec("cat /etc/crontab")
kali_exec("ls -la /etc/cron.*/ 2>/dev/null")
kali_exec("crontab -l 2>/dev/null")
kali_exec("for user in $(cut -d: -f1 /etc/passwd); do crontab -l -u $user 2>/dev/null; done")

# Suspicious processes
kali_exec("ps aux | grep -E 'nc|ncat|socat|meterpreter|empire|cobalt' | grep -v grep")
kali_exec("lsof -i | grep LISTEN")
kali_exec("ss -tulpn")

# Recently modified files (attacker artifacts)
kali_exec("find / -newer /tmp/.timeref -type f 2>/dev/null | grep -v proc | grep -v sys | head -50")
kali_exec("find /tmp /var/tmp /dev/shm -type f 2>/dev/null")

# SUID backdoors planted
kali_exec("find / -perm -u=s -type f 2>/dev/null")

# Unusual user accounts
kali_exec("cat /etc/passwd | awk -F: '$3 >= 1000 || $3 == 0 {print}'")
kali_exec("cat /etc/shadow | awk -F: '$2 != \"!\" && $2 != \"*\" {print $1}'")

# Shell history
kali_exec("cat /home/*/.bash_history 2>/dev/null | head -100")
kali_exec("cat /root/.bash_history 2>/dev/null | head -50")
```

---

## WORKFLOW C — Network IOC Detection

```bash
# Check for known-bad IPs/domains (from threat feeds)
IOC_IPS = ["185.220.101.0/24", "194.165.16.0/24"]  # Tor exit nodes / known C2

kali_exec("ss -tulpn | grep ESTABLISHED")
kali_exec("netstat -antp 2>/dev/null | grep ESTABLISHED | grep -v 'localhost\|127.0.0\|::1'")

# DNS queries for suspicious domains
kali_exec("cat /var/log/syslog | grep 'named\|dnsmasq' | grep -v 'NOERROR' | tail -50")

# Scan for C2 beaconing patterns
kali_exec("tcpdump -i eth0 -w /tmp/traffic.pcap -G 300 -W 1 2>/dev/null &")
# After 5 min:
kali_exec("tcpdump -r /tmp/traffic.pcap -nn | awk '{print $3}' | cut -d. -f1-4 | sort | uniq -c | sort -rn | head -20")
```

---

## WORKFLOW D — MITRE ATT&CK Coverage Check

```bash
# Check for common persistence mechanisms
PERSISTENCE_CHECKS = [
    # T1053 - Scheduled Tasks
    "schtasks /query /fo csv 2>/dev/null | grep -iv 'Microsoft\\|Windows' | head -20",
    # T1547 - Registry Run Keys (via wine or powershell)
    "reg query HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run 2>/dev/null",
    # T1136 - Create Account
    "net user 2>/dev/null",
    # T1543 - Create Service
    "sc query type= all 2>/dev/null | grep -i 'service name' | head -20",
]

# Check for lateral movement artifacts
LATERAL_CHECKS = [
    # T1021 - Remote Services
    "find / -name '.ssh' -type d 2>/dev/null | head -10",
    "cat /root/.ssh/authorized_keys 2>/dev/null",
    "cat /home/*/.ssh/authorized_keys 2>/dev/null",
    # T1550 - Use Alternate Auth
    "find / -name '*.kdbx' -o -name '*.keystore' 2>/dev/null | head -5",
]

for check in PERSISTENCE_CHECKS + LATERAL_CHECKS:
    kali_exec(check)
```

---

## WORKFLOW E — Memory Forensics (Volatile Evidence)

```bash
# Process memory dumps for indicators
kali_exec("ps aux --no-headers | sort -k4 -rn | head -10")  # Top memory consumers

# Check for injected code (hollowed processes)
kali_exec("for pid in $(ls /proc | grep '^[0-9]'); do [ -d /proc/$pid ] && diff /proc/$pid/exe /proc/$pid/maps 2>/dev/null; done 2>/dev/null | head -20")

# Look for deleted executables still running (common malware technique)
kali_exec("ls -la /proc/*/exe 2>/dev/null | grep deleted")

# Memory-mapped files (potential injections)
kali_exec("grep -l 'heap\|stack\[' /proc/*/maps 2>/dev/null | head -10")

# Volatility3 (if available) for full memory forensics
kali_exec("python3 /opt/volatility3/vol.py -f /tmp/memory.dump windows.pslist 2>/dev/null || echo 'Volatility not available or no dump'")
```

---

## IOC Cross-Reference (with VulnGPT + HexStrike)

```
Given IOC list: [IP_LIST], [DOMAIN_LIST], [HASH_LIST]

Using hexstrike-ai OSINT:
1. Check each IP against VirusTotal, Shodan, AbuseIPDB
2. Check each domain against VirusTotal, URLhaus
3. Check each file hash against VirusTotal

Using vulngpt:
4. Cross-reference IOCs with known APT groups (MITRE ATT&CK)
5. Identify campaign signatures
6. Suggest defensive countermeasures

Save IOC report to: loot/[MISSION]/threat_hunt/ioc_analysis.md
```

---

## Threat Hunt Output Template

```markdown
# Threat Hunt Report — [ENVIRONMENT]
Date: [DATE] | Hunter: [NAME]

## Executive Summary
[Compromise confirmed / No confirmed compromise / Evidence of persistence]

## IOCs Investigated
| IOC | Type | Status | Source |
|-----|------|--------|--------|
| [IP] | IP | MALICIOUS | VirusTotal |
| [DOMAIN] | Domain | SUSPICIOUS | URLhaus |

## Findings
### Finding 1: [DESCRIPTION]
- First seen: [DATE]
- Evidence: [LOG EXTRACT]
- MITRE ATT&CK: T[XXXX] - [Technique Name]
- Severity: [HIGH/MEDIUM/LOW]

## Timeline of Attacker Activity
| Time | Activity | Evidence |
|------|----------|---------|

## Recommended Actions
1. [IMMEDIATE]
2. [SHORT TERM]
3. [LONG TERM]
```

---

## Cost Notes
- Log analysis: minimal tokens (Sonnet)
- IOC cross-reference: ~5-15k tokens per IOC batch
- Full hunt report: ~20-30k tokens (Sonnet)
- Memory forensics: tool-cost only, minimal LLM
