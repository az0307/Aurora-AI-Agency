# Aurora constitution
<!-- Read by GitHub Spec Kit. Version 1.0.0 · ratified 2026-09-27. -->

The non-negotiable rules every spec, plan and change in this repo inherits.

## Principles
1. **Secrets stay secret.** Only `.env.example`/`secrets.env.example` are committed. Real secrets
   live in `/opt/aurora/secrets.env` (root, 600) and per-stack `.env`. Provider tokens never leave
   the operator's phone/session. No secret value is ever printed or logged.
2. **Client data is sacred.** Client PII (e.g. Y.M.I Roofing leads) is routed only through paid model
   chains, never a `-free` chain. Data stored in the EU is disclosed to clients (APP 8).
3. **Private by default.** Services bind `127.0.0.1`; access is over Tailscale (`serve`, never Funnel).
   Internet-facing images are pinned. SSH is closed once Tailscale works.
4. **Money and destruction need a human.** Spending (VPS purchase) needs a typed confirmation; the
   Kali toolbox and agent actions are operator-driven, never unattended.
5. **Test before you trust.** Validate against spec-validating mocks before touching a paid API; run
   the repo's own checks (bash -n, check-chains.py, compose config, npm lint) before pushing.
6. **Docs move with code.** A change updates the docs and `tasks.yaml` in the same PR.
7. **Staged, not all-at-once.** On the 8 GB box, bring stacks up one at a time (`aurora up`).
8. **Scope discipline.** Agency + client work only; AutoBoros/HexStrike stay in their own SPVs.

## Governance
- Amendments happen by PR that edits this file and bumps the version (semver: breaking rule change =
  major). The ratified date changes only on a major.
- A spec or PR that conflicts with a principle is rejected or the principle is amended first — never
  silently overridden.
- The PR steward / reviewer checks every change against these principles.
