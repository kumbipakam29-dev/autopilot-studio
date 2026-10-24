import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agents"))
import data_labeling_hunter as hunter

class PayEvidenceTests(unittest.TestCase):
    def test_inr_per_accepted_task(self):
        self.assertEqual(hunter.extract_pay_evidence("Payment: ₹2 per accepted task"), ("INR", "2", "per accepted task", "Payment: ₹2 per accepted task"))

    def test_inr_per_approved_task(self):
        self.assertEqual(hunter.extract_pay_evidence("Hindi recording pays ₹2 per approved task"), ("INR", "2", "per approved task", "Hindi recording pays ₹2 per approved task"))

    def test_usd_per_hour_is_not_per_task(self):
        cur, amount, unit, evidence = hunter.extract_pay_evidence("Pay is USD $2 per hour")
        self.assertEqual((cur, amount, unit), ("USD", "2", "per hour"))
        self.assertNotIn("task", unit)

    def test_amount_without_unit_is_not_rate(self):
        self.assertEqual(hunter.extract_pay_evidence("Earn ₹200 today, apply now"), ("", "", "", ""))

    def test_wrong_hours_number_is_not_currency(self):
        self.assertEqual(hunter.extract_pay_evidence("Work 8 hours, reward is unknown"), ("", "", "", ""))

class RiskTests(unittest.TestCase):
    def test_upfront_fee_quarantined(self):
        self.assertIn("upfront_fee", hunter.classify_risk("Pay registration fee to start."))

    def test_official_no_fee_warning_not_quarantined(self):
        text = "We never charge to join. There is no registration fee or deposit. Never pay to unlock tasks."
        self.assertEqual(hunter.classify_risk(text), [])

    def test_denial_does_not_hide_a_separate_scam_offer(self):
        text = "No fee is required for this platform. Pay an activation deposit to unlock this specific job."
        flags = hunter.classify_risk(text)
        self.assertIn("deposit", flags)

    def test_account_rental_flagged(self):
        self.assertIn("account_rental", hunter.classify_risk("Rent your account for money."))

    def test_otp_request_flagged(self):
        self.assertIn("credential_request", hunter.classify_risk("Send your OTP to the recruiter."))

    def test_fake_review_flagged(self):
        self.assertIn("fake_reviews", hunter.classify_risk("Earn cash by posting fake reviews."))

    def test_captcha_bypass_flagged(self):
        self.assertIn("captcha_bypass", hunter.classify_risk("Use captcha bypass to finish tasks."))

class HtmlTests(unittest.TestCase):
    def test_html_stripping_and_title(self):
        title, body = hunter.strip_html(b"<html><title>Test Job</title><script>bad()</script><p>Pay: Rs 50 per task</p></html>")
        self.assertEqual(title, "Test Job")
        self.assertIn("Pay: Rs 50 per task", body)
        self.assertNotIn("bad()", body)

    def test_only_same_host_links(self):
        raw = '<a href="/jobs/1">one</a><a href="https://evil.example/x">offsite</a><a href="http://example.com/no">http</a>'
        links = hunter.find_links("https://example.com/jobs", raw)
        self.assertEqual(links, ["https://example.com/jobs/1"])

    def test_login_and_register_links_are_excluded(self):
        raw = '<a href="/login">login</a><a href="/register">register</a><a href="/jobs/abc">task</a>'
        links = hunter.find_links("https://example.com/jobs", raw)
        self.assertEqual(links, ["https://example.com/jobs/abc"])

    def test_invalid_url_blocked(self):
        _, status, _ = hunter.fetch_public("http://example.com")
        self.assertEqual(status, "blocked_url")


class EligibilityAndPriorityTests(unittest.TestCase):
    def test_generic_openings_landing_page_is_not_a_task_detail(self):
        source = next(s for s in hunter.SOURCES if s.name == "YPAI Data Annotator India")
        url = "https://freelancer.ypai.ai/jobs/openings/"
        raw = "<html><title>Open freelance roles, rates listed</title><p>Typical pay INR 550-800 per hour.</p></html>"
        lead = hunter.make_lead(source, url, "200", raw)
        self.assertFalse(hunter.is_task_detail_url(source, url))
        self.assertEqual(lead.currency, "")
        self.assertEqual(lead.amount, "")

    def test_generic_slug_ending_in_jobs_is_not_detail(self):
        source = next(s for s in hunter.SOURCES if s.name.startswith("OpenTrain Python"))
        self.assertFalse(hunter.is_task_detail_url(source, "https://www.opentrain.ai/jobs/remote-ai-code-evaluator-jobs"))

    def test_specific_job_slug_is_detail(self):
        source = next(s for s in hunter.SOURCES if s.name.startswith("OpenTrain Python"))
        self.assertTrue(hunter.is_task_detail_url(source, "https://www.opentrain.ai/jobs/c-llm-evaluation-engineer-cm123"))

    def test_child_job_does_not_inherit_india_from_parent_source(self):
        source = next(s for s in hunter.SOURCES if s.name == "YPAI Data Annotator India")
        url = "https://freelancer.ypai.ai/jobs/remote-reviewer-cm123"
        raw = "<html><title>Remote Reviewer</title><p>Typical project pay INR 550-800 per hour.</p></html>"
        lead = hunter.make_lead(source, url, "200", raw)
        self.assertEqual(lead.fit_hint, "ELIGIBILITY_UNKNOWN_VERIFY")

    def test_generic_us_physician_rate_is_not_promoted(self):
        source = next(s for s in hunter.SOURCES if s.name == "OneForma Jobs")
        raw = "<html><title>Open Freelance Projects</title><p>Review clinical reasoning tasks. Remote, for physicians in the United States, $150 USD per hour.</p></html>"
        lead = hunter.make_lead(source, source.url, "200", raw)
        self.assertEqual(lead.currency, "")
        self.assertEqual(lead.fit_hint, "LIKELY_NOT_ELIGIBLE_INDIA")
        self.assertEqual(lead.priority_score, 0)
        self.assertEqual(lead.status, "eligibility_mismatch_review")

    def test_ypai_role_page_keeps_specific_inr_range(self):
        source = next(s for s in hunter.SOURCES if s.name == "YPAI Data Annotator India")
        raw = "<html><title>Data Annotator, India</title><p>Typical project pay INR 550–800 per hour.</p><p>Applications open in India.</p></html>"
        lead = hunter.make_lead(source, source.url, "200", raw)
        self.assertEqual((lead.currency, lead.amount, lead.pay_unit), ("INR", "550-800", "per hour"))
        self.assertEqual(lead.fit_hint, "INDIA_RELEVANT_VERIFY")
        self.assertGreaterEqual(lead.priority_score, 75)

    def test_generic_homepage_amount_is_not_a_task_rate(self):
        source = next(s for s in hunter.SOURCES if s.name == "HumanSignal AI Training Contributors")
        raw = "<html><title>Contributor portal</title><p>Some projects pay $500 per hour. Match to an eligible project first.</p></html>"
        lead = hunter.make_lead(source, source.url, "200", raw)
        self.assertEqual(lead.currency, "")
        self.assertEqual(lead.amount, "")
        self.assertIn("broad page", lead.caveat)

class HighValueSourceTests(unittest.TestCase):
    def test_ypai_rate_range_keeps_hour_unit(self):
        cur, amount, unit, evidence = hunter.extract_pay_evidence("Typical project pay INR 550-800 per hour")
        self.assertEqual((cur, amount, unit), ("INR", "550-800", "per hour"))
        self.assertIn("550-800", evidence)

    def test_unicode_dash_range_normalizes(self):
        cur, amount, unit, _ = hunter.extract_pay_evidence("Rate: INR 550–800 per hour")
        self.assertEqual((cur, amount, unit), ("INR", "550-800", "per hour"))

    def test_higher_value_sources_are_registered(self):
        names = {source.name for source in hunter.SOURCES}
        self.assertIn("YPAI Data Annotator India", names)
        self.assertIn("YPAI Model Evaluator India", names)
        self.assertIn("YPAI Data Collection Contributor India", names)
        self.assertIn("HumanSignal AI Training Contributors", names)

    def test_expanded_ypai_roles_are_registered(self):
        sources = {source.name: source for source in hunter.SOURCES}
        expected = [
            "YPAI Text and NLP Annotator India",
            "YPAI Image Annotator India",
            "YPAI Pose and Keypoint Annotator India",
            "YPAI Transcriber with Diarization India",
            "YPAI Diarization Specialist India",
        ]
        for name in expected:
            self.assertIn(name, sources)
            self.assertTrue(sources[name].specific_page)

    def test_outlier_india_rate_stays_usd_hourly(self):
        source = next(s for s in hunter.SOURCES if s.name == "Outlier Coding Expertise — India")
        raw = "<html><title>Coding Expertise for AI Training - India</title><p>Core project work coding experts in India average USD $13.75 per hour. Experienced software engineers required.</p></html>"
        lead = hunter.make_lead(source, source.url, "200", raw)
        self.assertEqual((lead.currency, lead.amount, lead.pay_unit), ("USD", "13.75", "per hour"))
        self.assertEqual(lead.fit_hint, "INDIA_RELEVANT_VERIFY")

    def test_rws_source_does_not_claim_a_fixed_rate(self):
        source = next(s for s in hunter.SOURCES if s.name == "RWS TrainAI Community")
        self.assertFalse(source.specific_page)
        raw = "<html><title>TrainAI Community</title><p>Payment depends on each project and tasks are paid per task.</p></html>"
        lead = hunter.make_lead(source, source.url, "200", raw)
        self.assertEqual(lead.currency, "")
        self.assertEqual(lead.amount, "")

    def test_open_train_specialist_role_is_labelled_as_specialist(self):
        source = next(s for s in hunter.SOURCES if s.name.startswith("OpenTrain Python"))
        self.assertIn("specialist", source.notes.lower())


if __name__ == "__main__":
    unittest.main()
