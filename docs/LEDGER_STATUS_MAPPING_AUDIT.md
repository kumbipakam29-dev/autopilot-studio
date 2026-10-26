# Read-only Ledger Status Mapping Audit

Status: proposal/fixture specification only. This document does not read, rewrite, migrate, or delete runtime ledger data.

## Source models reviewed

- `agents/earning_task_ledger.py`: JSON task stages and an explicit transition graph.
- `agents/work_win_payment_loop.py`: SQLite lead workflow statuses plus a separate `payments` table.

The mapping below is intentionally conservative. A status name alone is not proof that a user applied, completed work, was accepted, or received money. A future dry-run importer should emit the source ledger, source ID, source status, proposed domain/status, mapping confidence, and a human-readable reason.

## JSON task ledger: every declared stage

| Source stage | Proposed target domain | Dry-run disposition | Reason |
|---|---|---|---|
| `discovered` | Opportunity | `discovered` | A lead exists; no verification implied. |
| `current_listing_verified` | Opportunity | `verified` | Listing was explicitly checked as current by the source workflow. Preserve its evidence and timestamp. |
| `eligibility_check` | Opportunity | `eligibility_review` | A check stage is not itself a positive eligibility decision. |
| `applied` | Work engagement | `manual_review` | The legacy label does not record who submitted the application or preserve a separate owner-confirmation field. |
| `qualification` | Work engagement | `manual_review` | It may mean a qualification step, not approval or paid work. |
| `approved` | Work engagement | `manual_review` | Approval semantics and approving party need source evidence; do not infer work started. |
| `work_in_progress` | Work engagement | `manual_review` | The stage alone does not establish owner identity or work evidence. |
| `submitted` | Work engagement | `manual_review` | Preserve submission status, but do not infer acceptance. |
| `accepted` | Work engagement | `accepted` with evidence review | Acceptance is distinct from payout; preserve accepted amount and provenance. |
| `rejected` | Work engagement | `rejected` | Preserve terminal state; do not auto-advance. |
| `payout_pending` | Payment | `payout_pending` | A pending payout is not a received payment. |
| `paid` | Payment | `manual_review` | Legacy records may have owner confirmation, amount, and timestamp fields; verify all are present before creating a canonical payment record. |

## SQLite lead ledger: every declared workflow status

| Source status | Proposed target domain | Dry-run disposition | Reason |
|---|---|---|---|
| `new` | Opportunity | `discovered` | New lead only. |
| `reviewed` | Opportunity | `manual_review` | Review does not necessarily mean listing verified or eligible. |
| `shortlisted` | Opportunity | `manual_review` | Shortlisting is a triage decision, not proof of eligibility. |
| `application_ready` | Work engagement | `application_ready` | Draft/checklist may be ready; no claim that an application was sent. |
| `applied_by_user` | Work engagement | `applied_by_user` | Explicit owner-action wording; retain source provenance. |
| `task_started_by_user` | Work engagement | `task_started_by_user` | Explicit owner-action wording; not acceptance or payment. |
| `submitted_by_user` | Work engagement | `submitted_by_user` | Explicit owner-action wording; not acceptance or payment. |
| `accepted` | Work engagement | `accepted` | Acceptance remains separate from payout. |
| `rejected` | Work engagement | `rejected` | Preserve terminal state. |
| `not_eligible` | Opportunity | `not_eligible` | Preserve eligibility outcome; never reinterpret as eligible. |
| `paused` | Work engagement | `paused` | Preserve owner pause. |
| `quarantined` | Opportunity / risk | `quarantined` | Preserve the risk hold; never auto-promote during import. |
| `paid` | Payment | `manual_review` | A workflow label is insufficient by itself; require a matching row in `payments` and explicit owner-confirmation provenance. |

## Payment table rules

The SQLite `payments` table requires a positive INR amount, method, evidence note, `owner_confirmed=1`, and confirmation timestamp. The code's report explicitly says this is owner-confirmed, **not independently verified**. During a dry run:

- Do not create a payment from a `paid` status alone.
- Match payment rows to the source lead ID and retain the original payment ID.
- Treat missing or conflicting payment rows as unmapped/manual review.
- Never copy private screenshots, credentials, OTPs, bank/UPI details, or full account identifiers into migration output.
- Do not label owner-entered confirmation as bank/provider verification.

## Required dry-run fixture matrix

A future implementation should have fixtures for:

1. One fixture for every status listed above, including unknown status values.
2. A JSON `paid` task with all required confirmation fields, and variants with missing amount, missing confirmation, and malformed amount.
3. SQLite `paid` with a matching valid payment row, with no payment row, and with mismatched lead ID.
4. A quarantined lead re-imported after its source row changes; the quarantine must not be silently removed.
5. Duplicate source IDs, repeated imports, timestamps, and terminal states.
6. Unknown states, conflicting evidence, and ambiguous JSON application/work states; these must be reported, not guessed.
7. A dry-run mode that performs no writes to source JSON or SQLite files; verify source-file hashes and database row counts before/after.
8. A report summary with counts by source status, proposed mapping, confidence, manual-review reason, and unmapped state.

## Safe implementation sequence

1. Add fixtures and a pure mapping function with no filesystem/database writes.
2. Test every source status and the ambiguous/error cases.
3. Add a read-only CLI dry run that reads copies or opens SQLite read-only, emits a report, and never writes to source ledgers.
4. Review the report before implementing any destination writes.
5. Only after explicit approval, add an importer to a separate new destination with backup/export and rollback. Keep both original ledgers intact.

No consolidation or runtime behavior change is authorized by this document.
