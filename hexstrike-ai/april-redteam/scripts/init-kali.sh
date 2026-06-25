#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# init-kali.sh — Post-build Kali container tool setup
# Run once after: docker compose up -d kali-mcp
# Usage: docker exec kali-mcp bash /opt/init-kali.sh
# OR:    ./scripts/init-kali.sh
# ─────────────────────────────────────────────────────────────

set -euo pipefail
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; BLU='\033[0;34m'; NC='\033[0m'

log()  { echo -e "${GRN}[+]${NC} $*"; }
warn() { echo -e "${YLW}[!]${NC} $*"; }
info() { echo -e "${BLU}[*]${NC} $*"; }

KALI_SSH="${KALI_SSH:-localhost}"
KALI_PORT="${KALI_PORT:-2222}"
KALI_USER="${KALI_USER:-kali}"
KALI_KEY="${KALI_KEY:-$HOME/.ssh/kali_mcp_ed25519}"

# Run in container via SSH or exec
kali() {
    if [[ "${IN_CONTAINER:-}" == "1" ]]; then
        bash -c "$*"
    else
        ssh -i "$KALI_KEY" -p "$KALI_PORT" -o StrictHostKeyChecking=no \
            "$KALI_USER@$KALI_SSH" "$*"
    fi
}

echo ""
echo -e "${BLU}══════════════════════════════════════════════${NC}"
echo -e "${BLU}  KALI MCP — POST-BUILD INITIALIZATION${NC}"
echo -e "${BLU}══════════════════════════════════════════════${NC}"
echo ""

# ── APT update ────────────────────────────────────────────────
info "Updating package lists..."
kali "sudo apt update -qq 2>/dev/null"
log "Package lists updated"

# ── Core pentesting tools ─────────────────────────────────────
info "Installing core tools..."
kali "sudo apt install -y -qq \
    nmap masscan netdiscover nbtscan \
    gobuster ffuf feroxbuster dirsearch \
    sqlmap dalfox nikto wpscan \
    hashcat john hydra medusa \
    crackmapexec kerbrute responder \
    metasploit-framework searchsploit \
    evil-winrm bloodhound \
    impacket-scripts \
    aircrack-ng hcxdumptool hcxpcapngtool reaver \
    binwalk foremost strings file binutils \
    gdb radare2 ltrace strace \
    proxychains4 sshuttle tmux jq curl wget git python3-pip \
    2>/dev/null"
log "Core tools installed"

# ── Nuclei (latest) ───────────────────────────────────────────
info "Installing Nuclei..."
kali "if ! command -v nuclei &>/dev/null; then
    wget -q https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip -O /tmp/nuclei.zip
    unzip -q /tmp/nuclei.zip -d /tmp/nuclei_bin/
    sudo mv /tmp/nuclei_bin/nuclei /usr/local/bin/
    rm -rf /tmp/nuclei.zip /tmp/nuclei_bin/
fi
nuclei -version 2>&1 | head -1"
log "Nuclei ready"

# ── Nuclei templates ──────────────────────────────────────────
info "Updating Nuclei templates (4000+)..."
kali "nuclei -update-templates -silent"
log "Nuclei templates updated"

# ── SecLists ──────────────────────────────────────────────────
info "Installing SecLists..."
kali "if [[ ! -d /usr/share/seclists ]]; then
    sudo apt install -y -qq seclists 2>/dev/null || \
    sudo git clone --depth 1 https://github.com/danielmiessler/SecLists.git /usr/share/seclists
fi"
log "SecLists ready"

# ── Post-exploitation scripts ─────────────────────────────────
info "Installing post-exploitation tools..."
kali "mkdir -p /home/kali/tools && cd /home/kali/tools

# LinPEAS
if [[ ! -f linpeas.sh ]]; then
    wget -q https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh
    chmod +x linpeas.sh
fi

# WinPEAS (Windows PE — run via meterpreter)
if [[ ! -f winPEASx64.exe ]]; then
    wget -q https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEASx64.exe 2>/dev/null || true
fi

# Linux Exploit Suggester
if [[ ! -f linux-exploit-suggester.sh ]]; then
    wget -q https://raw.githubusercontent.com/mzet-/linux-exploit-suggester/master/linux-exploit-suggester.sh
    chmod +x linux-exploit-suggester.sh
fi

# pspy (process monitor)
if [[ ! -f pspy64 ]]; then
    wget -q https://github.com/DominicBreuker/pspy/releases/latest/download/pspy64
    chmod +x pspy64
fi

echo 'Tools downloaded to /home/kali/tools/'"
log "Post-exploitation scripts installed"

# ── Python tools ──────────────────────────────────────────────
info "Installing Python tools..."
kali "pip3 install --quiet --break-system-packages \
    impacket pwntools frida-tools objection \
    crackmapexec shodan truffleHog gitleaks \
    2>/dev/null || true"
log "Python tools installed"

# ── Rustscan ──────────────────────────────────────────────────
info "Installing Rustscan..."
kali "if ! command -v rustscan &>/dev/null; then
    wget -q https://github.com/RustScan/RustScan/releases/latest/download/rustscan_amd64.deb -O /tmp/rustscan.deb
    sudo dpkg -i /tmp/rustscan.deb 2>/dev/null || sudo apt-get install -f -y -qq
    rm -f /tmp/rustscan.deb
fi
rustscan --version 2>&1 | head -1"
log "Rustscan ready"

# ── Create rockyou symlink ─────────────────────────────────────
kali "if [[ -f /usr/share/wordlists/rockyou.txt.gz ]] && [[ ! -f /usr/share/wordlists/rockyou.txt ]]; then
    sudo gunzip /usr/share/wordlists/rockyou.txt.gz
fi"

# ── Verify critical tools ─────────────────────────────────────
echo ""
info "Verifying critical tools..."
TOOLS=(nmap sqlmap hashcat nuclei gobuster ffuf hydra)
for tool in "${TOOLS[@]}"; do
    if kali "command -v $tool" &>/dev/null; then
        log "  $tool ✓"
    else
        warn "  $tool ✗ (not found)"
    fi
done

# ── Summary ───────────────────────────────────────────────────
echo ""
echo -e "${GRN}══════════════════════════════════════════════${NC}"
echo -e "${GRN}  KALI MCP INITIALIZATION COMPLETE${NC}"
echo -e "${GRN}══════════════════════════════════════════════${NC}"
echo ""
log "Kali container is ready for authorized security testing"
log "Reference: kali-mcp/TOOLS.md for full tool list"
