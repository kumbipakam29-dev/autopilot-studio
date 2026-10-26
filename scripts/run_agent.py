#!/usr/bin/env python3
"""Run one implemented safe agent or print registry/runtime status."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agents.runtime import run_task, get_status

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run a registered handler")
    run.add_argument("--agent-id", required=True)
    run.add_argument("--task", required=True)
    run.add_argument("--inputs-json", default="{}")
    status = sub.add_parser("status", help="show registry and run-ledger status")
    args = parser.parse_args()
    if args.command == "run":
        try:
            inputs = json.loads(args.inputs_json)
            if not isinstance(inputs, dict):
                raise ValueError("inputs-json must be a JSON object")
        except (json.JSONDecodeError, ValueError) as exc:
            parser.error(str(exc))
        result = run_task(args.agent_id, args.task, inputs)
    else:
        result = get_status()
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return 0 if result.get("status") not in {"failed"} else 1

if __name__ == "__main__":
    raise SystemExit(main())
