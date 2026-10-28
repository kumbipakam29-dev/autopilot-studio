# 15-specialist supervised learning loop

**Status:** specification committed for review. This does not mean 15 separate model processes are running. The repository currently has a planned 100-agent catalog; this file defines a small, testable first cohort.

## Goal
Use 15 distinct specialist profiles with bounded tasks and a shared review loop. Start at ₹0 with deterministic Python checks and human-reviewed examples. Do not install paid models or dependencies by default.

## The 15 specialist profiles
1. **Chief of Staff** — priorities, blockers, approvals.
2. **Task Planner** — small tasks and acceptance criteria.
3. **Agent Router** — skill/risk/permission-based assignment.
4. **Market Research Analyst** — dated, source-backed market evidence.
5. **Prospect Qualifier** — official source, business fit, recent content, public contact channel.
6. **Offer Strategist** — specific service offer without outcome guarantees.
7. **Outreach Copywriter** — personalized unsent drafts only.
8. **Social Content Strategist** — pillars, audience, calendar, CTA.
9. **Short-Form Video Writer** — 14–20 second script timing, hook, shots, CTA.
10. **Caption & Brand Voice Editor** — clarity, tone, claim review.
11. **Visual Design QA** — readability, dimensions, originality, rights.
12. **SEO & Website Auditor** — search intent, structure, quality, no thin-page mass generation.
13. **CRM Data Steward** — source provenance, schema, duplicate checks, opt-outs.
14. **Python Test Engineer** — offline tests, reproducible defect reports.
15. **Learning & Evaluation Analyst** — score reviewed outputs and propose regression tests.

The exact machine-readable task definitions, versions, success metrics, failure labels, and tool boundaries are in [`config/agent_learning_loop_v1.json`](../config/agent_learning_loop_v1.json).

## Loop: every task gets evidence and a review
1. **Observe:** retain only permitted task inputs, outputs, source URLs/dates, and outcome evidence.
2. **Score:** check task acceptance criteria, factuality/evidence, safety, completeness, and reproducibility.
3. **Label:** distinguish confirmed error, reviewer preference, unknown, and successful outcome.
4. **Diagnose:** identify root cause instead of adding a vague instruction.
5. **Propose:** one minimal, versioned prompt/rule/code change.
6. **Regression-test:** compare baseline vs candidate on fixed offline fixtures.
7. **Review:** a human approves behavior, permissions, external actions, and any release.
8. **Release or rollback:** preserve previous known-good version and record the commit + evaluation result.

## Scoring
Use the JSON rubric: task success 30, evidence/factuality 25, safety/permissions 20, completeness/format 15, reproducibility 10. A score of 85/100 is a review threshold, not automatic approval. Fabricated evidence, unauthorized action, secret exposure, or claiming an unrun test passed is a hard fail regardless of score.

## Learning boundaries
- This is supervised improvement of examples, tests, prompts, rules and code—not automatic model-weight training.
- Agents do not approve their own code, permissions or release.
- No default shell, network, messaging, publishing, account, purchase, payment, or deployment tools.
- Use a deterministic mock if a model is not configured; never silently fall back to a paid endpoint.
- Never save secrets, private contact details or client-confidential records in the public repository.
- A task counts as learned only when a reviewed correction becomes a regression fixture or a versioned rule with a source of truth.

## Implementation order
1. Validate the JSON schema and unique IDs.
2. Add offline tests for the specialist catalog and scoring/hard-fail rules.
3. Run existing test suite and report actual output.
4. Build a no-network registry loader.
5. Trial one specialist against a deterministic baseline.
6. Expand only after tests pass and measured value is demonstrated.

## Honest current status
- 15 specialist profiles specified in JSON.
- Runtime agents, model assignments and model-weight training: **not configured / not claimed**.
- Learning loop execution, regression scores and CI: **not yet verified**.
- Repository changes are on the existing draft PR branch; nothing merged or externally published.
