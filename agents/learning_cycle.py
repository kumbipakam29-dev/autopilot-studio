"""Supervised learning-cycle orchestration; no self-modification or auto-release.

A learning cycle records a proposed change, evaluates baseline and candidate output,
checks deterministic regression results, and leaves final acceptance to a human.
"""
from __future__ import annotations

from typing import Any

from agents.evaluation_loop import compare_candidate, score_review


def run_learning_cycle(
    *,
    task_id: str,
    baseline_output: dict[str, Any],
    candidate_output: dict[str, Any],
    baseline_review: dict[str, Any],
    candidate_review: dict[str, Any],
    regression_results: dict[str, bool],
    change_rationale: str,
    reviewer_approved: bool = False,
) -> dict[str, Any]:
    """Produce a review record for one proposed specialist improvement."""
    if not task_id.strip():
        raise ValueError("task_id is required")
    if not change_rationale.strip():
        raise ValueError("change_rationale is required")
    if not isinstance(regression_results, dict) or not regression_results:
        raise ValueError("at least one named regression result is required")
    if any(not isinstance(name, str) or not name.strip() or not isinstance(passed, bool)
           for name, passed in regression_results.items()):
        raise ValueError("regression_results must map non-empty names to booleans")

    baseline_score = score_review(baseline_review)
    candidate_score = score_review(candidate_review)
    regression_passed = all(regression_results.values())
    comparison = compare_candidate(
        baseline_score,
        {
            **candidate_score,
            "safety_regression": (
                candidate_review.get("safety_regression") is True
                or candidate_review.get("scores", {}).get("safety_and_permissions", 0)
                < baseline_review.get("scores", {}).get("safety_and_permissions", 0)
            ),
        },
    )

    if baseline_score["status"] == "hard_fail":
        decision = "stop_and_review_baseline_hard_fail"
    elif candidate_score["status"] == "hard_fail":
        decision = "reject_candidate_hard_fail"
    elif not regression_passed:
        decision = "reject_candidate_regression_failed"
    elif comparison["decision"] == "reject_candidate":
        decision = "reject_candidate_safety_or_score"
    elif not reviewer_approved:
        decision = "awaiting_human_approval"
    else:
        decision = "human_approved_candidate_for_manual_release"

    return {
        "cycle_version": "0.1.0",
        "task_id": task_id,
        "baseline_output": baseline_output,
        "candidate_output": candidate_output,
        "baseline_review": baseline_score,
        "candidate_review": candidate_score,
        "regression_results": regression_results,
        "regression_passed": regression_passed,
        "change_rationale": change_rationale,
        "comparison": comparison,
        "decision": decision,
        "reviewer_approved": reviewer_approved,
        "auto_release": False,
        "model_weights_changed": False,
        "note": "This record does not alter prompts/code or release a candidate. Human-controlled implementation is a separate step.",
    }
