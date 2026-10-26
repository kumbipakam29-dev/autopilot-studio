# Read-only ledger status audit

This tool produces an aggregate report from existing AutoPilot Studio task/payment ledgers. It is an audit aid, not a migration tool, reconciliation system, or proof of earnings.

## Safety properties

- Opens the JSON ledger for reading only.
- Opens SQLite with `mode=ro`; it does not create a missing database.
- Does not update, merge, delete, or repair source records.
- Keeps unknown status values in manual review rather than guessing.
- Reports aggregate counts only, not individual lead/payment details.
- Treats owner-confirmed payment rows as **not independently verified** bank/provider evidence.

## Run

From the repository root, point the tool at one or both existing local files:

```bash
python tools/ledger_status_audit.py --json-ledger path/to/task-ledger.json
python tools/ledger_status_audit.py --sqlite-ledger path/to/work-win-ledger.sqlite3
python tools/ledger_status_audit.py --json-ledger path/to/task-ledger.json --sqlite-ledger path/to/work-win-ledger.sqlite3
```

Use actual local file paths from your own setup; the tool does not search for ledgers automatically. If a supplied file is missing or invalid, it prints an error to stderr and exits with code 2. It never creates a replacement database.

## Reading the report

- `total_records`: records with a valid string status (for JSON, valid task objects with a string `stage`; for SQLite, rows with a text `workflow_status`).
- `malformed_record_count`: records missing a usable status or not shaped as expected.
- `unknown_status_record_count`: records whose status is not in the explicit mapping.
- `proposed_status`: conservative suggested classification only; it is not a migration instruction.
- `payment_records_without_matching_lead_count`: payment rows with no corresponding lead ID.
- `independently_verified_payment_count`: always zero in this report because this local ledger audit does not verify bank/provider records.

## Required next step

Review unknown and malformed records manually against their original source and evidence. Do not bulk-map statuses or consolidate ledgers based on these aggregate counts alone. Any future migration must have a separately reviewed mapping, backup, dry-run, rollback plan, and explicit owner approval.
