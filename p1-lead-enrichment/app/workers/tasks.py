import logging

logger = logging.getLogger(__name__)


async def process_lead(ctx: dict, lead_id: str, client_api_key: str) -> None:
    # Background job — receives lead ID and processes it
    # lead_id references the leads table in PostgreSQL
    # Next sprints will add: enrich → score → notify logic here
    logger.info(f"Processing lead: lead_id={lead_id} client={client_api_key}")


class WorkerSettings:
    # arq worker configuration
    functions = [process_lead]
    redis_settings = None  # set dynamically from settings
