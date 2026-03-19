import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.hubspot_contacts import fetch_contact


def make_hubspot_response(contact_id: str = "42", **props) -> dict:
    defaults = {
        "firstname": "Jane",
        "lastname": "Doe",
        "email": "jane@acme.com",
        "company": "Acme Corp",
    }
    return {"id": contact_id, "properties": {**defaults, **props}}


@pytest.fixture
def mock_db():
    return AsyncMock()


@patch("app.services.hubspot_contacts.get_valid_token", return_value="valid-token")
async def test_fetch_contact_returns_contact_with_correct_fields(mock_token, mock_db):
    api_response = make_hubspot_response(contact_id="42")

    mock_http_response = MagicMock()
    mock_http_response.json.return_value = api_response
    mock_http_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_http_response)
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        contact = await fetch_contact(42, "client-key", mock_db)

    assert contact.id == "42"
    assert contact.firstname == "Jane"
    assert contact.email == "jane@acme.com"


@patch("app.services.hubspot_contacts.get_valid_token", return_value="valid-token")
async def test_fetch_contact_sends_authorization_header(mock_token, mock_db):
    api_response = make_hubspot_response()

    mock_http_response = MagicMock()
    mock_http_response.json.return_value = api_response
    mock_http_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_http_response)
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        await fetch_contact(42, "client-key", mock_db)

    _, call_kwargs = mock_client.get.call_args
    assert call_kwargs["headers"]["Authorization"] == "Bearer valid-token"


@patch("app.services.hubspot_contacts.get_valid_token", return_value="valid-token")
async def test_fetch_contact_handles_missing_optional_fields(mock_token, mock_db):
    # HubSpot may omit optional properties
    api_response = make_hubspot_response(firstname=None, company=None)

    mock_http_response = MagicMock()
    mock_http_response.json.return_value = api_response
    mock_http_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_http_response)
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        contact = await fetch_contact(42, "client-key", mock_db)

    assert contact.firstname is None
    assert contact.company is None


@patch("app.services.hubspot_contacts.get_valid_token", return_value="valid-token")
async def test_fetch_contact_raises_on_http_error(mock_token, mock_db):
    import httpx

    mock_http_response = MagicMock()
    mock_http_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found",
        request=MagicMock(),
        response=MagicMock(),
    )

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_http_response)
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        with pytest.raises(httpx.HTTPStatusError):
            await fetch_contact(999, "client-key", mock_db)
