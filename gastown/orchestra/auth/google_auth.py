"""
Google OAuth Authentication System
Secure multi-user authentication for Orchestra Town
"""

import json
import secrets
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from pathlib import Path


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
        """Get default permissions"""
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
        """Check if session is still valid"""
        return self.active and datetime.now() < self.expires_at

    def refresh(self):
        """Refresh session expiration"""
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
    Manages Google OAuth authentication
    Integration point for Google OAuth 2.0
    """

    def __init__(self, state_dir: str = "/root/gastown/orchestra/state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}

        # OAuth configuration (to be filled with actual credentials)
        self.oauth_config = {
            "client_id": "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uri": "http://localhost:5000/auth/callback",
            "scopes": [
                "openid",
                "email",
                "profile"
            ],
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo"
        }

        self.load_state()

    def get_auth_url(self, state: str = None) -> str:
        """
        Get Google OAuth authorization URL
        Integration point for actual OAuth flow
        """
        if not state:
            state = secrets.token_urlsafe(16)

        params = {
            "client_id": self.oauth_config["client_id"],
            "redirect_uri": self.oauth_config["redirect_uri"],
            "response_type": "code",
            "scope": " ".join(self.oauth_config["scopes"]),
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.oauth_config['auth_url']}?{query_string}"

    def exchange_code(self, code: str) -> Optional[Dict]:
        """
        Exchange authorization code for tokens
        Integration point for actual OAuth token exchange
        """
        # This would make actual API call to Google
        # For now, return integration configuration
        return {
            "status": "ready_for_integration",
            "method": "POST",
            "url": self.oauth_config["token_url"],
            "payload": {
                "code": code,
                "client_id": self.oauth_config["client_id"],
                "client_secret": self.oauth_config["client_secret"],
                "redirect_uri": self.oauth_config["redirect_uri"],
                "grant_type": "authorization_code"
            },
            "expected_response": {
                "access_token": "ya29.xxx",
                "refresh_token": "1//xxx",
                "expires_in": 3600,
                "token_type": "Bearer",
                "id_token": "eyJxxx"
            }
        }

    def get_user_info(self, access_token: str) -> Optional[Dict]:
        """
        Get user information from Google
        Integration point for actual API call
        """
        # This would make actual API call to Google
        return {
            "status": "ready_for_integration",
            "method": "GET",
            "url": self.oauth_config["userinfo_url"],
            "headers": {
                "Authorization": f"Bearer {access_token}"
            },
            "expected_response": {
                "id": "1234567890",
                "email": "user@example.com",
                "verified_email": True,
                "name": "John Doe",
                "given_name": "John",
                "family_name": "Doe",
                "picture": "https://lh3.googleusercontent.com/..."
            }
        }

    def create_session(self, google_id: str, email: str, name: str, picture: str = None) -> Session:
        """Create a new user session"""
        # Check if user exists
        user = self.users.get(google_id)
        if not user:
            user = User(google_id, email, name, picture)
            self.users[google_id] = user
        else:
            user.last_login = datetime.now().isoformat()

        # Create session
        session = Session(user)
        self.sessions[session.token] = session

        self.save_state()
        return session

    def verify_session(self, token: str) -> Optional[User]:
        """Verify session token and return user"""
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
        """Get user by Google ID"""
        return self.users.get(google_id)

    def list_users(self) -> List[User]:
        """List all users"""
        return list(self.users.values())

    def update_permissions(self, google_id: str, permissions: Dict) -> bool:
        """Update user permissions"""
        user = self.users.get(google_id)
        if not user:
            return False

        user.permissions.update(permissions)
        self.save_state()
        return True

    def promote_to_admin(self, google_id: str) -> bool:
        """Promote user to admin"""
        user = self.users.get(google_id)
        if not user:
            return False

        user.role = "admin"
        user.permissions = {
            "create_tasks": True,
            "view_tasks": True,
            "delete_tasks": True,
            "manage_agents": True,
            "view_mayor_thinking": True,
            "chat_with_mayor": True,
            "execute_utilities": True,
            "manage_users": True
        }
        self.save_state()
        return True

    def save_state(self):
        """Save users and sessions to disk"""
        state_file = self.state_dir / "auth.json"
        state = {
            "users": {uid: user.to_dict() for uid, user in self.users.items()},
            "sessions": {token: sess.to_dict() for token, sess in self.sessions.items() if sess.is_valid()}
        }
        state_file.write_text(json.dumps(state, indent=2))

    def load_state(self):
        """Load users and sessions from disk"""
        state_file = self.state_dir / "auth.json"
        if state_file.exists():
            data = json.loads(state_file.read_text())

            # Load users
            for uid, user_data in data.get("users", {}).items():
                user = User(
                    user_data["id"],
                    user_data["email"],
                    user_data["name"],
                    user_data.get("picture")
                )
                user.role = user_data.get("role", "user")
                user.permissions = user_data.get("permissions", user._default_permissions())
                user.created_at = user_data.get("created_at")
                user.last_login = user_data.get("last_login")
                self.users[uid] = user

    def get_stats(self) -> Dict:
        """Get authentication statistics"""
        active_sessions = sum(1 for s in self.sessions.values() if s.is_valid())

        return {
            "total_users": len(self.users),
            "active_sessions": active_sessions,
            "users_by_role": {
                "admin": sum(1 for u in self.users.values() if u.role == "admin"),
                "user": sum(1 for u in self.users.values() if u.role == "user"),
                "viewer": sum(1 for u in self.users.values() if u.role == "viewer")
            }
        }


# OAuth Integration Configuration
GOOGLE_OAUTH_INTEGRATION = {
    "setup_steps": [
        "1. Go to Google Cloud Console: https://console.cloud.google.com/",
        "2. Create a new project or select existing",
        "3. Enable Google+ API",
        "4. Create OAuth 2.0 credentials (Web application)",
        "5. Add authorized redirect URI: http://localhost:5000/auth/callback",
        "6. Copy Client ID and Client Secret",
        "7. Update oauth_config in GoogleAuthManager"
    ],
    "dependencies": {
        "pip install google-auth google-auth-oauthlib google-auth-httplib2"
    },
    "flask_routes": {
        "/auth/login": "Redirect to Google OAuth",
        "/auth/callback": "Handle OAuth callback",
        "/auth/logout": "Logout user",
        "/auth/me": "Get current user info"
    },
    "security_best_practices": [
        "Use HTTPS in production",
        "Store client_secret in environment variables",
        "Implement CSRF protection with state parameter",
        "Set secure session cookies",
        "Validate redirect_uri",
        "Implement rate limiting",
        "Log authentication attempts"
    ],
    "example_flask_integration": """
from flask import Flask, redirect, request, session
from auth.google_auth import GoogleAuthManager

auth_manager = GoogleAuthManager()

@app.route('/auth/login')
def login():
    auth_url = auth_manager.get_auth_url()
    return redirect(auth_url)

@app.route('/auth/callback')
def callback():
    code = request.args.get('code')
    # Exchange code for tokens
    tokens = auth_manager.exchange_code(code)
    # Get user info
    user_info = auth_manager.get_user_info(tokens['access_token'])
    # Create session
    session_obj = auth_manager.create_session(
        user_info['id'],
        user_info['email'],
        user_info['name'],
        user_info.get('picture')
    )
    session['token'] = session_obj.token
    return redirect('/dashboard')

@app.route('/auth/logout')
def logout():
    token = session.get('token')
    auth_manager.logout(token)
    session.clear()
    return redirect('/')

@app.before_request
def check_auth():
    if request.path.startswith('/auth/'):
        return  # Auth routes don't need authentication

    token = session.get('token')
    user = auth_manager.verify_session(token)
    if not user:
        return redirect('/auth/login')

    request.user = user
"""
}
