# TROUBLESHOOTING — April 2026 Red Team Stack
# Error → Cause → Fix for every component

---

## QUICK DIAGNOSTICS

```bash
make health                    # Full status check
docker compose ps              # Container states
docker compose logs --tail=50  # Recent logs all services
./scripts/healthcheck.sh       # Detailed per-service check
```

---

## HEXSTRIKE AI

### "Connection refused localhost:8888"

```bash
# Check if container is running:
docker compose ps hexstrike

# Restart:
docker compose restart hexstrike hexstrike-mcp

# View logs:
docker compose logs hexstrike --tail=30

# Check port binding:
ss -tulpn | grep 8888
# Should show: 127.0.0.1:8888
```

### "401 Unauthorized" from HexStrike API

```bash
# Token mismatch — regenerate:
make rotate-tokens

# Or manually check token matches:
grep HEXSTRIKE_API_TOKEN .env
# Verify it matches what's in docker container:
docker exec hexstrike env | grep HEXSTRIKE_API_TOKEN
```

### HexStrike scan returns empty results

```bash
# Check allowlist — target might be blocked:
docker exec hexstrike cat /app/config/allowlist.yaml

# Check Redis cache — stale results:
make clean-cache

# Check rate limiting:
docker exec hexstrike cat /app/config/rate_limits.yaml

# Test directly:
curl -H "Authorization: Bearer $HEXSTRIKE_API_TOKEN" \
     http://localhost:8888/api/tools/list | python3 -m json.tool | head
```

### "ImportError: cannot import name 'mcp_bridge'"

```bash
# HexStrike needs re-install:
cd hexstrike-ai && pip install -e . --break-system-packages
# Or rebuild Docker image:
docker compose build --no-cache hexstrike
```

---

## KALI MCP

### "SSH connection refused localhost:2222"

```bash
# Check if Kali container is running:
docker compose ps kali-mcp

# Check port 2222 is exposed:
ss -tulpn | grep 2222

# Restart Kali container:
docker compose restart kali-mcp

# Check SSH daemon inside container:
docker exec kali-mcp service ssh status
docker exec kali-mcp service ssh start
```

### "Permission denied (publickey)" on Kali SSH

```bash
# Regenerate SSH key pair:
ssh-keygen -t ed25519 -f ~/.ssh/kali_mcp_ed25519 -N ""

# Copy public key into container:
docker exec kali-mcp bash -c "
    mkdir -p /home/kali/.ssh
    echo '$(cat ~/.ssh/kali_mcp_ed25519.pub)' >> /home/kali/.ssh/authorized_keys
    chmod 700 /home/kali/.ssh
    chmod 600 /home/kali/.ssh/authorized_keys
    chown -R kali:kali /home/kali/.ssh
"

# Test:
ssh -i ~/.ssh/kali_mcp_ed25519 -p 2222 kali@localhost id
```

### "MCP token authentication failed"

```bash
# Rotate tokens:
make rotate-tokens

# Or manually update in .env and restart:
NEW_TOKEN=$(openssl rand -hex 32)
sed -i "s/KALI_MCP_TOKEN=.*/KALI_MCP_TOKEN=$NEW_TOKEN/" .env
docker compose restart kali-mcp
```

### Tool command hangs indefinitely

```bash
# Kali MCP has 300s timeout by default
# For long-running scans, use tmux sessions:

# Via Claude Code:
# kali_tmux_new("long_scan")
# kali_tmux_send("long_scan", "nmap -p- --min-rate 1000 target")
# kali_tmux_send("long_scan", "")  # check status
# kali_tmux_read("long_scan")      # read output
```

---

## PENTESTGPT

### "pentestgpt command not found"

```bash
# Re-install:
cd pentestgpt && pip install -e . --break-system-packages

# Or via Docker:
docker compose up -d pentestgpt
```

### PentestGPT "rate limit exceeded"

```bash
# Switch to Sonnet (cheaper, less rate limited):
PENTESTGPT_MODEL=claude-sonnet-4-20250514 pentestgpt --target [IP]

# Add retry delay:
pentestgpt --target [IP] --request-delay 2
```

### PentestGPT produces no output / hangs

```bash
# Test model connectivity:
python3 -c "
import anthropic
c = anthropic.Anthropic()
r = c.messages.create(model='claude-sonnet-4-20250514', max_tokens=50,
    messages=[{'role':'user','content':'Say OK'}])
print(r.content[0].text)
"

# If that fails: check ANTHROPIC_API_KEY in .env
grep ANTHROPIC_API_KEY .env
```

---

## VULNGPT

### "localhost:8090 connection refused"

```bash
docker compose up -d vulngpt
docker compose logs vulngpt --tail=20

# Check VulnGPT v2 is installed:
ls vulngpt-v2/ 2>/dev/null || echo "Need to run: ./scripts/install-extended.sh"
```

### "Shodan query failed: Invalid API key"

```bash
# Verify key:
grep SHODAN_API_KEY .env
python3 -c "import shodan; api = shodan.Shodan('YOUR_KEY'); print(api.info())"

# Shodan free tier limits: 1 query credit / day
# Use sparingly or upgrade to paid plan
```

---

## STRIDE-GPT

### Streamlit UI not loading at localhost:8501

```bash
docker compose up -d stride-gpt
docker compose logs stride-gpt --tail=20

# Streamlit sometimes takes 30+ seconds to start:
sleep 30 && curl -s http://localhost:8501/_stcore/health
```

### "ModuleNotFoundError: No module named 'stride_gpt'"

```bash
cd stride-gpt && pip install -r requirements.txt --break-system-packages
```

---

## AUTOGPT

### AutoGPT not starting

```bash
cd autogpt
cp .env.template .env  # If first run
docker compose up -d
# Web UI: http://localhost:8000
```

### AutoGPT runs but produces garbage output

```bash
# Increase thinking budget — AutoGPT needs room to reason:
# In .env:
AUTOGPT_SMART_LLM=claude-sonnet-4-20250514  # Not mini/flash
AUTOGPT_MAX_TASK_CYCLE_COUNT=500

# If using DeepSeek for OSINT (complex tasks may need Sonnet):
AUTOGPT_SMART_LLM=deepseek-chat  # OK for simple monitoring
AUTOGPT_SMART_LLM=claude-sonnet-4-20250514  # Better for complex OSINT
```

---

## DATABASE / REDIS

### PostgreSQL "FATAL: password authentication failed"

```bash
# Token rotation may have changed password without DB update:
NEW_PASS=$(grep POSTGRES_PASSWORD .env | cut -d= -f2)

# Update DB password:
docker exec rt-postgres psql -U postgres -c \
    "ALTER USER rtuser PASSWORD '$NEW_PASS';"

docker compose restart postgres
```

### Redis "WRONGTYPE" errors

```bash
# Cache corruption — flush and restart:
make clean-cache
docker compose restart redis
```

### "loot/notes.json cannot be parsed" (PentestAgent)

```bash
# Corrupted Shadow Graph — reset for this mission:
python3 -c "
import json
template = {
  'mission': '[NAME]', 'credentials': [],
  'vulnerabilities': [], 'findings': [],
  'artifacts': [], 'hosts': []
}
with open('loot/[MISSION]/notes.json', 'w') as f:
    json.dump(template, f, indent=2)
print('Shadow Graph reset')
"
```

---

## CLAUDE CODE / MCP

### "MCP server connection failed" in Claude Code

```bash
# Check claude.json syntax:
python3 -c "import json; json.load(open('claude.json')); print('OK')"

# Verify all MCP servers are actually running:
make health

# Restart Claude Code after any MCP config change:
# Ctrl+C → claude --dangerously-skip-permissions
```

### Claude Code not finding playbooks

```bash
# Verify CLAUDE.md is in current directory:
ls CLAUDE.md

# Claude Code loads CLAUDE.md from working directory.
# Must be launched from repo root:
cd /path/to/april-redteam-2026
claude --dangerously-skip-permissions
```

### Tool calls timing out

```bash
# Increase MCP timeout in claude.json:
# "timeout": 300  (default: 60 seconds)
# Add to each server config that times out

# For long nmap scans: use tmux via kali MCP (non-blocking)
```

---

## NETWORK / DOCKER

### "Network redteam not found"

```bash
docker network create --subnet 172.25.0.0/24 redteam
# OR:
docker compose up -d  # Creates network automatically
```

### Containers can't reach each other

```bash
# Inspect network:
docker network inspect redteam

# Check container IPs match docker-compose.yml:
docker inspect hexstrike | grep IPAddress
# Should be 172.25.0.10

# Recreate if needed:
docker compose down && docker compose up -d
```

### Port conflicts (address already in use)

```bash
# Find what's using the port:
ss -tulpn | grep 8888

# Kill conflicting process:
sudo fuser -k 8888/tcp

# Or change port in docker-compose.yml:
# ports: ["127.0.0.1:8890:8888"]  # map to different host port
```

---

## COMMON ERRORS QUICK REFERENCE

| Error | Fix |
|-------|-----|
| `Connection refused :8888` | `docker compose restart hexstrike` |
| `401 Unauthorized` | `make rotate-tokens` |
| `SSH: Permission denied` | Regenerate `~/.ssh/kali_mcp_ed25519` |
| `API key invalid` | Check `.env` values |
| `shell=True detected` | Patch per `docs/opsec.md` |
| `Redis WRONGTYPE` | `make clean-cache` |
| `CLAUDE.md not found` | Run Claude Code from repo root |
| `MCP server not found` | `make health` then `make restart` |
| Out-of-scope error | Add target to `loot/[MISSION]/mission.md` scope table |
| Nuclei templates outdated | `nuclei -update-templates` |
| rockyou not found | `gunzip /usr/share/wordlists/rockyou.txt.gz` |

---

*Still stuck? Open an issue: github.com/0x4m4/april-redteam-2026/issues*
