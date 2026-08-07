# n8n GitHub repos worth including

**Verified via web search on 2026-07-29.** Star counts and contents change — re-check before
relying on any number here.

> ⚠️ This file **replaces** an earlier internal `N8NRESOURCES.md` that circulated with
> unverifiable entries. That list credited `awesome-n8n` to `sladkovm` (the real one is
> **restyler**) and listed repos like `n8n-io/n8n-render` and `n8n-io/n8n-railway` as
> *official* n8n repos for third-party platforms, which is implausible. Its star counts were
> also suspiciously round. **Don't act on that list** — use this one.

## Tier 1 — include these first (highest leverage for Aurora)

| Repo | What it gives us | Why it matters here |
|---|---|---|
| [`czlonkowski/n8n-mcp`](https://github.com/czlonkowski/n8n-mcp) | MCP server giving Claude Code deep knowledge of n8n's ~2,285 nodes | **The missing piece in our MCP set** — lets Claude author/validate workflows against real node schemas instead of guessing. Added to [`mcp/.mcp.json.example`](../../mcp/.mcp.json.example). |
| [`czlonkowski/n8n-skills`](https://github.com/czlonkowski/n8n-skills) | 7 Claude Code skills for building production-ready n8n workflows | Mirror to `/opt/aurora/skills/` per [`SERVICES.md`](../../SERVICES.md). This is the repo the uploaded design doc was built around — that reference was correct. |
| [`czlonkowski/n8n-manager-for-ai-agents`](https://github.com/czlonkowski/n8n-manager-for-ai-agents) | MCP server to *manage* live n8n workflows | Complements n8n-mcp: one authors, one operates. Optional until the instance is live. |

## Tier 2 — template/workflow corpora (import selectively)

| Repo | Scale | Notes |
|---|---|---|
| [`Zie619/n8n-workflows`](https://github.com/Zie619/n8n-workflows) | ~2,053 workflows, searchable UI | The big one (~55k stars). **Caveat: repo history was rewritten in Aug 2025 for DMCA compliance** — treat provenance carefully before shipping anything to a client. |
| [`enescingoz/awesome-n8n-templates`](https://github.com/enescingoz/awesome-n8n-templates) | 280+ curated | Cleaner, more curated than the mega-collections. Good first stop. |
| [`Danitilahun/n8n-workflow-templates`](https://github.com/Danitilahun/n8n-workflow-templates) | ~2,053, organised + indexed | Same corpus, better browsing/search tooling. |
| [`restyler/awesome-n8n`](https://github.com/restyler/awesome-n8n) | Community nodes ranked by downloads | Use this to pick community nodes by actual adoption rather than vibes. |

## Tier 3 — security workflows (HexStrike)

| Repo | What |
|---|---|
| [`CyberSecurityUP/n8n-CyberSecurity-Workflows`](https://github.com/CyberSecurityUP/n8n-CyberSecurity-Workflows) | 100+ Red/Blue/AppSec playbooks — ~30 Red Team/pentest, ~35 Blue Team/SOC/DFIR, ~25 AppSec/DevSecOps, ~10 platform. Integrates Semgrep, Trivy, Checkov, cloud providers. |
| [`QuantumDef1337/n8n-soc-automation`](https://github.com/QuantumDef1337/n8n-soc-automation) | SOC templates: real-time alerting, automatic IP blocking, endpoint scanning. |

Directly relevant to the **UltronOmega / HexStrike** security arm — these map onto the
existing playbooks in `hexstrike-ai/playbooks/`. Many are *blueprints* (purpose + flow
outline) rather than importable JSON; expect to build the nodes.

## Official

[`n8n-io/n8n`](https://github.com/n8n-io/n8n) — the platform itself (fair-code, 400+
integrations). Docs at [docs.n8n.io](https://docs.n8n.io). Note that several "official"
sub-repos named in the old list could not be confirmed to exist.

## How to use these with our stack

1. **Add the MCP** — `czlonkowski/n8n-mcp` is already in `mcp/.mcp.json.example`; set
   `N8N_API_URL` + `N8N_API_KEY` once the instance is up.
2. **Mirror the skills** to `/opt/aurora/skills/` so any agent landing on the box has them.
3. **Import selectively** from Tier 2 — don't bulk-import thousands of workflows into a
   1-4 GB box. Pull the handful you need per client.
4. **Vet before client delivery** — especially anything from the DMCA-rewritten corpus.
