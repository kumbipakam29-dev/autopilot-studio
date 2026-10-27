# AutoPilot Studio

A review-first prototype for POD research and public microtask opportunity discovery.

## Current capabilities
- Python POD concept pipeline: public Google Trends RSS attempt, lexical concept matching, draft listing metadata, IP keyword flags, CSV/ZIP reports.
- Earnings Hunter: bounded scans of curated official public pages, rate evidence extraction, scam-risk keyword triage, and CSV/Markdown reports.
- Deterministic read-only opportunity evidence grader; see agents/evidence_grader.py and tests/test_evidence_grader.py.
- Mobile web/Android interface with a local-only Earnings Hunter status and payout ledger. The ledger is stored in this device's browser storage and can be lost if app data is cleared.
- GitHub Actions schedules tests and creates short-lived artifacts/APK builds.

## Important limitations
This is **not** a fully autonomous AGI or a guaranteed income system. It does not log into earning platforms, apply for jobs, complete personal tests, submit work, bypass CAPTCHAs, verify a user's eligibility, or receive payouts. The app does not yet sync live GitHub Actions output into its local tracker. POD publishing and model inference are not connected. A discovered link is a lead, not a promise of available work or payment. The evidence grader uses supplied data only and does not prove a job is genuine or payment will occur.

## First verified payment
- [First Verified Payment Sprint — India / zero budget](docs/FIRST_VERIFIED_PAYMENT_SPRINT.md)
- [Direct-client CSV/text labeling experiment](docs/DIRECT_CLIENT_MICROGIG_EXPERIMENT.md)

## Agent system (catalog / planned)
- [100-agent registry (versioned JSON)](config/agent_registry_v1.json) — catalog only; agents are not all deployed or running.
- [15 specialized agents across three framework patterns](config/specialist_agents_15_v1.json) — five distinct agent specifications each inspired by smolagents, LangGraph, and CrewAI; specifications only, not 15 running model-backed agents.
- [15-agent catalog integrity tests](tests/test_specialist_agents_15.py)
- [15 offline specialist capability prototypes](agents/specialist_capabilities.py) — deterministic, standard-library-only MVPs with no model calls or network access; drafts and classifiers only, not autonomous external actions.
- [Offline capability regression tests](tests/test_specialist_capabilities.py)
- [JSON CLI runner](agents/run_specialist.py) — accepts JSON on stdin and returns a capability result on stdout.
- [Offline client-acquisition draft pipeline](agents/client_acquisition_pipeline.py) — composes brief structuring, content angles, captions, a seven-day calendar, two 17-second Reels, fictional spec work and conditional outreach drafts; no browsing, sending, or publishing.
- [Client-acquisition pipeline tests](tests/test_client_acquisition_pipeline.py)
- [Client-acquisition pipeline guide](docs/CLIENT_ACQUISITION_DRAFT_PIPELINE.md)
- [Ahmedabad prospect research starter list](docs/PROSPECT_RESEARCH_AHMEDABAD_2026-10.md) — public-source candidates to manually qualify; no businesses contacted.
- [Ahmedabad prospect research — batch 2](docs/PROSPECT_RESEARCH_AHMEDABAD_BATCH_2_2026-10.md) — additional candidates and content hypotheses; no businesses contacted.
- [Ahmedabad prospect research — batch 3](docs/PROSPECT_RESEARCH_AHMEDABAD_BATCH_3_2026-10.md) — additional official-source café candidates; no businesses contacted.
- [Ahmedabad prospect research — batch 4](docs/PROSPECT_RESEARCH_AHMEDABAD_BATCH_4_2026-10.md) — four more candidates; research-only, not yet qualified.
- [Ahmedabad bulk coverage plan](docs/AHMEDABAD_BULK_COVERAGE_PLAN.md) — category × neighbourhood discovery method, qualification gates, and coverage clusters.
- [Ahmedabad prospect inventory v1 (CSV)](docs/AHMEDABAD_PROSPECT_INVENTORY_V1.csv) — 20 public-directory candidates, all marked unqualified and not contacted.
- [Ahmedabad prospect research — batch 5](docs/PROSPECT_RESEARCH_AHMEDABAD_BATCH_5_2026-10.md) — wider categories: interiors, education, property, auto care, photography and events; research only.
- [Ahmedabad prospect inventory — batch 5 (CSV)](docs/AHMEDABAD_PROSPECT_INVENTORY_BATCH_5.csv) — 23 additional candidates with explicit verification/contact gates.
- [Ahmedabad batch 5 outreach drafts (unsent)](docs/AHMEDABAD_BATCH_5_OUTREACH_DRAFTS_UNSENT.md) — six permission-first one-to-one drafts; not sent.
- [Ahmedabad prospect research — batch 6](docs/PROSPECT_RESEARCH_AHMEDABAD_BATCH_6_2026-10.md) — 15 more public-listing candidates across interiors, auto care, coaching and events; unqualified.
- [Ahmedabad prospect inventory — batch 6 (CSV)](docs/AHMEDABAD_PROSPECT_INVENTORY_BATCH_6.csv) — verification and approval gates for each candidate.
- [Prospect qualification scorecard](docs/PROSPECT_QUALIFICATION_SCORECARD.md) — hard gates, evidence scoring, and status/payment integrity rules.
- [Portfolio spec work: café + local service](docs/PORTFOLIO_SPEC_WORK_CAFE_AND_LOCAL_SERVICE.md) — two fictional examples with post concepts, captions, 17-second Reels, and seven-day calendars.
- [Ahmedabad outreach drafts](docs/AHMEDABAD_OUTREACH_DRAFTS_2026-10.md) — four fact-grounded drafts for manual review; unsent.
- [Specialist capability GitHub Actions workflow](.github/workflows/specialist-capability-tests.yml) — runs the full offline unittest suite on pushes and pull requests.
- [Agent versioning and supervised learning standard](docs/AGENT_VERSIONING_AND_SUPERVISED_LEARNING.md)
- [Pinned GitHub upstream agent sources](config/upstream_agent_sources_v1.json) — 10 public projects with commit pins, licenses and adaptation roles.
- [GitHub agent source adoption plan](docs/GITHUB_UPSTREAM_AGENT_SOURCES.md) — staged adoption, including first read-only evidence grader.
- [Open-source agent learning and integration roadmap](docs/OPEN_SOURCE_AGENT_LEARNING_ROADMAP.md)

## Research documents
- [Deep research, system gap audit, free tools/models and zero-budget roadmap](docs/DEEP_RESEARCH_ZERO_BUDGET.md)
- [1,224 categorized opportunity hypotheses (CSV)](docs/IDEA_BANK_1200.csv)
- [Earnings Hunter MVP and safe work loop](docs/EARNINGS_HUNTER_MVP.md)
- [POD Agent MVP](docs/POD_AGENT_MVP.md)

## Run tests
```bash
python -m unittest discover -s tests -v
```

Before spending time on any lead, check the official listing, country/language/device eligibility, task-specific rate unit, acceptance criteria, minimum payout, and supported payout route. Never pay a joining/deposit/unlock fee or store IDs, passwords, OTPs or payment details in the repository.
