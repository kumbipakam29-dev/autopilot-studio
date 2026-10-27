# GitHub Upstream Agent Sources

This file tracks public GitHub projects for learning and carefully adapting agent patterns into AutoPilot-Studio. These are upstream projects, not 10 ready-to-run bots that can simply be copied into this repository.

## Sources and pinned revisions

### smolagents
- Repository: https://github.com/huggingface/smolagents
- License: Apache-2.0
- Reviewed commit: [96f33faaf028](https://github.com/huggingface/smolagents/commit/96f33faaf028479119ec8d34507b47694cf14e34)
- Useful patterns: minimal tool-calling loop; model-provider abstraction; agent tests
- AutoPilot use: read-only research prototype; evidence grader
- Adoption: first candidate after existing CI is green

### LangGraph
- Repository: https://github.com/langchain-ai/langgraph
- License: MIT
- Reviewed commit: [858891aaa164](https://github.com/langchain-ai/langgraph/commit/858891aaa164ebdacf33b8f5e7f88b38b9132211)
- Useful patterns: explicit state graph; checkpoint and resume; human-in-the-loop
- AutoPilot use: task router; approval workflow; long-running state
- Adoption: evaluate only if current workflow needs graph state

### Agno
- Repository: https://github.com/agno-agi/agno
- License: Apache-2.0
- Reviewed commit: [ffe47567920e](https://github.com/agno-agi/agno/commit/ffe47567920e5a5c5d5d416c2b366f8c32c62f31)
- Useful patterns: agent/team abstractions; structured outputs; evaluation patterns
- AutoPilot use: team orchestration prototype; knowledge/research workflow
- Adoption: compare against simpler native Python baseline

### CrewAI
- Repository: https://github.com/crewAIInc/crewAI
- License: MIT
- Reviewed commit: [bb4d892e684e](https://github.com/crewAIInc/crewAI/commit/bb4d892e684e9289422e816b8769e7976fdd451a)
- Useful patterns: role and task definitions; handoff patterns; task-level acceptance criteria
- AutoPilot use: role-based research/content team
- Adoption: study examples; don't run a large crew without measured need

### OpenHands
- Repository: https://github.com/OpenHands/OpenHands
- License: MIT
- Reviewed commit: [311dc1be6375](https://github.com/OpenHands/OpenHands/commit/311dc1be63758e51d61e43d6574d5c03c7a30688)
- Useful patterns: software-agent loop; test-driven iteration; sandbox boundary patterns
- AutoPilot use: coding-agent patterns; CI diagnosis research
- Adoption: study architecture only; never grant unrestricted repo/shell access

### Ollama
- Repository: https://github.com/ollama/ollama
- License: MIT
- Reviewed commit: [8ec9ecdf692e](https://github.com/ollama/ollama/commit/8ec9ecdf692e417798169ff8d5972159078d3754)
- Useful patterns: local model serving; model identity/version pinning
- AutoPilot use: local model runtime option
- Adoption: not installed; first verify machine OS, RAM, disk and hardware

### Pydantic AI
- Repository: https://github.com/pydantic/pydantic-ai
- License: MIT
- Reviewed commit: [eb53455eda57](https://github.com/pydantic/pydantic-ai/commit/eb53455eda571bf27b4974e54f9a539826dc6673)
- Useful patterns: typed input/output; validation and retries; dependency injection
- AutoPilot use: typed extraction; validated JSON outputs
- Adoption: consider for source extraction or registry outputs

### Microsoft Agent Framework
- Repository: https://github.com/microsoft/agent-framework
- License: MIT
- Reviewed commit: [1168c001dd22](https://github.com/microsoft/agent-framework/commit/1168c001dd228d6c7a623fd14f53e1f05b7b4540)
- Useful patterns: workflow abstractions; agent orchestration patterns
- AutoPilot use: workflow orchestration comparison
- Adoption: compare dependencies and Python compatibility before use

### Langflow
- Repository: https://github.com/langflow-ai/langflow
- License: MIT
- Reviewed commit: [aeb10d96bb2e](https://github.com/langflow-ai/langflow/commit/aeb10d96bb2ea797696613af931e91ddf51f3320)
- Useful patterns: visual workflow design; component composition
- AutoPilot use: visual workflow prototyping
- Adoption: optional; likely too heavy until core tests pass

### AutoGen
- Repository: https://github.com/microsoft/autogen
- License: mixed repository metadata; verify code/docs subfolder licenses before reuse
- Reviewed commit: [004749e6b710](https://github.com/microsoft/autogen/commit/004749e6b7102c8fd317b9b1499ce5807223c278)
- Useful patterns: agent communication patterns; human proxy patterns
- AutoPilot use: multi-agent conversation research
- Adoption: research-only until maintenance direction and component license are checked


## Safe adoption plan

1. Repair or diagnose existing offline CI failures before importing dependencies.
2. Prototype one read-only smolagents adapter using deterministic fake-model tests.
3. Benchmark it against the existing Python Earnings Hunter and Source Verifier on the same fixtures.
4. Reject the adapter if quality, security, runtime, dependency size or zero-budget requirements are worse.
5. Only then consider an optional pinned dependency; preserve native Python fallback and rollback.

## Rules

- Pin commit SHAs and check licenses, dependencies, maintenance status and security before reuse.
- Do not copy whole repositories into the project without a clear need and license review.
- No paid API keys or subscriptions by default.
- Tests must run offline with deterministic mocks.
- Start with read-only tools; no unrestricted shell, arbitrary network, publishing, account actions, or repo writes.
- Record each adapted source, source commit, license, local adaptation commit and test result.
- Learning means reviewed adaptations and regression fixtures; it does not mean the upstream model's weights are being trained.
- Upstream commit SHAs are snapshots at the time this catalog was generated; verify again before adoption.
