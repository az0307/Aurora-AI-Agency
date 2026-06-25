---
name: network-forensics
description: >
  Network traffic capture, packet analysis, protocol dissection, and digital
  evidence preservation for security engagements. Use this skill whenever the
  user mentions packet capture, pcap analysis, Wireshark, tshark, tcpdump,
  network forensics, traffic analysis, protocol analysis, packet inspection,
  network evidence, DNS analysis from captures, HTTP traffic extraction,
  credential sniffing from pcap, malware traffic analysis, C2 detection,
  network timeline reconstruction, or any task involving captured network data.
  Also trigger for: "capture traffic", "analyze this pcap", "what's in this
  capture", "extract files from pcap", "find credentials in traffic",
  "reconstruct network session", or any network evidence analysis task.
  Expert tools: tshark (CLI analysis), tcpdump (capture), Wireshark (GUI),
  NetworkMiner (artifact extraction), zeek (protocol logging).
compatibility:
  tools: [bash, python]
  mcps: [desktop-commander]
  skills: [recon-osint, post-exploit, audit-logger]
---

# Network Forensics Skill

## Overview

Captures and analyzes network traffic for security engagements. Covers live
packet capture, PCAP file analysis, protocol dissection, credential extraction,
file carving from streams, and network timeline reconstruction.

## Expert Tool Selection

| Task | Best Tool | Why |
|------|-----------|-----|
| Live capture (CLI) | **tcpdump** | Lightweight, no GUI needed |
| Live capture (detailed) | **tshark** | Wireshark engine, rich filters |
| PCAP analysis | **tshark** | Scriptable, field extraction |
| GUI analysis | **Wireshark** | Visual, follow streams |
| Artifact extraction | **NetworkMiner** | Auto-extract files, images, creds |
| Protocol logging | **zeek** | Structured logs, conn.log |
| HTTP extraction | **tshark** + filters | Extract URLs, headers, bodies |

## Core Instructions

### Live Capture
```bash
# Basic capture
sudo tcpdump -i {interface} -w /tmp/pentest/{target}/capture.pcap

# Filter by target
sudo tcpdump -i {interface} host {target_ip} -w /tmp/pentest/{target}/capture.pcap

# Capture with ring buffer (long-running)
sudo tcpdump -i {interface} -w /tmp/capture_%Y%m%d_%H%M%S.pcap -G 3600 -W 24
```

### PCAP Analysis with tshark
```bash
# Summary statistics
tshark -r capture.pcap -q -z io,stat,1
tshark -r capture.pcap -q -z conv,ip
tshark -r capture.pcap -q -z endpoints,ip

# Extract HTTP requests
tshark -r capture.pcap -Y "http.request" -T fields \
  -e frame.time -e ip.src -e http.host -e http.request.uri

# Extract DNS queries
tshark -r capture.pcap -Y "dns.qry.name" -T fields \
  -e frame.time -e ip.src -e dns.qry.name -e dns.a

# Find credentials in cleartext protocols
tshark -r capture.pcap -Y "http.authbasic || ftp.request.command==PASS || smtp.auth.password"

# Extract files from HTTP streams
tshark -r capture.pcap --export-objects http,/tmp/pentest/{target}/extracted_files/
```

## Output Format

```json
{
  "capture_file": "/tmp/pentest/example.com/capture.pcap",
  "duration": "1h 23m",
  "packets": 45230,
  "protocols": ["TCP", "UDP", "HTTP", "DNS", "TLS", "SMB"],
  "top_talkers": [
    {"ip": "10.0.0.5", "packets": 12000, "bytes": "45MB"},
    {"ip": "10.0.0.1", "packets": 8500, "bytes": "22MB"}
  ],
  "findings": [
    {"type": "cleartext_credential", "protocol": "HTTP Basic Auth", "target": "10.0.0.5"},
    {"type": "unencrypted_traffic", "protocol": "FTP", "ports": [21]}
  ],
  "extracted_files": 12
}
```

## Output Checklist

- [ ] Capture authorized and within engagement scope
- [ ] PCAP files preserved with integrity hashes
- [ ] Protocol distribution analyzed
- [ ] Credentials and sensitive data identified
- [ ] Files extracted from streams where relevant
- [ ] Findings documented for red-team-report
