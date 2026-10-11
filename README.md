# Hosting Recommendation Multi-Agent Pipeline

BSc thesis project (BFH, Wirtschaftsinformatik) building a Langflow-based multi-agent pipeline that turns a free-text description of a web app into a cost-optimized hosting recommendation.

## Status

Phase 1 (Konzeption): reference profiles, requirements catalogue, scoring specification and scoring engine are in place.

Run the tests: `python3 -m venv .venv && .venv/bin/pip install pytest && .venv/bin/pytest`

- Working plan: [`PLAN.md`](./PLAN.md)
- Decisions: [`docs/entscheidungen.md`](./docs/entscheidungen.md)
- Proposal: [`Fahrenbruch-Timo_BT-Proposal.docx`](./docs/theorie/Fahrenbruch-Timo_BT-Proposal.docx)

## Planned stack

- **Langflow** — visual pipeline orchestration (Profiler → Discovery → Extraction → Matching)
- **ScrapeGraphAI** — provider search & structured data extraction
- **LangSmith** — tracing, evaluation, cost tracking
