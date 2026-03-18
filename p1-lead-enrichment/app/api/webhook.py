import hashlib
import hmac
import json
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from arq import create_pool
from arq.connections import RedisSettings
from app.core.database import get_db
from app.core.settings import get_settings
from app.schemas.webhook import WebhookResponse
from app.services.webhook_processor import process_webhook_events

settings = get_settings()

router = APIRouter(prefix="/api/v1", tags=["webhook"])


def verify_hubspot_signature(raw_body: bytes, signature: str) -> bool:
    # Verify request is genuinely from HubSpot (PRD Section 23)
    expected = hmac.new(
        settings.hubspot_webhook_secret.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/webhook", response_model=WebhookResponse, status_code=202)
async def webhook(
    request: Request,
    client_api_key: str = Header(..., alias="X-Client-Api-Key"),
    x_hubspot_signature: str = Header(..., alias="X-HubSpot-Signature"),
    db: AsyncSession = Depends(get_db),
):
    # Verify signature
    raw_body = await request.body()
    if not verify_hubspot_signature(raw_body, x_hubspot_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Delegate all processing logic to service
    redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    queued = await process_webhook_events(
        raw_events=json.loads(raw_body),
        client_api_key=client_api_key,
        db=db,
        redis=redis,
    )
    await redis.aclose()

    return WebhookResponse(status="queued", queued=queued)
