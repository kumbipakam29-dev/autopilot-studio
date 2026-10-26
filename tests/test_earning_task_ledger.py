import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agents"))
import earning_task_ledger as ledger


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.data = {"version": 1, "tasks": []}
        ledger.add_task(
            self.data, "T1", "Demo label task", "https://example.org/job",
            "INR", "100", "per task"
        )

    def advance_to_payout_pending(self):
        for stage in (
            "current_listing_verified", "eligibility_check", "applied",
            "qualification", "approved", "work_in_progress", "submitted",
        ):
            ledger.update_stage(self.data, "T1", stage)
        ledger.update_stage(self.data, "T1", "accepted", accepted_amount="100")
        ledger.update_stage(self.data, "T1", "payout_pending")

    def test_discovered_is_not_income(self):
        task = self.data["tasks"][0]
        self.assertEqual(task["stage"], "discovered")
        self.assertFalse(task["payout_confirmed_by_user"])
        self.assertEqual(task["payout_received_amount"], "")

    def test_paid_requires_confirmation(self):
        self.advance_to_payout_pending()
        with self.assertRaisesRegex(ValueError, "(?i)user confirms credit"):
            ledger.update_stage(self.data, "T1", "paid", payout_amount="100")

    def test_accepted_requires_amount(self):
        with self.assertRaisesRegex(ValueError, "(?i)accepted amount"):
            ledger.update_stage(self.data, "T1", "accepted")

    def test_cannot_skip_stages_to_paid(self):
        with self.assertRaisesRegex(ValueError, "(?i)invalid stage transition"):
            ledger.update_stage(
                self.data, "T1", "paid", payout_amount="100", payout_confirmed=True
            )

    def test_paid_requires_actual_amount(self):
        self.advance_to_payout_pending()
        with self.assertRaisesRegex(ValueError, "(?i)actual payout amount"):
            ledger.update_stage(self.data, "T1", "paid", payout_confirmed=True)

    def test_positive_amounts_accept_currency_and_thousands_separators(self):
        for stage in (
            "current_listing_verified", "eligibility_check", "applied",
            "qualification", "approved", "work_in_progress", "submitted",
        ):
            ledger.update_stage(self.data, "T1", stage)
        ledger.update_stage(
            self.data, "T1", "accepted", accepted_amount="INR 1,250.50"
        )
        self.assertEqual(self.data["tasks"][0]["accepted_amount"], "INR 1,250.50")
        ledger.update_stage(self.data, "T1", "payout_pending")
        ledger.update_stage(
            self.data, "T1", "paid", payout_amount="₹1,250.50", payout_confirmed=True
        )
        self.assertEqual(
            self.data["tasks"][0]["payout_received_amount"], "₹1,250.50"
        )

    def test_user_confirmed_paid_stage(self):
        self.advance_to_payout_pending()
        ledger.update_stage(
            self.data, "T1", "paid", payout_amount="100", payout_confirmed=True
        )
        task = self.data["tasks"][0]
        self.assertTrue(task["payout_confirmed_by_user"])
        self.assertEqual(task["payout_received_amount"], "100")
        self.assertEqual(task["stage"], "paid")

    def test_minutes_accumulate_on_valid_transitions(self):
        ledger.update_stage(self.data, "T1", "current_listing_verified", minutes=5)
        ledger.update_stage(self.data, "T1", "eligibility_check", minutes=7)
        self.assertEqual(self.data["tasks"][0]["minutes_spent"], 12)

    def test_invalid_minutes_rejected(self):
        for value in (-1, 1.5, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    ledger.update_stage(self.data, "T1", "discovered", minutes=value)

    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError):
            ledger.add_task(self.data, "T1", "Duplicate", "https://example.org")

    def test_json_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.json"
            ledger.save(path, self.data)
            loaded = ledger.load(path)
            self.assertEqual(loaded["tasks"][0]["task_id"], "T1")


if __name__ == "__main__":
    unittest.main()
