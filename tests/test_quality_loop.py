import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "runtime" / "quality_loop.py"
SPEC = importlib.util.spec_from_file_location("aps_quality_loop", MODULE)
quality = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quality)

def good(domain):
    return {key: 100 for key in quality.RUBRICS[domain]["weights"]}

class QualityLoopTests(unittest.TestCase):
    def test_all_domain_rubrics_pass_with_verified_scores(self):
        for domain in quality.RUBRICS:
            with self.subTest(domain=domain):
                self.assertTrue(quality.evaluate_attempt({"domain": domain, "checks": good(domain)})["passed"])

    def test_missing_checks_fail_closed(self):
        result = quality.evaluate_attempt({"domain": "video", "checks": {}})
        self.assertFalse(result["passed"])
        self.assertEqual(result["score"], 0)
        self.assertTrue(result["hard_gate_failures"])

    def test_out_of_frame_video_text_is_hard_failure_with_fix(self):
        checks = good("video")
        checks["frame_bounds"] = 0
        result = quality.evaluate_attempt({"domain": "video", "checks": checks})
        self.assertIn("frame_bounds", result["hard_gate_failures"])
        tips = {x["check"]: x["action"] for x in result["remediation"]}
        self.assertIn("safe area", tips["frame_bounds"])

    def test_image_text_overflow_blocks_delivery(self):
        checks = good("image")
        checks["no_text_overflow"] = 10
        result = quality.evaluate_attempt({"domain": "image", "checks": checks})
        self.assertFalse(result["passed"])
        self.assertIn("no_text_overflow", result["hard_gate_failures"])

    def test_website_form_must_be_working_or_absent(self):
        checks = good("website")
        checks["forms_verified_or_absent"] = 0
        self.assertFalse(quality.evaluate_attempt({"domain": "website", "checks": checks})["passed"])

    def test_invalid_or_unknown_scores_are_rejected(self):
        for value in (-1, 101, True, "90"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                quality.evaluate_attempt({"domain": "video", "checks": {"frame_bounds": value}})
        with self.assertRaisesRegex(ValueError, "Unknown checks"):
            quality.evaluate_attempt({"domain": "video", "checks": {"invented": 100}})

    def test_retry_uses_failure_context_and_passes_on_second_attempt(self):
        contexts = []
        def generator(context):
            contexts.append(context)
            checks = good("video")
            if context["attempt"] == 1:
                checks.update({"frame_bounds": 20, "text_legibility": 30})
            return {"domain": "video", "checks": checks, "agent_id": "Drishti-Video",
                    "agent_version": "1.0.0", "model_id": "fixture", "model_version": "1.0.0"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.jsonl"
            out = quality.run_learning_loop("retry-case", "video", generator, history_path=path)
            rows = [json.loads(line) for line in path.read_text().splitlines()]
        self.assertEqual(out["status"], "passed")
        self.assertEqual(out["attempts_used"], 2)
        self.assertTrue(contexts[1]["previous_failures"])
        self.assertIn("frame_bounds", contexts[1]["previous_failures"][0]["failed_checks"])
        self.assertEqual(rows[0]["status"], "retry_required")

    def test_retry_limit_never_claims_success(self):
        out = quality.run_learning_loop("bad-case", "music",
            lambda context: {"domain": "music", "checks": {"export_playable": 0}}, max_attempts=2)
        self.assertEqual(out["status"], "failed_retry_limit")
        self.assertFalse(out["external_action_executed"])

    def test_retry_limit_is_capped(self):
        with self.assertRaises(ValueError):
            quality.run_learning_loop("x", "video", lambda c: {}, max_attempts=99)

    def test_model_comparison_requires_cases_and_never_promotes(self):
        rows = []
        for version, score in [("1.0.0", 90), ("1.1.0", 96)]:
            for i in range(5):
                rows.append({"domain":"image","model_id":"local-test","model_version":version,
                             "case_id":"gold-%d" % i,"score":score,"passed":True})
        rows.append({"domain":"image","model_id":"untested","model_version":"0.1.0",
                     "case_id":"only","score":100,"passed":True})
        result = quality.compare_model_candidates(rows)
        self.assertEqual(result["recommendations"]["image"]["model_version"], "1.1.0")
        self.assertFalse(result["auto_promotion"])
        candidate = next(x for x in result["by_domain"]["image"] if x["model_id"] == "untested")
        self.assertEqual(candidate["promotion_status"], "insufficient_evidence")

    def test_synthetic_demo_reproduces_fail_then_pass(self):
        out = quality._demo()
        self.assertEqual(out["status"], "passed")
        self.assertEqual(out["attempts_used"], 2)
        self.assertFalse(out["attempt_history"][0]["passed"])
        self.assertTrue(out["attempt_history"][1]["passed"])

if __name__ == "__main__":
    unittest.main()
