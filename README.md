# AutoPilot Studio

A review-first prototype for POD research and public microtask opportunity discovery.

## Current capabilities
- Python POD concept pipeline: public Google Trends RSS attempt, lexical concept matching, draft listing metadata, IP keyword flags, CSV/ZIP reports.
- Earnings Hunter: bounded scans of curated official public pages, rate evidence extraction, scam-risk keyword triage, and CSV/Markdown reports.
- Mobile web/Android interface with a local-only Earnings Hunter status and payout ledger. The ledger is stored in this device's browser storage and can be lost if app data is cleared.
- GitHub Actions schedules tests and creates short-lived artifacts/APK builds.

## Important limitations
This is **not** a fully autonomous AGI or a guaranteed income system. It does not log into earning platforms, apply for jobs, complete personal tests, submit work, bypass CAPTCHAs, verify a user's eligibility, or receive payouts. The app does not yet sync live GitHub Actions output into its local tracker. POD publishing and model inference are not connected. A discovered link is a lead, not a promise of available work or payment.

## First verified payment
- [Small-business client acquisition playbook — ₹0 budget](docs/SMALL_BUSINESS_CLIENT_ACQUISITION.md)
- [Fictional small-business content portfolio (SPEC WORK)](portfolio/SMALL_BUSINESS_CONTENT_SAMPLES.md)
- [First Verified Payment Sprint — India / zero budget](docs/FIRST_VERIFIED_PAYMENT_SPRINT.md)
- [Direct-client CSV/text labeling experiment](docs/DIRECT_CLIENT_MICROGIG_EXPERIMENT.md)

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
