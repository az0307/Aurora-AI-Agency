import httpx
import structlog
from app.config import settings

logger = structlog.get_logger()

class N8NBridge:
    """Routes jobs to n8n workflows via webhooks."""

    def __init__(self):
        self.webhook_url = settings.n8n_webhook_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def trigger(self, job_id: int, action: str, payload: dict):
        """Fire an n8n webhook with the job context."""
        body = {
            "job_id": job_id,
            "action": action,
            "payload": payload,
            "callback_url": f"{settings.api_base_url}/api/v1/n8n/callback",
        }
        try:
            resp = await self.client.post(self.webhook_url, json=body)
            resp.raise_for_status()
            logger.info("n8n_triggered", job_id=job_id, action=action, status=resp.status_code)
            return resp.json()
        except httpx.HTTPError as e:
            logger.error("n8n_trigger_failed", job_id=job_id, error=str(e))
            raise

    async def close(self):
        await self.client.aclose()

n8n = N8NBridge()
