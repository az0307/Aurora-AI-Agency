# Aurora AI Agency — Services Agreement (Source Template)

> **DRAFT TEMPLATE — NOT YET REVIEWED BY A LAWYER.** This is a starting point assembled from the
> commercial terms already documented in `WELCOME-LETTER.txt`, `INVOICE-TEMPLATE.txt`, and
> `MASTER-DELIVERY-CHECKLIST.md`. Every `[bracketed placeholder]` is a genuine unknown — nothing
> has been invented or assumed. **Do not send this to Ben until:**
> 1. Every placeholder below is filled in or deliberately removed,
> 2. A qualified Australian solicitor has reviewed it (this is not legal advice), and
> 3. The Schedule of Services (Section 4) reflects what is *actually built and live*, not what's
>    planned — see the note at the top of that section.

---

## SERVICES AGREEMENT

This Agreement is made on **[Date]** between:

**(1) Service Provider**
Aaron Baker, trading as **Aurora AI Agency** (**"Aurora"**)
ABN: 15 870 917 390 (verified against the official ABR record — Individual/Sole Trader, active
from 1 Oct 2025, main business location VIC 3338)
ACN: N/A — Aurora operates as a sole trader, not a registered company
Registered address: Melton South, VIC 3338 — [full street address still outstanding]
Contact: Aaron Baker — aaron221048@gmail.com — 0401 154 219

> ⚠️ **New item from this ABR check:** the ABR record lists "Aaron Baker" as the registered
> trading name (since 2009) — **"Aurora AI Agency" does not currently appear as a registered
> business name** on the ASIC Business Names Register under this ABN. Trading under a name other
> than your own personal name generally needs to be registered with ASIC. Confirm whether "Aurora
> AI Agency" is registered elsewhere/pending, or register it, before this Agreement issues under
> that trading name — see Section 10.

**(2) Client**
Y.M.I Roofing Pty Ltd (**"Client"**)
ACN: 695 710 055
ABN: 14 695 710 055
Registered address: [Ben's business/registered address]
Contact: Ben Breheny (Director) — 0422 093 241 — y.m.iroofing@outlook.com

Together "the Parties."

---

### 1. Background

1.1 The Client operates a roof tiling and high-pressure cleaning business servicing Melton and
Melbourne's western suburbs.

1.2 Aurora provides website development, automation, and digital marketing infrastructure
services.

1.3 The Client wishes to engage Aurora to design, build, and operate the digital systems
described in Schedule A (the "Services"), and Aurora agrees to provide them on the terms of this
Agreement.

---

### 2. Term and Commencement

2.1 This Agreement commences on **[Start Date]** ("Commencement Date") and continues on a
month-to-month basis until terminated in accordance with Section 9.

2.2 The initial setup phase (Schedule A, Part 1) is expected to take **[X business days]** from
Commencement Date, subject to the Client providing the information and materials requested in
Section 6 (Client Responsibilities) in a timely manner.

---

### 3. Fees and Payment

3.1 **Setup fee:** $700.00 (one-off), payable on signing this Agreement.

3.2 **Monthly retainer:** $350.00 per month, payable in advance, covering the services listed in
Schedule A, Part 2.

3.3 **GST:** Confirmed via the ABR record — Aurora (Aaron Baker, ABN 15 870 917 390) is **not
currently registered for GST**. Aurora cannot charge GST on the fees in this Agreement. This
makes the supply **"not subject to GST"** — not "GST-free" (GST-free is a distinct legal category
for specific goods/services and doesn't apply here just because the supplier is unregistered).
The $700.00 and $350.00 figures in Sections 3.1–3.2 are the total amounts payable, with no GST
added. `INVOICE-TEMPLATE.txt` has been corrected to match. If Aurora later registers for GST,
this clause and the invoice template both need updating.

3.4 **Invoicing:** Invoices are issued monthly in advance / [confirm cycle] and are due within
**7 days** of the invoice date.

3.5 **Late payment:** [Confirm — does Aurora want a late fee / interest clause, or suspension of
services after a grace period? Not yet decided in the source documents.]

3.6 **Costs not included** (Client's direct responsibility, per `WELCOME-LETTER.txt`):
- Domain renewal (~$14/year) — domain registration account remains under [confirm — Client's or
  Aurora's registrar account?]; see Section 5.1 for control/transfer mechanics.
- SMS provider costs (~$0.60/month via Twilio), if/when SMS features are active
- ManyChat Pro subscription (~$22 USD/month), if/when the chatbot is active
- Email delivery costs via Resend, if usage exceeds the free tier — [confirm threshold and who
  pays overage]
- Google Sheets is hosted under [confirm — Aurora's or Client's Google account?]; this determines
  who owns the underlying data and who can access it directly, separate from the CSV export
  Aurora provides on termination (Section 9.3)
- Any advertising spend (Google Ads, Meta Ads)
- Photography or custom design work beyond what's scoped in Schedule A

---

### 4. Services (Schedule A)

> ⚠️ **Before this Agreement is finalised:** the list below must be checked against what is
> *actually deployed* on `ymiroofing.com.au` today, not what was originally planned. As of this
> draft, the live site delivers website hosting and email-based lead capture (via Resend) —
> SMS alerts, the Google Sheets CRM pipeline, the Review Machine, and the ManyChat chatbot
> described in `WELCOME-LETTER.txt` have specs and workflow files prepared but their live/active
> status has not been confirmed in this review. **Mark each line "Live," "In progress," or
> "Not started"** so the contract doesn't promise something not yet delivered.

**Part 1 — Setup (one-off)**

| Item | Status |
|---|---|
| Website design and build (`ymiroofing.com.au`) | [Live / In progress] |
| Mobile-optimised, SEO-ready structure with structured data | [Live / In progress] |
| Lead capture form on website | [Live / In progress] |
| [ ] Automated SMS lead alerts | [Live / In progress / Not started] |
| [ ] Lead logging to shared Google Sheet | [Live / In progress / Not started] |
| [ ] Review Machine (post-job review request automation) | [Live / In progress / Not started] |
| [ ] Facebook/Instagram chatbot (ManyChat) | [Live / In progress / Not started] |

**Part 2 — Ongoing monthly services**

| Item | Included |
|---|---|
| Website hosting and maintenance | ✅ |
| Automation platform hosting (n8n or equivalent), if applicable | [Confirm] |
| Monthly performance report | ✅ |
| Minor website updates (text, phone numbers, small content edits) | ✅ |
| Chatbot monitoring and tweaks, if chatbot is live | [Confirm] |

**Part 3 — Explicitly not included** (per `WELCOME-LETTER.txt`)
- Domain renewal
- Third-party subscription costs (Twilio, ManyChat Pro)
- Advertising spend
- Photography or custom design work

---

### 5. Intellectual Property

5.1 On full payment of the setup fee, the Client owns the website content, branding, and domain
registration (`ymiroofing.com.au`). Ownership includes control, not just legal registrant status:
[confirm — is the domain registered directly in the Client's own registrar account, or in
Aurora's, on the Client's behalf? If the latter, Aurora will transfer the registrar account (or
provide full DNS/registrar credentials) to the Client on request or on termination, whichever is
earlier.]

5.2 Aurora retains ownership of its own tools, frameworks, automation templates, and any
reusable code, workflows, or systems not built specifically and exclusively for the Client.

5.3 [Confirm — does Aurora want a licence-back clause allowing reuse of the general website
template/automation patterns for future clients? Not yet decided.]

---

### 6. Client Responsibilities

The Client agrees to provide, in a timely manner:
- Photos of completed jobs for the website gallery and Google Business Profile.
- Access to (or creation of) a Google Business Profile.
- A preferred phone number for SMS-based features, if applicable.
- Confirmation of business registration details (ABN confirmed: 14 695 710 055; BPC registration
  number: **[outstanding — see Section 10]**).
- Timely responses to leads generated through the website/automation (the value of the system
  depends on fast follow-up).

---

### 7. Confidentiality and Data

7.1 Each party will keep confidential any non-public business, financial, or customer
information disclosed by the other party, except as required by law.

7.2 Customer data collected via the website (names, phone numbers, enquiry details) is handled
per the Client's published Privacy Policy at `ymiroofing.com.au/privacy.html`.

> ⚠️ **Correction from the original draft:** that policy states the Client complies with the
> *Privacy Act 1988* (Cth) and the Australian Privacy Principles (APPs) — this Agreement should
> not simply repeat that as an established fact. Most small businesses (annual turnover ≤ $3
> million) are **exempt** from the Privacy Act unless a specific exception applies (e.g. trading
> in personal information, being a health service provider, holding a Commonwealth contract, or
> voluntarily opting in). Whether the Client is actually bound by the Privacy Act/APPs, exempt,
> or has voluntarily opted in has not been established here and needs solicitor/OAIC-guidance
> confirmation — see Section 10.

7.3 Aurora acts as a processor of Client customer data on the Client's behalf across several
third-party tools (Google Sheets, Twilio, Resend, and n8n if/when active). [A proper data
processing schedule is needed, covering: Aurora's processing role and permitted uses; which
third parties are authorised sub-processors; security controls Aurora applies to data in these
tools; how a data breach affecting Client data would be notified and to whom; how long Aurora
retains Client data after collection or after termination; and what disclosures (if any) Aurora
may make to third parties. Not yet drafted — needs solicitor input, not a template.]

---

### 8. Australian Consumer Law — Consumer Guarantees

8.1 Nothing in this Agreement excludes, restricts, or modifies any consumer guarantee, right, or
remedy conferred on the Client under the *Australian Consumer Law* (Schedule 2 to the
*Competition and Consumer Act 2010* (Cth)) that cannot lawfully be excluded.

8.2 Where the Australian Consumer Law applies to the Services supplied under this Agreement,
Aurora uses the ACCC's prescribed services-guarantee wording (current as at this draft — confirm
against accc.gov.au before signing, as ACCC guidance can be updated):

> "Our services come with guarantees that cannot be excluded under the Australian Consumer Law.
> For major failures with the service, you are entitled:
> — to cancel your service contract with us; and
> — to a refund for the unused portion, or to compensation for its reduced value.
>
> You are also entitled to be compensated for any other reasonably foreseeable loss or damage.
>
> If the failure does not amount to a major failure, you are entitled to have problems with the
> service rectified in a reasonable time and, if this is not done, to cancel your contract and
> obtain a refund for the unused portion of the contract."

---

### 9. Termination

9.1 Either party may terminate this Agreement for convenience by giving **14 days' written
notice** to the other party.

9.2 Either party may terminate immediately on written notice if the other party materially
breaches this Agreement and fails to remedy the breach within **[X days]** of being notified.

9.3 On termination, the Client retains ownership of the website and domain per Section 5. Within
**[X days]** of termination, Aurora will provide the Client with:
- A full export of website source files;
- Registrar/DNS account access or transfer for `ymiroofing.com.au`, per Section 5.1;
- A full export of Google Sheets data (format: [confirm — Google Sheets native / CSV / other]);
- A full export of any automation workflows built specifically for the Client (e.g. n8n workflow
  JSON), if applicable;
- Any vendor/hosting credentials that are the Client's to keep (as distinct from Aurora's own
  accounts, e.g. Aurora's Resend account, which is not handed over);
- Confirmation of what Client data Aurora deletes from its own systems after handover, and on
  what timeline.

9.4 Subject to Section 8 (Australian Consumer Law), fees paid for the then-current month are
non-refundable except where a consumer guarantee entitles the Client to a refund for the unused
portion per Section 8.2; no further monthly fees are payable after the effective termination
date. [Confirm — if termination happens mid-month, is any part of that month's fee prorated back
to the Client, or is the "non-refundable" rule absolute outside the ACL carve-out above? Not yet
decided.]

---

### 10. Outstanding Items Before Signing

The following must be resolved before this Agreement is finalised — none of these have been
fabricated or assumed, and none should be guessed at. This list is intended to be exhaustive:
nothing in brackets elsewhere in this document should be filled in without also being checked
off (or explicitly removed) here.

**Parties & dates**
- [x] Aurora's ABN (15 870 917 390), sole-trader status, and GST status — verified against the
      ABR record on 2026-08-10
- [ ] **New:** "Aurora AI Agency" is not a registered ASIC business name under this ABN — confirm
      registration status before issuing this Agreement under that trading name
- [ ] Aurora's full registered/business street address (suburb confirmed: Melton South, VIC 3338)
- [ ] Ben's registered business address (for the Client block above and GBP verification)
- [ ] Agreement date (top of §"SERVICES AGREEMENT") and Commencement Date (§2.1)
- [ ] Expected setup-phase duration in business days (§2.2)

**Fees & billing**
- [x] Aurora's GST registration status confirmed: not registered — supply is not subject to GST,
      no GST-inclusive/exclusive question applies (§3.3)
- [ ] Invoicing cycle confirmation (§3.4)
- [ ] Late payment terms — fee, interest, or service suspension (§3.5)
- [ ] Domain registrar account ownership, and who pays Resend overage if the free tier is exceeded (§3.6)
- [ ] Google Sheets account ownership (§3.6)
- [ ] Whether monthly fees are prorated on mid-month termination (§9.4)

**Scope**
- [ ] Which Schedule A items are actually live vs. planned — do not send until every row in the
      Part 1/Part 2 tables is marked (§4)
- [ ] Automation platform hosting — confirm whether this is actually included (§4, Part 2)

**Compliance**
- [ ] BPC (Building and Plumbing Commission) registration number for Y.M.I Roofing — flagged as
      outstanding since `CREDIBILITY-AUDIT.md` and `MASTER-DELIVERY-CHECKLIST.md`
- [ ] Public liability insurance certificate sighted and cover amount confirmed
- [ ] Whether the Client is actually bound by, exempt from, or has opted into the Privacy Act
      1988/APPs — do not assume compliance (§7.2)
- [ ] ACL services-guarantee wording in §8.2 re-checked against current ACCC guidance immediately
      before signing

**Legal terms needing solicitor drafting, not templating**
- [ ] IP licence-back terms, if wanted (§5.3)
- [ ] Domain/registrar transfer mechanics finalised (§5.1)
- [ ] Full data processing schedule for third-party tools (§7.3)
- [ ] Breach-remedy period (§9.2, currently **[X days]**)
- [ ] Termination handover deadline (§9.3, currently **[X days]**)
- [ ] Limitation of liability clause — entirely undrafted (§11)
- [ ] Dispute-resolution timeframe (§12.2, currently **[X days]**) and the actual enforceable
      forum(s) for unresolved disputes — do not rely on VCAT by default (§12.2)

**Execution**
- [ ] Aurora's signatory name and title (Signatures block)
- [ ] Signing dates for both parties (Signatures block)

---

### 11. Limitation of Liability

11.1 [Not yet drafted. This clause needs a solicitor's input — a blanket liability cap or
exclusion here could conflict with Section 8 (Australian Consumer Law) if drafted too broadly,
and an under-drafted clause leaves Aurora exposed. Do not draft this from a template without
review.]

---

### 12. Dispute Resolution

12.1 If a dispute arises, the parties will first attempt to resolve it through direct discussion
between Ben Breheny and Aaron Baker.

12.2 If unresolved within **[X days]**, either party **may** (this is a voluntary, non-binding
option, not a mandatory step) refer the matter to Consumer Affairs Victoria conciliation.

> ⚠️ **Flag for solicitor review:** the original draft named VCAT as the enforceable next step,
> but VCAT is not a Chapter III court and generally cannot hear matters that require applying
> federal law (e.g. a claim genuinely arising under the Commonwealth *Competition and Consumer
> Act 2010*, as opposed to the Australian Consumer Law as picked up by the Victorian *Australian
> Consumer Law and Fair Trading Act 2012*). Whether a given dispute under this Agreement would
> fall within VCAT's jurisdiction or need to go to a court (e.g. the Magistrates' Court of
> Victoria) depends on how the claim is framed. **A solicitor should specify the actual
> enforceable forum(s)** rather than this Agreement asserting VCAT applies to every dispute.

---

### 13. General

13.1 **Governing law:** This Agreement is governed by the laws of Victoria, Australia.

13.2 **Entire agreement:** This Agreement, together with Schedule A, constitutes the entire
agreement between the parties and supersedes all prior discussions. Note: `WELCOME-LETTER.txt`
and `INVOICE-TEMPLATE.txt` contain commercial terms (fees, inclusions, exclusions) that this
Agreement is meant to formalise — before signing, confirm every operative term from those
documents is either restated here (Sections 3–4) or that both parties agree those documents are
superseded by this Agreement rather than still relied upon.

13.3 **Variation:** Any changes to this Agreement must be agreed in writing by both parties.

13.4 **Notices:** Written notices under this Agreement (including under Section 9, termination
and breach notices) must be sent to the contact details listed at the top of this document, by
one of: email (deemed received when sent, provided no bounce/delivery-failure notice is
received), or prepaid post (deemed received 3 business days after posting to the address on
record). Either party may update its own notice contact details by written notice to the other
party under this clause.

---

### Signatures

**For Aurora AI Agency:**

Signature: _______________________
Name: [Aurora signatory name]
Position: [Title]
Date: [Date]

**For Y.M.I Roofing Pty Ltd:**

Signature: _______________________
Name: Ben Breheny
Position: Director
Date: [Date]

---

*This document is a working template assembled from Aurora's existing client-onboarding
materials. It is not a substitute for legal advice. Have it reviewed by a solicitor qualified in
Victoria, Australia before either party signs.*
