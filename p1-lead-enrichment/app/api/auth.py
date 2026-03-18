from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.hubspot_token import HubspotToken
from app.schemas.auth import AuthStatusResponse
from app.services.hubspot import (
    build_auth_url,
    exchange_code_for_token,
    save_token,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/login")
async def login(client_api_key: str = Query(..., description="Your client API key")):
    # Redirect client to HubSpot OAuth login page
    url = build_auth_url(client_api_key)
    return RedirectResponse(url)


@router.get("/callback")
async def callback(
    code: str = Query(...),
    state: str = Query(...),  # contains client_api_key
    db: AsyncSession = Depends(get_db),
):
    # HubSpot redirects here after user approves — exchange code for tokens
    try:
        token = await exchange_code_for_token(code)
        await save_token(db, client_api_key=state, token=token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth failed: {str(e)}")

    return {"message": "HubSpot connected successfully", "client": state}


@router.get("/status", response_model=AuthStatusResponse)
async def status(
    client_api_key: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    # Check if a client has a valid HubSpot token
    result = await db.execute(
        select(HubspotToken).where(HubspotToken.client_api_key == client_api_key)
    )
    token_record = result.scalar_one_or_none()

    return AuthStatusResponse(
        client_api_key=client_api_key,
        connected=token_record is not None,
        expires_at=token_record.expires_at if token_record else None,
    )
