from datetime import datetime, timedelta, timezone
import time
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# B2.7 — in-memory login throttle (per-process; swap for Redis in multi-worker prod)
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 300
_login_attempts: dict[str, tuple[int, float]] = {}

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
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {"sub": "operator", "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"id": user_id, "name": "Operator"}

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, request: Request):
    # B2.7 — naive per-IP brute-force throttle (single shared password = target).
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    fails, lock_until = _login_attempts.get(ip, (0, 0.0))
    if now < lock_until:
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")

    expected = getattr(settings, 'ab_password', 'autoboros')
    if req.password != expected:
        fails += 1
        lock = now + LOCKOUT_SECONDS if fails >= MAX_ATTEMPTS else 0.0
        _login_attempts[ip] = (0 if lock else fails, lock)
        raise HTTPException(status_code=401, detail="Invalid password")

    _login_attempts.pop(ip, None)
    token = create_token()
    return {"token": token, "user": {"id": "operator", "name": "Operator"}}

@router.get("/me", response_model=UserResponse)
async def me(user: dict = Depends(get_current_user)):
    return user
