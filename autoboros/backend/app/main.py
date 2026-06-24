"""AutoBoros Backend — Real-time agentic orchestration layer."""

import structlog
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import jobs_router, activity_router, ws_router, n8n_router, auth_router, seed_router
from app.routers.auth import get_current_user
from app.services import n8n

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # B2.4 — never boot production with the shipped dev secrets
    if settings.env == "production":
        insecure = []
        if settings.secret_key == "dev-key-change-in-production":
            insecure.append("SECRET_KEY")
        if settings.ab_password == "autoboros":
            insecure.append("AB_PASSWORD")
        if insecure:
            raise RuntimeError(f"refusing to start: default {', '.join(insecure)} in production")
    logger.info("startup", msg="Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("startup", msg="Tables ready")
    yield
    logger.info("shutdown", msg="Cleaning up...")
    await n8n.close()
    await engine.dispose()

app = FastAPI(
    title="AutoBoros Backend",
    description="Real-time API for agentic job orchestration with WebSocket push",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public routes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(n8n_router, prefix="/api/v1")

# Protected routes
app.include_router(seed_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(jobs_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(activity_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(ws_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}

@app.get("/")
async def root():
    return {
        "service": "AutoBoros Backend",
        "version": "2.0.0",
        "endpoints": {
            "jobs": "/api/v1/jobs",
            "activity": "/api/v1/activity",
            "websocket": "/api/v1/ws",
            "n8n_callback": "/api/v1/n8n/callback",
            "n8n_webhook": "/api/v1/n8n/webhook",
            "seed": "/api/v1/seed/evermystic",
            "auth": "/api/v1/auth/login",
            "health": "/health",
        }
    }
