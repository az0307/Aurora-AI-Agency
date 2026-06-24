from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Job, Activity
from app.schemas import JobCreate, JobUpdate, JobResponse, JobAction, ActivityCreate
from app.services import manager, n8n
import structlog

router = APIRouter(prefix="/jobs", tags=["jobs"])
logger = structlog.get_logger()


def _now() -> str:
    """UTC ISO-8601 timestamp (replaces the literal 'now' placeholder)."""
    return datetime.now(timezone.utc).isoformat()

@router.get("", response_model=List[JobResponse])
async def list_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).order_by(desc(Job.updated_at)))
    return [j.to_dict() for j in result.scalars().all()]

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.to_dict()

@router.post("", response_model=JobResponse, status_code=201)
async def create_job(job: JobCreate, db: AsyncSession = Depends(get_db)):
    db_job = Job(
        t=job.t,
        client=job.client,
        status=job.status,
        lvl=job.lvl,
        actor=job.actor,
        src=job.src,
        skill=job.skill,
        steps=job.steps,
        ask=job.ask,
        draft=job.draft,
        esc=job.esc,
        est=job.est,
        last_ag="Created via API",
        last_ts=_now(),
    )
    db.add(db_job)
    await db.flush()
    await db.refresh(db_job)

    await manager.broadcast("job_created", db_job.to_dict())
    await _log_activity(db, "info", f"Created new job: {db_job.t}", db_job.id)
    logger.info("job_created", job_id=db_job.id, title=db_job.t)
    return db_job.to_dict()

@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(job_id: int, update: JobUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    changed = False
    for field, value in update.model_dump(exclude_unset=True).items():
        if field in ("last_ag", "last_ts", "result_label", "result_url"):
            setattr(job, field, value)
        elif hasattr(job, field) and getattr(job, field) != value:
            setattr(job, field, value)
            changed = True

    if changed:
        await db.flush()
        await db.refresh(job)
        await manager.broadcast("job_updated", job.to_dict())
        logger.info("job_updated", job_id=job_id)

    return job.to_dict()

@router.post("/{job_id}/action")
async def job_action(job_id: int, action: JobAction, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    kind = action.action
    updates = {}
    log_type = "info"
    log_msg = ""

    if kind == "approve":
        updates = {"status": "Done", "actor": "Agent", "esc": False, "last_ag": "Sent after your approval", "last_ts": _now()}
        log_type, log_msg = "ok", f"Sent after approval — {job.t}"
    elif kind == "reject":
        updates = {"status": "Done", "actor": "You", "last_ag": "Draft rejected by you — closed", "last_ts": _now()}
        log_type, log_msg = "you", f"You rejected the draft — {job.t}"
    elif kind == "ok":
        updates = {"last_ag": "You confirmed — agent continuing", "last_ts": _now()}
        log_type, log_msg = "info", f"You confirmed the agent's action — {job.t}"
    elif kind == "veto":
        updates = {"status": "Waiting on you", "actor": "You", "last_ag": "Vetoed — handed to you", "last_ts": _now()}
        log_type, log_msg = "you", f"You vetoed — now needs you: {job.t}"
    elif kind == "done":
        updates = {"status": "Done", "esc": False, "last_ag": "Marked done by you", "last_ts": _now()}
        log_type, log_msg = "you", f"You marked it done — {job.t}"
    elif kind == "flag":
        updates = {"last_ag": "Flagged by you for review", "last_ts": _now()}
        log_type, log_msg = "warn", f"You flagged for review — {job.t}"
    elif kind == "notion":
        return {"status": "noop", "message": "Opening in Notion…"}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {kind}")

    for k, v in updates.items():
        setattr(job, k, v)
    if action.draft_text is not None and job.lvl == 2:
        job.draft = action.draft_text

    await db.flush()
    await db.refresh(job)

    await manager.broadcast("job_updated", job.to_dict())
    await _log_activity(db, log_type, log_msg, job_id)

    # B4.2 — L4 jobs complete autonomously; surface that to n8n too (not just approve/ok)
    if (kind in ("approve", "ok") and job.lvl >= 3) or (kind == "done" and job.lvl >= 4):
        try:
            await n8n.trigger(job_id, kind, job.to_dict())
        except Exception as e:
            logger.error("n8n_trigger_failed", job_id=job_id, error=str(e))

    logger.info("job_action", job_id=job_id, action=kind)
    return job.to_dict()

@router.delete("/{job_id}")
async def delete_job(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    title = job.t
    await db.delete(job)
    await manager.broadcast("job_deleted", {"id": job_id, "t": title})
    await _log_activity(db, "warn", f"Deleted job: {title}", job_id)
    logger.info("job_deleted", job_id=job_id)
    return {"status": "deleted", "id": job_id}

async def _log_activity(db: AsyncSession, typ: str, text: str, job_id: int = None):
    act = Activity(type=typ, t=text, ts=_now(), job_id=job_id)
    db.add(act)
    await db.flush()
    await db.refresh(act)
    await manager.broadcast("activity_new", act.to_dict())
