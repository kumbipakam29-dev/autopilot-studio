# Agent Runtime (MVP)

Current scope: deterministic task routing only. This is not yet a fully autonomous agent, distributed compute engine or dashboard integration.

## Run locally

Requirements: Python 3; no third-party package or API key is required.

```bash
python runtime/runner.py
python -m unittest discover -s tests -p 'test_agent_runner.py' -v
```

Run a task file:

```bash
python runtime/runner.py --task path/to/task.json
```

Minimal task example:

```json
{
  "task_type": "draft_content",
  "input": {"topic": "cafe offer", "mode": "draft_only"}
}
```

Known task types are listed in `agents/registry.json`. Unknown types and unexpected top-level fields are rejected. Tasks assigned to approval-required agents return `awaiting_user_approval`; the MVP does not perform the external action.

## Status and limitations
- `review_required` means a task was routed and needs review; it does not mean work was completed.
- `awaiting_user_approval` is a policy status, not a functioning approval UI.
- Events are appended to `runtime/events.jsonl` and may contain task IDs and agent metadata; do not place secrets or sensitive personal data in task inputs.
- Payment/application statuses must be confirmed by a person with evidence. The router cannot verify payment.
- GitHub Actions is configured to run tests on relevant changes, but a passing run must be checked in the Actions tab before reporting success.
- No paid model, external API, browser automation, client outreach or publishing is wired into this runtime.
