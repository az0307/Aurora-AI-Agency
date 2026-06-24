# Aurora AI Agency

> AI-native agency — automation systems, security tooling, and client delivery. Built in Australia under the Ouroboros umbrella.

## What we build

| Product | Description | Stack |
|---------|-------------|-------|
| **AutoBoros** | AI automation OS — multi-agent orchestration, L0–L4 job ladder, n8n workflows, MCP server, operator cockpit | FastAPI · React 19 · n8n |
| **HexStrike AI** | Red team platform — live Kali Linux integration, 14 security tool connectors, SSH-over-WebSocket | Express · React · xterm.js |

## Client work

| Client | Deliverable |
|--------|-------------|
| **YMI Roofing** | Lead-gen website + ops portal for Y.M.I Roofing (Ben Breheny, ACN 695 710 055) |

## Internal tools

| Tool | Description |
|------|-------------|
| **Gastown** | Zero-dependency Python CLI — generates project scaffolding from a natural language description |

## Organisation

```
Ouroboros Foundation Ltd Pty  (AU)
├── AutoBoros             — engine: n8n orchestration, MCP mesh, multi-agent
├── Aurora AI Agency      — client delivery (this repo)
└── HexStrike             — red team & security tooling
```

## This repo

Aurora-AI-Agency is a monorepo. Each subdirectory is an independent project with its own stack:

```
autoboros/      FastAPI backend + React cockpit (the AutoBoros engine)
hexstrike-ai/   HexStrike red team platform (Express + Kali integration)
ymi-roofing/    Client: YMI Roofing website + ops package
gastown/        Internal: project scaffolding CLI
_empire/        Strategy & architecture docs
```

See [CLAUDE.md](./CLAUDE.md) for full technical documentation on every subsystem.

---

Aurora AI Agency · [autoboros.ai](https://autoboros.ai) · Australia · 2026
