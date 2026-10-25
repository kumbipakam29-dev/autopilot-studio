"""Validate the additive specialist-team registry; registration is not runtime activation."""
from __future__ import annotations

import json
from pathlib import Path

REGISTRY_PATH = Path(__file__).resolve().parents[1] / "agents" / "specialist_team_registry.json"
EXPECTED_DEPARTMENTS = {
    "social_media_specialist": 15,
    "auto_error_handling": 15,
    "cybersecurity_defense": 15,
}
SAFE_TOOLS = {
    "local_files_read",
    "local_files_write_draft",
    "python_sandbox",
    "public_read_only",
}
REQUIRED_DENIALS = {
    "public_publish": False,
    "send_message": False,
    "account_change": False,
    "payment": False,
    "delete": False,
    "security_control_change": False,
}


def validate_registry(data: dict) -> list[str]:
    errors: list[str] = []
    agents = data.get("agents", [])
    if data.get("total_agents") != 45 or len(agents) != 45:
        errors.append("specialist registry must declare exactly 45 agents")
    if data.get("departments") != EXPECTED_DEPARTMENTS:
        errors.append("department counts must be 15 social, 15 error-handling, 15 cybersecurity")
    ids = [a.get("id") for a in agents]
    if len(set(ids)) != len(ids) or any(not isinstance(i, str) or not i for i in ids):
        errors.append("agent IDs must be non-empty and unique")
    actual_counts = {key: sum(a.get("department") == key for a in agents) for key in EXPECTED_DEPARTMENTS}
    if actual_counts != EXPECTED_DEPARTMENTS:
        errors.append(f"actual department counts mismatch: {actual_counts}")
    for agent in agents:
        agent_id = agent.get("id", "<missing-id>")
        if agent.get("registry_status") != "registered" or agent.get("execution_status") != "planned":
            errors.append(f"{agent_id}: registration must not imply a live worker")
        if agent.get("execution_mode") != "draft-only; external integrations not configured":
            errors.append(f"{agent_id}: unexpected execution mode")
        if not set(agent.get("allowed_tools", [])) <= SAFE_TOOLS:
            errors.append(f"{agent_id}: unknown or unsafe tool permission")
        permissions = agent.get("permissions", {})
        for key, expected in REQUIRED_DENIALS.items():
            if permissions.get(key) is not expected:
                errors.append(f"{agent_id}: {key} must remain denied")
        if agent.get("department") == "cybersecurity_defense" and agent.get("safety_profile") != "defensive_authorized_scope_only":
            errors.append(f"{agent_id}: cybersecurity role must be limited to authorized defensive scope")
        if not agent.get("role") or not agent.get("purpose"):
            errors.append(f"{agent_id}: role and purpose are required")
    return errors


def main() -> int:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    errors = validate_registry(data)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print("OK: 45 specialist roles validated (catalogue only; none are activated).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
