import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.webhook import HubSpotContact
from app.services.hubspot import get_valid_token

HUBSPOT_CONTACTS_URL = "https://api.hubapi.com/crm/v3/objects/contacts"


async def fetch_contact(
    contact_id: int, client_api_key: str, db: AsyncSession
) -> HubSpotContact:
    # Get a valid (auto-refreshed) token for this client
    access_token = await get_valid_token(db, client_api_key)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{HUBSPOT_CONTACTS_URL}/{contact_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"properties": "firstname,lastname,email,company"},
        )
        response.raise_for_status()
        data = response.json()

        return HubSpotContact(
            id=data["id"],
            firstname=data["properties"].get("firstname"),
            lastname=data["properties"].get("lastname"),
            email=data["properties"].get("email"),
            company=data["properties"].get("company"),
        )
