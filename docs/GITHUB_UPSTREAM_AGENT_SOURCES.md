# GitHub Upstream Agent Sources

This file tracks public GitHub projects for learning and carefully adapting agent patterns into AutoPilot-Studio. These are upstream projects, not 10 ready-to-run bots that can simply be copied into this repository.

## Sources and pinned revisions

### smolagents
- Repository: https://github.com/huggingface/smolagents
- License: Apache-2.0
- Reviewed commit: https://github.com/huggingface/smolagents/commit/96f33faaf028479119ec8d34507b47694cf14e34
- Useful patterns: minimal tool-calling loop; model-provider abstraction; agent tests
- AutoPilot use: read-only research prototype; evidence grader
- Adoption: first candidate; no third-party dependency installed yet

### LangGraph
- Repository: https://github.com/langchain-ai/langgraph
- License: MIT
- Reviewed commit: https://github.com/langchain-ai/langgraph/commit/858891aaa164ebdacf33b8f5e7f88b38b9132211
- Useful patterns: explicit state graph; checkpoint and resume; human-in-the-loop
- Adoption: evaluate only if current workflow needs graph state

### Agno
- Repository: https://github.com/agno-agi/agno
- License: Apache-2.0
- Reviewed commit: https://github.com/agno-agi/agno/commit/ffe47567920e5a5c5d5d416c2b366f8c32c62f31
- Useful patterns: agent/team abstractions; structured outputs; evaluation patterns
- Adoption: compare against simpler native Python baseline

### CrewAI
- Repository: https://github.com/crewAIInc/crewAI
- License: MIT
- Reviewed commit: https://github.com/crewAIInc/crewAI/commit/bb4d892e684e9289422e816b8769e7976fdd451a
- Useful patterns: role and task definitions; handoff patterns; task-level acceptance criteria
- Adoption: study examples; do not run a large crew without measured need

### OpenHands
- Repository: https://github.com/OpenHands/OpenHands
- License: MIT
- Reviewed commit: https://github.com/OpenHands/OpenHands/commit/311dc1be63758e51d61e43d6574d5c03c7a30688
- Useful patterns: software-agent loop; test-driven iteration; sandbox boundary patterns
- Adoption: architecture study only; never grant unrestricted repo/shell access

### Ollama
- Repository: https://github.com/ollama/ollama
- License: MIT
- Reviewed commit: https://github.com/ollama/ollama/commit/8ec9ecdf692e417798169ff8d5972159078d3754
- Useful patterns: local model serving; model identity/version pinning
- Adoption: not installed; first verify machine OS, RAM, disk and hardware

### Pydantic AI
- Repository: https://github.com/pydantic/pydantic-ai
- License: MIT
- Reviewed commit: https://github.com/pydantic/pydantic-ai/commit/eb53455eda571bf27b4974e54f9a539826dc6673
- Useful patterns: typed input/output; validation and retries; dependency injection

### Microsoft Agent Framework
- Repository: https://github.com/microsoft/agent-framework
- License: MIT
- Reviewed commit: https://github.com/microsoft/agent-framework/commit/1168c001dd228d6c7a623fd14f53e1f05b7b4540
- Useful patterns: workflow abstractions; agent orchestration patterns

### Langflow
- Repository: https://github.com/langflow-ai/langflow
- License: MIT
- Reviewed commit: https://github.com/langflow-ai/langflow/commit/aeb10d96bb2ea797696613af931e91ddf51f3320
- Useful patterns: visual workflow design; component composition
- Adoption: optional; likely too heavy until core tests pass

### AutoGen
- Repository: https://github.com/microsoft/autogen
- License: mixed repository metadata; verify code/docs subfolder licenses before reuse
- Reviewed commit: https://github.com/microsoft/autogen/commit/004749e6b7102c8fd317b9b1499ce5807223c278
- Useful patterns: agent communication patterns; human proxy patterns
- Adoption: research-only until maintenance direction and component license are checked

## What has now been implemented

- agents/evidence_grader.py is a standard-library-only deterministic grader inspired by read-only tool-boundary and structured-output principles studied in smolagents. It checks official HTTPS source, country eligibility, task-specific rate/unit or explicit not-stated, acceptance criteria, and payout details or explicit not-stated.
- tests/test_evidence_grader.py covers complete evidence, missing/unknown evidence, unsafe source URL, and invalid input.
- runtime/opportunity_tracker.py now marks a candidate needs_verification when eligibility or payment is unverified, even if descriptive text exists. Existing regression tests exposed this mismatch.
- This is a local pattern prototype, not the smolagents framework itself. No upstream package was installed; the grader requires no model API or network access.

## Adoption and validation status

1. Diagnose existing CI failures: done for two previously failing runs. Both fail on test_cli_writes_csv_and_never_removes_approval_gate, where payment_verified=false was incorrectly marked awaiting_user_approval. The code now conservatively assigns needs_verification.
2. Run the offline suite: pending confirmation from a fresh GitHub Actions run; do not mark tests green until the run reports success.
3. Prototype one read-only evidence grader: implemented with offline regression tests; test execution still pending.
4. Benchmark: pending. Compare against current Python baseline on the same fixtures before adding a framework dependency.
5. Framework dependency: not installed. Consider only if a measured benefit justifies the dependency and runtime cost.

## Rules

- Pin commit SHAs and check licenses, dependencies, maintenance status and security before reuse.
- Do not copy whole repositories into the project without a clear need and license review.
- No paid API keys or subscriptions by default.
- Tests must run offline with deterministic mocks.
- Start with read-only tools; no unrestricted shell, arbitrary network, publishing, account actions, or repo writes.
- Record each adapted source, source commit, license, local adaptation commit and test result.
- Learning means reviewed adaptations and regression fixtures; it does not mean upstream model weights are being trained.
- Upstream commit SHAs are snapshots at catalog generation; verify again before adoption.
