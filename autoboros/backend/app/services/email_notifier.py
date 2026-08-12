import httpx
import structlog
from app.config import settings

logger = structlog.get_logger()

RESEND_API_URL = "https://api.resend.com/emails"


async def send_job_notification(to: str, subject: str, body: str) -> None:
    """Send a transactional notification email via Resend's REST API.

    Calls Resend directly with httpx (no `resend` SDK dependency, matching the
    n8n bridge's pattern). No-ops with a debug log when RESEND_API_KEY isn't
    configured, so email stays optional and never crashes the app.
    """
    if not settings.resend_api_key:
        logger.debug("email_notification_skipped", reason="no_resend_api_key", to=to)
        return

    payload = {
        "from": settings.email_from,
        "to": to,
        "subject": subject,
        "html": f"<p>{body}</p>",
        "text": body,
    }
    headers = {"Authorization": f"Bearer {settings.resend_api_key}"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(RESEND_API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            logger.info("email_notification_sent", to=to, status=resp.status_code)
    except httpx.HTTPError as e:
        logger.error("email_notification_failed", to=to, error=str(e))
