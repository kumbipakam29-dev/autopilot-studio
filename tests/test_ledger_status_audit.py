import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tools.ledger_status_audit import (
    JSON_MAP, SQLITE_MAP, audit_json, audit_sqlite, classify, summarize_statuses,
)


class LedgerStatusAuditTests(unittest.TestCase):
    def test_every_declared_json_stage_has_explicit_mapping(self):
        stages = {
            "discovered", "current_listing_verified", "eligibility_check", "applied",
            "qualification", "approved", "work_in_progress", "submitted", "accepted",
            "rejected", "payout_pending", "paid",
        }
        self.assertEqual(stages, set(JSON_MAP))
        self.assertTrue(all(classify(stage, JSON_MAP)["mapping"] == "explicit" for stage in stages))

    def test_every_declared_sqlite_status_has_explicit_mapping(self):
        statuses = {
            "new", "reviewed", "shortlisted", "application_ready", "applied_by_user",
            "task_started_by_user", "submitted_by_user", "accepted", "rejected",
            "not_eligible", "paused", "quarantined", "paid",
        }
        self.assertEqual(statuses, set(SQLITE_MAP))
        self.assertTrue(all(classify(status, SQLITE_MAP)["mapping"] == "explicit" for status in statuses))

    def test_unknown_status_is_not_guessed(self):
        item = classify("surprise_status", JSON_MAP)
        self.assertEqual(item["proposed_domain"], "unknown")
        self.assertEqual(item["mapping"], "unknown_manual_review")
        summary = summarize_statuses(["paid", "surprise_status", "surprise_status"], JSON_MAP)
        self.assertEqual(summary["unknown_status_record_count"], 2)

    def test_json_audit_counts_statuses_and_does_not_rewrite_source(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ledger.json"
            original = json.dumps({"version": 1, "tasks": [
                {"task_id": "A", "stage": "paid"},
                {"task_id": "B", "stage": "mystery"},
                {"task_id": "C"},
            ]})
            path.write_text(original, encoding="utf-8")
            report = audit_json(path)
            self.assertEqual(report["total_records"], 2)
            self.assertEqual(report["unknown_status_record_count"], 1)
            self.assertEqual(report["malformed_record_count"], 1)
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_sqlite_audit_opens_read_only_and_reports_payment_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ledger.sqlite3"
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE leads (lead_id TEXT PRIMARY KEY, workflow_status TEXT)")
                db.execute("CREATE TABLE payments (payment_id TEXT, lead_id TEXT, owner_confirmed INTEGER)")
                db.execute("INSERT INTO leads VALUES ('L1', 'paid')")
                db.execute("INSERT INTO leads VALUES ('L2', 'quarantined')")
                db.execute("INSERT INTO leads VALUES ('L3', NULL)")
                db.execute("INSERT INTO payments VALUES ('P1', 'L1', 1)")
                db.execute("INSERT INTO payments VALUES ('P2', 'MISSING', 1)")
            before = path.read_bytes()
            report = audit_sqlite(path)
            self.assertEqual(report["total_records"], 2)
            self.assertEqual(report["malformed_record_count"], 1)
            self.assertEqual(report["payment_record_count"], 2)
            self.assertEqual(report["payment_records_without_matching_lead_count"], 1)
            self.assertEqual(report["independently_verified_payment_count"], 0)
            self.assertEqual(path.read_bytes(), before)

    def test_sqlite_missing_path_is_not_created(self):
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "missing.sqlite3"
            with self.assertRaises(sqlite3.OperationalError):
                audit_sqlite(missing)
            self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
