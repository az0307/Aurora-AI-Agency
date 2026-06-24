import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager

from app.main import app
from app.config import settings


@pytest.fixture
async def client():
    # LifespanManager runs the app's startup hook -> Base.metadata.create_all,
    # so the jobs/activity tables actually exist for the in-memory test run.
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac


@pytest.fixture
async def auth(client):
    # /auth/login returns {"token": ..., "user": {...}} — field is `token`.
    pw = getattr(settings, "ab_password", "autoboros")
    r = await client.post("/api/v1/auth/login", json={"password": pw})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


async def test_login_rejects_bad_password(client):
    r = await client.post("/api/v1/auth/login", json={"password": "wrong"})
    assert r.status_code == 401


async def test_jobs_require_auth(client):
    # protected route with no token must 401, not 201
    r = await client.post("/api/v1/jobs", json={"t": "x", "client": "Internal", "status": "Inbox"})
    assert r.status_code == 401


async def test_create_list_action_delete(client, auth):
    payload = {
        "t": "Test job",
        "client": "Internal",
        "status": "Inbox",
        "lvl": 2,
        "actor": "Agent",
        "src": "Test",
        "ask": "Test ask",
    }
    r = await client.post("/api/v1/jobs", json=payload, headers=auth)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["t"] == "Test job"
    job_id = data["id"]

    r = await client.get("/api/v1/jobs", headers=auth)
    assert r.status_code == 200
    assert any(j["id"] == job_id for j in r.json())

    r = await client.post(f"/api/v1/jobs/{job_id}/action", json={"action": "done"}, headers=auth)
    assert r.status_code == 200
    assert r.json()["status"] == "Done"

    r = await client.delete(f"/api/v1/jobs/{job_id}", headers=auth)
    assert r.status_code == 200
