# Aurora workflows (vps · agency · admin · personal)

Importable n8n workflows that back the Aurora Assistant and cover the four "lanes". Import
them all at once on the box:

```sh
docker exec -i n8n-n8n-1 n8n import:workflow --separate --input=/workflows/aurora   # if mounted
# or, from this folder on the box:
for f in *.json; do docker cp "$f" n8n-n8n-1:/tmp/ && docker exec n8n-n8n-1 n8n import:workflow --input="/tmp/$f"; done
```
Then open n8n, and for each one: connect the credentials it names, and toggle **Active**.

> **CLI import always lands a workflow *inactive*** (verified on n8n with Postgres 16, 2026-09-27),
> and each file carries a stable top-level `id` so `import:workflow` works on Postgres (without
> an id it errors `null value in column "id"`). Activation is a **UI toggle** in the editor, or a
> `PATCH` via the n8n API using your `N8N_API_KEY`. Until `assistant-intake` is Active, the
> console's "send a task" box gets a 404 from n8n — that's expected, not a wiring fault.

| File | Trigger | What it does | Connect in n8n |
|---|---|---|---|
| `assistant-intake.json` | Webhook `POST /webhook/assistant-intake` | The control panel's "send a task" box: asks the router, replies on Telegram | **Header Auth** cred "Aurora Router" (`Authorization: Bearer <LITELLM_MASTER_KEY>`); a **Telegram** cred |
| `vps-health-digest.json` | Cron 06:50 | Pings the router + n8n, sends a nightly one-liner | Telegram cred |
| `agency-lead-intake.json` | Webhook `POST /webhook/agency-lead` | Reusable client-lead intake → Google Sheet + alert | Google Sheets cred + sheet id; Telegram |
| `admin-weekly-digest.json` | Cron Mon 08:05 | Monday admin/finance checklist via the router | Router + Telegram creds |
| `personal-morning-brief.json` | Cron 06:30 | A short good-morning brief | Router + Telegram creds |
| `daily-runsheet.json` | Cron 06:15 | **The consolidated day plan** (Focus/Agency/Admin/Personal/Box) in one message | Router + Telegram creds |

**Credentials, not secrets in JSON.** These files carry no keys. n8n stores credentials
encrypted (that's what `N8N_ENCRYPTION_KEY` protects — back it up). The router is reached at
`http://router-litellm-1:4000` over the shared Docker network, so the router's host port can
stay loopback-only.

Verified against n8n docs (Context7, 2026-09-27): the webhooks use `responseMode: onReceived` (immediate ack — the fire-and-forget shape these want), so there is no separate Respond-to-Webhook node; the production URL registers when the workflow is published/active. Tested 2026-09-27 on real Docker: all six import cleanly with `n8n import:workflow` into Postgres-backed n8n, and their node graphs validate. The console → nginx `/intake` → n8n path was confirmed end-to-end (n8n receives the POST; it returns its own 'activate the workflow' notice until you toggle Active).
