"""Offline-first task runner for versioned specialist profiles.

This runner executes deterministic Python handlers only. It does not call LLMs,
access the network, send messages, publish content, or mutate its own code.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "agent_learning_loop_v1.json"
LOG_PATH = ROOT / "artifacts" / "learning_loop" / "task_runs.jsonl"
SUPPORTED_TASKS = {"validate_agent_catalog", "grade_opportunity_evidence"}


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    agents = config.get("agents")
    if not isinstance(agents, list) or len(agents) != 15:
        raise ValueError("expected exactly 15 specialist profiles")
    ids = [a.get("id") for a in agents]
    if len(ids) != len(set(ids)) or any(not x for x in ids):
        raise ValueError("agent IDs must be non-empty and unique")
    return config


def validate_catalog(payload: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    requested_count = payload.get("expected_count", 15)
    agents = config["agents"]
    errors = []
    if requested_count != len(agents):
        errors.append(f"expected_count={requested_count}, actual={len(agents)}")
    for agent in agents:
        for field in ("id", "name", "specialized_task", "workflow", "expected_output"):
            if not isinstance(agent.get(field), str) or not agent[field].strip():
                errors.append(f"{agent.get('id', 'unknown')}: missing {field}")
        if agent.get("tool_policy") != "deny-by-default":
            errors.append(f"{agent.get('id', 'unknown')}: tool policy is not deny-by-default")
        if agent.get("approval_required") is not True:
            errors.append(f"{agent.get('id', 'unknown')}: approval gate missing")
    return {
        "status": "passed" if not errors else "failed",
        "checked_agents": len(agents),
        "errors": errors,
        "note": "Structural checks only; does not prove agents are running or outputs are correct.",
    }


def grade_opportunity(payload: dict[str, Any], _config: dict[str, Any]) -> dict[str, Any]:
    required = (
        "official_source_url", "country_eligibility", "task_rate_unit",
        "acceptance_criteria", "payout_details",
    )
    missing = []
    for field in required:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip() or value.strip().lower() in {
            "unknown", "unverified", "tbd", "n/a"
        }:
            missing.append(field)
    url = payload.get("official_source_url", "")
    if isinstance(url, str) and url.strip() and not url.strip().lower().startswith("https://"):
        missing.append("official_source_url must use HTTPS")
    return {
        "status": "needs_human_review" if missing else "ready_for_human_review",
        "missing_evidence": missing,
        "note": "This checks supplied fields only; it does not verify the opportunity or guarantee payment.",
    }


HANDLERS: dict[str, Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]] = {
    "validate_agent_catalog": validate_catalog,
    "grade_opportunity_evidence": grade_opportunity,
}


def run_task(task_type: str, payload: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    if task_type not in SUPPORTED_TASKS:
        raise ValueError(f"unsupported task type: {task_type}")
    if not isinstance(payload, dict):
        raise TypeError("payload must be a JSON object")
    result = HANDLERS[task_type](payload, config)
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "task_type": task_type,
        "agent_version": "0.1.0",
        "prompt_version": "0.1.0",
        "model_version": "unassigned",
        "source_commit": "record-at-release-time",
        "input": payload,
        "result": result,
        "learning_status": "evaluation_record_only",
        "auto_learned": False,
    }


def append_log(record: dict[str, Any], path: Path = LOG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", choices=sorted(SUPPORTED_TASKS), required=True)
    parser.add_argument("--input", help="JSON object string; if omitted, read JSON from stdin")
    parser.add_argument("--log", action="store_true", help="append result to local JSONL log")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.input) if args.input else json.load(sys.stdin)
        config = load_config()
        record = run_task(args.task, payload, config)
        if args.log:
            append_log(record)
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0 if record["result"]["status"] in {"passed", "ready_for_human_review"} else 1
    except (ValueError, TypeError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
