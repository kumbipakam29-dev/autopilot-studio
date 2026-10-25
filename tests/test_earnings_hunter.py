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

    def test_hour_abbreviation_is_not_a_rupee_symbol(self):
        self.assertEqual(earnings.extract_amount("Long-term remote work, 10 hr per week"), ("", "", "NO_PUBLIC_AMOUNT_FOUND"))
        self.assertEqual(earnings.extract_amount("Work requires 20 hrs per month"), ("", "", "NO_PUBLIC_AMOUNT_FOUND"))

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

    def test_india_relevant_sources_are_in_registry(self):
        names = {source["name"] for source in earnings.SOURCES}
        self.assertIn("uTest — Project Radar Hindi-English subtitle evaluation", names)
        self.assertIn("UserTest Pro India", names)
        self.assertIn("Smallest AI Contributor", names)
        self.assertIn("Corpshore / Jwuma India AI data work", names)
        self.assertIn("Prolific participant studies", names)

    def test_new_direct_task_sources_are_registered(self):
        by_name = {source["name"]: source for source in earnings.SOURCES}
        self.assertIn("YPAI — Hindi Annotation Roles", by_name)
        self.assertFalse(by_name["YPAI — Hindi Annotation Roles"].get("detail_page"))
        for name in (
            "YPAI — Data Annotator India",
            "YPAI — Text and NLP Annotator India",
            "YPAI — Data Collection Contributor India",
            "Perit — Hindi Freelance AI Data Annotator",
            "TSMG — Hindi Audio Transcription Specialist",
            "Sigma AI — Hindi, Bengali and English linguistic projects",
            "Lionbridge — Hindi Transcriber",
        ):
            self.assertTrue(by_name[name].get("detail_page"), name)

    def test_direct_source_extracts_visible_root_task_evidence(self):
        source = {
            "name": "Test direct task",
            "url": "https://example.org/jobs/hindi-annotator",
            "type": "Hindi annotation",
            "region": "India",
            "payout_note": "Confirm rate before accepting",
            "detail_page": True,
        }
        original_fetch = earnings.fetch_public_page
        try:
            earnings.fetch_public_page = lambda url, require_same_path=False: (
                "<html><title>Hindi Annotator</title><body><p>Rate ₹550–₹800 per hour. Remote in India. "
                "Payment after validated work.</p></body></html>", "fetched"
            )
            rows, _ = earnings.discover_source(source)
        finally:
            earnings.fetch_public_page = original_fetch
        self.assertEqual(rows[0]["candidate_type"], "TASK_DETAIL_PAGE")
        self.assertIn("₹550", rows[0]["public_detail_evidence"])
        self.assertIn("India", rows[0]["eligibility_evidence"])
        self.assertEqual(rows[0]["payment_signal"], "INR_AMOUNT_OUTSIDE_TARGET")

    def test_generic_board_does_not_promote_payout_note_or_inherit_region(self):
        source = {
            "name": "Test public job board",
            "url": "https://example.org/careers/",
            "type": "Remote annotation roles",
            "region": "India",
            "payout_note": "Related roles may advertise ₹550–₹800 per hour; this is not a board rate.",
        }
        original_fetch = earnings.fetch_public_page
        def fake_fetch(url, require_same_path=False):
            if url == source["url"]:
                return (
                    '<html><title>Careers</title><body><p>Browse current roles.</p>'
                    '<a href="/jobs/hindi-transcriber">Hindi Transcriber</a></body></html>',
                    "fetched",
                )
            return (
                '<html><title>Transcriber Role</title><body><p>Rate $10 per hour. '
                'Role details should be checked with the employer.</p></body></html>',
                "fetched",
            )
        try:
            earnings.fetch_public_page = fake_fetch
            rows, _ = earnings.discover_source(source)
        finally:
            earnings.fetch_public_page = original_fetch
        root = next(row for row in rows if row["candidate_type"] == "OFFICIAL_PAGE_SCAN")
        detail = next(row for row in rows if row["candidate_type"] == "TASK_DETAIL_PAGE")
        self.assertEqual(root["public_amount_text"], "")
        self.assertEqual(root["currency"], "")
        self.assertEqual(detail["task_type"], "Transcriber Role")
        self.assertIn("Not established", detail["region_or_eligibility"])
        self.assertEqual(detail["currency"], "FOREIGN_CURRENCY_UNCONVERTED")

    def test_parent_link_salary_is_not_attributed_to_child_role(self):
        source = {
            "name": "Example careers board",
            "url": "https://example.org/careers/",
            "type": "Remote annotation roles",
            "region": "India",
            "payout_note": "Parent page has links to multiple roles.",
        }
        original_fetch = earnings.fetch_public_page
        def fake_fetch(url, require_same_path=False):
            if url == source["url"]:
                return (
                    '<html><title>Careers</title><body><p>Browse current roles.</p>'
                    '<a href="/careers/ai-data-annotation-ftc-india">'
                    'AI Data Annotation (FTC) Full-time · $260–365 / month</a></body></html>',
                    "fetched",
                )
            return (
                '<html><title>AI Data Annotation (FTC)</title><body>'
                '<p>Work involves labeling text and reviewing AI outputs.</p>'
                '</body></html>',
                "fetched",
            )
        try:
            earnings.fetch_public_page = fake_fetch
            rows, _ = earnings.discover_source(source)
        finally:
            earnings.fetch_public_page = original_fetch
        child = next(row for row in rows if row["candidate_type"] == "TASK_DETAIL_PAGE")
        self.assertEqual(child["public_amount_text"], "")
        self.assertEqual(child["currency"], "")
        self.assertEqual(child["payment_signal"], "NO_PUBLIC_AMOUNT_FOUND")
        self.assertIn("Not established", child["region_or_eligibility"])

    def test_hourly_paid_roles_rank_above_very_low_per_task_rate(self):
        hourly_score = earnings.score_candidate(
            "AI Data Annotator",
            "₹550–₹800 per hour for approved annotation work",
            "YPAI",
            "India",
        )[0]
        per_task_score = earnings.score_candidate(
            "Hindi Recording Task",
            "₹2 per approved task",
            "Karmyug AI",
            "India",
        )[0]
        self.assertGreater(hourly_score, per_task_score)

    def test_career_paths_are_scanned_as_role_details(self):
        self.assertTrue(earnings.is_task_detail_path("https://perit.ai/careers/ai-data-annotation-ftc-india"))
        self.assertTrue(earnings.is_task_detail_path("https://jobs.lever.co/tsmg/6a9979b9-3929-4e1d-9689-97926bc65dd5"))
        self.assertTrue(earnings.is_task_detail_path("https://www.oneforma.com/projects/paragraph-level-translation-quality-rater/"))
        self.assertFalse(earnings.is_task_detail_path("https://perit.ai/careers/"))
        self.assertFalse(earnings.is_task_detail_path("https://www.oneforma.com/projects/"))

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
        self.assertIn("qualification", facts.lower())

    def test_rate_after_long_generic_page_chrome_is_not_promoted(self):
        parser = earnings.PageParser()
        parser.text_parts = ["Navigation and generic website content " * 40, "$150 USD per hour"]
        facts = earnings.relevant_detail_facts(parser)
        self.assertNotIn("$150", facts)

    def test_generic_platform_amount_is_not_counted_as_task_rate(self):
        rows = [{
            "candidate_type": "OFFICIAL_PAGE_SCAN",
            "payment_signal": "TARGET_RANGE_MATCH",
            "triage_status": "REVIEW_TERMS",
            "public_detail_evidence": "",
        }]
        self.assertEqual(earnings.count_verified_target_rate_rows(rows), 0)

    def test_target_rate_requires_specific_task_detail_evidence(self):
        rows = [{
            "candidate_type": "TASK_DETAIL_PAGE",
            "payment_signal": "TARGET_RANGE_MATCH",
            "triage_status": "REVIEW_TERMS",
            "public_detail_evidence": "₹150 per approved task",
        }]
        self.assertEqual(earnings.count_verified_target_rate_rows(rows), 1)

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
