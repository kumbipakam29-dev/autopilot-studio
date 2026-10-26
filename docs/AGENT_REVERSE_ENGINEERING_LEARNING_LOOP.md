# Agent Reverse-Engineering Learning Loop (Safe, Evidence-Driven)

Status: proposed operating procedure; not a claim that an agent has run against a live system.
Budget: zero-cost first. Human approval required for external side effects.

## Purpose

Improve AutoPilot Studio agents by learning from reproducible failures and observable behavior—not by guessing, endlessly retrying, or claiming success without evidence. Here, reverse engineering means authorized analysis of our own repository, app, workflows, logs, and documented interfaces. Do not bypass access controls, extract secrets, evade platform limits, or probe systems without permission.

## Bounded loop

Each run handles one narrowly scoped defect or quality gap. Maximum: 3 fix attempts and 20 minutes of agent/tool work per issue unless a human explicitly extends it.

1. **Observe** — capture expected behavior, actual behavior, timestamp, app/commit/version, and relevant sanitized log or screenshot. Mark missing evidence as unknown.
2. **Reproduce** — create a minimal repeatable test case. If it cannot be reproduced, label it `needs_observation`; do not invent a root cause.
3. **Map the path** — trace inputs → routing/configuration → execution → output/state. Inspect only relevant code and logs. Never include tokens, passwords, personal data, or private customer content in artifacts.
4. **Hypothesize** — record one primary cause and at least one alternative. Tie each hypothesis to evidence and name a test that could disprove it.
5. **Patch minimally** — make the smallest reversible change on a feature branch. Preserve approval gates and fail-closed behavior. No production changes, account changes, publishing, outreach, payments, or destructive commands.
6. **Test** — run the focused test first, then relevant regression tests. Add a regression test for every confirmed defect. Record exact commands, exit codes, and results; if tests were not run, say so.
7. **Independent critique** — a separate review pass checks correctness, security, scope, user impact, and whether evidence supports the claim. It can reject the patch.
8. **Compare** — compare before/after behavior against explicit acceptance criteria. A green unit test is not proof that deployment, a UI, an integration, a client, or revenue works.
9. **Learn** — add a short sanitized entry: symptom, reproduction, confirmed cause (or unknown), change, tests, residual risk, and next action. Avoid secrets and identifying data.
10. **Stop or escalate** — stop on acceptance, 3 failed attempts, missing permission, destructive risk, unavailable dependencies, or ambiguous evidence. Escalate with the smallest useful evidence bundle instead of looping indefinitely.

## State machine

`queued → observing → reproducing → hypothesizing → patching → testing → independent_review → verified`

Allowed side states: `blocked`, `needs_observation`, `rejected`, `human_approval_required`. Only transition to `verified` when acceptance checks passed and evidence is attached. Otherwise preserve the blocker state; never silently convert an error into success.

## Evidence record template

Required fields: issue_id, target, expected, actual, reproduction, hypotheses (evidence and disproof test), change/commit, tests (command, exit code, result), review outcome, status, residual risks, next action, external_side_effects.

Use real values only. This is a schema guide, not a record of tests that have run.

## Agent roles

- **Observer:** gathers reproducible facts; cannot edit code.
- **Tracer:** maps the relevant code/config path and proposes competing hypotheses.
- **Fixer:** makes one minimal branch-only change.
- **Tester:** runs tests and records outcomes; cannot self-certify missing checks.
- **Critic:** independently reviews evidence, safety, and scope.
- **Recorder:** writes the learning entry and updates status only from evidence.

For a small free-tier project, these are logical roles, not six continuously running agents or six paid model calls. They can be sequential stages in one deterministic runner.

## Acceptance gates

A fix is ready for human review only when:
- the defect is reproducible or the limitation is explicitly recorded;
- a regression test fails before the fix and passes after it, where practical;
- focused and relevant regression tests have recorded results;
- no secrets or unnecessary personal data are included;
- changes are limited to the stated scope;
- rollback/revert is straightforward;
- external actions remain disabled unless separately approved.

A fix is not ready merely because the agent says it is fixed. Merge, deploy, publish, send, apply, or spend are separate gated actions.

## Quality and business outcome separation

Track engineering metrics separately from business outcomes:
- engineering: reproducibility rate, tests passed/failed, reopened defects, time per bounded loop, false-success claims;
- content quality: brief compliance, safe-area/line overflow, legibility, originality, useful CTA, human review;
- business: qualified leads, replies, proposals, paid orders, and verified receipts—with dated evidence.

Do not fabricate views, leads, clients, sales, or payments. Do not optimize for volume when quality checks fail.

## Immediate visual-content lesson

If text runs outside boxes or a video is poor/unviewable, mark the artifact **rejected**, not published. Rebuild with a 9:16 canvas for short-form video, measured safe areas and automatic line wrapping, 1–2 short text blocks per scene, readable type and contrast, adequate hold time, a frame-by-frame preview/contact sheet, and a final checklist for clipping, spelling, pacing, audio, and factual claims.

If no rendered preview is available, say visual QA is incomplete. Never describe a script or storyboard as a finished video.

## Cost and permission policy

Prefer Python standard library, existing repository tests, GitHub Actions free allowance, and manual evidence. Do not introduce paid APIs, paid subscriptions, or new dependencies without explicit approval. Never reverse engineer third-party private systems or defeat DRM, authentication, rate limits, or security controls.

## Run summary format

Every cycle reports: **Changed** (files/commit or none); **Evidence** (test results or not run); **Learned** (confirmed cause or unknown); **Status** (verified/blocked/needs observation/rejected); **Next step** (one concrete action); **External actions** (none unless separately approved and evidenced).

## References

- Google Cloud, agent loop and review/critique patterns: https://docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system
- Cucumber, small iterations and executable examples: https://cucumber.io/docs/bdd/
- Microsoft Learn, test early and layered testing: https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/testing