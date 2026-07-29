from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from app.config import settings
from app.services import store

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# S7 — token may also ride in an httpOnly cookie (set on login, cleared on
# logout). The Authorization header path still works unchanged, so this is
# purely additive: the frontend can migrate off localStorage without a flag day.
COOKIE_NAME = "ab_token"

# B2.7 / S6 — login throttle. State lives in `app.services.store`, which is
# Redis-backed when REDIS_URL is set and in-process otherwise. In-process is
# single-worker only, so a multi-VM deploy must set REDIS_URL or the 5-try lock
# is bypassable across instances.
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 300

class LoginRequest(BaseModel):
    password: str

class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: str
    name: str

# Simple password auth — in production, use hashed passwords + user DB
# For now, single password from env

def create_token():
    # S5 — every token carries a unique `jti` so it can be individually revoked.
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {"sub": "operator", "exp": expire, "iat": now, "jti": uuid4().hex}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)

def decode_token(token: str) -> dict | None:
    """Verify signature + expiry only. Returns the payload or None."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return None

async def authenticate_token(token: str) -> str | None:
    """Full check: valid signature/expiry AND not revoked (S5). Returns sub."""
    payload = decode_token(token)
    if not payload:
        return None
    jti = payload.get("jti")
    if jti and await store.exists(f"revoked_jti:{jti}"):
        return None
    return payload.get("sub")

def _extract_token(request: Request, credentials: HTTPAuthorizationCredentials | None) -> str | None:
    # Authorization header wins; fall back to the httpOnly cookie (S7).
    if credentials:
        return credentials.credentials
    return request.cookies.get(COOKIE_NAME)

async def get_current_payload(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = _extract_token(request, credentials)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    jti = payload.get("jti")
    if jti and await store.exists(f"revoked_jti:{jti}"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")
    return payload

async def get_current_user(payload: dict = Depends(get_current_payload)):
    return {"id": payload.get("sub"), "name": "Operator"}

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, request: Request, response: Response):
    # B2.7 / S6 — naive per-IP brute-force throttle (single shared password = target).
    ip = request.client.host if request.client else "unknown"
    if await store.exists(f"login_lock:{ip}"):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")

    expected = getattr(settings, 'ab_password', 'autoboros')
    if req.password != expected:
        fails = await store.incr_with_ttl(f"login_fails:{ip}", LOCKOUT_SECONDS)
        if fails >= MAX_ATTEMPTS:
            await store.set_flag(f"login_lock:{ip}", LOCKOUT_SECONDS)
            await store.delete(f"login_fails:{ip}")
        raise HTTPException(status_code=401, detail="Invalid password")

    await store.delete(f"login_fails:{ip}")
    await store.delete(f"login_lock:{ip}")
    token = create_token()
    # S7 — also hand the token back as an httpOnly cookie. `secure` in prod only
    # (HTTPS); SameSite=strict blunts CSRF for the cookie path.
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="strict",
        secure=settings.env == "production",
        max_age=ACCESS_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/",
    )
    return {"token": token, "user": {"id": "operator", "name": "Operator"}}

@router.post("/logout")
async def logout(response: Response, payload: dict = Depends(get_current_payload)):
    # S5 — revoke this token's jti for its remaining lifetime, then clear the cookie.
    jti = payload.get("jti")
    exp = payload.get("exp")
    if jti and exp:
        ttl = int(exp - datetime.now(timezone.utc).timestamp())
        if ttl > 0:
            await store.set_flag(f"revoked_jti:{jti}", ttl)
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"ok": True}

@router.get("/me", response_model=UserResponse)
async def me(user: dict = Depends(get_current_user)):
    return user
