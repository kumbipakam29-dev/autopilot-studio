# AutoPilot Studio: zero-budget LLM setup

## Current integration status

The Python adapter in `agents/llm_router.py` calls an OpenAI-compatible chat-completions endpoint. It is real inference plumbing, but it is not itself an autonomous browser or coding agent. Model responses are returned as text; tool calls and external actions are not executed.

## Default: local Qwen3 4B with Ollama

Install Ollama on a machine you control, then run:

```bash
ollama pull qwen3:4b
ollama serve
python -m agents.llm_router --prompt "Create a 3-step test plan for a Python utility."
```

The adapter defaults to `http://127.0.0.1:11434/v1` and model `qwen3:4b`. The model download is free, but local inference uses your device's storage, RAM and compute. It does not run inside GitHub automatically and does not make your Android APK a model host.

## Optional remote free-tier API

Only use a provider after checking its current free quota, privacy terms, region availability and model licence. Hugging Face Inference Providers documents a limited monthly free credit for free accounts; it is not unlimited and can change.

Set these as environment variables or repository Actions secrets (never commit keys):
- `AUTOPILOT_ALLOW_REMOTE_LLM=true`
- `AUTOPILOT_LLM_BASE_URL=https://<provider-openai-compatible-base-url>/v1`
- `AUTOPILOT_LLM_MODEL=<provider-model-id>`
- `AUTOPILOT_LLM_API_KEY=<secret>`

The remote endpoint is rejected unless explicit opt-in and an API key are present. The adapter never silently switches to a paid provider. If the free quota runs out, the request fails instead of authorizing a purchase.

## Variables

| Variable | Default | Purpose |
|---|---|---|
| `AUTOPILOT_LLM_BASE_URL` | `http://127.0.0.1:11434/v1` | Local or explicitly opted-in endpoint |
| `AUTOPILOT_LLM_MODEL` | `qwen3:4b` | Model identifier |
| `AUTOPILOT_LLM_API_KEY` | empty | Secret for remote API, if needed |
| `AUTOPILOT_ALLOW_REMOTE_LLM` | `false` | Explicit remote inference gate |
| `AUTOPILOT_LLM_TIMEOUT_SECONDS` | `45` | Request timeout |

## Current limitations

- No browser automation, file editing, shell execution, publishing, outreach, or payments are executed by model output.
- The model can be wrong; outputs need tests and human review.
- The existing 15 specialist handlers remain deterministic until explicitly migrated and evaluated against model-backed tasks.
- Do not expose an Ollama port to the public internet without authentication and network controls.
