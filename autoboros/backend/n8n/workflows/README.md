# n8n Workflows for AutoBoros

## Setup

1. Start n8n: `docker compose up n8n`
2. Open http://localhost:5678
3. Import the workflow JSON files from this directory
4. Set the webhook URL in FastAPI: `N8N_WEBHOOK_URL=http://localhost:5678/webhook/autoboros`

## Workflows

- **example_approval.json** — Minimal approval→callback loop. Clone this for each skill.
- **lead_first_touch.json** — Captures IG DM, drafts opener, flags L2.
- **invoice_filer.json** — Generates PDF, names to convention, files to Drive.

## Conventions

- All workflows must end with an HTTP Request node hitting `/api/v1/n8n/callback`
- The callback payload must include `job_id` and `result` object
- Use the `callback_url` field from the inbound webhook — don't hardcode
