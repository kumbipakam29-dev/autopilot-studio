"""Two deterministic hard-task simulations with professional delivery gates.

Virtual RAM is logical accounting, not operating-system memory allocation.
No live LLM or external action is performed by this module.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from agents.learning_cycle import run_learning_cycle

SCHEMA_VERSION = "autopilot_hard_task_report_v1"
LAB_VERSION = "0.1.0"
VIRTUAL_RAM_BUDGET_MB = 512
MAX_PARALLEL_JOBS = 2
COMPUTE_TASKS: list[dict[str, Any]] = [
    {"task_id": "compile-index", "memory_mb": 160, "duration_ticks": 2, "priority": 9, "checkpointable": True},
    {"task_id": "unit-test-suite", "memory_mb": 220, "duration_ticks": 3, "priority": 8, "checkpointable": True},
    {"task_id": "static-analysis", "memory_mb": 100, "duration_ticks": 2, "priority": 6, "checkpointable": True},
    {"task_id": "evidence-report", "memory_mb": 128, "duration_ticks": 1, "priority": 5, "checkpointable": True},
    {"task_id": "small-model-eval", "memory_mb": 300, "duration_ticks": 2, "priority": 4, "checkpointable": True},
    {"task_id": "oversized-model-probe", "memory_mb": 700, "duration_ticks": 1, "priority": 10, "checkpointable": False},
    {"task_id": "injected-transient-failure", "memory_mb": 180, "duration_ticks": 2, "priority": 7, "checkpointable": True, "simulate_fail_once": True},
]
CREATIVE_BRIEF: dict[str, Any] = {
    "business_name": "Demo Corner Cafe", "business_type": "cafe", "location": "Ahmedabad",
    "audience": "people looking for a relaxed coffee break", "offer": "coffee and snack combo",
    "platforms": ["Instagram", "Facebook"], "brand_voice": "warm, simple, inviting",
    "call_to_action": "Ask us about today's combo", "approved_facts": ["coffee and snack combo"],
    "prohibited_claims": ["best in the city", "guaranteed sales", "award-winning"], "simulation_only": True,
}

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _positive_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value

def simulate_virtual_ram_schedule(tasks: list[dict[str, Any]], *, budget_mb: int = VIRTUAL_RAM_BUDGET_MB,
    max_parallel: int = MAX_PARALLEL_JOBS) -> dict[str, Any]:
    """Schedule task fixtures under logical memory and concurrency budgets; retry transient faults once."""
    _positive_int(budget_mb, "budget_mb")
    _positive_int(max_parallel, "max_parallel")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks must be a non-empty list")
    pending, outcomes, seen = [], [], set()
    for ordinal, raw in enumerate(tasks):
        if not isinstance(raw, dict):
            raise TypeError("each task must be an object")
        task_id = raw.get("task_id")
        if not isinstance(task_id, str) or not task_id.strip() or task_id in seen:
            raise ValueError("each task must have a unique non-empty task_id")
        seen.add(task_id)
        memory = _positive_int(raw.get("memory_mb"), f"{task_id}.memory_mb")
        duration = _positive_int(raw.get("duration_ticks"), f"{task_id}.duration_ticks")
        priority = raw.get("priority", 0)
        if not isinstance(priority, int) or isinstance(priority, bool):
            raise ValueError(f"{task_id}.priority must be an integer")
        fail_once, checkpointable = raw.get("simulate_fail_once", False), raw.get("checkpointable", False)
        if not isinstance(fail_once, bool) or not isinstance(checkpointable, bool):
            raise ValueError(f"{task_id} simulation flags must be booleans")
        item = {"task_id": task_id, "memory_mb": memory, "duration_ticks": duration,
                "priority": priority, "checkpointable": checkpointable, "injected_failure_pending": fail_once,
                "attempts": 0, "ordinal": ordinal}
        if memory > budget_mb:
            outcomes.append({"task_id": task_id, "status": "blocked_memory_limit",
                "memory_mb_requested": memory, "budget_mb": budget_mb, "attempts": 0,
                "reason": "request exceeds logical virtual-RAM budget"})
        else:
            pending.append(item)
    pending.sort(key=lambda x: (-x["priority"], x["ordinal"]))
    running, finished, events = [], {}, []
    tick, peak_mb = 0, 0
    while pending or running:
        launched = True
        while pending and len(running) < max_parallel and launched:
            launched = False
            used = sum(x["memory_mb"] for x in running)
            for index, item in enumerate(pending):
                if used + item["memory_mb"] <= budget_mb:
                    item = pending.pop(index)
                    item["attempts"] += 1
                    item["remaining_ticks"] = item["duration_ticks"]
                    running.append(item)
                    used += item["memory_mb"]
                    peak_mb = max(peak_mb, used)
                    events.append({"tick": tick, "task_id": item["task_id"], "event": "attempt_started",
                        "attempt": item["attempts"], "used_virtual_ram_mb": used})
                    launched = True
                    break
        if not running:
            if pending:
                raise RuntimeError("scheduler deadlocked although each pending task fits budget")
            break
        tick += 1
        for item in running:
            item["remaining_ticks"] -= 1
        for item in [x for x in running if x["remaining_ticks"] <= 0]:
            running.remove(item)
            task_id = item["task_id"]
            if item["injected_failure_pending"]:
                item["injected_failure_pending"] = False
                events.append({"tick": tick, "task_id": task_id, "event": "simulated_transient_failure",
                    "attempt": item["attempts"], "recovery": "restore_checkpoint" if item["checkpointable"] else "restart"})
                pending.append(item)
                pending.sort(key=lambda x: (-x["priority"], x["ordinal"]))
            else:
                finished[task_id] = {"task_id": task_id, "status": "completed", "attempts": item["attempts"],
                    "duration_ticks": item["duration_ticks"], "memory_mb_requested": item["memory_mb"],
                    "checkpointable": item["checkpointable"]}
                events.append({"tick": tick, "task_id": task_id, "event": "completed", "attempt": item["attempts"]})
    outcomes.extend(finished.values())
    outcomes.sort(key=lambda x: x["task_id"])
    retry = next((x for x in outcomes if x["task_id"] == "injected-transient-failure"), None)
    return {
        "simulation": "logical_virtual_ram_scheduler", "execution_mode": "deterministic_simulation",
        "budget_mb": budget_mb, "max_parallel": max_parallel, "peak_virtual_ram_mb": peak_mb,
        "never_oversubscribed": peak_mb <= budget_mb, "elapsed_ticks": tick,
        "completed_task_ids": sorted(x["task_id"] for x in outcomes if x["status"] == "completed"),
        "blocked_task_ids": sorted(x["task_id"] for x in outcomes if x["status"] == "blocked_memory_limit"),
        "transient_failure_recovered": bool(retry and retry["status"] == "completed" and retry["attempts"] == 2),
        "outcomes": outcomes, "attempt_events": events,
        "real_os_ram_allocated": False, "external_processes_launched": False,
    }

def build_content_pack(brief: dict[str, Any]) -> dict[str, Any]:
    """Create draft-only text assets from supplied facts; no LLM or publisher is called."""
    required = ("business_name", "business_type", "audience", "offer", "platforms", "call_to_action")
    missing = [key for key in required if not brief.get(key)]
    if missing:
        raise ValueError("missing brief fields: " + ", ".join(missing))
    name, offer = str(brief["business_name"]).strip(), str(brief["offer"]).strip()
    audience, cta = str(brief["audience"]).strip(), str(brief["call_to_action"]).strip()
    approved = [str(x).strip() for x in brief.get("approved_facts", [])]
    if offer not in approved:
        raise ValueError("offer must appear in approved_facts to prevent unsupported claims")
    prohibited = [str(x).lower() for x in brief.get("prohibited_claims", [])]
    reel = {"duration_seconds": 16, "scenes": [
        {"start": 0, "end": 3, "visual": "A cup is placed on the table", "voiceover": "Need a little pause in your day?"},
        {"start": 3, "end": 8, "visual": "Coffee and snack arranged together", "voiceover": f"Take a moment with our {offer}."},
        {"start": 8, "end": 13, "visual": "A relaxed table setting", "voiceover": f"A simple stop for {audience}."},
        {"start": 13, "end": 16, "visual": "Final frame with name and call to action", "voiceover": cta + "."}],
        "production_note": "Draft only; confirm the offer and film the real product before publishing."}
    captions = [
        f"{name}: Make room for a small coffee break. Ask us about our {offer}. {cta}.",
        f"For {audience}: a relaxed stop and our {offer}. {cta}.",
        f"Coffee, a snack, and a moment to slow down. Ask {name} about the {offer}. {cta}.",
    ]
    poster = {"headline": "Your next coffee break", "subheadline": offer.title(), "call_to_action": cta,
        "visual_direction": "Product-first tabletop photo, uncluttered layout, strong contrast and generous margins.",
        "required_checks": ["confirm offer is current", "review spelling", "check mobile legibility"]}
    calendar = [
        {"day": 1, "format": "Reel", "topic": "A 16-second coffee-break moment", "asset": "reel_script"},
        {"day": 2, "format": "Story", "topic": "Poll: when do you take a coffee break?", "asset": "story_prompt"},
        {"day": 3, "format": "Single image", "topic": "Feature the combo with a real product photo", "asset": "poster_brief"},
        {"day": 4, "format": "Carousel", "topic": "Three moments for a short cafe break", "asset": "carousel_copy"},
        {"day": 5, "format": "Story", "topic": "Question sticker about snack preferences", "asset": "story_prompt"},
        {"day": 6, "format": "Reel", "topic": "Behind-the-scenes preparation", "asset": "reel_outline"},
        {"day": 7, "format": "Single image", "topic": "Friendly weekend reminder to ask about the combo", "asset": "caption"}]
    combined = " ".join([json.dumps(reel), *captions, json.dumps(poster), json.dumps(calendar)]).lower()
    hits = sorted({phrase for phrase in prohibited if phrase and phrase in combined})
    checks = {
        "offer_is_approved": offer in approved,
        "reel_is_16_seconds": reel["duration_seconds"] == 16,
        "scene_timing_is_contiguous": reel["scenes"][0]["start"] == 0 and reel["scenes"][-1]["end"] == 16 and all(
            reel["scenes"][i]["end"] == reel["scenes"][i + 1]["start"] for i in range(len(reel["scenes"]) - 1)),
        "three_caption_drafts": len(captions) == 3,
        "poster_has_required_fields": all(poster.get(k) for k in ("headline", "subheadline", "call_to_action", "visual_direction")),
        "seven_calendar_days": [x["day"] for x in calendar] == list(range(1, 8)),
        "no_prohibited_claims": not hits,
        "platforms_present": isinstance(brief.get("platforms"), list) and bool(brief["platforms"]),
    }
    return {"business_name": name, "reel_script": reel, "caption_drafts": captions, "poster_brief": poster,
        "seven_day_calendar": calendar, "checks": checks, "prohibited_claim_hits": hits,
        "draft_only": True, "published": False, "external_actions_performed": False, "model_inference_used": False}

def _review(scores: dict[str, int], reviewer_id: str) -> dict[str, Any]:
    return {"scores": scores, "hard_fail_flags": [], "pass_threshold": 70, "reviewer_id": reviewer_id}

def run_hard_task_suite() -> dict[str, Any]:
    compute_a, compute_b = simulate_virtual_ram_schedule(COMPUTE_TASKS), simulate_virtual_ram_schedule(COMPUTE_TASKS)
    compute_reproducible = compute_a == compute_b
    content_a, content_b = build_content_pack(CREATIVE_BRIEF), build_content_pack(CREATIVE_BRIEF)
    creative_reproducible = content_a == content_b
    cc = content_a["checks"]
    creative_score = round(100 * sum(v is True for v in cc.values()) / len(cc))
    cm = {
        "memory_budget_invariant": compute_a["never_oversubscribed"],
        "oversized_job_rejected": "oversized-model-probe" in compute_a["blocked_task_ids"],
        "transient_failure_recovered": compute_a["transient_failure_recovered"],
        "at_least_five_jobs_completed": len(compute_a["completed_task_ids"]) >= 5,
        "repeat_run_identical": compute_reproducible,
    }
    compute_score = round(100 * sum(v is True for v in cm.values()) / len(cm))
    regressions = {
        "compute_memory_budget": cm["memory_budget_invariant"],
        "oversized_task_blocked": cm["oversized_job_rejected"],
        "retry_recovery": cm["transient_failure_recovered"],
        "creative_offer_grounded": cc["offer_is_approved"],
        "creative_claims_filter": cc["no_prohibited_claims"],
        "reel_timing": cc["reel_is_16_seconds"] and cc["scene_timing_is_contiguous"],
        "calendar_completeness": cc["seven_calendar_days"],
        "repeatability": compute_reproducible and creative_reproducible,
        "customer_delivery_blocked": content_a["draft_only"] and not content_a["published"] and not content_a["external_actions_performed"],
    }
    # Synthetic baseline fixture only; this is not a measured previous-model result.
    baseline = _review({"task_success":35,"evidence_and_factuality":35,"safety_and_permissions":60,
        "format_and_completeness":30,"reproducibility":30}, "synthetic-baseline-fixture")
    candidate = _review({
        "task_success": min(100, (compute_score + creative_score) // 2),
        "evidence_and_factuality": 100 if cc["offer_is_approved"] and cc["no_prohibited_claims"] else 40,
        "safety_and_permissions": 100 if cm["memory_budget_invariant"] and content_a["draft_only"] and not content_a["published"] else 0,
        "format_and_completeness": creative_score,
        "reproducibility": 100 if compute_reproducible and creative_reproducible else 0,
    }, "deterministic-assertion-suite")
    learning = run_learning_cycle(task_id="hard-task-suite-v1",
        baseline_output={"label":"synthetic_baseline_fixture","track_a":{"memory_guard":False,"retry":False},
            "track_b":{"claims_gate":False,"complete_calendar":False}},
        candidate_output={"track_a":{"score":compute_score,"checks":cm,"result":compute_a},
            "track_b":{"score":creative_score,"checks":cc,"result":content_a}},
        baseline_review=baseline, candidate_review=candidate, regression_results=regressions,
        change_rationale="Compare deterministic resource scheduling/recovery and fact-constrained creative drafts against an explicitly synthetic baseline.",
        reviewer_approved=False)
    compute_gate, creative_gate = all(cm.values()), all(cc.values()) and creative_reproducible
    overall = compute_gate and creative_gate and all(regressions.values())
    fixture = {"lab_version":LAB_VERSION,"compute_tasks":COMPUTE_TASKS,"creative_brief":CREATIVE_BRIEF,
        "budget_mb":VIRTUAL_RAM_BUDGET_MB,"max_parallel":MAX_PARALLEL_JOBS}
    digest = hashlib.sha256(json.dumps(fixture, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return {
        "schema_version":SCHEMA_VERSION,"lab_version":LAB_VERSION,
        "run_id":digest[:16]+"-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "created_at":_now(),"fixture_sha256":digest,
        "tracks":{
            "A_compute_virtual_ram":{"status":"PASS_SIMULATION" if compute_gate else "REJECTED","score":compute_score,
                "checks":cm,"result":compute_a,"same_fixture_reproducible":compute_reproducible},
            "B_customer_creative_workflow":{"status":"PASS_SIMULATION" if creative_gate else "REJECTED","score":creative_score,
                "checks":cc,"result":content_a,"same_fixture_reproducible":creative_reproducible}},
        "learning_cycle":learning,
        "quality_gate":{"status":"PASS_SIMULATION_ONLY" if overall else "REJECTED","all_track_checks_passed":overall,
            "customer_delivery_allowed":False,
            "reason":"Offline fixtures are not client-approved output. Live model-backed evaluation and human review are required before customer delivery."},
        "execution_truth":{"live_llm_called":False,"real_os_ram_allocated":False,"real_code_build_run":False,
            "internet_browsing_performed":False,"content_published":False,"customer_contacted":False,"payment_processed":False},
        "alerts":[{"severity":"info" if overall else "high","event":"simulation_gate_result",
            "message":"Both tracks passed deterministic simulation checks." if overall else "Checks failed; candidate must stay quarantined.",
            "requires_attention":not overall}],
        "next_steps":["Run CI tests","Attach CI artifact evidence","Replace synthetic baseline with reviewed real samples",
            "Connect local LLM only after opt-in","Human approval before customer delivery"],
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="artifacts/hard-task-learning-report.json")
    args = parser.parse_args()
    try:
        report = run_hard_task_suite()
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status":report["quality_gate"]["status"],"run_id":report["run_id"],
            "report_path":str(path),"compute_score":report["tracks"]["A_compute_virtual_ram"]["score"],
            "creative_score":report["tracks"]["B_customer_creative_workflow"]["score"],
            "customer_delivery_allowed":False,"alert_count":len(report["alerts"])}, ensure_ascii=False))
        return 0 if report["quality_gate"]["all_track_checks_passed"] else 1
    except (OSError, TypeError, ValueError, RuntimeError) as exc:
        print(json.dumps({"status":"FAILED","error_type":type(exc).__name__,"error":str(exc)}, ensure_ascii=False))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
