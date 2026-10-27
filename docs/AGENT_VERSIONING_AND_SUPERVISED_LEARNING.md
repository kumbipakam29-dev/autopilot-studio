# Agent, Prompt & Model Versioning Standard

**Status:** specification for implementation; not a claim that all 100 agents are running.
**Budget:** ₹0 default. No paid API or subscription without explicit approval.

## Version dimensions

Every agent release records these separately:

- `agent_id`: stable identifier, `APS-001` through `APS-100`; never recycle IDs.
- `agent_version`: semantic version for agent contract and behavior.
- `prompt_version`: semantic version for system prompt, rules and task template.
- `model_profile`: provider/model family selected by configuration; `unassigned` until verified.
- `model_version`: exact model release/tag or local model digest when obtainable; never infer it from a friendly label.
- `framework` and `framework_version`: orchestration framework and pinned release, if used.
- `tool_policy_version`: allowed tool list and permissions.
- `evaluation_suite_version`: benchmark/fixture version used for release approval.
- `source_commit`: repository commit containing the tested implementation.
- `status`: planned, prototype, tested, active, paused, retired.
- `evaluation_status`: not-run, passed, failed, needs-review.

## Semantic version rules

- **PATCH** (0.1.0 → 0.1.1): bug fix or prompt clarification that preserves the input/output contract.
- **MINOR** (0.1.0 → 0.2.0): backward-compatible skill or tool addition.
- **MAJOR** (0.9.0 → 1.0.0): breaking contract, permission, safety or output-schema change.
- Model changes do not silently bump the agent version: record model ID/version separately and rerun the same evaluation suite.
- A prompt, model, framework or tool-permission change creates a new evaluation record. Keep the prior known-good config for rollback.

## Supervised learning loop

1. **Observe:** capture task input, output, source evidence, errors and user feedback. Redact secrets and unnecessary personal data.
2. **Classify:** assign a failure category (wrong facts, missing evidence, poor format, policy block, timeout, dependency issue, etc.).
3. **Build fixture:** turn the failure into a synthetic or permission-safe regression test. Do not put credentials or private customer data in fixtures.
4. **Propose:** a researcher/critic proposes one change to prompt, rules, code or model configuration.
5. **Evaluate:** run old and candidate versions on the same offline benchmark, including adversarial and edge cases.
6. **Review:** require human approval for changes that affect safety, permissions, external actions or production behavior.
7. **Release:** pin versions, publish a changelog and record tested commit + metrics.
8. **Monitor & rollback:** revert if quality, safety, reliability or cost worsens.

This loop improves prompts, rules, code and test coverage. It is **not model-weight training** and does not imply autonomous self-modification.

## Model comparison record

For each candidate model, log:
- model family and exact version/digest (if available)
- license and redistribution/use restrictions
- runtime hardware, memory, latency and failure rate
- benchmark score by task category
- factuality/evidence score and safety test results
- network use and whether any paid endpoint is involved
- date checked and source URL

A model is not "best" merely because it is popular. Route by measured task fit, cost, hardware, license and safety. If no model is available locally, use deterministic test doubles; never silently fall back to a paid API.

## Permissions and approvals

- Deny tools by default; each agent receives only the minimum allowlisted tools it needs.
- No shell execution, repository writes, account actions or arbitrary network access in the first prototype.
- Human approval is mandatory before external outreach, submissions, publishing, purchases, deployments, payout/account changes or spending.
- CI must be deterministic and offline using mocks; secrets must never appear in logs or fixtures.
- The model cannot approve its own proposed code, permission changes or release.

## First implementation milestones

1. Validate `config/agent_registry_v1.json` against a schema and assert exactly 100 unique IDs.
2. Add a small registry loader with no model dependency and unit tests.
3. Repair existing offline-test failures before adding orchestration dependencies.
4. Prototype one read-only agent with deterministic mocks and compare it with the existing Python baseline.
5. Add a versioned evaluation report and rollback procedure.
6. Only after measured benefit, evaluate one optional framework adapter (smolagents or LangGraph) with a pinned version and license review.

## Honest status

The registry is a plan/catalog, not 100 deployed autonomous processes. Model assignments, framework installations, benchmarks, and running status must remain unassigned/not-run until verified in the repository and CI.
