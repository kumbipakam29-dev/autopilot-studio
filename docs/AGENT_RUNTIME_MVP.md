# Agent runtime MVP

## What is implemented
- Registry-backed ID lookup and duplicate-ID validation.
- Five deterministic handlers: social caption draft, short Reel script draft, 7-day content calendar, website audit checklist, and job-search filter.
- SQLite run ledger recording run ID, agent/model versions, status, result, error, and approval flag.
- Sensitive-action keyword gate that records an approval request instead of executing the action.
- CLI status report and automated unit tests.

## Run locally
```bash
python scripts/run_agent.py status
python scripts/run_agent.py run --agent-id APS-SOCIAL-GROWTH-121 --task "draft caption" --inputs-json '{"business":"Cafe","offer":"Coffee tasting","audience":"nearby customers"}'
python -m unittest discover -s tests -v
```

The SQLite ledger defaults to `runtime/run_ledger.sqlite3`, which is local and should not be committed. Use a private persistent path in a deployed service.

## Boundaries
- Only handlers in `agents/runtime.py` execute. The other registry entries remain blocked until implemented and tested.
- A registry record does not mean a worker is running. This runtime executes one task per CLI invocation; it is not a 500-worker daemon or scheduler.
- Publishing, sending messages, purchases, payments, account changes, deletion, deployment, job applications, and financial actions are not performed. Matching tasks are held in an approval queue.
- The approval queue currently records pending requests only; it does not provide an authenticated approval UI or execute approved actions.
- The website audit agent emits a checklist, not findings from a live crawl. Job alert agent provides filters only; no live job feed is connected.
- The current router uses deterministic templates and no external model/API.
- Do not expose this CLI or SQLite ledger to the public internet without authentication, authorization, retention limits, and security review.
