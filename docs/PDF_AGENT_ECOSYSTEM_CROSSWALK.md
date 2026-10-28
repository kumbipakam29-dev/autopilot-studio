# PDF Agent Ecosystem Crosswalk

Updated: 2026-10-28

## Purpose

This note maps the two uploaded PDF outlines to the existing AutoPilot Studio repository. It prevents the PDF examples from being mistaken for deployed agents and avoids rebuilding capabilities already present in the draft agent-system branch.

- [10-agent ecosystem PDF](../config/pdf_agent_ecosystem_crosswalk_v1.json)
- The first PDF's three roles map to Researcher, Writer, and Reviewer below.
- Registry entries, source code, and the latest GitHub Actions result provide the implementation evidence; PDF diagrams alone do not.

## Verified branch context

The current draft branch already contains a 100-agent *catalogue*, 15 deterministic offline specialist capability prototypes, a JSON CLI, an offline client-acquisition draft pipeline and unit tests. These are not 100 live agents or 15 model-backed agents. Model/API assignments remain unconfigured and external actions remain approval-gated.

The latest observed Specialist Capability Tests run for PR #56 completed with conclusion `success` before this crosswalk change. A new run is required to verify the new mapping test.

## Ten PDF roles — implementation reading

| PDF role | Current mapping | Status |
|---|---|---|
| Architect | Deterministic task routing and dependency mapping | Partial |
| Coder | No safe, tested general code-generation worker | Not implemented |
| Reviewer / PDF 1 Editor | Evidence and annotation checks; not a general code-security auditor | Partial |
| Researcher | Existing bounded opportunity researchers; source-verifier checks supplied snippets only | Partial |
| Writer | Offline content and client-acquisition draft pipeline | Partial |
| Analyst | Structured opportunity tracking and ledger reports | Partial |
| Communicator | Drafts only; no automatic sending or sentiment-aware live chat | Partial |
| Executor | Bounded local routing/logging, no arbitrary shell or external execution | Partial |
| Memory | Supervised evaluation loop; no ChromaDB semantic conversation memory | Partial |
| Orchestrator | Deterministic runner and bounded specialist pipeline; no installed LangGraph/CrewAI | Partial |

The machine-readable mapping contains the concrete repository paths, current behavior, gaps and safe next steps for every role.

## Why the example packages are not installed

The CrewAI PDF introduces an OpenAI API key and Serper search tool. The ten-agent PDF contains illustrative snippets, including explicit placeholders (for example, an unfinished JSON parser and fixed demo responses), incomplete error handling, and an unrestricted `shell=True` executor example. Those snippets are useful as architecture sketches, not as evidence of a working zero-cost production system.

This crosswalk therefore adds no dependencies, API secrets, network calls, new model downloads or automatic external actions. The existing offline pipeline is the lowest-risk first execution path.

## Safe implementation order

1. Keep the existing offline task runtime and versioned registry as the source of truth.
2. Add and run the crosswalk integrity test in GitHub Actions.
3. Add one capability at a time only when a concrete business task needs it; require inputs, outputs, expected evidence and regression tests.
4. Add live research only through bounded, attributable sources with timestamps.
5. Keep content, outreach, publishing, payment, account and deployment actions under explicit human approval.
6. Report `planned`, `implemented`, `tested`, `connected` and `live-verified` separately.

## Status honesty

A successful unit-test workflow means the tested code passed that workflow at that commit. It does not prove the app is installed on the user's phone, an external account is connected, a post was published, a client was contacted, or any sale/payment occurred.
