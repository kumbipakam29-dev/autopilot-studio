import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "runtime" / "opportunity_tracker.py"
SPEC = importlib.util.spec_from_file_location("aps_opportunity_tracker", MODULE)
tracker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tracker)


class OpportunityTrackerTests(unittest.TestCase):
    def test_relevant_verified_opportunity_scores_and_has_approval_gate(self):
        score, flags = tracker.score({
            "title": "Social media captions for local cafe",
            "description": "Write Instagram content",
            "url": "https://example.org/opportunity",
            "source": "Example source",
            "eligibility_checked": True,
            "payment_text": "Rate listed",
            "payment_verified": True,
        })
        self.assertGreaterEqual(score, 8)
        self.assertEqual(flags, [])

    def test_flags_unverified_and_suspicious_opportunity(self):
        score, flags = tracker.score({
            "title": "Guaranteed income - pay to apply",
            "description": "Registration fee required",
            "url": "http://example.org",
        })
        self.assertGreaterEqual(len(flags), 4)
        self.assertIn("missing_or_non_https_url", flags)
        self.assertIn("source_missing", flags)
        self.assertIn("eligibility_not_checked", flags)
        self.assertIn("possible_upfront_fee", flags)
        self.assertIn("unrealistic_income_claim", flags)
        self.assertLessEqual(score, 1)

    def test_cli_writes_csv_and_never_removes_approval_gate(self):
        sample = [{
            "opportunity_id": "sample-1",
            "source": "Example source",
            "title": "Content writing task",
            "url": "https://example.org/task",
            "payment_text": "Rate displayed, not independently confirmed",
            "eligibility_checked": True,
            "payment_verified": False,
        }]
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.json"
            output_path = Path(tmp) / "nested" / "queue.csv"
            input_path.write_text(json.dumps(sample), encoding="utf-8")
            import subprocess, sys
            result = subprocess.run(
                [sys.executable, str(MODULE), "--input", str(input_path), "--output", str(output_path)],
                check=True, capture_output=True, text=True,
            )
            summary = json.loads(result.stdout)
            self.assertEqual(summary["input_count"], 1)
            self.assertEqual(summary["external_actions_taken"], 0)
            with output_path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["approval_required"], "true")
            self.assertEqual(rows[0]["status"], "awaiting_user_approval")

    def test_non_array_input_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.json"
            input_path.write_text(json.dumps({"title": "not an array"}), encoding="utf-8")
            import subprocess, sys
            result = subprocess.run(
                [sys.executable, str(MODULE), "--input", str(input_path), "--output", str(Path(tmp) / "out.csv")],
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Input must be a JSON array", result.stderr)


if __name__ == "__main__":
    unittest.main()
