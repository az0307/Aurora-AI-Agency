from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base

class Activity(Base):
    __tablename__ = "activity"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)   # ok, info, you, warn, esc
    t = Column(Text, nullable=False)              # text
    ts = Column(String(50), default=lambda: datetime.now(timezone.utc).isoformat())
    job_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "t": self.t,
            "ts": self.ts,
            "job_id": self.job_id,
        }
