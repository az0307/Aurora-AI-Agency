# KALI MCP CONTAINER — TOOL INVENTORY
# What's installed in the kali-mcp Docker container
# Source: kalilinux/kali-rolling + apt installs in Dockerfile

---

## Reconnaissance

```
nmap              Port scanning, service detection, OS fingerprinting
masscan           High-speed port scanner (100k pps capable)
rustscan          Fast port scanner (finds ports, passes to nmap)
netdiscover       ARP-based network discovery
nbtscan           NetBIOS scanner for Windows environments
enum4linux-ng     Samba / Windows enumeration
```

## Web Testing

```
gobuster          Directory/DNS/vhost brute-forcing
ffuf              Fast web fuzzer (multi-purpose)
feroxbuster       Recursive content discovery in Rust
dirsearch         Web path scanner with extensive wordlist support
nikto             Web server vulnerability scanner (legacy)
wpscan            WordPress security scanner
joomscan          Joomla security scanner
sqlmap            SQL injection detection and exploitation
dalfox            XSS scanner (fast, accurate)
nuclei            Template-based vulnerability scanner (4000+ templates)
```

## Password Attacks

```
hashcat           GPU-accelerated password cracking
john              CPU-based password cracking (John the Ripper)
hydra             Online brute-force tool (multi-protocol)
medusa            Parallel brute-force tool
crackmapexec      SMB/WinRM/MSSQL brute-force + enum
kerbrute          Kerberos username enum and brute-force
responder         LLMNR/NBT-NS/MDNS poisoner + credential capture
```

## Exploitation

```
metasploit-framework  Exploitation framework (msfconsole, msfvenom)
searchsploit          Local ExploitDB search
impacket-scripts      14 scripts: psexec, secretsdump, getTGT, etc.
evil-winrm            WinRM shell with upload/download/pass-the-hash
```

## Active Directory

```
bloodhound            AD attack path visualization (Neo4j backend)
sharphound            BloodHound data collector (.NET)
ldapdomaindump        LDAP enumeration and data dump
kerbrute              AS-REP roasting, Kerberoasting setup
crackmapexec          SMB enum, pass-the-hash, spray
impacket-GetNPUsers   AS-REP roasting
impacket-GetUserSPNs  Kerberoasting
impacket-secretsdump  DCSync, LSA dump
```

## Post-Exploitation

```
mimikatz          Credential extraction (Windows — via wine or meterpreter)
linux-exploit-suggester  Linux privesc suggester
linpeas           Linux privilege escalation script
winpeas           Windows privilege escalation script
pspy              Process monitoring without root (Linux)
```

## Network Analysis

```
wireshark/tshark  Packet capture and analysis
tcpdump           Command-line packet capture
ettercap          MITM attacks + ARP poisoning
bettercap         Modern MITM framework
netcat            TCP/UDP Swiss army knife
socat             Advanced netcat (SSL, proxies)
```

## Wireless

```
aircrack-ng       WEP/WPA cracking suite
airmon-ng         Monitor mode management
airodump-ng       802.11 packet capture
aireplay-ng       Packet injection
hcxdumptool       PMKID capture (no client needed)
hcxpcapngtool     Convert captures for hashcat
reaver             WPS brute-force
wash              WPS-enabled AP discovery
```

## Forensics / Reverse Engineering

```
binwalk           Firmware analysis + extraction
foremost          File carving
volatility3       Memory forensics
strings           String extraction from binaries
file              File type identification
binutils          Object file tools (nm, objdump, readelf)
gdb               GNU debugger
radare2           Reverse engineering framework
ltrace/strace     Library/syscall tracing
```

## Utilities

```
curl / wget       HTTP clients
python3           Python 3 + pip
python3-pip       Package installer
git               Version control
jq                JSON processor
tmux              Terminal multiplexer (used by Kali MCP for sessions)
proxychains4      Proxy chains for pivoting
ssh               OpenSSH client and server
sshuttle          Transparent proxy over SSH
```

## NOT Installed (Use HexStrike Instead)

```
# These are available via hexstrike-ai:
# subfinder, amass, httpx, dnsx, naabu, katana, gau
# These are too large for the container:
# Burp Suite Pro, Cobalt Strike
```

---

## Adding Tools at Runtime

```bash
# Via Kali MCP:
kali_exec("sudo apt update && sudo apt install -y [PACKAGE]")

# Verify install:
kali_exec("which [TOOL] && [TOOL] --version")
```

## Tool Locations

```
/usr/bin/          Most Kali tools
/usr/share/        Config files, wordlists, scripts
/opt/              Manually installed tools
/home/kali/        User tools (linpeas, winpeas, etc.)
/usr/share/wordlists/  Default wordlists
/usr/share/seclists/   SecLists (installed separately)
```
