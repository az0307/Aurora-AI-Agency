# Client-onboarding runbook — take on a new client, cleanly and reversibly

The repeatable process for standing up (and later tearing down) a client. The core principle
is **blast-radius isolation**: **one Hetzner Project per client**, with its **own API token and
firewall**, so a mistake, a leak, or a compromise is contained to that client and never touches
the agency box or another client.

This runbook is the *client-specific wrapper* around the standard box build. It does **not**
duplicate the mechanics — it references them:
- Standing a box up → [`DAY1.md`](./DAY1.md)
- Backups + restore drill → [`BACKUP.md`](./BACKUP.md)
- What to install and why → [`../STACK.md`](../STACK.md) · services + MCPs → [`../SERVICES.md`](../SERVICES.md)

> Naming convention used below: `<client>` = a short slug (e.g. `ymi`). Use it consistently for
> the Project, the box hostname, DNS, and the backup path so everything is greppable later.

---

## 0. Before you provision (intake + guardrails)
- [ ] **Scope + contract signed.** What are you hosting/automating, expected data, SLAs.
- [ ] **Data-sensitivity check.** Any PII? If so, re-read the **AU data-residency / APP 8** note
      in [`../README.md`](../README.md): hosting PII in **Singapore is a cross-border disclosure**.
      Decide region **now** (an EU/AU-appropriate box or a compliant path for PII-touching
      workflows) — not after data is flowing.
- [ ] **Domain + Cloudflare.** Confirm who owns the domain and that it's on Cloudflare (or will
      be). You need Cloudflare for the Tunnel + Access model.
- [ ] **Credential hygiene.** New client = new secrets. Nothing shared with another client or the
      agency box. All secrets go into the secrets manager (Infisical), never into git.

## 1. Create an isolated Hetzner **Project** (the isolation boundary)
1. In the Hetzner Cloud console, create a **new Project** named `aurora-<client>`.
2. In that Project, create a **dedicated API token** (Read/Write). This token can only see/act
   on **this** Project's resources — that is the blast-radius wall.
3. Store the token in the secrets manager as `hetzner_token_<client>`.
4. Scope Claude to it: give the **Hetzner MCP** *only this token* when working this client, so
   Claude's provisioning reach = this client's Project and nothing else
   (see [`../mcp/.mcp.json.example`](../mcp/.mcp.json.example) and [`../SERVICES.md`](../SERVICES.md)).

> One token per Project is the whole game: a leaked or misused `<client>` token can't enumerate,
> resize, or destroy anything in `aurora-<otherclient>` or the agency Project.

## 2. Provision the client box
Follow [`DAY1.md`](./DAY1.md) steps 1–2, inside the new Project:
- Region per the §0 data-sensitivity decision. **Reminder:** CAX (ARM) is **EU-only** — for
  Singapore (`sin`, lowest AU latency) you must use **AMD CPX/CCX**; **never pair `cax*` with
  `sin`**. Size per workload (see the workload→placement table in [`../README.md`](../README.md)).
- Boot from [`../hetzner/cloud-init.yaml`](../hetzner/cloud-init.yaml) (hardened base: key-only
  SSH, ufw default-deny, fail2ban, Docker) — identical hardening to every other box.
- [ ] Verify the base per `DAY1.md` §2 (`ssh`, `ufw status`, `docker version`).

## 3. Per-client **firewall**
- [ ] Attach a Hetzner **firewall** scoped to this Project: default **deny incoming**; allow only
      what the tunnel model needs. Because ingress rides the **outbound-only Cloudflare Tunnel**,
      the box needs **no inbound port opened** — keep SSH as a separate controlled path (key-only,
      ideally also via the tunnel). This mirrors the security baseline in [`../README.md`](../README.md).

## 4. Deploy the client's stack
Deploy **only that client's stack** on their box — nothing from other clients, keep it minimal:
- [ ] Control plane + tunnel per [`DAY1.md`](./DAY1.md) §3–4 (Dokploy, then Cloudflare Tunnel +
      Access with an **email allowlist policy scoped to this client's people**).
- [ ] The stacks they actually need from [`../stacks/`](../stacks/), each with its **own
      `.env`** (copied from `.env.example`, filled from the secrets manager) — e.g.
      [`n8n`](../stacks/n8n/) or [`activepieces`](../stacks/activepieces/) for automation,
      [`monitoring`](../stacks/monitoring/), and any client deliverable.
- [ ] All service ports stay on **127.0.0.1** and are reached via **Cloudflare Access** — never
      published publicly (same rule as the on-demand pool in [`../SERVICES.md`](../SERVICES.md)).
- [ ] If the deliverable is a **static site** (e.g. Y.M.I), it belongs on **Cloudflare Pages**,
      not the VPS — the box is only for automation/backends.

## 5. DNS + Cloudflare Access
- [ ] Add public hostnames on the client's tunnel (e.g. `automate.<client>.com → localhost:5678`
      for standalone n8n, or route to Dokploy's Traefik) per [`DAY1.md`](./DAY1.md) §4.
- [ ] **Access policy per hostname** — allowlist the client's emails / your team only; add OTP.
- [ ] Restrict any app **CORS** from wildcard `*` to the real domain(s) (the standing n8n /
      Y.M.I open item — don't repeat it for a new client).
- [ ] Smoke test through the tunnel per [`DAY1.md`](./DAY1.md) §6.

## 6. Backups (before they rely on it)
Set up backups **on the client box** following [`BACKUP.md`](./BACKUP.md), kept **isolated**:
- [ ] Back up to a **client-scoped path** — the restic repo already namespaces by hostname
      (`rclone:r2:aurora-backups/$(hostname)`), so a distinct hostname keeps client snapshots
      separate. Use a **separate restic password** (and ideally a separate R2 bucket/prefix or
      Storage Box) per client so one client's backup credentials can't read another's.
- [ ] Back up the automation **encryption key** (n8n `N8N_ENCRYPTION_KEY` / Activepieces
      `AP_ENCRYPTION_KEY`) to the secrets manager — losing it makes stored credentials unreadable.
- [ ] **Run the restore drill once, for real** (`BACKUP.md` §4). A backup you haven't restored
      is a hope, not a backup.
- [ ] Take a **Hetzner snapshot** as the fast whole-box layer (covers "I broke the box"; restic
      off-box covers "the region/provider is gone" — keep both).

## 7. Handover
- [ ] **Access:** add the client's people to the relevant Cloudflare Access policies (least
      privilege). Remove anyone who shouldn't stay.
- [ ] **Docs:** hand over what they need to operate — URLs, what each service does, support
      boundary. Keep agency-internal ops docs internal.
- [ ] **Runbook entry:** record the client in your ops notes — Project name, box, region, stacks,
      hostnames, backup location, secret names (names, **not** values). Future-you needs the map.
- [ ] **Monitoring → phone:** wire Beszel/Uptime Kuma alerts to **ntfy** so you hear about their
      box going down before they do (see [`../STACK.md`](../STACK.md)).

## 8. Offboarding / teardown (reversible by design)
When an engagement ends, tearing a client down is clean *because* they were isolated:
- [ ] **Final backup + export.** Take a last restic snapshot and a Hetzner snapshot; export any
      data the client is owed (n8n/Activepieces workflows, DB dumps) and deliver it.
- [ ] **Confirm retention.** Agree how long you keep the final backup (and honour any contractual
      / privacy retention obligation) before deleting it.
- [ ] **Revoke access.** Remove Cloudflare Access policies + hostnames; delete the tunnel.
- [ ] **Destroy the box + resources.** Delete servers, volumes, firewalls, and snapshots in the
      client's Project (Claude can do this via the Project-scoped Hetzner MCP).
- [ ] **Rotate/revoke secrets.** Revoke the `hetzner_token_<client>` API token, delete the
      client's `.env`s and `restic` password from the secrets manager, and remove the backup
      repo/bucket once retention lapses.
- [ ] **Delete the Hetzner Project** once empty — the isolation boundary goes away with it, and
      nothing lingers that could bill you or leak.

---

### Why this shape
Everything a client touches lives inside **their own Hetzner Project** (own token, own firewall,
own box, own secrets, own backup path). That single decision makes onboarding a checklist and
offboarding a delete — no untangling shared infrastructure, and no client can reach another's.
