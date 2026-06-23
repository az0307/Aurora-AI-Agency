from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Activity
from app.schemas import ActivityResponse

router = APIRouter(prefix="/activity", tags=["activity"])

@router.get("", response_model=List[ActivityResponse])
async def list_activity(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Activity).order_by(desc(Activity.created_at)).limit(limit))
    return [a.to_dict() for a in result.scalars().all()]
