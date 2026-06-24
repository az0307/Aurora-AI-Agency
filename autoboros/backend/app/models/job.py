from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, func
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    t = Column(String(500), nullable=False, index=True)           # title
    client = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)       # Inbox, Next, In progress, etc.
    lvl = Column(Integer, nullable=False, index=True)             # 0-4
    actor = Column(String(20), nullable=False)                    # You, Agent, External
    src = Column(String(100), nullable=False)                     # Email, Slack, ManyChat...
    skill = Column(String(100), nullable=True)
    steps = Column(JSON, default=list)                            # ["step 1", "step 2"]
    ask = Column(Text, default="")
    draft = Column(Text, nullable=True)
    esc = Column(Boolean, default=False)
    est = Column(Integer, default=0)                            # minutes saved
    last_ag = Column(String(500), default="")
    last_ts = Column(String(50), default=lambda: datetime.now(timezone.utc).isoformat())
    result_label = Column(String(200), nullable=True)
    result_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "t": self.t,
            "client": self.client,
            "status": self.status,
            "lvl": self.lvl,
            "actor": self.actor,
            "src": self.src,
            "skill": self.skill,
            "steps": self.steps or [],
            "ask": self.ask,
            "draft": self.draft,
            "esc": self.esc,
            "est": self.est,
            "last": {"ag": self.last_ag, "ts": self.last_ts},
            "result": {"label": self.result_label, "url": self.result_url} if self.result_label else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
