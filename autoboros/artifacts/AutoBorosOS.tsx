import { useState, useEffect, useRef } from "react";

// ── CONSTANTS ────────────────────────────────────────────────────────────────
const MODEL   = "claude-sonnet-4-20250514";
const DAYS    = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
const SHORT   = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
const MONTHS  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

const ENERGY = [
  { id:"red",    label:"🔴 Deep Work",  desc:"Complex builds, new systems",        color:"#e05050", bg:"#2a0808" },
  { id:"yellow", label:"🟡 Medium",     desc:"Client work, research, docs",         color:"#e09020", bg:"#2a1a00" },
  { id:"green",  label:"🟢 Light",      desc:"Admin, email, reviewing",             color:"#40b060", bg:"#082008" },
  { id:"sleep",  label:"😴 Rest/Care",  desc:"Grandparent care, rest",             color:"#506080", bg:"#080e18" },
  { id:"create", label:"🎨 Creative",   desc:"Ratdog & Skunk, design",             color:"#9060d0", bg:"#160828" },
  { id:"client", label:"💼 Client",     desc:"Aurora/Evermystic — billable",       color:"#2080c0", bg:"#081428" },
];

const BLOCKS = [
  { id:"b1", label:"Early",     time:"5–8am",    icon:"🌅" },
  { id:"b2", label:"Morning",   time:"8–11am",   icon:"☕" },
  { id:"b3", label:"Midday",    time:"11am–2pm", icon:"⚡" },
  { id:"b4", label:"Afternoon", time:"2–5pm",    icon:"🔧" },
  { id:"b5", label:"Evening",   time:"5–8pm",    icon:"🌆" },
  { id:"b6", label:"Night",     time:"8–11pm",   icon:"🌙" },
];

const PROJECTS = ["ECC Recovery","Kali Agent","HexStrike","Evermystic","Aurora Agency",
  "Ratdog & Skunk","Home Lab","Elder Care","AutoBoros Stack","WorldMonitor",
  "Legal Skills","Notion Skills","Personal","Admin","Research"];

const DEFAULT_SCHED = {
  Monday:    {b1:"sleep",b2:"green", b3:"yellow",b4:"red",   b5:"yellow",b6:"green"},
  Tuesday:   {b1:"sleep",b2:"red",   b3:"red",   b4:"yellow",b5:"client",b6:"yellow"},
  Wednesday: {b1:"sleep",b2:"yellow",b3:"red",   b4:"red",   b5:"yellow",b6:"green"},
  Thursday:  {b1:"sleep",b2:"red",   b3:"red",   b4:"client",b5:"create",b6:"yellow"},
  Friday:    {b1:"sleep",b2:"yellow",b3:"client",b4:"green", b5:"create",b6:"sleep"},
  Saturday:  {b1:"sleep",b2:"green", b3:"green", b4:"sleep", b5:"sleep", b6:"sleep"},
  Sunday:    {b1:"sleep",b2:"sleep", b3:"yellow",b4:"red",   b5:"yellow",b6:"green"},
};

const SCAN_URL = "https://claude.ai/new?q=" + encodeURIComponent("Scan today's conversations and give me my AutoBoros Dispatch daily brief block — structured as: headline, rating, sessions (time/hed/body), stats, pull_quote. I'll paste it into my Dispatch Engine.");
const SAT_URL  = "https://claude.ai/new?q=" + encodeURIComponent("Scan this week's conversations and give me my AutoBoros Dispatch Saturday edition brief — a full summary of every day this week: what I built, sessions, key outputs, stats, patterns. I'll paste it into my Dispatch Engine to compile the weekly newspaper.");

// ── HELPERS ──────────────────────────────────────────────────────────────────
function fmt(d){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;}
function fmtDisplay(d){return `${DAYS[d.getDay()===0?6:d.getDay()-1]} ${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}`;}
function weekStart(){
  const d=new Date(), day=d.getDay(), diff=day===0?-6:1-day;
  const m=new Date(d); m.setDate(d.getDate()+diff); return m;
}
function weekKey(d){
  const day=d.getDay(),diff=d.getDate()-day+(day===0?-6:1);
  const m=new Date(d); m.setDate(diff); return fmt(m);
}
function weekDates(wk){
  const m=new Date(wk+"T00:00:00");
  return Array.from({length:7},(_,i)=>{const x=new Date(m);x.setDate(m.getDate()+i);return x;});
}
function addDays(d,n){const x=new Date(d);x.setDate(x.getDate()+n);return x;}
function timeToMins(t){const[h,m]=t.split(":").map(Number);return h*60+m;}

// ── PROMPTS ───────────────────────────────────────────────────────────────────
const DAILY_PROMPT=(date,raw)=>`You are editor of "The AutoBoros Dispatch" for Az — AI systems builder, Melton VIC, AutoBoros.ai, ADHD+autism, carer for grandparents.
Date: ${date} · Raw input: ---\n${raw}\n---
Return JSON only, no fences:
{"headline":"max 12 words","dek":"one italic subheading","rating":"🔴 Peak Day|🟢 Productive|🟡 Steady|😴 Rest Day","tags":["3-5"],"sessions":[{"time":"Morning/Afternoon/Evening","hed":"headline","body":"2-3 sentences"}],"stats":{"sessions":"n","primary_focus":"label","key_output":"what shipped","notable":"interesting thing"},"pull_quote":"memorable insight"}`;

const WEEKLY_PROMPT=(weekOf,days,schedData,goalsData,tasksData)=>`You are editor of "The AutoBoros Dispatch". Az: AI systems builder, Melton VIC, AutoBoros.ai, ADHD+autism, carer for grandparents, twin daughters. Projects: ECC, Kali Agent, HexStrike, Evermystic/Aurora AI Agency, Ratdog & Skunk, WorldMonitor, Home Lab.

Week of: ${weekOf}

DAILY BRIEFS (from conversation logs):
${days.map(d=>`=== ${d.date} (${d.dayName}) ===\n${d.data?`Headline: ${d.data.headline}\nRating: ${d.data.rating}\nSessions: ${JSON.stringify(d.data.sessions)}\nStats: ${JSON.stringify(d.data.stats)}`:"No brief logged"}`).join('\n\n')}

ENERGY SCHEDULE (planned blocks):
${DAYS.map(day=>{
  const s=schedData[day]||{};
  return `${day}: ${BLOCKS.map(b=>`${b.time}=${ENERGY.find(e=>e.id===(s[b.id]||"sleep"))?.label||"Rest"}`).join(", ")}`;
}).join('\n')}

GOALS SET:
${DAYS.map(d=>`${d}: ${goalsData[d]||"(none)"}`).join('\n')}

TASKS:
${DAYS.map(d=>{const ts=(tasksData[d]||[]);return ts.length?`${d}: ${ts.map(t=>`${t.done?"✓":"○"} ${t.text}${t.project?" ["+t.project+"]":""}`).join(", ")}`:null;}).filter(Boolean).join('\n')||"No tasks logged"}

Return JSON only, no fences:
{"edition_date":"${weekOf}","lead_headline":"big headline max 14 words","lead_dek":"2-sentence italic subheading","lead_body":"4-5 paragraphs genuine newspaper prose — specific, honest, reference real sessions AND whether the energy plan was followed","week_stats":{"systems_built":"n","skills_created":"n","client_work":"summary","peak_day":"day","theme":"one word","planned_vs_actual":"honest assessment"},"intel_flash":"2-3 sentences key external discoveries","client_desk":"2-3 sentences client/business work","pull_quote":"memorable weekly insight","looking_ahead":[{"priority":"01","hed":"title","body":"2 sentences"},{"priority":"02","hed":"title","body":"2 sentences"},{"priority":"03","hed":"title","body":"2 sentences"}],"day_summaries":[{"day":"name","date":"date","hed":"one line","rating":"emoji","detail":"2 sentences","energy_match":"did actual activity match planned energy? yes/partial/no"}]}`;

const SCHED_SUMMARY_PROMPT=(weekOf,schedData,goalsData,tasksData)=>`You are the planning editor for Az's AutoBoros weekly schedule. Az: ADHD+autism, live-in carer for grandparents, AI systems builder, Melton VIC. Non-linear work pattern. Energy-tagged task management critical.

Week of: ${weekOf}

Energy plan:
${DAYS.map(day=>{
  const s=schedData[day]||{};
  return `${day}: ${BLOCKS.map(b=>`${b.time}=${ENERGY.find(e=>e.id===(s[b.id]||"sleep"))?.label||"Rest"}`).join(", ")}`;
}).join('\n')}

Goals: ${DAYS.map(d=>`${d}: ${goalsData[d]||"(none)"}`).join(' | ')}
Tasks: ${DAYS.map(d=>{const ts=(tasksData[d]||[]);return ts.length?`${d}: ${ts.map(t=>`${t.done?"✓":"○"} ${t.text}`).join(", ")}`:null;}).filter(Boolean).join(' | ')||"None"}

Return JSON only, no fences:
{"week_headline":"punchy intention headline max 12 words","week_theme":"one word","opening":"2 paragraphs — what this week's energy pattern signals, honest assessment, what the ADHD/carer context means for this particular layout","daily_intentions":[{"day":"Monday","intention":"one sentence focus","energy":"energy type","watch_out":"one honest risk"}],"priorities":[{"num":"01","hed":"title","body":"2 sentences why this matters + what done looks like"},{"num":"02","hed":"title","body":"2 sentences"},{"num":"03","hed":"title","body":"2 sentences"}],"honest_note":"one paragraph — direct editorial about the pattern showing up, what needs to change, what's working","week_mantra":"one short phrase to carry through the week"}`;

// ── CSS ───────────────────────────────────────────────────────────────────────
const css=`
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;500;600&family=Source+Serif+4:wght@300;400;600&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body{background:#060c18;color:#c0d0e0;font-family:'Inter',sans-serif;font-size:14px;line-height:1.6;}

/* CMD BAR */
.cmd{background:#03080f;border-bottom:1px solid #0a1628;padding:8px 16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;position:sticky;top:0;z-index:60;}
.cmd-brand{font-family:'IBM Plex Mono',monospace;color:#00c8f0;font-size:0.72em;letter-spacing:0.2em;text-transform:uppercase;}
.cmd-meta{font-family:'IBM Plex Mono',monospace;font-size:0.6em;color:#2a4a6a;margin-top:1px;}
.cmd-right{display:flex;align-items:center;gap:4px;flex-wrap:wrap;}
.pill{font-family:'IBM Plex Mono',monospace;font-size:0.58em;padding:2px 8px;border-radius:10px;}
.pill-g{background:#082010;color:#40b060;border:1px solid #104020;}
.pill-a{background:#201200;color:#e09020;border:1px solid #402800;}
.pill-b{background:#080e20;color:#4080c0;border:1px solid #102040;}
.tabs{display:flex;gap:0;flex-wrap:wrap;}
.ctab{font-family:'IBM Plex Mono',monospace;font-size:0.6em;letter-spacing:0.08em;text-transform:uppercase;padding:5px 11px;border:1px solid #0a1628;background:transparent;color:#2a4a6a;cursor:pointer;transition:all 0.12s;}
.ctab:hover{background:#0a1628;color:#6090b0;}
.ctab.on{background:#0a1e3a;color:#00c8f0;border-color:#1a3a60;}
.ctab.sat{color:#f0c030;}
.ctab.sat.on{background:#1a1000;color:#f0c030;border-color:#403010;}

/* SECTION DIVIDER */
.sec-div{display:flex;align-items:center;gap:8px;margin:4px 0 12px;}
.sec-div span{font-family:'IBM Plex Mono',monospace;font-size:0.58em;letter-spacing:0.2em;text-transform:uppercase;color:#1a3a5a;white-space:nowrap;}
.sec-div::before,.sec-div::after{content:'';flex:1;height:1px;background:#0a1628;}

/* MAIN */
.main{max-width:1100px;margin:0 auto;padding:14px;}

/* CARDS */
.card{background:#08111e;border:1px solid #0a1628;border-radius:3px;padding:16px;margin-bottom:12px;}
.card-title{font-family:'IBM Plex Mono',monospace;font-size:0.62em;letter-spacing:0.18em;text-transform:uppercase;color:#00c8f0;margin-bottom:10px;}

/* BUTTONS */
.btn{font-family:'IBM Plex Mono',monospace;font-size:0.65em;letter-spacing:0.08em;text-transform:uppercase;padding:7px 14px;border:none;border-radius:2px;cursor:pointer;transition:all 0.12s;}
.btn-p{background:#0a1e3a;color:#00c8f0;border:1px solid #1a3a60;}
.btn-p:hover{background:#1a3a60;}
.btn-p:disabled{opacity:0.3;cursor:not-allowed;}
.btn-sat{background:linear-gradient(135deg,#1a1000,#2a1a00);color:#f0c030;border:1px solid #403010;font-size:0.72em;padding:9px 18px;}
.btn-sat:hover{opacity:0.85;}
.btn-g{background:transparent;border:1px solid #0a1628;color:#4a6a8a;}
.btn-g:hover{background:#0a1628;}
.btn-row{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-top:10px;}
.loading{display:flex;align-items:center;gap:5px;color:#4a6a8a;font-family:'IBM Plex Mono',monospace;font-size:0.65em;}
.dot{animation:blink 1s infinite;font-size:1.2em;}
@keyframes blink{0%,100%{opacity:0.15;}50%{opacity:1;}}

/* ── REMINDERS ── */
.rem-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px;}
.rem-card{border:1px solid #0a1628;border-radius:3px;padding:14px;background:#080e18;}
.rem-title{font-family:'IBM Plex Mono',monospace;font-size:0.6em;letter-spacing:0.15em;text-transform:uppercase;color:#2a4a6a;margin-bottom:8px;}
.rem-card h3{font-family:'Playfair Display',serif;font-size:1.05em;color:#c0d0e0;margin-bottom:6px;}
.rem-desc{font-size:0.8em;color:#3a5a7a;line-height:1.5;margin-bottom:10px;}
.time-row{display:flex;align-items:center;gap:8px;}
input[type=time]{font-family:'IBM Plex Mono',monospace;font-size:0.9em;padding:5px 8px;border:1px solid #0a1628;border-radius:2px;background:#03080f;color:#c0d0e0;}
.toggle{position:relative;display:inline-block;width:40px;height:22px;cursor:pointer;}
.toggle input{opacity:0;width:0;height:0;}
.tog-sl{position:absolute;inset:0;background:#0a1628;border-radius:22px;transition:0.2s;}
.tog-sl:before{content:'';position:absolute;height:16px;width:16px;left:3px;bottom:3px;background:#2a4a6a;border-radius:50%;transition:0.2s;}
.toggle input:checked+.tog-sl{background:#0a2a4a;}
.toggle input:checked+.tog-sl:before{transform:translateX(18px);background:#00c8f0;}
.notif-banner{background:#1a0e00;border:1px solid #402800;border-radius:3px;padding:12px 14px;margin-bottom:12px;display:flex;align-items:flex-start;gap:10px;font-size:0.83em;color:#906030;}
.alert-ov{position:fixed;inset:0;background:rgba(0,0,0,0.8);z-index:100;display:flex;align-items:center;justify-content:center;padding:16px;}
.alert-box{background:#08111e;border:1px solid #1a3a60;border-radius:4px;max-width:460px;width:100%;overflow:hidden;}
.alert-head{background:#0a1e3a;padding:16px 20px;border-bottom:1px solid #1a3a60;}
.alert-head h2{font-family:'Playfair Display',serif;font-size:1.3em;color:#fff;margin-bottom:3px;}
.alert-head p{font-family:'IBM Plex Mono',monospace;font-size:0.62em;color:#2a4a6a;letter-spacing:0.1em;}
.alert-body{padding:20px;}
.alert-body p{font-size:0.88em;color:#6090b0;line-height:1.6;margin-bottom:14px;}
.alert-actions{display:flex;flex-direction:column;gap:6px;}
.scan-btn{display:block;text-align:center;text-decoration:none;font-family:'IBM Plex Mono',monospace;font-size:0.7em;letter-spacing:0.1em;text-transform:uppercase;padding:10px 16px;border-radius:2px;cursor:pointer;border:none;transition:all 0.12s;}
.scan-primary{background:#00c8f0;color:#03080f;}
.scan-primary:hover{background:#00a0c0;}
.scan-secondary{background:#0a1e3a;color:#00c8f0;border:1px solid #1a3a60;}
.scan-secondary:hover{background:#1a3a60;}
.scan-ghost{background:transparent;border:1px solid #0a1628;color:#3a5a7a;}
.scan-ghost:hover{background:#0a1628;}

/* ── DAILY LOGGER ── */
.day-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin-bottom:14px;}
.day-cell{border:1px solid #0a1628;border-radius:2px;padding:7px 4px;cursor:pointer;text-align:center;transition:all 0.12s;position:relative;}
.day-cell:hover{background:#0a1628;border-color:#1a3a60;}
.day-cell.today{border-color:#1a3a5c;background:#080e20;}
.day-cell.has-data{background:#081408;}
.day-cell.has-data::after{content:'●';position:absolute;top:2px;right:3px;font-size:7px;color:#40b060;}
.day-cell.sel{border-color:#e05050;background:#180808;}
.dc-name{font-family:'IBM Plex Mono',monospace;font-size:0.58em;color:#2a4a6a;text-transform:uppercase;}
.dc-num{font-size:1em;font-weight:600;color:#80a0c0;margin-top:1px;}
.dc-st{font-size:0.65em;margin-top:1px;height:12px;}
textarea{width:100%;min-height:100px;padding:10px;border:1px solid #0a1628;border-radius:2px;font-family:'Source Serif 4',serif;font-size:0.88em;resize:vertical;background:#03080f;color:#c0d0e0;}
textarea:focus{outline:none;border-color:#1a3a60;}
.inp-label{font-family:'IBM Plex Mono',monospace;font-size:0.62em;letter-spacing:0.12em;text-transform:uppercase;color:#2a4a6a;margin-bottom:5px;}
.brief-card{background:#03080f;border:1px solid #0a1628;border-radius:3px;padding:14px;margin-top:12px;}
.brief-kicker{font-family:'IBM Plex Mono',monospace;font-size:0.6em;letter-spacing:0.18em;text-transform:uppercase;color:#e05050;margin-bottom:5px;}
.brief-hed{font-family:'Playfair Display',serif;font-size:1.15em;font-weight:900;color:#fff;margin-bottom:7px;line-height:1.25;}
.tag{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:0.58em;letter-spacing:0.08em;text-transform:uppercase;padding:2px 6px;border-radius:2px;margin:0 3px 4px 0;}
.tag-b{background:#08141e;color:#4080c0;border:1px solid #1a3a60;}
.tag-g{background:#081408;color:#40b060;border:1px solid #104020;}
.stats-row{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:6px;margin-top:10px;}
.stat-box{background:#0a1e3a;padding:9px 10px;border-radius:2px;text-align:center;}
.stat-val{font-family:'IBM Plex Mono',monospace;font-size:1em;font-weight:600;color:#f0c030;}
.stat-lbl{font-size:0.62em;color:#2a4a6a;margin-top:2px;text-transform:uppercase;letter-spacing:0.06em;}

/* ── SCHED GRID ── */
.sched-grid{display:grid;grid-template-columns:80px repeat(7,1fr);gap:1px;background:#0a1628;border:1px solid #0a1628;border-radius:3px;overflow:hidden;margin-bottom:12px;}
.sg-head{background:#03080f;padding:7px 4px;text-align:center;cursor:pointer;}
.sg-head:hover .sg-day{color:#00c8f0;}
.sg-day{font-family:'IBM Plex Mono',monospace;font-size:0.6em;letter-spacing:0.08em;text-transform:uppercase;color:#2a4a6a;transition:color 0.12s;}
.sg-date{font-size:0.7em;color:#1a3a5a;margin-top:1px;}
.sg-date.today{color:#40b060;font-weight:600;}
.sg-lbl{background:#03080f;padding:7px 8px;display:flex;flex-direction:column;justify-content:center;}
.sg-icon{font-size:0.9em;margin-bottom:1px;}
.sg-name{font-family:'IBM Plex Mono',monospace;font-size:0.55em;color:#1a3a5a;text-transform:uppercase;}
.sg-range{font-family:'IBM Plex Mono',monospace;font-size:0.5em;color:#0a2030;}
.sg-cell{padding:3px;cursor:pointer;transition:filter 0.1s;min-height:46px;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:2px;}
.sg-cell:hover{filter:brightness(1.4);}
.sg-cell-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.5em;text-transform:uppercase;text-align:center;line-height:1.3;opacity:0.9;}
.legend{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:12px;}
.leg-item{display:flex;align-items:center;gap:5px;padding:4px 9px;border-radius:2px;border:1px solid #0a1628;cursor:pointer;transition:all 0.12s;background:#080e18;}
.leg-item:hover{border-color:#1a3a60;}
.leg-item.active{border-color:#00c8f0;}
.leg-dot{width:8px;height:8px;border-radius:50%;}
.leg-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.6em;letter-spacing:0.06em;text-transform:uppercase;}

/* ── DAY VIEW ── */
.dv-wrap{display:grid;grid-template-columns:1fr 280px;gap:12px;}
.dv-nav{display:flex;align-items:center;gap:8px;margin-bottom:12px;}
.nav-btn{font-family:'IBM Plex Mono',monospace;font-size:0.65em;padding:4px 9px;border:1px solid #0a1628;background:transparent;color:#2a4a6a;cursor:pointer;border-radius:2px;transition:all 0.12s;}
.nav-btn:hover{color:#00c8f0;border-color:#1a3a60;}
.dv-title{font-family:'Playfair Display',serif;font-size:1.3em;color:#fff;flex:1;text-align:center;}
.dv-date{font-family:'IBM Plex Mono',monospace;font-size:0.62em;color:#1a3a5a;text-align:center;margin-bottom:12px;}
.goal-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.6em;letter-spacing:0.12em;text-transform:uppercase;color:#2a4a6a;margin-bottom:4px;}
.goal-in{width:100%;background:#03080f;border:1px solid #0a1628;color:#c0d0e0;padding:7px 9px;border-radius:2px;font-family:'Inter',sans-serif;font-size:0.85em;outline:none;}
.goal-in:focus{border-color:#1a3a60;}
.blk-row{display:flex;gap:8px;margin-bottom:6px;align-items:stretch;}
.blk-time{min-width:76px;display:flex;flex-direction:column;justify-content:center;}
.blk-icon{font-size:1em;}
.blk-name{font-family:'IBM Plex Mono',monospace;font-size:0.58em;color:#1a3a5a;text-transform:uppercase;}
.blk-range{font-family:'IBM Plex Mono',monospace;font-size:0.54em;color:#0a1e30;}
.blk-en{flex:1;border-radius:2px;padding:9px 11px;cursor:pointer;transition:filter 0.12s;border:1px solid transparent;}
.blk-en:hover{filter:brightness(1.2);}
.blk-en-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.62em;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:3px;}
.blk-in{width:100%;background:transparent;border:none;color:#6080a0;font-size:0.8em;font-family:'Inter',sans-serif;outline:none;}
.blk-in::placeholder{color:#1a2a3a;}
.sb-card{background:#08111e;border:1px solid #0a1628;border-radius:3px;padding:12px;margin-bottom:10px;}
.sb-title{font-family:'IBM Plex Mono',monospace;font-size:0.6em;letter-spacing:0.16em;text-transform:uppercase;color:#00c8f0;margin-bottom:8px;}
.task-item{display:flex;align-items:center;gap:7px;padding:5px 0;border-bottom:1px solid #0a1628;}
.task-item:last-child{border-bottom:none;}
.task-chk{width:13px;height:13px;border:1px solid #1a3a5a;border-radius:2px;cursor:pointer;flex-shrink:0;display:flex;align-items:center;justify-content:center;transition:all 0.12s;}
.task-chk.done{background:#082010;border-color:#40b060;}
.task-txt{flex:1;font-size:0.8em;color:#6090b0;cursor:pointer;}
.task-txt.done{text-decoration:line-through;color:#1a3a5a;}
.task-proj{font-family:'IBM Plex Mono',monospace;font-size:0.56em;padding:1px 5px;background:#0a1628;color:#2a4a6a;border-radius:2px;}
.task-del{font-size:0.75em;color:#1a2a3a;cursor:pointer;padding:2px 3px;transition:all 0.12s;}
.task-del:hover{color:#e05050;}
.add-row{display:flex;gap:5px;margin-top:7px;}
.task-in{flex:1;background:#03080f;border:1px solid #0a1628;color:#c0d0e0;padding:5px 7px;border-radius:2px;font-size:0.78em;font-family:'Inter',sans-serif;outline:none;}
.task-in:focus{border-color:#1a3a60;}
select.proj-sel{background:#03080f;border:1px solid #0a1628;color:#2a4a6a;padding:5px 7px;border-radius:2px;font-size:0.7em;font-family:'IBM Plex Mono',monospace;outline:none;cursor:pointer;}
.stat-sm{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #0a1628;font-size:0.78em;}
.stat-sm:last-child{border-bottom:none;}
.stat-k{color:#1a3a5a;}
.stat-v{font-family:'IBM Plex Mono',monospace;color:#00c8f0;font-weight:600;}

/* ── WEEK VIEW ── */
.week-list{display:flex;flex-direction:column;gap:8px;}
.we{border:1px solid #0a1628;border-radius:3px;overflow:hidden;}
.we-head{background:#080e18;padding:9px 14px;display:flex;justify-content:space-between;align-items:center;cursor:pointer;gap:8px;}
.we-head:hover{background:#0a1628;}
.we-day{font-family:'IBM Plex Mono',monospace;font-size:0.65em;letter-spacing:0.08em;text-transform:uppercase;color:#2a4a6a;}
.we-hed{font-family:'Playfair Display',serif;font-size:0.9em;color:#c0d0e0;}
.we-body{padding:12px 14px;background:#03080f;border-top:1px solid #0a1628;display:none;font-size:0.85em;line-height:1.65;}
.we-body.open{display:block;}

/* ── NEWSPAPER ── */
.paper{background:#faf8f3;color:#1a1a1a;max-width:100%;padding:28px 34px 48px;box-shadow:0 4px 40px rgba(0,0,0,0.4);}
.mast{text-align:center;border-bottom:4px double #222;padding-bottom:10px;margin-bottom:7px;}
.mast-title{font-family:'Playfair Display',serif;font-weight:900;font-size:2.8em;letter-spacing:0.06em;text-transform:uppercase;line-height:1;}
.mast-sub{font-family:'IBM Plex Mono',monospace;font-size:0.65em;letter-spacing:0.16em;color:#666;text-transform:uppercase;margin-top:4px;}
.mast-meta{display:flex;justify-content:space-between;font-family:'IBM Plex Mono',monospace;font-size:0.65em;color:#888;border-top:1px solid #222;border-bottom:1px solid #222;padding:4px 0;margin-top:7px;}
.np-sec{display:flex;align-items:center;gap:9px;margin:20px 0 12px;}
.np-sec span{font-family:'IBM Plex Mono',monospace;font-size:0.62em;font-weight:600;letter-spacing:0.18em;text-transform:uppercase;white-space:nowrap;color:#1a3a5c;}
.np-sec::before,.np-sec::after{content:'';flex:1;height:2px;background:#1a3a5c;}
.np2{display:grid;grid-template-columns:2fr 1fr;gap:0;}
.np3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:0;}
.npc{padding:0 14px;}
.npc:first-child{padding-left:0;}
.npc:last-child{padding-right:0;}
.npc-b{border-left:1px solid #bbb;}
.np-kicker{font-family:'IBM Plex Mono',monospace;font-size:0.6em;letter-spacing:0.2em;text-transform:uppercase;color:#c0392b;margin-bottom:3px;}
.np-hed-xl{font-family:'Playfair Display',serif;font-weight:900;font-size:1.9em;line-height:1.1;margin-bottom:7px;}
.np-hed-sm{font-family:'Playfair Display',serif;font-weight:700;font-size:1.05em;line-height:1.25;margin-bottom:4px;}
.np-dek{font-style:italic;color:#555;font-size:0.86em;margin-bottom:7px;line-height:1.4;}
.np-byline{font-family:'IBM Plex Mono',monospace;font-size:0.6em;color:#888;text-transform:uppercase;border-top:1px solid #ccc;padding-top:4px;margin-bottom:8px;}
.np-body{font-size:0.87em;text-align:justify;line-height:1.65;}
.np-body p{margin-bottom:7px;}
.np-pull{border-top:3px solid #1a1a1a;border-bottom:3px solid #1a1a1a;padding:9px 0;margin:12px 0;font-family:'Playfair Display',serif;font-size:1em;font-style:italic;color:#1a3a5c;line-height:1.4;}
.np-sc{background:#1a3a5c;color:#e8e4d9;padding:12px 14px;margin-bottom:12px;}
.np-sc-title{font-family:'IBM Plex Mono',monospace;font-size:0.6em;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:7px;opacity:0.6;}
.np-sc-row{display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.08);padding:4px 0;font-size:0.8em;}
.np-sc-row:last-child{border-bottom:none;}
.np-sc-val{font-family:'IBM Plex Mono',monospace;font-weight:600;color:#f0d080;}
.np-hr{border:none;border-top:3px double #999;margin:16px 0;}
.np-thin{border:none;border-top:1px solid #ccc;margin:10px 0;}
.np-foot{border-top:4px double #222;margin-top:26px;padding-top:9px;display:flex;justify-content:space-between;font-family:'IBM Plex Mono',monospace;font-size:0.6em;color:#888;}

/* SCHED BLOCK IN EDITION */
.en-row{display:flex;gap:3px;margin-bottom:4px;flex-wrap:wrap;}
.en-pip{font-family:'IBM Plex Mono',monospace;font-size:0.55em;padding:1px 5px;border-radius:2px;}

/* SUMMARY */
.sum-hed{font-family:'Playfair Display',serif;font-size:1.25em;color:#fff;margin-bottom:6px;}
.sum-body{font-size:0.86em;color:#6090b0;line-height:1.7;}
.sum-body p{margin-bottom:7px;}
.pri-item{display:flex;gap:9px;padding:9px 0;border-bottom:1px solid #0a1628;}
.pri-item:last-child{border-bottom:none;}
.pri-num{font-family:'Playfair Display',serif;font-size:1.5em;color:#1a3a5a;min-width:26px;line-height:1;}
.pri-hed{font-weight:600;color:#c0d0e0;margin-bottom:2px;font-size:0.88em;}
.pri-body{font-size:0.78em;color:#3a5a7a;line-height:1.5;}
.di-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px;}
.di-card{background:#08111e;border:1px solid #0a1628;border-radius:3px;padding:11px;}
.di-day{font-family:'IBM Plex Mono',monospace;font-size:0.62em;letter-spacing:0.1em;text-transform:uppercase;color:#00c8f0;margin-bottom:3px;}
.di-int{font-weight:600;font-size:0.86em;color:#c0d0e0;margin-bottom:3px;}
.di-warn{font-size:0.76em;color:#8a5020;border-left:2px solid #402010;padding-left:7px;margin-top:4px;}

@media(max-width:680px){.np2,.np3{grid-template-columns:1fr;}.npc-b{border-left:none;border-top:1px solid #bbb;padding-top:12px;margin-top:10px;}.mast-title{font-size:2em;}.dv-wrap{grid-template-columns:1fr;}.rem-grid{grid-template-columns:1fr;}.di-grid{grid-template-columns:1fr;}.sched-grid{grid-template-columns:60px repeat(7,1fr);}}
`;

// ── APP ───────────────────────────────────────────────────────────────────────
export default function App(){
  const today     = new Date();
  const isSat     = today.getDay()===6;
  const todayFmt  = fmt(today);
  const mon       = weekStart();
  const currentWk = weekKey(today);
  const wkDates   = weekDates(currentWk);

  // view
  const [view,setView]   = useState("grid");
  const [notifPerm,setNotifPerm] = useState("default");
  const [alert,setAlert] = useState(null);

  // dispatch state
  const [selDate,setSelDate]         = useState(todayFmt);
  const [rawInput,setRawInput]       = useState("");
  const [loading,setLoading]         = useState(false);
  const [dailyData,setDailyData]     = useState({});
  const [weeklyEd,setWeeklyEd]       = useState(null);
  const [weeklyLoading,setWkLoad]    = useState(false);
  const [expanded,setExpanded]       = useState({});

  // scheduler state
  const [selDayIdx,setSelDayIdx]     = useState(today.getDay()===0?6:today.getDay()-1);
  const [schedule,setSchedule]       = useState(DEFAULT_SCHED);
  const [goals,setGoals]             = useState({});
  const [tasks,setTasks]             = useState({});
  const [activeLeg,setActiveLeg]     = useState(null);
  const [newTask,setNewTask]         = useState("");
  const [newProj,setNewProj]         = useState("");
  const [schedSum,setSchedSum]       = useState(null);
  const [schedSumLoad,setSchedSumL]  = useState(false);

  const [settings,setSettings] = useState({dailyEnabled:true,dailyTime:"21:00",satEnabled:true,satTime:"09:00"});
  const timerRef = useRef(null);

  // ── LOAD STORAGE ──
  useEffect(()=>{
    async function load(){
      try{const r=await window.storage.get("sched:schedule");if(r)setSchedule(JSON.parse(r.value));}catch{}
      try{const r=await window.storage.get("sched:goals");if(r)setGoals(JSON.parse(r.value));}catch{}
      try{const r=await window.storage.get("sched:tasks");if(r)setTasks(JSON.parse(r.value));}catch{}
      try{const r=await window.storage.get("sched:summary:"+currentWk);if(r)setSchedSum(JSON.parse(r.value));}catch{}
      try{
        const keys=await window.storage.list("dispatch:day:");
        const loaded={};
        for(const k of(keys?.keys||[])){
          try{const r=await window.storage.get(k);if(r)loaded[k.split("dispatch:day:").pop()]=JSON.parse(r.value);}catch{}
        }
        setDailyData(loaded);
      }catch{}
      try{const r=await window.storage.get("dispatch:weekly:"+currentWk);if(r)setWeeklyEd(JSON.parse(r.value));}catch{}
      try{const r=await window.storage.get("dispatch:settings");if(r)setSettings(JSON.parse(r.value));}catch{}
      if("Notification" in window)setNotifPerm(Notification.permission);
    }
    load();
  },[]);

  // ── REMINDER TIMER ──
  useEffect(()=>{
    function check(){
      const now=new Date(), mins=now.getHours()*60+now.getMinutes(), isSaturday=now.getDay()===6;
      if(settings.dailyEnabled&&!isSaturday&&mins===timeToMins(settings.dailyTime)) triggerAlert("daily");
      if(settings.satEnabled&&isSaturday&&mins===timeToMins(settings.satTime)) triggerAlert("saturday");
    }
    timerRef.current=setInterval(check,60000);
    return()=>clearInterval(timerRef.current);
  },[settings]);

  function triggerAlert(type){
    setAlert(type);
    if(notifPerm==="granted") new Notification(type==="daily"?"⬡ Dispatch — Daily Scan":"📰 Dispatch — Saturday Edition",{body:type==="daily"?"Time to log today":"Time to compile your edition"});
  }

  // ── SAVE HELPERS ──
  async function saveSched(s){setSchedule(s);try{await window.storage.set("sched:schedule",JSON.stringify(s));}catch{}}
  async function saveGoals(g){setGoals(g);try{await window.storage.set("sched:goals",JSON.stringify(g));}catch{}}
  async function saveTasks(t){setTasks(t);try{await window.storage.set("sched:tasks",JSON.stringify(t));}catch{}}
  async function saveSettings(s){setSettings(s);try{await window.storage.set("dispatch:settings",JSON.stringify(s));}catch{}}

  // ── SCHEDULER ──
  function cycleEnergy(day,block){
    const curr=schedule[day]?.[block]||"sleep";
    const idx=ENERGY.findIndex(e=>e.id===curr);
    saveSched({...schedule,[day]:{...(schedule[day]||{}),[block]:ENERGY[(idx+1)%ENERGY.length].id}});
  }
  function paintCell(day,block){
    if(!activeLeg){cycleEnergy(day,block);return;}
    saveSched({...schedule,[day]:{...(schedule[day]||{}),[block]:activeLeg}});
  }
  function addTask(day){
    if(!newTask.trim())return;
    const t=[...(tasks[day]||[]),{id:Date.now(),text:newTask.trim(),project:newProj,done:false}];
    saveTasks({...tasks,[day]:t}); setNewTask(""); setNewProj("");
  }
  function toggleTask(day,id){saveTasks({...tasks,[day]:(tasks[day]||[]).map(t=>t.id===id?{...t,done:!t.done}:t)});}
  function delTask(day,id){saveTasks({...tasks,[day]:(tasks[day]||[]).filter(t=>t.id!==id)});}

  // ── API CALLS ──
  async function processDay(){
    if(!rawInput.trim())return;
    setLoading(true);
    try{
      const res=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({model:MODEL,max_tokens:1500,messages:[{role:"user",content:DAILY_PROMPT(selDate,rawInput)}]})});
      const data=await res.json();
      const parsed=JSON.parse((data.content?.find(b=>b.type==="text")?.text||"").replace(/```json|```/g,"").trim());
      const updated={...dailyData,[selDate]:parsed};
      setDailyData(updated); setRawInput("");
      await window.storage.set("dispatch:day:"+selDate,JSON.stringify(parsed));
    }catch(e){console.error(e);}
    setLoading(false);
  }

  async function generateWeekly(){
    setWkLoad(true);
    const days=wkDates.map(d=>({date:fmt(d),dayName:DAYS[d.getDay()===0?6:d.getDay()-1],data:dailyData[fmt(d)]||null}));
    try{
      const res=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({model:MODEL,max_tokens:3000,messages:[{role:"user",content:WEEKLY_PROMPT(currentWk,days,schedule,goals,tasks)}]})});
      const data=await res.json();
      const parsed=JSON.parse((data.content?.find(b=>b.type==="text")?.text||"").replace(/```json|```/g,"").trim());
      setWeeklyEd(parsed); setView("edition");
      await window.storage.set("dispatch:weekly:"+currentWk,JSON.stringify(parsed));
    }catch(e){console.error(e);}
    setWkLoad(false);
  }

  async function generateSchedSum(){
    setSchedSumL(true);
    try{
      const res=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({model:MODEL,max_tokens:2000,messages:[{role:"user",content:SCHED_SUMMARY_PROMPT(currentWk,schedule,goals,tasks)}]})});
      const data=await res.json();
      const parsed=JSON.parse((data.content?.find(b=>b.type==="text")?.text||"").replace(/```json|```/g,"").trim());
      setSchedSum(parsed);
      await window.storage.set("sched:summary:"+currentWk,JSON.stringify(parsed));
    }catch(e){console.error(e);}
    setSchedSumL(false);
  }

  // ── DERIVED ──
  const selDay   = DAYS[selDayIdx];
  const selDate2 = wkDates[selDayIdx];
  const selData  = dailyData[selDate];
  const daysWithData = wkDates.filter(d=>dailyData[fmt(d)]);
  const totalTasks=DAYS.reduce((a,d)=>a+(tasks[d]||[]).length,0);
  const doneTasks =DAYS.reduce((a,d)=>a+(tasks[d]||[]).filter(t=>t.done).length,0);
  const deepDays  =DAYS.filter(d=>Object.values(schedule[d]||{}).includes("red")).length;
  const clientDays=DAYS.filter(d=>Object.values(schedule[d]||{}).includes("client")).length;

  // ── RENDER ────────────────────────────────────────────────────────────────
  return(<>
    <style>{css}</style>

    {/* ALERT */}
    {alert&&(
      <div className="alert-ov" onClick={()=>setAlert(null)}>
        <div className="alert-box" onClick={e=>e.stopPropagation()}>
          <div className="alert-head">
            <h2>{alert==="daily"?"⬡ Daily Scan Time":"📰 Saturday Edition"}</h2>
            <p>{alert==="daily"?"TIME TO LOG TODAY'S SESSIONS":"TIME TO COMPILE YOUR WEEKLY NEWSPAPER"}</p>
          </div>
          <div className="alert-body">
            <p>{alert==="daily"?"Ask Claude to scan your conversations and return a brief block. Takes 30 seconds.":"Ask Claude to scan the full week. Paste the result, then compile your newspaper."}</p>
            <div className="alert-actions">
              <a className="scan-btn scan-primary" href={alert==="daily"?SCAN_URL:SAT_URL} target="_blank" rel="noopener">Open Claude → {alert==="daily"?"Scan Today":"Scan This Week"} ↗</a>
              <button className="scan-btn scan-secondary" onClick={()=>{setAlert(null);setView(alert==="daily"?"logger":"weekview");}}>Paste manually</button>
              <button className="scan-btn scan-ghost" onClick={()=>setAlert(null)}>Dismiss</button>
            </div>
          </div>
        </div>
      </div>
    )}

    {/* CMD BAR */}
    <div className="cmd">
      <div>
        <div className="cmd-brand">⬡ AutoBoros OS</div>
        <div className="cmd-meta">Week of {currentWk} · {daysWithData.length}/7 logged · {doneTasks}/{totalTasks} tasks</div>
      </div>
      <div className="cmd-right">
        <span className={`pill ${notifPerm==="granted"?"pill-g":notifPerm==="denied"?"pill-a":"pill-b"}`}>
          {notifPerm==="granted"?"● Notifs ON":notifPerm==="denied"?"⚠ Notifs blocked":"○ Notifs off"}
        </span>
        {isSat&&<span className="pill pill-a">📰 Saturday</span>}
        <div className="tabs">
          <div className="sec-div" style={{display:"inline-flex",border:"none",margin:0,gap:0}}>
            <button className={`ctab ${view==="grid"?"on":""}`}    onClick={()=>setView("grid")}>Grid</button>
            <button className={`ctab ${view==="dayview"?"on":""}`} onClick={()=>setView("dayview")}>Day</button>
            <button className={`ctab ${view==="schedsum"?"on":""}`}onClick={()=>setView("schedsum")}>Plan</button>
            <button className={`ctab ${view==="reminders"?"on":""}`}onClick={()=>setView("reminders")}>⏰</button>
            <button className={`ctab ${view==="logger"?"on":""}`}  onClick={()=>setView("logger")}>Log</button>
            <button className={`ctab ${view==="weekview"?"on":""}`}onClick={()=>setView("weekview")}>Week</button>
            <button className={`ctab sat ${view==="edition"?"on":""}`} onClick={()=>setView("edition")}>📰 Edition</button>
          </div>
        </div>
      </div>
    </div>

    <div className="main">

    {/* ── SCHEDULER GRID ── */}
    {view==="grid"&&<>
      <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.6em",letterSpacing:"0.12em",textTransform:"uppercase",color:"#1a3a5a",marginBottom:"6px"}}>
        {activeLeg?`Painting: ${ENERGY.find(e=>e.id===activeLeg)?.label} — click cells · click again to deselect`:"Click cell to cycle · or select energy to paint multiple"}
      </div>
      <div className="legend">
        {ENERGY.map(e=>(
          <div key={e.id} className={`leg-item ${activeLeg===e.id?"active":""}`}
            style={{background:activeLeg===e.id?e.bg:"#080e18"}}
            onClick={()=>setActiveLeg(activeLeg===e.id?null:e.id)}>
            <div className="leg-dot" style={{background:e.color}}/>
            <span className="leg-lbl" style={{color:activeLeg===e.id?e.color:"#2a4a6a"}}>{e.label}</span>
          </div>
        ))}
      </div>
      <div className="sched-grid">
        <div className="sg-lbl"/>
        {DAYS.map((d,i)=>{
          const date=wkDates[i]; const isToday=fmt(date)===todayFmt;
          return(
            <div key={d} className="sg-head" onClick={()=>{setSelDayIdx(i);setView("dayview");}}>
              <div className="sg-day">{SHORT[i]}</div>
              <div className={`sg-date ${isToday?"today":""}`}>{date.getDate()} {MONTHS[date.getMonth()]}</div>
            </div>
          );
        })}
        {BLOCKS.map(blk=>(
          [<div key={blk.id+"l"} className="sg-lbl">
            <div className="sg-icon">{blk.icon}</div>
            <div className="sg-name">{blk.label}</div>
            <div className="sg-range">{blk.time}</div>
          </div>,
          ...DAYS.map(d=>{
            const eId=schedule[d]?.[blk.id]||"sleep";
            const en=ENERGY.find(e=>e.id===eId)||ENERGY[3];
            return(
              <div key={d+blk.id} className="sg-cell" style={{background:en.bg}} onClick={()=>paintCell(d,blk.id)}>
                <div className="sg-cell-lbl" style={{color:en.color}}>{en.label.split(" ")[0]}</div>
              </div>
            );
          })]
        ))}
      </div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(150px,1fr))",gap:"6px"}}>
        {[["Deep Work Days",deepDays],["Client Days",clientDays],["Tasks Done",`${doneTasks}/${totalTasks}`],["Days Logged",`${daysWithData.length}/7`]].map(([k,v])=>(
          <div key={k} style={{background:"#08111e",border:"1px solid #0a1628",borderRadius:"3px",padding:"9px 11px",display:"flex",justifyContent:"space-between",alignItems:"center"}}>
            <span style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.58em",color:"#1a3a5a",textTransform:"uppercase"}}>{k}</span>
            <span style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.88em",color:"#00c8f0",fontWeight:"600"}}>{v}</span>
          </div>
        ))}
      </div>
    </>}

    {/* ── DAY VIEW ── */}
    {view==="dayview"&&(
      <div className="dv-wrap">
        <div>
          <div className="dv-nav">
            <button className="nav-btn" onClick={()=>setSelDayIdx((selDayIdx+6)%7)}>← {SHORT[(selDayIdx+6)%7]}</button>
            <div style={{flex:1,textAlign:"center"}}>
              <div className="dv-title">{selDay}</div>
              <div className="dv-date">{selDate2.getDate()} {MONTHS[selDate2.getMonth()]} {selDate2.getFullYear()}
                {fmt(selDate2)===todayFmt&&<span style={{color:"#40b060",marginLeft:"8px",fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.85em"}}>TODAY</span>}
              </div>
            </div>
            <button className="nav-btn" onClick={()=>setSelDayIdx((selDayIdx+1)%7)}>{SHORT[(selDayIdx+1)%7]} →</button>
          </div>
          <div style={{marginBottom:"10px"}}>
            <div className="goal-lbl">Day Focus</div>
            <input className="goal-in" placeholder="What makes today a win?"
              value={goals[selDay]||""} onChange={e=>saveGoals({...goals,[selDay]:e.target.value})}/>
          </div>
          {BLOCKS.map(blk=>{
            const eId=schedule[selDay]?.[blk.id]||"sleep";
            const en=ENERGY.find(e=>e.id===eId)||ENERGY[3];
            const noteKey=selDay+"_"+blk.id;
            return(
              <div key={blk.id} className="blk-row">
                <div className="blk-time">
                  <div className="blk-icon">{blk.icon}</div>
                  <div className="blk-name">{blk.label}</div>
                  <div className="blk-range">{blk.time}</div>
                </div>
                <div className="blk-en" style={{background:en.bg,borderColor:en.color+"44"}} onClick={()=>cycleEnergy(selDay,blk.id)}>
                  <div className="blk-en-lbl" style={{color:en.color}}>{en.label}</div>
                  <input className="blk-in" placeholder="Block notes…" onClick={e=>e.stopPropagation()}
                    value={goals[noteKey]||""} onChange={e=>saveGoals({...goals,[noteKey]:e.target.value})}/>
                </div>
              </div>
            );
          })}
        </div>
        <div>
          <div className="sb-card">
            <div className="sb-title">Tasks — {selDay}</div>
            {(tasks[selDay]||[]).map(t=>(
              <div key={t.id} className="task-item">
                <div className={`task-chk ${t.done?"done":""}`} onClick={()=>toggleTask(selDay,t.id)}>
                  {t.done&&<span style={{color:"#40b060",fontSize:"0.75em"}}>✓</span>}
                </div>
                <span className={`task-txt ${t.done?"done":""}`} onClick={()=>toggleTask(selDay,t.id)}>{t.text}</span>
                {t.project&&<span className="task-proj">{t.project}</span>}
                <span className="task-del" onClick={()=>delTask(selDay,t.id)}>✕</span>
              </div>
            ))}
            {!(tasks[selDay]||[]).length&&<div style={{color:"#1a3a5a",fontSize:"0.78em",fontStyle:"italic",padding:"5px 0"}}>No tasks</div>}
            <div className="add-row">
              <input className="task-in" placeholder="Add task…" value={newTask} onChange={e=>setNewTask(e.target.value)} onKeyDown={e=>e.key==="Enter"&&addTask(selDay)}/>
              <select className="proj-sel" value={newProj} onChange={e=>setNewProj(e.target.value)}>
                <option value="">Tag…</option>
                {PROJECTS.map(p=><option key={p} value={p}>{p}</option>)}
              </select>
              <button className="btn btn-p" onClick={()=>addTask(selDay)}>+</button>
            </div>
          </div>
          <div className="sb-card">
            <div className="sb-title">Week Stats</div>
            {[["Tasks done",`${doneTasks}/${totalTasks}`],["Deep work days",deepDays],["Client days",clientDays],["Days logged",`${daysWithData.length}/7`]].map(([k,v])=>(
              <div key={k} className="stat-sm"><span className="stat-k">{k}</span><span className="stat-v">{v}</span></div>
            ))}
          </div>
          <div className="sb-card">
            <div className="sb-title">Energy Key</div>
            {ENERGY.map(e=>(
              <div key={e.id} style={{display:"flex",gap:"7px",padding:"4px 0",borderBottom:"1px solid #0a1628",alignItems:"flex-start"}}>
                <div style={{width:"7px",height:"7px",borderRadius:"50%",background:e.color,marginTop:"5px",flexShrink:0}}/>
                <div>
                  <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.6em",color:e.color}}>{e.label}</div>
                  <div style={{fontSize:"0.7em",color:"#1a3a5a"}}>{e.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )}

    {/* ── SCHEDULE SUMMARY ── */}
    {view==="schedsum"&&(
      <div>
        <div className="btn-row" style={{marginBottom:"14px"}}>
          <button className="btn btn-p" disabled={schedSumLoad} onClick={generateSchedSum}>
            {schedSumLoad?<><span className="dot">·</span><span className="dot" style={{animationDelay:"0.3s"}}>·</span><span className="dot" style={{animationDelay:"0.6s"}}>·</span> Generating…</>:"⬡ Generate Week Plan"}
          </button>
          {schedSum&&<button className="btn btn-g" onClick={generateSchedSum}>↻</button>}
          <span style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.6em",color:"#1a3a5a"}}>Based on your energy map, goals, and tasks · feeds into Saturday edition</span>
        </div>
        {!schedSum?(
          <div style={{textAlign:"center",padding:"50px 20px",color:"#1a3a5a"}}>
            <div style={{fontSize:"0.8em",fontFamily:"'IBM Plex Mono',monospace",letterSpacing:"0.1em",textTransform:"uppercase",marginBottom:"8px"}}>Set your energy schedule in Grid view, then generate</div>
          </div>
        ):(
          <>
            <div className="card">
              <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.6em",letterSpacing:"0.18em",textTransform:"uppercase",color:"#00c8f0",marginBottom:"5px"}}>Week of {currentWk} · {schedSum.week_theme}</div>
              <div className="sum-hed">{schedSum.week_headline}</div>
              {schedSum.week_mantra&&<div style={{fontFamily:"'Playfair Display',serif",fontStyle:"italic",color:"#f0c030",fontSize:"0.95em",margin:"7px 0 10px",borderLeft:"3px solid #302000",paddingLeft:"10px"}}>{schedSum.week_mantra}</div>}
              <div className="sum-body" dangerouslySetInnerHTML={{__html:(schedSum.opening||"").replace(/\n\n/g,"</p><p>").replace(/^/,"<p>").replace(/$/,"</p>")}}/>
            </div>
            <div className="di-grid">
              {(schedSum.daily_intentions||[]).map(di=>(
                <div key={di.day} className="di-card">
                  <div className="di-day">{di.day}</div>
                  <div className="di-int">{di.intention}</div>
                  {di.watch_out&&<div className="di-warn">⚠ {di.watch_out}</div>}
                </div>
              ))}
            </div>
            <div className="card">
              <div className="card-title">Priorities</div>
              {(schedSum.priorities||[]).map(p=>(
                <div key={p.num} className="pri-item">
                  <div className="pri-num">{p.num}</div>
                  <div><div className="pri-hed">{p.hed}</div><div className="pri-body">{p.body}</div></div>
                </div>
              ))}
            </div>
            {schedSum.honest_note&&(
              <div style={{background:"#081408",border:"1px solid #103010",borderRadius:"3px",padding:"14px"}}>
                <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.6em",letterSpacing:"0.16em",textTransform:"uppercase",color:"#40b060",marginBottom:"6px"}}>Honest Note</div>
                <div style={{fontSize:"0.84em",color:"#4a7a5a",lineHeight:"1.7"}}>{schedSum.honest_note}</div>
              </div>
            )}
          </>
        )}
      </div>
    )}

    {/* ── REMINDERS ── */}
    {view==="reminders"&&(
      <div>
        {notifPerm==="default"&&(
          <div className="notif-banner">
            <span>🔔</span>
            <div style={{flex:1}}>Enable browser notifications to be reminded even when this tab is in the background.</div>
            <button className="btn btn-p" onClick={async()=>{const p=await Notification.requestPermission();setNotifPerm(p);}}>Allow</button>
          </div>
        )}
        {notifPerm==="denied"&&<div className="notif-banner"><span>⚠️</span><span>Notifications blocked. Allow in browser settings → lock icon → Notifications.</span></div>}
        <div className="rem-grid">
          {[{key:"daily",title:"Daily Brief",desc:"Fires Mon–Fri at your set time. Alert opens Claude with a pre-written scan prompt.",tKey:"dailyTime",eKey:"dailyEnabled"},
            {key:"saturday",title:"Saturday Edition",desc:"Fires every Saturday morning. Prompts full week scan and newspaper compilation.",tKey:"satTime",eKey:"satEnabled"}].map(r=>(
            <div key={r.key} className="rem-card">
              <div className="rem-title">{r.key==="daily"?"⬡ Daily":"📰 Saturday"}</div>
              <h3>{r.title}</h3>
              <div className="rem-desc">{r.desc}</div>
              <div className="time-row">
                <input type="time" value={settings[r.tKey]} onChange={e=>saveSettings({...settings,[r.tKey]:e.target.value})}/>
                <label className="toggle"><input type="checkbox" checked={settings[r.eKey]} onChange={e=>saveSettings({...settings,[r.eKey]:e.target.checked})}/><span className="tog-sl"/></label>
                <span style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.65em",color:settings[r.eKey]?"#40b060":"#2a4a6a"}}>{settings[r.eKey]?"ON":"OFF"}</span>
              </div>
            </div>
          ))}
        </div>
        <div className="btn-row">
          <button className="btn btn-p" onClick={()=>setAlert("daily")}>Preview Daily Alert</button>
          <button className="btn btn-p" onClick={()=>setAlert("saturday")}>Preview Saturday Alert</button>
          <a className="btn btn-g" style={{textDecoration:"none"}} href={SCAN_URL} target="_blank" rel="noopener">Scan Today ↗</a>
        </div>
      </div>
    )}

    {/* ── LOGGER ── */}
    {view==="logger"&&(
      <div className="card">
        <div className="card-title">Daily Brief Logger</div>
        <div className="day-grid">
          {wkDates.map((d,i)=>{
            const dk=fmt(d), isToday=dk===todayFmt, hasDat=!!dailyData[dk], isSel=dk===selDate;
            return(
              <div key={dk} className={`day-cell ${isToday?"today":""} ${hasDat?"has-data":""} ${isSel?"sel":""}`} onClick={()=>setSelDate(dk)}>
                <div className="dc-name">{SHORT[i]}</div>
                <div className="dc-num">{d.getDate()}</div>
                <div className="dc-st">{hasDat&&<span style={{color:"#40b060"}}>{dailyData[dk]?.rating?.split(" ")[0]}</span>}</div>
              </div>
            );
          })}
        </div>
        <div style={{background:"#03080f",borderRadius:"2px",padding:"7px 10px",marginBottom:"12px",fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.65em",color:"#2a4a6a",display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:"6px"}}>
          <span>Selected: <strong style={{color:"#00c8f0"}}>{fmtDisplay(new Date(selDate+"T12:00:00"))}</strong>
            {selData&&<span style={{marginLeft:"10px",color:"#40b060"}}>✓ {selData.headline}</span>}
          </span>
          <a href={SCAN_URL} target="_blank" rel="noopener" style={{color:"#2a4a6a",textDecoration:"none",fontSize:"0.9em"}}>Open Claude to scan ↗</a>
        </div>
        {!selData?(
          <>
            <div className="inp-label">Paste brief block from Claude</div>
            <textarea value={rawInput} onChange={e=>setRawInput(e.target.value)}
              placeholder="Paste the output from your Claude scan here, or type your own session notes."/>
            <div className="btn-row">
              <button className="btn btn-p" disabled={loading||!rawInput.trim()} onClick={processDay}>
                {loading?<><span className="dot">·</span><span className="dot" style={{animationDelay:"0.3s"}}>·</span><span className="dot" style={{animationDelay:"0.6s"}}>·</span> Processing…</>:"Process into Brief"}
              </button>
            </div>
          </>
        ):(
          <div className="brief-card">
            <div className="brief-kicker">{DAYS[new Date(selDate+"T12:00:00").getDay()===0?6:new Date(selDate+"T12:00:00").getDay()-1]} · Daily Brief</div>
            <div className="brief-hed">{selData.headline}</div>
            <div style={{marginBottom:"8px"}}>{(selData.tags||[]).map(t=><span key={t} className="tag tag-b">{t}</span>)}<span className="tag tag-g">{selData.rating}</span></div>
            {(selData.sessions||[]).map((s,i)=>(
              <div key={i} style={{marginBottom:"10px",paddingBottom:"8px",borderBottom:"1px solid #0a1628"}}>
                <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.6em",color:"#e05050",textTransform:"uppercase",letterSpacing:"0.08em"}}>{s.time}</div>
                <div style={{fontFamily:"'Playfair Display',serif",fontWeight:"700",fontSize:"0.95em",color:"#c0d0e0",margin:"2px 0"}}>{s.hed}</div>
                <div style={{fontSize:"0.84em",color:"#4a6a8a",lineHeight:"1.65"}}>{s.body}</div>
              </div>
            ))}
            {selData.pull_quote&&<div style={{borderTop:"2px solid #0a1628",borderBottom:"2px solid #0a1628",padding:"8px 0",margin:"10px 0",fontStyle:"italic",color:"#4a6a8a",fontSize:"0.88em"}}>{selData.pull_quote}</div>}
            <div className="stats-row">{Object.entries(selData.stats||{}).map(([k,v])=>(
              <div key={k} className="stat-box"><div className="stat-val">{v}</div><div className="stat-lbl">{k.replace(/_/g," ")}</div></div>
            ))}</div>
            <div className="btn-row" style={{marginTop:"10px"}}>
              <button className="btn btn-g" onClick={async()=>{const u={...dailyData};delete u[selDate];setDailyData(u);try{await window.storage.delete("dispatch:day:"+selDate);}catch{}}}>✕ Clear</button>
            </div>
          </div>
        )}
      </div>
    )}

    {/* ── WEEK VIEW ── */}
    {view==="weekview"&&(
      <div className="card">
        <div className="card-title">{currentWk} · {daysWithData.length}/7 days logged</div>
        <div className="btn-row" style={{marginBottom:"14px"}}>
          <button className="btn btn-sat" disabled={weeklyLoading||daysWithData.length===0} onClick={generateWeekly}>
            {weeklyLoading?<><span className="dot">·</span><span className="dot" style={{animationDelay:"0.3s"}}>·</span><span className="dot" style={{animationDelay:"0.6s"}}>·</span> Compiling…</>:"📰 Compile Saturday Edition"}
          </button>
          <a className="btn btn-g" style={{textDecoration:"none"}} href={SAT_URL} target="_blank" rel="noopener">Scan week ↗</a>
          {weeklyEd&&<button className="btn btn-p" onClick={()=>setView("edition")}>View Edition →</button>}
        </div>
        <div className="week-list">
          {wkDates.map((d,i)=>{
            const dk=fmt(d), dd=dailyData[dk], isExp=expanded[dk];
            // scheduler data for this day
            const dayName=DAYS[i];
            const sched=schedule[dayName]||{};
            return(
              <div key={dk} className="we">
                <div className="we-head" onClick={()=>setExpanded(p=>({...p,[dk]:!p[dk]}))}>
                  <div>
                    <div className="we-day">{DAYS[i]} {d.getDate()} {MONTHS[d.getMonth()]}</div>
                    <div className="we-hed">{dd?dd.headline:<em style={{color:"#1a3a5a",fontSize:"0.9em"}}>No brief — {goals[dayName]||"no focus set"}</em>}</div>
                    <div className="en-row" style={{marginTop:"3px"}}>
                      {BLOCKS.map(blk=>{
                        const en=ENERGY.find(e=>e.id===(sched[blk.id]||"sleep"))||ENERGY[3];
                        return <span key={blk.id} className="en-pip" style={{background:en.bg,color:en.color}}>{blk.icon}</span>;
                      })}
                    </div>
                  </div>
                  <div style={{display:"flex",gap:"6px",alignItems:"center"}}>
                    {dd&&<span style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.65em",background:"#0a1e3a",color:"#00c8f0",padding:"2px 7px",borderRadius:"2px"}}>{dd.rating}</span>}
                    <span style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.65em",color:"#1a3a5a"}}>{isExp?"▲":"▼"}</span>
                  </div>
                </div>
                {isExp&&dd&&(
                  <div className="we-body open">
                    {(dd.sessions||[]).map((s,j)=>(
                      <div key={j} style={{marginBottom:"9px"}}>
                        <span style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.6em",color:"#e05050",textTransform:"uppercase"}}>{s.time} · </span>
                        <strong style={{color:"#c0d0e0"}}>{s.hed}</strong>
                        <div style={{color:"#4a6a8a",marginTop:"3px",fontSize:"0.88em"}}>{s.body}</div>
                      </div>
                    ))}
                    {dd.pull_quote&&<div style={{borderLeft:"3px solid #1a3a60",paddingLeft:"9px",fontStyle:"italic",color:"#2a5a8a",marginTop:"8px",fontSize:"0.88em"}}>{dd.pull_quote}</div>}
                    {(tasks[dayName]||[]).length>0&&(
                      <div style={{marginTop:"10px",paddingTop:"8px",borderTop:"1px solid #0a1628"}}>
                        <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.58em",color:"#1a3a5a",textTransform:"uppercase",marginBottom:"5px"}}>Tasks</div>
                        {(tasks[dayName]||[]).map(t=>(
                          <div key={t.id} style={{fontSize:"0.8em",color:t.done?"#1a4a2a":"#3a5a7a",display:"flex",gap:"6px",marginBottom:"3px"}}>
                            <span>{t.done?"✓":"○"}</span><span style={{textDecoration:t.done?"line-through":"none"}}>{t.text}</span>
                            {t.project&&<span style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.8em",color:"#1a3a5a"}}>[{t.project}]</span>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    )}

    {/* ── EDITION ── */}
    {view==="edition"&&(
      !weeklyEd?(
        <div style={{textAlign:"center",padding:"50px 20px",color:"#1a3a5a"}}>
          <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.75em",marginBottom:"12px"}}>No edition compiled for week of {currentWk}</div>
          <button className="btn btn-sat" disabled={daysWithData.length===0} onClick={()=>setView("weekview")}>Go to Week View →</button>
        </div>
      ):(
        <div className="paper">
          <div style={{textAlign:"right",marginBottom:"8px",display:"flex",gap:"6px",justifyContent:"flex-end"}}>
            <button className="btn btn-g" style={{fontSize:"0.65em",color:"#888"}} onClick={generateWeekly}>↻ Regenerate</button>
          </div>
          <header className="mast">
            <div className="mast-title">The AutoBoros Dispatch</div>
            <div className="mast-sub">Personal Intelligence · Systems · Build Log · Inner Orbit</div>
            <div className="mast-meta">
              <span>Saturday Edition · Week of {weeklyEd.edition_date}</span>
              <span>Melton, Victoria, Australia</span>
              <span>AutoBoros.ai · Az</span>
            </div>
          </header>

          {/* Energy map strip */}
          <div style={{background:"#f0ede5",border:"1px solid #ddd",borderRadius:"2px",padding:"10px 14px",margin:"14px 0",display:"flex",gap:"8px",flexWrap:"wrap",alignItems:"center"}}>
            <span style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.6em",letterSpacing:"0.16em",textTransform:"uppercase",color:"#888",marginRight:"4px"}}>Week Energy</span>
            {DAYS.map((d,i)=>{
              const s=schedule[d]||{};
              const dominant=Object.values(s).reduce((acc,v)=>{acc[v]=(acc[v]||0)+1;return acc;},{});
              const top=Object.entries(dominant).sort((a,b)=>b[1]-a[1])[0]?.[0]||"sleep";
              const en=ENERGY.find(e=>e.id===top)||ENERGY[3];
              return(
                <div key={d} style={{textAlign:"center",minWidth:"50px"}}>
                  <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.58em",color:"#aaa",textTransform:"uppercase"}}>{SHORT[i]}</div>
                  <div style={{background:en.bg,border:`1px solid ${en.color}44`,borderRadius:"2px",padding:"3px 6px",marginTop:"2px"}}>
                    <span style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.58em",color:en.color}}>{en.label.split(" ")[0]}</span>
                  </div>
                  {goals[d]&&<div style={{fontSize:"0.55em",color:"#bbb",marginTop:"2px",maxWidth:"56px",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{goals[d].slice(0,12)}</div>}
                </div>
              );
            })}
          </div>

          <div className="np-sec"><span>Week in Review</span></div>
          <div className="np2">
            <div className="npc" style={{paddingBottom:"16px",borderBottom:"1px solid #ccc"}}>
              <div className="np-kicker">Lead Story · {weeklyEd.week_stats?.theme||"Build Week"}</div>
              <h1 className="np-hed-xl">{weeklyEd.lead_headline}</h1>
              <div className="np-dek">{weeklyEd.lead_dek}</div>
              <div className="np-byline">Az · AutoBoros.ai · Week of {weeklyEd.edition_date}</div>
              <div className="np-body" dangerouslySetInnerHTML={{__html:(weeklyEd.lead_body||"").replace(/\n\n/g,"</p><p>").replace(/^/,"<p>").replace(/$/,"</p>")}}/>
              <div className="np-pull">{weeklyEd.pull_quote}</div>
            </div>
            <div className="npc npc-b">
              <div className="np-sc">
                <div className="np-sc-title">📊 Week at a Glance</div>
                {Object.entries(weeklyEd.week_stats||{}).map(([k,v])=>(
                  <div key={k} className="np-sc-row"><span>{k.replace(/_/g," ")}</span><span className="np-sc-val">{v}</span></div>
                ))}
              </div>
              {weeklyEd.client_desk&&<><div className="np-kicker">Client Desk</div><div className="np-hed-sm">Business Update</div><div className="np-body"><p>{weeklyEd.client_desk}</p></div><hr className="np-thin"/></>}
              {weeklyEd.intel_flash&&<><div className="np-kicker">Intel Flash</div><div className="np-hed-sm">Ecosystem Intelligence</div><div className="np-body"><p>{weeklyEd.intel_flash}</p></div></>}
              {/* Schedule plan vs actual */}
              {schedSum&&<><hr className="np-thin"/><div className="np-kicker">Week Plan</div><div className="np-hed-sm">{schedSum.week_headline}</div><div className="np-body"><p style={{fontStyle:"italic",color:"#666"}}>{schedSum.week_mantra}</p></div></>}
            </div>
          </div>

          <div className="np-sec"><span>Daily Chronicle</span></div>
          <div className="np3">
            {(weeklyEd.day_summaries||[]).map((ds,i)=>(
              <div key={i} className={`npc ${i>0?"npc-b":""}`}>
                <div className="np-kicker">{ds.day} {ds.rating}</div>
                <div className="np-hed-sm">{ds.hed}</div>
                <div className="np-body"><p>{ds.detail}</p></div>
                {ds.energy_match&&<div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.58em",marginTop:"4px",color:ds.energy_match==="yes"?"#2a8a44":ds.energy_match==="partial"?"#906020":"#8a2020"}}>
                  Plan match: {ds.energy_match}
                </div>}
              </div>
            ))}
          </div>

          <hr className="np-hr"/>
          <div className="np-sec"><span>Looking Ahead</span></div>
          <div className="np3">
            {(weeklyEd.looking_ahead||[]).map((la,i)=>(
              <div key={i} className={`npc ${i>0?"npc-b":""}`}>
                <div className="np-kicker">Priority {la.priority}</div>
                <div className="np-hed-sm">{la.hed}</div>
                <div className="np-body"><p>{la.body}</p></div>
              </div>
            ))}
          </div>

          {schedSum&&(schedSum.priorities||[]).length>0&&<>
            <div className="np-sec"><span>This Week's Plan</span></div>
            <div className="np3">
              {(schedSum.priorities||[]).map((p,i)=>(
                <div key={i} className={`npc ${i>0?"npc-b":""}`}>
                  <div className="np-kicker">{p.num}</div>
                  <div className="np-hed-sm">{p.hed}</div>
                  <div className="np-body"><p>{p.body}</p></div>
                </div>
              ))}
            </div>
          </>}

          <div className="np-foot">
            <span>The AutoBoros Dispatch · Az · Melton VIC</span>
            <span>Compiled {fmtDisplay(today)}</span>
            <span>AutoBoros.ai · Claude Sonnet 4.6</span>
          </div>
        </div>
      )
    )}

    </div>
  </>);
}