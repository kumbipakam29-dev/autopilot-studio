"""Integration tests for a single supervised learning cycle."""
import unittest

from agents.learning_cycle import run_learning_cycle


def rubric(task=90, evidence=90, safety=95, format_score=90, reproducibility=90):
    return {
        "scores": {
            "task_success": task,
            "evidence_and_factuality": evidence,
            "safety_and_permissions": safety,
            "format_and_completeness": format_score,
            "reproducibility": reproducibility,
        },
        "hard_fail_flags": [],
    }


class LearningCycleTests(unittest.TestCase):
    def test_improved_candidate_waits_for_human_approval(self):
        result = run_learning_cycle(
            task_id="fixture-001",
            baseline_output={"draft": "old"},
            candidate_output={"draft": "improved"},
            baseline_review=rubric(task=80),
            candidate_review=rubric(task=95),
            regression_results={"offline_fixture_001": True, "safety_fixture": True},
            change_rationale="Added a source-check reminder after reviewer feedback.",
        )
        self.assertEqual(result["decision"], "awaiting_human_approval")
        self.assertTrue(result["regression_passed"])
        self.assertFalse(result["auto_release"])
        self.assertFalse(result["model_weights_changed"])

    def test_failed_regression_rejects_candidate_even_with_approval(self):
        result = run_learning_cycle(
            task_id="fixture-002",
            baseline_output={"draft": "old"},
            candidate_output={"draft": "new"},
            baseline_review=rubric(task=80),
            candidate_review=rubric(task=99),
            regression_results={"offline_fixture_001": True, "safety_fixture": False},
            change_rationale="Test a proposed formatting improvement.",
            reviewer_approved=True,
        )
        self.assertEqual(result["decision"], "reject_candidate_regression_failed")
        self.assertFalse(result["auto_release"])

    def test_safety_regression_blocks_candidate(self):
        result = run_learning_cycle(
            task_id="fixture-003",
            baseline_output={"draft": "old"},
            candidate_output={"draft": "new"},
            baseline_review=rubric(safety=100),
            candidate_review=rubric(safety=80, task=100),
            regression_results={"fixture": True},
            change_rationale="Try a new response template.",
            reviewer_approved=True,
        )
        self.assertEqual(result["decision"], "reject_candidate_safety_or_score")

    def test_hard_fail_never_passes(self):
        result = run_learning_cycle(
            task_id="fixture-004",
            baseline_output={},
            candidate_output={},
            baseline_review=rubric(),
            candidate_review={**rubric(task=100), "hard_fail_flags": ["fabricated_source_or_result"]},
            regression_results={"fixture": True},
            change_rationale="No fabricated sources.",
            reviewer_approved=True,
        )
        self.assertEqual(result["decision"], "reject_candidate_hard_fail")

    def test_missing_task_or_rationale_is_rejected(self):
        args = dict(
            task_id="",
            baseline_output={},
            candidate_output={},
            baseline_review=rubric(),
            candidate_review=rubric(task=95),
            regression_results={"fixture": True},
            change_rationale="A change",
        )
        with self.assertRaisesRegex(ValueError, "task_id"):
            run_learning_cycle(**args)
        args["task_id"] = "fixture-005"
        args["change_rationale"] = " "
        with self.assertRaisesRegex(ValueError, "change_rationale"):
            run_learning_cycle(**args)


if __name__ == "__main__":
    unittest.main()
