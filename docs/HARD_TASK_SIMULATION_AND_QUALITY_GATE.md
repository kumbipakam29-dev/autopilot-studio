# Hard Task Lab, Learning Loop, and Customer Quality Gate

## Two separate assignments

- Track A — compute/runtime resilience: schedules seeded jobs under a 512 MB logical budget and two-job concurrency limit, rejects oversized jobs, simulates one transient failure and retry, and records event history plus a fixture SHA-256.
- Track B — customer creative workflow: creates a 16-second Reel script, three caption drafts, a poster brief and a seven-day calendar from a named fictional cafe brief. It checks approved-fact grounding, prohibited claims, timing, completeness and draft-only status.

## Truth boundaries

These are deterministic Python simulations. “Virtual RAM” is logical resource accounting; no OS memory is allocated. The suite does not run a real compiler or Android build, invoke a live LLM, browse the web, publish a post, contact a client, or process a payment. The JSON records these facts explicitly. The baseline is a labelled synthetic fixture, not a measured old-model score. Scores are rule-based and do not prove creative quality.

## Professional customer gate

The simulation always sets customer_delivery_allowed to false. Future model-backed work must pass all of these gates:
1. Client brief completeness and permission to use supplied information.
2. Approved-fact grounding; no invented testimonials, awards, prices, guarantees or business results.
3. Format checks: timing, spelling, aspect ratio and readability where visual assets are created.
4. Privacy, safety and copyright review.
5. Regression checks against versioned reference examples.
6. Human quality approval before external delivery or publishing.

A failed factuality, privacy or safety check must reject/hold the candidate regardless of its aggregate score. Code and billing tasks need unit/integration tests, security review, sandbox validation and explicit owner approval before production changes or real payments.

## Run locally

    python -m agents.hard_task_simulation --output artifacts/hard-task-learning-report.json
    python -m unittest tests.test_hard_task_simulation -v

The JSON contains run ID, fixture hash, timestamp, separate track scores, test assertions, learning-cycle comparison, alert status, and execution-truth flags.

## Hourly report

The GitHub Actions workflow is configured for an hourly schedule plus manual runs. It uploads a machine-readable report artifact and writes a run summary. Scheduled workflows run from the default branch, so this workflow must be reviewed and merged before hourly runs will start. Standard GitHub alert delivery depends on repository/account notification settings. It does not send customer-facing alerts or messages.
