import { useState, useEffect } from "react";

const DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
const SHORT = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

const ENERGY = [
  { id:"red",    label:"🔴 Deep Work",    desc:"Complex builds, new systems, hard thinking",   color:"#c0392b", bg:"#3a0a0a" },
  { id:"yellow", label:"🟡 Medium",       desc:"Client work, research, documentation",          color:"#f0a000", bg:"#3a2a00" },
  { id:"green",  label:"🟢 Light",        desc:"Admin, email, reviewing, packaging",            color:"#2a9a44", bg:"#0a2a1a" },
  { id:"sleep",  label:"😴 Rest/Care",    desc:"Grandparent care, rest, no sessions",           color:"#4a5a7a", bg:"#0a1020" },
  { id:"create", label:"🎨 Creative",     desc:"Ratdog & Skunk, design, creative writing",      color:"#9a50d0", bg:"#1a0a30" },
  { id:"client", label:"💼 Client",       desc:"Aurora/Evermystic — billable delivery work",    color:"#0a7ac0", bg:"#0a1a3a" },
];

const BLOCKS = [
  { id:"b1", label:"Early Morning",  time:"5–8am",   icon:"🌅" },
  { id:"b2", label:"Morning",        time:"8–11am",  icon:"☕" },
  { id:"b3", label:"Midday",         time:"11am–2pm",icon:"⚡" },
  { id:"b4", label:"Afternoon",      time:"2–5pm",   icon:"🔧" },
  { id:"b5", label:"Evening",        time:"5–8pm",   icon:"🌆" },
  { id:"b6", label:"Night",          time:"8–11pm",  icon:"🌙" },
];

const PROJECTS = [
  "ECC Recovery","Kali Agent","HexStrike","Evermystic","Aurora Agency",
  "Ratdog & Skunk","Home Lab","Elder Care","AutoBoros Stack","WorldMonitor",
  "Legal Skills","Notion Skills","Personal","Admin","Research"
];

const DEFAULT_SCHEDULE = {
  Monday:    { b1:"sleep",  b2:"green",  b3:"yellow", b4:"red",    b5:"yellow", b6:"green"  },
  Tuesday:   { b1:"sleep",  b2:"red",    b3:"red",    b4:"yellow", b5:"client", b6:"yellow" },
  Wednesday: { b1:"sleep",  b2:"yellow", b3:"red",    b4:"red",    b5:"yellow", b6:"green"  },
  Thursday:  { b1:"sleep",  b2:"red",    b3:"red",    b4:"client", b5:"create", b6:"yellow" },
  Friday:    { b1:"sleep",  b2:"yellow", b3:"client", b4:"green",  b5:"create", b6:"sleep"  },
  Saturday:  { b1:"sleep",  b2:"green",  b3:"green",  b4:"sleep",  b5:"sleep",  b6:"sleep"  },
  Sunday:    { b1:"sleep",  b2:"sleep",  b3:"yellow", b4:"red",    b5:"yellow", b6:"green"  },
};

const DEFAULT_GOALS = {
  Monday:"",Tuesday:"",Wednesday:"",Thursday:"",Friday:"",Saturday:"",Sunday:""
};

const DEFAULT_TASKS = {
  Monday:[],Tuesday:[],Wednesday:[],Thursday:[],Friday:[],Saturday:[],Sunday:[]
};

function weekStart() {
  const d = new Date();
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  const mon = new Date(d);
  mon.setDate(d.getDate() + diff);
  return mon;
}
function fmt(d){ return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`; }
function addDays(d,n){ const x=new Date(d); x.setDate(x.getDate()+n); return x; }

const css = `
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;500;600&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body{background:#080e18;color:#c8d8e8;font-family:'Inter',sans-serif;font-size:14px;}

/* CMD */
.cmd{background:#050a12;border-bottom:1px solid #0d1a28;padding:10px 20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;position:sticky;top:0;z-index:50;}
.cmd-brand{font-family:'IBM Plex Mono',monospace;color:#00d4ff;font-size:0.78em;letter-spacing:0.2em;text-transform:uppercase;}
.cmd-week{font-family:'IBM Plex Mono',monospace;font-size:0.65em;color:#3a5a7a;}
.tabs{display:flex;gap:0;}
.ctab{font-family:'IBM Plex Mono',monospace;font-size:0.65em;letter-spacing:0.1em;text-transform:uppercase;padding:6px 12px;border:1px solid #0d1a28;background:transparent;color:#3a5a7a;cursor:pointer;transition:all 0.12s;}
.ctab:hover{color:#7a9ab0;background:#0d1a28;}
.ctab.on{background:#0d2040;color:#00d4ff;border-color:#1a3a60;}

/* MAIN */
.main{max-width:1100px;margin:0 auto;padding:16px;}

/* LEGEND */
.legend{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px;}
.leg-item{display:flex;align-items:center;gap:6px;padding:5px 10px;border-radius:3px;border:1px solid #0d1a28;cursor:pointer;transition:all 0.12s;}
.leg-item:hover{border-color:#1a3a60;}
.leg-item.active{border-color:#00d4ff;}
.leg-dot{width:10px;height:10px;border-radius:50%;}
.leg-label{font-family:'IBM Plex Mono',monospace;font-size:0.62em;letter-spacing:0.08em;text-transform:uppercase;}

/* GRID VIEW */
.sched-grid{display:grid;grid-template-columns:90px repeat(7,1fr);gap:1px;background:#0d1a28;border:1px solid #0d1a28;border-radius:4px;overflow:hidden;margin-bottom:16px;}
.sg-head{background:#050a12;padding:8px 6px;text-align:center;}
.sg-day{font-family:'IBM Plex Mono',monospace;font-size:0.68em;letter-spacing:0.1em;text-transform:uppercase;color:#7a9ab0;}
.sg-date{font-size:0.75em;color:#3a5a7a;margin-top:2px;}
.sg-date.today{color:#00ff88;font-weight:600;}
.sg-time-label{background:#050a12;padding:8px 10px;display:flex;flex-direction:column;justify-content:center;}
.sg-time-icon{font-size:1em;margin-bottom:2px;}
.sg-time-name{font-family:'IBM Plex Mono',monospace;font-size:0.58em;letter-spacing:0.06em;color:#3a5a7a;text-transform:uppercase;}
.sg-time-range{font-family:'IBM Plex Mono',monospace;font-size:0.55em;color:#2a3a4a;}
.sg-cell{padding:4px;cursor:pointer;transition:all 0.12s;min-height:52px;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:2px;position:relative;}
.sg-cell:hover{filter:brightness(1.3);}
.sg-cell-label{font-family:'IBM Plex Mono',monospace;font-size:0.55em;letter-spacing:0.05em;text-transform:uppercase;text-align:center;line-height:1.3;opacity:0.8;}
.sg-task-dot{width:5px;height:5px;border-radius:50%;background:rgba(255,255,255,0.4);}

/* DAY VIEW */
.day-view{display:grid;grid-template-columns:1fr 300px;gap:16px;}
.day-panel{background:#0a1420;border:1px solid #0d1a28;border-radius:4px;padding:16px;}
.day-nav{display:flex;align-items:center;gap:8px;margin-bottom:16px;}
.nav-btn{font-family:'IBM Plex Mono',monospace;font-size:0.7em;padding:5px 10px;border:1px solid #0d1a28;background:transparent;color:#3a5a7a;cursor:pointer;border-radius:2px;transition:all 0.12s;}
.nav-btn:hover{color:#00d4ff;border-color:#1a3a60;}
.day-title{font-family:'Playfair Display',serif;font-size:1.4em;color:#fff;flex:1;text-align:center;}
.day-date{font-family:'IBM Plex Mono',monospace;font-size:0.65em;color:#3a5a7a;text-align:center;margin-bottom:14px;}

.block-row{display:flex;gap:10px;margin-bottom:8px;align-items:stretch;}
.block-time{min-width:90px;display:flex;flex-direction:column;justify-content:center;}
.block-icon{font-size:1.1em;}
.block-name{font-family:'IBM Plex Mono',monospace;font-size:0.62em;color:#3a5a7a;text-transform:uppercase;letter-spacing:0.06em;}
.block-range{font-family:'IBM Plex Mono',monospace;font-size:0.58em;color:#2a3a4a;}
.block-energy{flex:1;border-radius:3px;padding:10px 12px;cursor:pointer;transition:all 0.12s;border:1px solid transparent;}
.block-energy:hover{filter:brightness(1.2);}
.block-energy-label{font-family:'IBM Plex Mono',monospace;font-size:0.68em;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px;}
.block-task-input{width:100%;background:transparent;border:none;color:#8aa0b0;font-size:0.82em;font-family:'Inter',sans-serif;outline:none;padding:2px 0;}
.block-task-input::placeholder{color:#2a3a5a;}

/* FOCUS / GOAL */
.goal-section{margin-bottom:12px;}
.goal-label{font-family:'IBM Plex Mono',monospace;font-size:0.62em;letter-spacing:0.15em;text-transform:uppercase;color:#3a5a7a;margin-bottom:5px;}
.goal-input{width:100%;background:#050a12;border:1px solid #0d1a28;color:#c8d8e8;padding:8px 10px;border-radius:3px;font-family:'Inter',sans-serif;font-size:0.88em;outline:none;resize:none;}
.goal-input:focus{border-color:#1a3a60;}

/* SIDEBAR */
.sidebar-card{background:#0a1420;border:1px solid #0d1a28;border-radius:4px;padding:14px;margin-bottom:12px;}
.sidebar-title{font-family:'IBM Plex Mono',monospace;font-size:0.62em;letter-spacing:0.18em;text-transform:uppercase;color:#00d4ff;margin-bottom:10px;}

/* TASK LIST */
.task-item{display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid #0d1a28;}
.task-item:last-child{border-bottom:none;}
.task-check{width:14px;height:14px;border:1px solid #2a3a5a;border-radius:2px;cursor:pointer;flex-shrink:0;display:flex;align-items:center;justify-content:center;transition:all 0.12s;}
.task-check.done{background:#0a3a1a;border-color:#2a9a44;}
.task-text{flex:1;font-size:0.82em;color:#8aa0b0;cursor:pointer;}
.task-text.done{text-decoration:line-through;color:#2a3a5a;}
.task-proj{font-family:'IBM Plex Mono',monospace;font-size:0.58em;padding:1px 5px;border-radius:2px;background:#0d1a28;color:#3a5a7a;}
.task-del{font-size:0.8em;color:#2a3a5a;cursor:pointer;padding:2px 4px;transition:all 0.12s;}
.task-del:hover{color:#c0392b;}

/* ADD TASK */
.add-task-row{display:flex;gap:6px;margin-top:8px;}
.task-new-input{flex:1;background:#050a12;border:1px solid #0d1a28;color:#c8d8e8;padding:6px 8px;border-radius:3px;font-size:0.8em;font-family:'Inter',sans-serif;outline:none;}
.task-new-input:focus{border-color:#1a3a60;}
select.proj-select{background:#050a12;border:1px solid #0d1a28;color:#3a5a7a;padding:6px 8px;border-radius:3px;font-size:0.75em;font-family:'IBM Plex Mono',monospace;outline:none;cursor:pointer;}
.btn-add{font-family:'IBM Plex Mono',monospace;font-size:0.65em;padding:6px 10px;border:1px solid #1a3a60;background:#0d2040;color:#00d4ff;cursor:pointer;border-radius:3px;transition:all 0.12s;white-space:nowrap;}
.btn-add:hover{background:#1a3a60;}

/* WEEK STATS */
.stat-row{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #0d1a28;font-size:0.8em;}
.stat-row:last-child{border-bottom:none;}
.stat-key{color:#3a5a7a;}
.stat-val{font-family:'IBM Plex Mono',monospace;color:#00d4ff;font-weight:600;}

/* WEEKLY SUMMARY */
.sum-card{background:#0a1420;border:1px solid #0d1a28;border-radius:4px;padding:18px;margin-bottom:14px;}
.sum-hed{font-family:'Playfair Display',serif;font-size:1.3em;color:#fff;margin-bottom:6px;}
.sum-body{font-size:0.87em;color:#7a9ab0;line-height:1.7;}
.sum-body p{margin-bottom:8px;}
.priority-item{display:flex;gap:10px;padding:10px 0;border-bottom:1px solid #0d1a28;}
.priority-item:last-child{border-bottom:none;}
.priority-num{font-family:'Playfair Display',serif;font-size:1.6em;color:#1a3a60;min-width:28px;line-height:1;}
.priority-content{}
.priority-hed{font-weight:600;color:#c8d8e8;margin-bottom:3px;font-size:0.9em;}
.priority-body{font-size:0.8em;color:#4a6a7a;line-height:1.5;}
.gen-btn{font-family:'IBM Plex Mono',monospace;font-size:0.7em;letter-spacing:0.1em;text-transform:uppercase;padding:9px 18px;border:1px solid #1a3a60;background:#0d2040;color:#00d4ff;cursor:pointer;border-radius:3px;transition:all 0.12s;display:flex;align-items:center;gap:6px;}
.gen-btn:hover{background:#1a3a60;}
.gen-btn:disabled{opacity:0.4;cursor:not-allowed;}
.dot{animation:blink 1s infinite;font-size:1.2em;line-height:1;}
@keyframes blink{0%,100%{opacity:0.2;}50%{opacity:1;}}

/* PRINT */
@media print{.cmd,.tabs,.gen-btn,.add-task-row,.task-del,.nav-btn{display:none!important;} body{background:#fff;color:#000;} .sched-grid{border-color:#ccc;}}

@media(max-width:700px){.day-view{grid-template-columns:1fr;} .sched-grid{grid-template-columns:70px repeat(7,1fr);} .sg-cell{min-height:40px;}}
`;

const SUMMARY_PROMPT = (weekOf, days, schedule, goals, tasks) => `You are the editor of "The AutoBoros Dispatch" personal newspaper for Az — AI systems builder, Melton VIC, Australia. AutoBoros.ai. ADHD + autism. Live-in carer for grandparents. Working toward reunification with twin daughters. Projects: ECC, Kali Agent, HexStrike, Evermystic/Aurora AI Agency, Ratdog & Skunk, WorldMonitor.

Week of: ${weekOf}

Energy schedule this week:
${days.map((d,i)=>{
  const s = schedule[d]||{};
  const energyStr = Object.entries(s).map(([b,e])=>{
    const block = BLOCKS.find(x=>x.id===b);
    const en = ENERGY.find(x=>x.id===e);
    return `${block?.time}: ${en?.label}`;
  }).join(', ');
  const goal = goals[d]||'';
  const ts = (tasks[d]||[]).map(t=>`${t.done?'✓':'○'} ${t.text}${t.project?' ['+t.project+']':''}`).join(', ');
  return `${d}: ${energyStr}${goal?'\n  Focus: '+goal:''}${ts?'\n  Tasks: '+ts:''}`;
}).join('\n\n')}

Generate a structured weekly plan and summary as JSON only (no markdown fences):
{
  "week_headline": "punchy headline capturing the week's intention (max 12 words)",
  "week_theme": "one word theme",
  "opening": "2 paragraph opening editorial — what this week is about, what the energy pattern signals, honest assessment of priorities",
  "daily_intentions": [
    {"day":"Monday","intention":"one sentence focus","energy":"energy descriptor","watch_out":"one honest risk or trap to avoid"}
  ],
  "priorities": [
    {"num":"01","hed":"priority title","body":"2 sentences on why this matters this week and what done looks like"},
    {"num":"02","hed":"priority title","body":"2 sentences"},
    {"num":"03","hed":"priority title","body":"2 sentences"}
  ],
  "honest_note": "one paragraph of honest, direct editorial — what pattern is showing up, what needs to change, what's actually working",
  "week_mantra": "one short phrase or sentence to carry through the week"
}`;

export default function App() {
  const [view, setView] = useState("grid");
  const [selectedDayIdx, setSelectedDayIdx] = useState(new Date().getDay()===0?6:new Date().getDay()-1);
  const [schedule, setSchedule] = useState(DEFAULT_SCHEDULE);
  const [goals, setGoals] = useState(DEFAULT_GOALS);
  const [tasks, setTasks] = useState(DEFAULT_TASKS);
  const [activeLeg, setActiveLeg] = useState(null);
  const [newTask, setNewTask] = useState("");
  const [newProj, setNewProj] = useState("");
  const [summary, setSummary] = useState(null);
  const [sumLoading, setSumLoading] = useState(false);
  const mon = weekStart();
  const weekDates = DAYS.map((_,i)=>addDays(mon,i));
  const todayFmt = fmt(new Date());

  useEffect(()=>{
    async function load(){
      try{const r=await window.storage.get("sched:schedule");if(r)setSchedule(JSON.parse(r.value));}catch{}
      try{const r=await window.storage.get("sched:goals");if(r)setGoals(JSON.parse(r.value));}catch{}
      try{const r=await window.storage.get("sched:tasks");if(r)setTasks(JSON.parse(r.value));}catch{}
      try{const r=await window.storage.get("sched:summary:"+fmt(mon));if(r)setSummary(JSON.parse(r.value));}catch{}
    }
    load();
  },[]);

  async function saveSchedule(s){setSchedule(s);try{await window.storage.set("sched:schedule",JSON.stringify(s));}catch{}}
  async function saveGoals(g){setGoals(g);try{await window.storage.set("sched:goals",JSON.stringify(g));}catch{}}
  async function saveTasks(t){setTasks(t);try{await window.storage.set("sched:tasks",JSON.stringify(t));}catch{}}

  function setCell(day, block, energy){
    saveSchedule({...schedule,[day]:{...(schedule[day]||{}), [block]:energy}});
  }

  function cycleEnergy(day, block){
    const curr = schedule[day]?.[block]||"sleep";
    const idx = ENERGY.findIndex(e=>e.id===curr);
    const next = ENERGY[(idx+1)%ENERGY.length];
    setCell(day, block, next.id);
  }

  function setActive(day, block){
    if(!activeLeg) return cycleEnergy(day, block);
    setCell(day, block, activeLeg);
  }

  function addTask(day){
    if(!newTask.trim()) return;
    const t = [...(tasks[day]||[]), {id:Date.now(), text:newTask.trim(), project:newProj, done:false}];
    saveTasks({...tasks,[day]:t});
    setNewTask(""); setNewProj("");
  }

  function toggleTask(day, id){
    const t = (tasks[day]||[]).map(tk=>tk.id===id?{...tk,done:!tk.done}:tk);
    saveTasks({...tasks,[day]:t});
  }

  function delTask(day, id){
    saveTasks({...tasks,[day]:(tasks[day]||[]).filter(tk=>tk.id!==id)});
  }

  async function generateSummary(){
    setSumLoading(true);
    try{
      const res=await fetch("https://api.anthropic.com/v1/messages",{
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({model:"claude-sonnet-4-20250514",max_tokens:2000,
          messages:[{role:"user",content:SUMMARY_PROMPT(fmt(mon),DAYS,schedule,goals,tasks)}]
        })
      });
      const data=await res.json();
      const text=data.content?.find(b=>b.type==="text")?.text||"";
      const parsed=JSON.parse(text.replace(/```json|```/g,"").trim());
      setSummary(parsed);
      await window.storage.set("sched:summary:"+fmt(mon),JSON.stringify(parsed));
    }catch(e){console.error(e);}
    setSumLoading(false);
  }

  const selDay = DAYS[selectedDayIdx];
  const selDate = weekDates[selectedDayIdx];

  // week stats
  const totalTasks = DAYS.reduce((a,d)=>a+(tasks[d]||[]).length,0);
  const doneTasks  = DAYS.reduce((a,d)=>a+(tasks[d]||[]).filter(t=>t.done).length,0);
  const deepDays   = DAYS.filter(d=>Object.values(schedule[d]||{}).includes("red")).length;
  const clientDays = DAYS.filter(d=>Object.values(schedule[d]||{}).includes("client")).length;
  const restDays   = DAYS.filter(d=>Object.values(schedule[d]||{}).filter(v=>v!=="sleep").length<=1).length;

  return(
    <>
      <style>{css}</style>
      <div>
        <div className="cmd">
          <div>
            <div className="cmd-brand">⬡ AutoBoros Weekly Scheduler</div>
            <div className="cmd-week">Week of {mon.getDate()} {MONTHS[mon.getMonth()]} — {fmt(mon)}</div>
          </div>
          <div className="tabs">
            <button className={`ctab ${view==="grid"?"on":""}`} onClick={()=>setView("grid")}>Grid</button>
            <button className={`ctab ${view==="day"?"on":""}`} onClick={()=>setView("day")}>Day View</button>
            <button className={`ctab ${view==="summary"?"on":""}`} onClick={()=>setView("summary")}>Weekly Summary</button>
          </div>
        </div>

        <div className="main">

          {/* ── GRID VIEW ── */}
          {view==="grid" && <>
            {/* Legend / Brush */}
            <div style={{marginBottom:"10px"}}>
              <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.62em",letterSpacing:"0.15em",textTransform:"uppercase",color:"#2a3a5a",marginBottom:"6px"}}>
                {activeLeg ? `Painting: ${ENERGY.find(e=>e.id===activeLeg)?.label} — click cells to apply · click active below to deselect` : "Click a cell to cycle energy · or select energy below to paint"}
              </div>
              <div className="legend">
                {ENERGY.map(e=>(
                  <div key={e.id} className={`leg-item ${activeLeg===e.id?"active":""}`}
                    style={{background:activeLeg===e.id?e.bg:"#0a1420"}}
                    onClick={()=>setActiveLeg(activeLeg===e.id?null:e.id)}>
                    <div className="leg-dot" style={{background:e.color}}/>
                    <span className="leg-label" style={{color:activeLeg===e.id?e.color:"#3a5a7a"}}>{e.label}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Grid */}
            <div className="sched-grid">
              {/* Header row */}
              <div className="sg-head"/>
              {DAYS.map((d,i)=>{
                const date = weekDates[i];
                const isToday = fmt(date)===todayFmt;
                return(
                  <div key={d} className="sg-head" style={{cursor:"pointer"}} onClick={()=>{setSelectedDayIdx(i);setView("day");}}>
                    <div className="sg-day">{SHORT[i]}</div>
                    <div className={`sg-date ${isToday?"today":""}`}>{date.getDate()} {MONTHS[date.getMonth()]}</div>
                    {goals[d]&&<div style={{fontSize:"0.55em",color:"#2a4a6a",marginTop:"2px",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap",maxWidth:"90px"}}>{goals[d].slice(0,20)}</div>}
                  </div>
                );
              })}

              {/* Block rows */}
              {BLOCKS.map(blk=>(
                <>
                  <div key={blk.id+"lbl"} className="sg-time-label">
                    <div className="sg-time-icon">{blk.icon}</div>
                    <div className="sg-time-name">{blk.label}</div>
                    <div className="sg-time-range">{blk.time}</div>
                  </div>
                  {DAYS.map(d=>{
                    const eId = schedule[d]?.[blk.id]||"sleep";
                    const en = ENERGY.find(e=>e.id===eId)||ENERGY[3];
                    const hasTasks = (tasks[d]||[]).some(()=>true);
                    return(
                      <div key={d+blk.id} className="sg-cell"
                        style={{background:en.bg}}
                        onClick={()=>setActive(d,blk.id)}>
                        <div className="sg-cell-label" style={{color:en.color}}>{en.label.split(" ")[0]}</div>
                        {hasTasks && <div className="sg-task-dot"/>}
                      </div>
                    );
                  })}
                </>
              ))}
            </div>

            {/* Quick week stats */}
            <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(160px,1fr))",gap:"8px",marginTop:"8px"}}>
              {[
                ["Deep Work Days",deepDays],["Client Days",clientDays],["Rest Days",restDays],
                ["Tasks",`${doneTasks}/${totalTasks}`],["Week of",fmt(mon)]
              ].map(([k,v])=>(
                <div key={k} style={{background:"#0a1420",border:"1px solid #0d1a28",borderRadius:"3px",padding:"10px 12px",display:"flex",justifyContent:"space-between",alignItems:"center"}}>
                  <span style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.62em",color:"#3a5a7a",textTransform:"uppercase",letterSpacing:"0.08em"}}>{k}</span>
                  <span style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.85em",color:"#00d4ff",fontWeight:"600"}}>{v}</span>
                </div>
              ))}
            </div>
          </>}

          {/* ── DAY VIEW ── */}
          {view==="day" && (
            <div className="day-view">
              <div>
                <div className="day-nav">
                  <button className="nav-btn" onClick={()=>setSelectedDayIdx((selectedDayIdx+6)%7)}>← {SHORT[(selectedDayIdx+6)%7]}</button>
                  <div style={{flex:1,textAlign:"center"}}>
                    <div className="day-title">{selDay}</div>
                    <div className="day-date">{selDate.getDate()} {MONTHS[selDate.getMonth()]} {selDate.getFullYear()}
                      {fmt(selDate)===todayFmt && <span style={{color:"#00ff88",marginLeft:"8px",fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.85em"}}>TODAY</span>}
                    </div>
                  </div>
                  <button className="nav-btn" onClick={()=>setSelectedDayIdx((selectedDayIdx+1)%7)}>{SHORT[(selectedDayIdx+1)%7]} →</button>
                </div>

                {/* Day goal */}
                <div className="goal-section">
                  <div className="goal-label">Day's Main Focus</div>
                  <textarea className="goal-input" rows={2}
                    placeholder="What's the one thing that makes today a win?"
                    value={goals[selDay]||""}
                    onChange={e=>saveGoals({...goals,[selDay]:e.target.value})}
                  />
                </div>

                {/* Energy blocks */}
                {BLOCKS.map(blk=>{
                  const eId=schedule[selDay]?.[blk.id]||"sleep";
                  const en=ENERGY.find(e=>e.id===eId)||ENERGY[3];
                  return(
                    <div key={blk.id} className="block-row">
                      <div className="block-time">
                        <div className="block-icon">{blk.icon}</div>
                        <div className="block-name">{blk.label}</div>
                        <div className="block-range">{blk.time}</div>
                      </div>
                      <div className="block-energy" style={{background:en.bg,borderColor:en.color+"44"}}
                        onClick={()=>cycleEnergy(selDay,blk.id)}>
                        <div className="block-energy-label" style={{color:en.color}}>{en.label}</div>
                        <div style={{fontSize:"0.75em",color:"#3a5a7a"}}>{en.desc}</div>
                        <input className="block-task-input" placeholder="Notes for this block…"
                          onClick={e=>e.stopPropagation()}
                          value={(goals[selDay+"_"+blk.id])||""}
                          onChange={e=>{
                            const key=selDay+"_"+blk.id;
                            const updated={...goals,[key]:e.target.value};
                            saveGoals(updated);
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Sidebar */}
              <div>
                <div className="sidebar-card">
                  <div className="sidebar-title">Tasks for {selDay}</div>
                  {(tasks[selDay]||[]).map(t=>(
                    <div key={t.id} className="task-item">
                      <div className={`task-check ${t.done?"done":""}`} onClick={()=>toggleTask(selDay,t.id)}>
                        {t.done&&<span style={{color:"#2a9a44",fontSize:"0.8em"}}>✓</span>}
                      </div>
                      <span className={`task-text ${t.done?"done":""}`} onClick={()=>toggleTask(selDay,t.id)}>{t.text}</span>
                      {t.project&&<span className="task-proj">{t.project}</span>}
                      <span className="task-del" onClick={()=>delTask(selDay,t.id)}>✕</span>
                    </div>
                  ))}
                  {(tasks[selDay]||[]).length===0&&<div style={{color:"#2a3a5a",fontSize:"0.8em",fontStyle:"italic",padding:"6px 0"}}>No tasks yet</div>}
                  <div className="add-task-row">
                    <input className="task-new-input" placeholder="Add task…"
                      value={newTask} onChange={e=>setNewTask(e.target.value)}
                      onKeyDown={e=>e.key==="Enter"&&addTask(selDay)} />
                    <select className="proj-select" value={newProj} onChange={e=>setNewProj(e.target.value)}>
                      <option value="">Project…</option>
                      {PROJECTS.map(p=><option key={p} value={p}>{p}</option>)}
                    </select>
                    <button className="btn-add" onClick={()=>addTask(selDay)}>+ Add</button>
                  </div>
                </div>

                <div className="sidebar-card">
                  <div className="sidebar-title">Week Stats</div>
                  <div className="stat-row"><span className="stat-key">Tasks done</span><span className="stat-val">{doneTasks}/{totalTasks}</span></div>
                  <div className="stat-row"><span className="stat-key">Deep work days</span><span className="stat-val">{deepDays}</span></div>
                  <div className="stat-row"><span className="stat-key">Client days</span><span className="stat-val">{clientDays}</span></div>
                  <div className="stat-row"><span className="stat-key">Rest days</span><span className="stat-val">{restDays}</span></div>
                </div>

                <div className="sidebar-card">
                  <div className="sidebar-title">Energy Key</div>
                  {ENERGY.map(e=>(
                    <div key={e.id} style={{display:"flex",gap:"8px",alignItems:"flex-start",padding:"5px 0",borderBottom:"1px solid #0d1a28"}}>
                      <div style={{width:"8px",height:"8px",borderRadius:"50%",background:e.color,marginTop:"5px",flexShrink:0}}/>
                      <div>
                        <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.65em",color:e.color}}>{e.label}</div>
                        <div style={{fontSize:"0.72em",color:"#3a5a7a"}}>{e.desc}</div>
                      </div>
                    </div>
                  ))}
                  <div style={{marginTop:"8px",fontSize:"0.72em",color:"#2a3a5a",fontStyle:"italic"}}>Tap any block to cycle energy type</div>
                </div>
              </div>
            </div>
          )}

          {/* ── WEEKLY SUMMARY ── */}
          {view==="summary" && (
            <div>
              <div style={{display:"flex",gap:"10px",alignItems:"center",marginBottom:"16px",flexWrap:"wrap"}}>
                <button className="gen-btn" disabled={sumLoading} onClick={generateSummary}>
                  {sumLoading?<><span className="dot">·</span><span className="dot" style={{animationDelay:"0.3s"}}>·</span><span className="dot" style={{animationDelay:"0.6s"}}>·</span> Generating…</>:"⬡ Generate Weekly Summary"}
                </button>
                {summary&&<button className="gen-btn" style={{background:"transparent"}} onClick={generateSummary}>↻ Regenerate</button>}
                <span style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.62em",color:"#2a3a5a"}}>
                  Based on your energy schedule, goals, and tasks for week of {fmt(mon)}
                </span>
              </div>

              {!summary?(
                <div style={{textAlign:"center",padding:"60px 20px",color:"#2a3a5a"}}>
                  <div style={{fontSize:"2em",marginBottom:"12px"}}>⬡</div>
                  <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.75em",letterSpacing:"0.1em",textTransform:"uppercase",marginBottom:"8px"}}>No summary yet</div>
                  <div style={{fontSize:"0.82em"}}>Set your energy schedule and add tasks, then hit Generate to get your weekly editorial.</div>
                </div>
              ):(
                <>
                  <div className="sum-card">
                    <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.62em",letterSpacing:"0.2em",textTransform:"uppercase",color:"#00d4ff",marginBottom:"6px"}}>Week of {fmt(mon)} · {summary.week_theme}</div>
                    <div className="sum-hed">{summary.week_headline}</div>
                    {summary.week_mantra&&<div style={{fontFamily:"'Playfair Display',serif",fontStyle:"italic",color:"#f0d080",fontSize:"1em",margin:"8px 0 12px",borderLeft:"3px solid #f0d080",paddingLeft:"12px"}}>{summary.week_mantra}</div>}
                    <div className="sum-body" dangerouslySetInnerHTML={{__html:(summary.opening||"").replace(/\n\n/g,"</p><p>").replace(/^/,"<p>").replace(/$/,"</p>")}}/>
                  </div>

                  <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"12px",marginBottom:"12px"}}>
                    {(summary.daily_intentions||[]).map(di=>{
                      const en=ENERGY.find(e=>e.id===(di.energy||"").toLowerCase().replace(/\s+/g,"_"))||null;
                      return(
                        <div key={di.day} style={{background:"#0a1420",border:"1px solid #0d1a28",borderRadius:"4px",padding:"12px"}}>
                          <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.65em",letterSpacing:"0.12em",textTransform:"uppercase",color:"#00d4ff",marginBottom:"4px"}}>{di.day}</div>
                          <div style={{fontWeight:"600",fontSize:"0.88em",color:"#c8d8e8",marginBottom:"4px"}}>{di.intention}</div>
                          {di.watch_out&&<div style={{fontSize:"0.78em",color:"#5a3a2a",borderLeft:"2px solid #5a2a0a",paddingLeft:"8px",marginTop:"4px"}}>⚠ {di.watch_out}</div>}
                        </div>
                      );
                    })}
                  </div>

                  <div className="sum-card">
                    <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.62em",letterSpacing:"0.2em",textTransform:"uppercase",color:"#00d4ff",marginBottom:"10px"}}>Week Priorities</div>
                    {(summary.priorities||[]).map(p=>(
                      <div key={p.num} className="priority-item">
                        <div className="priority-num">{p.num}</div>
                        <div className="priority-content">
                          <div className="priority-hed">{p.hed}</div>
                          <div className="priority-body">{p.body}</div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {summary.honest_note&&(
                    <div style={{background:"#0d1a10",border:"1px solid #1a3a1a",borderRadius:"4px",padding:"16px"}}>
                      <div style={{fontFamily:"'IBM Plex Mono',monospace",fontSize:"0.62em",letterSpacing:"0.18em",textTransform:"uppercase",color:"#00ff88",marginBottom:"8px"}}>Honest Note</div>
                      <div style={{fontSize:"0.87em",color:"#7a9ab0",lineHeight:"1.7"}}>{summary.honest_note}</div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

        </div>
      </div>
    </>
  );
}