# Open-source tool catalog for AutoPilot Studio

This catalog turns the long community list into an install-first shortlist. It is a discovery index, not a claim that every project is key-free, easy to install, or suitable for every device.

## Ground rules

- Prefer local-first tools and public repositories with a clear license.
- Check each repository's current license, release activity, dependencies, hardware needs, and security notes before adopting it.
- "Open source" does not automatically mean zero-cost hosting, zero setup, or no account/API key.
- Public-APIs lists directories of APIs; individual APIs may require registration, keys, impose quotas, or have separate terms.
- Never put secrets in GitHub, workflow logs, client drafts, or public portal inputs.
- Keep publishing, outreach, payments, account changes, deployments, and destructive operations behind explicit human approval.
- Do not scrape private accounts or collect/sell personal data. Prefer official APIs and business-published contact channels; respect robots.txt, terms, rate limits, and opt-outs.

## Phase 1: low-complexity building blocks

| Need | Candidate | Repository | What it provides | Key caveat |
|---|---|---|---|---|
| Local model runtime | Ollama | https://github.com/ollama/ollama | Run supported models locally | Model download, disk/RAM requirements; not every model fits every machine |
| Lightweight inference | llama.cpp | https://github.com/ggml-org/llama.cpp | Local inference for supported quantized models | Setup and model compatibility still matter |
| Local task memory | SQLite | https://www.sqlite.org/ | Embedded local database | Back up data; not a shared multi-user server |
| Automation | n8n | https://github.com/n8n-io/n8n | Visual workflow automation | Self-hosting and workflow setup required; review license/usage terms |
| Browser automation/testing | Playwright | https://github.com/microsoft/playwright | Browser automation and tests | Use only on sites where access is permitted; browser binaries consume storage |
| Web article extraction | Trafilatura | https://github.com/adbar/trafilatura | Extract main text from pages | Respect site terms, robots rules, copyright, and rate limits |
| Image workflows | ComfyUI | https://github.com/comfyanonymous/ComfyUI | Node-based local image generation workflows | GPU/RAM and model storage can be substantial |
| Image editing/upscaling | Upscayl | https://github.com/upscayl/upscayl | Local image upscaling app | Device compatibility and model downloads |
| Voice transcription | Whisper | https://github.com/openai/whisper | Local speech-to-text | Model downloads and compute; review data consent |
| Audio/video processing | FFmpeg | https://github.com/FFmpeg/FFmpeg | Media conversion and processing | Codec licensing and command-line learning curve |
| Design | Penpot | https://github.com/penpot/penpot | Open-source design/prototyping platform | Self-hosting is more involved than using a hosted service |
| PDF tools | Stirling-PDF | https://github.com/Stirling-Tools/Stirling-PDF | Self-hosted PDF operations | Deployment/security configuration required |
| Monitoring | Uptime Kuma | https://github.com/louislam/uptime-kuma | Monitor service availability | Monitoring does not make a service always-on |
| Analytics | Umami | https://github.com/umami-software/umami | Privacy-oriented website analytics | Requires deployment and correct consent/privacy setup |

## Phase 2: optional frameworks to evaluate later

- Agent orchestration: https://github.com/langchain-ai/langgraph
- Agent framework: https://github.com/huggingface/smolagents
- Retrieval/indexing: https://github.com/run-llama/llama_index
- Vector database: https://github.com/chroma-core/chroma
- Self-hosted workflow alternative: https://github.com/activepieces/activepieces
- Local-first backend: https://github.com/pocketbase/pocketbase
- Search/API discovery directory: https://github.com/public-apis/public-apis
- Self-hosted software directory: https://github.com/awesome-selfhosted/awesome-selfhosted

Frameworks add complexity; adopt them only when a concrete task needs them. Avoid installing multiple tools that solve the same problem.

## AutoPilot Studio implementation order

1. Keep the existing registry, CLI router, SQLite run ledger, and test workflows as the system of record.
2. Add a deterministic prospect-research workflow that stores only business-level public facts, source URL, date checked, confidence, and a manual review status. No automated outreach.
3. Add a POD research workflow that produces niche hypotheses, original design briefs, and a human review checklist. No marketplace uploads.
4. Add local-model support as an optional backend, with deterministic fallback and clear model/version reporting.
5. Add scheduling only after idempotency, run limits, logs, and failure handling are tested.
6. Add a dashboard view over safe status summaries; do not expose the SQLite database or admin endpoints publicly without authentication and security review.

## Status vocabulary

- `catalogued`: listed for evaluation
- `configured`: dependencies and settings prepared
- `tested`: repeatable test passed
- `running`: process is currently executing
- `connected`: a real integration was authenticated and verified
- `published`: an external post/listing was verified live
- `paid`: payment receipt/transaction was verified

Do not infer one status from another. In particular, catalogued tools and registered agents are not running agents, and a prepared outreach draft is not a sent message or customer.
