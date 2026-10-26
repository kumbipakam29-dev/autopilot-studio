# Free-First AI, ML, NLP and Automation Resource Catalog

Status: planning/catalog baseline. A listed tool is a candidate, not proof it is installed, connected, or running in AutoPilot Studio. Re-check official docs, license, hardware requirements, and availability before each adoption.

## Non-negotiable resource policy

1. ₹0 first: prefer local execution, free tiers, public documentation, and permissively licensed open-source software.
2. No hidden costs: record hardware, storage, bandwidth, rate limits, account requirements, and free-tier expiry/quotas. Never start a paid trial or enter payment details without explicit approval.
3. License before use: “free to download” does not automatically mean open source or free for commercial use. Check the exact code, model-weight, dataset, and dependency licenses separately.
4. Evidence over hype: every tool/model gets a reproducible small test, date checked, official source, limitations, and status.
5. Route by task: use deterministic code for deterministic jobs; ML/NLP for structured analysis; LLMs for language/reasoning tasks; combine tools only when tests show benefit.
6. No fake autonomy: catalog entries do not mean workers are live. Do not claim model training, deployment, outreach, publishing, or earnings without evidence.
7. Safe improvement: agents may propose changes on a feature branch and run tests; do not expose secrets, bypass access controls, publish, spend, or merge/deploy without required approval.

## Candidate toolbox by capability

| Capability | Free-first candidates | Typical uses | Caveats / evaluation |
|---|---|---|---|
| Workflow automation | Python, cron where a host supports it, GitHub Actions free allowance, Playwright | Scheduled scripts, repeatable workflows, browser testing | Hosted quotas and runner availability can change; never assume always-on scheduling |
| Local LLM inference | Ollama, llama.cpp, LM Studio | Chat, drafting, extraction, local agent tasks | Needs compatible hardware and disk/RAM; compare model license and output quality |
| LLM/model ecosystem | Hugging Face Transformers and model hub | Load, compare, run supported open-weight models | Each model has its own license, hardware needs and restrictions |
| ML / classical prediction | scikit-learn, pandas, NumPy | Classification, ranking, forecasting baselines, anomaly checks | Requires useful data and evaluation; do not train without a defined target |
| Deep learning / MLP | PyTorch | Neural networks, multilayer perceptrons, experiments | Training can be compute-intensive; start with small CPU-friendly tests |
| NLP | spaCy, NLTK, Transformers | Tokenization, entities, text classification, language tasks | Language coverage and model licenses vary |
| Embeddings / semantic search | Sentence Transformers; FAISS where suitable | Similarity, deduplication, retrieval, clustering | Embedding models also have individual licenses; evaluate retrieval quality |
| Retrieval / knowledge base | Local files + SQLite FTS; optional vector index | Search internal docs, evidence-linked answers | Keep source URLs, dates, and citations; avoid unsupported answers |
| Reasoning / planning | Small local instruction/reasoning models; explicit Python planners and checklists | Multi-step task plans, decomposition, verification | “Deep thinking” is not guaranteed; benchmark correctness, latency and resource use |
| Computer vision / media | OpenCV; selected Hugging Face models; FFmpeg | Image/video processing, resizing, quality checks | Check model/data licenses and CPU/GPU needs |
| Speech / transcription | whisper.cpp or compatible local speech models | Transcription, audio processing | Language accuracy, compute, and model license vary |
| Testing / quality | pytest, Ruff, mypy where useful, Playwright, JSON Schema | Unit tests, linting, browser checks, output validation | A green test only proves the tested conditions passed |
| Data / ledger | SQLite, CSV, JSON, Python | Task queue, run ledger, tool registry, audit trail | Back up data; avoid storing credentials or unnecessary personal data |
| Packaging / reproducibility | Git, GitHub, Python virtual environments, pinned dependencies | Versioning, repeatable setup, rollback | Repository/CI access and free quotas may change |
| Workflow orchestration frameworks | Evaluate lightweight Python first; consider frameworks only if needed | Tool routing, agent graphs, retries | Extra dependencies can add complexity; review licenses before adopting |
| Automation platform caution | n8n is source-available under a Sustainable Use License, not OSI open source | Potential internal workflow experiments | Check commercial-use limits carefully before embedding it in a paid customer product |

## Minimum registry record for every resource

- Name and capability category
- Official project URL and documentation URL
- Resource type: code library / model weights / dataset / hosted service
- Exact version or model revision
- License for code, weights, and data (separate fields)
- Commercial-use permission checked: yes / no / unclear
- Cost: $0 local / free tier / quota-limited / paid / unknown
- Hardware, RAM/VRAM, disk and OS requirements
- Installation and reproducible smoke-test command
- Evaluation dataset or test cases and measured results
- Security/privacy notes and data sent externally
- Last checked date, status: proposed / reviewed / tested / adopted / blocked / retired
- Fallback tool and reason for selection

## Router policy

1. Classify task and risk.
2. Try deterministic/local/free solution first.
3. For language tasks, select an available model that fits hardware and task; do not call a paid API by default.
4. Validate output against schema, evidence, tests, duplication, and safety rules.
5. If quality is below threshold, try a different free candidate or return “needs review”; never invent certainty.
6. Log tool/version, elapsed time, resource usage when measurable, result, failures, and source evidence.
7. Re-test candidates periodically only when a real scheduler is configured and verified.

## Suggested implementation order

1. Add a machine-readable resource registry (JSON/YAML) and schema validation.
2. Add capability tags and license/cost/hardware fields.
3. Add small smoke tests and benchmark fixtures per capability.
4. Implement a Python router with deterministic fallbacks and explicit unavailable states.
5. Record every run in SQLite/JSONL with evidence and error details.
6. Add an evaluation report that compares candidates; no automatic adoption solely because a model claims to be better.
7. Only later add optional local model execution and verified scheduling, based on available hardware and quota.

## Initial official references

- Ollama API docs: https://docs.ollama.com/api
- llama.cpp: https://github.com/ggml-org/llama.cpp
- Hugging Face Transformers: https://huggingface.co/docs/transformers
- scikit-learn docs: https://scikit-learn.org/stable/
- PyTorch docs: https://docs.pytorch.org/docs/
- spaCy docs: https://spacy.io/usage
- Sentence Transformers docs: https://www.sbert.net/
- n8n license terms: https://github.com/n8n-io/n8n/blob/master/LICENSE.md

This document is a planning baseline. The tools are not represented as installed, tested, connected, or running until a separate verified test record says so.
