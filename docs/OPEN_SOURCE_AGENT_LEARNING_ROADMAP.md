# Open-Source Agent Learning & Integration Roadmap

**Status:** research and implementation plan; no third-party framework is installed or running yet.
**Budget:** ₹0. Prefer local execution, existing GitHub Actions free allowance, and permissive open-source licenses. Do not add paid API dependencies.
**Purpose:** help AutoPilot-Studio agents improve through evidence, reviewed examples, regression tests, and versioned changes—not by claiming they autonomously retrain themselves.

## Current repository baseline

The repository README describes a Python POD concept pipeline, an Earnings Hunter that scans curated public pages, a local-only Android/web status and payout ledger, and GitHub Actions for tests/artifacts. It explicitly says model inference, publishing, and live GitHub Actions-to-app sync are not connected. Keep the current working paths intact while prototyping.

Before any framework integration:
1. Re-run `python -m unittest discover -s tests -v` in CI and investigate the current failing offline-test step.
2. Inspect the actual Python version, dependency manifests, workflow permissions, and tests. Do not assume dependencies or runtime versions.
3. Make each experiment optional, isolated, and removable. Do not add a framework to the core runtime merely because it is popular.

## Curated free/open-source projects to study

The projects below are learning sources and optional integration candidates—not installed dependencies or proof of capability in our repo. Recheck each repository's license, release activity, Python compatibility, and model-provider terms before copying code.

| Project | Official repository | License / useful pattern | Suggested use here | Cost / risk note |
|---|---|---|---|---|
| Hugging Face smolagents | https://github.com/huggingface/smolagents | Apache-2.0; small, model-agnostic agent abstractions and tool calling | First isolated prototype for one read-only research or QA agent | Library is free; hosted model calls may cost money. Local models need enough RAM/compute. Code execution must remain sandboxed. |
| LangGraph | https://github.com/langchain-ai/langgraph | MIT; explicit state, nodes, transitions, durable workflows and human-in-the-loop patterns | Study patterns for retryable task queues, approval gates, and resumable jobs | Keep as a design reference first; more dependencies and complexity than our current scripts need. |
| Agno | https://github.com/agno-agi/agno | Apache-2.0; agents, teams, knowledge/memory, evaluations and approval patterns | Study agent registry, evaluation and human-approval UX; prototype only if a concrete gap remains | Framework is OSS, but hosting, databases, and model endpoints can incur costs; telemetry can be disabled with its documented setting. |
| CrewAI | https://github.com/crewAIInc/crewAI | MIT; role-based agents and task orchestration | Compare role/task definitions with our department/agent registry | Do not run multiple agents just to simulate headcount; every extra agent increases latency and failure surface. |
| OpenHands | https://github.com/OpenHands/OpenHands | MIT core; coding-agent and tool/sandbox architecture | Study controlled code-change proposals and test-first repair workflow | Full environment can be resource-heavy; never give an autonomous agent unrestricted repo secrets or production write access. |
| Ollama | https://github.com/ollama/ollama | MIT; local model runner | Optional local inference on a capable computer, if available | The software is free, but a compatible computer and storage are required. No assumption that the user's Android phone can run chosen models. |

## Recommended approach: learn first, integrate one thing at a time

### Phase 0 — Repair and measure (no new dependency)
- Make the existing test suite reliable and capture the failing test names and tracebacks.
- Add deterministic fixtures for public-page parsing, rate/unit extraction, scam-risk flags, and lead-status transitions.
- Record baseline: tests passed/failed, runtime, false-positive examples, and missing evidence fields.
- Treat scheduled scanner output as candidate leads, never as verified jobs or earnings.

### Phase 1 — Create a reviewed knowledge/evaluation loop
For each agent task, save a small, non-sensitive case record:
- task type and input source URL;
- expected output schema and required evidence;
- actual output;
- human review result (pass/fail/needs-review);
- failure category and a short correction;
- agent version, prompt/rules version, and test fixture ID.

Turn approved corrections into regression fixtures. On each code or prompt change, rerun fixtures and compare results. Store only public data or synthetic examples in GitHub. Never store IDs, voice samples, private customer data, cookies, tokens, bank details, UPI IDs, or personal account exports.

**This is supervised improvement, not automatic model training.** A framework cannot reliably “learn” just because it is installed. Weight training/fine-tuning is out of scope unless a free, suitable dataset, lawful licence, compatible hardware, and measurable evaluation plan exist.

### Phase 2 — Optional framework adapter
Prototype exactly one adapter in an isolated folder or optional extra:
- Start with smolagents for a single bounded, read-only task.
- Use a deterministic fake/mock model in unit tests so CI does not require network access or paid keys.
- Define a narrow tool allowlist: read local fixtures, parse supplied public HTML/text, validate schemas, and write a draft report only.
- Block arbitrary shell execution, secret access, account login, sending messages, publishing, purchases, payout settings, and production deployment.
- Require approval before any external side effect.
- Compare the prototype to the current plain-Python baseline. Keep it only if quality improves without breaking offline tests or adding unavoidable cost.

### Phase 3 — Agent registry and router
Each agent record should include:
- stable agent ID, department, purpose, owner/reviewer;
- versioned instructions and implementation commit;
- supported input/output schemas;
- model/provider and license/cost status;
- capability requirements (network, CPU/RAM, device, credentials);
- test suite, last evaluation result, known failure modes;
- permissions and approval gates;
- rollback version and status.

Route tasks by required capability, measured evaluation quality, resource budget, and risk—not by agent count or model popularity. If no compatible free model is available, use the deterministic rule-based path and mark the task as not model-assisted.

## Suggested first experiments for AutoPilot-Studio

1. **Earnings Hunter evidence grader:** reject a candidate unless it has an official source URL, checked timestamp, country eligibility evidence, task-specific rate/unit if published, acceptance criteria, and payout details or explicit “not stated”. Do not infer a rate from a homepage banner.
2. **Data-labeling QA critic:** compare a synthetic label against a written rubric; return pass/fail/uncertain plus the exact rubric clause. An “uncertain” result must go to human review.
3. **Portfolio QA agent:** check that spec work is labelled fictional, claims are supported, copy has no invented client results, and links/metadata are present.
4. **CI failure triager:** summarize failing test names and likely file ownership from logs; propose a patch but never merge or deploy it automatically.

## Acceptance gates for any prototype

- Existing offline test suite passes.
- New tests pass without a paid API key or network access.
- No credentials or personal data in logs/artifacts.
- Tool permissions are allowlisted and external side effects are blocked by default.
- Results are compared against a baseline with recorded examples.
- License, dependencies, memory/compute needs, and free-tier limits are documented.
- A rollback path exists.
- No claim of improved performance unless measured test results support it.

## Approval and payment safeguards

- No account creation, ID/liveness checks, human qualification tests, voice recording, paid-platform task submission, client outreach, publishing, purchase, payment, payout-setting changes, or deployment without the user's explicit approval and required human participation.
- Never bypass CAPTCHA, fake reviews, fabricate qualifications, or claim interest/results that have not been verified.
- Keep the first-payment ledger at ₹0 until the user confirms actual credit in their own payment app.

## Source links

- smolagents: https://github.com/huggingface/smolagents
- LangGraph: https://github.com/langchain-ai/langgraph
- Agno: https://github.com/agno-agi/agno
- CrewAI: https://github.com/crewAIInc/crewAI
- OpenHands: https://github.com/OpenHands/OpenHands
- Ollama: https://github.com/ollama/ollama
- GitHub Actions usage/billing docs: https://docs.github.com/en/billing/concepts/product-billing/github-actions
