# YMI Roofing — ManyChat Chatbot Specification
**Aurora AI Agency · Client: Ben Breheny, Y.M.I Roofing**

---

## Platform
ManyChat Pro connected to Ben's Facebook Page + Instagram Business Profile.

---

## Keyword Triggers

| Keyword Group | Triggers (any match) | Routes To |
|---|---|---|
| Quote/Price | quote, price, cost, how much, rates, pricing | → Flow: Get a Quote |
| Repairs | repair, leak, cracked, broken, slipped, emergency | → Flow: Repairs |
| New Roof | new roof, reroof, full roof, install | → Flow: New Roof |
| Inspection | inspect, inspection, pre-purchase, check | → Flow: Inspection |
| Repoint | repoint, rebed, ridge, mortar, pointing | → Flow: Re-Bedding |
| General Greeting | hi, hello, hey, good morning, good afternoon | → Flow: Welcome |
| Location | area, suburb, where, location, service area | → Flow: Service Areas |

---

## Flow 1: Welcome (Default / Greeting)

**Trigger:** DM received with no keyword match, OR greeting keyword

```
Bot: Hi there! 👋 Thanks for reaching out to Y.M.I Roofing.

I'm here to help you get the right information fast.
What can I help you with today?

[🏠 Get a Quote]   [🔧 Emergency Repair]
[🔍 Roof Inspection]   [💬 Something Else]
```

**Button routes:**
- Get a Quote → Flow: Get a Quote
- Emergency Repair → Flow: Repairs
- Roof Inspection → Flow: Inspection
- Something Else → Flow: Fallback

---

## Flow 2: Get a Quote (Lead Qualification)

```
Bot: Great! Getting you a free quote is easy.

First, what type of work do you need?

[New Roof Tiling]
[Re-Bedding & Re-Pointing]
[Roof Repairs]
[Tile Replacement]
[Ridge Capping]
[Not sure — need advice]
```

**After service selection:**
```
Bot: Perfect. What's your suburb? 
(This helps Ben confirm he services your area)

[User types suburb]
```

**After suburb:**
```
Bot: And roughly how old is your roof, if you know?

[Under 10 years]
[10–25 years]
[25+ years]
[Not sure]
```

**Lead capture:**
```
Bot: Almost done! To get Ben to call you with a free quote,
what's the best phone number to reach you?

[User types phone number]
```

**Confirmation:**
```
Bot: ✅ Done! Here's what we've got:

📍 Suburb: [suburb]
🛠️ Service: [service]
📞 Contact: [phone]

Ben will call you within 1 hour during business hours.
After hours? Expect a call first thing in the morning.

Is there anything else you'd like to add about your roof?
(Type it out, or tap Skip)

[Skip]
```

**After message/skip — SEND LEAD to n8n:**
```
Bot: You're all set! Ben has been notified. 🙏

In the meantime, you can also reach him directly:
📞 0422 093 241
📧 y.m.iroofing@outlook.com

Talk soon!
```

**n8n webhook call (ManyChat Custom Action):**
```
POST https://YOUR-N8N-DOMAIN/webhook/ymi-roofing-lead
Body: {
  name:    "{{first_name}} {{last_name}}",
  phone:   "{{phone}}",
  suburb:  "{{suburb_custom_field}}",
  service: "{{service_custom_field}}",
  message: "{{message_custom_field}} [via Instagram/Facebook DM]",
  source:  "manychat"
}
```

---

## Flow 3: Repairs / Emergency

```
Bot: Oh no — leaks and damaged tiles need attention fast. 🛠️

Is this an emergency (active leak, storm damage)?

[🚨 Yes — emergency]   [⏰ No — can wait a few days]
```

**Emergency branch:**
```
Bot: For urgent repairs, call Ben directly — he'll do his best
to get out to you ASAP.

📞 0422 093 241
📞 0423 858 503

Tell him you saw this message and it's urgent. 👍
```

**Non-urgent branch:**
→ Routes into Flow 2 (Get a Quote) from service = "Roof Repairs"

---

## Flow 4: FAQ — Service Areas

```
Bot: Ben services Melbourne and surrounding suburbs.

Key areas include:
• Eastern Suburbs (Croydon, Ringwood, Doncaster, Box Hill)
• North-East (Eltham, Diamond Creek, Greensborough)
• South-East (Dandenong, Berwick, Narre Warren)
• Inner East (Balwyn, Kew, Hawthorn)

Not on the list? Just ask — Ben may still cover your area!

[✅ Get a Quote]   [❓ Ask About My Area]
```

---

## Flow 5: Fallback (No Intent Match)

```
Bot: I'm not sure I caught that — sorry! 😅

Here's what I can help with:

[📋 Get a Free Quote]
[🔧 Book a Repair]
[📞 Call Ben Directly]
[🌐 Visit Our Website]
```

**"Call Ben Directly" button:** `tel:0422093241`
**"Visit Our Website" button:** `https://ymiroofing.com.au`

---

## Custom Fields to Create in ManyChat

| Field Name | Type | Set In |
|---|---|---|
| `suburb` | Text | Flow 2 (user input) |
| `service_needed` | Text | Flow 2 (button selection) |
| `roof_age` | Text | Flow 2 (button selection) |
| `lead_message` | Text | Flow 2 (free text) |
| `lead_sent_to_n8n` | Boolean | Flow 2 (after webhook) |
| `is_emergency` | Boolean | Flow 3 (emergency branch) |

---

## Agency Setup Checklist

- [ ] Connect ManyChat to Ben's Facebook Page
- [ ] Connect ManyChat to Ben's Instagram Business Profile
- [ ] Set default reply to Flow 1 (Welcome)
- [ ] Configure all keyword triggers
- [ ] Set up Custom Action for n8n webhook in ManyChat
- [ ] Add all custom fields
- [ ] Test each flow end-to-end
- [ ] Verify n8n receives the lead payload
- [ ] Confirm Ben receives SMS for each test lead
- [ ] Set "Away" message for overnight (directs to phone)

---

## ManyChat Pricing Note
ManyChat Pro: ~USD $15/mo at Ben's subscriber volume.
Charge client as pass-through or include in Ignite retainer.

