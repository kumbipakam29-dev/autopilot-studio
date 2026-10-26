# Honest local agent runtime status

AutoPilot Studio has a large agent catalogue, but catalogue entries are not persistent workers. Use the local runtime command to inspect the registry and the most recent run ledger.

## Run the status command

From the repository root, with Python available:

```bash
python scripts/run_agent.py status
```

The command prints JSON with:

- `registered`: total agent IDs in `agents/registry.json`.
- `implemented_handlers`: registered IDs that have a deterministic handler in `agents/runtime.py`.
- `catalogued_but_unimplemented`: registered IDs that do not have a handler in that runtime.
- `planned`, `ready`, `running`, `blocked`, and `failed`: registry execution-status labels, not proof of a live process.
- `recent_runs`: the last records found in the local SQLite run ledger, if that file exists.

The implemented-handler count does not mean every handler has been executed successfully. For execution evidence, inspect the individual run's status and result. A `completed` status means the local handler returned a result; it does not mean an external action happened or a customer received content.

## Run a deterministic draft handler

For example, to draft a short Reel script without publishing it:

```bash
python scripts/run_agent.py run --agent-id APS-SOCIAL-GROWTH-364 --task "draft reel script" --inputs-json '{"topic":"introduce our cafe"}'
```

The output is a local draft and requires human review. The runtime does not publish the content or contact customers.

## Safety boundaries

- Unknown or unimplemented agent IDs should remain blocked.
- Sensitive tasks such as publishing, sending messages, payments, deployment or deletion require approval; the approval record is not execution.
- A model label in the registry does not prove that a local LLM is installed or that inference occurred.
- A registry entry, CI pass, generated draft, lead, application, invoice, or dashboard estimate is not revenue.
- Confirm any payment in the actual receiving account before marking it paid.

## Current implementation scope

The runtime currently has a small set of deterministic handlers. The larger registry is a catalogue for planned capabilities, not 500 always-on AI workers. Add handlers one at a time with tests and explicit evidence before changing their status.
