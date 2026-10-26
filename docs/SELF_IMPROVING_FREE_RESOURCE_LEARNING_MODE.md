# AutoPilot Digital Studio — Free-Resource Learning Mode

## Purpose

Build a zero-budget, portable agent system that discovers public learning resources, studies documented tool capabilities, proposes useful workflows, tests them, records evidence, and improves its own code through reviewable changes.

**Important:** “Learning mode” is a controlled engineering loop, not a claim that agents are conscious, continuously running, or able to learn from every website automatically. A workflow runs only when its runtime/scheduler is available. Model training is not implied by updating prompts, documentation, or code.

## Operating principles

1. **Zero-budget first:** prioritize open-source software, official documentation, public examples, free tiers, local models where hardware permits, and GitHub-hosted source control/CI within current quotas.
2. **Portable by default:** keep source, configuration examples, tests, data schemas, and deployment instructions in this repository. Avoid requiring a single proprietary host or paid API.
3. **Evidence before adoption:** record the official source URL, checked date, license, requirements, free-tier limits, privacy implications, and a reproducible test for every tool evaluated.
4. **No invented capabilities:** distinguish documented capability, locally tested capability, prototype, and unavailable/untested capability.
5. **No secret collection:** never commit passwords, tokens, API keys, private user data, or unredacted logs. Use environment variables/secrets only when needed and approved.
6. **Quality over volume:** no mass-generated thin pages, fake engagement, spam, scraping that violates site rules, or unsolicited bulk outreach. Respect robots/terms, rate limits, attribution, copyright, and platform policies.
7. **Human approval gates:** public publishing, external messages, purchases, paid services, identity checks, payment/bank actions, permission changes, merges, deployments, destructive changes, and legal declarations require explicit authorization.
8. **No earnings claims without evidence:** separate opportunity discovery, account registration, accepted task, approved work, and verified payment.

## The learning loop

1. **Discover:** find a tool or skill from official documentation, a repository, release notes, or a trusted public tutorial.
2. **Triage:** check project activity, license, dependencies, hardware requirements, data handling, security notes, and whether it can genuinely run for free.
3. **Create a tool card:** describe purpose, inputs/outputs, setup, limitations, alternatives, last-checked date, and source links.
4. **Build a minimal experiment:** use synthetic/sample data or a sandbox. Keep the experiment small, reversible, and within free quotas.
5. **Evaluate:** add automated tests, expected-output checks, quality metrics, failure cases, and resource/latency measurements where feasible.
6. **Record the result:** mark statuses as documented, prototype, locally tested, CI tested, needs review, or blocked. Never upgrade status without evidence.
7. **Propose an improvement:** prepare a small code/doc change on a feature branch and include tests plus a rollback note.
8. **Review and release:** inspect CI and the diff; request approval before merge/deploy or external action.
9. **Revisit:** check links, licenses, versions, tool health, and free-tier limits on a schedule only when a functioning scheduler is configured.

## Suggested departments

- **Research & Source Verification:** official docs, changelogs, trend sources, citations, freshness.
- **Website & Documentation:** static-first pages, accessible layouts, source-controlled content, portable builds.
- **Content Studio:** original blog drafts, captions, carousel concepts, scripts, and editorial calendars.
- **Media Lab:** image/audio/video workflow experiments; verify model and hardware requirements before claiming free generation.
- **Agent & Workflow Engineering:** tool adapters, task router, local ledger, queue, retries, idempotency, and error handling.
- **Quality & Safety:** tests, source checks, duplication checks, privacy, license review, human approval gates.
- **Opportunity Research:** public opportunities and eligibility; no guarantee of acceptance, tasks, or income.
- **Operations & Reporting:** task status, resource use, failures, verified outputs, next actions.

A department name or registry entry does not mean a separate live worker exists. The registry should report what is implemented and runnable.

## Tool evaluation card

For every proposed tool, record:

- Name and official repository/docs URL
- What problem it solves and the exact workflow proposed
- License and whether commercial use is allowed
- Dependencies, OS, RAM/VRAM, storage, and network requirements
- Whether it needs a paid API, cloud account, GPU, or external service
- Free-tier quotas and date checked
- Data sent to third parties and privacy/security concerns
- Small reproducible test, expected result, actual result, logs/artifacts
- Known limitations and fallback option
- Status and last verified date

## Minimum architecture

- **Registry:** machine-readable list of tools/agents, versions, capabilities, dependencies, status, and evidence.
- **Task queue:** pending/running/succeeded/failed/blocked/review-required states, with bounded retries.
- **Run ledger:** local or portable records of task inputs, output paths, timestamps, status, and error summaries; avoid sensitive data.
- **Resource library:** deduplicated source links, license notes, tool cards, and versioned learning notes.
- **Evaluation suite:** unit tests, integration tests using mocks/samples, output quality checks, and security checks.
- **Approval queue:** explicit gates for consequential or public actions.
- **Scheduler:** optional and disabled/unverified until a free runner or local scheduler is configured and tested.
- **Dashboard:** show actual state, last run, evidence, blockers, resource cost, and approval needs.

## First milestones

### Milestone 1 — Inventory
List existing scripts, agents, workflows, dependencies, and documentation. Label each item as implemented, prototype, untested, blocked, or planned.

### Milestone 2 — Free tool catalog
Create a small curated catalog for website building, research, writing, image generation, local text-to-speech, audio, video editing, automation, and testing. Prefer official project sources; do not assume all media generation is practical on a phone or free cloud runner.

### Milestone 3 — Testable content pipeline
Input a topic and target audience; produce a cited research brief, original draft, short-video script, caption variants, and quality report. Export files only; publishing stays approval-gated.

### Milestone 4 — Media pipeline experiments
Test one tool at a time with legal sample assets. Measure whether it works on available hardware and identify any paid dependencies before integration.

### Milestone 5 — Improvement loop
Run tests, compare outputs against defined checks, propose a small branch change, and report the diff and CI status. Do not self-merge or self-deploy.

### Milestone 6 — Reliable scheduling
Only after the workflow passes tests, configure a free/local schedule and verify an actual run. Document quotas, failure alerts, manual fallback, and how to disable it.

## Success metrics

- Reproducible tests passed / total tests
- Percentage of tool cards with official sources and license checks
- Freshness of source records
- Duplicate/unsupported claim rate in content drafts
- Successful runs / attempted runs
- Average runtime and compute/storage use
- Number of changes with tests and rollback notes
- Count of public actions completed only after approval
- Verified accepted work and verified payments, tracked separately from leads or advertised rates

## Current status template

For each component report: **Status**, **Evidence**, **Last verified**, **Cost**, **Blocker**, **Next test**. If there is no test evidence, say “untested”; do not infer success from a prompt, commit, or workflow definition.
