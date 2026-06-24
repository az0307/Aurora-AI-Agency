# Domain & DNS Cheat Sheet — Y.M.I Roofing

## DOMAIN REGISTRATION

**Recommended:** VentraIP (ventraip.com.au)
- Domain: `ymiroofing.com.au`
- Cost: ~$14/year
- Also grab: `ymiroofing.com` (if available, redirect to .com.au)

## CLOUDFLARE DNS RECORDS

After connecting domain to Cloudflare Pages:

### Required Records:
```
Type    Name    Target/Content                    TTL      Proxy
─────────────────────────────────────────────────────────────────
CNAME   @       ymi-roofing.pages.dev             Auto     Proxied ☁️
CNAME   www     ymi-roofing.pages.dev             Auto     Proxied ☁️
TXT     @       google-site-verification=...    Auto     DNS only
```

### Email Records (if using custom domain email):
```
Type    Name    Target/Content                    TTL      Proxy
─────────────────────────────────────────────────────────────────
MX      @       10 mx.zoho.com                    Auto     DNS only
MX      @       20 mx2.zoho.com                   Auto     DNS only
TXT     @       v=spf1 include:zoho.com ~all      Auto     DNS only
```

### Security Headers (Cloudflare → Rules → Transform Rules):
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

## SSL/TLS

Cloudflare Pages provides SSL automatically. In Cloudflare dashboard:
1. SSL/TLS → Overview → Set to "Full (strict)"
2. Always Use HTTPS: ON
3. Automatic HTTPS Rewrites: ON

## PAGE RULES (if on paid Cloudflare plan)

```
URL: ymiroofing.com.au/*
Settings:
  - Cache Level: Standard
  - Edge Cache TTL: 2 hours
  - Browser Cache TTL: 30 minutes
```

## TROUBLESHOOTING

| Symptom | Cause | Fix |
|---------|-------|-----|
| Domain shows 404 | DNS not propagated | Wait 24-48 hours, check nameservers |
| SSL error | Certificate not issued | Ensure proxy is ON (orange cloud) |
| www doesn't work | Missing CNAME | Add www CNAME pointing to pages.dev |
| Old site still shows | Browser cache | Hard refresh (Ctrl+Shift+R) |
