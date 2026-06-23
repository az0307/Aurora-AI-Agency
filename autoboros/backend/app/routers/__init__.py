from app.routers.jobs import router as jobs_router
from app.routers.activity import router as activity_router
from app.routers.websocket import router as ws_router
from app.routers.n8n import router as n8n_router
from app.routers.auth import router as auth_router
from app.routers.seed import router as seed_router

__all__ = ["jobs_router", "activity_router", "ws_router", "n8n_router", "auth_router", "seed_router"]
