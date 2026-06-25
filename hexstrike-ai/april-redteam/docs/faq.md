# FAQ — April 2026 Red Team Stack
# Common questions and answers

---

## SETUP

**Q: Does this replace needing Kali Linux?**

No — the Kali MCP container runs actual Kali Linux tools. The stack wraps
them in MCP protocol so Claude Code can call them. You still need Kali
(or the Docker container) for tool execution. What the stack replaces is
the manual decision-making around which tool to run next and in what order.

**Q: Can I run this without Docker?**

HexStrike works natively on Kali:
```bash
sudo apt install hexstrike-ai   # Kali 2025.4+
```
For the other tools (PentestGPT, VulnGPT, STRIDE-GPT, AutoGPT), you still
need Docker or manual installs via `scripts/install-extended.sh`.
The Kali MCP server can also run without Docker — it just needs SSH access
to a Kali instance (local, VM, or remote).

**Q: Do I need all 9 tools?**

No. Minimum viable setup:
- **HexStrike** (required — primary tool orchestrator)
- **Kali MCP** (required — interactive tool execution)
- **PentestThinkingMCP** (strongly recommended — attack planning)

Everything else is additive. Add them as you need the capability.

**Q: What's the minimum hardware?**

```
MINIMUM:
  4GB RAM (8GB recommended)
  20GB disk (for Docker images + SecLists)
  Any modern CPU
  WiFi adapter if doing wireless testing

RECOMMENDED (matches Az's HP rig):
  8GB+ RAM
  50GB+ disk
  2GB+ NVIDIA GPU (for hashcat WPA2 cracking)
  Alfa AWUS036ACH (WiFi adapter for monitor mode)
```

**Q: The Docker build is slow — is that normal?**

Yes. `kali-mcp` pulls `kalilinux/kali-rolling` which is ~2GB, then installs
tools. First build: 15–30 minutes. Subsequent builds use cache: 1–3 minutes.
Run once: `docker compose build --parallel` to build all services at once.

---

## TOOLS

**Q: What's the difference between HexStrike profiles?**

HexStrike loads different tool subsets per profile:
- `hs` (full): All 150+ tools — slow to initialize, use for full engagements
- `web`: 93 web-focused tools — faster, ideal for bug bounty
- `net`: 75 network tools — crackmapexec, netexec, enum4linux family

Start with `web` or `net` for targeted work. Use `hs` when you want
complete coverage.

**Q: Is HexStrike v6.1 better than v6.0?**

Yes — v6.1 rewrote the server from 17,289 lines to 507 (97% reduction)
with 921 passing tests. Much faster startup, fewer bugs. The PR hasn't
merged to main as of April 2026 but the community edition has it.

**Q: PentestGPT vs PentestThinkingMCP — what's the difference?**

```
PentestThinkingMCP:  MCTS planning engine. Explores attack paths.
                     Input: what you know. Output: ranked attack plan.
                     Use FIRST — tells you what to try.

PentestGPT:          Task tree executor. Runs tests autonomously.
                     Input: target IP. Output: shells + flags.
                     Use AFTER planning — or for autonomous CTF.
```

Use them together: `think` plans the path, `pgpt` executes it.

**Q: AutoGPT keeps timing out on complex tasks — what do I do?**

AutoGPT has a default task timeout. For long-running OSINT:
```bash
# Increase timeout in autogpt config:
# .env: AUTOGPT_MAX_TASK_CYCLE_COUNT=500  (default: 100)
# Or break the task into smaller subtasks
```
Also — switch to DeepSeek backend to reduce latency and cost:
```bash
AUTOGPT_SMART_LLM=deepseek-chat
AUTOGPT_FAST_LLM=deepseek-chat
```

**Q: VulnGPT says "Shodan key not set" — is that required?**

No. VulnGPT works without Shodan — it falls back to nmap + NVD only.
Shodan adds: pre-existing scan data, historical exposure, geolocation.
Get a free Shodan key at shodan.io (basic tier works for most purposes).
Set: `SHODAN_API_KEY=yourkey` in `.env`.

---

## COST & BILLING

**Q: I got a big unexpected API bill — what happened?**

Most likely: AutoGPT running continuously with an expensive model.
Fixes:
```bash
# Check current AutoGPT config:
grep -E 'SMART_LLM|FAST_LLM' .env

# Switch to DeepSeek (37x cheaper):
sed -i 's/AUTOGPT_SMART_LLM=.*/AUTOGPT_SMART_LLM=deepseek-chat/' .env

# Set hard cap in litellm_config.yaml:
# max_budget: 5.0  (USD per day)
```

**Q: The $1.11/benchmark figure for PentestGPT — is that accurate?**

That's from their published XBOW benchmark paper (USENIX Security 2024).
Your cost will vary based on model choice:
- GPT-4o: ~$1.11 (paper benchmark)
- Claude Sonnet: ~$0.35–0.80 (cheaper, nearly same success rate)
- DeepSeek: ~$0.08–0.20 (significant quality drop on hard challenges)

**Q: Can I use a free tier API key?**

Anthropic and OpenAI free tiers have strict rate limits that will cause
failures mid-engagement. Minimum: Anthropic Tier 1 ($5 pre-paid).
For serious use: $20–50/month in API credits covers most engagements.

---

## SECURITY

**Q: Is the shell=True vulnerability actually dangerous?**

Yes — critically so if the MCP server is network-exposed (not just localhost).
With `shell=True`, crafted tool output from a target could inject shell
commands that execute on your red team machine.

Verify it's patched:
```bash
grep -r 'shell=True' kali-mcp/mcp_server.py
# Must return nothing
```

The patch is in `docs/opsec.md`. Apply before any engagement.

**Q: Can the target system detect that I'm using AI tools?**

Yes, in some ways:
- HexStrike User-Agent strings identify AI-assisted scanning
- Nuclei has distinctive request patterns
- Very regular timing (AI orchestration tends to be metronomically consistent)

Mitigation:
- Configure custom User-Agent in HexStrike
- Add random delays between requests (`HEXSTRIKE_REQUEST_DELAY_MS=100-500`)
- Use Kali MCP for manual-looking traffic when stealth matters

**Q: Is my test traffic logged by Anthropic?**

Claude API calls may be used for safety monitoring per Anthropic's policies.
Do not send: actual exploit payloads, real credentials, client PII, or
proprietary system details through the API. Use Ollama (local) for anything
sensitive. See `docs/opsec.md` for full guidance.

**Q: Can I use this for a client engagement professionally?**

Yes, with these requirements:
1. Written authorization from the client (get it before any testing)
2. Scope defined in writing (specific domains, IPs, exclusions)
3. Loot directory encrypted, client data not sent to external APIs
4. Report delivered securely (encrypted, not emailed plaintext)
5. Credentials and evidence securely destroyed after engagement closes

---

## PLAYBOOKS & SKILLS

**Q: When should I run the threat model vs just starting testing?**

Always run the threat model first if the client has provided system
architecture details (even a diagram or verbal description).
Reason: threat modeling takes 15 minutes and often reveals high-value
attack paths that pure scanning would miss (logic flaws, trust boundaries,
auth flow weaknesses). The ROI is very high.

**Q: The CTF playbook says PentestGPT first — why not HexStrike?**

HexStrike is optimized for real-world targets (bug bounty, client engagements).
Its tool selection and rate limiting are tuned for production systems.
PentestGPT is specifically benchmarked against CTF/HTB-style challenges
and handles their specific patterns better (intentional vulns, CTF flags,
specific privilege escalation paths). Use `pgpt` for CTF, `hs web` for
real engagements.

**Q: How do I add a new playbook for a technique not covered?**

1. Copy the structure from any existing playbook
2. Minimum sections: Overview, Tools, Phase 1...N, Evidence Collection
3. Add authorization gate at top if it requires explicit written scope
4. Reference the appropriate MCP server (`kali`, `hs`, `vuln`, etc.)
5. Add to CLAUDE.md playbook index
6. Submit PR (see CONTRIBUTING.md)

---

## TROUBLESHOOTING

See `docs/troubleshooting.md` for detailed error resolutions.

Common quick fixes:
```bash
make health           # Check which services are down
make restart          # Restart everything
docker compose logs   # See what's failing
make rotate-tokens    # If auth errors after long idle

# Redis cache causing stale results:
make clean-cache

# HexStrike not responding:
curl http://localhost:8888/health
docker compose restart hexstrike hexstrike-mcp
```

---

*April 2026 | Something not covered here? Open an issue on GitHub.*
