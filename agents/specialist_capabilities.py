"""Offline MVP capabilities for 15 AutoPilot Studio specialist roles.

These are deterministic, standard-library-only prototypes, not model-backed agents.
They use supplied inputs only: no network, filesystem writes, model calls, or external
side effects. All generated outreach/content remains a draft for human review.
"""
from __future__ import annotations

import re
from collections import defaultdict, deque
from typing import Any
from urllib.parse import urlparse

CAPABILITY_VERSION = "0.1.0"


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _words(value: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", value)


def public_source_verifier(data: dict[str, Any]) -> dict[str, Any]:
    """Check URL shape and supplied evidence fields without fetching the URL."""
    url = _text(data.get("url"))
    parsed = urlparse(url)
    checks = {
        "https_url": parsed.scheme == "https" and bool(parsed.netloc),
        "evidence_summary_present": bool(_text(data.get("evidence_summary"))),
        "source_owner_or_publisher_present": bool(_text(data.get("publisher"))),
        "checked_at_present": bool(_text(data.get("checked_at"))),
    }
    return {"capability_version": CAPABILITY_VERSION, "checks": checks,
            "status": "needs_human_review" if not all(checks.values()) else "shape_checks_passed_review_required",
            "fetched_or_verified_online": False, "approval_required": True}


def rate_evidence_extractor(data: dict[str, Any]) -> dict[str, Any]:
    """Extract visible amount/rate-like snippets from user-supplied text only."""
    text = _text(data.get("text"))
    pattern = re.compile(
        r"(?:₹|INR\s?|USD\s?|\$|£|€)\s?\d[\d,]*(?:\.\d+)?"
        r"(?:\s*(?:/|per\s+)(?:hour|hr|day|task|label|minute|word|project|month))?",
        re.IGNORECASE,
    )
    matches = [{"text": m.group(0), "start": m.start(), "end": m.end(),
                "context": text[max(0, m.start()-70):min(len(text), m.end()+70)]}
               for m in pattern.finditer(text)]
    return {"capability_version": CAPABILITY_VERSION, "matches": matches,
            "status": "found_rate_snippets" if matches else "rate_not_found_in_supplied_text",
            "verified_rate": False, "approval_required": True}


def scam_signal_triage(data: dict[str, Any]) -> dict[str, Any]:
    """Flag common warning phrases; this is not a fraud verdict."""
    text = " ".join(_text(data.get(k)) for k in ("title", "description", "terms")).lower()
    rules = {
        "upfront_payment": r"registration fee|pay upfront|upfront fee|deposit required|security deposit",
        "guaranteed_income": r"guaranteed income|guaranteed earning|earn guaranteed|100% guaranteed",
        "unrealistic_income": r"earn\s+\$?\d[\d,]*\s*(?:daily|per day|in one hour|in an hour)",
        "credential_request": r"send your password|share otp|one-time password|bank pin",
    }
    flags = [name for name, pattern in rules.items() if re.search(pattern, text)]
    return {"capability_version": CAPABILITY_VERSION, "signals": flags,
            "status": "high_attention_human_review" if flags else "no_rule_matched_not_a_safety_clearance",
            "fraud_determined": False, "approval_required": True}


def client_brief_structurer(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize a small-business content brief and expose missing information."""
    fields = ("business_name", "business_type", "location", "audience", "offer",
              "platforms", "brand_voice", "call_to_action", "constraints")
    brief = {key: data.get(key) for key in fields if data.get(key) not in (None, "", [], {})}
    missing = [key for key in ("business_type", "audience", "offer", "platforms") if key not in brief]
    return {"capability_version": CAPABILITY_VERSION, "brief": brief,
            "missing_fields": missing, "status": "needs_clarification" if missing else "brief_structured_review_required"}


def caption_variant_lab(data: dict[str, Any]) -> dict[str, Any]:
    """Create three transparent caption drafts from supplied, approved facts."""
    offer = _text(data.get("offer")) or "our service"
    audience = _text(data.get("audience")) or "your business"
    benefit = _text(data.get("benefit")) or "a simpler way to get started"
    cta = _text(data.get("call_to_action")) or "Message us to learn more"
    brand = _text(data.get("business_name"))
    prefix = f"{brand}: " if brand else ""
    captions = [
        f"{prefix}Looking for {benefit}? We help {audience} with {offer}. {cta}.",
        f"Small steps can make a difference. Explore {offer} and see whether it fits your needs. {cta}.",
        f"For {audience}: {offer}, focused on {benefit}. Questions? {cta}.",
    ]
    return {"capability_version": CAPABILITY_VERSION, "drafts": captions,
            "status": "drafts_for_review", "facts_independently_verified": False}


def task_dependency_mapper(data: dict[str, Any]) -> dict[str, Any]:
    """Validate a supplied task dependency graph and return a topological order."""
    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        return {"capability_version": CAPABILITY_VERSION, "status": "invalid_input", "errors": ["tasks must be a list"]}
    ids = [str(t.get("id", "")).strip() for t in tasks if isinstance(t, dict)]
    errors = []
    if len(ids) != len(tasks) or any(not x for x in ids):
        errors.append("every task must be an object with a non-empty id")
    if len(set(ids)) != len(ids):
        errors.append("task ids must be unique")
    known = set(ids)
    graph: dict[str, list[str]] = {x: [] for x in ids}
    indegree = {x: 0 for x in ids}
    for task in tasks:
        if not isinstance(task, dict) or not _text(task.get("id")):
            continue
        tid = str(task["id"]).strip()
        deps = task.get("depends_on", [])
        if not isinstance(deps, list):
            errors.append(f"{tid}: depends_on must be a list")
            continue
        for dep in deps:
            dep = str(dep)
            if dep not in known:
                errors.append(f"{tid}: unknown dependency {dep}")
            else:
                graph[dep].append(tid)
                indegree[tid] += 1
    queue = deque(sorted(x for x, n in indegree.items() if n == 0))
    order = []
    while queue:
        current = queue.popleft()
        order.append(current)
        for child in sorted(graph[current]):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    cycle = len(order) != len(known)
    if cycle:
        errors.append("dependency cycle detected")
    return {"capability_version": CAPABILITY_VERSION, "topological_order": order,
            "errors": errors, "status": "needs_human_review" if errors else "graph_valid"}


def approval_gatekeeper(data: dict[str, Any]) -> dict[str, Any]:
    """Conservative action classifier; never executes the requested action."""
    action = _text(data.get("action")).lower().replace("-", "_").replace(" ", "_")
    safe = {"format_text", "summarize_supplied_text", "validate_json", "run_offline_tests",
            "draft_content", "analyze_supplied_data"}
    forbidden_without_approval = {"send_message", "send_email", "send_dm", "publish_post",
        "submit_application", "submit_paid_task", "purchase", "spend_money", "deploy",
        "change_payout_settings", "change_security_settings", "delete_data", "create_account"}
    if action in safe:
        decision = "allowed_local_draft_or_analysis"
        approval = False
    elif action in forbidden_without_approval:
        decision = "blocked_pending_explicit_human_approval"
        approval = True
    else:
        decision = "unknown_action_blocked_pending_review"
        approval = True
    return {"capability_version": CAPABILITY_VERSION, "action": action, "decision": decision,
            "approval_required": approval, "action_executed": False}


def failure_replay_analyst(data: dict[str, Any]) -> dict[str, Any]:
    """Turn supplied CI failure text into a bounded replay checklist."""
    log = _text(data.get("log"))
    lines = [line.strip() for line in log.splitlines() if line.strip()]
    markers = ("traceback", "error", "failed", "exception", "assertionerror")
    relevant = [line for line in lines if any(marker in line.lower() for marker in markers)][-12:]
    command = _text(data.get("test_command")) or "python -m unittest discover -s tests"
    return {"capability_version": CAPABILITY_VERSION, "failure_markers": relevant,
            "proposed_replay_command": command, "replay_executed": False,
            "status": "failure_text_found" if relevant else "no_failure_marker_found",
            "next_step": "Reproduce in an isolated test run, then add a regression test before patching."}


def version_drift_auditor(data: dict[str, Any]) -> dict[str, Any]:
    """Compare expected and observed version maps without modifying either."""
    expected = data.get("expected", {})
    observed = data.get("observed", {})
    if not isinstance(expected, dict) or not isinstance(observed, dict):
        return {"capability_version": CAPABILITY_VERSION, "status": "invalid_input"}
    keys = sorted(set(expected) | set(observed))
    drift = [{"component": key, "expected": expected.get(key), "observed": observed.get(key)}
             for key in keys if expected.get(key) != observed.get(key)]
    return {"capability_version": CAPABILITY_VERSION, "drift": drift,
            "status": "drift_detected" if drift else "versions_match",
            "changes_applied": False}


def workflow_resume_planner(data: dict[str, Any]) -> dict[str, Any]:
    """Find pending tasks whose declared dependencies are completed."""
    tasks = data.get("tasks", [])
    if not isinstance(tasks, list):
        return {"capability_version": CAPABILITY_VERSION, "status": "invalid_input"}
    by_id = {str(t.get("id")): t for t in tasks if isinstance(t, dict) and t.get("id") is not None}
    completed = {tid for tid, t in by_id.items() if t.get("status") == "completed"}
    ready, blocked = [], []
    for tid, task in by_id.items():
        if task.get("status") == "completed":
            continue
        deps = task.get("depends_on", [])
        if not isinstance(deps, list):
            blocked.append({"id": tid, "reason": "invalid_dependencies"})
        elif all(str(dep) in completed for dep in deps):
            ready.append(tid)
        else:
            blocked.append({"id": tid, "reason": "dependencies_incomplete",
                            "waiting_for": [str(dep) for dep in deps if str(dep) not in completed]})
    return {"capability_version": CAPABILITY_VERSION, "ready": sorted(ready),
            "blocked": blocked, "status": "resume_plan_only", "tasks_started": False}


def local_business_niche_researcher(data: dict[str, Any]) -> dict[str, Any]:
    """Summarize supplied public business facts; never claims fresh web research."""
    facts = data.get("facts", [])
    if not isinstance(facts, list):
        facts = []
    cleaned = [str(x).strip() for x in facts if str(x).strip()]
    services = data.get("services", [])
    if not isinstance(services, list):
        services = []
    return {"capability_version": CAPABILITY_VERSION,
            "business_type": _text(data.get("business_type")) or "not supplied",
            "location": _text(data.get("location")) or "not supplied",
            "provided_facts": cleaned[:20], "provided_services": [str(x).strip() for x in services if str(x).strip()][:20],
            "content_angles_to_validate": ["customer FAQ", "process or behind-the-scenes", "service explainer"],
            "research_source": "user_supplied_input_only", "status": "hypotheses_for_human_validation"}


def content_calendar_architect(data: dict[str, Any]) -> dict[str, Any]:
    """Draft a seven-day content calendar from supplied business details."""
    business = _text(data.get("business_name")) or "the business"
    offer = _text(data.get("offer")) or "the main service"
    audience = _text(data.get("audience")) or "target customers"
    platforms = data.get("platforms", ["Instagram"])
    if not isinstance(platforms, list) or not platforms:
        platforms = ["Instagram"]
    themes = [
        ("Awareness", f"Introduce {business} and who it serves"),
        ("Problem", f"Explain a common {audience} problem related to {offer}"),
        ("Education", f"Share one practical tip about {offer}"),
        ("Process", f"Show the steps behind {offer}"),
        ("FAQ", f"Answer one frequently asked question about {offer}"),
        ("Trust", "Share a transparent process or clearly labelled illustrative example"),
        ("Conversion", f"Explain how interested customers can ask about {offer}"),
    ]
    calendar = [{"day": i + 1, "theme": theme, "concept": concept,
                 "platforms": platforms, "status": "draft_not_published"}
                for i, (theme, concept) in enumerate(themes)]
    return {"capability_version": CAPABILITY_VERSION, "business_name": business,
            "calendar": calendar, "status": "seven_day_draft"}


def reel_script_engineer(data: dict[str, Any]) -> dict[str, Any]:
    """Create a short vertical-video draft with timestamps between 14 and 20 seconds."""
    topic = _text(data.get("topic")) or _text(data.get("offer")) or "one useful tip"
    audience = _text(data.get("audience")) or "your audience"
    cta = _text(data.get("call_to_action")) or "Save this for later"
    script = [
        {"start_sec": 0, "end_sec": 3, "visual": "Clear hook text on screen", "voiceover": f"{audience}: struggling with {topic}?"},
        {"start_sec": 3, "end_sec": 8, "visual": "Show the problem or context", "voiceover": f"Start by focusing on one specific part of {topic}."},
        {"start_sec": 8, "end_sec": 14, "visual": "Show one practical step", "voiceover": "Keep it simple, useful, and relevant to your needs."},
        {"start_sec": 14, "end_sec": 17, "visual": "End card with CTA", "voiceover": cta},
    ]
    return {"capability_version": CAPABILITY_VERSION, "duration_sec": 17,
            "scenes": script, "status": "script_draft_not_published",
            "claims_verified": False}


def portfolio_spec_work_designer(data: dict[str, Any]) -> dict[str, Any]:
    """Produce a clearly labelled fictional portfolio brief, never imply real client work."""
    business_type = _text(data.get("business_type")) or "local cafe"
    concept = _text(data.get("concept")) or "seasonal offer"
    return {"capability_version": CAPABILITY_VERSION,
            "label": "FICTIONAL SPEC WORK — NOT A REAL CLIENT OR CAMPAIGN",
            "business_type": business_type, "concept": concept,
            "deliverables": ["three social post concepts", "two 14–20 second Reel script drafts",
                             "caption drafts", "seven-day content calendar"],
            "published": False, "real_client_claim": False, "status": "portfolio_concept_draft"}


def outreach_personalization_drafter(data: dict[str, Any]) -> dict[str, Any]:
    """Draft one respectful message using only explicitly supplied facts; never sends it."""
    name = _text(data.get("business_name")) or "there"
    fact = _text(data.get("specific_public_fact"))
    service = _text(data.get("service_offer")) or "social media content support"
    sender = _text(data.get("sender_name")) or "AutoPilot Digital Studio"
    if not fact:
        return {"capability_version": CAPABILITY_VERSION, "status": "needs_specific_fact",
                "draft": None, "sent": False,
                "note": "Supply a relevant, accurate public fact before personalizing; do not invent one."}
    draft = (f"Hi {name}, I noticed {fact}. I help small businesses with {service} and can share "
             f"a small, clearly labelled sample idea if useful. No pressure either way. "
             f"Best, {sender}")
    return {"capability_version": CAPABILITY_VERSION, "status": "draft_for_human_review",
            "draft": draft, "sent": False, "facts_independently_verified": False}


CAPABILITIES = {
    "APS-SM-01": public_source_verifier,
    "APS-SM-02": rate_evidence_extractor,
    "APS-SM-03": scam_signal_triage,
    "APS-SM-04": client_brief_structurer,
    "APS-SM-05": caption_variant_lab,
    "APS-LG-01": task_dependency_mapper,
    "APS-LG-02": approval_gatekeeper,
    "APS-LG-03": failure_replay_analyst,
    "APS-LG-04": version_drift_auditor,
    "APS-LG-05": workflow_resume_planner,
    "APS-CR-01": local_business_niche_researcher,
    "APS-CR-02": content_calendar_architect,
    "APS-CR-03": reel_script_engineer,
    "APS-CR-04": portfolio_spec_work_designer,
    "APS-CR-05": outreach_personalization_drafter,
}


def run_capability(agent_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Run one known offline capability; reject unknown IDs and malformed inputs."""
    if agent_id not in CAPABILITIES:
        raise KeyError(f"unknown specialist agent: {agent_id}")
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    return CAPABILITIES[agent_id](data)
