import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.lead_store import upsert_lead
from app.schemas.webhook import HubSpotContact
from app.core.enums import LeadStatus


def make_contact(**kwargs) -> HubSpotContact:
    defaults = {
        "id": "12345",
        "firstname": "John",
        "lastname": "Smith",
        "email": "john@acme.com",
        "company": "Acme Corp",
    }
    return HubSpotContact(**{**defaults, **kwargs})


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    return db


async def test_new_lead_is_inserted_with_pending_status(mock_db):
    # No existing lead in DB
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    contact = make_contact()

    lead = await upsert_lead(mock_db, contact)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    added_lead = mock_db.add.call_args[0][0]
    assert added_lead.status == LeadStatus.pending
    assert added_lead.crm_lead_id == "12345"


async def test_duplicate_lead_updates_existing_record(mock_db):
    # Existing lead already in DB
    existing = MagicMock()
    existing.email = "old@acme.com"
    mock_db.execute.return_value.scalar_one_or_none.return_value = existing

    contact = make_contact(email="new@acme.com")
    await upsert_lead(mock_db, contact)

    # Should update, not insert
    mock_db.add.assert_not_called()
    assert existing.email == "new@acme.com"
    mock_db.commit.assert_called_once()


async def test_name_is_combined_from_firstname_and_lastname(mock_db):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    contact = make_contact(firstname="Jane", lastname="Doe")

    await upsert_lead(mock_db, contact)

    added_lead = mock_db.add.call_args[0][0]
    assert added_lead.name == "Jane Doe"


async def test_name_handles_missing_lastname(mock_db):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    contact = make_contact(firstname="Madonna", lastname=None)

    await upsert_lead(mock_db, contact)

    added_lead = mock_db.add.call_args[0][0]
    assert added_lead.name == "Madonna"


async def test_name_handles_missing_firstname(mock_db):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    contact = make_contact(firstname=None, lastname="Prince")

    await upsert_lead(mock_db, contact)

    added_lead = mock_db.add.call_args[0][0]
    assert added_lead.name == "Prince"
