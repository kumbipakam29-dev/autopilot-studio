# AutoPilot Studio public agent portal (MVP)

A mobile-friendly website chat prototype with a small allowlist of deterministic draft tasks.

## Run locally

From the repository root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r public-portal/requirements.txt
uvicorn public-portal.app:app --host 127.0.0.1 --port 8000
```

Then open http://127.0.0.1:8000. If Python rejects the hyphenated package path in the command above, run from the repository root with:

```bash
uvicorn app:app --app-dir public-portal --host 127.0.0.1 --port 8000
```

Health endpoint: `/api/health`.

## What it can do

- Draft a social caption.
- Draft a 14–20 second Reel script.
- Create a basic 7-day content calendar.
- Accept a public-research brief while clearly stating that no live research connector is enabled.

These are deterministic templates; no paid or local LLM is connected yet.

## Safety boundaries

- Unsupported tasks are rejected.
- Potential publishing, outbound messaging, purchase/payment, account-change, submission, and destructive requests are marked for approval and not executed.
- There is no shell tool, arbitrary code execution, filesystem access, external publishing integration, payment integration, or credentials store.
- The in-memory rate limiter is a prototype guard, not a substitute for production edge rate limiting.
- The approval queue is volatile memory only. It is not a usable multi-user approval workflow and resets when the server restarts.
- Do not expose this prototype to the public internet until tests, persistent queue/authentication, privacy review, production rate limiting, and deployment hardening are complete.

## Next hardening milestones

1. Add automated API tests for allowlisted tasks, approval gating, validation, and rate limits.
2. Add durable task storage with per-user authorization and a real review UI.
3. Configure deployment-specific trusted proxy handling and edge rate limits.
4. Add consent/privacy text and data retention controls.
5. Add a provider-neutral agent registry and connect existing agents only behind explicit task permissions.
6. Deploy only after all tests pass and the public URL is verified.

No task is considered published, paid, or successful until independently verified.
