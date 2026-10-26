# Device-Adaptive Router MVP

## What is now present on the feature branch
- `agents/adaptive_factory.py` classifies a small set of task categories and returns a device-aware route recommendation from caller-declared capabilities.
- The router prefers deterministic handling for simple validation/parse tasks; local model profiles are candidates only when a local runtime is declared available and memory appears sufficient.
- Audio/vision requests remain blocked until a specialist model/runtime is explicitly configured.
- Remote inference is never called. Even when `allow_remote=True`, the result says approval/configuration are required and `remote_used` remains false.
- `draft_agent_spec(...)` creates a JSON-like agent specification for review, with a version, required tests, explicit safe tool allowlist, and public-action/payment permissions disabled.
- `tests/test_adaptive_factory.py` covers the core routing and agent-spec safety behavior.

## Run and verify locally
From the repository root:
```bash
python -m unittest tests.test_adaptive_factory -v
python -m unittest discover -s tests -v
```

Example route recommendation:
```python
from agents.adaptive_factory import recommend_execution
print(recommend_execution(
    'summarize a document',
    {'free_ram_gb': 6, 'free_vram_gb': 0, 'local_runtime_available': True},
))
```

Device capabilities must be collected with user permission and supplied explicitly. This module does not inspect or fingerprint a device, install packages/models, execute an LLM, generate model weights, run a scheduler, or create a production agent automatically.

## Next implementation gates
1. Run the tests in CI and record the actual result.
2. Add a versioned model-profile registry with real model IDs, licenses, hardware requirements and benchmark evidence.
3. Add optional local-runtime adapters (initially one runtime) that are explicitly configured and never silently fall back to paid endpoints.
4. Add evaluation fixtures and memory/latency measurements on supported device classes.
5. Integrate with the existing task runtime only after compatibility and regression tests pass.
6. Keep generated agent specifications in draft state until schema, quality, privacy, prompt-injection, and permission tests pass; require review before enabling external actions.

## Honest cost statement
Local inference can reduce per-call API spend, but cannot guarantee zero total cost. Hardware, power, storage, bandwidth, maintenance and support remain costs. Do not advertise 100% free compute unless actual measured operating conditions substantiate the exact claim.