# Agent Factory + Device Router Integration

Status: implemented as a recommendation bridge; no local model weights are bundled and no model is launched.

## Components

- `agents/device_adaptive_router.py` owns the versioned model-profile catalog selection logic.
- `agents/model_profiles.json` lists candidate profiles, rough resource thresholds, task labels, and installation requirements.
- `agents/adaptive_factory.py` exposes `recommend_agent_profile(...)` as the bridge used by agent-spec workflows.
- `tests/test_adaptive_factory.py` tests the bridge, setup-required behavior, explicit installed-profile selection, and unsupported tasks.

## Safe call example

```python
from agents.adaptive_factory import recommend_agent_profile

route = recommend_agent_profile(
    task_type="summarization",
    device={"ram_gb": 12, "vram_gb": 0},  # caller-provided after consent
)
print(route)
```

Expected meaning: a compatible small-model profile may be recommended, but its status remains `setup_required` unless the caller explicitly supplies a profile that is actually installed and smoke-tested. Memory thresholds are heuristics, not guarantees.

## Installed-profile declaration

Pass `installed_profiles` only after verifying the runtime and model weights are installed and a smoke test passed. A profile marked ready means only that the caller supplied that verification; the router itself does not inspect the machine or execute inference.

## Safety and cost rules

- The default available profile is the deterministic `rules-engine` only.
- Unknown task types return `unsupported`; they are not silently routed to a remote provider.
- Remote inference is never called by this bridge. `allow_remote` does not grant permission to spend or send data; any future remote adapter requires separate provider configuration, privacy review, and explicit cost approval.
- Agent specs remain drafts. Public publishing, outbound messaging, payments, and account changes remain disabled.
- A registered agent or profile is not evidence that an agent is running, a model is installed, or a task was completed.

## Validation

Run from the repository root:

```sh
python -m unittest tests.test_adaptive_factory tests.test_device_adaptive_router
python agents/device_adaptive_router.py --task summarization --ram-gb 12
```

A passing test suite validates routing logic only; it does not validate model quality, runtime performance, hardware compatibility, or revenue.
