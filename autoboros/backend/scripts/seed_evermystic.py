#!/usr/bin/env python3
"""Seed the Autoboros database with Evermystic SOP phases."""

import asyncio
import os
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models import Job, Activity
from app.database import Base

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://autoboros:autoboros@localhost:5432/autoboros')

engine = create_async_engine(DATABASE_URL, echo=False)
sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# B5 — single source of truth: reuse the canonical phase list from the API router
from app.routers.seed import EVERMYSTIC_JOBS

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with sessionmaker() as session:
        # Clear existing Evermystic jobs to avoid duplicates
        from sqlalchemy import delete
        await session.execute(delete(Job).where(Job.client == "Evermystic"))
        await session.execute(delete(Activity).where(Activity.t.like("%Evermystic%")))

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
            session.add(job)

        # Add seed activity log
        act = Activity(type="info", t="Seeded 6 Evermystic SOP phases into Cockpit", ts=datetime.now(timezone.utc).isoformat())
        session.add(act)

        await session.commit()
        print(f"Seeded {len(EVERMYSTIC_JOBS)} Evermystic jobs + 1 activity log")

if __name__ == "__main__":
    asyncio.run(seed())
