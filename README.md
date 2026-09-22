# Aurora AI Agency

> AI-native agency — client delivery, automation and hosting. Built in Australia under the Ouroboros umbrella.

## Client work

| Client | Deliverable |
|--------|-------------|
| **YMI Roofing** | Lead-gen website + ops package for Y.M.I Roofing (Ben Breheny, ACN 695 710 055) |

## What's in this repo

Aurora-AI-Agency is a monorepo scoped to agency and client work. Each subdirectory is an
independent project with its own stack:

```
client-portal/  Aurora client portal (Next.js 14 + Clerk + Prisma + Stripe)
ymi-roofing/    Client: YMI Roofing website + ops package
site/           Aurora's own marketing landing page (static)
infra/          Self-hosting strategy + Docker stacks (n8n, LLM router, monitoring, …)
evermystic/     Experimental: self-contained Haiku executor tool
_empire/        Strategy & architecture docs
```

> The AutoBoros orchestration engine, the HexStrike security platform, and the gastown
> scaffolding CLI previously lived here. They belong to their own SPVs/repos and have been removed
> so this repo stays agency- and client-focused.

See [CLAUDE.md](./CLAUDE.md) for full technical documentation on every subsystem.

## Organisation

```
Ouroboros Foundation Ltd Pty  (AU)
└── Aurora AI Agency      — client delivery (this repo)
```

---

Aurora AI Agency · Australia · 2026
