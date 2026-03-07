"""
Google OAuth Authentication System
Secure multi-user authentication for Orchestra Town.
Supports real OAuth flow when credentials are configured, with demo mode fallback.
"""

import json
import secrets
import os
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

try:
    import urllib.request
    import urllib.error
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False


class User:
    """Represents an authenticated user"""

    def __init__(self, google_id: str, email: str, name: str, picture: str = None):
        self.id = google_id
        self.email = email
        self.name = name
        self.picture = picture
        self.created_at = datetime.now().isoformat()
        self.last_login = datetime.now().isoformat()
        self.role = "user"  # user, admin, viewer
        self.permissions = self._default_permissions()

    def _default_permissions(self) -> Dict:
        return {
            "create_tasks": True,
            "view_tasks": True,
            "delete_tasks": False,
            "manage_agents": False,
            "view_mayor_thinking": True,
            "chat_with_mayor": True,
            "execute_utilities": False,
            "manage_users": False
        }

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "picture": self.picture,
            "role": self.role,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "permissions": self.permissions
        }


class Session:
    """User session management"""

    def __init__(self, user: User):
        self.token = secrets.token_urlsafe(32)
        self.user = user
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(hours=24)
        self.active = True

    def is_valid(self) -> bool:
        return self.active and datetime.now() < self.expires_at

    def refresh(self):
        self.expires_at = datetime.now() + timedelta(hours=24)

    def to_dict(self) -> Dict:
        return {
            "token": self.token,
            "user": self.user.to_dict(),
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "active": self.active
        }


class GoogleAuthManager:
    """
    Manages Google OAuth authentication.
    Uses real OAuth when credentials are configured via environment variables:
      GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
    Falls back to demo mode when not configured.
    """

    def __init__(self, state_dir: str = None):
        base = Path(__file__).parent.parent
        self.state_dir = Path(state_dir) if state_dir else base / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.pending_states: Dict[str, str] = {}  # state -> timestamp

        # OAuth configuration from environment
        self.client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
        self.client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")
        self.redirect_uri = os.environ.get(
            "GOOGLE_REDIRECT_URI",
            "http://localhost:5000/auth/callback"
        )

        self.oauth_config = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scopes": ["openid", "email", "profile"],
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo"
        }

        self.load_state()

    @property
    def is_configured(self) -> bool:
        """Check if real OAuth credentials are configured"""
        return bool(self.client_id and self.client_secret)

    @property
    def mode(self) -> str:
        return "live" if self.is_configured else "demo"

    def get_auth_url(self, state: str = None) -> str:
        """Get Google OAuth authorization URL"""
        if not state:
            state = secrets.token_urlsafe(16)
        self.pending_states[state] = datetime.now().isoformat()

        params = {
            "client_id": self.client_id or "DEMO_CLIENT_ID",
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.oauth_config["scopes"]),
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }

        return f"{self.oauth_config['auth_url']}?{urlencode(params)}"

    def exchange_code(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for tokens"""
        if not self.is_configured:
            return self._demo_exchange(code)

        if not HAS_URLLIB:
            return {"error": "urllib not available"}

        try:
            data = urlencode({
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code"
            }).encode("utf-8")

            req = urllib.request.Request(
                self.oauth_config["token_url"],
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e)}

    def get_user_info(self, access_token: str) -> Optional[Dict]:
        """Get user information from Google"""
        if not self.is_configured:
            return self._demo_user_info()

        if not HAS_URLLIB:
            return {"error": "urllib not available"}

        try:
            req = urllib.request.Request(
                self.oauth_config["userinfo_url"],
                headers={"Authorization": f"Bearer {access_token}"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e)}

    def _demo_exchange(self, code: str) -> Dict:
        """Demo mode token exchange"""
        return {
            "access_token": f"demo_token_{secrets.token_hex(8)}",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "openid email profile",
            "mode": "demo"
        }

    def _demo_user_info(self) -> Dict:
        """Demo mode user info"""
        return {
            "id": "demo_user_001",
            "email": "demo@orchestra.town",
            "verified_email": True,
            "name": "Demo User",
            "given_name": "Demo",
            "family_name": "User",
            "picture": None,
            "mode": "demo"
        }

    def login_demo(self) -> Session:
        """Quick login for demo mode (no Google required)"""
        info = self._demo_user_info()
        return self.create_session(
            info["id"], info["email"], info["name"], info.get("picture")
        )

    def create_session(self, google_id: str, email: str,
                       name: str, picture: str = None) -> Session:
        """Create a new user session"""
        user = self.users.get(google_id)
        if not user:
            user = User(google_id, email, name, picture)
            self.users[google_id] = user
        else:
            user.last_login = datetime.now().isoformat()

        session = Session(user)
        self.sessions[session.token] = session
        self.save_state()
        return session

    def verify_session(self, token: str) -> Optional[User]:
        """Verify session token and return user"""
        if not token:
            return None
        session = self.sessions.get(token)
        if not session:
            return None
        if not session.is_valid():
            session.active = False
            return None
        session.refresh()
        return session.user

    def logout(self, token: str):
        """Logout user session"""
        session = self.sessions.get(token)
        if session:
            session.active = False
            self.save_state()

    def get_user(self, google_id: str) -> Optional[User]:
        return self.users.get(google_id)

    def list_users(self) -> List[User]:
        return list(self.users.values())

    def update_permissions(self, google_id: str, permissions: Dict) -> bool:
        user = self.users.get(google_id)
        if not user:
            return False
        user.permissions.update(permissions)
        self.save_state()
        return True

    def promote_to_admin(self, google_id: str) -> bool:
        user = self.users.get(google_id)
        if not user:
            return False
        user.role = "admin"
        user.permissions = {k: True for k in user.permissions}
        self.save_state()
        return True

    def save_state(self):
        state_file = self.state_dir / "auth.json"
        state = {
            "users": {uid: user.to_dict() for uid, user in self.users.items()},
            "sessions": {
                token: sess.to_dict()
                for token, sess in self.sessions.items()
                if sess.is_valid()
            }
        }
        state_file.write_text(json.dumps(state, indent=2))

    def load_state(self):
        state_file = self.state_dir / "auth.json"
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
                for uid, user_data in data.get("users", {}).items():
                    user = User(
                        user_data["id"], user_data["email"],
                        user_data["name"], user_data.get("picture")
                    )
                    user.role = user_data.get("role", "user")
                    user.permissions = user_data.get(
                        "permissions", user._default_permissions()
                    )
                    user.created_at = user_data.get("created_at")
                    user.last_login = user_data.get("last_login")
                    self.users[uid] = user
            except (json.JSONDecodeError, KeyError):
                pass

    def get_stats(self) -> Dict:
        active_sessions = sum(1 for s in self.sessions.values() if s.is_valid())
        return {
            "mode": self.mode,
            "configured": self.is_configured,
            "total_users": len(self.users),
            "active_sessions": active_sessions,
            "users_by_role": {
                role: sum(1 for u in self.users.values() if u.role == role)
                for role in ["admin", "user", "viewer"]
            }
        }
