"""Scored agent candidate registry and version proposals.

Versions agent configurations/prompts/skills, not model weights. Never self-modifies
source code, fine-tunes a foundation model, deploys a candidate, or promotes a version.
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from agents.evaluation_loop import score_review

EVOLUTION_SCHEMA = "autopilot_agent_evolution_v1"
SEMVER_RE = re.compile(r"^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)$")

def _semver_parts(version: str) -> tuple[int, int, int]:
    if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
        raise ValueError("version must be semantic version MAJOR.MINOR.PATCH")
    return tuple(int(part) for part in version.split("."))

def bump_version(version: str, change_type: str) -> str:
    major, minor, patch = _semver_parts(version)
    if change_type == "major": return f"{major + 1}.0.0"
    if change_type == "minor": return f"{major}.{minor + 1}.0"
    if change_type == "patch": return f"{major}.{minor}.{patch + 1}"
    raise ValueError("change_type must be major, minor, or patch")

def evaluate_agent_candidate(*, agent_id: str, current_version: str, candidate_version: str,
    baseline_review: dict[str, Any], candidate_review: dict[str, Any],
    regression_results: dict[str, bool], change_type: str, human_approved: bool = False) -> dict[str, Any]:
    if not isinstance(agent_id, str) or not agent_id.strip(): raise ValueError("agent_id is required")
    _semver_parts(current_version); _semver_parts(candidate_version)
    expected = bump_version(current_version, change_type)
    if candidate_version != expected: raise ValueError(f"candidate_version must be the next {change_type} version: {expected}")
    if not isinstance(regression_results, dict) or not regression_results: raise ValueError("at least one named regression result is required")
    if any(not isinstance(k, str) or not k.strip() or not isinstance(v, bool) for k, v in regression_results.items()):
        raise ValueError("regression_results must map non-empty names to booleans")
    baseline = score_review(baseline_review); candidate = score_review(candidate_review)
    regression_passed = all(regression_results.values())
    safety_not_lower = candidate_review["scores"]["safety_and_permissions"] >= baseline_review["scores"]["safety_and_permissions"]
    hard_fail = baseline["status"] == "hard_fail" or candidate["status"] == "hard_fail"
    if hard_fail: status = "rejected_hard_fail"
    elif not regression_passed: status = "rejected_regression_failure"
    elif not safety_not_lower: status = "rejected_safety_score_drop"
    elif candidate["weighted_score"] <= baseline["weighted_score"]: status = "rejected_no_score_improvement"
    elif not human_approved: status = "candidate_passed_awaiting_human_approval"
    else: status = "approved_for_manual_promotion"
    return {
      "schema_version": EVOLUTION_SCHEMA, "agent_id": agent_id, "current_version": current_version,
      "candidate_version": candidate_version, "change_type": change_type,
      "baseline_score": baseline["weighted_score"], "candidate_score": candidate["weighted_score"],
      "score_delta": round(candidate["weighted_score"] - baseline["weighted_score"], 2),
      "regression_results": regression_results, "regression_passed": regression_passed,
      "safety_score_not_lower": safety_not_lower, "human_approved": human_approved,
      "status": status, "promoted": False, "model_weights_changed": False,
      "created_at": datetime.now(timezone.utc).isoformat(),
      "next_step": "human must review diff and explicitly promote; no registry files are written"
    }

def load_registry(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("agents"), list): raise ValueError("registry must contain an agents array")
    seen: set[str] = set()
    for item in data["agents"]:
        if not isinstance(item, dict) or not isinstance(item.get("agent_id"), str): raise ValueError("each agent entry must have agent_id")
        if item["agent_id"] in seen: raise ValueError(f"duplicate agent_id: {item['agent_id']}")
        seen.add(item["agent_id"]); _semver_parts(item.get("current_version", ""))
    return data

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default="agents/agent_registry.json")
    args = parser.parse_args(); registry = load_registry(args.registry)
    print(json.dumps({"status":"registry_valid","schema_version":EVOLUTION_SCHEMA,
      "agent_count":len(registry["agents"]),"agents":registry["agents"],
      "auto_promotion":False,"model_training":False}, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__": raise SystemExit(main())
