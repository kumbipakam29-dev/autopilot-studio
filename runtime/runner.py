#!/usr/bin/env python3
"""Tiny deterministic task runner for AutoPilot Studio; standard library only."""
import argparse
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "agents" / "registry.json"
EVENTS = ROOT / "runtime" / "events.jsonl"

def now():
    return datetime.now(timezone.utc).isoformat()

def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))

def log_event(event):
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def run_task(task):
    required = {"task_type", "input"}
    missing = required - task.keys()
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(sorted(missing)))
    registry = load_registry()["agents"]
    agent = next((a for a in registry if task["task_type"] in a["task_types"]), None)
    if not agent:
        raise ValueError("No registered agent for task type: " + str(task["task_type"]))
    task_id = task.get("task_id") or str(uuid.uuid4())
    approval_required = bool(agent.get("approval_required"))
    status = "awaiting_user_approval" if approval_required else "review_required"
    result = {
        "task_id": task_id, "task_type": task["task_type"],
        "agent_id": agent["id"], "agent_version": agent["version"],
        "status": status, "approval_required": approval_required,
        "created_at": task.get("created_at") or now(), "updated_at": now(),
        "input": task["input"],
        "message": "Task routed only; external actions are not executed by this MVP."
    }
    log_event({"event": "task_routed", "task_id": task_id, "agent_id": agent["id"],
               "agent_version": agent["version"], "status": status, "timestamp": now()})
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", help="Path to task JSON; if omitted, run a safe demo task")
    args = parser.parse_args()
    task = json.loads(Path(args.task).read_text(encoding="utf-8")) if args.task else {
        "task_type": "draft_content", "input": {"topic": "sample cafe post", "mode": "draft_only"}}
    result = run_task(task)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
