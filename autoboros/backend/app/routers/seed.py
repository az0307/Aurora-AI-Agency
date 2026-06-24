from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from app.database import get_db
from app.models import Job, Activity
from app.services import manager
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/seed", tags=["seed"])

EVERMYSTIC_JOBS = [
    {
        "t": "Phase 0: Lock Stefan — verbal yes on $799/mo, send agreement + invoice AUR-001",
        "client": "Evermystic", "status": "Waiting on you", "lvl": 0, "actor": "You",
        "src": "SOP · Phase 0", "skill": None,
        "steps": ["Call Stefan, confirm $799/mo retainer verbally", "Send service agreement via DocuSign", "Generate and send invoice AUR-001", "Mark Phase 0 complete in Cockpit"],
        "ask": "This is money + relationship. You handle it. Call Stefan, get the verbal, send the docs.",
        "draft": None, "esc": False, "est": 0,
    },
    {
        "t": "Phase 1: Onboard Stefan — collect brand voice, logo, IG handle, refund policy",
        "client": "Evermystic", "status": "Next", "lvl": 1, "actor": "You",
        "src": "SOP · Phase 1", "skill": "client-onboarder",
        "steps": ["Send onboarding form (brand voice, logo assets, IG handle)", "Collect refund/turnaround policy in writing", "Agent preps the ManyChat custom field mapping from responses", "Hand to you for ManyChat wiring"],
        "ask": "Run the onboarding call or form. Agent will prep the custom field mapping once you have the responses.",
        "draft": None, "esc": False, "est": 15,
    },
    {
        "t": "Phase 2: Generate copy — 12 FAQs, welcome flows, keyword synonyms, fallback text via Haiku",
        "client": "Evermystic", "status": "Next", "lvl": 4, "actor": "Agent",
        "src": "SOP · Phase 2", "skill": "copy-generator",
        "steps": ["Pull brand voice + policy from Phase 1 results", "Generate 12 FAQ responses in Stefan's tone", "Draft welcome flow + fallback text", "Compile keyword synonym map for intent matching", "Save all outputs to /Clients/Evermystic/Copy/"],
        "ask": "", "draft": None, "esc": False, "est": 45,
    },
    {
        "t": "Phase 3: Build ManyChat flows — 12 flows starting with Quote Flow (Flow 2)",
        "client": "Evermystic", "status": "Inbox", "lvl": 1, "actor": "You",
        "src": "SOP · Phase 3", "skill": "manychat-assembler",
        "steps": ["Agent formats Phase 2 copy into ManyChat message blocks", "You wire custom fields: product_type, print_size, qty", "You build Flow 2 (Quote) with conditional logic", "Agent tests flow paths, reports drop-off points"],
        "ask": "Agent has prepped the copy blocks. You do the ManyChat wiring — custom fields, tags (HOT_LEAD), and Flow 2 logic.",
        "draft": None, "esc": False, "est": 60,
    },
    {
        "t": "Phase 4: Connect Activepieces — webhook routing, lead capture, Notion sync",
        "client": "Evermystic", "status": "Inbox", "lvl": 3, "actor": "Agent",
        "src": "SOP · Phase 4", "skill": "integration-wirer",
        "steps": ["Configure ManyChat → Activepieces webhook", "Map lead data to Notion Lead Ledger", "Set up auto-tagging: HOT_LEAD, WARM, COLD", "Test end-to-end: IG DM → ManyChat → Activepieces → Notion"],
        "ask": "", "draft": None, "esc": False, "est": 30,
    },
    {
        "t": "Phase 5: Launch + Agency Layer — extract SOP into Aurora client-delivery template v0.1",
        "client": "Evermystic", "status": "Inbox", "lvl": 2, "actor": "Agent",
        "src": "SOP · Phase 5", "skill": "sop-extractor",
        "steps": ["Compile all executed phases into structured SOP", "Draft Aurora client-delivery template v0.1", "Include pricing, timelines, and handoff checklist", "Park in Cockpit for your approval before templating"],
        "ask": "Review the drafted Aurora SOP v0.1. This becomes your repeatable client delivery playbook.",
        "draft": None, "esc": False, "est": 20,
    },
]

@router.post("/evermystic")
async def seed_evermystic(db: AsyncSession = Depends(get_db)):
    """Reset and seed Evermystic SOP phases."""
    # Clear existing
    await db.execute(delete(Job).where(Job.client == "Evermystic"))
    await db.execute(delete(Activity).where(Activity.t.like("%Evermystic%")))

    created = []
    for data in EVERMYSTIC_JOBS:
        job = Job(
            t=data["t"],
            client=data["client"],
            status=data["status"],
            lvl=data["lvl"],
            actor=data["actor"],
            src=data["src"],
            skill=data["skill"],
            steps=data["steps"],
            ask=data["ask"],
            draft=data["draft"],
            esc=data["esc"],
            est=data["est"],
            last_ag=f"Seeded from SOP — {data['src']}",
            last_ts=datetime.now(timezone.utc).isoformat(),
        )
        db.add(job)
        await db.flush()
        await db.refresh(job)
        created.append(job.to_dict())
        await manager.broadcast("job_created", job.to_dict())

    act = Activity(type="info", t=f"Seeded {len(created)} Evermystic SOP phases", ts=datetime.now(timezone.utc).isoformat())
    db.add(act)
    await db.flush()
    await db.refresh(act)
    await manager.broadcast("activity_new", act.to_dict())

    logger.info("seed_evermystic", count=len(created))
    return {"status": "seeded", "count": len(created), "jobs": created}
