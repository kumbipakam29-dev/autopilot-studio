# Device-Adaptive Models and Self-Improving Agent Factory

Status: architecture proposal. This document describes intended design, not an implemented or deployed feature. Device probing, model generation, agent generation, local inference, and billing behavior must each be implemented and tested before being called live.

## Product goal
Build AutoPilot Studio as a low-cost AI service platform that selects or assembles the smallest capable model/agent for a user's task and available device. Reuse tested components and improve them through measured experiments. Keep the service affordable by moving eligible computation to user-controlled devices and by routing other work to efficient shared infrastructure where available.

## Critical cost principle
100% free compute cannot be guaranteed. Local inference may reduce provider GPU/API charges, but hardware ownership, electricity, bandwidth, storage, maintenance, and support still cost someone something. Free cloud quotas can change, expire, or impose limits. Product claims must describe actual measured costs and limits rather than promise zero cost.

## Request and device-adaptive flow
1. Receive the task and classify its capability, complexity, privacy sensitivity, latency needs, and risk.
2. Ask permission before collecting device capability information. Collect the minimum necessary: operating system, available RAM/VRAM if safely obtainable, CPU/GPU class, storage, supported runtimes, network availability, and user consent. Do not fingerprint a device or collect unrelated identifiers.
3. Match the task to a capability-tested profile: deterministic script, classical ML, small local LLM, larger local model, or optional remote provider only if explicitly configured and approved.
4. Check model and dependency compatibility, code/weight/data licenses, context length, memory requirements, and expected runtime. Never assume a model is commercially usable just because its weights can be downloaded.
5. Offer an existing tested model/agent first. Prefer configuration, prompt/tool composition, retrieval, quantization, or adapter-based tuning where appropriate over training a new foundation model from scratch.
6. Run a small local benchmark and schema/safety tests. If the device cannot run the workload, downshift to a smaller model, split the task, use an approved remote route, or explain the limitation.
7. Record the result and cost evidence. Do not describe the profile as supported until the relevant test passes.

## Model versioning strategy
Use a registry with immutable versions and explicit capability profiles, for example summarizer-small version 1.2.0 or local-code-helper-q4 version 0.3.0. Each version should record:
- model/repository ID and exact revision or weight hash;
- code, model-weight, dataset, and dependency licenses separately;
- target device profile and memory requirements;
- supported tasks, languages, context limits, and known weaknesses;
- benchmark dataset/version, scores, latency, memory and failure rates;
- safety checks, privacy behavior, and external network behavior;
- parent version, change rationale, release status, rollback target, and approval record.

A user request should select a compatible tested version, not automatically create new model weights every time. Generate a new model version only when a measured need justifies it and the compute/data/license budget is known.

## Agent factory and versioning
Agents are versioned task packages, not necessarily separate neural models. Each agent definition includes:
- purpose, input/output schema, allowed tools, and explicit permission scope;
- model profile, prompts/instructions, retrieval sources, and deterministic code;
- time/resource budget, retry limits, and safe failure behavior;
- test fixtures, expected outcomes, quality threshold, and owner/reviewer;
- version, parent version, change log, evaluation results, and rollback plan.

When a task cannot be handled reliably by existing agents, the factory may propose a new agent composition from tested components. It must run offline/sandbox tests and evaluation before being marked tested. New agents start with least privilege, no credentials by default, no public posting or external messages by default, and no access to payment settings. Changes to permissions require review.

## Learning and improvement loop
Collect allowed, privacy-respecting, minimal task feedback → identify recurring failures → create a reproducible test → compare candidate prompts/tools/models → propose a version on a feature branch → run automated tests and safety evaluation → require approval for meaningful behavior or permission changes → release with rollback → monitor measured outcomes.

Do not train on customer data without clear authorization and appropriate retention/deletion controls. Prefer synthetic or public appropriately licensed evaluation examples. Do not copy proprietary models or scrape restricted datasets.

## Routing policy
- Tier 0: deterministic local code for parsing, arithmetic, validation, file transforms and known workflows.
- Tier 1: classical ML/NLP or small local model for lightweight tasks.
- Tier 2: larger compatible local model for complex language/code/reasoning tasks.
- Tier 3: optional remote inference only when enabled, with transparent cost/privacy settings and user approval.
- If quality or device capacity is insufficient, stop safely or request review instead of silently routing to a paid service.

## Cost model and customer promise
Track per task: local vs remote execution, API spend, measured compute time, storage, data transfer where measurable, retries, human review time, and support overhead. Distinguish marginal cash cost from total operating cost. Offer lower-cost tiers based on measured workload and capacity; do not promise free forever or claim zero cost without evidence.

## Release gates
Before a model or agent is marked production-ready:
1. License and provenance reviewed.
2. Device compatibility test passes on the declared profile.
3. Task quality meets a defined threshold on held-out tests.
4. Safety, privacy, injection, permission and data-exfiltration tests pass.
5. Cost/latency/memory have been measured.
6. Version metadata and rollback path exist.
7. Human approval is recorded for releases with material behavioral changes.

## Current implementation status
Architecture proposal only. This document alone does not install models, inspect user devices, create model weights, generate live agents, run background learning, or guarantee free computation. Those features require implementation, actual runtime/device access, reproducible tests, and verified scheduling.