# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Monorepo of 4 production-grade AI integration projects. Only P1 is active; P2–P4 are stubs.

- `p1-lead-enrichment/` — CRM lead enrichment pipeline (FastAPI + Claude + HubSpot)
- `p2-invoice-intelligence/` — Planned
- `p3-content-automation/` — Planned
- `p4-bi-agent/` — Planned

## P1 Development Commands

All commands run from `p1-lead-enrichment/`.

```bash
# Start services (API + PostgreSQL)
docker-compose up --build

# Run API only (requires running DB)
uvicorn app.main:app --reload

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"
alembic downgrade -1

# Install/sync dependencies
uv pip install -r requirements.txt
uv pip freeze > requirements.txt

# Run tests
pytest
pytest tests/unit/
pytest tests/integration/
pytest --cov=app --cov-report=term-missing

# Lint
ruff check .
ruff check . --fix
```

## Architecture (P1)

**Data flow:**
```
HubSpot Webhook → Route (signature verify) → Enrichment Service (Clearbit + Hunter.io)
  → Claude Scoring Service (1–10 score) → Database → Notification Service (Slack/email)
```

**Layer rules (strict):**
- `app/api/` — Route handlers only; no business logic
- `app/services/` — All business logic (enrichment, scoring, notifications)
- `app/schemas/` — Pydantic request/response models
- `app/models/` — SQLAlchemy ORM models
- `app/core/` — Settings, database session, enums

**Key patterns:**
- Async everywhere: FastAPI routes, SQLAlchemy 2.0 async ORM, asyncpg driver
- Settings via `app/core/settings.py` (Pydantic `BaseSettings`, cached with `lru_cache`)
- DB sessions injected via FastAPI `Depends(get_db)`
- All enums in `app/core/enums.py` — use `StrEnum` for type safety

## Code Standards (from CONTRIBUTING.md)

- Max function length: 20 lines
- Type hints required on every function
- No hardcoded values — all config via `.env` + `settings.py`
- No PII in logs (no emails, names, API keys)
- Specific exception handling — never bare `except:`
- Always log before raising exceptions
- Retry logic for all external API calls (Clearbit, Hunter, Claude, HubSpot)

## Testing Requirements

- 80% minimum coverage (enforced by pytest-cov in `pyproject.toml`)
- Unit tests: `tests/unit/test_*_service.py` — mock all external APIs
- Integration tests: `tests/integration/` — test full flows
- `asyncio_mode = "auto"` is configured — no need to mark async tests

## Environment Setup

Copy `.env.example` to `.env` and fill in:
- `ANTHROPIC_API_KEY` — Claude API
- `DATABASE_URL` — PostgreSQL connection string
- `HUBSPOT_CLIENT_ID`, `HUBSPOT_CLIENT_SECRET`, `HUBSPOT_WEBHOOK_SECRET`
- `CLEARBIT_API_KEY`, `HUNTER_API_KEY`
- `SLACK_WEBHOOK_URL`
- `JWT_SECRET` (min 32 chars)

Local Postgres variables (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) are used by docker-compose.

## Git Workflow

- Branch per sprint: `sprint-1`, `sprint-2`, etc.
- Never push directly to `main` — PRs only
- Commit prefix conventions: `feat:`, `fix:`, `test:`, `chore:`, `docs:`
- One commit per sprint task
