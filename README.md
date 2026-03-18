# AI Integrations Portfolio

A collection of production-grade AI integration projects covering CRM automation, invoice intelligence, content automation, and business intelligence.

---

## Projects

| Project | Description | Stack |
|---|---|---|
| [P1 — CRM Lead Enrichment](./p1-lead-enrichment/) | Enrich and score CRM leads automatically | Python, FastAPI, HubSpot, Claude, PostgreSQL |
| [P2 — Invoice Intelligence](./p2-invoice-intelligence/) | AI-powered invoice extraction and ERP posting | Python, FastAPI, Business Central, Claude, RAG |
| [P3 — Content Automation](./p3-content-automation/) | Multi-platform content generation and publishing | Python, n8n, WordPress, Claude, Mailchimp |
| [P4 — BI Agent](./p4-bi-agent/) | Anomaly detection and proactive business alerts | Python, LangChain, Weaviate, HubSpot, Stripe |

---

## Docs

- [Project PRD Template](./docs/project_prd_template.md)
- [P1 PRD](./docs/p1_prd.md)
- [P1 Sprints](./docs/p1_sprints.md)
- [All Projects Overview](./docs/projects_overview.md)

---

## Standards

All projects follow the same standards defined in [CONTRIBUTING.md](./CONTRIBUTING.md):
- Python 3.13 + FastAPI
- uv for dependency management
- PostgreSQL + Alembic
- Docker + GCP Cloud Run
- pytest with 80% coverage minimum
- Ruff for linting
