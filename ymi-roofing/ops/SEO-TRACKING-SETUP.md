# SEO & Tracking Setup Guide — Y.M.I Roofing

## GOOGLE SEARCH CONSOLE

1. Go to https://search.google.com/search-console
2. Click "Add property" → "Domain" → type: `ymiroofing.com.au`
3. Verify via DNS (Cloudflare):
   - Copy the TXT record provided by Google
   - Cloudflare dashboard → DNS → Add record:
     - Type: TXT
     - Name: @
     - Content: [paste Google verification string]
     - TTL: Auto
4. Submit sitemap: `https://ymiroofing.com.au/sitemap.xml`
5. Request indexing of the homepage

## GOOGLE ANALYTICS 4 (GA4)

1. Go to https://analytics.google.com
2. Create property: "Y.M.I Roofing"
3. Data stream: Web → `https://ymiroofing.com.au`
4. Copy the Measurement ID (G-XXXXXXXXXX)
5. In index.html, uncomment the GA block and paste your ID:
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-YOUR-ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-YOUR-ID');
</script>
```

## GOOGLE BUSINESS PROFILE

1. Go to https://business.google.com
2. Search for "Y.M.I Roofing" or create new
3. Verify via postcard (sent to Ben's business address)
4. Once verified:
   - Add services (all 6 from the website)
   - Upload photos of completed jobs
   - Set hours: Mon-Sun 7am-7pm
   - Add website link: `https://ymiroofing.com.au`
   - Enable messaging
5. Get review link: Share → Copy link → extract Place ID for review-machine.json

## META PIXEL (Optional — for future ad campaigns)

1. Go to https://business.facebook.com/events_manager
2. Create Pixel → name: "YMI Roofing Website"
3. Copy the Pixel ID
4. Add to index.html `<head>`:
```html
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', 'YOUR_PIXEL_ID');
fbq('track', 'PageView');
</script>
```

## CONVERSION EVENTS TO TRACK

| Event | Trigger | GA4 | Meta |
|-------|---------|-----|------|
| page_view | Every page load | auto | auto |
| generate_lead | Form submitted | manual | manual |
| click_to_call | Phone link clicked | manual | manual |
| scroll | 50%+ page scroll | auto | — |

## LOCAL SEO CHECKLIST

- [ ] Google Business Profile claimed and verified
- [ ] NAP (Name, Address, Phone) consistent across all platforms
- [ ] Schema.org LocalBusiness markup on website (✅ already done)
- [ ] Reviews actively requested (✅ review-machine.json)
- [ ] Local citations on directories (hipages, OneFlare, Service.com.au)
- [ ] Backlinks from local business associations
