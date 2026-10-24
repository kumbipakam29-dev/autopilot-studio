import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agents"))
import data_labeling_hunter as hunter

class PayEvidenceTests(unittest.TestCase):
    def test_inr_per_accepted_task(self):
        self.assertEqual(hunter.extract_pay_evidence("Payment: ₹2 per accepted task"), ("INR", "2", "per accepted task", "Payment: ₹2 per accepted task"))

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

    def test_invalid_url_blocked(self):
        _, status, _ = hunter.fetch_public("http://example.com")
        self.assertEqual(status, "blocked_url")


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

    def test_open_train_specialist_role_is_labelled_as_specialist(self):
        source = next(s for s in hunter.SOURCES if s.name.startswith("OpenTrain Python"))
        self.assertIn("specialist", source.notes.lower())


if __name__ == "__main__":
    unittest.main()
