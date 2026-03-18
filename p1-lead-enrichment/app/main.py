from fastapi import FastAPI
from app.core.settings import get_settings
from app.core.enums import AppEnv

settings = get_settings()

app = FastAPI(
    title="P1 Lead Enrichment API",
    version="1.0.0",
    docs_url="/docs" if settings.app_env != AppEnv.production else None,
)


@app.get("/api/v1/health")
async def health() -> dict:
    return {"status": "ok", "env": settings.app_env}
