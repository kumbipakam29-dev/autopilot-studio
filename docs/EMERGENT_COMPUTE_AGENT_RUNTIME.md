# Emergent Compute and Agent Runtime — Zero-Budget Implementation
Updated: 2026-10-26

## Purpose
Turn AutoPilot Studio from agent labels into a small, testable task runtime. Here, emergent compute is a design concept, not a specific product. Build observable bounded workflows first; multiple agent names do not by themselves prove autonomy.

## Constraints
- Zero-budget by default: local Python/Node tools and GitHub Actions free allowance where available.
- No paid model/API required for v0. Use deterministic rules, templates and human review; optionally add a locally run model if hardware supports it.
- No secrets in the client, public repository or logs.
- No automatic external applications, client DMs, publishing, purchases, account/security changes or payment actions.
- Reverse engineer only systems you own or are authorized to test. Do not extract third-party cookies, tokens, private prompts or hidden endpoints.

## Runtime v0 architecture
1. **Task intake** — JSON record with task_id, type, input, created_at, status, approval_required and evidence_refs.
2. **Registry** — stable agent IDs and versions, allowed task types, input/output schema, timeout, retry limit and approval policy.
3. **Planner/router** — deterministic mapping from task type to agent ID/version; no LLM needed for v0 routing.
4. **Worker** — one bounded function per agent. Workers do not execute arbitrary shell commands or free-form tool instructions.
5. **Evidence log** — append-only events for task creation, worker start/completion/failure and approval transitions. Include timestamp, agent/version, result summary and evidence path; redact secrets and personal data.
6. **Policy gate** — external side effects remain awaiting approval until the user approves. Payment claims require explicit user evidence and confirmation.
7. **Quality checks** — validate schemas, source URLs, timestamps, duplicate IDs and expected outputs. Invalid outputs fail closed.
8. **Dashboard/reporting** — distinguish planned, implemented, tested, connected and live_verified. Display last run and evidence; never infer a connection from a static label.

## Minimal task lifecycle
Normal: queued -> running -> review_required -> approved -> completed.
Failure: running -> retryable_failed -> queued (bounded retries), then failed.
External action: review_required -> awaiting_user_approval -> approved_for_action -> action_completed.

## Agent roles for AutoPilot Studio
- Opportunity Researcher v1: gathers official role links and records last_checked; never applies.
- Source Verifier v1: checks required fields and marks source confidence; a page fetch is not proof of eligibility or payout.
- Content Planner v1: creates draft calendars/captions; no publishing permission.
- Portfolio Builder v1: creates explicitly labelled fictional/spec samples; no fabricated client outcomes.
- Quality Reviewer v1: checks spelling, claims, duplicate content, IP risk and CTA.
- Earnings Ledger v1: records user-confirmed application/work/payment evidence; cannot mark Paid from a listing or estimate.
- Router v1: deterministic task dispatch only.
- Report Writer v1: summarizes task records and evidence; no invented accomplishments.

## Implementation phases
### Phase 1 — local deterministic MVP
- Add versioned agents/registry.json and JSON schemas.
- Add runtime/runner.py using Python standard library only.
- Add unit tests for valid/invalid tasks, retry limits, approval gates and status transitions.
- Write JSONL events locally; redact token-like strings before logging.
- Add a demo command for a harmless sample task and report.
- No external API calls or model downloads.

### Phase 2 — dashboard integration
- Replace status-only cards with runtime task data while keeping the app usable offline.
- Show last execution timestamp, version, failure reason and evidence path.
- Keep localStorage as a UI cache, not authoritative payment proof.
- Export tasks and events as CSV/JSON.

### Phase 3 — optional distributed execution
- Only after local tests pass, consider GitHub Actions or a self-hosted runner for scheduled non-sensitive jobs.
- Ray/Kubernetes/Slurm are not needed for a small zero-budget MVP; they add operational overhead and may incur compute cost.
- Decentralized compute networks are optional experiments, not assumed cheaper or safer. Verify pricing, data policy and payout first.

## Acceptance criteria
- A sample task runs locally without credentials or paid APIs.
- Every task has an ID, agent/version, timestamps, status and evidence.
- Invalid schema fails closed with a useful error.
- A failed worker respects a bounded retry count.
- External side effects cannot execute without explicit approval.
- Tests prove payment cannot be verified without a user-confirmed evidence record.
- Successful build/tests must be observed before claiming they pass.

## Reverse-engineering checklist (authorized systems only)
- Start with source code, manifests, lockfiles and official API documentation.
- Use DevTools/Wireshark only on systems and traffic you own or are authorized to inspect.
- Record input/output behavior with a fixed test corpus and redact credentials.
- Do not bypass access controls, extract secrets, evade rate limits or fuzz production endpoints without written permission.
- Reproduce public interfaces and observable behavior rather than copying proprietary implementation.