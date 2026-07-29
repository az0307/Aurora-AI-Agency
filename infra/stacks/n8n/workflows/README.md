# n8n workflow library

Workflows staged for import into the n8n stack. **None of these have been run against a live
n8n instance yet** — there isn't one provisioned. Treat every file here as *staged*, not
*validated*, until it imports cleanly and executes.

Import order and credential setup differ per bundle — see each section.

## `freelance-pipeline/` — the agency revenue loop ⭐

Four chained workflows covering lead → cash. Import in numeric order; they hand off via
Postgres status changes and webhooks.

| File | Nodes | Does |
|---|---|---|
| `1-job-scraping-lead-discovery.json` | 12 | Scrapes freelance platforms every 4h, scores by hourly rate + urgency + source, dedupes, enriches company data, alerts on high scores |
| `2-proposal-generation-delivery.json` | 9 | On `qualified`: generates a proposal via Claude, creates + shares a Google Doc, emails it, schedules day-2 follow-up |
| `3-project-setup-task-generation.json` | 13 | On `won`: creates client/contact/project, generates tasks from an SOP template, builds Drive folders, books kickoff |
| `4-invoice-generation-payment-tracking.json` | 13 | On `delivery`: invoice number + record, PDF, Stripe payment link, email, reminder at day 23, testimonial request |
| `INSTALL-NOTES.json` | — | Prerequisites, setup steps, the Postgres `NOTIFY` trigger SQL, and target metrics |

**Known rework before these will run:**
- Credentials are referenced as inline expressions (e.g. `{{$credentials.brightData.token}}`
  in an HTTP header value). That is **not** how n8n's credential system works — rewire each
  node to use a proper credential entry.
- Some Postgres nodes use a `queryParameters` string shape that may not match the current
  node version; verify against your n8n version.
- Requires a `leads`/`clients`/`projects`/`tasks`/`invoices` schema plus API keys for
  Anthropic, Bright Data, Clearbit, Stripe, Google Workspace, Slack.

## `trend-engine/` — content/monetisation engine

Seven workflows plus a blueprint. Heavier and more dependency-hungry.

| File | Nodes |
|---|---|
| `trend_engine_orchestrator.json` | 39 |
| `trend_engine_orchestrator_github.json` | 19 |
| `trend_engine_monetization.json` | 17 |
| `trend_engine_mailing.json` | 10 |
| `trend_engine_analytics.json` / `trend_engine_retry.json` | 4 each |
| `trend_engine_github_monitor.json` / `trend_engine_github_trigger.json` | 3 each |
| `BLUEPRINT.json` | setup order, 26 env placeholders, post-install checklist |

**Read `BLUEPRINT.json` first** — it defines the import order and the Google Sheets tabs to
create. Be aware it expects ~20 credentials (Apify, Printful, Gumroad, TikTok, Pinterest,
LinkedIn, Mailchimp…). Enable publishing nodes one at a time, per its own checklist.

## `specs/` — design reference, NOT importable

`workflow-library-SPECS.json` describes 20 workflows (lead discovery, onboarding, content
distribution, health monitoring, incident response…) with outputs and impact estimates.

**These will not import.** Node types are written descriptively (`"Schedule Trigger"`) rather
than as n8n type identifiers (`"n8n-nodes-base.scheduleTrigger"`), and there's no n8n-format
connection graph. Use them as a build catalogue — pair with the
[`czlonkowski/n8n-mcp`](../RESOURCES.md) MCP to turn a spec into a real workflow.

## Deploying

```sh
# once the n8n stack is up (see ../../../runbooks/DAY1.md)
# UI: Workflows → Import from File
# or API:
curl -X POST "http://127.0.0.1:5678/api/v1/workflows" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @freelance-pipeline/1-job-scraping-lead-discovery.json
```

Import with publishing/sending nodes **disabled** first, confirm the data path, then enable
outbound nodes one by one. Several of these send client-facing email and create Stripe
payment links — a misfire is externally visible.
