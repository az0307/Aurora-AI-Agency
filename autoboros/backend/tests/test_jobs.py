import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager

from app.main import app
from app.config import settings
from app.services import store


@pytest.fixture(autouse=True)
def _reset_security():
    # Isolate the in-process rate-limit / revocation store between cases so a
    # lockout in one test can't 429 the login in the next.
    store.clear()
    yield
    store.clear()


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


async def test_logout_revokes_token(client, auth):
    # S5 — a token works until it is revoked, then it must be rejected.
    r = await client.get("/api/v1/auth/me", headers=auth)
    assert r.status_code == 200

    r = await client.post("/api/v1/auth/logout", headers=auth)
    assert r.status_code == 200

    # Same (now-revoked) token must no longer authenticate.
    r = await client.get("/api/v1/auth/me", headers=auth)
    assert r.status_code == 401
    r = await client.get("/api/v1/jobs", headers=auth)
    assert r.status_code == 401


async def test_rate_limit_locks_after_max_attempts(client):
    # S6 — after MAX_ATTEMPTS bad passwords the IP is locked (429), and the
    # lock applies even to a subsequently-correct password.
    for _ in range(5):
        r = await client.post("/api/v1/auth/login", json={"password": "wrong"})
        assert r.status_code == 401

    r = await client.post("/api/v1/auth/login", json={"password": "wrong"})
    assert r.status_code == 429

    pw = getattr(settings, "ab_password", "autoboros")
    r = await client.post("/api/v1/auth/login", json={"password": pw})
    assert r.status_code == 429


async def test_login_sets_httponly_cookie(client):
    # S7 — login also issues the token as an httpOnly cookie, which alone
    # authenticates subsequent requests (no Authorization header needed).
    pw = getattr(settings, "ab_password", "autoboros")
    r = await client.post("/api/v1/auth/login", json={"password": pw})
    assert r.status_code == 200
    set_cookie = r.headers.get("set-cookie", "")
    assert "ab_token=" in set_cookie
    assert "httponly" in set_cookie.lower()

    # The httpx client keeps the cookie; /me should authenticate via it.
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["id"] == "operator"
