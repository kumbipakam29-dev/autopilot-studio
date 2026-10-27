"""JSON stdin/stdout CLI for offline specialist capability prototypes.

Usage:
  python -m agents.run_specialist APS-CR-02 < input.json

No network or external actions are performed. Inputs are supplied by the caller.
"""
from __future__ import annotations

import json
import sys

from agents.specialist_capabilities import run_capability


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "usage: python -m agents.run_specialist AGENT_ID"}, ensure_ascii=False))
        return 2
    try:
        payload = json.load(sys.stdin)
        result = run_capability(sys.argv[1], payload)
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
