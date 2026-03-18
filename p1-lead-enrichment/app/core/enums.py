from enum import StrEnum


class AppEnv(StrEnum):
    local = "local"
    staging = "staging"
    production = "production"


class LogLevel(StrEnum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"


class LeadTier(StrEnum):
    hot = "hot"
    cold = "cold"


class LeadStatus(StrEnum):
    pending = "pending"
    notified = "notified"
    archived = "archived"
    flagged = "flagged"  # needs manual review
