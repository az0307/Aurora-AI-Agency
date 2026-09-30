# Y.M.I Roofing — Accounts runbook (DRAFT)

> **Status: DRAFT, 2026-09-30.** Nothing in this document has been done. No account has been created
> on Ben's behalf and none should be.

## Why Claude/Aurora does not "sign up in Ben's name"

- **Ben has to be the one signing up.** Google, Meta, Cloudflare and others require the account
  holder's own identity checks (e.g. Google's Business Profile live-video verification), his
  acceptance of their terms, and his payment method. Creating those accounts *as* Ben would be
  misrepresenting who agreed to them.
- **Aurora's standing rule:** every account is created under the **client's** login; Aurora is added
  afterwards as Manager/Admin with consent recorded. Never the reverse. That makes the exit clause
  true on day one.
- **No passwords.** Ben never sends a password to anyone. Access is granted from inside each account
  (delegated user), which he can revoke at any time.

**How it works in practice:** a 30–45 minute screen-share with Ben. He has his phone (for 2-step
verification and the GBP video) and his laptop. Aaron talks him through; Ben clicks; Aaron is added
as manager at the end of each step. Record consent in the log at the bottom of this file.

## Current state of accounts (owner today: CONFIRM each — these are unknown from the repo)

| Account | Needed for | Must be owned by | Owner today | Delegated access for Aaron | State |
|---|---|---|---|---|---|
| Domain registrar (ymiroofing.com.au) | The website address | Ben / Y.M.I Roofing Pty Ltd | **CONFIRM** (Services Agreement §5.1 is still an open question) | Not needed day-to-day | Live domain |
| Cloudflare (DNS + Pages + D1) | Hosting, form function, database | Ben's own Cloudflare account | **CONFIRM** (the account that holds the `ymiroofing` Pages project and the `ymi-leads` D1 database) | Member with the roles needed | Live |
| Resend (email delivery) | Quote-form emails | Ben or documented as Aurora-held | **CONFIRM** (domain shows verified; zero emails sent so far) | — | Needs a proven test |
| Google Search Console | Indexing, sitemap | Ben's Google account | **CONFIRM** (property verified 4 Aug 2026 — by whom?) | Full user | Live — resubmit sitemap |
| Google Analytics 4 | Visits, phone taps, forms | Ben's Google account | **CONFIRM** (Measurement ID `G-1JZCR7ZBF3` is on the site) | Editor | Live |
| Google Business Profile | Maps + local search (biggest call source) | Ben | **Not verified** | Manager | **Blocked on Ben's live video** |
| Google Ads | Search ads | Ben, with his own card | Not created | Standard user or manager link | Not started |
| Meta Business (Facebook Page, Instagram, ad account) | Social presence, ads, ManyChat | Ben's Meta Business portfolio | Not created/unknown | Partner access | Not started |
| Twilio | SMS alerts and review requests | Ben, his own card | Not created | Delegated | **Not until the compliance gates below are cleared** |
| ManyChat | Facebook/Instagram chatbot | Ben | Not created | Delegated | Not started |
| Bing Places / Apple Business Connect / directories | Local listings | Ben | Not started | — | See `ymiroofing.com.au/CITATIONS.md` |

## Order (earns money first, lowest risk first)

1. **Confirm who owns what today** (table above). Ben should own the domain and the Cloudflare account;
   if Aaron holds either, plan the transfer *now*, not at exit.
2. **Prove the form.** One marked test enquiry, Ben watching his inbox. Then check the `ymi-leads`
   database for the row. Until this passes, do not describe delivery as working.
3. **Google Business Profile** (Ben, live video ~30 s, business name exactly **Y.M.I Roofing**).
4. **Search Console + GA4:** add Aaron as a delegated user; resubmit `sitemap.xml` (11 URLs).
5. **Review link:** paste Ben's "Ask for reviews" link into `assets/site-config.js`
   (`YMI_GBP_REVIEW_URL`) and deploy; `/review/` and the QR card then send customers to Google.
6. **Google Ads** and **Meta** only once 2–5 work and Ben has agreed a budget in writing.
7. **Twilio/ManyChat/automation** only after the compliance gates below.

## Per-platform steps (check current menu names on the day; platform screens change)

### Google Business Profile — business.google.com
1. Ben signs in with the Google account that will own the business (ideally a dedicated one, e.g. a
   business Gmail, not his personal one).
2. Search first; **claim an existing listing rather than creating a duplicate.**
3. Name: exactly `Y.M.I Roofing`. Category: roofing contractor. If he has no public shopfront, set it
   up as a **service-area business**, list only the 13 confirmed suburbs, and hide the address.
4. Same phone, website and suburb list as the site (NAP must match everywhere). Primary number:
   `0422 093 241` (confirm with Ben first).
5. Verify (live video/other method Google offers). Only Ben can do this.
6. Add Aaron as **Manager**, not Owner (Profile settings → people and access).
7. Add real job photos and the 7 services. **No fake reviews; never gate or filter who is asked.**

### Google Search Console / Analytics 4
- Add Aaron via each product's user-management screen (Search Console: Settings → Users and
  permissions; GA4: Admin → Account access management). Least privilege that lets him work.

### Google Ads — ads.google.com
- Ben creates the account with his own payment method; Aaron is a user (or a manager-account link
  Ben accepts). Never hold Ben's ad spend or card.
- Link GA4; import the two site events (`generate_lead`, `phone_call_click`) as conversions.
- Target only the 13 confirmed suburbs. Daily budget set by Ben in writing.

### Meta (Facebook + Instagram)
- Ben creates a Business portfolio at business.facebook.com, then the Page `Y.M.I Roofing`, an
  Instagram professional account and an ad account under it, with his own payment method.
- Aaron gets **partner/delegated access** to the assets from inside Ben's portfolio.
- The Facebook/Instagram footer links on the site are placeholders until the real URLs exist.

### Cloudflare / domain / Resend
- Ben as account owner; Aaron added as a member with only the roles he needs. Record where the domain is
  registered and whose name is the registrant; fix `Aurora_Services_Agreement_SOURCE.md` §5.1 to match.

### Twilio and ManyChat (later)
- Ben's accounts and cards. Check the current Australian SMS sender-ID requirements before sending
  anything. **Do not create either account until the gates below are cleared.**

## Compliance gates before any automated message is switched on (hard stops)

1. **Spam Act 2003:** the opt-out list is **checked before every send** (not merely recorded); every
   message carries a working opt-out; sender is identifiable; consent is recorded and how it was
   obtained is known.
2. **Privacy:** every processor (Resend, Cloudflare, Google Analytics, and Twilio/ManyChat/Meta once
   used) is named in `privacy.html` *before* it handles customer data.
3. **Australian Consumer Law:** no fabricated or filtered reviews; no ranking promises ("#1"); no
   unverified licence or insurance claims.
4. **Human-in-the-loop:** automated client-facing messages are drafted by Aurora and approved by a
   person; no autonomous sending.

## Consent and access log (fill in as each step is done)

| Date | Account | What Aaron was given | Given by | How (screen-share/email) | Revoke path |
|---|---|---|---|---|---|
| | | | | | |

## Offboarding

Aurora removes its own access from each account and confirms in writing. Because Ben owns everything
from day one, nothing needs migrating.
