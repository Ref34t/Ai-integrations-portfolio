from pydantic_settings import BaseSettings
from functools import lru_cache
from app.core.enums import AppEnv, LogLevel


class Settings(BaseSettings):
    # App
    app_env: AppEnv = AppEnv.local
    log_level: LogLevel = LogLevel.info
    hot_lead_threshold: int = 7

    # HubSpot
    hubspot_client_id: str
    hubspot_client_secret: str
    hubspot_redirect_uri: str
    hubspot_webhook_secret: str

    # Enrichment
    clearbit_api_key: str
    hunter_api_key: str

    # Claude
    anthropic_api_key: str

    # Slack
    slack_webhook_url: str
    slack_fallback_email: str

    # Database
    database_url: str

    # Security
    jwt_secret: str
    jwt_expiry_minutes: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    # Cached so settings are only loaded once per process lifetime
    return Settings()
