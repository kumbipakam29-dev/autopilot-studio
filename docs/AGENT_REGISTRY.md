# AutoPilot Studio — Agent Registry
**Version:** 1.0  
**Updated:** 2026-10-26  
**Operating principle:** departments are workflow roles, not claims of independently running AI agents. A role is "active" only when a real workflow executes and leaves evidence.

## Status vocabulary
- **PLANNED** — defined, not implemented.
- **DOCUMENTED** — workflow/spec exists in repository.
- **IMPLEMENTED** — code exists; still needs test evidence.
- **TESTED** — a test completed successfully; does not imply production deployment.
- **LIVE-VERIFIED** — production endpoint or external action was checked successfully.
- **BLOCKED** — a concrete dependency prevents progress.
- **APPROVAL-REQUIRED** — requires owner confirmation before an external action.

## Registry

| ID | Department / role | Purpose | Current status | Human gate |
|---|---|---|---|---|
| ADS-01 | Website Builder | Customer-facing website, service pages, portfolio | DOCUMENTED / deployment unverified | Verify public URL and contact route before launch |
| ADS-02 | Content Studio | Produce captions, calendars, short video scripts and spec samples | DOCUMENTED | Owner approves claims and publishing |
| ADS-03 | Prospect Research | Find relevant businesses and record public contact routes | PLANNED | Owner reviews prospects and outreach |
| ADS-04 | Outreach Assistant | Prepare personalized email/DM drafts and follow-ups | PLANNED | Owner approves and sends; no mass spam |
| ADS-05 | Earnings Hunter | Find and compare legitimate online work opportunities | DOCUMENTED | Owner handles accounts, applications and identity checks |
| ADS-06 | POD Research | Demand research, original design briefs, listing drafts | PLANNED | Owner approves IP rights and listings |
| ADS-07 | Quality & Safety Reviewer | Check factual claims, scam signs, copyright and privacy | PLANNED | Mandatory review for external publication |
| ADS-08 | Build & Release Monitor | Check CI results, website deploy and APK artifacts | PLANNED | Never call an artifact released until its URL and install are verified |
| ADS-09 | Finance & Payout Ledger | Record accepted work and verified receipts | PLANNED | Only owner-confirmed evidence can mark payment verified |

## Current verified scope

- Repository documentation for Earnings Hunter exists.
- Earnings Hunter tracker CSV exists.
- This registry describes planned workflow roles; it does **not** prove that nine autonomous agents are running.
- No client, application, sale, paid task, or payment is marked complete without evidence.
- No paid APIs or subscriptions are required by this registry.

## Next implementation order

1. Add a small local dashboard view that reads the tracker data.
2. Add source freshness checks and a clear last-checked date.
3. Add duplicate detection and scam-risk flags.
4. Add a human approval queue for outreach/applications.
5. Add deployment and artifact checks; show links only after verification.
