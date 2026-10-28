"""CLI for a real Python supervised-evaluation cycle.

Input scores and evidence are supplied by a human/review tool. This command runs the
repository's evaluation logic; it does not train model weights, fetch the web, or release
code. Use --output to save a review record that can be imported into the dashboard.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agents.learning_cycle import run_learning_cycle

RECORD_TYPE = "autopilot_learning_cycle_evidence_v1"


def build_record(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("input must be a JSON object")
    required_objects = (
        "baseline_output", "candidate_output", "baseline_review",
        "candidate_review", "regression_results",
    )
    for field in required_objects:
        if not isinstance(payload.get(field), dict):
            raise ValueError(f"{field} must be a JSON object")
    if not isinstance(payload.get("reviewer_approved", False), bool):
        raise ValueError("reviewer_approved must be a boolean")
    result = run_learning_cycle(
        task_id=payload.get("task_id", ""),
        baseline_output=payload["baseline_output"],
        candidate_output=payload["candidate_output"],
        baseline_review=payload["baseline_review"],
        candidate_review=payload["candidate_review"],
        regression_results=payload["regression_results"],
        change_rationale=payload.get("change_rationale", ""),
        reviewer_approved=payload.get("reviewer_approved", False),
    )
    return {
        "record_type": RECORD_TYPE,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "agent_name": str(payload.get("agent_name", "Unspecified specialist")),
        "error_category": str(payload.get("error_category", "Unspecified")),
        "evidence_notes": str(payload.get("evidence_notes", "")),
        "result": result,
        "limits": {
            "scores_are_human_or_reviewer_supplied": True,
            "model_weights_changed": False,
            "auto_release": False,
            "network_used": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="JSON input path; default is standard input")
    parser.add_argument("--output", help="optional JSON output path; default prints to stdout")
    args = parser.parse_args(argv)
    try:
        if args.input:
            payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        else:
            payload = json.load(sys.stdin)
        record = build_record(payload)
        rendered = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(rendered, encoding="utf-8")
            print(json.dumps({
                "status": "record_written",
                "output": str(out),
                "decision": record["result"]["decision"],
                "record_type": RECORD_TYPE,
            }, ensure_ascii=False))
        else:
            print(rendered, end="")
        return 0
    except (OSError, json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
