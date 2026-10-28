"""Deterministic, read-only evidence grader for opportunity candidates.

Pattern adapted from the tool-boundary and structured-output principles studied in
Hugging Face smolagents. This module does not import that framework, call a model,
browse the network, or take external actions. It grades only supplied evidence.
"""
from typing import Any

REQUIRED_FIELDS = {
    "official_source_url": "official source URL",
    "country_eligibility": "country eligibility evidence",
    "task_rate_unit": "task-specific rate and unit, or explicit 'not stated'",
    "acceptance_criteria": "task acceptance criteria",
    "payout_details": "payout details, or explicit 'not stated'",
}

def grade_evidence(candidate: dict[str, Any]) -> dict[str, Any]:
    """Return a conservative evidence report; missing data never gets inferred."""
    if not isinstance(candidate, dict):
        raise TypeError("candidate must be a dictionary")

    missing = []
    for field, description in REQUIRED_FIELDS.items():
        value = candidate.get(field)
        if not isinstance(value, str) or not value.strip():
            missing.append({"field": field, "requirement": description})
            continue
        normalized = value.strip().lower()
        if normalized in {"unknown", "unverified", "tbd", "n/a"}:
            missing.append({"field": field, "requirement": description})

    source = str(candidate.get("official_source_url", "")).strip().lower()
    if source and not source.startswith("https://"):
        missing.append({
            "field": "official_source_url",
            "requirement": "HTTPS official source URL",
        })

    return {
        "grader_version": "0.1.0",
        "candidate_id": str(candidate.get("candidate_id", "unspecified")),
        "status": "needs_human_review" if missing else "evidence_complete_review_required",
        "evidence_complete": not missing,
        "missing_or_invalid_evidence": missing,
        "approval_required": True,
        "external_actions_taken": 0,
        "payment_verified": False,
        "note": "Evidence completeness is not proof that a job is genuine or that payment will occur.",
    }
