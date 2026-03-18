import httpx
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.settings import get_settings
from app.models.hubspot_token import HubspotToken
from app.schemas.auth import TokenResponse

settings = get_settings()

HUBSPOT_TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"
HUBSPOT_AUTH_URL = "https://app.hubspot.com/oauth/authorize"


def build_auth_url(client_api_key: str) -> str:
    # Pass client_api_key as state so we know which client is connecting on callback
    return (
        f"{HUBSPOT_AUTH_URL}"
        f"?client_id={settings.hubspot_client_id}"
        f"&redirect_uri={settings.hubspot_redirect_uri}"
        f"&scope=crm.objects.contacts.read crm.objects.contacts.write"
        f"&state={client_api_key}"
    )


async def exchange_code_for_token(code: str) -> TokenResponse:
    # Exchange authorization code for access + refresh tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            HUBSPOT_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": settings.hubspot_client_id,
                "client_secret": settings.hubspot_client_secret,
                "redirect_uri": settings.hubspot_redirect_uri,
                "code": code,
            },
        )
        response.raise_for_status()
        data = response.json()
        return TokenResponse(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_in=data["expires_in"],
        )


async def refresh_access_token(refresh_token: str) -> TokenResponse:
    # Use refresh token to get a new access token before it expires
    async with httpx.AsyncClient() as client:
        response = await client.post(
            HUBSPOT_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "client_id": settings.hubspot_client_id,
                "client_secret": settings.hubspot_client_secret,
                "refresh_token": refresh_token,
            },
        )
        response.raise_for_status()
        data = response.json()
        return TokenResponse(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_in=data["expires_in"],
        )


async def save_token(
    db: AsyncSession, client_api_key: str, token: TokenResponse
) -> None:
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=token.expires_in)

    # Upsert — update if exists, insert if new
    result = await db.execute(
        select(HubspotToken).where(HubspotToken.client_api_key == client_api_key)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.access_token = token.access_token
        existing.refresh_token = token.refresh_token
        existing.expires_at = expires_at
    else:
        db.add(HubspotToken(
            client_api_key=client_api_key,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            expires_at=expires_at,
        ))

    await db.commit()


async def get_valid_token(db: AsyncSession, client_api_key: str) -> str:
    # Returns a valid access token — refreshes automatically if expired
    result = await db.execute(
        select(HubspotToken).where(HubspotToken.client_api_key == client_api_key)
    )
    token_record = result.scalar_one_or_none()

    if not token_record:
        raise ValueError(f"No HubSpot token found for client: {client_api_key}")

    # Refresh if token expires within 5 minutes
    now = datetime.now(timezone.utc)
    if token_record.expires_at - now < timedelta(minutes=5):
        new_token = await refresh_access_token(token_record.refresh_token)
        await save_token(db, client_api_key, new_token)
        return new_token.access_token

    return token_record.access_token
