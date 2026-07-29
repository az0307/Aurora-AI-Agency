"""Shared-state store for auth security primitives (S5 revocation + S6 rate limit).

Backed by Redis when REDIS_URL is set; otherwise falls back to an in-process
dict with per-key TTLs.

IMPORTANT: the in-process fallback is SINGLE-WORKER ONLY. Across multiple
uvicorn workers or Fly.io VMs the state is NOT shared, so token revocation
(S5) and the login lockout (S6) can be bypassed by hitting a different
instance. Set REDIS_URL in any multi-process / multi-VM deployment.
See docs/SECONDARY_REVIEW.md.
"""
from __future__ import annotations

import time

from app.config import settings

# Redis client is created lazily and cached. `_redis_ready` guards a single
# init attempt so a missing `redis` package or bad URL degrades gracefully to
# the in-process fallback instead of crashing the app on every call.
_redis = None
_redis_ready = False

# In-process fallback: key -> (int_value, expiry_monotonic). expiry == 0 => flag.
_mem: dict[str, tuple[int, float]] = {}


def _get_redis():
    global _redis, _redis_ready
    if _redis_ready:
        return _redis
    _redis_ready = True
    if not settings.redis_url:
        return None
    try:
        import redis.asyncio as aioredis

        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        # redis not installed or URL unusable -> in-process fallback
        _redis = None
    return _redis


def _mem_get(key: str) -> int | None:
    entry = _mem.get(key)
    if entry is None:
        return None
    value, expiry = entry
    if time.monotonic() >= expiry:
        _mem.pop(key, None)
        return None
    return value


async def incr_with_ttl(key: str, ttl: int) -> int:
    """Increment a counter and return the new value. TTL is set on first write
    and preserved across subsequent increments within the window."""
    r = _get_redis()
    if r is not None:
        try:
            value = await r.incr(key)
            if value == 1:
                await r.expire(key, ttl)
            return int(value)
        except Exception:
            pass  # fall through to in-process
    now = time.monotonic()
    entry = _mem.get(key)
    if entry is not None and entry[1] > now:
        value = entry[0] + 1
        _mem[key] = (value, entry[1])
    else:
        value = 1
        _mem[key] = (1, now + ttl)
    return value


async def set_flag(key: str, ttl: int) -> None:
    """Set an existence marker (value 1) with a TTL — used for token revocation."""
    r = _get_redis()
    if r is not None:
        try:
            await r.set(key, "1", ex=ttl)
            return
        except Exception:
            pass
    _mem[key] = (1, time.monotonic() + ttl)


async def exists(key: str) -> bool:
    r = _get_redis()
    if r is not None:
        try:
            return bool(await r.exists(key))
        except Exception:
            pass
    return _mem_get(key) is not None


async def delete(key: str) -> None:
    r = _get_redis()
    if r is not None:
        try:
            await r.delete(key)
            return
        except Exception:
            pass
    _mem.pop(key, None)


def clear() -> None:
    """Reset the in-process store. Test-only helper for isolation between cases."""
    _mem.clear()
