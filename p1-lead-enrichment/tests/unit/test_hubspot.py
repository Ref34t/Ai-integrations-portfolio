import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.hubspot import build_auth_url, save_token, get_valid_token
from app.schemas.auth import TokenResponse


def make_token_response(**kwargs) -> TokenResponse:
    defaults = {
        "access_token": "access-abc",
        "refresh_token": "refresh-xyz",
        "expires_in": 3600,
    }
    return TokenResponse(**{**defaults, **kwargs})


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.add = MagicMock()
    return db


# --- build_auth_url ---

def test_build_auth_url_contains_client_id():
    url = build_auth_url("my-client-key")
    assert "client_id=" in url


def test_build_auth_url_contains_state():
    url = build_auth_url("my-client-key")
    assert "state=my-client-key" in url


def test_build_auth_url_contains_scopes():
    url = build_auth_url("my-client-key")
    assert "crm.objects.contacts.read" in url


# --- save_token ---

async def test_save_token_inserts_when_no_existing(mock_db):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    await save_token(mock_db, "client-key", make_token_response())

    mock_db.add.assert_called_once()
    saved = mock_db.add.call_args[0][0]
    assert saved.access_token == "access-abc"
    assert saved.client_api_key == "client-key"
    mock_db.commit.assert_called_once()


async def test_save_token_updates_when_existing(mock_db):
    existing = MagicMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = existing

    await save_token(mock_db, "client-key", make_token_response(access_token="new-access"))

    mock_db.add.assert_not_called()
    assert existing.access_token == "new-access"
    mock_db.commit.assert_called_once()


# --- get_valid_token ---

async def test_get_valid_token_returns_access_token_when_not_expiring(mock_db):
    token_record = MagicMock()
    token_record.access_token = "valid-token"
    token_record.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    mock_db.execute.return_value.scalar_one_or_none.return_value = token_record

    result = await get_valid_token(mock_db, "client-key")

    assert result == "valid-token"


async def test_get_valid_token_refreshes_when_expiring_soon(mock_db):
    token_record = MagicMock()
    token_record.access_token = "old-token"
    token_record.refresh_token = "refresh-xyz"
    # Expires in 3 minutes — under the 5-minute threshold
    token_record.expires_at = datetime.now(timezone.utc) + timedelta(minutes=3)
    mock_db.execute.return_value.scalar_one_or_none.return_value = token_record

    new_token = make_token_response(access_token="refreshed-token")

    with patch("app.services.hubspot.refresh_access_token", return_value=new_token) as mock_refresh:
        with patch("app.services.hubspot.save_token") as mock_save:
            result = await get_valid_token(mock_db, "client-key")

    mock_refresh.assert_called_once_with("refresh-xyz")
    mock_save.assert_called_once()
    assert result == "refreshed-token"


async def test_get_valid_token_raises_when_no_token_found(mock_db):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(ValueError, match="No HubSpot token found"):
        await get_valid_token(mock_db, "unknown-client")
