# AutoPilot Studio — Deep Research, Gap Audit & Zero-Budget Roadmap

**Research snapshot:** 24 October 2026  
**Scope:** Existing GitHub repository, autonomous earning-agent design, open/local models, free tooling, India-relevant paid-work discovery, and a 1,200-item opportunity hypothesis bank.

## Executive finding

The repository is a useful **review-first prototype**, not yet an autonomous income system. Its strengths are: public-page discovery with conservative rate evidence, scheduled GitHub Actions jobs, offline unit tests, POD concept/listing-draft generation, and a mobile UI with a local earning/payout tracker. Its largest gaps are: discovery is limited to a curated source registry and a small number of same-site pages; outputs are GitHub artifacts rather than an app-connected, durable database; the UI's lead cards are a dated snapshot, not a live feed; and no task platform accounts, eligibility checks, work submission, acceptance callbacks, or payouts are integrated.

There is no honest way to guarantee a first payment, ₹50–₹200 per task, or infinite work. Treat “1,200 ideas” as **work hypotheses to validate**, not 1,200 open jobs. Build the loop around verified paid offers, permitted assistance, truthful proof, and measured earnings per minute.

## What exists today (verified against `main`)

### Working building blocks
- `agents/earnings_hunter.py`: fetches public HTML with bounded timeout/response size; starts from a curated list of 14 platforms; prefers explicit INR evidence; flags risk phrases; limits same-site detail crawls; exports CSV and Markdown reports.
- `.github/workflows/earnings-hunter.yml`: scheduled and manually triggered daily public-page discovery, offline unit tests, and a 14-day GitHub artifact.
- `agents/pod_pipeline.py`: reads the existing POD idea catalogue, attempts to read the public Google Trends RSS feed, creates draft metadata/CSV/ZIP outputs, flags a small list of brand/IP terms and keeps publication human-reviewed.
- `.github/workflows/pod-agent-pipeline.yml`: scheduled/manual pipeline and a seven-day artifact.
- `src/main.jsx`: mobile UI with Overview, POD Studio, Earnings Hunter, AI Agents, Task Queue, Reports, and Settings. Earnings status and amount fields are saved in device `localStorage` and CSV export is available.
- `tests/test_earnings_hunter.py`: offline tests cover currency parsing, evidence requirements, basic risk quarantine, source registry, and output files. The merged change's GitHub Actions test and POD pipeline runs passed. Android web build/APK job was still running at the last research check; inspect Releases before distributing.

### What is *not* implemented
- No autonomous “500/1,000 agents” or model pool. The UI is role labels and workspaces, not 1,000 independent models.
- No direct ingestion of a completed GitHub Actions artifact into the mobile UI. The app's lead snapshot and local tracker are separate from the generated CSV.
- No remote database or account synchronization. Clearing app data/device storage can lose the local tracker.
- No provider API connectors, worker OAuth, controlled login/browser sessions, job application, task reservation, work submission, acceptance callback, or payment verification.
- No automatic model inference in the scheduled GitHub workflows. They use standard-library scripts and existing templates; no inference endpoint or local model is connected.
- No full internet crawl. The scanner visits a curated registry and a capped number of same-domain HTML links; JavaScript-rendered content, login-only boards, and many anti-bot pages will be missed.
- No guarantee that a found page is currently open to this user, that the advertised rate is paid, or that the user's work will pass acceptance.
- POD: no generated print-ready image, robust trademark search, sales proof, seller account, marketplace API, listing publishing, order sync, or sales analytics. Google Trends is only a weak demand proxy.

## Priority gaps and fixes

| Priority | Gap | Recommended fix | Acceptance test |
|---|---|---|---|
| P0 | Source pages may be stale or blocked | Store fetch timestamp, HTTP status, page hash, extracted evidence, crawl depth, and last-success timestamp per source | Each lead shows source/time/evidence; stale leads are labelled stale |
| P0 | Candidate ≠ eligible job ≠ paid work | Separate states: discovered, current-open-verified, eligibility-unknown, eligible, applied, accepted-to-work, submitted, accepted, payable, payout-received | No “earnings” metric increments without a verified acceptance/payout record |
| P0 | ₹ per task vs ₹ per hour vs reward per batch can be confused | Add normalized rate units, currency, FX timestamp if converted, task duration interval, minimum payout, and rate confidence | Tests reject wrong unit conversions and generic homepage amounts |
| P0 | Tracker is local-only | First version: downloadable CSV backup/import and clear “this device only” indicator; later: SQLite or free managed backend only if its current limits/terms fit | Export then import preserves every row and monetary field |
| P0 | Scam and policy-risk triage is keyword-only | Add explicit checks for up-front fee, deposit, reimbursable deposit, fake reviews, identity resale, account rental, OTP/password requests, prohibited automation, and unsafe APKs; ambiguous leads go to quarantine | A labelled adversarial test set is 100% quarantined for known disallowed patterns |
| P1 | Small source coverage | Expand by official source adapters, not indiscriminate scraping; include source terms, robots/rate-limit notes, supported regions and payout methods | Source registry has ownership, terms URL, last audit date, region, and unit tests |
| P1 | Extractor uses heuristics | Add per-source parsers and evidence snippets; distinguish page-wide mentions from task-specific rates | Every rate requires task-detail evidence and a nearby unit phrase |
| P1 | Ranking optimizes posted amount, not expected value | Score hourly value, acceptance chance, qualification time, payout threshold, device needs, deadline, and repeatability; keep confidence separate from score | Ranking explanation can be reconstructed from stored evidence |
| P1 | No task-to-proof workflow | Add a checklist per task: instructions read, requirements passed, original work done, final human check, proof saved, submitted, accepted | Each task has evidence and a next action; never generates fake evidence |
| P1 | No scheduling/alerts from the user's app | Use Actions artifacts as a first milestone; later add notification/email only with explicit user opt-in and a supported free channel | Alert links to official page and timestamp, avoids duplicate spam |
| P1 | POD trend match is lexical only | Add niche-specific keyword source evidence and record trend date/region; deduplicate topics; keep sales claims out of copy | No trend is described as sales proof without sales data |
| P1 | POD IP checks are incomplete | Add exact phrase checks and manual search links to official trademark databases/marketplaces; check image similarity/license; keep publish approval manual | Each asset/listing has a dated IP review checklist |
| P2 | Missing product-grade docs | Add README setup/run steps, LICENSE decision, threat model, data retention, sources, troubleshooting, and screenshots | A newcomer can run offline tests and understand all limits |
| P2 | Tests mostly cover parsing | Add fixtures for each source adapter, fetch timeout, bad HTML, duplicate links, rate-unit confusion, persistence migration, import/export and build smoke tests | CI fails safely on regression |

## Recommended system architecture

1. **Source registry:** one record per official work source: country/languages, task types, official terms, eligibility, login requirement, payout currency/method/minimum, crawl permission, rate units, and last verified date.
2. **Fetch layer:** conservative public-page fetches only; clear per-domain caps, timeout/backoff, content-size cap, cache, duplicate removal, and an “unavailable” state. Use documented official APIs when the provider offers one and permits this use. Do not bypass CAPTCHAs, access controls, or login restrictions.
3. **Evidence extractor:** source-specific parser first; optional local LLM only to classify/structure already-fetched text. Store verbatim short evidence + page URL + timestamp; never let a model invent rates.
4. **Policy and eligibility engine:** deterministic rules for location, language, device, age/identity requirements, deadline, legal eligibility, automation rules, payout availability, scam risk, and required human action.
5. **Opportunity score:** use expected net value rather than headline pay:
   `expected net INR/min = (posted task value × estimated acceptance probability − known fees) / (work + qualification + review minutes)`.
   Keep the estimate clearly labelled; do not pretend acceptance probability is known before real observations.
6. **Task workflow:** discovered → current-open-confirmed → eligible → applied → qualification → approved → performed → submitted → accepted/rejected → payable → paid. Only the user/provider can confirm the relevant transitions.
7. **Proof and ledger:** keep only non-sensitive proof references and task IDs. Never store government ID, bank/UPI details, passwords or OTPs in repo artifacts, logs, prompts, or CSV reports.
8. **Model router:** deterministic parsers/classifiers first; local model for summaries and formatting; human review for money, legal/IP, identity, high-risk or irreversible actions. Do not run a separate LLM instance for each “agent” unless a real workload justifies it.
9. **Feedback loop:** record actual minutes, acceptance/rejection, and payout. Rank sources using observed personal outcomes, not guessed earnings claims.
10. **Audit and rollback:** version source parsers and prompts; keep an audit log of why each lead was ranked/quarantined; fail closed if rate evidence is missing.

## Free / open tools worth testing

| Tool | Best role | No-API / budget reality |
|---|---|---|
| GitHub Actions | Daily public-page checks, Python tests, APK build, report artifacts | Public-repository standard hosted workflows are free under GitHub's published terms, but job runtime, runner types, artifact retention, and abuse policies still limit the design. Not a permanent server or free GPU. |
| Python standard library | Current scanner, CSV/HTML/XML parsing, validation | Already used; keep for reliable low-cost processing. |
| Ollama | Local model runner on a computer | No inference API bill when running downloaded local weights, but a supported computer, storage, memory, and electricity are needed; it is not an Android cron server. |
| llama.cpp | Local CPU/GPU model inference and Android builds | Open-source runtime; Android builds exist, but integration and phone thermals/memory need testing. |
| LM Studio | Local desktop model UI/server and document chat | Offline after model download; mainly a desktop path, not a hosted always-on agent. |
| ComfyUI | Local image generation workflows (including print-art prototyping) | Core is free/local; suitable hardware and model licenses matter. GitHub's ordinary hosted runner is not a dependable free GPU. |
| Playwright | Browser QA, repeatable tests on sites you own/are authorized to test | Great for QA; not permission to automate third-party paid-task accounts or ignore their rules. |
| n8n Community | Visual orchestration on an always-on machine | Free self-hosting exists under Sustainable Use License; commercial hosted/embedded/customer-editable workflows have license boundaries. Not truly zero-maintenance. |
| Hugging Face Hub / model cards | Download and audit model files/licenses | Model files can be free; hosted inference has quotas/credits and is not unlimited. |
| Google Trends public RSS | Lightweight trend signal | Free public feed is best-effort and can fail; not sales data. |
| Tesseract / OCRmyPDF / Pandoc / FFmpeg | OCR, document conversion, media transcoding | Open-source tooling; use only within input-data rights and client rules. |
| Cloudflare Workers Free | Small webhook, redirect, or metadata utility | Published request/CPU caps make it a small glue service, not an LLM GPU or infinite scheduler. |
| Google Colab | Experiments and evaluation | Free compute is variable and not guaranteed; not a reliable unattended production service. |

Official references:
- GitHub Actions billing: https://docs.github.com/en/actions/concepts/billing-and-usage
- Ollama: https://ollama.com/download and https://ollama.com/library
- llama.cpp Android/build docs: https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md
- LM Studio offline: https://lmstudio.ai/docs/app/offline
- ComfyUI: https://www.comfy.org/about
- n8n license FAQ: https://support.n8n.io/article/can-i-use-your-license-for-my-use-case
- Hugging Face inference pricing: https://huggingface.co/docs/inference-providers/pricing
- Cloudflare Workers limits: https://developers.cloudflare.com/workers/platform/limits/
- Google Colab FAQ: https://research.google.com/colaboratory/faq.html

## Local model shortlist (no inference API required)

Model choice depends on memory, speed, language, vision, and license. “Open weights” is not always the same as an OSI-approved open-source model. Re-check the exact model card/license before commercial use or redistribution.

- **Very small / phone experiments:** Qwen3.5 0.8B or 2B quantized variants; use for simple classification, short summaries and drafts only. The downloaded model file is not the full RAM requirement. Do not assume a phone can run continuous background jobs.
- **Small/general-purpose local model:** Qwen3.5 4B quantized on a capable computer or phone with adequate free memory; useful for structured extraction and simple multilingual drafts but must be tested on Hindi/Gujarati and task guidelines.
- **Code/reasoning tests:** small DeepSeek-R1 distilled variants or Qwen coder variants where the model card fits the intended use. Reasoning output must be validated; a long explanation does not prove correctness.
- **Larger workstation model:** gpt-oss 20B is open-weight and listed with Apache 2.0 on the Ollama library page, but is around 14 GB of model files in Ollama's listing; it is not a realistic default for a phone. The larger 120B variant is not a zero-budget, low-memory recommendation.
- **Image generation:** ComfyUI plus a compatible local diffusion model is a separate stack from text models; verify model/license and GPU memory before selecting. It is not included in the current APK.

Official model catalogue: https://ollama.com/library/qwen3.5, https://ollama.com/library/deepseek-r1, https://ollama.com/library/gpt-oss, https://ollama.com/library/mistral-small. Model ranking should come from task-specific tests on a fixed benchmark, not brand claims.

## India-relevant earning leads to validate

These are places to inspect, not guarantees of open work or payout. Re-check the live official page before starting; a platform link is not proof that you are eligible.

| Source | Public evidence / possible fit | Important caveat |
|---|---|---|
| Karmyug AI | Official page currently shows Hindi/English/Bengali script recording at ₹2 per approved task; the site says joining is free and acceptance/quality checks apply. | This is below ₹50–₹200 per task. Voice recording must be original human work; automation should not impersonate the contributor. |
| CrowdGen / Appen Project Coffee | Official India page advertises US$2/hour (about ₹175/hour on its page) for data labelling; requirements include fluent English, India residence and laptop/PC. | Hourly, not per-task pay. Qualification/recruitment and actual hours are not guaranteed. |
| Corpshore / Jwuma India | Official India page describes annotation, model evaluation, transcription, QA and other contributor tasks. | Public page does not guarantee a rate or an open role; check offer terms first. |
| Clickworker | Official help says registration can be temporarily closed by country and payment methods differ by country. | Verify your account shows a supported payout method before spending time; the published minimum may require accumulating a balance. |
| TELUS Digital AI Community | Official flow describes applications and job-specific language/critical-thinking assessments. | Application-based; not an instant cash task. |
| Prolific | Official participant help page dated Sep 2, 2026 includes India among supported countries. | Eligibility isn't a guarantee of studies; account verification, waitlist/supply and study-specific rates can apply. |
| uTest | Public board lists India software-testing projects, sometimes invite-only. | Check specific test, invitation, compensation and all risk/expense terms. Reject anything requiring an upfront deposit or funding from a zero-budget worker—even where an advert says reimbursed. |
| OneForma / Toloka / Microworkers / Gitcoin bounties | Additional potential task/project sources in the registry. | Current region, project, payout, skill, wallet/KYC and acceptance conditions vary; verify the exact official listing. |

Official links:
- Karmyug jobs: https://work.karmyug.in/jobs
- CrowdGen Project Coffee: https://crowdgen.com/coffee-en-in/
- Corpshore/Jwuma India: https://platform.corpshore.ai/india
- Clickworker eligibility/payout: https://support-workplace.clickworker.com/support/solutions/articles/80000671469
- TELUS India roles: https://jobs.telusdigital.com/search/cfm5/ai-community/jobs/in/country/india
- Prolific supported countries: https://participant-help.prolific.com/en/articles/445007-who-can-participate-in-studies-on-prolific
- uTest projects: https://www.utest.com/projects?country=India&tab=all
- OneForma: https://www.oneforma.com/jobs/
- Toloka: https://toloka.ai/tolokers/
- Microworkers: https://www.microworkers.com/
- Gitcoin bounties: https://gitcoin.co/mechanisms/bounties

## What “autonomous” should mean for this project

**Good automation targets:** refreshing public job pages; extracting posted terms; filtering country/language/device; rate-unit conversion with source timestamp; ranking; drafting checklists; creating evidence templates; validating work files; export and reminder generation; duplicate/stale lead detection; POD metadata draft/QA; public API tasks explicitly permitted by their provider.

**Keep user/provider-controlled:** identity and tax verification; tests requiring genuine personal answers or voice; accepting contracts; clicking through terms; work where a platform forbids AI assistance; sensitive information; final quality submission; publisher/account actions; payouts; any irreversible or financial action.

**Never do:** fake reviews, fake accounts/proof, OTP/password sharing, circumvent CAPTCHA or bans, evade task rules, fabricate location/qualifications, submit crowdsourced human-study responses as a bot, or pay to unlock a job.

## First 30-day implementation plan

1. **Days 1–3 — evidence reliability:** record scan age and HTTP result; store extracted rate evidence and unit; add minimum payout/device/language/location/qualification fields; create “not a current verified task” default.
2. **Days 4–7 — usable mobile flow:** import/export tracker CSV; merge daily artifact leads into a single normalized board; filter by India, device (phone/PC), language, rate unit, payout rail, deadline and confidence; add local backup/recovery.
3. **Week 2 — more official sources:** add a source adapter contract, source policy/terms registry, parser fixtures and per-domain crawl budgets; remove dead/blocked sources after consecutive failures.
4. **Week 3 — local model option:** create a provider interface and offline rule-only fallback; add a small local model integration only where user hardware supports it. Test Hindi/Gujarati/English extraction, amount/unit correctness, fake-fee detection and JSON validity against fixtures.
5. **Week 4 — measure outcome:** add actual time and rejection reasons; compute net INR/minute and payout latency only from observed data; prioritize one legitimate accepted task first rather than registering everywhere.
6. **POD parallel track:** generate asset only on a verified local/free compute route; run transparent PNG dimensions/alpha/print size QA and manual IP checks; keep publishing disabled without a supported official path.
7. **Release safety:** test web build, Python tests and APK build after each change; tag only the current `main` commit; publish a debug APK as debug, and never claim the build includes a feature until the release asset's commit has it.

## 1,200 idea bank disclaimer

`IDEA_BANK_1200.csv` contains 50 repeatable work archetypes crossed with 24 customer/task verticals. It is intentionally labelled **hypothesis, not live paid job**. The right next step for each row is to locate a specific authorized buyer/listing, verify rate and acceptance terms, and only then create a task card. Automation percentages are qualitative; the human gate is part of the product, not a bug.
