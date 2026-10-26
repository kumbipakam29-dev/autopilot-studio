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

## Opportunity review queue

The opportunity tracker ranks records already collected from sources that permit the chosen collection method. It does not discover jobs, scrape sites, log in, message clients, or submit applications.

Start from the clearly labelled demo input (not a real lead list):

```bash
python runtime/opportunity_tracker.py --input runtime/opportunities.example.json --output /tmp/approval_queue.csv
```

For real records, create a private local JSON file (do not commit personal contact details or private lead data) and run:

```bash
python runtime/opportunity_tracker.py --input /path/to/opportunities.json --output /path/to/approval_queue.csv
```

Input must be a JSON array. Each record may include `opportunity_id`, `source`, `title`, `url`, `posted_at`, `description`, `payment_text`, `eligibility_checked`, `payment_verified`, and `notes`. The score is a triage hint, not a legitimacy guarantee. Review risk flags and verify terms, location eligibility, payment, and deadlines yourself. Every generated row has `approval_required=true`; no application or outreach is submitted.

Run the complete Python test suite:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```
