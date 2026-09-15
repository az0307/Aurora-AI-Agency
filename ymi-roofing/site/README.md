# ⚠️ Snapshot — not the deployed site

The live site is **[`az0307/ymiroofing.com.au`](https://github.com/az0307/ymiroofing.com.au)**.
That is the repository Cloudflare Pages builds from, and the one that serves
ymiroofing.com.au. This directory is an older copy kept for reference.

Do not edit this copy expecting it to reach the client, and do not deploy it.

## Verified drift, as at August 2026

Every row below was checked against both copies rather than assumed.

| | This copy | Live repo |
|---|---|---|
| Primary phone | `0422 093 241` (19 occurrences vs 6 for the other number) | `0423 858 503`; 0422 remains as the secondary |
| `areaServed` | A single generic `Melbourne` entry | 13 named suburbs across Melton and Melbourne's west |
| `sanitizePhone` | Turns `61 423 858 503` into `+6161423858503` — the country code is applied twice | Fixed |
| Google Analytics | The conversion hooks exist (`gtag('event', 'generate_lead')`) but there is no loader and no Measurement ID, so nothing is recorded | Live and recording |
| ABN | Not shown anywhere | Displayed, and in the structured data |
| Contrast | 13 WCAG 2.1 AA failures on the home page (measured with axe-core) | 0 across all twelve pages |
| CSP | `connect-src` still reads `https://YOUR-N8N-DOMAIN` — an unreplaced placeholder, so the quote form's request would be blocked by the browser | Not applicable; the form posts to a Pages Function on the same origin |

`privacy.html`, `terms.html`, `robots.txt` and `sitemap.xml` **are** present here. What is
missing is `404.html`, the Pages Functions (`functions/`), the enquiries dashboard, and the
client document pack.

## Other files in this directory

- `ymi-roofing-final.jsx` (448 KB) — a React version of the site. Not what is deployed; the
  live site is static HTML.
- `../dashboard/AuroraYMIDashboard.jsx` — an internal build-tracking dashboard, not the
  client's enquiries portal. Several of its steps are marked "todo" that are long since done
  (the domain is bought, the site is live).

## What to do with it

Fix bugs in the live repo. Deleting this copy would remove the risk of the wrong one being
deployed, but which copy is canonical and what belongs in the archive is a call for whoever
owns this repository, so nothing has been removed.
