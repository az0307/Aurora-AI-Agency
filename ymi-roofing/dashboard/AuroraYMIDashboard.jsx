import { useState } from "react";

// ─── TOKENS ──────────────────────────────────────────────
const C = {
  bg: "#06101E", navy: "#0A1628", navyLight: "#0F2040",
  blue: "#1B68B4", bright: "#2E8AF6", silver: "#B8C8D8",
  white: "#FFFFFF", muted: "#6B829A", dark: "#030810",
  green: "#10B981", amber: "#F59E0B", red: "#EF4444",
  purple: "#8B5CF6",
};

// ─── DATA ─────────────────────────────────────────────────
const DELIVERABLES = [
  { id: 1, name: "Website (JSX + HTML)", status: "done", file: "ymi-roofing-final.jsx", category: "Website", time: "~8 hrs", desc: "Full production site — SEO schema, ARIA, logo embedded, n8n webhook, testimonials, clipboard copy." },
  { id: 2, name: "GitHub Actions Deploy", status: "done", file: "deploy.yml", category: "Deploy", time: "~30 min", desc: "Auto-deploys to Cloudflare Pages on every push to main. Set 2 GitHub secrets and it runs forever." },
  { id: 3, name: "n8n Lead Capture", status: "done", file: "n8n-lead-capture.json", category: "Automation", time: "~2 hrs", desc: "Webhook → Sanitize+Honeypot → Google Sheets → SMS to both Ben numbers. Importable JSON." },
  { id: 4, name: "n8n Review Machine", status: "done", file: "n8n-review-machine.json", category: "Automation", time: "~2 hrs", desc: "Ben triggers URL after each job → 24hr wait → SMS review request → 72hr wait → follow-up. Importable JSON." },
  { id: 5, name: "ManyChat Chatbot Spec", status: "done", file: "manychat-spec.md", category: "Chatbot", time: "~4 hrs build", desc: "5 flows: Welcome, Get a Quote, Emergency Repairs, FAQ, Fallback. Keyword triggers, lead capture, n8n webhook." },
  { id: 6, name: "Master Delivery Guide", status: "done", file: "MASTER-DELIVERY.md", category: "Docs", time: "—", desc: "Step-by-step: swap webhook URL → GitHub → Cloudflare → domain → n8n → ManyChat. Full replace-list." },
  { id: 7, name: "Domain Purchase", status: "todo", file: null, category: "Deploy", time: "~15 min", desc: "Buy ymiroofing.com.au at VentraIP or Hostmate (~$14/yr). Then point nameservers to Cloudflare." },
  { id: 8, name: "Cloudflare Pages Live", status: "todo", file: null, category: "Deploy", time: "~20 min", desc: "Connect GitHub repo → deploy → add custom domain → SSL auto. Refer to MASTER-DELIVERY.md Step 3." },
  { id: 9, name: "n8n Workflows Active", status: "todo", file: null, category: "Automation", time: "~1 hr", desc: "Import both JSONs, replace REPLACE_ placeholders, add Twilio + Google Sheets credentials, activate." },
  { id: 10, name: "ManyChat Flows Live", status: "todo", file: null, category: "Chatbot", time: "~4 hrs", desc: "Build flows from spec in ManyChat Pro. Connect to Ben's Facebook + Instagram. Test end-to-end." },
  { id: 11, name: "Google Business Profile", status: "todo", file: null, category: "SEO", time: "~2 hrs", desc: "Set up GBP: categories, all photos, service areas, Q&A, hours. Update website URL to ymiroofing.com.au." },
  { id: 12, name: "Jobber CRM Setup", status: "todo", file: null, category: "AI Adoption", time: "~4 hrs", desc: "Set up Jobber Core for Ben: contacts, job stages, quote template, invoice branding. 1hr walkthrough." },
];

const WORKFLOW_LEAD = [
  { step: 1, name: "Receive Lead", type: "Webhook", icon: "🌐", color: C.blue, desc: "POST /webhook/ymi-roofing-lead from website form" },
  { step: 2, name: "Sanitize + Honeypot", type: "Code", icon: "⚙️", color: C.purple, desc: "Drop bots, normalise AU phone to +614…, format payload" },
  { step: 3, name: "Log to Sheets", type: "Google Sheets", icon: "📊", color: C.green, desc: "Append row: Timestamp, Name, Phone, Suburb, Service, Message" },
  { step: 4, name: "SMS to Ben ×2", type: "Twilio", icon: "📱", color: C.amber, desc: "Alert both 0422 and 0423 numbers with full lead summary" },
  { step: 5, name: "Respond 200 OK", type: "Webhook Response", icon: "✅", color: C.green, desc: "Return success JSON to website form handler" },
];

const WORKFLOW_REVIEW = [
  { step: 1, name: "Job Done Trigger", type: "Webhook", icon: "🔔", color: C.blue, desc: "Ben opens bookmarked URL: /ymi-review-done?name=John&phone=0412…" },
  { step: 2, name: "Parse + Log Job", type: "Code + Sheets", icon: "⚙️", color: C.purple, desc: "Extract name/phone, log to Completed Jobs sheet, confirm to Ben" },
  { step: 3, name: "Wait 24 Hours", type: "Wait", icon: "⏰", color: C.muted, desc: "Pause execution — n8n resumes automatically after 24hrs" },
  { step: 4, name: "SMS Review Request", type: "Twilio", icon: "⭐", color: C.amber, desc: "Personalised SMS to customer with direct Google review link" },
  { step: 5, name: "Wait 72 Hours", type: "Wait", icon: "⏰", color: C.muted, desc: "Pause again for 3 days" },
  { step: 6, name: "SMS Follow-Up", type: "Twilio", icon: "💬", color: C.amber, desc: "Softer second ask if no review yet" },
];

const MANYCHAT_FLOWS = [
  { name: "Welcome", trigger: "Greeting / Default", route: "4 quick-reply buttons" },
  { name: "Get a Quote", trigger: "quote, price, cost, how much", route: "Service → Suburb → Phone → Send to n8n" },
  { name: "Emergency Repair", trigger: "repair, leak, cracked, emergency", route: "Urgent → call direct / Non-urgent → Quote flow" },
  { name: "Service Areas", trigger: "area, suburb, where, location", route: "List areas → Get a Quote button" },
  { name: "Fallback", trigger: "Anything unrecognised", route: "4 buttons: Quote / Repair / Call / Website" },
];

const MONTHLY_COSTS = [
  { item: "Cloudflare Pages hosting", cost: "$0.00" },
  { item: "Domain (ymiroofing.com.au)", cost: "~$1.20" },
  { item: "n8n (self-hosted, existing)", cost: "$0.00" },
  { item: "Twilio (~30 SMS/mo)", cost: "~$0.60" },
  { item: "ManyChat Pro", cost: "~$22.00" },
];

const REPLACE_LIST = [
  { file: "ymi-roofing-final.jsx", find: "YOUR-N8N-DOMAIN", with: "your n8n server hostname" },
  { file: "n8n-lead-capture.json", find: "REPLACE_SHEET_ID", with: "Google Sheet ID from URL" },
  { file: "n8n-lead-capture.json", find: "REPLACE_TWILIO_NUMBER", with: "Your Twilio virtual number (+614…)" },
  { file: "n8n-review-machine.json", find: "REPLACE_SHEET_ID", with: "Same Google Sheet ID" },
  { file: "n8n-review-machine.json", find: "REPLACE_TWILIO_NUMBER", with: "Your Twilio virtual number" },
  { file: "n8n-review-machine.json", find: "REPLACE_GOOGLE_PLACE_ID", with: "Ben's Google Place ID (from GBP)" },
  { file: "deploy.yml", find: "CLOUDFLARE_API_TOKEN (secret)", with: "Set in GitHub repo Settings → Secrets" },
  { file: "deploy.yml", find: "CLOUDFLARE_ACCOUNT_ID (secret)", with: "Set in GitHub repo Settings → Secrets" },
];

const PITCH_HOOKS = [
  { hook: "Speed = Jobs", body: "78% of customers book the first business that calls them back. Right now your competitors are missing the same calls you are. We fix that — automatically, even while you're on the roof." },
  { hook: "Reviews = Free Leads", body: "One 5-star Google review is worth more than a $50 Facebook ad. We build a machine that generates them for you after every single job, with zero effort on your end." },
  { hook: "Pro Website = Credibility", body: "Your work is premium. Your online presence should match. A polished website with a clear quote button converts 3× better than no site or a basic Facebook page." },
];

const TABS = [
  { id: "status",   label: "Deliverables" },
  { id: "setup",    label: "Setup Steps" },
  { id: "lead",     label: "Lead Workflow" },
  { id: "review",   label: "Review Machine" },
  { id: "manychat", label: "ManyChat" },
  { id: "costs",    label: "Costs & ROI" },
  { id: "pitch",    label: "Pitch Hooks" },
  { id: "framework",label: "Aurora Framework" },
];

// ─── REUSABLE COMPONENTS ─────────────────────────────────
const Tag = ({ label, color = C.blue }) => (
  <span style={{ display: "inline-block", padding: "2px 8px", borderRadius: 4, fontSize: 10, fontWeight: 700, letterSpacing: "0.06em", background: `${color}22`, color, border: `1px solid ${color}44`, fontFamily: "monospace" }}>{label}</span>
);

const StatusBadge = ({ status }) => {
  const map = { done: [C.green, "✓ Done"], todo: [C.amber, "⏳ To Do"], blocked: [C.red, "⛔ Blocked"] };
  const [color, label] = map[status] || [C.muted, status];
  return <Tag label={label} color={color} />;
};

const Card = ({ children, style = {} }) => (
  <div style={{ background: `linear-gradient(160deg, ${C.navyLight}, ${C.navy})`, border: `1px solid ${C.blue}25`, borderRadius: 10, padding: 18, marginBottom: 10, ...style }}>
    {children}
  </div>
);

const SectionLabel = ({ children }) => (
  <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.18em", color: C.blue, textTransform: "uppercase", marginBottom: 14 }}>{children}</div>
);

// ─── VIEWS ───────────────────────────────────────────────

function StatusView() {
  const [filter, setFilter] = useState("all");
  const cats = ["all", "Website", "Deploy", "Automation", "Chatbot", "SEO", "AI Adoption", "Docs"];
  const shown = DELIVERABLES.filter(d => filter === "all" || d.category === filter);
  const done = DELIVERABLES.filter(d => d.status === "done").length;
  return (
    <div>
      <Card>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 0 }}>
          {[
            ["Complete", `${done}/${DELIVERABLES.length}`, C.green],
            ["In Progress", "0", C.amber],
            ["To Do", `${DELIVERABLES.length - done}`, C.muted],
          ].map(([label, val, color]) => (
            <div key={label} style={{ textAlign: "center" }}>
              <div style={{ fontFamily: "monospace", fontSize: 28, fontWeight: 700, color }}>{val}</div>
              <div style={{ fontSize: 11, color: C.muted, marginTop: 2 }}>{label}</div>
            </div>
          ))}
        </div>
      </Card>

      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 14 }}>
        {cats.map(c => (
          <button key={c} onClick={() => setFilter(c)} style={{ background: filter === c ? C.blue : "transparent", border: `1px solid ${filter === c ? C.blue : C.blue + "44"}`, borderRadius: 6, padding: "4px 12px", cursor: "pointer", fontSize: 11, fontWeight: 600, color: filter === c ? C.white : C.silver, fontFamily: "sans-serif" }}>{c}</button>
        ))}
      </div>

      {shown.map(d => (
        <Card key={d.id} style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
          <div style={{ flexShrink: 0, width: 28, height: 28, borderRadius: "50%", background: d.status === "done" ? `${C.green}22` : `${C.amber}22`, border: `1px solid ${d.status === "done" ? C.green : C.amber}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, marginTop: 2 }}>
            {d.status === "done" ? "✓" : "○"}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap", marginBottom: 4 }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: C.white }}>{d.name}</div>
              <StatusBadge status={d.status} />
              <Tag label={d.category} color={C.purple} />
              <Tag label={d.time} color={C.muted} />
            </div>
            <div style={{ fontSize: 12, color: C.silver, lineHeight: 1.6 }}>{d.desc}</div>
            {d.file && <div style={{ marginTop: 6, fontSize: 11, color: C.blue, fontFamily: "monospace" }}>📄 {d.file}</div>}
          </div>
        </Card>
      ))}
    </div>
  );
}

function SetupView() {
  const [open, setOpen] = useState(0);
  const steps = [
    {
      n: 1, title: "Swap WEBHOOK_URL", time: "5 min",
      content: (
        <div>
          <p style={{ fontSize: 13, color: C.silver, marginBottom: 12 }}>Open <code style={{ background: C.dark, padding: "2px 6px", borderRadius: 4 }}>ymi-roofing-final.jsx</code> and find line 4:</p>
          <pre style={{ background: C.dark, borderRadius: 8, padding: 14, fontSize: 12, color: "#7DD3FC", overflowX: "auto" }}>{`const WEBHOOK_URL = "https://YOUR-N8N-DOMAIN/webhook/ymi-roofing-lead";`}</pre>
          <p style={{ fontSize: 13, color: C.silver, margin: "10px 0 6px" }}>Replace with your actual n8n URL:</p>
          <pre style={{ background: C.dark, borderRadius: 8, padding: 14, fontSize: 12, color: "#86EFAC", overflowX: "auto" }}>{`const WEBHOOK_URL = "https://n8n.yourdomain.com/webhook/ymi-roofing-lead";`}</pre>
        </div>
      )
    },
    {
      n: 2, title: "Upload to GitHub", time: "10 min",
      content: (
        <div>
          <pre style={{ background: C.dark, borderRadius: 8, padding: 14, fontSize: 12, color: "#7DD3FC", overflowX: "auto", lineHeight: 1.8 }}>{`mkdir ymi-roofing-frontend && cd ymi-roofing-frontend
git init && git branch -M main

# Copy files in:
# index.html (production HTML — from ymi-roofing-production/)
# .github/workflows/deploy.yml

git add .
git commit -m "feat: YMI Roofing initial deploy"
git remote add origin https://github.com/YOUR_ORG/ymi-roofing-frontend.git
git push -u origin main`}</pre>
          <p style={{ fontSize: 12, color: C.muted, marginTop: 10 }}>Keep the repo <strong style={{ color: C.white }}>Private</strong>. Add GitHub Secrets: <code style={{ background: C.dark, padding: "1px 5px", borderRadius: 3, fontSize: 11 }}>CLOUDFLARE_API_TOKEN</code> and <code style={{ background: C.dark, padding: "1px 5px", borderRadius: 3, fontSize: 11 }}>CLOUDFLARE_ACCOUNT_ID</code></p>
        </div>
      )
    },
    {
      n: 3, title: "Cloudflare Pages + Domain", time: "30 min",
      content: (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {[
            ["1", "Cloudflare → Workers & Pages → Pages → Connect to Git → select repo"],
            ["2", "Build settings: Framework = None, Build command = blank, Output = /"],
            ["3", "Deploy → get ymi-roofing-frontend.pages.dev live URL"],
            ["4", "Buy ymiroofing.com.au at VentraIP (~$14/yr)"],
            ["5", "Cloudflare → Add Site → enter ymiroofing.com.au → copy 2 nameservers"],
            ["6", "VentraIP → DNS settings → replace nameservers with Cloudflare's"],
            ["7", "Cloudflare Pages → Custom Domains → Set up ymiroofing.com.au"],
            ["8", "Wait 1–24hrs for DNS propagation. SSL is automatic."],
          ].map(([n, text]) => (
            <div key={n} style={{ display: "flex", gap: 10 }}>
              <div style={{ width: 20, height: 20, borderRadius: "50%", background: C.blue, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700 }}>{n}</div>
              <div style={{ fontSize: 12, color: C.silver, paddingTop: 2 }}>{text}</div>
            </div>
          ))}
        </div>
      )
    },
    {
      n: 4, title: "Wire n8n Workflows", time: "60 min",
      content: (
        <div>
          <SectionLabel>Replacements needed in both JSON files</SectionLabel>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {REPLACE_LIST.filter(r => r.file.includes("json")).map((r, i) => (
              <div key={i} style={{ background: C.dark, borderRadius: 8, padding: 12 }}>
                <div style={{ fontSize: 10, color: C.muted, marginBottom: 4 }}>{r.file}</div>
                <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                  <code style={{ fontSize: 11, color: C.red, background: `${C.red}15`, padding: "2px 6px", borderRadius: 4 }}>{r.find}</code>
                  <span style={{ color: C.muted, fontSize: 11 }}>→</span>
                  <span style={{ fontSize: 12, color: C.silver }}>{r.with}</span>
                </div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 14, background: `${C.green}12`, border: `1px solid ${C.green}33`, borderRadius: 8, padding: 12, fontSize: 12, color: C.silver }}>
            <strong style={{ color: C.green }}>Test command:</strong><br />
            <code style={{ color: "#7DD3FC" }}>curl -X POST https://YOUR-N8N/webhook/ymi-roofing-lead -H "Content-Type: application/json" -d '{`{"name":"Test","phone":"0400000000","suburb":"Test","service":"Repairs"}`}'</code>
          </div>
        </div>
      )
    },
    {
      n: 5, title: "ManyChat + Google Business Profile", time: "6 hrs",
      content: (
        <div>
          <SectionLabel>ManyChat</SectionLabel>
          <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 16 }}>
            {["Connect Facebook Page + Instagram to ManyChat Pro", "Build 5 flows from manychat-spec.md", "Set keyword triggers (quote, price, repair, area…)", "Set up Custom Action webhook → n8n endpoint", "Test every flow end-to-end"].map((s, i) => (
              <div key={i} style={{ display: "flex", gap: 8, fontSize: 12, color: C.silver }}>
                <span style={{ color: C.blue }}>→</span>{s}
              </div>
            ))}
          </div>
          <SectionLabel>Google Business Profile</SectionLabel>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {["Create GBP for Y.M.I Roofing at business.google.com", "Category: Roof Tiler + Roofing Contractor", "Add all 6 services with descriptions", "Upload 10+ job photos", "Set service areas (Melbourne suburbs)", "Get Google Place ID → update review machine workflow", "Update website URL to ymiroofing.com.au once live"].map((s, i) => (
              <div key={i} style={{ display: "flex", gap: 8, fontSize: 12, color: C.silver }}>
                <span style={{ color: C.green }}>→</span>{s}
              </div>
            ))}
          </div>
        </div>
      )
    },
  ];

  return (
    <div>
      {steps.map((s, i) => (
        <div key={s.n} style={{ marginBottom: 8 }}>
          <div onClick={() => setOpen(open === i ? -1 : i)} style={{ background: C.navy, border: `1px solid ${open === i ? C.blue : C.blue + "33"}`, borderRadius: open === i ? "10px 10px 0 0" : 10, padding: "14px 18px", cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <div style={{ width: 28, height: 28, borderRadius: "50%", background: `${C.blue}22`, border: `1px solid ${C.blue}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, color: C.blue, flexShrink: 0 }}>{s.n}</div>
              <div>
                <div style={{ fontSize: 14, fontWeight: 700, color: C.white }}>{s.title}</div>
                <div style={{ fontSize: 11, color: C.muted }}>Est. {s.time}</div>
              </div>
            </div>
            <span style={{ color: C.muted, fontSize: 14 }}>{open === i ? "▲" : "▼"}</span>
          </div>
          {open === i && (
            <div style={{ background: C.navy, border: `1px solid ${C.blue}`, borderTop: "none", borderRadius: "0 0 10px 10px", padding: "16px 18px" }}>
              {s.content}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function WorkflowView({ nodes, title }) {
  return (
    <div>
      <Card style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 12, color: C.silver, lineHeight: 1.7 }}>
          <strong style={{ color: C.white }}>Import file → </strong> Settings → Import workflow in n8n. Then update the REPLACE_ placeholders and activate.
        </div>
      </Card>
      <div style={{ position: "relative" }}>
        {nodes.map((node, i) => (
          <div key={i} style={{ display: "flex", gap: 14, marginBottom: i < nodes.length - 1 ? 0 : 0 }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <div style={{ width: 44, height: 44, borderRadius: "50%", background: `${node.color}22`, border: `2px solid ${node.color}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, flexShrink: 0 }}>{node.icon}</div>
              {i < nodes.length - 1 && <div style={{ width: 2, height: 32, background: `${node.color}44`, margin: "4px 0" }} />}
            </div>
            <div style={{ flex: 1, paddingBottom: i < nodes.length - 1 ? 24 : 0, paddingTop: 8 }}>
              <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
                <div style={{ fontSize: 14, fontWeight: 700, color: C.white }}>{node.name}</div>
                <Tag label={node.type} color={node.color} />
              </div>
              <div style={{ fontSize: 12, color: C.silver }}>{node.desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ManyView() {
  const [activeFlow, setActiveFlow] = useState(0);
  const chatPreviews = [
    [
      { from: "user", text: "Hi there!" },
      { from: "bot", text: "Hi there! 👋 Thanks for reaching out to Y.M.I Roofing.\n\nWhat can I help you with today?" },
      { from: "bot", text: "🏠 Get a Quote   🔧 Emergency Repair\n🔍 Roof Inspection   💬 Something Else", isButtons: true },
    ],
    [
      { from: "user", text: "How much does roof tiling cost?" },
      { from: "bot", text: "Great! Getting you a free quote is easy.\n\nWhat type of work do you need?" },
      { from: "bot", text: "New Roof Tiling\nRe-Bedding & Re-Pointing\nRoof Repairs\nTile Replacement\nRidge Capping\nNot sure — need advice", isButtons: true },
      { from: "user", text: "Roof Repairs" },
      { from: "bot", text: "Perfect. What's your suburb?" },
      { from: "user", text: "Croydon" },
      { from: "bot", text: "And what's the best phone number to reach you?" },
      { from: "user", text: "0412 345 678" },
      { from: "bot", text: "✅ Done! Ben has been notified and will call you within 1 hour.\n\nYou can also reach him directly:\n📞 0422 093 241" },
    ],
    [
      { from: "user", text: "I have a leak — urgent!" },
      { from: "bot", text: "Oh no — leaks need attention fast. 🛠️\n\nIs this an emergency (active leak, storm damage)?" },
      { from: "bot", text: "🚨 Yes — emergency   ⏰ No — can wait", isButtons: true },
      { from: "user", text: "🚨 Yes — emergency" },
      { from: "bot", text: "For urgent repairs, call Ben directly — he'll do his best to get out ASAP.\n\n📞 0422 093 241\n📞 0423 858 503\n\nTell him it's urgent. 👍" },
    ],
  ];

  return (
    <div>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 16 }}>
        {MANYCHAT_FLOWS.map((f, i) => (
          <button key={i} onClick={() => setActiveFlow(i)} style={{ background: activeFlow === i ? C.blue : "transparent", border: `1px solid ${activeFlow === i ? C.blue : C.blue + "44"}`, borderRadius: 6, padding: "5px 12px", cursor: "pointer", fontSize: 11, fontWeight: 600, color: activeFlow === i ? C.white : C.silver, fontFamily: "sans-serif" }}>
            {f.name}
          </button>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <Card>
          <SectionLabel>Flow Info</SectionLabel>
          <div style={{ marginBottom: 10 }}>
            <div style={{ fontSize: 10, color: C.muted, marginBottom: 3 }}>TRIGGERS</div>
            <div style={{ fontSize: 12, color: C.silver, fontFamily: "monospace", background: C.dark, padding: "6px 10px", borderRadius: 6 }}>{MANYCHAT_FLOWS[activeFlow]?.trigger}</div>
          </div>
          <div>
            <div style={{ fontSize: 10, color: C.muted, marginBottom: 3 }}>ROUTE</div>
            <div style={{ fontSize: 12, color: C.silver }}>{MANYCHAT_FLOWS[activeFlow]?.route}</div>
          </div>
        </Card>

        {/* Chat preview */}
        <div style={{ background: "#111827", borderRadius: 10, overflow: "hidden", border: `1px solid ${C.blue}25` }}>
          <div style={{ background: C.navyLight, padding: "10px 14px", display: "flex", alignItems: "center", gap: 10, borderBottom: `1px solid ${C.blue}22` }}>
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: C.green }} />
            <div style={{ fontSize: 12, fontWeight: 700, color: C.white }}>Y.M.I Roofing</div>
            <div style={{ fontSize: 10, color: C.muted }}>Instagram DM</div>
          </div>
          <div style={{ padding: 14, display: "flex", flexDirection: "column", gap: 10, maxHeight: 320, overflowY: "auto" }}>
            {(chatPreviews[activeFlow] || chatPreviews[0]).map((msg, i) => (
              <div key={i} style={{ display: "flex", justifyContent: msg.from === "user" ? "flex-end" : "flex-start" }}>
                <div style={{
                  maxWidth: "80%", padding: "8px 12px", borderRadius: msg.from === "user" ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
                  background: msg.from === "user" ? C.blue : C.navyLight,
                  border: `1px solid ${msg.from === "user" ? C.blue : C.blue + "33"}`,
                  fontSize: 12, color: C.white, lineHeight: 1.55, whiteSpace: "pre-line",
                }}>
                  {msg.text}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function CostsView() {
  const total = 23.80;
  const retainer = 350;
  const margin = ((retainer - total) / retainer * 100).toFixed(0);

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 16 }}>
        {[
          ["Monthly Cost", `$${total.toFixed(2)}`, C.muted],
          ["Ignite Retainer", `$${retainer}`, C.blue],
          ["Net Margin", `${margin}%`, C.green],
        ].map(([label, val, color]) => (
          <Card key={label} style={{ textAlign: "center" }}>
            <div style={{ fontSize: 28, fontWeight: 700, color, fontFamily: "monospace" }}>{val}</div>
            <div style={{ fontSize: 11, color: C.muted, marginTop: 4 }}>{label}</div>
          </Card>
        ))}
      </div>

      <Card>
        <SectionLabel>Monthly Cost Breakdown</SectionLabel>
        {MONTHLY_COSTS.map((row, i) => (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: i < MONTHLY_COSTS.length - 1 ? `1px solid ${C.blue}22` : "none" }}>
            <span style={{ fontSize: 13, color: C.silver }}>{row.item}</span>
            <span style={{ fontSize: 13, color: C.white, fontFamily: "monospace", fontWeight: 700 }}>{row.cost}</span>
          </div>
        ))}
        <div style={{ display: "flex", justifyContent: "space-between", padding: "10px 0 0", marginTop: 4 }}>
          <span style={{ fontSize: 13, fontWeight: 700, color: C.white }}>Total</span>
          <span style={{ fontSize: 15, fontWeight: 700, color: C.amber, fontFamily: "monospace" }}>~$23.80 AUD/mo</span>
        </div>
      </Card>

      <Card style={{ background: `${C.green}12`, border: `1px solid ${C.green}33` }}>
        <SectionLabel>Aurora Trades Stack — Scaling Economics</SectionLabel>
        {[
          ["Client 1 (YMI)", "$350/mo", "$23.80/mo", "$326.20", "93%"],
          ["Client 2 (+1 trades)", "$700/mo", "$30/mo", "$670", "96%"],
          ["Client 3 (+1 trades)", "$1,050/mo", "$36/mo", "$1,014", "97%"],
          ["5 Clients", "$1,750/mo", "$55/mo", "$1,695", "97%"],
        ].map(([client, rev, cost, margin, pct]) => (
          <div key={client} style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr 1fr 1fr", gap: 8, padding: "8px 0", borderBottom: `1px solid ${C.blue}18`, fontSize: 12 }}>
            <span style={{ color: C.white, fontWeight: 600 }}>{client}</span>
            <span style={{ color: C.blue, fontFamily: "monospace" }}>{rev}</span>
            <span style={{ color: C.muted, fontFamily: "monospace" }}>{cost}</span>
            <span style={{ color: C.white, fontFamily: "monospace" }}>{margin}</span>
            <span style={{ color: C.green, fontFamily: "monospace" }}>{pct}</span>
          </div>
        ))}
        <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr 1fr 1fr", gap: 8, paddingTop: 6, fontSize: 10, color: C.muted }}>
          <span>Client</span><span>Revenue</span><span>Stack Cost</span><span>Net</span><span>Margin</span>
        </div>
        <div style={{ fontSize: 12, color: C.muted, marginTop: 12 }}>Second client onwards costs almost nothing extra — n8n is self-hosted, Cloudflare is free. Each new client is near-pure margin.</div>
      </Card>
    </div>
  );
}

function PitchView() {
  return (
    <div>
      <Card style={{ background: `${C.amber}10`, border: `1px solid ${C.amber}33`, marginBottom: 20 }}>
        <SectionLabel>Opening Hook (lead with this)</SectionLabel>
        <div style={{ fontSize: 15, color: C.white, lineHeight: 1.7, fontStyle: "italic" }}>
          "Ben, you're on the roof and missing calls. Your competitors are missing the same calls. We make you the business that always responds first — automatically. Then your Google reviews do the rest of the selling."
        </div>
      </Card>

      {PITCH_HOOKS.map((p, i) => (
        <Card key={i}>
          <div style={{ fontSize: 13, fontWeight: 700, color: C.amber, marginBottom: 8 }}>Hook {i + 1}: {p.hook}</div>
          <div style={{ fontSize: 13, color: C.silver, lineHeight: 1.7 }}>{p.body}</div>
        </Card>
      ))}

      <Card>
        <SectionLabel>Recommended Pitch Sequence</SectionLabel>
        {[
          ["1. Lead with the problem", "\"You're on the roof. Your phone rings. You can't answer. That job just went to the next roofer.\""],
          ["2. Show the solution", "\"We build an automatic system that texts the customer within 30 seconds and texts you the lead details.\""],
          ["3. Stack the value", "\"Same system asks every happy customer for a Google review 24hrs after the job. While you sleep.\""],
          ["4. Social proof", "\"Croydon, Doncaster, Ringwood — local homeowners who need a tiler find you first.\""],
          ["5. Anchor price", "\"Everything for $350 a month. Less than one job covers it.\""],
          ["6. Low-risk close", "\"Start with Spark ($199/mo) — website + Google profile only. Prove it works. Upgrade from there.\""],
        ].map(([label, text]) => (
          <div key={label} style={{ display: "flex", gap: 12, padding: "8px 0", borderBottom: `1px solid ${C.blue}22` }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: C.blue, minWidth: 180, paddingTop: 1 }}>{label}</div>
            <div style={{ fontSize: 12, color: C.silver, lineHeight: 1.6 }}>{text}</div>
          </div>
        ))}
      </Card>
    </div>
  );
}

function FrameworkView() {
  const stages = [
    { n: "01", name: "Discovery", time: "30 min", input: "Business card, logo, 10-question form", process: "Extract brand colours, contact info, services, USPs", output: "Brand token file, content data objects", tools: ["Claude API", "Camera"] },
    { n: "02", name: "Website Build", time: "4–6 hrs", input: "Brand tokens, content, logo (base64)", process: "Clone ymi-roofing-final.jsx, swap tokens + content, embed logo", output: "Production JSX + static HTML", tools: ["Claude", "Wix / Cloudflare Pages"] },
    { n: "03", name: "Automations", time: "3–4 hrs", input: "n8n instance, Twilio creds, Google Sheet ID", process: "Import both workflow JSONs, update REPLACE_ values, add creds, test", output: "Live lead capture + review machine", tools: ["n8n", "Twilio", "Google Sheets"] },
    { n: "04", name: "Chatbot", time: "3–4 hrs", input: "Client FAQ answers, ManyChat account", process: "Clone flow spec, update services/service areas, add Custom Action webhook", output: "Live FB + Instagram chatbot with lead capture", tools: ["ManyChat", "n8n"] },
    { n: "05", name: "Deploy + Handover", time: "1–2 hrs", input: "GitHub repo, Cloudflare, domain, client contact", process: "Run deploy workflow, connect domain, walkthrough with Ben, hand over bookmarked review URL", output: "Live site, trained client, Aurora credit in footer", tools: ["GitHub Actions", "Cloudflare Pages"] },
  ];

  return (
    <div>
      <Card style={{ background: `${C.purple}12`, border: `1px solid ${C.purple}33`, marginBottom: 16 }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: C.purple, marginBottom: 6 }}>Aurora Trades Stack v1.0 — Reusable Framework</div>
        <div style={{ fontSize: 12, color: C.silver, lineHeight: 1.7 }}>
          Extracted from YMI Roofing delivery. Apply to any Melbourne trades client (plumber, electrician, painter, tiler, landscaper) in <strong style={{ color: C.white }}>12–16 hrs</strong> vs 40+ hrs for Client 1. Each subsequent client is near-pure margin.
        </div>
      </Card>

      {stages.map((s, i) => (
        <Card key={i} style={{ borderLeft: `3px solid ${C.blue}` }}>
          <div style={{ display: "flex", gap: 12, alignItems: "flex-start", marginBottom: 12 }}>
            <div style={{ fontFamily: "monospace", fontSize: 28, fontWeight: 700, color: `${C.blue}66`, lineHeight: 1, flexShrink: 0 }}>{s.n}</div>
            <div>
              <div style={{ fontSize: 15, fontWeight: 700, color: C.white, marginBottom: 2 }}>{s.name}</div>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                <Tag label={s.time} color={C.amber} />
                {s.tools.map(t => <Tag key={t} label={t} color={C.muted} />)}
              </div>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10 }}>
            {[["Input", s.input, C.blue], ["Process", s.process, C.purple], ["Output", s.output, C.green]].map(([label, text, color]) => (
              <div key={label} style={{ background: `${color}10`, borderRadius: 6, padding: "8px 10px", border: `1px solid ${color}22` }}>
                <div style={{ fontSize: 9, fontWeight: 700, color, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 4 }}>{label}</div>
                <div style={{ fontSize: 11, color: C.silver, lineHeight: 1.5 }}>{text}</div>
              </div>
            ))}
          </div>
        </Card>
      ))}

      <Card>
        <SectionLabel>Next Trades Clients — Target List</SectionLabel>
        {[
          ["Local Plumber", "Same stack. Swap services. Emergency call routing more important."],
          ["Electrician", "Same stack. Add safety disclaimer to chatbot. Licensing field on form."],
          ["Painter", "Same stack. Add 'project type' (interior/exterior). Portfolio gallery heavier."],
          ["Landscaper", "Same stack. Seasonal campaigns. Maintenance reminder system key."],
          ["Solar Installer", "Same stack. Add financing FAQ flows. Higher-value lead = more automation justified."],
        ].map(([client, note]) => (
          <div key={client} style={{ display: "flex", gap: 12, padding: "8px 0", borderBottom: `1px solid ${C.blue}18` }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: C.white, minWidth: 140 }}>{client}</div>
            <div style={{ fontSize: 12, color: C.muted }}>{note}</div>
          </div>
        ))}
      </Card>
    </div>
  );
}

// ─── APP ─────────────────────────────────────────────────
export default function App() {
  const [tab, setTab] = useState("status");

  return (
    <div style={{ background: C.bg, minHeight: "100vh", fontFamily: "'Inter', sans-serif", color: C.white }}>
      <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />

      {/* Header */}
      <div style={{ background: C.navyLight, borderBottom: `1px solid ${C.blue}33`, padding: "16px 20px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", maxWidth: 960, margin: "0 auto" }}>
          <div>
            <div style={{ fontSize: 10, color: C.blue, fontWeight: 700, letterSpacing: "0.16em", textTransform: "uppercase", marginBottom: 3 }}>Aurora AI Agency</div>
            <div style={{ fontFamily: "'Syne', sans-serif", fontSize: 18, fontWeight: 800, letterSpacing: "-0.02em" }}>YMI Roofing — Full Delivery Package</div>
            <div style={{ fontSize: 11, color: C.muted, marginTop: 2 }}>Ben Breheny · ACN 695 710 055 · 0422 093 241</div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 10, color: C.muted }}>Skills Used</div>
            <div style={{ fontSize: 9, color: C.blue, fontFamily: "monospace" }}>ActionPlan · FrameworkExtractor · OpportunityMapper · LeveragePointFinder</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ background: C.navyLight, borderBottom: `1px solid ${C.blue}22`, padding: "0 20px", display: "flex", gap: 0, overflowX: "auto", maxWidth: "100%" }}>
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            background: "none", border: "none", padding: "10px 14px", cursor: "pointer",
            fontSize: 12, fontWeight: 600, color: tab === t.id ? C.bright : C.muted,
            borderBottom: tab === t.id ? `2px solid ${C.bright}` : "2px solid transparent",
            whiteSpace: "nowrap", fontFamily: "sans-serif",
            transition: "color 0.2s",
          }}>{t.label}</button>
        ))}
      </div>

      {/* Body */}
      <div style={{ padding: 20, maxWidth: 960, margin: "0 auto" }}>
        {tab === "status"    && <StatusView />}
        {tab === "setup"     && <SetupView />}
        {tab === "lead"      && <WorkflowView nodes={WORKFLOW_LEAD}   title="Lead Capture" />}
        {tab === "review"    && <WorkflowView nodes={WORKFLOW_REVIEW} title="Review Machine" />}
        {tab === "manychat"  && <ManyView />}
        {tab === "costs"     && <CostsView />}
        {tab === "pitch"     && <PitchView />}
        {tab === "framework" && <FrameworkView />}
      </div>
    </div>
  );
}
