from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Job schemas ---

class JobBase(BaseModel):
    t: str = Field(..., max_length=500)
    client: str = Field(..., max_length=100)
    status: str = Field(..., max_length=50)
    lvl: int = Field(..., ge=0, le=4)
    actor: str = Field(..., max_length=20)
    src: str = Field(..., max_length=100)
    skill: Optional[str] = None
    steps: List[str] = []
    ask: str = ""
    draft: Optional[str] = None
    esc: bool = False
    est: int = 0

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    t: Optional[str] = None
    client: Optional[str] = None
    status: Optional[str] = None
    lvl: Optional[int] = None
    actor: Optional[str] = None
    src: Optional[str] = None
    skill: Optional[str] = None
    steps: Optional[List[str]] = None
    ask: Optional[str] = None
    draft: Optional[str] = None
    esc: Optional[bool] = None
    est: Optional[int] = None
    last_ag: Optional[str] = None
    last_ts: Optional[str] = None
    result_label: Optional[str] = None
    result_url: Optional[str] = None

class JobAction(BaseModel):
    action: str  # approve, reject, ok, veto, done, flag, notion
    draft_text: Optional[str] = None  # for L2 jobs

class JobResponse(JobBase):
    id: int
    last: Dict[str, str]
    result: Optional[Dict[str, str]] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

# --- Activity schemas ---

class ActivityCreate(BaseModel):
    type: str = Field(..., max_length=20)
    t: str
    ts: Optional[str] = None
    job_id: Optional[int] = None

class ActivityResponse(ActivityCreate):
    id: int
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

# --- WebSocket schemas ---

class WSPayload(BaseModel):
    event: str  # job_updated, activity_new, job_created, job_deleted
    data: Dict[str, Any]
