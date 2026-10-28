# Model Factory & Agent Evolution Layer

## What this adds
- Small-model catalog and task-to-model routing suggestions.
- Versioned specialist registry for reels/video scripts, social posts, poster briefs, app/code drafts, billing design, research summaries, and structured extraction.
- Deterministic score gate comparing candidate agent configurations with a baseline.
- Semantic-version proposals and explicit human review before promotion.

## Boundaries
- This versions agent configurations, prompts, and skills. It does not create new foundation-model weights or fine-tune a model.
- Scores depend on supplied review rubrics and regression evidence; the evaluator cannot independently establish truth.
- A candidate may be marked approved for manual promotion, but this module does not write registry files or deploy code.
- Catalog entries are suggestions; models are not confirmed installed, available on the current hardware, or benchmarked in this repository.
- Poster briefs and image prompts are text tasks; final images need a separate image-generation engine.
- Billing work is limited to design, invoice/ledger drafts, and sandbox specifications until integrations are reviewed. No real charges or financial settings are changed.

## Model setup
The current agents/llm_router.py defaults to local Ollama at 127.0.0.1:11434 with qwen3:4b. The router must run on the same machine as the caller; GitHub Actions and Android do not automatically inherit local Ollama.

Install only one model at a time after checking disk and RAM:
- ollama pull qwen3:0.6b
- ollama pull qwen3:1.7b
- ollama pull qwen3:4b
- ollama pull qwen2.5-coder:1.5b

Set AUTOPILOT_LLM_MODEL to the exact installed model tag. Do not download every model by default.

## Candidate scoring and versioning
1. Run baseline and candidate on the same versioned task set.
2. Score task success, evidence/factuality, safety/permissions, format/completeness, reproducibility.
3. Require named regression checks, all passing.
4. Reject hard-fail flags and any safety-score drop.
5. Candidate score must strictly exceed baseline.
6. Human approval is required, followed by a separate manual registry change.

Store baseline/candidate outputs, prompt/config diff, model tag, task-set version, scores, regression results, reviewer identity, and approval record together.

## Learning loop
Collect reviewed examples with consent; remove secrets and unnecessary personal data; version the evaluation set; propose prompt/skill/config changes first; compare baseline and candidate; reject regressions; require human approval. Fine-tuning such as LoRA/QLoRA is a separate future experiment requiring clean licensed data and compute.

## Free-tier warning
Remote inference is not guaranteed free or unlimited. Hugging Face currently documents a small monthly free credit allowance and pay-as-you-go beyond that; remote calls remain opt-in. See https://huggingface.co/docs/inference-providers/pricing. Local inference avoids API fees but uses device memory, storage, battery and CPU/GPU.
