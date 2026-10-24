# AutoPilot Studio — POD Agent MVP

## What this workflow does today

The POD Agent Pipeline GitHub Actions workflow runs manually on demand or once per day. It uses only Python's standard library and the concept briefs already in src/podData.js.

1. Attempts to read the public Google Trends RSS feed for India (or US/GB when manually triggered).
2. Matches trend labels conservatively to existing niche words. It keeps trends as research signals only and does not inject them into listings or artwork.
3. Generates draft titles, descriptions and tags from each existing concept brief.
4. Creates a review queue that defaults to approved_to_publish=NO.
5. Uploads CSV/Markdown reports and a ZIP bundle as a GitHub Actions artifact for seven days.

No paid API key, external Python package, database, or GPU is required for this stage. The GitHub-hosted runner may fail to reach a public feed; if so, the job still produces evergreen concept drafts and states that live trend data was unavailable.

## Find the output

Open the repository's Actions tab → POD Agent Pipeline → latest successful run → Artifacts → download pod-agent-results-*. The ZIP inside is pod-agent-bundle.zip.

On a manual run, choose Run workflow, select IN, US, or GB, and select 10 or 25 concepts. The daily scheduled run uses India and 25 concepts.

## Strict boundaries

This is a real scheduled data-processing workflow, but it is **not yet a fully autonomous generative AI**. It does not:

- generate original raster artwork or transparent print-ready PNGs;
- prove demand, sales potential, or keyword search volume;
- perform a complete trademark, copyright, or duplicate-image search;
- connect to Etsy, Amazon Merch on Demand, Printful, Shopify, or seller credentials;
- create or publish marketplace listings; or
- keep a permanent database after the artifact expires.

The trend matcher, brand term list and metadata checks are heuristics only. All drafts need human review. Amazon Merch on Demand must remain a manual upload step unless Amazon provides the account with an official supported route. Never automate around platform access controls.

## Why the next stages are separate

**Stage 2 — Artwork:** Add an image provider adapter with an explicit documented license and a user-provided provider token in GitHub Secrets if required. A standard GitHub-hosted runner does not guarantee GPU acceleration. Until a no-cost, reliable inference route is verified, this MVP only exports the existing art prompt brief.

**Stage 3 — Print QA:** Inspect generated PNG dimensions, alpha channel, format, and embedded DPI/print-size assumptions; create a contact sheet and quarantine failed images. DPI metadata alone does not create resolution.

**Stage 4 — Publishing:** Start with a dry-run/export adapter. Only connect a marketplace after a real seller account, official API access, platform eligibility, fees, and OAuth are confirmed. Any live listing creation should stay disabled by default until the owner explicitly enables it.

**Stage 5 — Analytics:** Use the seller's own authorized orders/listing data; record actual observations separately from trend proxies and estimates.

## Acceptance criteria for this MVP

- Unit tests pass on the hosted runner.
- The workflow can complete even when trend RSS is unavailable.
- It reads concepts from the current app source (no duplicated concept catalogue).
- Output CSVs have stable headers and contain one listing draft and review row per processed concept.
- Every generated listing is marked HUMAN_REVIEW_REQUIRED; the approval field is NO.
- The job publishes an artifact with a seven-day retention period.
- It does not need secrets and cannot publish a live listing.
