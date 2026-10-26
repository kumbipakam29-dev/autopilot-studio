# Integrated Agent Factory and Device-Aware Router

## Purpose
The integrated pipeline combines the existing draft-only agent factory with the
versioned model profile catalog. It creates an agent specification plus a route
recommendation for review; it does not create a running worker.

## Flow
1. Validate the requested task and draft the agent spec with a restricted tool allowlist.
2. Map the requested task to a declared profile task type.
3. Select the cheapest compatible profile from `agents/model_profiles.json`.
4. Treat only caller-supplied, installed-and-smoke-tested profile IDs as available.
5. Mark the package review-ready only when the selected profile is actually declared ready.
6. Keep all execution and external actions disabled; require evaluation and human review.

## Status meanings
- `draft_ready_for_human_review`: a route exists using a profile declared available; this is not a claim that an agent ran.
- `draft_blocked_on_model_setup_or_task_support`: no verified profile is ready, or the task is not in the catalog.
- `setup_required`: profile is only a candidate and runtime/model weights still need separate setup and smoke tests.
- `unsupported`: no catalog profile declares the mapped task. The router must not silently switch to a paid/remote provider.

## Safety and cost controls
- No model weights are bundled or installed by this code.
- No hardware probing is performed; device details must be supplied by the caller with consent.
- Remote inference remains a candidate only and is not called.
- Agent publishing, outbound messages, account changes, and payments remain disabled.
- Model profile memory limits are initial heuristics, not guarantees; benchmark quality, latency, memory, license, and privacy before release.

## Tests
Run:
```sh
python -m unittest discover -s tests -p 'test_adaptive_factory.py' -v
python -m unittest discover -s tests -p 'test_device_adaptive_router.py' -v
python -m unittest discover -s tests -p 'test_integrated_agent_router.py' -v
```
