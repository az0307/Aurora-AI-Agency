# AutoBoros — Secondary Review Findings
# Scope: post-audit patched codebase (changelog state)
# Method: static analysis of architectural gaps the first pass missed

## 🔴 P0 — New criticals

### [S1] Missing `__all__` exports in `app/__init__.py`
- **File:** `app/__init__.py` (empty)
- **Effect:** `from app import foo` pollutes namespace; circular import risk as project grows.
- **Fix:** Add `__all__ = []` or explicit re-exports.

### [S2] `n8n_bridge.py` — no timeout on `httpx.AsyncClient` requests
- **File:** `app/services/n8n_bridge.py`
- **Effect:** Hanging n8n instance blocks FastAPI event loop indefinitely.
- **Fix:** `httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0))`

### [S3] `ConnectionManager` — no backpressure on broadcast
- **File:** `app/routers/websocket.py`
- **Effect:** Slow WS client causes memory bloat; unbounded `send_text` queue.
- **Fix:** Add `asyncio.wait_for(conn.send_text(msg), timeout=2.0)` + drop on timeout.

## 🟠 P1 — Security / reliability

### [S4] `db_query` in MCP server — no query length limit
- **File:** `mcp/mcp_server.py`
- **Effect:** 10MB SQL string → DoS via memory exhaustion.
- **Fix:** Reject queries > 10KB before execution.

### [S5] JWT `access_token` — no `jti` claim, no revocation
- **File:** `app/routers/auth.py`
- **Effect:** Stolen 30-day token is valid forever; no logout that actually invalidates.
- **Fix:** Add `jti` (UUID), store in Redis/memory with TTL, check on every request. Or switch to short-lived access + refresh tokens.

### [S6] Rate-limit lockout — no distributed state
- **File:** `app/routers/auth.py`
- **Effect:** Multi-process deployment (Fly.io has 2+ VMs) → brute force across instances bypasses the 5-try lock.
- **Fix:** Redis-backed rate limiter (e.g., `slowapi` with Redis store) or Fly.io `fly-replay` to sticky sessions.

### [S7] `localStorage` token — XSS exposure
- **File:** `src/hooks/useAuth.js` (inferred)
- **Effect:** Any XSS payload can exfiltrate `ab_token`.
- **Fix:** Use `httpOnly` cookie (requires SameSite=Strict, CSRF token) OR at minimum `sessionStorage` + short expiry.

## 🟡 P2 — Correctness / robustness

### [S8] Alembic `env.py` — no `target_metadata` set correctly for async
- **File:** `alembic/env.py`
- **Effect:** `alembic revision --autogenerate` may miss tables or generate broken SQL for async engines.
- **Fix:** Ensure `target_metadata = Base.metadata` and `run_migrations_online()` uses `async_engine` with `asyncio.run()` wrapper.

### [S9] `useWebSocket` — reconnect on `token` change never closes old socket
- **File:** `src/hooks/useWebSocket.js` (inferred)
- **Effect:** Rapid login/logout leaks WebSocket connections.
- **Fix:** `useEffect` cleanup must call `ws.close()` unconditionally before opening new connection.

### [S10] `Feed.jsx` — `formatRelative` on every render without memo
- **File:** `src/components/Feed.jsx`
- **Effect:** 1000 activities × re-render = 1000 `Date` calculations.
- **Fix:** `useMemo(() => activities.map(...), [activities])`.

## ⚪ P3 — Debt / polish

### [S11] No structured logging in frontend
- **File:** `src/`
- **Effect:** Production errors are invisible; no Sentry/LogRocket equivalent.
- **Fix:** Add `window.onerror` + `window.onunhandledrejection` handlers that POST to `/api/v1/log` (or use a real service).

### [S12] `docker-compose.yml` — no resource limits on n8n
- **File:** `docker-compose.yml`
- **Effect:** Runaway workflow execution consumes all host RAM.
- **Fix:** Add `deploy.resources.limits.memory: 1g` to n8n service.

### [S13] Missing `Content-Security-Policy` headers
- **File:** `app/main.py`
- **Effect:** XSS payload can load external scripts even without token access.
- **Fix:** Add CSP middleware: `default-src 'self'; script-src 'self'; connect-src 'self' wss:;`

---

## Verdict

The first audit caught all the "won't boot" and "obvious RCE" issues. This secondary pass finds **distributed-systems blind spots** (rate limit shared state, backpressure, JWT revocation) and **frontend production gaps** (CSP, structured logging, XSS token storage). None are blockers for a single-machine demo, but [S5], [S6], and [S7] are mandatory before any multi-user or internet-facing deployment.
