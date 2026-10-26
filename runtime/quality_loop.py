"""Evidence-based bounded quality retries for AutoPilot Studio; standard library only.

This is a QA/retry framework, not a media generator or model-weight trainer.
Checks must come from real tools or independent reviewers. Missing evidence fails closed.
"""
import argparse
import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PASS_SCORE = 85.0
HARD_GATE_SCORE = 90.0
MAX_ATTEMPTS = 3
ABSOLUTE_MAX_ATTEMPTS = 5
RUBRICS = {
    "video": {
        "weights": {"frame_bounds": 20, "text_legibility": 15, "story_and_pacing": 10, "audio_sync": 10, "duration_valid": 10, "export_playable": 15, "rights_cleared": 10, "human_review": 10},
        "hard": ["frame_bounds", "export_playable", "rights_cleared", "human_review"]},
    "music": {
        "weights": {"export_playable": 15, "no_clipping": 15, "loudness_consistent": 10, "arrangement_quality": 10, "mix_balance": 15, "rights_cleared": 15, "human_review": 20},
        "hard": ["export_playable", "no_clipping", "rights_cleared", "human_review"]},
    "image": {
        "weights": {"dimensions_valid": 10, "no_text_overflow": 20, "brief_match": 15, "composition_quality": 15, "text_legibility": 10, "rights_cleared": 10, "human_review": 20},
        "hard": ["dimensions_valid", "no_text_overflow", "rights_cleared", "human_review"]},
    "website": {
        "weights": {"responsive_layout": 15, "no_overflow": 15, "links_valid": 10, "forms_verified_or_absent": 15, "accessibility_basics": 10, "content_accuracy": 15, "browser_test": 10, "human_review": 10},
        "hard": ["no_overflow", "links_valid", "forms_verified_or_absent", "content_accuracy", "browser_test", "human_review"]}
}
FIXES = {
    "frame_bounds": "Re-compose all shots inside the safe area; inspect rendered frames at the target aspect ratio.",
    "text_legibility": "Shorten copy, increase contrast/type size, then inspect on a phone-sized display.",
    "story_and_pacing": "Rebuild the edit around one hook, a useful middle, and a clear ending.",
    "audio_sync": "Re-align cuts, voice and music; re-check the final exported file.",
    "duration_valid": "Trim or extend to the brief and verify export duration.",
    "export_playable": "Re-export with supported settings and decode the complete output.",
    "rights_cleared": "Use original/licensed material or attach evidence of permitted use.",
    "human_review": "Stop for independent inspection of the actual artifact; a model cannot self-approve.",
    "no_clipping": "Reduce peaks, export again, inspect meter data, and listen to the loudest section.",
    "loudness_consistent": "Measure integrated loudness/true peak and normalize for the intended platform.",
    "arrangement_quality": "Revise structure, transitions and repetition against the brief.",
    "mix_balance": "Rebalance vocals, lead, bass and accompaniment; check headphones and phone speakers.",
    "dimensions_valid": "Export the requested size/aspect ratio and verify actual pixel dimensions.",
    "no_text_overflow": "Reduce copy/font size or expand the container; inspect every edge at final resolution.",
    "brief_match": "Compare the actual artifact requirement-by-requirement; regenerate unmet parts.",
    "composition_quality": "Improve hierarchy, spacing, contrast, focal point and crop.",
    "responsive_layout": "Test mobile, tablet and desktop breakpoints and fix each separately.",
    "no_overflow": "Capture viewport screenshots and fix horizontal scroll, clipped text and out-of-bounds elements.",
    "links_valid": "Test every link/CTA; remove empty destinations and placeholders.",
    "forms_verified_or_absent": "Remove a nonworking form or submit a test entry end-to-end and save evidence.",
    "accessibility_basics": "Check headings, labels, alt text, keyboard/focus behavior and contrast.",
    "content_accuracy": "Verify claims, contact details and prices; label fictional spec work clearly.",
    "browser_test": "Open the built site in a real browser and attach test/screenshot evidence."
}

def now():
    return datetime.now(timezone.utc).isoformat()

def _score(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 100:
        raise ValueError("Check '%s' must be a number from 0 to 100" % name)
    return float(value)

def evaluate_attempt(attempt, pass_score=PASS_SCORE, hard_gate_score=HARD_GATE_SCORE):
    if not isinstance(attempt, dict):
        raise ValueError("Attempt must be an object")
    domain = attempt.get("domain")
    if domain not in RUBRICS:
        raise ValueError("Unsupported domain: %r" % domain)
    checks = attempt.get("checks")
    if not isinstance(checks, dict):
        raise ValueError("checks must be an object mapping check IDs to scores")
    rubric = RUBRICS[domain]
    weights = rubric["weights"]
    extra = sorted(set(checks) - set(weights))
    if extra:
        raise ValueError("Unknown checks for %s: %s" % (domain, ", ".join(extra)))
    values = {key: _score(checks.get(key, 0), key) for key in weights}
    score = round(sum(values[k] * weights[k] for k in weights) / sum(weights.values()), 2)
    hard_failures = [key for key in rubric["hard"] if values[key] < hard_gate_score]
    low = [key for key in weights if values[key] < pass_score]
    failed = sorted(set(hard_failures + low))
    return {
        "domain": domain, "task_id": str(attempt.get("task_id", "unspecified")),
        "attempt": attempt.get("attempt", 1), "agent_id": attempt.get("agent_id", "unassigned"),
        "agent_version": attempt.get("agent_version", "0.0.0"),
        "model_id": attempt.get("model_id", "unconfigured"),
        "model_version": attempt.get("model_version", "0.0.0"),
        "artifact_ref": attempt.get("artifact_ref"), "score": score,
        "passed": score >= pass_score and not hard_failures,
        "status": "quality_passed" if score >= pass_score and not hard_failures else "retry_required",
        "checks": values, "hard_gate_failures": hard_failures, "failed_checks": failed,
        "remediation": [{"check": k, "score": values[k], "action": FIXES[k]} for k in failed],
        "evaluated_at": now()
    }

def _append(path, record):
    if path is None:
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as out:
        out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

def run_learning_loop(task_id, domain, generator, max_attempts=MAX_ATTEMPTS, history_path=None):
    """Call generator(context), score each returned artifact report, and feed failure details back."""
    if domain not in RUBRICS:
        raise ValueError("Unsupported domain: %r" % domain)
    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or not 1 <= max_attempts <= ABSOLUTE_MAX_ATTEMPTS:
        raise ValueError("max_attempts must be from 1 to %d" % ABSOLUTE_MAX_ATTEMPTS)
    history = []
    context = {"task_id": task_id, "domain": domain, "previous_failures": []}
    for number in range(1, max_attempts + 1):
        candidate = generator(dict(context, attempt=number, max_attempts=max_attempts))
        if not isinstance(candidate, dict) or candidate.get("domain", domain) != domain:
            raise ValueError("Generator must return an attempt object for the requested domain")
        report = evaluate_attempt(dict(candidate, task_id=task_id, domain=domain, attempt=number))
        history.append(report)
        _append(history_path, report)
        if report["passed"]:
            break
        context = {"task_id": task_id, "domain": domain,
                   "previous_failures": [{"attempt": h["attempt"], "score": h["score"],
                       "failed_checks": h["failed_checks"], "remediation": h["remediation"]} for h in history],
                   "latest_remediation": report["remediation"]}
    last = history[-1]
    outcome = {"task_id": task_id, "domain": domain,
        "status": "passed" if last["passed"] else "failed_retry_limit",
        "attempts_used": len(history), "max_attempts": max_attempts,
        "final_score": last["score"], "final_result": last, "attempt_history": history,
        "external_action_executed": False,
        "note": "Quality pass is not publish/payment approval." if last["passed"] else
                "Retry limit reached. Escalate to a human; do not claim success or publish."}
    _append(history_path, {"event": "learning_loop_finished", "task_id": task_id,
        "domain": domain, "status": outcome["status"], "attempts_used": len(history),
        "final_score": last["score"], "timestamp": now()})
    return outcome

def compare_model_candidates(records, min_cases=5):
    """Compare model versions over distinct golden cases; recommend but never auto-promote."""
    if isinstance(min_cases, bool) or not isinstance(min_cases, int) or min_cases < 1:
        raise ValueError("min_cases must be positive")
    groups = defaultdict(dict)
    for item in records:
        domain, model_id, version, case_id = (item.get("domain"), item.get("model_id"),
                                                item.get("model_version"), item.get("case_id"))
        if domain not in RUBRICS or not all(isinstance(x, str) and x for x in (model_id, version, case_id)):
            raise ValueError("Each record needs domain, model_id, model_version and case_id")
        passed = item.get("passed")
        if not isinstance(passed, bool):
            raise ValueError("passed must be boolean")
        groups[(domain, model_id, version)][case_id] = {"score": _score(item.get("score"), "score"), "passed": passed}
    by_domain = defaultdict(list)
    for (domain, model_id, version), cases in groups.items():
        values = list(cases.values())
        by_domain[domain].append({"domain": domain, "model_id": model_id, "model_version": version,
            "case_count": len(values), "mean_score": round(statistics.mean(x["score"] for x in values), 2),
            "pass_rate": round(sum(x["passed"] for x in values) / len(values), 4),
            "eligible_for_review": len(values) >= min_cases,
            "promotion_status": "requires_human_approval" if len(values) >= min_cases else "insufficient_evidence"})
    recommendations = {}
    for domain, candidates in by_domain.items():
        eligible = [c for c in candidates if c["eligible_for_review"]]
        eligible.sort(key=lambda c: (c["pass_rate"], c["mean_score"]), reverse=True)
        recommendations[domain] = eligible[0] if eligible else None
    return {"min_cases": min_cases, "by_domain": dict(by_domain), "recommendations": recommendations,
            "auto_promotion": False}

def _demo():
    candidates = [
        {"artifact_ref": "synthetic://attempt-1", "agent_id": "Drishti-Video", "agent_version": "1.0.0",
         "model_id": "demo-only", "model_version": "0.0.0",
         "checks": {"frame_bounds": 20, "text_legibility": 30, "story_and_pacing": 80,
                    "audio_sync": 95, "duration_valid": 100, "export_playable": 100,
                    "rights_cleared": 100, "human_review": 40}},
        {"artifact_ref": "synthetic://attempt-2", "agent_id": "Drishti-Video", "agent_version": "1.0.0",
         "model_id": "demo-only", "model_version": "0.0.0",
         "checks": {"frame_bounds": 100, "text_legibility": 95, "story_and_pacing": 90,
                    "audio_sync": 95, "duration_valid": 100, "export_playable": 100,
                    "rights_cleared": 100, "human_review": 95}}
    ]
    def generator(context):
        candidate = candidates[min(context["attempt"] - 1, len(candidates) - 1)]
        candidate["received_feedback"] = context.get("latest_remediation", [])
        return candidate
    return run_learning_loop("synthetic-video-layout-demo", "video", generator)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Run synthetic fail-then-pass regression; no model/media generated")
    parser.add_argument("--history", help="Optional JSONL evaluation log")
    args = parser.parse_args()
    if not args.demo:
        parser.error("Use the Python API with a configured generator adapter, or --demo for synthetic regression")
    result = _demo()
    if args.history:
        _append(args.history, {"event": "demo_summary", "status": result["status"], "score": result["final_score"]})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "passed":
        raise SystemExit(1)
