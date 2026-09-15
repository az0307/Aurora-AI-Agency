from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./autoboros.db"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    # public base URL the API is reachable at (used for n8n callbacks)
    api_base_url: str = "http://localhost:8000"
    log_level: str = "INFO"
    secret_key: str = "dev-key-change-in-production"
    ab_password: str = "autoboros"
    n8n_webhook_url: str = "http://localhost:5678/webhook/autoboros"
    n8n_api_key: str = ""
    resend_api_key: str = ""
    email_from: str = "AutoBoros <noreply@autoborosai.com>"
    mcp_server_url: str = "http://localhost:3001"
    # comma-separated list of allowed browser origins for CORS
    cors_origins: str = "http://localhost:5173,http://localhost:4173"
    # "development" | "production" — production refuses insecure default secrets
    env: str = "development"
    # Redis URL for shared token-revocation + login-throttle state (S5/S6).
    # Empty = in-process fallback (single-worker only). Set in multi-VM prod.
    redis_url: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"

settings = Settings()
