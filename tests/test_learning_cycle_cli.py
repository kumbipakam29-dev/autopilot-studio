"""Tests for the real Python learning-cycle JSON evidence CLI."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from agents.learning_cycle_cli import RECORD_TYPE, build_record

ROOT = Path(__file__).resolve().parents[1]


def review(task=80, evidence=90, safety=95, completeness=90, reproducibility=90):
    return {
        "scores": {
            "task_success": task,
            "evidence_and_factuality": evidence,
            "safety_and_permissions": safety,
            "format_and_completeness": completeness,
            "reproducibility": reproducibility,
        },
        "hard_fail_flags": [],
        "reviewer_id": "test-fixture",
    }


def payload():
    return {
        "task_id": "training-fixture-001",
        "agent_name": "Writer / Content Strategist",
        "error_category": "Clarity / completeness",
        "baseline_output": {"caption": "Short baseline"},
        "candidate_output": {"caption": "Clearer candidate"},
        "baseline_review": review(task=70),
        "candidate_review": review(task=90),
        "regression_results": {"content_fixture": True, "safety_fixture": True},
        "change_rationale": "Add a clear CTA and require evidence for claims.",
        "reviewer_approved": False,
        "evidence_notes": "Synthetic unit-test fixture; not a real business result.",
    }


class LearningCycleCliTests(unittest.TestCase):
    def test_build_record_runs_python_evaluator_and_does_not_claim_training(self):
        record = build_record(payload())
        self.assertEqual(record["record_type"], RECORD_TYPE)
        self.assertEqual(record["result"]["decision"], "awaiting_human_approval")
        self.assertGreater(record["result"]["candidate_review"]["weighted_score"],
                           record["result"]["baseline_review"]["weighted_score"])
        self.assertFalse(record["result"]["model_weights_changed"])
        self.assertFalse(record["result"]["auto_release"])
        self.assertTrue(record["limits"]["scores_are_human_or_reviewer_supplied"])

    def test_regression_failure_blocks_candidate(self):
        data = payload()
        data["regression_results"]["safety_fixture"] = False
        record = build_record(data)
        self.assertEqual(record["result"]["decision"], "reject_candidate_regression_failed")
        self.assertFalse(record["result"]["auto_release"])

    def test_hard_fail_overrides_improved_score(self):
        data = payload()
        data["candidate_review"]["hard_fail_flags"] = ["fabricated_source_or_result"]
        record = build_record(data)
        self.assertEqual(record["result"]["decision"], "reject_candidate_hard_fail")

    def test_cli_can_write_importable_json(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            output_path = Path(directory) / "evidence.json"
            input_path.write_text(json.dumps(payload()), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "agents.learning_cycle_cli",
                 "--input", str(input_path), "--output", str(output_path)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(result["record_type"], RECORD_TYPE)
            self.assertEqual(result["result"]["task_id"], "training-fixture-001")


if __name__ == "__main__":
    unittest.main()
