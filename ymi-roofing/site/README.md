# ⚠️ Snapshot — not the deployed site

The live site is **[`az0307/ymiroofing.com.au`](https://github.com/az0307/ymiroofing.com.au)**.
That is the repository Cloudflare Pages builds from and the one that serves
ymiroofing.com.au. This directory is an older partial copy kept for reference.

Do not edit this copy expecting it to reach the client, and do not deploy it.

## Known drift, as at August 2026

| | This copy | Live repo |
|---|---|---|
| Primary phone | `0422 093 241` throughout | `0423 858 503`; the 0422 number remains as the secondary |
| Service area | Whole-of-Melbourne regions | Melton and Melbourne's west, 13 named suburbs |
| `sanitizePhone` | Doubles the country code — a number entered as `61 423 858 503` becomes `+6161423858503` | Fixed |
| Analytics | Not present | GA4 live |
| ABN | Not shown | Displayed, and in the structured data |
| Contrast | Fails WCAG 2.1 AA in 12 places | 0 violations across all pages |

It is also incomplete: no `privacy.html`, `terms.html`, `robots.txt`, `sitemap.xml`,
`404.html`, no Pages Functions, no enquiries dashboard and no client document pack.

Fix bugs in the live repo. If this copy is no longer wanted, deleting it removes the
risk of the wrong one being deployed — but that is a call for whoever owns the archive,
so nothing has been removed here.
