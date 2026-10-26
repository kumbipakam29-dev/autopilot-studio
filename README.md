# AutoPilot Studio

A review-first prototype for POD research and public microtask opportunity discovery.

## Current capabilities
- Python POD concept pipeline: public Google Trends RSS attempt, lexical concept matching, draft listing metadata, IP keyword flags, CSV/ZIP reports.
- Earnings Hunter: bounded scans of curated official public pages, rate evidence extraction, scam-risk keyword triage, and CSV/Markdown reports.
- Work → Win → Payment Loop: explicit tool registry, ranked opportunity action pack, local status ledger, draft-only client pitch generator, and owner-confirmed payment records.
- Mobile web/Android interface with a local-only Earnings Hunter status and payout ledger. The ledger is stored in this device's browser storage and can be lost if app data is cleared.
- GitHub Actions schedules tests and creates short-lived artifacts/APK builds.

## Important limitations
This is **not** a fully autonomous AGI or a guaranteed income system. It does not log into earning platforms, apply for jobs, complete personal tests, submit work, bypass CAPTCHAs, verify a user's eligibility, or receive payouts. The app does not yet sync live GitHub Actions output into its local tracker. POD publishing and model inference are not connected. A discovered link is a lead, not a promise of available work or payment.

## Agent earning experiment
- [Live experiment log, verified run metrics, permission boundaries and next experiments](docs/AGENT_EARNING_EXPERIMENT_LOG.md)

## First verified payment
- [Work → Win → Payment Loop — setup, commands, status and owner-confirmed payment ledger](docs/WORK_WIN_PAYMENT_LOOP.md)
- [Read-only ledger status audit — usage, report fields and safety limits](docs/LEDGER_STATUS_AUDIT.md)
- [Zero-budget revenue experiment protocol, success metrics and approval boundaries](docs/REVENUE_EXPERIMENT_PROTOCOL.md)
- [Measured experiment baseline — first live scan, visible pay evidence and zero-payment truth](docs/REVENUE_EXPERIMENT_RESULTS_BASELINE_1.md)
- [Small-business client acquisition playbook — ₹0 budget](docs/SMALL_BUSINESS_CLIENT_ACQUISITION.md)
- [Fictional small-business content portfolio (SPEC WORK)](portfolio/SMALL_BUSINESS_CONTENT_SAMPLES.md)
- [First Verified Payment Sprint — India / zero budget](docs/FIRST_VERIFIED_PAYMENT_SPRINT.md)
- [Direct-client CSV/text labeling experiment](docs/DIRECT_CLIENT_MICROGIG_EXPERIMENT.md)

## Agent training and safety
- [Agent training and evaluation playbook — quality gates, regression tests, safety metrics and release levels](docs/AGENT_TRAINING_AND_EVALUATION.md)
- [Agent identity and signup rules — autonomous free steps, owner-only verification and privacy boundaries](docs/AGENT_IDENTITY_AND_SIGNUP_RULES.md)

## Free-first learning and adaptive routing
- [Free AI/ML/NLP/LLM/MLP/MLM and automation tool catalog](docs/FREE_AI_ML_NLP_AUTOMATION_TOOL_CATALOG.md)
- [Self-improving free-resource Learning Mode design](docs/SELF_IMPROVING_FREE_RESOURCE_LEARNING_MODE.md)
- [Device-adaptive model and agent factory architecture](docs/DEVICE_ADAPTIVE_MODEL_AND_AGENT_FACTORY.md)
- [Device-adaptive router MVP and verification gates](docs/DEVICE_ADAPTIVE_ROUTER_MVP.md)
- [Adaptive route recommendations and draft agent-spec generator](agents/adaptive_factory.py)
- [Integrated draft-agent factory + versioned device-aware model router](agents/integrated_agent_router.py)
- [Integrated agent factory/router: status semantics, safety gates, and test commands](docs/INTEGRATED_AGENT_FACTORY_ROUTER.md)

## Agent registry and versioning
- [500-agent registry — unique IDs, role/niche variants, model/agent versions and honest execution states](agents/registry.json)
- [Additional 45-role specialist team registry — 15 social media, 15 error handling, 15 defensive cybersecurity roles](agents/specialist_team_registry.json)
- [Specialist team registry, validation and permission boundaries](docs/SPECIALIST_TEAM_REGISTRY.md)
- [Registry validation and CI tests](docs/AGENT_REGISTRY_AND_VERSIONING.md)
- [Safe runtime MVP — router, five deterministic handlers, SQLite run ledger, and approval gate](docs/AGENT_RUNTIME_MVP.md)
- [Agent tool registry — what is implemented vs disabled](agents/tool_registry.json)
- [Work-loop agent runtime](agents/work_win_payment_loop.py)

## Open-source tool stack
- [Curated local-first open-source tool catalog and adoption order](docs/OPEN_SOURCE_TOOL_CATALOG.md)

## Research documents
- [Deep research, system gap audit, free tools/models and zero-budget roadmap](docs/DEEP_RESEARCH_ZERO_BUDGET.md)
- [1,224 categorized opportunity hypotheses (CSV)](docs/IDEA_BANK_1200.csv)
- [Earnings Hunter MVP and safe work loop](docs/EARNINGS_HUNTER_MVP.md)
- [POD Agent MVP](docs/POD_AGENT_MVP.md)

## Run tests
```bash
python -m unittest discover -s tests -v
python scripts/validate_specialist_team_registry.py
python -m unittest discover -s tests -p 'test_specialist_team_registry.py' -v
```

Before spending time on any lead, check the official listing, country/language/device eligibility, task-specific rate unit, acceptance criteria, minimum payout, and supported payout route. Never pay a joining/deposit/unlock fee or store IDs, passwords, OTPs or payment details in the repository.
