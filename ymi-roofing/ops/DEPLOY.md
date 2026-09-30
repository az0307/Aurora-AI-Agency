# YMI Roofing — Deployment & Backend Guide
**Aurora AI Agency — Internal Reference**  
Client: Ben Breheny, Y.M.I Roofing · ACN 695 710 055

---

## 1. File Structure

```
Aurora-AI-Agency/
└── ymi-roofing/
    └── index.html          ← production-ready file (deploy this)
```

That's it. One file. No build step, no dependencies.

---

## 2. Domain

**Recommended registrar:** VentraIP or Hostmate (~$14 AUD/year)  
**Target domain:** `ymiroofing.com.au`  
**Backup option:** `ymiroofing.com.au` → `ymirotofing.com.au`

> Don't overthink the domain. Get ymiroofing.com.au first.

---

## 3. Cloudflare Pages — Free Hosting

### 3A. Push to GitHub
1. Create private repo: `ymi-roofing-frontend`
2. Upload `index.html` directly via GitHub web UI
3. That's the entire repo — one file

### 3B. Connect to Cloudflare Pages
1. Cloudflare Dashboard → Workers & Pages → Pages → Connect to Git
2. Select `ymi-roofing-frontend` repo
3. **Build settings:** Leave blank (static HTML, no build command needed)
4. Deploy → you get a live URL: `ymi-roofing-frontend.pages.dev`

### 3C. Add Custom Domain
1. Cloudflare → Pages → ymi-roofing-frontend → Custom Domains
2. Enter `ymiroofing.com.au`
3. Cloudflare gives you two nameservers (e.g. `kevin.ns.cloudflare.com`)
4. Log into VentraIP → replace default nameservers with Cloudflare's
5. SSL is automatic — done

**Total hosting cost: $0/mo**  
**Domain cost: ~$1.20/mo ($14/year)**

---

## 4. n8n Webhook — Backend Setup

### 4A. Your n8n Instance
Use your existing self-hosted n8n. No new setup needed.

Update `index.html` line 1 of the AGENCY CONFIG section:
```js
const WEBHOOK_URL = 'https://YOUR-N8N-DOMAIN/webhook/ymi-roofing-lead';
```

### 4B. Workflow: 4 Nodes

```
[Webhook] → [Code: Sanitize] → [Google Sheets: Log] → [Twilio: SMS to Ben]
```

---

#### Node 1 — Webhook
| Setting | Value |
|---|---|
| HTTP Method | POST |
| Path | `ymi-roofing-lead` |
| Authentication | None |
| CORS → Allowed Origins | `*` (or `https://ymiroofing.com.au` once live) |
| Respond | Immediately (200 OK) |

---

#### Node 2 — Code (Data Sanitize + Honeypot Gate)
```javascript
// Gate: drop execution if honeypot was filled (extra server-side check)
const hp = $json.body?.website_hp ?? '';
if (hp !== '') {
  return []; // stops the workflow silently
}

const name    = ($json.body?.name ?? '').trim();
const phone   = ($json.body?.phone ?? '').trim();  // already +614... from frontend
const suburb  = ($json.body?.suburb ?? 'Not provided').trim();
const service = $json.body?.service ?? 'Not specified';
const message = ($json.body?.message ?? 'None provided').trim();
const timestamp = new Date().toLocaleString('en-AU', { timeZone: 'Australia/Melbourne' });

// Extra phone sanitization (belt + braces)
const cleanPhone = phone.replace(/[^\d+]/g, '');

return [{
  json: {
    name, phone: cleanPhone, suburb, service, message, timestamp,
    raw_payload: $json.body
  }
}];
```

---

#### Node 3 — Google Sheets (Lead Log)
**Sheet:** `YMI Roofing — Leads` (create in your agency Google Drive)

| Column | n8n Expression |
|---|---|
| Timestamp | `{{ $json.timestamp }}` |
| Name | `{{ $json.name }}` |
| Phone | `{{ $json.phone }}` |
| Suburb | `{{ $json.suburb }}` |
| Service | `{{ $json.service }}` |
| Message | `{{ $json.message }}` |
| Source | `ymi-roofing-website` |

> **Why log first?** If Twilio fails or Ben deletes the SMS, this is the backup. It's also your monthly proof-of-value report.

---

#### Node 4 — Twilio SMS to Ben
| Setting | Value |
|---|---|
| To | `+61422093241` (Ben's primary) |
| From | Your Twilio virtual number |
| Body | (see below) |

**SMS body:**
```
🚨 NEW LEAD — Y.M.I ROOFING 🚨
👤 {{ $json.name }}
📞 {{ $json.phone }}
📍 {{ $json.suburb }}
🛠️ {{ $json.service }}
📝 {{ $json.message }}

⏱️ 1hr response clock is ticking!
Tap number above to call back.
```

**Optional second SMS to Ben's secondary (0423 858 503):**  
Duplicate the Twilio node, change the To number. Wire both from Node 3.

---

## 5. Email Notification (Optional)

If Ben wants email alerts to `y.m.iroofing@outlook.com`:

- **From:** `leads@ymiroofing.com.au` (your domain — NOT the customer's email)
- **Reply-To:** customer's email if they provided one
- **Subject:** `New Roofing Quote Request — {{ $json.name }}, {{ $json.suburb }}`
- **Body:** same data as SMS but formatted for email

> ⚠️ Never set From = customer's email. Outlook/Gmail will spam-filter or block it (SPF/DKIM rules). Always send FROM your own domain.

---

## 6. Pre-Launch Checklist

- [ ] `index.html` WEBHOOK_URL updated to live n8n endpoint
- [ ] GA4 script uncommented and Measurement ID replaced (if Ben wants analytics)
- [ ] Test form submitted — SMS received by Ben in <10 seconds
- [ ] Test form submitted — Google Sheet row created
- [ ] Browser network tab shows `200 OK` on form submit
- [ ] Success state displays correctly with submitter's first name
- [ ] Honeypot test: manually set `website_hp` value in DevTools → confirm n8n drops it
- [ ] CORS confirmed: no browser console errors on form submit
- [ ] Click-to-call works on mobile (test on iPhone and Android)
- [ ] Custom domain live and SSL padlock showing
- [ ] GBP (Google Business Profile) website field updated to `ymiroofing.com.au`
- [ ] Facebook page URL updated

---

## 7. Monthly Cost Summary

| Item | Cost |
|---|---|
| Cloudflare Pages hosting | $0/mo |
| Domain (ymiroofing.com.au) | ~$1.20/mo |
| n8n (self-hosted, existing) | $0/mo |
| Twilio SMS (~20 leads/mo) | ~$0.40/mo |
| **Total** | **~$1.60/mo** |

**Aurora retainer margin on Ignite ($350/mo): ~$348.40/mo net**

---

## 8. Next Steps After Go-Live

| Week | Action |
|---|---|
| Week 1 | Site live, GBP verified, n8n wired |
| Week 2 | Review machine live (job-done → SMS → Google review link) |
| Week 3 | ManyChat chatbot on Ben's Facebook/Instagram |
| Month 2 | Social content engine + quote estimator tool |

---

*Aurora AI Agency — internal doc. Not for client distribution.*
