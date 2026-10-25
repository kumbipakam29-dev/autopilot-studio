# AutoPilot Agent Training & Evaluation Playbook

## Mission
Build a reliable, useful, low-cost agent team for AutoPilot Digital Studio. Optimize for verified user value and eventual legitimate income—not agent count, impressive status labels, or activity volume.

## Current reality
The registry is a catalog of agent roles, not proof that every listed agent is a running autonomous worker. Treat each agent as a versioned capability with an owner, inputs, allowed tools, output schema, tests, and measurable success criteria. Do not claim LLM reasoning, live integrations, or background operation unless those capabilities are implemented and a run is evidenced.

## Training loop
1. **Choose one measurable task.** Examples: find eligible free work, rank a client lead, draft a social post, or check an opportunity's payout terms.
2. **Collect source evidence.** Prefer official provider pages, current dates, canonical URLs, and short supporting excerpts. Separate observed facts from assumptions.
3. **Produce a structured result.** Include source, checked time, confidence, status, eligibility, rate and unit, payout conditions, risk flags, next action, and evidence.
4. **Evaluate before promotion.** Run unit tests, fixed regression examples, adversarial/safety cases, and where possible a small human-reviewed sample.
5. **Record errors.** Classify each as extraction, freshness, duplication, eligibility, ranking, policy, or reporting failure. Create a minimal regression test for every fixed bug.
6. **Change one thing at a time.** Keep changes on a feature branch, compare before/after metrics, and preserve rollback ability.
7. **Promote only with evidence.** A new agent version is accepted only if tests pass, safety regressions are absent, and its task-specific metrics improve or remain within documented tolerances.

## Required per-agent card
Each agent must document:
- Stable name and semantic version
- One-sentence job and explicit non-goals
- Inputs, output schema, dependencies, and timeout/rate limits
- Allowed tools and forbidden side effects
- Data handling and identity boundary
- Unit tests, regression fixtures, safety tests
- Metrics, known failure modes, last evaluated commit, and current status

## Initial evaluation suite

### Earnings discovery
- Official source URL is retained and normalized.
- Generic category pages are not mislabelled as individual open jobs.
- Amounts preserve their unit and context: per task, per hour, per study, range, bonus, or unspecified.
- A number appearing anywhere on a page is not automatically treated as the payout rate.
- Availability and checked time are explicit; unknown is not equivalent to open.
- Duplicate canonical URLs/project IDs are collapsed without losing source evidence.
- Fees, deposits, crypto purchases, suspicious payout claims, and requests for sensitive data are quarantined.
- A successful scan is never counted as income.

### Client acquisition
- Lead facts are public, business-level, relevant, and source-linked.
- Personal data is minimized; no private-data scraping.
- Pitch drafts mention only verifiable observations and do not promise outcomes.
- Drafting is separate from sending; opt-outs and platform terms are respected.
- Portfolio samples are labelled SPEC until real client work exists.

### Signup and identity
- Use only official domains and check current country/language eligibility.
- Free, low-risk steps may proceed autonomously when the platform allows it and the data is accurate.
- Never invent identity/profile facts or store secrets in logs, artifacts, prompts, or Git.
- Stop for OTP, CAPTCHA, government ID, selfie/liveness, biometrics, bank/payment credentials, owner-only declarations, fees, or uncertain permissions.
- Do not claim signup completion without platform confirmation.

### POD and creative work
- Generate original briefs and assets; document provenance and rights checks.
- Do not copy protected characters, logos, brand marks, or competitor designs.
- Validate dimensions, transparency, format, and print-readiness before labelling an asset ready.
- Research and draft only until marketplace publication is separately authorized.

## Metrics dashboard
Track these per run and per agent version:
- Source fetch success / failure rate
- Freshness coverage and percentage of rows with evidence URLs
- Precision on a manually reviewed sample (especially open-job and payout claims)
- Duplicate rate and false-positive rate
- Safety-test pass rate; target 100% for critical identity/financial boundaries
- Useful outputs per minute / free compute budget
- Owner actions needed and owner-confirmed completion rate
- Applications accepted, tasks approved, and actual owner-confirmed payments—each a distinct metric
- Cost incurred; target ₹0 unless the owner explicitly changes the budget

Do not optimize a metric by hiding failures, inventing confidence, or counting leads as jobs or payments.

## Release gates
- **Prototype:** output exists; reliability not yet established.
- **Tested:** automated tests and safety cases pass.
- **Observed:** live run completed with evidence and limitations recorded.
- **Pilot:** reviewed sample meets documented quality thresholds.
- **Production:** stable monitoring, rollback, permissions, and owner-approved release are in place.

A successful workflow run alone only proves that the workflow completed. It does not prove that a lead is valid, a signup succeeded, an application was accepted, or money was earned.

## Default working cadence
For each bounded cycle: discover → verify → rank → draft/prepare → test → report. Prefer one high-quality, actionable lead over dozens of weak links. Keep experiments free, rate-limited, reversible, and transparent. Stop only when the cycle's defined checks are complete or a real blocker is reached; then record the blocker and next safe action.
