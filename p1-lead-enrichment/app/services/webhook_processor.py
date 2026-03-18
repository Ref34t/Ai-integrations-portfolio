import json
import logging
from arq import ArqRedis
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.webhook import HubSpotEvent
from app.services.hubspot_contacts import fetch_contact

logger = logging.getLogger(__name__)


async def process_webhook_events(
    raw_events: list[dict],
    client_api_key: str,
    db: AsyncSession,
    redis: ArqRedis,
) -> int:
    # Parse and filter to contact creation events only
    events = [HubSpotEvent(**e) for e in raw_events]
    new_contacts = [e for e in events if e.subscriptionType == "contact.creation"]

    if not new_contacts:
        return 0

    queued = 0
    for event in new_contacts:
        try:
            contact = await fetch_contact(event.objectId, client_api_key, db)
            await redis.enqueue_job(
                "process_lead",
                contact.model_dump(),
                client_api_key,
            )
            queued += 1
            logger.info(f"Queued lead: contact_id={event.objectId} client={client_api_key}")
        except Exception as e:
            # Log and continue — don't fail entire batch for one bad contact
            logger.error(f"Failed to queue contact_id={event.objectId}: {e}")
            continue

    return queued
