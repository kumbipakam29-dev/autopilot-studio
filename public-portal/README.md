# AutoPilot Studio public agent portal (MVP)

A mobile-friendly website chat prototype with a small allowlist of deterministic draft tasks.

## Run locally

From the repository root:

\`\`\`bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r public-portal/requirements.txt
uvicorn app:app --app-dir public-portal --host 127.0.0.1 --port 8000
\`\`\`

Then open http://127.0.0.1:8000.

Health endpoint: \`/api/health\`. Agent registry: \`/api/agents\`.

## Supported tasks

- Draft a social caption.
- Draft a 14–20 second Reel script.
- Create a basic 7-day content calendar.
- Accept a public-research brief while stating that live research is not connected.

These are deterministic templates; no paid or local LLM is connected yet.

## Approval review API (not an action executor)

Potential publishing, outbound messaging, uploads/deploys, purchases/payments, account changes, submissions, and destructive requests are stored in a SQLite queue for review. Queue records expire after seven days. Likely passwords/API keys/secrets, email addresses, and phone numbers are redacted before storage, but this is only best-effort filtering: **never submit passwords, OTPs, payment details, government IDs, or private customer information.**

The approval API is disabled unless a server-side \`AUTOPILOT_APPROVAL_TOKEN\` is configured. Set a long random secret in the hosting environment; never put it in browser code, the repository, or a URL. Send it only as the \`X-Approval-Token\` header. The endpoints are:

- \`GET /api/approvals\` — list up to 100 unexpired records.
- \`POST /api/approvals/{task_id}/decision\` with JSON \`{"decision":"approved_for_manual_review"}\` or \`{"decision":"rejected"}\`.

A recorded approval means only “approved for manual review”; **it does not send, publish, pay, deploy, modify accounts, or execute any other external action.** Review endpoints are intended for an owner-operated admin client, not the public chat UI.

The SQLite path defaults to \`/tmp/autopilot-approval-queue.sqlite3\`. Configure \`AUTOPILOT_APPROVAL_DB\` to a private persistent disk path when hosting. If the filesystem is ephemeral, queue data can be lost during restarts/redeploys. The per-peer in-memory rate limiter is only a prototype guard and can be bypassed across instances/restarts.

## Safety limits

- Unsupported tasks are rejected.
- No shell tool, arbitrary code execution, credentials store, external publishing integration, payment integration, or connected model is present.
- The agent registry describes local handlers, not background agents or connected accounts.
- Do not expose the app publicly until authentication, privacy, rate limiting, persistent storage, and deployment hardening have been independently reviewed.
- No task is considered published, paid, or successful until independently verified.

## Tests

\`\`\`bash
PYTHONPATH=public-portal python -m unittest discover -s public-portal -v
\`\`\`
