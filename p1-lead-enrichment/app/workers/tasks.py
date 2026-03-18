from arq import ArqRedis
from app.schemas.webhook import HubSpotContact


async def process_lead(ctx: dict, contact: dict, client_api_key: str) -> None:
    # Background job — receives contact data and processes it
    # ctx is provided by arq and contains shared resources (db, redis, etc.)
    # Next sprints will add: enrich → score → notify logic here
    print(f"Processing lead: {contact['id']} for client: {client_api_key}")


class WorkerSettings:
    # arq worker configuration
    functions = [process_lead]
    redis_settings = None  # set dynamically from settings in main.py
