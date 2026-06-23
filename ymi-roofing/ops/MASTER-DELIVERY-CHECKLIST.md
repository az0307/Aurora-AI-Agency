# Y.M.I ROOFING — MASTER DELIVERY CHECKLIST v2.0
# Aurora AI Agency · Client: Ben Breheny
# Updated: 22 June 2026
# Changes from v1: High Pressure Washing, Floating CTA, ACL Compliance, BPC Registration, Terms of Service, OG Image, Favicon

═══════════════════════════════════════════════════════════════════════════════
PHASE 0: PRE-LAUNCH (Before anything goes live)
═══════════════════════════════════════════════════════════════════════════════

□ Ben's details confirmed:
  □ Full legal name for contract
  □ Business address (for Google Business Profile verification postcard)
  □ ABN (if registered — ACN is 695 710 055)
  □ BPC registration number (roofing plumber class — verify at bpc.vic.gov.au)
  □ Public liability insurance certificate (minimum $10M recommended for roofing)
  □ Preferred payment method for invoices

□ Aurora's details confirmed:
  □ Legal / trading name for contract
  □ ABN
  □ Bank account details for invoice
  □ Business address
  □ Email and phone for contract

□ Pricing confirmed:
  □ Initial payment amount (setup + 2 months)
  □ Monthly retainer ($350/month)
  □ GST status (inclusive / not registered)
  □ Reporting frequency (monthly)

□ High Pressure Washing scope confirmed:
  □ Equipment owned or hired? (pressure washer, surface cleaner, extension poles)
  □ Chemicals/cleaning agents used? (must be eco-friendly, gutter-safe)
  □ Water source arrangements (client tap vs tanker)
  □ Waste water disposal compliance (EPA Victoria requirements)
  □ Height limitations (2-storey max? scaffolding needed?)
  □ Insurance covers pressure washing? (some policies exclude high-pressure work)

═══════════════════════════════════════════════════════════════════════════════
PHASE 1: WEBSITE GOES LIVE (15 min)
═══════════════════════════════════════════════════════════════════════════════

□ Cloudflare account created (dash.cloudflare.com)
□ Cloudflare Pages project created: "ymi-roofing"
□ Files uploaded:
  □ index.html (v2.0 — with high pressure washing, floating CTA, ACL compliance)
  □ privacy.html (v2.0 — with ACL notices, OAIC, opt-out, 7-year retention)
  □ terms.html (NEW — full ACL-compliant terms of service)
  □ robots.txt
  □ sitemap.xml
  □ favicon.png
  □ og-image.jpg
□ Site loads at ymi-roofing.pages.dev
□ All phone links work (tel:0422093241, tel:0423858503)
□ All email links work (mailto:y.m.iroofing@outlook.com)
□ Form validation works (name required, phone AU format)
□ Mobile responsive test passed
□ Page speed check (aim: <2s on mobile)
□ Floating CTA bar appears after scrolling 400px
□ Floating CTA bar can be dismissed with ✕ button
□ Footer links to Privacy Policy and Terms of Service

OPTIONAL — Custom domain:
□ Domain purchased: ymiroofing.com.au (VentraIP ~$14/year)
□ Custom domain connected in Cloudflare Pages
□ DNS propagated (check with whatsmydns.net)
□ SSL certificate auto-issued by Cloudflare
□ www redirect configured (www → apex)

═══════════════════════════════════════════════════════════════════════════════
PHASE 2: LEAD CAPTURE AUTOMATION (20 min)
═══════════════════════════════════════════════════════════════════════════════

□ n8n instance running (self-hosted or cloud)
□ Google Sheet created: "YMI Leads"
  □ Tab 1: "Leads" with correct headers (see GOOGLE-SHEETS-SETUP.md)
  □ Tab 2: "Jobs" with correct headers
  □ Tab 3: "Monthly Summary" with correct headers
  □ Shared with n8n service account (if using service auth)
□ Google Sheet ID copied
□ Twilio account created
  □ Account SID copied
  □ Auth Token copied
  □ Phone number purchased (format: +614XXXXXXXX)
□ Lead-capture workflow imported (lead-capture.json)
  □ REPLACE_SHEET_ID → actual Sheet ID
  □ REPLACE_TWILIO_NUMBER → actual Twilio number (×2 nodes)
  □ Twilio credentials connected in n8n
  □ Workflow toggled ACTIVE
□ Production webhook URL copied (ends in /webhook/ymi-roofing-lead)
□ index.html updated:
  □ Line ~883: WEBHOOK_URL replaced with actual n8n URL
□ Site redeployed with updated index.html
□ END-TO-END TEST:
  □ Submit test lead via website form (select "High Pressure Roof Cleaning")
  □ Ben's primary phone receives SMS within 30 seconds
  □ Ben's secondary phone receives SMS within 30 seconds
  □ Google Sheet shows new row with correct data
  □ Success message displays on website
  □ Honeypot test: fill hidden field → submission silently discarded

═══════════════════════════════════════════════════════════════════════════════
PHASE 3: REVIEW MACHINE (10 min)
═══════════════════════════════════════════════════════════════════════════════

□ Google Business Profile claimed for Y.M.I Roofing
□ Google Business Profile verified (postcard method)
□ Google review link obtained (Share → Copy link)
□ Place ID extracted from review link
□ Review-machine workflow imported (review-machine.json)
  □ REPLACE_SHEET_ID → actual Sheet ID
  □ REPLACE_TWILIO_NUMBER → actual Twilio number (×2 nodes)
  □ REPLACE_GOOGLE_PLACE_ID → actual Place ID
  □ SMS message includes opt-out: "Reply STOP to opt out"
  □ Workflow toggled ACTIVE
□ Production webhook URL copied (ends in /webhook/ymi-review-done)
□ Phone bookmark created for Ben:
  URL: https://YOUR-N8N-DOMAIN/webhook/ymi-review-done?name=NAME&phone=04XXXXXXXX&suburb=SUBURB
□ TEST:
  □ Hit review webhook URL with test data
  □ Confirm "Thanks Ben!" response
  □ Confirm row added to "Jobs" sheet
  □ (Shorten Wait node to test SMS immediately)
  □ Confirm review SMS received with correct Google link
  □ Confirm follow-up SMS received after 72h
  □ Confirm STOP opt-out works

═══════════════════════════════════════════════════════════════════════════════
PHASE 4: MANYCHAT CHATBOT (1-2 hours)
═══════════════════════════════════════════════════════════════════════════════

□ ManyChat Pro account created
□ Connected to Ben's Facebook Page
□ Connected to Ben's Instagram Business Profile
□ All 8 custom fields created (see MANYCHAT-SETUP-CHECKLIST.md)
□ All keyword triggers configured
□ All 8 flows built (Welcome, Get a Quote, Repairs, New Roof, Inspection, Re-Bedding, Service Areas, Fallback)
□ NEW: High Pressure Washing flow added (or integrated into Services flow)
□ n8n webhook Custom Action added to "Get a Quote" flow
□ Away message configured (7pm-7am)
□ Default reply set to Welcome flow
□ TEST EACH FLOW:
  □ Welcome → all 4 buttons route correctly
  □ Get a Quote → collects suburb, service, roof age, phone
  □ Get a Quote → webhook fires → n8n receives payload
  □ Get a Quote → Ben receives SMS
  □ Repairs → emergency vs non-urgent branches
  □ Service Areas → suburb list accurate
  □ Fallback → all 4 options work
  □ High Pressure Washing → quote path works

═══════════════════════════════════════════════════════════════════════════════
PHASE 5: PAPERWORK & BILLING
═══════════════════════════════════════════════════════════════════════════════

□ Services Agreement filled and reviewed:
  □ All [blanks] completed
  □ Monthly fee confirmed ($350)
  □ GST wording confirmed
  □ Notice period confirmed (14 days)
  □ ACL compliance clause added (consumer guarantees cannot be excluded)
  □ Cooling-off period clause added (10 business days for unsolicited agreements)
  □ Special terms added (if any)
  □ Both parties signed
□ Invoice AURORA-0001 generated and sent
  □ Setup fee + 2 months retainer
  □ Payment terms: 7 days
  □ Bank details included
□ Welcome letter sent to Ben
□ All files delivered to Ben:
  □ Website link
  □ Google Sheet link (view access)
  □ ManyChat dashboard access (if shared)
  □ Review bookmark URL
  □ Emergency contact card (Aurora's details)

═══════════════════════════════════════════════════════════════════════════════
PHASE 6: POST-LAUNCH (Ongoing)
═══════════════════════════════════════════════════════════════════════════════

□ Google Search Console property added
  □ Domain verification (DNS TXT record)
  □ Sitemap submitted
  □ Indexing requested
□ Google Analytics 4 property created (optional)
  □ Measurement ID obtained
  □ Added to index.html
  □ Site redeployed
□ Google Business Profile optimised:
  □ All 9 services listed (6 roofing + 3 cleaning)
  □ Hours set: Mon-Sun 7am-7pm
  □ Website link added
  □ Photos uploaded (before/after if available)
  □ First review requested from Ben's best customer
□ Meta Pixel created (optional — for future ads)
□ Local citations submitted:
  □ hipages.com.au
  □ OneFlare
  □ Service.com.au
  □ TrueLocal
  □ Google Business Profile
□ Monthly reporting schedule established
□ n8n workflow backup schedule (weekly JSON export)

═══════════════════════════════════════════════════════════════════════════════
AUSTRALIAN CONSUMER LAW COMPLIANCE CHECKLIST
═══════════════════════════════════════════════════════════════════════════════

□ Website displays mandatory warranty notice (ACL s 102):
  "Our services come with guarantees that cannot be excluded under the Australian Consumer Law. You are entitled to a replacement or refund for a major failure and for compensation for any other reasonably foreseeable loss or damage. You are also entitled to have the services re-performed if they fail to be of acceptable quality and the failure does not amount to a major failure."

□ Website acknowledges consumer guarantees:
  □ Due care and skill (s 60)
  □ Fit for purpose (s 61)
  □ Reasonable time (s 62)

□ No "no refund" policies or signs anywhere
□ No terms that purport to exclude consumer guarantees
□ Quotes are itemised, fixed-price, and valid for 30 days
□ Written quotes provided before work begins
□ 10-day cooling-off period honoured for unsolicited agreements
□ BPC registration number displayed (or linked to bpc.vic.gov.au)
□ Public liability insurance mentioned
□ Privacy Policy compliant with Privacy Act 1988
□ Terms of Service reference ACL and cannot override it
□ Form includes clear consent for data collection
□ Form includes opt-out mechanism for SMS
□ Complaints process documented (contact → CAV → VCAT)

═══════════════════════════════════════════════════════════════════════════════
HIGH PRESSURE WASHING COMPLIANCE CHECKLIST
═══════════════════════════════════════════════════════════════════════════════

□ EPA Victoria waste water requirements checked
  □ No chemicals entering stormwater drains
  □ Sediment traps used where required
  □ Waste water disposed of at approved facility (if not to sewer)
□ Insurance covers high-pressure work (some policies exclude)
□ Equipment safety checks:
  □ Pressure washer PAT tested annually
  □ Nozzle guards in place
  □ Extension poles rated for height
  □ Non-slip footwear mandatory
□ Chemical safety:
  □ SDS sheets available for all cleaning agents
  □ Eco-friendly products only (no bleach on roofs)
  □ Client plants/pets protected
□ Height safety:
  □ 2-storey limit without scaffolding
  □ Harness and anchor points for roof work
  □ Ladder safety (3-point contact, secured top and bottom)

═══════════════════════════════════════════════════════════════════════════════
KNOWN ISSUES / TECHNICAL DEBT
═══════════════════════════════════════════════════════════════════════════════

⚠️ WEBSITE:
  • No real photos — using emoji icons only. ACTION: Get 5-10 photos from Ben.
  • No before/after gallery. ACTION: Request photos from next 3 jobs.
  • No actual testimonials — using placeholder reviews. ACTION: Replace with real Google reviews once collected.
  • og:image exists but is auto-generated. ACTION: Replace with professional branded photo when available.
  • No ABN displayed (only ACN). ACTION: Check if Ben has ABN; add if yes.
  • Facebook/Instagram links in footer are placeholders. ACTION: Update with real URLs once pages created.

⚠️ N8N:
  • CORS allowedOrigins is wildcard '*'. ACTION: Restrict to actual domain after go-live.
  • No duplicate lead detection. ACTION: Add phone number lookup before SMS node.
  • No error fallback if Twilio fails. ACTION: Add email fallback node.
  • Review SMS has basic opt-out but no automated STOP handling. ACTION: Add Twilio inbound webhook for STOP processing.

⚠️ MANYCHAT:
  • No pricing information in chatbot. ACTION: Add rough price ranges per service.
  • High Pressure Washing flow not yet built. ACTION: Build from spec once chatbot is live.

⚠️ CONTRACT:
  • Monthly fee placeholder says $799 but launch guide says $350. RESOLVED: Use $350.
  • No specific deliverables listed in Schedule. ACTION: Fill "Included" and "Not included" sections.

⚠️ COMPLIANCE:
  • BPC registration number not yet verified. ACTION: Ben to provide registration number for display.
  • Insurance certificate not yet sighted. ACTION: Request copy from Ben.
  • No asbestos management plan. ACTION: If Ben encounters asbestos, must use licensed removalist.

═══════════════════════════════════════════════════════════════════════════════
COST SUMMARY (Monthly)
═══════════════════════════════════════════════════════════════════════════════

Client pays:        $350/month (retainer)
Aurora costs:
  Cloudflare Pages:   $0
  Domain:             ~$1.20/mo
  n8n self-host:      $0 (or ~$20/mo cloud)
  Twilio SMS:         ~$0.60/mo
  ManyChat Pro:       ~$22/mo (USD)
  ─────────────────────────
  Total costs:        ~$24-44/mo

Margin:             ~$306-326/mo

═══════════════════════════════════════════════════════════════════════════════
FILES DELIVERED (v2.0)
═══════════════════════════════════════════════════════════════════════════════

CLIENT-FACING:
  index.html              → Main website (v2.0: pressure washing, floating CTA, ACL compliance, testimonials)
  privacy.html            → Privacy policy (v2.0: ACL, OAIC, opt-out, 7-year retention)
  terms.html              → Terms of Service (NEW: full ACL compliance, BPC, cooling-off, remedies)
  robots.txt              → Search engine directives
  sitemap.xml             → Search engine sitemap
  favicon.png             → Site favicon (64x64)
  og-image.jpg            → Social sharing image (1200x630)

AGENCY INTERNAL:
  lead-capture.json       → n8n lead workflow
  review-machine.json     → n8n review workflow
  manychat-spec.md        → Chatbot build specification
  Aurora_Services_Agreement_SOURCE.md → Contract template

NEW — CREATED BY THIS AUDIT:
  GOOGLE-SHEETS-SETUP.md       → Sheet structure guide
  email-signature.html         → Ben's email signature
  WELCOME-LETTER.txt           → Client onboarding letter
  INVOICE-TEMPLATE.txt         → AURORA-0001 template
  n8n-BACKUP-SECURITY.md       → Backup & security guide
  SEO-TRACKING-SETUP.md        → GSC/GA4/Meta setup
  DOMAIN-DNS-CHEATSHEET.md     → DNS records reference
  MANYCHAT-SETUP-CHECKLIST.md  → Expanded chatbot checklist
  MASTER-DELIVERY-CHECKLIST.md → This file (v2.0)

═══════════════════════════════════════════════════════════════════════════════
SUGGESTIONS NOT YET CONSIDERED (Future Phase)
═══════════════════════════════════════════════════════════════════════════════

1. BEFORE/AFTER GALLERY PAGE
   → Dedicated page with slider comparisons. Huge conversion booster for tradies.
   → Requires: 6+ real photo pairs from Ben's jobs.

2. VIDEO TESTIMONIALS
   → 30-second phone videos from happy customers. More credible than text.
   → Requires: Ben to ask 3 customers after next jobs.

3. INSTANT QUOTE CALCULATOR
   → "How much will my roof cost?" interactive tool. Captures leads at top of funnel.
   → Requires: Ben's pricing data (per m² for tiling, per lineal metre for pointing, etc.)

4. EMERGENCY REPAIR HOTLINE
   → Separate 24/7 number with premium pricing for after-hours storm damage.
   → Requires: Ben willing to take emergency calls + higher rate structure.

5. SEASONAL MAINTENANCE PLANS
   → Annual roof check + clean subscription. Recurring revenue for Ben.
   → Requires: Pricing model ($X/year for 2 inspections + 1 clean)

6. ASBESTOS TESTING PARTNERSHIP
   → Partner with licensed asbestos removalist. Referral fee + full service.
   → Requires: Legal partnership agreement, disclosure to customers.

7. GUTTER GUARD INSTALLATION
   → Natural upsell after roof work. High margin, low labour.
   → Requires: Supplier relationship, stock holding.

8. SOLAR PANEL CLEANING
   → Add-on service for existing solar customers. Fast growing market.
   → Requires: Pure water fed pole system, training on solar-safe methods.

9. COMMERCIAL CLIENT SECTION
   → Real estate agents, property managers, body corporates. Bigger jobs.
   → Requires: Separate pricing sheet, contract terms, invoicing system.

10. REFERRAL PROGRAM
    → "Refer a neighbour, get $50 off your next clean." Viral growth mechanic.
    → Requires: Tracking system, voucher codes, terms.

11. GOOGLE ADS CAMPAIGN
    → "Roof repairs Melbourne" — high intent, immediate leads. $500-1000/mo spend.
    → Requires: Landing page, conversion tracking, ad copy, ongoing management.

12. LOCAL SEO CITATIONS
    → Submit to 20+ directories (Yellow Pages, TrueLocal, StartLocal, etc.)
    → Requires: Consistent NAP (Name, Address, Phone) across all listings.

13. CHATBOT INTEGRATION WITH FACEBOOK ADS
    → Click-to-Messenger ads → ManyChat → Lead capture. Lower CPC than website ads.
    → Requires: Meta Business Manager, ad creative, ManyChat flow.

14. SMS REMINDER SYSTEM
    → "Your roof is due for its annual inspection." Recurring revenue trigger.
    → Requires: Customer database with job dates, automated SMS workflow.

15. WARRANTY REGISTRATION PORTAL
    → Customers register their job online for warranty tracking. Reduces disputes.
    → Requires: Simple form, database, automated reminder emails.

═══════════════════════════════════════════════════════════════════════════════
