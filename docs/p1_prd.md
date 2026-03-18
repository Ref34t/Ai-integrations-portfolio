# Project Technical Architecture Document
**Project Name:** AI-Powered CRM Lead Enrichment & Scoring System
**Client:** TBD
**Author:** TBD
**Date:** 2026-03-18
**Version:** 1.0

---

## 1. One-Line Summary
> Automatically analyze and score leads from the CRM into hot and cold ones, notify the sales team about hot leads, and archive cold ones.

---

## 2. Problem Statement
The sales team spends significant time manually researching and qualifying new leads before making contact.

**Goal:** Cut the time to find good leads by 75% through full automation of the enrichment, scoring, and routing process.

---

## 3. Solution Overview
**What it does:**
- Catches new leads entering the CRM via web form
- Enriches them with external company and contact data
- Scores them using AI into hot or cold
- Notifies the sales team about hot leads via Slack
- Archives cold leads automatically in the CRM

**What it does NOT do:**
- Does not create leads
- Does not delete leads
- Does not send emails to leads
- Does not manage the sales pipeline beyond initial routing

---

## 4. User Stories
- As a **sales rep**, I want to be notified only about hot leads so that I focus my time on deals that are likely to close
- As a **sales manager**, I want every new lead automatically scored so that I don't rely on my team's gut feeling
- As a **marketing manager**, I want cold leads archived automatically so that the CRM stays clean and actionable

---

## 5. Data Flow
```
[Web form submission]
        ↓
[HubSpot creates new lead → fires webhook]
        ↓
[FastAPI backend receives webhook]
        ↓
[Enrichment — Clearbit + Hunter.io]
    → Company size, industry, revenue
    → Email validity, domain data
        ↓
[Claude scores lead 1-10]
    → Returns: score, tier, reason, recommended action
        ↓
[Store result in PostgreSQL]
        ↓
[Decision]
    → Score >= 7 (hot) → Slack notification to sales team
    → Score < 7 (cold) → Archive lead in HubSpot
```

---

## 6. Tech Stack
| Layer | Tool | Why |
|---|---|---|
| CRM | HubSpot | Client's existing CRM |
| Backend | Python 3.11 + FastAPI | Core processing service |
| Enrichment | Clearbit + Hunter.io | Company + email data |
| AI / LLM | Claude (Anthropic) | Lead scoring + reasoning |
| Database | PostgreSQL + Alembic | Store leads, scores, audit trail + migrations |
| Auth | OAuth2 (HubSpot) + JWT (internal) | Secure integrations |
| Notifications | Slack | Sales team alerts |
| Package manager | uv | Fast, reliable dependency management |
| Testing | pytest | Unit + integration tests |
| Infra | Docker + GCP Cloud Run | Containerized deployment |
| CI/CD | GitHub Actions | Automated deployment |

---

## 7. Integrations & APIs
| Service | Purpose | Auth Method | Rate Limits (Free) |
|---|---|---|---|
| HubSpot | Receive webhooks, update + archive leads | OAuth2 | 100 API calls/day |
| Clearbit | Company enrichment | API Key | 50 enrichments/month |
| Hunter.io | Email validation | API Key | 25 searches/month |
| Claude | Lead scoring + reasoning | API Key | Tier dependent |
| Slack | Sales team notifications | Webhook URL | Unlimited |

> **Note:** Free tier limits apply. Client will need paid plans if lead volume exceeds 50/month.

---

## 8. Data Model
```
Table: leads
- id                  (UUID, primary key)
- crm_lead_id         (HubSpot lead ID)
- name                (string)
- email               (string)
- company             (string)
- enriched_data       (JSON — Clearbit + Hunter.io response)
- score               (integer 1-10)
- tier                (enum: hot / cold)
- reason              (string — AI explanation)
- recommended_action  (string — AI suggestion)
- status              (enum: notified / archived)
- created_at          (timestamp)
- updated_at          (timestamp)
```

---

## 9. Error Handling
| Scenario | What Happens |
|---|---|
| HubSpot webhook not received | Retry 3 times, then log and alert admin |
| Clearbit/Hunter.io returns no data | Score with available data, flag as "partially enriched" |
| Claude returns unexpected output | Retry once with same prompt, then flag for manual review |
| Duplicate lead detected | Skip processing, log it |
| Slack notification fails | Fallback to email notification |

---

## 10. Security
- **Authentication:** HubSpot OAuth2 for CRM access, JWT for internal API
- **Authorization:** Only authenticated services can trigger scoring
- **Secrets management:** Environment variables via `.env` locally, GCP Secret Manager in production
- **API keys:** Stored in `.env`, rotated every 90 days
- **Data sensitivity:** Medium — contains personal contact data, GDPR applies (EU/Malta client)

---

## 11. Testing Plan
| Test Type | What to Test |
|---|---|
| Unit tests | Scoring logic, enrichment parsing, duplicate detection |
| Integration tests | HubSpot webhook → enrichment → Claude → Slack full flow |
| Manual QA | Submit a real test lead via web form, verify output end to end |

---

## 12. Deployment
- **Hosting:** GCP Cloud Run
- **Containerization:** Docker
- **CI/CD:** GitHub Actions — auto deploy on push to main
- **Environment variables:** `.env` locally, GCP Secret Manager in production

---

## 13. Monitoring & Logging
- **What is logged:** Every lead received, enrichment result, score, decision, notification sent
- **Where logs are stored:** PostgreSQL + GCP Cloud Logging
- **Alerts for:** Enrichment failure, Claude error, Slack failure, >10 leads unprocessed in queue

---

## 14. Milestones
| Milestone | Deliverable | Due |
|---|---|---|
| 1 | HubSpot webhook connected + lead data received | Week 1 |
| 2 | Enrichment pipeline working (Clearbit + Hunter.io) | Week 2 |
| 3 | Claude scoring + PostgreSQL storage working | Week 3 |
| 4 | Slack notification + archive logic + Docker deployed | Week 4 |

---

## 15. Open Questions
- [ ] What is the minimum score threshold for a lead to be considered hot?
- [ ] How many leads per month do they currently receive?
- [ ] Do they have a paid HubSpot plan or free tier?
- [ ] Who on the sales team receives Slack notifications?
- [ ] What happens to archived leads — can they be revived later?

---

## 16. Scoring Prompt Template

The following prompt will be sent to Claude for every lead. Client must review and approve scoring criteria before build begins.

```
You are a lead qualification assistant.

Given the following lead data:
{lead_data}

Score this lead from 1 to 10 based on fit with a B2B business.
Consider: company size, industry relevance, email validity, job title seniority.

Return JSON only — no explanation outside the JSON:
{
  "score": 7,
  "tier": "hot",
  "reason": "Mid-size company in a relevant industry with a verified email and senior contact",
  "recommended_action": "Call within 24 hours, reference their industry pain points"
}

Rules:
- Score 7-10 = hot
- Score 1-6 = cold
- Always return valid JSON
- Never return null values
```

---

## 17. Rollback Plan

| Scenario | Fallback |
|---|---|
| System goes down | HubSpot leads remain unprocessed — daily manual export as backup |
| Claude API unavailable | Queue leads in PostgreSQL, retry every 30 minutes |
| Enrichment APIs down | Score lead with raw CRM data only, flag as "unenriched" |
| Full outage > 24hrs | Alert client, provide manual scoring spreadsheet as temporary fallback |

---

## 18. Slack Notification Format

Every hot lead notification sent to the sales team Slack channel will follow this format:

```
🔥 New Hot Lead — Score: 8/10

👤 Name: John Smith
🏢 Company: Acme Corp (120 employees, SaaS, Series B)
📧 Email: john@acme.com (verified)
💼 Title: Head of Operations

🤖 AI Reasoning:
Mid-size SaaS company in a relevant industry. Senior decision-maker
with a verified email. Company recently raised Series B — likely
budget available.

✅ Recommended Action: Call within 24 hours. Reference their
recent funding and operational scaling challenges.
```

---

## 19. Success Metrics

How we measure if the project succeeded:

| Metric | Target |
|---|---|
| Reduction in manual lead research time | 75% |
| Leads processed automatically per day | 100% of new leads |
| Hot lead conversion rate vs previous | +20% improvement |
| False positives (cold leads marked hot) | < 10% |
| System uptime | > 99% |

---

## 20. Out of Scope (Explicit)
- No A/B testing of scoring models
- No custom ML model training
- No mobile app or dashboard UI
- No email sending to leads
- No sales pipeline management beyond initial routing
- No integration with tools other than those listed in Section 6

---

## 21. API Versioning

All endpoints are versioned under `/api/v1/` to allow future changes without breaking existing integrations.

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/webhook` | POST | Receive HubSpot lead webhook |
| `/api/v1/health` | GET | Health check |

If breaking changes are needed in future, a `/api/v2/` prefix is introduced — `/api/v1/` remains live until client migrates.

---

## 22. Database Migration Strategy

- **Tool:** Alembic (PostgreSQL migrations)
- Every schema change requires a migration file — no manual table edits
- Migrations are run automatically on deployment via GitHub Actions
- Every migration is reversible — `alembic downgrade -1` must always work
- Migration files are committed to the repo alongside the code change

---

## 23. HubSpot Webhook Signature Verification

HubSpot sends an `X-HubSpot-Signature` header with every webhook request. Every incoming request must be verified before processing.

**Verification logic:**
```
1. Get raw request body
2. Concatenate: CLIENT_SECRET + raw_body
3. SHA-256 hash the result
4. Compare with X-HubSpot-Signature header value
5. Reject request with 401 if mismatch
```

Any request failing signature verification is logged and rejected immediately.

---

## 24. Data Retention Policy (GDPR)

This system processes personal data (name, email, company) of EU contacts. The following rules apply:

| Data Type | Retention Period | Action After |
|---|---|---|
| Raw lead data | 12 months | Anonymized (name + email nulled) |
| Enriched data | 12 months | Deleted |
| Score + tier | 24 months | Kept for model improvement |
| Audit logs | 24 months | Kept for compliance |

- Client is the **data controller** — this system is the **data processor**
- Client must have a valid legal basis for collecting lead data
- Data subject requests (access, deletion) handled by client via HubSpot

---

## 25. Staging Environment

Three environments are defined:

| Environment | Purpose | URL |
|---|---|---|
| Local | Development | `localhost:8000` |
| Staging | Testing before release | `staging.p1.your-domain.com` |
| Production | Live client system | `p1.your-domain.com` |

**Rules:**
- All sprint deliverables are deployed to staging first
- Client demos happen on staging — never local
- Production deploy only happens after staging is verified
- Staging uses separate HubSpot sandbox account

---

## 26. Client Demo Plan

A short demo is delivered to the client at the end of every sprint.

| Sprint | Demo Content |
|---|---|
| 1 | Submit test lead via form → show it appears in DB |
| 2 | Show enriched lead data returned from Clearbit + Hunter.io |
| 3 | Show Claude scoring output with reason and recommended action |
| 4 | Full live demo: form → enrich → score → Slack notification |

Demo format: screen share, max 15 minutes, show real data not mockups.

---

## 27. Cost Estimation

Monthly running costs at steady state (paid tiers):

| Service | Plan | Est. Monthly Cost |
|---|---|---|
| HubSpot | Starter | ~$20/month |
| Clearbit | Growth (1,000 enrichments) | ~$99/month |
| Hunter.io | Starter (500 searches) | ~$49/month |
| Claude API | ~1,000 scoring calls/month | ~$5–15/month |
| GCP Cloud Run | Low traffic | ~$5–10/month |
| GCP Cloud Logging | Standard | ~$0–5/month |
| **Total** | | **~$178–$193/month** |

> **Note:** Free tiers cover up to ~50 leads/month. Above that, paid plans are required. Client should budget ~$200/month for infrastructure at moderate lead volume.

---

## 28. Concurrent Request Strategy

The webhook endpoint must handle simultaneous lead submissions without data loss or race conditions.

**Strategy:**
- FastAPI runs async — handles concurrent requests natively
- Each webhook request is processed in an independent async task
- Database writes use connection pooling (asyncpg) — no locking issues
- Duplicate detection uses a DB-level unique constraint on `crm_lead_id` — prevents race condition duplicates
- If load exceeds capacity: GCP Cloud Run auto-scales horizontally

**Concurrency limits:**
- Cloud Run: max 10 concurrent instances, 80 requests per instance
- If sustained load > 800 req/min: add a Redis queue as a buffer

---

## 29. Handoff & Onboarding Document

When the project is delivered, the client receives:

### What They Get
- Access to the GitHub repo
- GCP Cloud Run deployment (client's own GCP account)
- All API keys in GCP Secret Manager
- Admin access to PostgreSQL database
- Slack integration in their workspace

### Runbook — Common Operations

| Task | How |
|---|---|
| View recent leads | Query PostgreSQL `leads` table |
| Manually re-score a lead | Call `/api/v1/webhook` with lead data |
| Change hot lead threshold | Update `HOT_LEAD_THRESHOLD` in GCP Secret Manager |
| View logs | GCP Cloud Logging → filter by service name |
| Deploy a new version | Push to `main` branch — GitHub Actions deploys automatically |
| Roll back a deployment | GCP Cloud Run → select previous revision → route 100% traffic |

### What To Do When Something Breaks

| Symptom | First Step |
|---|---|
| Leads not being processed | Check GCP Cloud Logging for errors |
| Slack notifications not arriving | Check `SLACK_WEBHOOK_URL` in Secret Manager |
| Enrichment failing | Check Clearbit/Hunter.io API key validity and quota |
| Claude scoring failing | Check Anthropic API key and billing |
| Database connection error | Check `DATABASE_URL` in Secret Manager |

### Monthly Maintenance Checklist
- [ ] Review GCP Cloud Logging for recurring errors
- [ ] Check API quota usage (Clearbit, Hunter.io, Claude)
- [ ] Rotate API keys (every 90 days)
- [ ] Review hot/cold lead accuracy with sales team
- [ ] Run data retention cleanup if not automated
