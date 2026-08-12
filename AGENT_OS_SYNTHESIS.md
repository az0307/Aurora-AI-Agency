# AutoBoros Agent OS — Repo Synthesis + Build Prompts

> **RECONCILED AGAINST LIVE REPO STATE — 2026-07-10, branch `claude/new-session-5vhxhz`.**
> This document was originally reconstructed from memory/summaries with no live
> filesystem access (see original note below). It has now been verified against the
> actual cloned repos under `/home/user` (17 repos). Claims that did not survive
> verification are corrected inline with a `> **Reconciled:**` callout, and a full
> live-audit record (Phase 1 inventory, Phase 2 invariant findings, Phase 4 fix
> proposals) is appended at the end. Original prose is otherwise preserved.
>
> **Environment reality that reframes several claims:** the kickoff assumed a
> standalone AutoBoros-OS repo with `autoboros-backend` / `autoboros-cockpit` holding
> code. On disk those two repos are **empty placeholders (one `CLAUDE.md` each)**; the
> canonical code lives in `Aurora-AI-Agency/autoboros/` and the red-team surface in
> `Aurora-AI-Agency/hexstrike-ai/`. `freellmapi` and `revfactory` are **not cloned**.

Pulled from: Drive docs (Ouroboros/Aurora blueprints, Sovereign Mesh 2026.2, Gastown/OpenCode/Antigravity research, LLM-cognitive-architecture report, local deployment guide), past conversations (freellmapi mining, AutoBoros MCP hardening install script, AutoBoros Business Suite architecture, AutoborosAI legacy repo), and memory. GitHub/local filesystem were not reachable from this chat — the file inventories below are from what's documented, not a live `ls`. Confirm against actual repo state before treating file-line-counts as current.

---

## 1. What's actually good — keep and promote to "core OS"

| Pattern | Source | Why it's a core primitive |
|---|---|---|
| **Curator → role-specialized team dispatch** | AutoBoros Business Suite architecture doc | This *is* your agent OS scheduler. Curator (Claude) reads intent, builds a playbook, assigns named sub-agents by role — not by generic "agent 1, agent 2." Promote this to the literal kernel loop. |
| **Blackboard / A2A shared context** | ai-agent-orchestration skill, memory | Solves the #1 multi-agent failure mode (context loss on handoff). Already built. Don't rebuild — extend it with... |
| **Context handoff injection** | freellmapi mining session | freellmapi's mid-conversation model-switch preamble (task continuity injection, TTL'd, fires only on actual model change) is a direct, small patch onto your existing A2A handoff boundary. This is the single highest-value external pattern you've found — implement it. |
| **Family-locked embedding failover** | freellmapi mining | Prevents silent vector corruption when a memory/RAG path fails over to a different embedding model mid-session. Maps onto SimpleMem and any future vector store. |
| **Proactive multi-dimensional rate ledging** | freellmapi mining | Track RPM/RPD/TPM/TPD *before* sending, not react-to-429. Belongs in whatever client wraps your multi-provider calls (the "aces in their places" router below). |
| **Hardened install.sh with environment auto-detect + security hooks** | AutoBoros MCP hardening session | 12-phase installer (Linux/Termux/WSL2/Kali detection, allow/deny tool lists, destructive-command/credential-exfil/reverse-shell hooks, audit logging). This is your **cross-node bootstrap** — the thing that makes "multi-node hardware fleet" (tkpsz3, Radxa, HP Kali, ASUS Twist, Vista, XP lab) actually coherent as one OS instead of five separate setups. |
| **SKILL.md + A2A frontmatter + Blackboard protocol on skills** | AutoBoros skill ecosystem v3.0.0 | This is your OS's "syscall" layer — uniform interface every capability exposes. Keep as the contract; don't let it drift per-skill. |
| **Curator-based playbook composition (47 playbooks / 9 domains)** | memory | This is the OS's process scheduler / job definition layer. |
| **shell=True permanent ban + shlex.split allowlist** | HexStrike audit, cockpit audit session | Non-negotiable P0 security invariant. Bake into the OS kernel, not per-project. |
| **push.sh v2 clone-then-overlay + AGENT.md for autonomous execution** | multi-archive push session | This is your **deployment primitive** — how the OS ships itself and its own agents ship code without human-in-the-loop for routine pushes. |

> **Reconciled (row: rate ledging / handoff / embedding):** two of these three
> "external, still-to-implement" freellmapi patterns are already partly in-tree, and
> one is genuinely missing:
> - **Proactive rate ledging — PARTIALLY BUILT.** `claude-ecosystem-hub/llm_fallback/free_llm_system.py`
>   (907 lines) tracks per-provider `rate_limit_rpm` + provider status
>   (available/rate_limited/down) with a `rate_limit_reset` store. `gg/autoboros-core`
>   adds a token-budget governor (`governance.py`, `AUTOBOROS_TOKEN_BUDGET`, enforced in
>   `autoboros_core/api/routes.py`). It is not yet a unified RPM/RPD/TPM/TPD pre-send
>   ledger wrapping *every* call — see Phase 2 finding P1-A.
> - **Context handoff injection (preamble) — MISSING.** No `handoff`/`preamble`/
>   `continuity` implementation found in any cloned repo. Still the highest-ROI gap.
> - **Family-locked embedding failover — MISSING / N/A.** No embedding-family lock in
>   the audited core surface; `model_router.py` failover is LLM-only (GLM↔Sonnet).

## 2. What's redundant or should be retired

- **AutoborosAI legacy repo** ("freelance business… lead discovery") — this is a different, earlier product surface (freelance lead-gen), not agent-OS infrastructure. Fine to keep as a *tenant app* running on top of the OS, but don't let its README's framing ("comprehensive automation platform") bleed into how you describe the OS itself.
- **Ouroboros Foundation "Phase 1/2/3" legal-entity docs** — real and important, but business/legal scaffolding, not OS architecture. Keep separate from the technical repo review; don't let McScrooge/grants-agent context dilute the engineering prompts below.
- **Multiple overlapping "Master Implementation Overview" / onboarding docs** (Ouroboros Foundation master doc, ChatGPT "Bhy" onboarding transcript, Aurora & Ouroboros Notion blueprint) — three docs describing similar org structure from different eras. Worth a single consolidation pass so future prompts pull from one source of truth instead of three drifting copies.
- **kali-mcp/mcp_server.py at 217/500+ lines** — flagged already as P0 blocker. Not "redundant" but actively broken; do not build new agent-OS layers on top of it until it's complete (hashcat, impacket, tmux, AD enum tools missing).

> **Reconciled (kali-mcp claim — this was materially wrong):** the file at
> `hexstrike-ai/april-redteam/kali-mcp/mcp_server.py` is **217 lines, and it is
> complete, not truncated.** It defines **14 working `@mcp.tool` functions** and ends
> cleanly at `kali_health` (lines 208–217). "217/500+ lines / actively broken" is not
> accurate — there was never a 500-line target file; it is complete-but-limited.
> **tmux is present** (`kali_tmux_new` / `kali_tmux_send` / `kali_tmux_read`), so it
> should be removed from the "missing" list. Genuinely absent tools vs the wish-list:
> **hashcat, impacket, AD-enum** (and no hashcat despite the Express backend
> allowlisting it). This is a *coverage gap*, not a *broken build* — treat it as
> "extend when scope is signed," not "P0 blocker." Full tool inventory in Phase 1.

## 3. Recommended consolidated architecture ("aces in their places")

```
                        ┌─────────────────────────┐
                        │   CURATOR (Claude)      │  ← intent parse, playbook build,
                        │   AutoBoros Kernel       │    task routing, final synthesis
                        └───────────┬─────────────┘
                                    │  Blackboard / A2A (shared context)
              ┌─────────────────────┼─────────────────────┐
      ┌───────▼──────┐      ┌───────▼───────┐      ┌───────▼───────┐
      │ Research/     │      │ Reasoning/     │      │ Execution/     │
      │ Extraction    │      │ Architecture   │      │ Code+Deploy    │
      │ GPT-4o/Firecrawl│    │ DeepSeek R1    │      │ Claude Code /  │
      │ or Gemini      │     │ (cheap deep    │      │ Codex CLI       │
      │ (cheap, fast)  │      │ reasoning)     │      │                │
      └───────────────┘      └───────────────┘      └───────────────┘
                                    │
                         Rate-ledger + failover router
                         (freellmapi patterns: proactive
                          RPM/RPD/TPM/TPD, family-locked
                          embedding failover, handoff preamble)
                                    │
                         Skill layer (SKILL.md + A2A frontmatter)
                                    │
                         install.sh bootstrap → tkpsz3 / Radxa /
                         HP Kali / ASUS Twist / Vista / XP lab
```

The routing rule ("aces in their places"): Curator never does extraction or brute-force reasoning itself — it delegates to whichever model is cheapest-per-token for that job class, then re-synthesizes. That's already in your own AutoBoros Business Suite doc (Curator/Financial/Startup/Architecture split) — it just needs to be generalized into the kernel rather than living in one vertical.

> **Reconciled (does the split exist in code, or only in docs?):** it exists in code
> **partially and today it is a two-tier router, not the three-lane kernel drawn above.**
> `hexstrike-ai/kali-agent/model_router.py` implements a real `ModelRouter`: a
> `ROUTING_TABLE` mapping 15 task-types onto **GLM-4.5 (worker)** vs **Sonnet (the
> "Curator" role, verbatim in the code comments)**, keyword task classification, and
> GLM↔Sonnet fallback, exposed over a Flask `/interpret`, `/routing/stats`,
> `/routing/classify` API. It is red-team-scoped (kali-agent), not a general kernel, and
> the "Research / Reasoning / Execution" three-way lane is **not** present — the current
> reality is Curator(Sonnet) ↔ structured-worker(GLM). The rate-ledger box in the diagram
> is **not wired into `model_router.py`** — it calls provider SDKs directly (Phase 2,
> P1-A). To realize this diagram, generalize `model_router.py` out of `kali-agent/` and
> route its calls through the `free_llm_system.py` / `autoboros-core` governor.

---

## 4. Build prompts — one per surface

### 4.1 Claude Code — `CLAUDE.md` (project root)

```markdown
# AutoBoros Agent OS

## Identity
You are operating inside the AutoBoros Agent OS kernel repo. Your job on this
repo is kernel work: Curator dispatch logic, Blackboard/A2A protocol, skill
loader, rate-ledger router, install.sh bootstrap. You are NOT building a
vertical product feature unless explicitly told which tenant app.

## Hard invariants (never violate, no exceptions, no "just this once")
- NEVER use `shell=True` in any subprocess call. Always `shlex.split()` +
  explicit allowlist.
- All model calls route through the rate-ledger (proactive RPM/RPD/TPM/TPD
  check BEFORE send, not reactive to 429).
- Every skill exposes a SKILL.md with A2A frontmatter. No skill without one.
- Any Blackboard write must be idempotent and TTL'd where it carries
  cross-agent context (see freellmapi handoff-preamble pattern).
- Embedding calls are family-locked: never silently failover from one
  embedding family to another mid-session.

## Architecture reference
Curator (you, Claude) → parses intent → builds playbook → dispatches to
role-specialized sub-agents (Research/Extraction, Reasoning, Execution) →
re-synthesizes. See AGENT_OS_SYNTHESIS.md §3 for the full diagram.

## Workflow
1. Before touching kernel code, run `bash -n` / shellcheck on any bash you
   change (Debian 12 Meta Server Bootstrap v2.0.0 standard).
2. Terse output. No hedging. Flag blockers directly, don't bury them.
3. If a task touches red-team tooling (april-redteam-2026, HexStrike/Specter),
   confirm scope-of-work is signed before treating it as anything but
   defensive/authorized.
4. Mobile-friendly scannable prose in any doc you write. No emojis in
   technical output.

## Known open blockers (check before assuming clean state)
- kali-mcp/mcp_server.py is COMPLETE at 217 lines / 14 tools — NOT truncated.
  Coverage gap only: hashcat, impacket, AD-enum tools not yet added. Extend
  only when engagement scope is signed. (Corrected 2026-07-10.)
- No claude.json / .mcp.json exists in any cloned repo — the "missing 8 MCP
  server entries" blocker cannot be verified and is removed pending the real
  config file being added to the repo. (Corrected 2026-07-10.)
- docker-compose: mem_limit is absent on ALL services across all 7 compose
  files; healthcheck present on only a minority. See Phase 1 / finding P2-B.
- Live P0: two shell=True command sinks in workspace-hub/clawdbot-station
  (finding P0-A/P0-B) violate the shell=True ban above.
```

### 4.2 Claude Code — slash command example (`.claude/commands/kernel-review.md`)

```markdown
---
description: Review a proposed change against Agent OS kernel invariants
---
Check the diff/plan against these AutoBoros Agent OS invariants before
approving: no shell=True, rate-ledger routing on all model calls, SKILL.md
present with A2A frontmatter for any new skill, Blackboard writes are
idempotent/TTL'd, embedding calls are family-locked. List any violation as
a blocking finding, not a suggestion. If clean, say so in one line.
```

### 4.3 Cursor / other IDE — `.cursorrules` or system prompt

```
You are working in the AutoBoros Agent OS codebase — a Curator-dispatched
multi-agent kernel (Blackboard/A2A shared context, skill-based capability
layer, multi-provider rate-ledger router). Treat this repo as infrastructure,
not a product feature repo.

Rules:
- shell=True in subprocess calls is a hard reject — always shlex.split with
  an explicit allowlist.
- Any new capability must ship as a skill: SKILL.md + A2A frontmatter,
  registered in SKILL_REGISTRY.
- Route all outbound model calls through the rate-ledger client — do not
  call provider SDKs directly from feature code.
- When suggesting completions for cross-agent handoff code, prefer the
  TTL'd context-injection pattern (mirrors freellmapi's model-switch
  preamble) over silent context drop.
- Style: terse, dense, no filler comments, no "TODO: handle edge case"
  placeholders — either handle it or flag it as an explicit open blocker
  in the PR description.
```

### 4.4 Raw CLI / terminal agent (Codex CLI, aider, generic agent loop) — system prompt

```
SYSTEM: You are an autonomous coding agent operating on the AutoBoros Agent
OS repository set (autoboros-backend, autoboros-cockpit, autoboros skill
ecosystem). You run non-interactively — assume no human confirms each step
unless a command is destructive (rm -rf, force-push, DB drop), in which case
stop and print the exact command for approval.

Non-negotiable constraints:
1. Never construct subprocess calls with shell=True. Use shlex.split() and
   an explicit command allowlist.
2. Never call an LLM provider SDK directly — always go through the
   rate-ledger router module, which pre-checks RPM/RPD/TPM/TPD before
   sending.
3. Any new agent capability must be delivered as a skill directory with a
   SKILL.md containing A2A protocol frontmatter (name, description,
   inputs, outputs, blackboard_reads, blackboard_writes).
4. When you push code, use the push.sh v2 clone-then-overlay pattern
   (AGENT.md defines your own execution contract) — do not hand-roll a
   different git flow.
5. Log every Blackboard write with a TTL. Context-handoff writes (agent A
   → agent B mid-task) must include a one-paragraph task-continuity
   preamble so the receiving agent doesn't restart or re-ask settled
   questions.

Output format: plain diffs/patches or full file contents. No conversational
preamble. If you hit a blocker (missing dependency, ambiguous spec,
truncated file like kali-mcp/mcp_server.py), stop and report the blocker
instead of guessing.
```

> **Reconciled (§4.4 note):** `autoboros-backend` and `autoboros-cockpit` are empty
> placeholder repos on disk (one `CLAUDE.md` each). An autonomous agent pointed at
> them today has nothing to operate on — the live code is in `Aurora-AI-Agency/autoboros/`.
> `kali-mcp/mcp_server.py` is not truncated (see §2 correction).

### 4.5 Model-agnostic system prompt — for the "aces in their places" router (used when Curator dispatches to GPT-4o / Gemini / DeepSeek R1 sub-agents via API)

```
You are a specialist sub-agent operating under the AutoBoros Curator inside
a multi-agent Blackboard system. You do not own the overall task — the
Curator does. Your job is exactly the sub-task assigned to you, nothing more.

Context you receive:
- A task-continuity preamble (if this is a handoff from another agent/model):
  read it fully before acting; do not restart work already described as done.
- Shared Blackboard state relevant to your role only.

Rules:
- Do not attempt orchestration, task-splitting, or delegation — that is the
  Curator's job. Return your result and stop.
- If you are a Research/Extraction agent: return structured findings only,
  no synthesis/recommendation — that's the Curator's or a Reasoning agent's
  job.
- If you are a Reasoning agent (e.g. deep multi-step analysis): show your
  work compactly, return a conclusion the Curator can act on directly.
- If you are an Execution/Code agent: never use shell=True; route any model
  calls through the rate-ledger; ship any new capability as a skill with
  SKILL.md.
- If your task is underspecified or you're missing context you'd expect
  from a proper handoff, say so explicitly rather than filling gaps with
  assumptions — the Curator will re-inject context, this is cheap; a wrong
  guess propagated downstream is not.
- Output only what the Curator needs to consume programmatically or
  synthesize — no meta-commentary about being an AI sub-agent.
```

---

## 5. Immediate next actions (in priority order)

1. **Unblock kali-mcp/mcp_server.py** (217/500+ lines) — nothing red-team-adjacent should be built on the OS until this is complete.
2. **Implement the freellmapi handoff-preamble pattern** on the existing A2A boundary — highest ROI external pattern found, small diff.
3. **Extract the Curator/Research/Reasoning/Execution split** out of the AutoBoros Business Suite doc and generalize it into the kernel (§3 diagram) rather than leaving it vertical-specific.
4. **Wire install.sh as the standard bootstrap** for any new node added to the hardware fleet — don't hand-configure Radxa/ASUS Twist/etc individually again.
5. **Consolidate the three overlapping Ouroboros/Aurora master docs** into one source of truth before they drift further.

> **Reconciled (priority order after live audit):**
> 1. **Now #1: kill the two P0 `shell=True` sinks** in `workspace-hub/clawdbot-station`
>    (findings P0-A / P0-B) — these are live command-injection sinks and violate the
>    kernel's own top invariant. This outranks everything else.
> 2. `kali-mcp` is **not** blocking (it's complete); adding hashcat/impacket/AD-enum is a
>    scope-gated *enhancement*, not an unblock.
> 3. The freellmapi **handoff-preamble** remains the highest-ROI *feature* gap; its real
>    landing site is `model_router.py`'s GLM↔Sonnet switch (the actual model-change
>    boundary in code), integrated with the existing `free_llm_system.py`.

## Gaps I couldn't fill from here

- No live GitHub access in this chat — repo file trees, actual line counts, and current branch state are from documented summaries, not a fresh clone. If you want a literal file-by-file audit, either paste repo URLs for me to `web_fetch`/clone via Claude Code, or run this from an environment with git access.
- Local machine state (tkpsz3, Radxa, etc.) isn't visible to claude.ai — the install.sh content above is reconstructed from a past session's description, not read fresh from disk.

> **Reconciled:** the "no live access" gap is now closed for the 17 cloned repos — the
> live-audit record below replaces the reconstructed inventory. Machine-state (tkpsz3,
> Radxa, etc.) and the un-cloned repos (`freellmapi`, `revfactory`) remain out of reach.

---
---

# LIVE AUDIT RECORD (added 2026-07-10)

Read-only audit run from Claude Code with git + filesystem access, branch
`claude/new-session-5vhxhz`, across all 17 cloned repos under `/home/user`.
No source code was modified; Phase 4 lists proposals only.

## Phase 1 — Inventory (CLAIM | DOC SAYS | REALITY | DELTA)

| Claim | Doc says | Reality (verified) | Delta |
|---|---|---|---|
| kali-mcp `mcp_server.py` size | "217/500+ lines, truncated, actively broken" | 217 lines, **complete**, 14 `@mcp.tool` fns, clean EOF at `kali_health` | Not truncated — complete-but-limited |
| kali-mcp tool coverage | tmux/hashcat/impacket/AD-enum missing | **tmux present** (`kali_tmux_new/send/read`); hashcat, impacket, AD-enum absent | tmux claim wrong; other 3 confirmed |
| kali-mcp tool inventory | (not enumerated) | `kali_exec, kali_nmap, kali_msf_run, kali_msf_search, kali_sqlmap, kali_gobuster, kali_hydra, kali_tmux_new/send/read, kali_write_file, kali_read_file, kali_which_tools, kali_health` | 14 tools |
| `claude.json` MCP entries | "missing 8 MCP server entries (April 2026 stack)" | **No `claude.json` / `.mcp.json` exists** in any cloned repo | Unverifiable — no such file on disk |
| Curator/Research/Reasoning/Execution split | "only in the Business Suite doc" | **Partially in code:** `hexstrike-ai/kali-agent/model_router.py` = GLM(worker) ↔ Sonnet("Curator") 2-tier router, 15 task-types, Flask `/interpret` | Exists in code, but 2-tier not 3-lane |
| install.sh | "12-phase, 1089 lines" | **No single 1089-line/12-phase installer.** Installers are split: `kali-agent/install_kali_agent.sh` 292, `setup-stage6-kaliagent.sh` 253, `april-redteam/scripts/install.sh` 236, `install-extended.sh` 193; `specter/install.sh` 86; `DesktopCommanderMCP/install.sh` 52 | No 1089-line monolith; distributed |
| docker-compose hardening | "missing mem_limits + healthcheck on some services" | **mem_limit absent on ALL** 7 compose files (0/53 services); healthcheck present only on a minority | Understated — mem_limit fleet-wide gap |
| Repos hosting the OS | `autoboros-backend` / `autoboros-cockpit` hold code | Both are **empty placeholders** (1 `CLAUDE.md` each); code is in `Aurora-AI-Agency/autoboros/` | Repos empty; canonical code elsewhere |
| freellmapi / revfactory | referenced as sources | **Not cloned** in this environment | Absent — cannot audit |
| freellmapi rate-ledger | external, to-implement | **Partially built:** `claude-ecosystem-hub/llm_fallback/free_llm_system.py` (907 ln, per-provider RPM + status) + `gg/autoboros-core` token-budget governor | Already partly in-tree |
| freellmapi handoff-preamble | external, to-implement | **Not found anywhere** | Confirmed missing |

Repo set (all on `claude/new-session-5vhxhz`): Aurora-AI-Agency (375 files),
AutoBoros.AI- (2), AutoborosAi.com (127), DesktopCommanderMCP (123), Director (135),
autoboros-backend (1), autoboros-cockpit (1), claude-ecosystem-hub (84), creator-hub
(68), gg (124), meta-automation-hub (34), n8n-nodes-mcp (41), specter (34),
visual-builder (203), workspace-hub (502), ymiroofing.com.au (19), ymiroofing (40).

## Phase 2 — Invariant findings (SEVERITY | FILE:LINE | ISSUE | FIX)

**P0-A — `shell=True` command sink** | `workspace-hub/02_System_Workspaces/unified-workspace/projects/clawdbot-station/COORDINATION/mcp_tool_registry.py:409` |
`subprocess.run(command, shell=True, …)` where `command` is a caller-supplied
`params` value → shell command injection | Replace with `shlex.split(command)` +
`shell=False` + command allowlist (mirror `autoboros/backend/mcp/mcp_server.py`).

**P0-B — `shell=True` command sink** | `workspace-hub/…/clawdbot-station/clawbot_unified.py:352` |
`subprocess.run(command, shell=True, …)`, `command = params.get("command")` → same
injection class | Same fix; these two share a pattern and should be fixed together.

**P1-A — provider-SDK calls bypass the rate-ledger** | `hexstrike-ai/kali-agent/model_router.py:208` (`glm_client.chat.completions.create`), `:216` (`sonnet_client.messages.create`) |
The one module that routes models calls provider SDKs directly with no proactive
RPM/RPD/TPM/TPD pre-check — violates invariant "all model calls route through the
rate-ledger" | Route through `claude-ecosystem-hub/llm_fallback/free_llm_system.py`
or the `autoboros-core` governor before send. Same pattern in `Director/backend/director/llm/{openai,anthropic,googleai,videodb_proxy}.py` and `tools/composio_tool.py` (vendored third-party app — lower priority, isolate rather than rewrite).

**P1-B — 17 skills missing A2A/Blackboard frontmatter** | `hexstrike-ai/kali-agent/skills/*/SKILL.md` (post-exploit, active-directory, ctf-walkthrough, threat-intel, web-app-security, scope-guard, wireless-recon, pentest-cheatsheet, audit-logger, red-team-report, payload-craft, exploit-dev, network-forensics, vuln-analysis, credential-attack, recon-osint, tool-output-sanitizer) |
Each has `name:` but **no `inputs`/`outputs`/`blackboard_reads`/`blackboard_writes`**
→ violates the SKILL.md A2A-frontmatter invariant | Add the four A2A fields to each
skill's frontmatter; codify the schema so it can't drift. (`workspace-hub` aura /
system-cleaner SKILL.md use a different OpenCode schema — out of scope for A2A.)

**P2-A — `mem_limit` absent fleet-wide** | all 7 `docker-compose.yml` (meta-automation-hub ×2, creator-hub, gg/autoboros-core, claude-ecosystem-hub, Director, autoboros/backend) |
No `mem_limit`/`memory:` on any of ~53 services; unbounded containers can OOM a node
in the "multi-node fleet" model | Add per-service `mem_limit` (and `healthcheck`
where missing) — low-risk hardening.

**INFO — no hardcoded production secrets found** | `workspace-hub/.../test_governance.py` (`api_key="secret123"` test fixture) and an archived chat-export JSON |
The only `api_key=`/`sk-` matches are a unit-test fixture and archived conversation
logs — **not live credentials** | No action; noted to close the secret-scan item.

**N/A — embedding family-lock** | (no site) | No vector-store / embedding-failover path
in the audited core surface; `model_router.py` failover is LLM-only | Invariant not yet
applicable; enforce if/when SimpleMem or a vector store lands.

## Phase 4 — Top-3 fix proposals (NOT executed — awaiting go)

**Fix 1 — Complete `kali-mcp/mcp_server.py` coverage (hashcat, impacket, AD-enum).**
Files: `hexstrike-ai/april-redteam/kali-mcp/mcp_server.py` (+`TOOLS.md`, `requirements.txt`).
Diff shape: add `@mcp.tool` fns following the existing `run_ssh_command(...)` +
`@mcp.tool()` pattern (same as `kali_hydra`/`kali_sqlmap`) — `kali_hashcat`,
`kali_impacket_*`, `kali_ad_enum`. Blast radius: additive, isolated to the kali-mcp
container; no change to existing tools. **GATE: offensive-tooling surface expansion —
requires explicit signed engagement scope before any code is written** (per kickoff
rule and §4.1 workflow step 3). This is an enhancement, not the P0 the doc claimed.

**Fix 2 — freellmapi handoff-preamble on the model-switch boundary.**
Files: `hexstrike-ai/kali-agent/model_router.py` (the real A2A/model-change point —
`route()`/`interpret()` where GLM↔Sonnet switches), integrating the existing
`claude-ecosystem-hub/llm_fallback/free_llm_system.py`. Diff shape: on a detected
model change, inject a TTL'd one-paragraph task-continuity preamble into the outgoing
prompt; fire only on actual switch. Blast radius: prompt-construction only; no API
surface change. Note: the standalone `freellmapi` repo is **not cloned**, but the
pattern does not require it — the landing site and the rate-limit substrate both
already exist in-tree.

**Fix 3 — Eliminate the two P0 `shell=True` sinks (P0-A / P0-B).**
Files: `workspace-hub/.../clawdbot-station/COORDINATION/mcp_tool_registry.py:409` and
`clawbot_unified.py:352`. Diff shape: `shlex.split(command)` + `shell=False` + an
explicit command allowlist, mirroring `autoboros/backend/mcp/mcp_server.py`'s
`shell_exec`. Blast radius: local to clawdbot-station's tool executor; behavior
identical for allowlisted commands, injection closed. **This is the true #1** — a live
injection sink beats a coverage gap. Lands in `workspace-hub`, not this repo.
