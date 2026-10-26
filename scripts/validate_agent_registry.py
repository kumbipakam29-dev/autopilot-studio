#!/usr/bin/env python3
"""Generate and validate the AutoPilot Studio 500-agent registry.

This is a catalog generator, not a process launcher. Registry entries marked
planned must not be reported as running. No external APIs or paid models used.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "agents" / "registry.json"

def load():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))

def validate(data):
    agents = data.get("agents", [])
    ids = [a.get("id") for a in agents]
    errors = []
    if len(agents) != 500:
        errors.append(f"expected 500 records, found {len(agents)}")
    if len(set(ids)) != len(ids):
        errors.append("agent IDs are not unique")
    required = {"id", "department", "role", "niche", "agent_version",
                "model_version", "registry_status", "execution_status",
                "revenue_model", "approval_required", "safety_profile"}
    for index, agent in enumerate(agents):
        missing = required - agent.keys()
        if missing:
            errors.append(f"record {index} missing {sorted(missing)}")
        if agent.get("registry_status") != "registered":
            errors.append(f"{agent.get('id')}: unexpected registry status")
        if agent.get("execution_status") not in {"planned", "ready", "running", "blocked", "failed"}:
            errors.append(f"{agent.get('id')}: invalid execution status")
        if agent.get("execution_status") == "running" and not agent.get("last_run_id"):
            errors.append(f"{agent.get('id')}: running status requires last_run_id evidence")
        if not agent.get("agent_version") or not agent.get("model_version"):
            errors.append(f"{agent.get('id')}: missing version")
    return errors

def main():
    data = load()
    errors = validate(data)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"VALID: {len(data['agents'])} unique registered agent records")
    print(f"Departments: {len({a['department'] for a in data['agents']})}")
    print("Execution status: catalog only; no agent is claimed running")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
