# P1: AI-Powered CRM Lead Enrichment — Sprint Plan
**Project:** AI-Powered CRM Lead Enrichment & Scoring System
**Total Duration:** 4 Weeks
**Sprint Length:** 1 Week

---

## Sprint 1 — Foundation & HubSpot Integration
**Goal:** Receive and store a real lead from HubSpot

### Tasks
- [x] Create GitHub repo + folder structure (as defined in CONTRIBUTING.md)
- [x] Set up Docker + docker-compose (FastAPI + PostgreSQL)
- [x] Create `.env.example` with all variable descriptions
- [x] Set up PostgreSQL + Alembic migrations
- [x] Create initial migration for `leads` table
- [ ] Register app in HubSpot developer sandbox account
- [ ] Implement OAuth2 flow with HubSpot
- [ ] Build `/api/v1/webhook` endpoint in FastAPI
- [ ] Implement HubSpot webhook signature verification (PRD Section 23)
- [ ] Parse and validate incoming webhook payload with Pydantic
- [ ] Store raw lead in PostgreSQL
- [ ] Write unit tests for webhook parsing + signature verification
- [ ] Deploy to staging environment
- [ ] Test end to end: submit web form → lead appears in DB
- [ ] **Sprint 1 demo to client**

### Definition of Done
A new lead submitted via web form is received, signature verified, and stored in PostgreSQL with all raw fields. Live on staging.

---

## Sprint 2 — Enrichment Pipeline
**Goal:** Enrich every incoming lead with external data

### Tasks
- [ ] Integrate Clearbit API — fetch company data by domain
- [ ] Integrate Hunter.io API — validate email + fetch domain info
- [ ] Build enrichment service: takes raw lead, returns enriched lead
- [ ] Handle enrichment failures gracefully (partial enrichment fallback)
- [ ] Create Alembic migration for enriched_data field
- [ ] Add duplicate detection logic — skip if lead already exists
- [ ] Write unit tests for enrichment parsing
- [ ] Write unit tests for duplicate detection
- [ ] Deploy to staging
- [ ] Test end to end: submit lead → enriched data appears in DB
- [ ] **Sprint 2 demo to client**

### Definition of Done
Every new lead is automatically enriched with Clearbit + Hunter.io data and stored. Duplicates are skipped. Partial enrichment is flagged. Live on staging.

---

## Sprint 3 — AI Scoring Engine
**Goal:** Score every enriched lead using Claude

### Tasks
- [ ] Integrate Claude API (Anthropic SDK)
- [ ] Implement scoring prompt from PRD Section 16
- [ ] Build scoring service: takes enriched lead, returns score JSON
- [ ] Validate Claude response — ensure valid JSON every time
- [ ] Handle Claude failures — retry once, then flag for manual review
- [ ] Create Alembic migration for score fields
- [ ] Store score, tier, reason, recommended_action in PostgreSQL
- [ ] Write unit tests for scoring logic
- [ ] Write unit tests for JSON validation
- [ ] Integration test: webhook → enrich → score → stored in DB
- [ ] Manually review 10 test leads to verify scoring accuracy
- [ ] Deploy to staging
- [ ] **Sprint 3 demo to client**

### Definition of Done
Every enriched lead is scored by Claude and stored with score, tier, reason and recommended action. Invalid responses are handled gracefully. Live on staging.

---

## Sprint 4 — Notifications, Routing & Deployment
**Goal:** Notify sales of hot leads, archive cold leads, deploy to production

### Tasks
- [ ] Build Slack notification service using Slack webhook URL
- [ ] Implement Slack message format from PRD Section 18
- [ ] Build HubSpot archiving service — archive cold leads via API
- [ ] Implement routing logic: score >= 7 → Slack / score < 7 → archive
- [ ] Add email fallback if Slack notification fails
- [ ] Set up GCP Cloud Run for production deployment
- [ ] Set up GCP Secret Manager for production secrets
- [ ] Write GitHub Actions CI/CD pipeline (staging on PR, production on merge to main)
- [ ] Set up GCP Cloud Logging
- [ ] Add monitoring alerts (enrichment failure, Claude error, queue backlog)
- [ ] Run full data retention cleanup job (PRD Section 24)
- [ ] Full end to end integration test on staging
- [ ] Promote to production
- [ ] Manual QA: submit 5 real test leads on production, verify full flow
- [ ] **Sprint 4 full live demo to client**

### Definition of Done
Hot leads trigger a Slack notification in the correct format. Cold leads are archived in HubSpot. System is live on GCP Cloud Run with CI/CD, logging, monitoring and staging environment all active.

---

## Sprint Summary

| Sprint | Focus | Deliverable |
|---|---|---|
| 1 | Foundation + HubSpot | Webhook receives + stores leads |
| 2 | Enrichment pipeline | Leads enriched with Clearbit + Hunter.io |
| 3 | AI scoring engine | Leads scored by Claude |
| 4 | Notifications + deploy | Slack alerts + archive + live on GCP |

---

## Daily Standup Template
Answer these 3 questions every day:
1. What did I complete yesterday?
2. What am I working on today?
3. Is anything blocking me?

---

## Definition of Done (Global)
A task is done when ALL of these are true:
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

> Full standards in CONTRIBUTING.md
