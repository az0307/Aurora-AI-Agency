# ManyChat Setup Checklist — Y.M.I Roofing

## PRE-SETUP

- [ ] Ben has a Facebook Business Page for Y.M.I Roofing
- [ ] Ben has an Instagram Business Profile (connected to the Facebook Page)
- [ ] ManyChat Pro account created (manychat.com)
- [ ] Facebook Page connected to ManyChat
- [ ] Instagram Business Profile connected to ManyChat

## CUSTOM FIELDS (Create in ManyChat → Settings → Custom Fields)

| Field Name | Type | Purpose |
|------------|------|---------|
| suburb | Text | Customer's suburb |
| service_needed | Text | Selected service type |
| roof_age | Text | Age range of roof |
| lead_message | Text | Free text about the job |
| lead_sent_to_n8n | Boolean | Track if webhook fired |
| is_emergency | Boolean | Flag urgent repairs |
| quote_status | Text | New / Quoted / Booked / Completed |

## KEYWORD TRIGGERS (Automation → Keywords)

| Keyword Group | Triggers | Action |
|--------------|----------|--------|
| quote | quote, price, cost, how much, rates, pricing | → Flow: Get a Quote |
| repair | repair, leak, cracked, broken, slipped, emergency | → Flow: Repairs |
| newroof | new roof, reroof, full roof, install | → Flow: New Roof |
| inspect | inspect, inspection, pre-purchase, check | → Flow: Inspection |
| repoint | repoint, rebed, ridge, mortar, pointing | → Flow: Re-Bedding |
| greeting | hi, hello, hey, good morning, good afternoon | → Flow: Welcome |
| location | area, suburb, where, location, service area | → Flow: Service Areas |

## FLOWS TO BUILD

### Flow 1: Welcome (Default Reply)
- Trigger: Any unmatched message, OR greeting keywords
- Content: See manychat-spec.md
- Set as "Default Reply" in ManyChat settings

### Flow 2: Get a Quote
- Trigger: quote keyword group
- Content: See manychat-spec.md
- Final step: Custom Action → POST to n8n webhook

### Flow 3: Repairs / Emergency
- Trigger: repair keyword group
- Content: See manychat-spec.md
- Emergency branch: Show both phone numbers, urge immediate call

### Flow 4: New Roof
- Trigger: newroof keyword group
- Route into Flow 2 with service = "New Roof Tiling"

### Flow 5: Inspection
- Trigger: inspect keyword group
- Route into Flow 2 with service = "Roof Inspections"

### Flow 6: Re-Bedding
- Trigger: repoint keyword group
- Route into Flow 2 with service = "Re-Bedding & Re-Pointing"

### Flow 7: Service Areas
- Trigger: location keyword group
- Content: List of suburbs + "Not on the list? Just ask"

### Flow 8: Fallback
- Trigger: Any unmatched message (if not default)
- Content: Apologise + offer 4 clear options

## AWAY MESSAGE (Settings → Away Message)

```
Thanks for reaching out! 👋

We're currently offline, but Ben will get back to you first thing.

For urgent repairs, call directly:
📞 0422 093 241
📞 0423 858 503

Otherwise, leave your details and we'll call you back.
```

Schedule: Outside 7am-7pm, 7 days a week.

## N8N WEBHOOK INTEGRATION

In the "Get a Quote" flow, after collecting phone number:

1. Add "Action" → "Perform Actions"
2. Choose "HTTP Request" (or "Custom Action" if available)
3. Method: POST
4. URL: `https://YOUR-N8N-DOMAIN/webhook/ymi-roofing-lead`
5. Body (JSON):
```json
{
  "name": "{{first_name}} {{last_name}}",
  "phone": "{{phone}}",
  "suburb": "{{suburb}}",
  "service": "{{service_needed}}",
  "message": "{{lead_message}} [via ManyChat]",
  "source": "manychat"
}
```

## TESTING CHECKLIST

- [ ] Send "hi" → Welcome flow triggers
- [ ] Send "quote" → Get a Quote flow triggers
- [ ] Send "leaking roof" → Repairs flow triggers
- [ ] Complete quote flow → Check n8n execution log
- [ ] Verify SMS received by Ben
- [ ] Verify Google Sheet has new row
- [ ] Send message at 10pm → Away message triggers
- [ ] Test emergency path → Both phone numbers shown

## PRICING

ManyChat Pro: ~$15 USD/month (at Ben's subscriber volume)
- Pass through to client OR include in $350/month retainer
