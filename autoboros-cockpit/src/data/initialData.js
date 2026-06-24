export const LADDER = {
  0:{name:'You only',     color:'#6b7280', mean:'You handle this yourself. The agent stays out — it\'s money or it\'s sensitive.'},
  1:{name:'You + agent',  color:'#fb923c', mean:'You lead. The agent has already prepped the context so you move faster.'},
  2:{name:'Draft → you',  color:'#eab308', mean:'The agent drafted it. Nothing leaves until you approve.'},
  3:{name:'Agent acts',   color:'#38bdf8', mean:'The agent is doing this and keeping you posted. Veto anytime.'},
  4:{name:'Autonomous',   color:'#22c55e', mean:'Fully handled by the agent. Logged here so you can see it.'},
};

export const STATUS_ORDER = ['Inbox','Next','In progress','Waiting on you','Waiting external','Done'];
export const CLIENT_ORDER = ['Evermystic','Aurora','Internal'];

export const INITIAL_JOBS = [
  {id:1, t:'Reply to Stefan — bulk hoodie quote (50×)', client:'Evermystic', status:'Waiting on you', lvl:2, actor:'You', src:'Email',
   skill:'quote-responder', steps:['Pull product + size + qty from the thread','Apply the A3 bulk tier from the price guide','Draft the quote in Stefan\'s tone','Hold for your approval before sending'],
   ask:'Approve the quote, or edit the number, then send.',
   last:{ag:'Drafted: 50× A3 @ $9.50 = $475 + GST, 3–5 day turnaround',ts:'2m ago'},
   draft:`Hey Stefan! 👋 Thanks for the bulk enquiry.\n\nFor 50× A3 full-front prints on your hoodies, you're looking at $9.50 per transfer = $475 + GST. That includes the bulk tier discount (kicks in at 10+).\n\nTurnaround is 3–5 business days once artwork's approved. Want me to lock it in?`},

  {id:2, t:'New HOT_LEAD "Priya" — first reply due within 2h', client:'Evermystic', status:'Waiting on you', lvl:2, actor:'You', src:'ManyChat · Activepieces',
   skill:'lead-first-touch', steps:['Capture lead + intent from the IG DM','Tag HOT_LEAD in Notion','Draft a warm opener referencing her enquiry','Hold for you — first reply sets the tone'],
   ask:'Send the opener, or tweak it first. Clock\'s ticking on the 2-hour SLA.',
   last:{ag:'Captured from IG DM ("need 30 tees for an event"), drafted opener',ts:'8m ago'},
   draft:`Hey Priya! 👋 Thanks for reaching out about the 30 event tees — love it.\n\nQuick one so I can quote you properly: what print size are you after (front only, or front + back), and do you have the artwork ready to go?\n\nWe do no-minimum DTF so 30 is no problem at all 🎨`},

  {id:3, t:'Escalated: ManyChat capture webhook timing out', client:'Evermystic', status:'In progress', lvl:1, actor:'You', src:'Agent-generated', esc:true,
   skill:'connection-watchdog', steps:['Detected 3× failed lead-capture POSTs','Retried with backoff — still 504','Paused auto-capture to avoid dropping leads','Escalated to you with the fix path'],
   ask:'Re-auth the Meta token in Activepieces (Settings → Connections → Meta). Agent will resume capture once it\'s green.',
   last:{ag:'Retried 3×, still 504 — auto-capture paused, escalated',ts:'14m ago'}},

  {id:4, t:'Refund request — damaged transfer, order #1043', client:'Evermystic', status:'Waiting on you', lvl:0, actor:'You', src:'Slack',
   skill:null, steps:[],
   ask:'You handle refunds personally. The agent flagged it and pulled the order — over to you.',
   last:{ag:'Flagged as sensitive (refund) → routed to you, order #1043 attached',ts:'21m ago'}},

  {id:5, t:'Pay supplier — DTF film restock invoice', client:'Internal', status:'Next', lvl:0, actor:'You', src:'Email',
   skill:null, steps:[],
   ask:'Approve and pay. Anything touching money stays human-only.',
   last:{ag:'Invoice received from supplier, parked for you — $312.40',ts:'1h ago'}},

  {id:6, t:'Monthly bot analytics review — Evermystic', client:'Evermystic', status:'Next', lvl:1, actor:'You', src:'Recurring',
   skill:'analytics-compiler', steps:['Pull 30-day ManyChat flow stats','Flag the biggest drop-off point','Compile into the Notion review doc','Hand to you for the pricing call'],
   ask:'Read the compiled numbers and decide if pricing needs a tweak.',
   last:{ag:'Compiled 30-day stats — biggest drop-off is at the quote step',ts:'today 7:04am'},
   result:{label:'Notion — Evermystic Analytics',url:'#'}},

  {id:7, t:'Draft proposal — cafe loyalty automation', client:'Aurora', status:'Waiting on you', lvl:2, actor:'You', src:'Manual',
   skill:'proposal-writer', steps:['Read discovery-call notes','Build a 2-page scope + price','Match Aurora\'s proposal template','Hold for your review before it goes out'],
   ask:'Review the draft proposal, then it\'s ready to send to the prospect.',
   last:{ag:'Drafted 2-page proposal from discovery notes ($1.8k build + $290/mo)',ts:'40m ago'},
   draft:`AURORA AI AGENCY — Proposal: Cafe Loyalty Automation\n\nThe build: an automated loyalty + re-order flow across IG and SMS, capturing regulars into an owned list and nudging repeat visits.\n\nInvestment: $1,800 build, then $290/mo (hosting, monthly optimisation, new flows on request).\n\nTimeline: live in 2 weeks. First month's results reviewed together.`},

  {id:8, t:'File Evermystic Q2 invoice to Drive', client:'Evermystic', status:'In progress', lvl:3, actor:'Agent', src:'Recurring',
   skill:'invoice-filer', steps:['Generate the Q2 invoice PDF','Name it to the Drive convention','File to /Clients/Evermystic/Invoices','Notify you it\'s done'],
   ask:'',
   last:{ag:'Generated invoice PDF, filing to Drive /Clients/Evermystic',ts:'just now'}},

  {id:9, t:'Schedule discovery call — cafe prospect', client:'Aurora', status:'Next', lvl:3, actor:'Agent', src:'Email',
   skill:'calendar-scheduler', steps:['Read the prospect\'s availability','Check your calendar for clashes','Propose Tue 2pm AEST','Send the invite, notify you'],
   ask:'',
   last:{ag:'Proposed Tue 2pm AEST, drafting calendar invite',ts:'18m ago'}},

  {id:10, t:'Send Saturday weekly newspaper', client:'Internal', status:'Done', lvl:4, actor:'Agent', src:'Recurring', est:30,
   skill:'dispatch-engine', steps:['Pull the week\'s outcomes from Notion','Compile the weekly newspaper','Send to your inbox'],
   ask:'',
   last:{ag:'Compiled + sent the weekly brief to your inbox',ts:'today 7:00am'},
   result:{label:'Gmail — sent ✓',url:'#'}},

  {id:11, t:'Triage + label 14 inbox emails', client:'Internal', status:'Done', lvl:4, actor:'Agent', src:'Email', est:20,
   skill:'gmail-inbox-system', steps:['Read new inbox mail','Classify by type + client','Apply labels, surface anything urgent'],
   ask:'',
   last:{ag:'Sorted 14 emails: 3 client · 2 invoices · 9 promo',ts:'today 7:02am'}},

  {id:12, t:'Sync Evermystic Lead Ledger (4 new)', client:'Evermystic', status:'Done', lvl:4, actor:'Agent', src:'Recurring', est:10,
   skill:'lead-ledger-sync', steps:['Read new captures from ManyChat','Append to the Lead Ledger sheet','Dedupe against existing rows'],
   ask:'',
   last:{ag:'Appended 4 leads to the Lead Ledger',ts:'today 7:03am'},
   result:{label:'Sheet — Lead Ledger',url:'#'}},

  {id:13, t:'Research best POS for cafe client', client:'Aurora', status:'In progress', lvl:4, actor:'Agent', src:'Manual', est:0,
   skill:'information-retrieval', steps:['Compare Square vs Lightspeed for API fit','Check loyalty + integration support','Summarise into the prospect\'s Notion'],
   ask:'',
   last:{ag:'Comparing Square vs Lightspeed — read-only research, no actions',ts:'30m ago'}},

  {id:14, t:'Waiting on Stefan: hi-vis artwork files', client:'Evermystic', status:'Waiting external', lvl:1, actor:'External', src:'Email',
   skill:'artwork-chaser', steps:['Requested the hi-vis artwork from Stefan','Awaiting his reply','Will nudge once at 24h if quiet'],
   ask:'',
   last:{ag:'Requested artwork, awaiting Stefan\'s reply',ts:'2h ago'}},

  {id:15, t:'New enquiry — gym merch run (cold IG DM)', client:'Evermystic', status:'Inbox', lvl:2, actor:'Agent', src:'ManyChat',
   skill:'lead-first-touch', steps:['New enquiry captured','Classifying intent + urgency','Will draft an opener for your approval'],
   ask:'',
   last:{ag:'New enquiry captured, classifying intent',ts:'4m ago'}},

  {id:16, t:'Auto-answered "turnaround?" FAQ ×3', client:'Evermystic', status:'Done', lvl:4, actor:'Agent', src:'ManyChat', est:8,
   skill:'faq-responder', steps:['Matched the turnaround keyword','Replied with the standard answer','Logged each as handled'],
   ask:'',
   last:{ag:'Answered 3 turnaround FAQs via the bot',ts:'today 8:10am'}},

  {id:17, t:'Posted Monday brief to Slack', client:'Internal', status:'Done', lvl:4, actor:'Agent', src:'Recurring', est:5,
   skill:'dispatch-engine', steps:['Compiled the morning brief','Posted to your Slack'],
   ask:'',
   last:{ag:'Posted the morning brief to Slack',ts:'today 7:00am'}},
];

export const INITIAL_ACTIVITY = [
  {id:1, type:'esc',  t:'Paused Evermystic lead-capture — webhook 504, escalated to you', ts:'14m ago'},
  {id:2, type:'info', t:'Filing Evermystic Q2 invoice to Drive', ts:'just now'},
  {id:3, type:'info', t:'Drafted bulk hoodie quote for Stefan — awaiting your approval', ts:'2m ago'},
  {id:4, type:'you',  t:'Captured HOT_LEAD "Priya" → drafted opener, flagged for you', ts:'8m ago'},
  {id:5, type:'ok',   t:'Synced 4 new leads to the Lead Ledger', ts:'7:03am'},
  {id:6, type:'ok',   t:'Triaged + labelled 14 inbox emails', ts:'7:02am'},
  {id:7, type:'ok',   t:'Sent the Saturday weekly newspaper', ts:'7:00am'},
  {id:8, type:'ok',   t:'Answered 3 turnaround FAQs via the bot', ts:'8:10am'},
];
