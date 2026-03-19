import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.webhook_processor import process_webhook_events


def make_event(subscription_type: str = "contact.creation", object_id: int = 123):
    return {
        "eventId": 1,
        "subscriptionType": subscription_type,
        "objectId": object_id,
        "occurredAt": 1234567890,
    }


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.enqueue_job = AsyncMock()
    return redis


@patch("app.services.webhook_processor.fetch_contact")
@patch("app.services.webhook_processor.upsert_lead")
async def test_contact_creation_events_are_queued(
    mock_upsert, mock_fetch, mock_db, mock_redis
):
    mock_fetch.return_value = MagicMock(id="123")
    mock_upsert.return_value = MagicMock(id="uuid-lead-id")

    events = [make_event("contact.creation")]
    queued = await process_webhook_events(events, "client-key", mock_db, mock_redis)

    assert queued == 1
    mock_redis.enqueue_job.assert_called_once()


@patch("app.services.webhook_processor.fetch_contact")
@patch("app.services.webhook_processor.upsert_lead")
async def test_non_creation_events_are_filtered_out(
    mock_upsert, mock_fetch, mock_db, mock_redis
):
    events = [
        make_event("contact.propertyChange"),
        make_event("contact.deletion"),
    ]
    queued = await process_webhook_events(events, "client-key", mock_db, mock_redis)

    assert queued == 0
    mock_fetch.assert_not_called()
    mock_redis.enqueue_job.assert_not_called()


async def test_empty_event_list_returns_zero(mock_db, mock_redis):
    queued = await process_webhook_events([], "client-key", mock_db, mock_redis)
    assert queued == 0


@patch("app.services.webhook_processor.fetch_contact")
async def test_failed_contact_fetch_logs_error_and_continues(
    mock_fetch, mock_db, mock_redis
):
    # First contact fails, second succeeds
    mock_fetch.side_effect = [
        Exception("HubSpot API error"),
        MagicMock(id="456"),
    ]

    with patch("app.services.webhook_processor.upsert_lead") as mock_upsert:
        mock_upsert.return_value = MagicMock(id="uuid-lead-id")
        events = [make_event(object_id=123), make_event(object_id=456)]
        queued = await process_webhook_events(events, "client-key", mock_db, mock_redis)

    # Only second contact queued — first failed but didn't crash batch
    assert queued == 1
