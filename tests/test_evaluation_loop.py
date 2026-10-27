"""Offline tests for the human-reviewed agent evaluation rubric."""
import unittest

from agents.evaluation_loop import compare_candidate, score_review


def review(scores=None, flags=None, **extra):
    return {
        "scores": scores or {
            "task_success": 90,
            "evidence_and_factuality": 90,
            "safety_and_permissions": 100,
            "format_and_completeness": 80,
            "reproducibility": 90,
        },
        "hard_fail_flags": flags or [],
        **extra,
    }


class EvaluationLoopTests(unittest.TestCase):
    def test_weighted_score_passes_threshold(self):
        result = score_review(review())
        self.assertEqual(result["weighted_score"], 90.5)
        self.assertEqual(result["status"], "pass_for_review")
        self.assertTrue(result["approval_required"])

    def test_hard_fail_overrides_high_numeric_score(self):
        result = score_review(review(flags=["fabricated_source_or_result"]))
        self.assertEqual(result["weighted_score"], 90.5)
        self.assertEqual(result["status"], "hard_fail")

    def test_missing_or_invalid_scores_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            score_review({"scores": {"task_success": 90}})
        bad = review()
        bad["scores"]["safety_and_permissions"] = 101
        with self.assertRaisesRegex(ValueError, "invalid"):
            score_review(bad)

    def test_candidate_improvement_still_requires_human_review(self):
        result = compare_candidate(
            {"weighted_score": 80, "status": "needs_revision"},
            {"weighted_score": 90, "status": "pass_for_review"},
        )
        self.assertEqual(result["decision"], "propose_for_human_review")
        self.assertFalse(result["auto_release"])

    def test_candidate_hard_fail_rejected_even_with_higher_score(self):
        result = compare_candidate(
            {"weighted_score": 80, "status": "needs_revision"},
            {"weighted_score": 99, "status": "hard_fail", "hard_fail_flags": ["secret"]},
        )
        self.assertEqual(result["decision"], "reject_candidate")
        self.assertFalse(result["auto_release"])

    def test_safety_regression_blocks_candidate(self):
        result = compare_candidate(
            {"weighted_score": 80, "status": "needs_revision"},
            {"weighted_score": 95, "status": "pass_for_review", "safety_regression": True},
        )
        self.assertEqual(result["decision"], "reject_candidate")


if __name__ == "__main__":
    unittest.main()
