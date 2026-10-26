# Ledger Consolidation: State Contract and Migration Plan

Status: design/audit only. No ledger code or existing user data has been changed.

## Why the ledgers are not interchangeable

The repository currently has two related but distinct data models:

- `agents/earning_task_ledger.py` tracks an individual task's lifecycle using a JSON file and stages such as `discovered`, `current_listing_verified`, `applied`, `accepted`, `payout_pending`, and `paid`.
- `agents/work_win_payment_loop.py` tracks opportunities/leads in SQLite using statuses such as `new`, `shortlisted`, `application_ready`, `applied_by_user`, `submitted_by_user`, `accepted`, `rejected`, and `paid`. Its separate `payments` table records an owner-confirmed credit and explicitly returns `independently_verified: false`.

These represent overlapping but not identical concepts. A discovered opportunity is not necessarily an applied-for task, and an owner-confirmed payment is not independent verification. A direct rename or destructive merge would lose meaning.

## Recommended canonical concepts

Keep three concepts separate in any future unified schema:

1. **Opportunity** — source, URL, eligibility, public payment evidence, triage/risk state.
2. **Work engagement** — owner-confirmed application/start/submission, acceptance/rejection and provider terms.
3. **Payment record** — amount, currency, payment reference/evidence note, owner confirmation and confirmation timestamp. Do not store screenshots, OTPs, banking credentials or full account details in the repository.

A task may link to an opportunity, but neither stage should imply payment. Payment must remain a separate record with explicit provenance.

## Proposed canonical lifecycle

- Opportunity: `discovered -> verified -> eligible | not_eligible | quarantined`
- Work: `not_started -> application_ready -> applied_by_user -> task_started_by_user -> submitted_by_user -> accepted | rejected`
- Payment: `not_due -> payout_pending -> owner_confirmed`

These are conceptual domains, not a proposal to change current enum values immediately. Rejected and quarantined records must not be advanced by ordinary status updates. A payment record should only be created after explicit owner confirmation of the actual credit.

## Migration rules

1. Preserve both existing ledgers as read-only inputs during migration.
2. Write a one-time importer that maps each source status to a canonical domain plus a migration note; do not silently coerce unknown states.
3. Retain original source IDs, timestamps, status values and provenance.
4. Quarantine ambiguous records for manual review instead of guessing.
5. Use a dry-run report first: counts by source status, mapped status, unmapped records and duplicate IDs.
6. Do not switch the application to the unified store until the dry-run is reviewed and fixtures cover every status and transition.
7. Keep a rollback/export path. Never delete original JSON or SQLite data as part of migration.
8. Ensure CI tests verify that lead discovery, application, acceptance and owner-confirmed payment cannot be conflated.

## Required tests before implementation

- Every current JSON stage has an explicit mapping or is reported as unmapped.
- Every SQLite workflow status has an explicit mapping or is reported as unmapped.
- `paid` in the JSON ledger requires payout amount plus owner confirmation.
- A SQLite payment is recorded as owner-confirmed and is not labelled independently verified.
- A quarantined lead cannot be promoted by an import/update cycle.
- Re-import is idempotent and preserves existing terminal states and timestamps.
- Malformed amounts, duplicate IDs and unknown statuses fail safely.
- Dry-run migration makes no writes to either source database/file.
- Export and rollback are tested against representative fixtures.

## Immediate next step

Add a read-only status-mapping report and migration fixtures. Do not consolidate production paths or delete either ledger until the report is reviewed and the migration tests pass.

## Evidence boundary

This document is based on direct reads of the two ledger implementations and their unit tests on the feature branch. It is a design proposal; no data migration, revenue claim, or runtime behavior change has been performed.
