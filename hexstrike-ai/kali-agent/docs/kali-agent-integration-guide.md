# KALI AGENT → KALI-BACKUP-SYSTEM INTEGRATION GUIDE

## Your Existing Structure (from kali-backup-system repo)

```
/mnt/sf_KaliShare/           ← VirtualBox shared folder
├── scripts/                 ← Setup stages 1-5, start-kali.sh, monitor-mode.sh, red-button.sh
├── skills/                  ← OpenCode skills
├── docs/                    ← Bibles, guides, references
├── agents/                  ← AI agent configs
├── mcp/                     ← MCP server configs
├── config/                  ← System configs
├── bibles/                  ← Reference bibles
├── claude/                  ← Claude Code config
├── gemini/                  ← Gemini CLI config
├── references/              ← Technical references
└── chains/                  ← Attack chains

/opt/hexstrike/              ← HexStrike AI
~/.config/opencode/skills/   ← OpenCode skill files
~/.opencode.json             ← OpenCode config
/usr/share/wordlists/        ← Wordlists
/opt/pentest-tools/          ← Additional tools
```

VM: 4GB RAM, 2 CPUs — resource-constrained, be careful with heavy tools.

---

## MERGE PLAN

### Step 1: Extract Kali Agent into KaliShare

```bash
# On your host (before starting VM), put the tarball in KaliShare
cp kali-agent-full.tar.gz /path/to/KaliShare/tars/

# In Kali VM:
cd /mnt/sf_KaliShare/tars
tar xzf kali-agent-full.tar.gz
```

### Step 2: Install Python Modules → /opt/hexstrike/

Your HexStrike already lives at `/opt/hexstrike`. Merge our modules in:

```bash
# Backup existing hexstrike first
sudo cp -r /opt/hexstrike /opt/hexstrike.bak.$(date +%Y%m%d)

# Copy our enhanced modules
cd /mnt/sf_KaliShare/tars/kali-agent-repo
sudo cp scope_guard.py /opt/hexstrike/
sudo cp audit_logger.py /opt/hexstrike/
sudo cp sanitizer.py /opt/hexstrike/
sudo cp hexstrike_mcp.py /opt/hexstrike/
sudo cp model_router.py /opt/hexstrike/
sudo cp virustotal_enrichment.py /opt/hexstrike/
sudo cp burp_adapter.py /opt/hexstrike/
sudo cp deduplicator.py /opt/hexstrike/
sudo cp findings_exporter.py /opt/hexstrike/
sudo cp mermaid_generator.py /opt/hexstrike/
sudo cp notion_sync.py /opt/hexstrike/

# Copy test suites
sudo cp test_modules.py /opt/hexstrike/
sudo cp integration_test.py /opt/hexstrike/

# Verify
cd /opt/hexstrike && python3 test_modules.py
```

### Step 3: Install Skills → Your Skill Locations

You have two skill locations. Install to both:

```bash
# OpenCode skills
for skill in /mnt/sf_KaliShare/tars/kali-agent-repo/skills/*/; do
  skill_name=$(basename "$skill")
  dest="$HOME/.config/opencode/skills/${skill_name}"
  mkdir -p "$dest"
  cp "$skill/SKILL.md" "$dest/"
  [ -d "$skill/references" ] && cp -r "$skill/references" "$dest/"
  echo "  ✓ ${skill_name}"
done

# KaliShare backup copy
cp -r /mnt/sf_KaliShare/tars/kali-agent-repo/skills/* /mnt/sf_KaliShare/skills/
```

### Step 4: Integrate with Existing Setup Stages

Add a Stage 6 to your setup flow:

```bash
cat > /mnt/sf_KaliShare/scripts/setup-stage6-kaliagent.sh << 'STAGE6'
#!/usr/bin/env bash
# ═══════════════════════════════════════════
# STAGE 6: KALI AGENT INSTALLATION
# Run AFTER stages 1-5 complete
# ═══════════════════════════════════════════
set -euo pipefail

echo "💀 STAGE 6: Installing Kali Agent..."

# Python deps (FastMCP for the MCP server)
pip3 install --break-system-packages mcp 2>/dev/null || pip3 install mcp

# Create engagement directories
mkdir -p /tmp/pentest
mkdir -p ~/.hexstrike/archives

# Install to /opt/hexstrike (merging with existing)
AGENT_DIR="/mnt/sf_KaliShare/tars/kali-agent-repo"
if [ -d "$AGENT_DIR" ]; then
  sudo cp "$AGENT_DIR"/*.py /opt/hexstrike/ 2>/dev/null
  echo "  ✓ Python modules installed to /opt/hexstrike/"
else
  echo "  ✗ Extract kali-agent-full.tar.gz to /mnt/sf_KaliShare/tars/ first"
  exit 1
fi

# Install skills
for skill in "$AGENT_DIR"/skills/*/; do
  name=$(basename "$skill")
  dest="$HOME/.config/opencode/skills/${name}"
  mkdir -p "$dest"
  cp "$skill/SKILL.md" "$dest/"
  [ -d "$skill/references" ] && cp -r "$skill/references" "$dest/"
done
echo "  ✓ 17 skills installed to ~/.config/opencode/skills/"

# Copy configs
cp "$AGENT_DIR/scope_configs_example.json" /mnt/sf_KaliShare/config/ 2>/dev/null
cp "$AGENT_DIR/kali_playbook_template.json" /mnt/sf_KaliShare/config/ 2>/dev/null
cp "$AGENT_DIR/vuln-kb-seed-data.json" /mnt/sf_KaliShare/references/ 2>/dev/null

# Copy JS modules (for report/proposal generation)
cp "$AGENT_DIR"/*.js /opt/hexstrike/ 2>/dev/null
cd /opt/hexstrike && npm install docx 2>/dev/null

# Verify
echo ""
echo "Running tests..."
cd /opt/hexstrike && python3 test_modules.py 2>&1 | tail -3
echo ""
echo "💀 Stage 6 complete!"
echo "   Start HexStrike: cd /opt/hexstrike && python3 hexstrike_mcp.py"
echo "   Or: systemctl start hexstrike (if service installed)"
STAGE6

chmod +x /mnt/sf_KaliShare/scripts/setup-stage6-kaliagent.sh
```

### Step 5: Update MCP Config

Merge into your existing MCP config:

```bash
# Add to your Claude Code / OpenCode MCP config
# Your existing config is at /mnt/sf_KaliShare/mcp/ or ~/.claude.json

# The key entries to add:
cat << 'MCP_CONFIG'
{
  "hexstrike": {
    "command": "python3",
    "args": ["/opt/hexstrike/hexstrike_mcp.py"],
    "env": { "PENTEST_BASE": "/tmp/pentest" }
  }
}
MCP_CONFIG
```

### Step 6: Update Quick Reference Files

Add to your existing QUICK-CHEAT.txt:

```bash
cat >> /mnt/sf_KaliShare/QUICK-CHEAT.txt << 'KALI_AGENT'

# ═══════════════════════════════════════════
# KALI AGENT COMMANDS
# ═══════════════════════════════════════════

# Start HexStrike MCP (11 tools)
cd /opt/hexstrike && python3 hexstrike_mcp.py

# Run tests (113 total)
cd /opt/hexstrike && python3 test_modules.py && python3 integration_test.py

# Initialize engagement
# Tell Claude: "Initialize pentest against example.com"

# Export findings
# Tell Claude: "Export findings to CSV/Jira/Linear/SARIF"

# Generate report
cd /opt/hexstrike && node generate_report.js findings.json report.docx

# Generate proposal
cd /opt/hexstrike && node generate_proposal.js intake.json proposal.docx

# Cleanup engagement (secure shred)
/mnt/sf_KaliShare/tars/kali-agent-repo/cleanup_engagement.sh ENG-XXXX --confirm
KALI_AGENT
```

---

## MCP SERVERS TO ADD (Researched — Complement Your Setup)

### zebbern-kali-mcp (145+ tools, best for your setup)
```bash
# Docker method (recommended for 4GB VM — isolates resource usage)
curl -sLO https://raw.githubusercontent.com/zebbern/zebbern-kali-mcp/main/docker-compose.yml
docker compose up -d

# Or native install:
git clone https://github.com/zebbern/zebbern-kali-mcp.git
cd zebbern-kali-mcp && sudo ./install.sh
```
Why: 145+ tools, VPN management, CTF platform integration, AD tools, network pivoting.

### TriV3/MCP-Kali-Server (SSH + reverse shell management)
```bash
git clone https://github.com/TriV3/MCP-Kali-Server.git
cd MCP-Kali-Server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./server.py
```
Why: SSH session management, reverse shell handling, file transfers between target/kali/host. Great for HTB.

### fkesheh/skill-mcp (Programmatic skill management)
```bash
pip install skill-mcp
# Skills stored at ~/.skill-mcp/skills/
```
Why: Create/edit/run skills programmatically via Claude. No more manual file uploads.

---

## RESOURCE-AWARE NOTES (4GB RAM / 2 CPU)

Your VM is constrained. Follow these rules:

1. **Never run Ollama + HexStrike + heavy scans simultaneously** — pick two
2. **Use `nice -n 19` for background scans** to keep the VM responsive
3. **Nuclei**: Limit concurrency: `nuclei -c 10 -rl 50` (default is too aggressive)
4. **nmap**: Use `-T3` not `-T4` in the VM to avoid memory pressure
5. **hashcat**: Run on the HOST, not in the VM (GPU matters)
6. **HexStrike MCP**: Low memory footprint (~50MB) — safe to run always
7. **Docker MCP servers**: Each container adds ~200MB — limit to 2 concurrent

---

## FILE MAPPING: What Goes Where

| Kali Agent File | Your Location | Why |
|---|---|---|
| `*.py` (13 modules) | `/opt/hexstrike/` | Merges with existing HexStrike |
| `*.js` (3 modules) | `/opt/hexstrike/` | Report/proposal generation |
| `skills/*/SKILL.md` | `~/.config/opencode/skills/` | OpenCode skill location |
| `skills/*/SKILL.md` | `/mnt/sf_KaliShare/skills/` | Backup copy in shared folder |
| `scope_configs_example.json` | `/mnt/sf_KaliShare/config/` | Engagement templates |
| `kali_playbook_template.json` | `/mnt/sf_KaliShare/config/` | Curator playbooks |
| `vuln-kb-seed-data.json` | `/mnt/sf_KaliShare/references/` | Intel reference |
| `kali-operations-guide.md` | `/mnt/sf_KaliShare/docs/` | Operations bible |
| `setup-stage6-kaliagent.sh` | `/mnt/sf_KaliShare/scripts/` | Setup stage 6 |
| `cleanup_engagement.sh` | `/mnt/sf_KaliShare/scripts/` | Post-engagement cleanup |
| `hexstrike.service` | `/etc/systemd/system/` | Optional systemd service |
| `.github/workflows/` | Push to github.com/az0307/kali-agent | CI pipeline |
| `artifacts/*.jsx` | Use in Claude.ai web | Dashboard, KB, intake, etc. |

---

## QUICK DEPLOY (Copy-Paste This Into Kali Terminal)

```bash
# One-shot deploy after extracting tarball
cd /mnt/sf_KaliShare/tars/kali-agent-repo && \
sudo cp *.py /opt/hexstrike/ && \
sudo cp *.js /opt/hexstrike/ && \
cd /opt/hexstrike && pip3 install --break-system-packages mcp 2>/dev/null && \
python3 test_modules.py 2>&1 | tail -3 && \
for s in /mnt/sf_KaliShare/tars/kali-agent-repo/skills/*/; do \
  n=$(basename "$s"); mkdir -p ~/.config/opencode/skills/$n; \
  cp "$s/SKILL.md" ~/.config/opencode/skills/$n/; \
done && \
echo "💀 Kali Agent deployed — 17 skills, 13 modules, 113 tests"
```
