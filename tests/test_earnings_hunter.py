import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "agents" / "earnings_hunter.py"
SPEC = importlib.util.spec_from_file_location("earnings_hunter", MODULE_PATH)
earnings = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(earnings)

class EarningsHunterTests(unittest.TestCase):
    def test_rupee_target_amount_is_detected(self):
        currency, amount, signal = earnings.extract_amount("₹150 per approved task")
        self.assertEqual(currency, "INR")
        self.assertIn("₹150", amount)
        self.assertEqual(signal, "TARGET_RANGE_MATCH")

    def test_unknown_rate_is_not_invented(self):
        self.assertEqual(earnings.extract_amount("Rate disclosed after qualification"), ("", "", "NO_PUBLIC_AMOUNT_FOUND"))

    def test_foreign_currency_is_not_silently_converted(self):
        currency, amount, signal = earnings.extract_amount("$10 per task")
        self.assertEqual(currency, "FOREIGN_CURRENCY_UNCONVERTED")
        self.assertIn("$10", amount)
        self.assertEqual(signal, "CURRENCY_CONVERSION_AND_PAYOUT_CHECK_REQUIRED")

    def test_duplicate_rupee_mentions_are_deduplicated(self):
        currency, amount, signal = earnings.extract_amount("₹2 per task, approved at ₹2; overall unrelated ₹7")
        self.assertEqual(currency, "INR")
        self.assertEqual(amount, "₹2, ₹7")
        self.assertEqual(signal, "INR_AMOUNT_OUTSIDE_TARGET")

    def test_risky_fake_review_lead_is_quarantined(self):
        _, _, _, _, status = earnings.score_candidate("Earn ₹100: post fake reviews", "task", "Example", "India")
        self.assertIn("QUARANTINE_RISK_REVIEW", status)

    def test_human_submission_required(self):
        candidate = earnings.make_candidate(earnings.SOURCES[0], "Hindi recording project", "https://work.karmyug.in/", "Recording task", "fetched", "OFFICIAL_PAGE_SCAN")
        self.assertEqual(candidate["automation_status"], "DISCOVERY_ONLY_NO_LOGIN_NO_SUBMISSION")
        self.assertIn("manually", candidate["required_next_step"])

    def test_link_priority_prefers_general_language_work_over_us_only_specialty(self):
        india_task = earnings.task_link_priority("Apply", "https://www.oneforma.com/projects/online-data-labeling-and-search-evaluation-tasks/")
        us_specialty = earnings.task_link_priority("Apply", "https://www.oneforma.com/projects/physician-clinical-reasoning-reviewer-ehr-cases/")
        self.assertGreater(india_task, us_specialty)

    def test_unsafe_external_link_not_allowed(self):
        self.assertFalse(earnings.allowed_same_site_url("https://evil.example/task", "https://work.karmyug.in/"))
        self.assertTrue(earnings.allowed_same_site_url("/jobs/", "https://work.karmyug.in/"))

    def test_detail_page_extracts_rate_and_eligibility(self):
        parser = earnings.PageParser()
        parser.text_parts = ["Recording project", "₹150 per approved task", "Open to residents in India", "Payment weekly"]
        facts = earnings.relevant_detail_facts(parser)
        self.assertIn("₹150", facts)
        self.assertIn("per approved task", facts)
        self.assertIn("weekly", facts)
        evidence = earnings.eligibility_evidence(facts)
        self.assertIn("India", evidence)

    def test_unrelated_recommendation_rates_are_excluded(self):
        parser = earnings.PageParser()
        parser.text_parts = [
            "Online Data Labeling and Search Evaluation Tasks",
            "Work involves annotation and evaluation for supported languages.",
            "Rates are shown after qualification.",
            "Similar Projects",
            "$150 USD per hour",
            "$130 to $150 per hour",
        ]
        facts = earnings.relevant_detail_facts(parser)
        self.assertNotIn("$150", facts)
        self.assertNotIn("$130", facts)
        self.assertIn("labeling", facts.lower())

    def test_rate_after_long_generic_page_chrome_is_not_promoted(self):
        parser = earnings.PageParser()
        parser.text_parts = ["Navigation and generic website content " * 40, "$150 USD per hour"]
        facts = earnings.relevant_detail_facts(parser)
        self.assertNotIn("$150", facts)

    def test_offline_run_writes_expected_files(self):
        old_out = earnings.OUT
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                earnings.OUT = Path(temp_dir)
                result = earnings.run_hunt(offline=True, limit=20)
                self.assertTrue(result.exists())
                self.assertTrue((Path(temp_dir) / "source_status.csv").exists())
                self.assertTrue((Path(temp_dir) / "earnings_tracker_template.csv").exists())
                self.assertTrue((Path(temp_dir) / "earnings_hunt_report.md").exists())
        finally:
            earnings.OUT = old_out

if __name__ == "__main__":
    unittest.main()
