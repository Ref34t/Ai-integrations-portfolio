from pydantic import BaseModel


class HubSpotEvent(BaseModel):
    eventId: int
    subscriptionType: str
    objectId: int  # HubSpot contact ID
    occurredAt: int  # Unix timestamp


class HubSpotContact(BaseModel):
    id: str
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    company: str | None = None


class WebhookResponse(BaseModel):
    status: str
    queued: int  # number of events queued
