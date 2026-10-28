"""Safe local office orchestrator for AutoPilot Studio.

Runs implemented offline handlers as a coordinated job and records evidence. This is
not an LLM runtime, browser automation engine, or autonomous code-writing agent.
External actions remain blocked and require a separate reviewed implementation.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agents.client_acquisition_pipeline import build_client_acquisition_pack
from agents.specialist_capabilities import run_capability
from agents.specialist_runner import grade_opportunity, load_config, validate_catalog

VERSION = "0.1.0"
SUPPORTED_JOBS = {"office_audit", "client_acquisition_pack", "specialist_task", "opportunity_review"}
BLOCKED_ACTIONS = {"browse_web", "send_outreach", "publish_content", "modify_repository", "make_payment"}


def execute_job(job: dict[str, Any]) -> dict[str, Any]:
    """Execute one explicitly typed job; no dynamic code or shell execution."""
    if not isinstance(job, dict):
        raise TypeError("job must be a JSON object")
    job_type = job.get("job_type")
    payload = job.get("payload", {})
    if not isinstance(payload, dict):
        raise TypeError("payload must be a JSON object")
    if job_type in BLOCKED_ACTIONS:
        return {
            "status": "blocked",
            "job_type": job_type,
            "reason": "External or repository-changing action is not implemented in this offline runner.",
            "approval_required": True,
        }
    if job_type not in SUPPORTED_JOBS:
        raise ValueError(f"unsupported job_type: {job_type}")

    config = load_config()
    if job_type == "office_audit":
        result = validate_catalog({"expected_count": payload.get("expected_count", 15)}, config)
    elif job_type == "client_acquisition_pack":
        result = build_client_acquisition_pack(payload)
    elif job_type == "specialist_task":
        agent_id = payload.get("agent_id")
        task_input = payload.get("input", {})
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("payload.agent_id is required")
        if not isinstance(task_input, dict):
            raise TypeError("payload.input must be a JSON object")
        result = run_capability(agent_id, task_input)
    else:
        result = grade_opportunity(payload, config)

    return {
        "status": "completed_for_review",
        "job_type": job_type,
        "result": result,
        "external_side_effects": False,
        "model_inference_used": False,
        "approval_required_before_external_action": True,
    }


def build_run_report(jobs: list[dict[str, Any]]) -> dict[str, Any]:
    """Run a batch in order and continue after per-job failures."""
    if not isinstance(jobs, list):
        raise TypeError("jobs must be a JSON array")
    records = []
    for index, job in enumerate(jobs):
        try:
            record = execute_job(job)
        except (ValueError, TypeError, KeyError) as exc:
            record = {
                "status": "failed",
                "job_type": job.get("job_type") if isinstance(job, dict) else None,
                "error": str(exc),
            }
        records.append({"job_id": f"job-{index + 1:03d}", **record})
    statuses = [item["status"] for item in records]
    return {
        "schema_version": "autopilot_office_run_v1",
        "orchestrator_version": VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": len(records),
            "completed_for_review": statuses.count("completed_for_review"),
            "blocked": statuses.count("blocked"),
            "failed": statuses.count("failed"),
        },
        "records": records,
        "limitations": [
            "Offline deterministic handlers only; no LLM is called.",
            "Browser research, message sending, publishing, repository mutation and payments are not executed.",
            "Results are drafts/evidence checks, not proof of sales, eligibility or payment.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="JSON job or array of jobs; otherwise read stdin")
    parser.add_argument("--output", help="write report to this JSON path instead of stdout")
    args = parser.parse_args(argv)
    try:
        source = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
        payload = json.loads(source)
        jobs = payload if isinstance(payload, list) else [payload]
        report = build_run_report(jobs)
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(rendered, encoding="utf-8")
            print(json.dumps({"status": "report_written", "output": str(out), **report["summary"]}))
        else:
            print(rendered, end="")
        return 1 if report["summary"]["failed"] else 0
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
