from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Job, Activity
from app.services import manager
from app.config import settings
import structlog

router = APIRouter(prefix="/n8n", tags=["n8n"])
logger = structlog.get_logger()

def verify_n8n_key(x_n8n_key: str = Header(None)):
    expected = getattr(settings, 'n8n_api_key', '')
    if not expected or x_n8n_key != expected:
        raise HTTPException(status_code=403, detail="Invalid n8n API key")
    return True

@router.post("/callback")
async def n8n_callback(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_n8n_key),
):
    job_id = payload.get("job_id")
    result = payload.get("result", {})

    if not job_id:
        raise HTTPException(status_code=400, detail="job_id required")

    res = await db.execute(select(Job).where(Job.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = result.get("status", job.status)
    job.actor = result.get("actor", job.actor)
    job.last_ag = result.get("last_ag", "n8n completed workflow")
    job.last_ts = datetime.now(timezone.utc).isoformat()
    if result.get("result_label"):
        job.result_label = result["result_label"]
        job.result_url = result.get("result_url", "")

    await db.flush()
    await db.refresh(job)

    await manager.broadcast("job_updated", job.to_dict())

    act = Activity(
        type="ok",
        t=result.get("activity_text", f"n8n completed: {job.t}"),
        ts=datetime.now(timezone.utc).isoformat(),
        job_id=job_id,
    )
    db.add(act)
    await db.flush()
    await db.refresh(act)
    await manager.broadcast("activity_new", act.to_dict())

    logger.info("n8n_callback_processed", job_id=job_id)
    return {"status": "ok", "job_id": job_id}

@router.post("/webhook")
async def n8n_inbound(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_n8n_key),
):
    event = payload.get("event")

    if event == "new_job":
        job_data = payload.get("job", {})
        job = Job(
            t=job_data.get("t", "Untitled"),
            client=job_data.get("client", "Internal"),
            status=job_data.get("status", "Inbox"),
            lvl=job_data.get("lvl", 2),
            actor=job_data.get("actor", "Agent"),
            src=job_data.get("src", "n8n"),
            skill=job_data.get("skill"),
            steps=job_data.get("steps", []),
            ask=job_data.get("ask", ""),
            draft=job_data.get("draft"),
            esc=job_data.get("esc", False),
            est=job_data.get("est", 0),
            last_ag="Created by n8n workflow",
            last_ts=datetime.now(timezone.utc).isoformat(),
        )
        db.add(job)
        await db.flush()
        await db.refresh(job)
        await manager.broadcast("job_created", job.to_dict())

        act = Activity(type="info", t=f"n8n created job: {job.t}", ts=datetime.now(timezone.utc).isoformat(), job_id=job.id)
        db.add(act)
        await db.flush()
        await manager.broadcast("activity_new", act.to_dict())

        logger.info("n8n_inbound_new_job", job_id=job.id)
        return {"status": "created", "job_id": job.id}

    if event == "alert":
        act = Activity(type="warn", t=payload.get("text", "n8n alert"), ts=datetime.now(timezone.utc).isoformat())
        db.add(act)
        await db.flush()
        await manager.broadcast("activity_new", act.to_dict())
        return {"status": "logged"}

    return {"status": "ignored", "event": event}
