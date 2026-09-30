# Y.M.I Roofing — Billing decision record (DRAFT for Aaron)

> **Status: DRAFT — recommendation only. Nothing here has been sent to Ben and no figure below is
> approved.** Drafted 2026-09-30 from the Services Agreement source, `INVOICE-AURORA-0001.md`
> (superseded), `INVOICE-TEMPLATE.txt`, `PHASE-2-PROPOSAL.md`, the Aurora service catalogue and the
> live state of `ymiroofing.com.au`. Decisions that only Aaron can make are marked **[DECIDE]**.

## 1. Why this needs a decision

Three documents in this folder disagree, and none of them is an approved invoice:

| Source | Setup | Monthly | Notes |
|---|---|---|---|
| Services Agreement source §3.1–3.2 | $700 | $350 | Never solicitor-reviewed; liability clause is a placeholder; carries its own "do not send" warning |
| `INVOICE-TEMPLATE.txt` | $700 | $350 × 2 months | Bills "website build + n8n automation setup" and a retainer that implies automation. The automation has never run |
| Pricing audit (referenced in `INVOICE-AURORA-0001.md`) | $4,550 list / $2,750 payable | $150 | Market-benchmarked. Internal reference only — never put in front of Ben retroactively |

`INVOICE-AURORA-0001.md` is marked **SUPERSEDED — DO NOT SEND**. It deliberately keeps the old ABN
`45 746 317 471` as a record of a past mistake. **Aurora's ABN is `15 870 917 390`** (checked against
the public ABR record on 2026-09-30: Baker, Aaron James Reginald, sole trader, VIC 3338, not
registered for GST). The other ABN (`45 746 317 471`, VIC 3165) is a different record — never use it.

## 2. What is actually delivered today (verified 2026-09-30 — see the site audit)

| Component | State |
|---|---|
| Website on Cloudflare Pages (home + 7 service pages + service areas + review page + privacy/terms) | **LIVE** |
| Quote form → email (Resend) + D1 record + enquiries dashboard | **NEEDS SWITCHING ON / UNPROVEN** — built, but no test enquiry has ever been sent; `ymi-leads` has 0 rows; Pages bindings can't be seen from the repo |
| Google Analytics (GA4 + phone-tap and form events) | **LIVE** (real Measurement ID in the page) |
| Google Business Profile | **NOT DEPLOYED** — Ben must verify (live video) |
| Automated SMS alerts, review machine, missed-call text-back, chatbot | **NOT DEPLOYED** — specs and workflow files only; all workflows `active: false`; n8n host does not resolve |

Rule applied: *honest state labelling* and *nothing is done until it's invoiced* — bill only what is
live; never bill for what is switched off.

## 3. Options

| | A. Bill only what is live (recommended) | B. Bill the agreed $700 / $350 as written | C. Re-price to the audit figure |
|---|---|---|---|
| Setup | $700 | $700 | $2,750 |
| Monthly | **$200** (Essentials: hosting, maintenance, monthly report, ~1 h of small changes) → **$400** (Growth) when GBP is verified and the review machine is live | $350 from month 1 | $150 |
| Honesty vs delivery | Matches what runs | Charges $350 for a retainer whose automation half is off | Bills a price Ben never agreed |
| Breaks a pricing rule? | No | Only "state what's live" | **Yes** — never retro-bill a fee the client never agreed; don't reprice mid-engagement |
| Trust / case-study value | High — "you only pay for what's running" | Medium | Low |

**Recommendation: A.** Keep the $700 Ben has seen (it is far below the $1,500–3,500 one-off market
range, so it needs no defending). Start the retainer at the tier that matches what runs, and step up
on evidence at a month-6 review. Use the audit figure for the *next* client.

**[DECIDE]** Confirm what Ben has been told or agreed **in writing** (email/SMS/signed agreement).
If he agreed $350/month explicitly, honour it only if you are comfortable billing it while the
automation is off; otherwise say so openly and move forward, never backwards.

## 4. Invoice content (Option A)

- Title the document **"Invoice"**, never "Tax invoice" (Aurora is not GST-registered; supply is
  "not subject to GST", not "GST-free").
- From: Aaron Baker, trading as Aurora AI Agency — ABN `15 870 917 390`. Street address still
  outstanding (Services Agreement §10). **[DECIDE]** confirm ASIC business-name registration for
  "Aurora AI Agency" (the ABR shows no registered business name of that kind; this is a separate ASIC
  register I could not check).
- To: Y.M.I Roofing Pty Ltd — ACN `695 710 055`, ABN `14 695 710 055` (ABR-verified, GST-registered
  from 1 Mar 2026). Ben's postal address: outstanding.
- Lines: website build and launch (list the LIVE items); month-1 retainer at the chosen tier.
- Explicit line: *"Not yet active, no charge: automated SMS alerts, review-request automation,
  missed-call text-back, chatbot. These will be added, and the monthly fee reviewed, only when each
  is live and you have agreed."*
- Excluded and billed to Ben in his own name: domain renewal, SMS provider, ManyChat, ad spend,
  photography.
- Payment terms per the agreement: 7 days. Bank details: copy from `INVOICE-TEMPLATE.txt` **at send
  time only**; do not duplicate them into new files.
- Do **not** write "services commence upon receipt of payment" — the site is already live.

See `INVOICE-AURORA-0001-DRAFT-v2.txt` for the draft layout.

## 5. How to approach Ben (client-lifecycle rules)

1. Send the **status + information request first** (`MESSAGE-TO-BEN-DRAFT.md`, message 1), the
   invoice second. An apology and a price in the same message undercut each other.
2. Lead with the state of things: what is live, what is not, and that only live items are billed.
3. If there has been silence or delay, acknowledge it in two sentences, name the failure (the
   silence, not just the delay), say it is on you, say it is fixed. No explanations.
4. Name any figure mentioned earlier: *"I mentioned $700 and $350 a month before I understood what
   was involved."* Renegotiate forward only.
5. Offer a short phone walkthrough; trades clients prefer it.
6. Do not ask Ben to sign the Services Agreement as it stands (unreviewed, empty liability clause).
   Until a solicitor has reviewed it, confirm price and scope by plain written email. *(General
   guidance, not legal advice.)*

## 6. Value framing for the conversation

Roofing jobs are worth $3,000–8,000 (restoration) and $15,000+ (re-roof). At the Growth tier ($400/mo
= $4,800/yr), one restoration covers a year; the site needs to bring a few jobs he would not otherwise
have had. Step up only when leads are provable (form enquiries, phone-tap events, reviews).

## 7. Open items that block sending

1. Price decision (this document). 2. Ben's written agreement on file. 3. Street addresses for both
parties. 4. ASIC business-name status. 5. Proof the quote form delivers (one marked test enquiry,
coordinated with Ben). 6. Solicitor review of the Services Agreement (or a written-email substitute
agreed by Aaron).
