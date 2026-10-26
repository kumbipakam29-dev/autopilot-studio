#!/usr/bin/env python3
"""Read-only aggregate audit of the two AutoPilot ledgers; never modifies source data."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import quote

JSON_MAP = {
    "discovered": ("opportunity", "discovered"),
    "current_listing_verified": ("opportunity", "verified"),
    "eligibility_check": ("opportunity", "eligibility_review"),
    "applied": ("work_engagement", "manual_review"),
    "qualification": ("work_engagement", "manual_review"),
    "approved": ("work_engagement", "manual_review"),
    "work_in_progress": ("work_engagement", "manual_review"),
    "submitted": ("work_engagement", "manual_review"),
    "accepted": ("work_engagement", "accepted_review_evidence"),
    "rejected": ("work_engagement", "rejected"),
    "payout_pending": ("payment", "payout_pending"),
    "paid": ("payment", "manual_review_payment_provenance"),
}

SQLITE_MAP = {
    "new": ("opportunity", "discovered"),
    "reviewed": ("opportunity", "manual_review"),
    "shortlisted": ("opportunity", "manual_review"),
    "application_ready": ("work_engagement", "application_ready"),
    "applied_by_user": ("work_engagement", "applied_by_user"),
    "task_started_by_user": ("work_engagement", "task_started_by_user"),
    "submitted_by_user": ("work_engagement", "submitted_by_user"),
    "accepted": ("work_engagement", "accepted"),
    "rejected": ("work_engagement", "rejected"),
    "not_eligible": ("opportunity", "not_eligible"),
    "paused": ("work_engagement", "paused"),
    "quarantined": ("opportunity_risk", "quarantined"),
    "paid": ("payment", "manual_review_payment_provenance"),
}


def classify(status: str, mapping: dict[str, tuple[str, str]]) -> dict[str, str]:
    """Pure mapping function. Unknown values are reported, never guessed."""
    domain, proposed_status = mapping.get(status, ("unknown", "manual_review_unknown_status"))
    return {
        "source_status": status,
        "proposed_domain": domain,
        "proposed_status": proposed_status,
        "mapping": "explicit" if status in mapping else "unknown_manual_review",
    }


def summarize_statuses(values: list[str], mapping: dict[str, tuple[str, str]]) -> dict[str, Any]:
    counts = Counter(values)
    return {
        "total_records": len(values),
        "by_source_status": [
            {"count": count, **classify(status, mapping)}
            for status, count in sorted(counts.items())
        ],
        "unknown_status_record_count": sum(
            count for status, count in counts.items() if status not in mapping
        ),
    }


def audit_json(path: Path) -> dict[str, Any]:
    # Read only: no mkdir, no writes, and no attempt to repair malformed input.
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("version") != 1 or not isinstance(raw.get("tasks"), list):
        raise ValueError("JSON ledger must have version=1 and a tasks list")
    statuses = []
    malformed_records = 0
    for task in raw["tasks"]:
        if not isinstance(task, dict) or not isinstance(task.get("stage"), str):
            malformed_records += 1
            continue
        statuses.append(task["stage"])
    result = summarize_statuses(statuses, JSON_MAP)
    result["malformed_record_count"] = malformed_records
    result["source"] = "json_task_ledger"
    return result


def audit_sqlite(path: Path) -> dict[str, Any]:
    # mode=ro prevents SQLite from creating a missing DB or writing to an existing DB.
    uri = "file:" + quote(str(path.resolve()), safe="/:") + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as db:
        db.row_factory = sqlite3.Row
        tables = {
            row["name"] for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        if "leads" not in tables:
            raise ValueError("SQLite ledger has no leads table")
        raw_lead_statuses = [
            row[0] for row in db.execute(
                "SELECT workflow_status FROM leads ORDER BY workflow_status"
            ).fetchall()
        ]
        # NULL or non-text statuses are malformed data, not sortable status names.
        lead_statuses = [status for status in raw_lead_statuses if isinstance(status, str)]
        result = summarize_statuses(lead_statuses, SQLITE_MAP)
        result["malformed_record_count"] = len(raw_lead_statuses) - len(lead_statuses)
        result["source"] = "sqlite_work_win_payment_loop"
        result["payments_table_present"] = "payments" in tables
        if "payments" in tables:
            payment_count = db.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
            owner_confirmed_count = db.execute(
                "SELECT COUNT(*) FROM payments WHERE owner_confirmed = 1"
            ).fetchone()[0]
            orphan_count = db.execute(
                "SELECT COUNT(*) FROM payments p LEFT JOIN leads l ON l.lead_id=p.lead_id "
                "WHERE l.lead_id IS NULL"
            ).fetchone()[0]
            result["payment_record_count"] = payment_count
            result["owner_confirmed_payment_record_count"] = owner_confirmed_count
            result["payment_records_without_matching_lead_count"] = orphan_count
            result["independently_verified_payment_count"] = 0
        else:
            result["payment_record_count"] = None
            result["owner_confirmed_payment_record_count"] = None
            result["payment_records_without_matching_lead_count"] = None
            result["independently_verified_payment_count"] = 0
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-ledger", type=Path, help="existing JSON ledger path (read-only)")
    parser.add_argument("--sqlite-ledger", type=Path, help="existing SQLite ledger path (read-only)")
    args = parser.parse_args(argv)
    if not args.json_ledger and not args.sqlite_ledger:
        parser.error("provide --json-ledger and/or --sqlite-ledger")
    report: dict[str, Any] = {
        "mode": "read_only_aggregate_audit",
        "writes_performed": False,
        "payment_truth": "Owner-confirmed records are not independent bank/provider verification.",
        "sources": [],
    }
    try:
        for label, path, audit_fn in (
            ("json_task_ledger", args.json_ledger, audit_json),
            ("sqlite_work_win_payment_loop", args.sqlite_ledger, audit_sqlite),
        ):
            if path is None:
                continue
            if not path.is_file():
                raise FileNotFoundError(f"{label}: file does not exist: {path}")
            report["sources"].append(audit_fn(path))
    except (OSError, ValueError, json.JSONDecodeError, sqlite3.Error) as exc:
        print(json.dumps({"error": str(exc), "writes_performed": False}, indent=2), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
