# 500-agent registry, versioning, and rollout

## Registry status
`agents/registry.json` contains 500 unique IDs covering all 150 supplied idea roles, three market/niche variants per role (450 entries), and 50 seasonal specializations. IDs are stable catalog identifiers. `registry_status=registered` means only that the record exists. All initial `execution_status=planned`; this does not claim 500 workers are running.

## IDs and versions
- Stable ID: `APS-<DEPARTMENT>-<NNN>`; seasonal entries use `APS-SEASONAL-<NNN>`.
- Agent semantic version: MAJOR for incompatible role/contract changes, MINOR for backwards-compatible capabilities, PATCH for fixes/metadata corrections.
- Model version: explicit provider/model/version string where a real model is configured. Initial `rules-engine@1.0` means deterministic templates/rules, not an LLM and not a paid API.
- Change a version only with a corresponding commit, test, and changelog entry. Do not silently overwrite model identity.
- Statuses: `planned`, `ready`, `running`, `blocked`, `failed`. `running` must have run evidence/ID; a registry entry alone is never evidence of execution.

## Runtime architecture
1. Registry: source of truth in JSON, version-controlled.
2. Router: selects an agent by ID/capability and validates the request.
3. Executor: runs only implemented, tested handlers; unknown capabilities return `blocked`, never pretend success.
4. Run ledger: records run ID, timestamps, code commit, agent/model versions, outcome, and redacted logs.
5. Approval queue: any public publishing, DM/email, purchases/payments, account/security changes, deletion, application submission, or financial execution waits for explicit human approval.
6. Dashboard: displays registered, ready, running, blocked, failed counts separately; no fabricated live status.

## ₹0 operating constraints
- Start with Python standard library and GitHub Actions; public CI minutes and quotas are limited and can change. Avoid one workflow per agent; batch catalog validation and only run relevant tasks.
- Do not assume free hosting is persistent or always-on. Keep credentials in repository secrets only after explicit approval; never commit secrets.
- Model calls are not implied by a model label. If no local model/runtime or authorized endpoint is configured, use rules-based handlers or mark the agent blocked.
- No scraping that violates terms, access controls, rate limits, or privacy rules. Use official/public feeds where permitted, respect robots/terms, and prefer opt-in/aggregated data.
- Copyright/trademark review required for designs, quotes, clips, stock assets, and marketplace uploads. Never republish Reddit posts or other people's content without rights/permission.
- Finance/crypto agents are informational only: no trading, custody, investment guarantees, or wallet actions.
- Email lists are not products to resell unless lawful consent and licensing are documented. Do not sell personal data.
- SEO pages must be useful and original, not mass-generated doorway or thin affiliate pages. Ad/affiliate revenue requires eligibility and disclosure.
- Revenue fields describe potential revenue models, not verified income.

## Validation
Run:
```bash
python scripts/validate_agent_registry.py
python -m unittest discover -s tests
```

## Rollout sequence
1. Validate the registry and schemas.
2. Implement a small number of safe deterministic agents with tests and run evidence.
3. Add a router and ledger; make unsupported integrations visibly blocked.
4. Add connectors one at a time with permissions, rate limits, and tests.
5. Keep public actions behind approvals.
6. Expand operational coverage based on measured task success, not the registered count.

## Current honest status
This commit adds a 500-record registry and validation tooling. It does not start 500 processes, connect marketplace accounts, scrape restricted sites, publish content, or guarantee sales/payments. Public deployment and PR merge remain separate decisions.
