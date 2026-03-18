import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.lead import Lead
from app.core.enums import LeadStatus
from app.schemas.webhook import HubSpotContact

logger = logging.getLogger(__name__)


async def upsert_lead(db: AsyncSession, contact: HubSpotContact) -> Lead:
    # Check if lead already exists by HubSpot contact ID
    result = await db.execute(
        select(Lead).where(Lead.crm_lead_id == contact.id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update with latest data from HubSpot
        existing.name = f"{contact.firstname or ''} {contact.lastname or ''}".strip()
        existing.email = contact.email
        existing.company = contact.company
        logger.info(f"Updated existing lead: crm_lead_id={contact.id}")
    else:
        # Insert new lead with pending status
        existing = Lead(
            crm_lead_id=contact.id,
            name=f"{contact.firstname or ''} {contact.lastname or ''}".strip(),
            email=contact.email,
            company=contact.company,
            status=LeadStatus.pending,
        )
        db.add(existing)
        logger.info(f"Stored new lead: crm_lead_id={contact.id}")

    await db.commit()
    await db.refresh(existing)
    return existing
