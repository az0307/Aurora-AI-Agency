# Aurora AI Agency — Website

Static, self-contained landing page for **Aurora AI Agency** — the public-facing,
client-delivery arm of the Ouroboros group. Content is sourced from
[`../AGENCY.md`](../AGENCY.md).

## Files

| File | Purpose |
|------|---------|
| `index.html` | Entire landing page (inline CSS + JS, no build step) |
| `404.html` | Branded not-found page |
| `_headers` | Cloudflare Pages security + caching headers (CSP, HSTS, etc.) |
| `robots.txt` / `sitemap.xml` | SEO |

## Sections

Hero · Service Lines (6) · Clients in Delivery (Y.M.I Roofing, Evermystic) ·
Our Own Products · How We Work (5 steps) · Contact.

## Deploy (Cloudflare Pages)

1. Create a Pages project pointing at this repo, build output directory `site/`
   (or upload the contents of `site/` directly — there is no build step).
2. Connect the custom domain (`autoboros.ai` / `autoborosai.com.au`).
3. No environment variables or secrets required — the contact CTA is a `mailto:` link.

Also deployable as-is to Vercel, Netlify, or GitHub Pages (static hosting).

## Notes

- Fully self-contained: only external requests are Google Fonts.
- Contact goes to `aaron221048@gmail.com` via `mailto:`. To capture enquiries into
  automation instead, swap the CTA for a form POSTing to a Worker/Pages Function
  (mirror the pattern in the `ymiroofing.com.au` repo's `functions/api/lead.js`).
- All copy is factual and drawn from `AGENCY.md` — no unsubstantiated claims.
