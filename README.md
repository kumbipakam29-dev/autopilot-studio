# AutoPilot Studio

A zero-budget, review-first prototype for digital-product workflows, small-business content services, public opportunity discovery, and Android status reporting.

## Current verified status

**Last checked:** 26 October 2026. This status reflects repository and GitHub Actions evidence, not continuous background execution.

- The earning-ledger validation-message fix was tested on branch `fix/earning-ledger-error-case`; its latest run reported **129 tests passed**. [Workflow run](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40273797893).
- Runtime, registry, public-portal, device-adaptive-router, earnings-hunter and payment-loop checks completed successfully on that fix branch. Check the latest Actions page for current results.
- A debug APK artifact was produced by [Build Android APK](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40272915141). A successful CI build does **not** prove that it installs and opens correctly on a physical device.
- [Phase 2–6 execution checklist](https://github.com/kumbipakam29-dev/autopilot-studio/issues/19) tracks stabilization, runtime safety, client acquisition, portal/app reliability and revenue validation.
- [Public agent chat portal MVP PR](https://github.com/kumbipakam29-dev/autopilot-studio/pull/17) is still a draft and has not been merged or deployed.

## Current capabilities

- Python POD concept pipeline: public trend-source attempt, lexical concept matching, draft listing metadata, IP keyword flags, and CSV/ZIP reports.
- Earnings Hunter: bounded scans of curated public pages, rate-evidence extraction, scam-risk keyword triage, and CSV/Markdown reports.
- Prototype agent runtime and device-adaptive routing with tests for setup-required local models and preventing unknown tasks from silently falling back to remote execution.
- Review-first content drafts and fictional portfolio samples are developed on the portal feature branch; examples must remain labelled **SPEC** and are not paid-client work.
- GitHub Actions run tests and can create short-lived artifacts/APK builds.

## Important limitations

This is **not** a fully autonomous AGI, a 500-agent fleet, or a guaranteed income system. Passing tests verifies only the tested code paths.

- The system does not log into earning platforms, bypass CAPTCHAs, take identity tests, or submit work on the user's behalf.
- A discovered job or task is a lead, not proof of eligibility, available work, fair hourly earnings, or payment.
- Actual local-model installation, model inference on the user's device, and live device connection have not been fully verified.
- The public portal is not deployed. Review authentication, rate limiting, data retention, privacy and abuse protection before any public deployment.
- The Android APK artifact is not a verified device installation or a stable public release.
- No client message, public post, order or payment is claimed unless separately confirmed with evidence. The current business workflow has **no verified revenue**.
- No paid API, subscription, purchase, account change, outbound message, publishing or deployment should happen without explicit owner approval.

## Zero-budget client acquisition

The current test offer is a **₹499 introductory quote** for 3 post concepts/captions, one 14–20 second Reel script, a 7-day calendar and one revision. This is an experiment, not a researched market average or a result guarantee.

Before contacting a business, manually verify its public profile and the detail used in the draft. Use relevant, permitted channels; do not bulk-spam or repeatedly message non-responders. Keep SPEC samples separate from client work. Track prospects, messages sent, replies, quotes, accepted orders, delivered work and owner-confirmed payments as distinct stages.

## First verified payment

- [First Verified Payment Sprint — India / zero budget](docs/FIRST_VERIFIED_PAYMENT_SPRINT.md)
- [Direct-client CSV/text labeling experiment](docs/DIRECT_CLIENT_MICROGIG_EXPERIMENT.md)
- [Revenue experiment baseline](docs/REVENUE_EXPERIMENT_RESULTS_BASELINE_1.md)

A payment is marked verified only after the owner confirms the credit in their own receiving account. A dashboard estimate, lead, invoice, application or verbal interest is not revenue.

## Research documents

- [Deep research, system gap audit, free tools/models and zero-budget roadmap](docs/DEEP_RESEARCH_ZERO_BUDGET.md)
- [1,224 categorized opportunity hypotheses (CSV)](docs/IDEA_BANK_1200.csv)
- [Earnings Hunter MVP and safe work loop](docs/EARNINGS_HUNTER_MVP.md)
- [POD Agent MVP](docs/POD_AGENT_MVP.md)

## Run tests

```bash
python -m unittest discover -s tests -v
```

Before spending time on any opportunity, check the official listing, country/language/device eligibility, task-specific pay unit, acceptance criteria, minimum payout and supported payout route. Never pay a joining/deposit/unlock fee or store IDs, passwords, OTPs or payment details in the repository.
