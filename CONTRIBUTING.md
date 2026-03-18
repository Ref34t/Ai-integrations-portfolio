# Contributing Guide — P1: AI-Powered CRM Lead Enrichment

This document defines the A+ code standards for this project.
Every task must meet these standards before it is considered done.

---

## 1. Project Structure

```
p1-lead-enrichment/
├── app/
│   ├── api/          # FastAPI routes only — no business logic
│   ├── services/     # One file per service (enrich, score, notify)
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic request/response validation
│   ├── core/         # Config, settings, constants
│   └── utils/        # Shared helpers
├── tests/
│   ├── unit/
│   └── integration/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt
└── README.md
```

---

## 2. Code Quality Rules

- **No business logic in routes** — routes only call services
- **No hardcoded values** — everything in `.env` + `settings.py`
- **Pydantic everywhere** — validate every input and output
- **Type hints on every function** — no bare `def func(x)`
- **One responsibility per function** — if it does 2 things, split it
- **Max function length: 20 lines** — if longer, refactor

### Good Example
```python
async def score_lead(lead: EnrichedLead) -> LeadScore:
    prompt = build_scoring_prompt(lead)
    response = await call_claude(prompt)
    return parse_score_response(response)
```

### Bad Example
```python
async def process(data):
    # enriches, scores, notifies all in one function — never do this
    ...
```

---

## 3. Error Handling

- **Never use bare `except:`** — always catch specific exceptions
- **Always log before raising** — never silent failures
- **Return meaningful errors** — not just `500 Internal Server Error`
- **Every external API call wrapped** in try/except with retry logic

### Good Example
```python
try:
    response = await clearbit.enrich(email)
except ClearbitRateLimitError as e:
    logger.warning(f"Clearbit rate limit hit for {email}: {e}")
    raise EnrichmentUnavailableError("Clearbit rate limit exceeded")
```

### Bad Example
```python
try:
    response = await clearbit.enrich(email)
except:
    pass  # never do this
```

---

## 4. Testing Standards

- **Every service has unit tests** — mock all external APIs
- **Every happy path tested** — and at least 2 edge cases per service
- **Integration test covers full flow** — webhook to Slack
- **Minimum 80% code coverage**

### Test File Naming
```
tests/unit/test_enrich_service.py
tests/unit/test_score_service.py
tests/unit/test_notify_service.py
tests/integration/test_full_flow.py
```

### Good Test Example
```python
def test_score_lead_returns_hot_for_high_quality_lead():
    lead = EnrichedLead(company_size=200, email_valid=True, title="CEO")
    result = score_lead(lead)
    assert result.tier == "hot"
    assert result.score >= 7
```

---

## 5. Security Rules

- **Never log sensitive data** — no emails, names, or API keys in logs
- **Validate HubSpot webhook signatures** — verify every incoming request
- **Rate limit the webhook endpoint** — prevent abuse
- **Secrets never in code** — enforced by `.env.example` with no real values
- **API keys rotated every 90 days**

### Logging — Good vs Bad
```python
# Good
logger.info(f"Lead received: id={lead_id}")

# Bad — never log PII
logger.info(f"Lead received: email={email}, name={name}")
```

---

## 6. Git Standards

### Branch Naming
```
sprint-1
sprint-2
sprint-3
sprint-4
```

### One commit per task. Commit message format:
```
feat: add HubSpot webhook receiver
fix: handle empty enrichment response
test: add unit tests for scoring service
chore: add docker-compose setup
docs: update README with setup instructions
```

### Rules
- **Never push directly to main** — PRs only
- **PR must have passing tests** before merge
- **One task = one commit** — keep commits small and meaningful
- **No commented-out code** in commits

---

## 7. Documentation Standards

- `README.md` must include:
  - What the project does
  - How to set up locally
  - How to run tests
  - Environment variables reference

- `.env.example` must list every variable with a description:
```
HUBSPOT_CLIENT_ID=        # HubSpot OAuth2 client ID
HUBSPOT_CLIENT_SECRET=    # HubSpot OAuth2 client secret
CLEARBIT_API_KEY=         # Clearbit enrichment API key
HUNTER_API_KEY=           # Hunter.io email validation key
ANTHROPIC_API_KEY=        # Claude API key
SLACK_WEBHOOK_URL=        # Slack incoming webhook URL
DATABASE_URL=             # PostgreSQL connection string
JWT_SECRET=               # Secret for signing internal JWTs
```

- Every non-obvious function gets a one-line comment explaining WHY:
```python
# Retry once before failing — Claude occasionally returns malformed JSON on first attempt
response = await call_claude_with_retry(prompt)
```

---

## 8. Dependency Management

- **Package manager: `uv`** — faster than pip, use for all installs
- **Always pin exact versions** — no floating versions
- Use `uv pip compile` to generate locked `requirements.txt`

### Setup with uv
```bash
# Install uv
curl -Ls https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Add a new package
uv pip install fastapi==0.110.0
uv pip freeze > requirements.txt
```

### Good
```
fastapi==0.135.1
anthropic==0.85.0
psycopg2-binary==2.9.11
alembic==1.18.4
```

### Bad
```
fastapi>=0.100
anthropic
psycopg2-binary
```

- Review dependencies for security vulnerabilities before adding them
- Never add a package you don't fully need

---

## 9. Definition of Done Checklist

A task is complete only when ALL of these are true:

- [ ] Code is written and working
- [ ] Follows clean architecture (no logic in routes)
- [ ] Type hints on all functions
- [ ] No hardcoded secrets or values
- [ ] Error handling with specific exceptions
- [ ] Logging added (no PII logged)
- [ ] Unit test written and passing
- [ ] No function longer than 20 lines
- [ ] Committed with correct message format
- [ ] Pushed to correct sprint branch
- [ ] Manually tested at least once
