from pydantic import BaseModel
from datetime import datetime


class OAuthCallbackParams(BaseModel):
    code: str
    state: str  # contains client_api_key for identifying which client is connecting


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int  # seconds until expiry


class AuthStatusResponse(BaseModel):
    client_api_key: str
    connected: bool
    expires_at: datetime | None
