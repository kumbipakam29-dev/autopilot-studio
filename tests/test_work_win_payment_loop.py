import csv
import sqlite3
import tempfile
import unittest
from pathlib import Path

from agents.work_win_payment_loop import (
    confirm_payment, draft_client_pitches, get_status, import_opportunities,
    next_action, run_cycle, stable_lead_id, update_lead_status,
)


class WorkWinPaymentLoopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.ledger = self.root / "private" / "ledger.sqlite3"
        self.output = self.root / "output"
        self.opportunities = self.root / "opportunities.csv"

    def tearDown(self):
        self.temp.cleanup()

    def _write_opportunities(self, rows):
        fields = ["source", "title", "url", "region_or_eligibility", "task_type",
                  "public_amount_text", "currency", "payment_signal", "triage_score",
                  "triage_status", "public_detail_evidence"]
        with self.opportunities.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_stable_id_is_reproducible(self):
        self.assertEqual(stable_lead_id("source", "https://example.org/job"),
                         stable_lead_id("source", "https://example.org/job"))

    def test_risk_quarantine_cannot_be_bypassed(self):
        self.assertIn("STOP", next_action("quarantined", "QUARANTINE_RISK_REVIEW", "₹100"))

    def test_import_update_and_payment_confirmation_gate(self):
        self._write_opportunities([{
            "source": "Official source", "title": "Example labeling task",
            "url": "https://example.org/task", "region_or_eligibility": "India",
            "task_type": "annotation", "public_amount_text": "₹100",
            "currency": "INR", "payment_signal": "TARGET_RANGE_MATCH",
            "triage_score": "40", "triage_status": "REVIEW_TERMS",
            "public_detail_evidence": "Rate shown on public page"
        }])
        imported, quarantined = import_opportunities(self.opportunities, self.ledger)
        self.assertEqual((imported, quarantined), (1, 0))
        lead_id = stable_lead_id("Official source", "https://example.org/task")
        update_lead_status(lead_id, "accepted", "provider accepted work")
        with self.assertRaisesRegex(ValueError, "confirm-received"):
            confirm_payment(lead_id, 100, "UPI", "checked actual credit", False, self.ledger)
        recorded = confirm_payment(lead_id, 100, "UPI", "actual credit checked in payment app today", True, self.ledger)
        self.assertEqual(recorded["status"], "paid_owner_confirmed")
        self.assertFalse(recorded["independently_verified"])
        status = get_status(self.ledger)
        self.assertEqual(status["owner_confirmed_payments_count"], 1)
        self.assertEqual(status["owner_confirmed_payments_total_inr"], 100.0)

    def test_quarantined_lead_status_cannot_be_changed(self):
        self._write_opportunities([{
            "source": "Risky source", "title": "Pay fee to unlock job",
            "url": "https://example.org/risky", "region_or_eligibility": "India",
            "task_type": "task", "public_amount_text": "", "currency": "",
            "payment_signal": "NO_PUBLIC_AMOUNT_FOUND", "triage_score": "-100",
            "triage_status": "QUARANTINE_RISK_REVIEW", "public_detail_evidence": ""
        }])
        import_opportunities(self.opportunities, self.ledger)
        lead_id = stable_lead_id("Risky source", "https://example.org/risky")
        with self.assertRaisesRegex(ValueError, "quarantined"):
            update_lead_status(lead_id, "shortlisted", "", self.ledger)

    def test_offline_cycle_creates_report_without_network(self):
        result = run_cycle(limit=10, offline=True, ledger_path=self.ledger, output_dir=self.output)
        self.assertEqual(result["status"], "completed")
        self.assertTrue(Path(result["queue_csv"]).exists())
        self.assertTrue(Path(result["report_md"]).exists())
        self.assertFalse(result["database_upload_allowed"])
        self.assertGreater(result["total_leads_in_ledger"], 0)

    def test_client_pitches_are_drafts_only(self):
        prospects = self.root / "prospects.csv"
        with prospects.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["business_name", "business_type", "public_profile_url", "observation", "recommended_idea"])
            writer.writeheader()
            writer.writerow({"business_name":"Test Cafe","business_type":"cafe",
                             "public_profile_url":"https://example.org/cafe",
                             "observation":"the public menu post has no clear enquiry prompt",
                             "recommended_idea":"a short behind-the-scenes coffee Reel"})
        result = draft_client_pitches(prospects, self.output)
        self.assertEqual(result["draft_count"], 1)
        self.assertEqual(result["messages_sent"], 0)
        self.assertIn("DRAFT_ONLY_NOT_SENT", (self.output / "client_outreach_drafts.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
