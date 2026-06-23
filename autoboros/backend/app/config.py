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
    mcp_server_url: str = "http://localhost:3001"
    # comma-separated list of allowed browser origins for CORS
    cors_origins: str = "http://localhost:5173,http://localhost:4173"
    # "development" | "production" — production refuses insecure default secrets
    env: str = "development"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"

settings = Settings()
