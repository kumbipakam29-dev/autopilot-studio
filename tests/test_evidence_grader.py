import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "agents" / "evidence_grader.py"
SPEC = importlib.util.spec_from_file_location("aps_evidence_grader", MODULE)
grader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(grader)


class EvidenceGraderTests(unittest.TestCase):
    def test_complete_evidence_still_requires_review_and_is_not_payment(self):
        report = grader.grade_evidence({
            "candidate_id": "fixture-1",
            "official_source_url": "https://official.example/jobs/1",
            "country_eligibility": "India explicitly listed",
            "task_rate_unit": "₹12 per accepted item",
            "acceptance_criteria": "Labels must match rubric v1",
            "payout_details": "Minimum payout and method stated on official page",
        })
        self.assertEqual(report["status"], "evidence_complete_review_required")
        self.assertTrue(report["evidence_complete"])
        self.assertTrue(report["approval_required"])
        self.assertFalse(report["payment_verified"])
        self.assertEqual(report["external_actions_taken"], 0)

    def test_missing_and_unknown_fields_fail_closed(self):
        report = grader.grade_evidence({
            "official_source_url": "http://not-secure.example",
            "country_eligibility": "unknown",
            "task_rate_unit": "TBD",
            "acceptance_criteria": "",
            "payout_details": "not stated",
        })
        self.assertEqual(report["status"], "needs_human_review")
        self.assertFalse(report["evidence_complete"])
        fields = {entry["field"] for entry in report["missing_or_invalid_evidence"]}
        self.assertIn("official_source_url", fields)
        self.assertIn("country_eligibility", fields)
        self.assertIn("task_rate_unit", fields)
        self.assertIn("acceptance_criteria", fields)
        self.assertIn("payout_details", fields)

    def test_non_dictionary_input_rejected(self):
        with self.assertRaises(TypeError):
            grader.grade_evidence([])


if __name__ == "__main__":
    unittest.main()
