# Offline Client Acquisition Draft Pipeline

The pipeline composes the existing deterministic specialist capabilities into one
review-ready pack for a small-business social-media service offer.

## What it produces
- Structured brief and missing-field list.
- Content-angle hypotheses based only on supplied business facts.
- Three caption drafts, a seven-day content calendar, and two 17-second Reel scripts.
- A clearly labelled fictional spec-work portfolio concept.
- A one-to-one outreach draft only when a specific fact is supplied.

## Run locally

From the repository root:

```bash
python -m unittest tests.test_client_acquisition_pipeline -v
python -c 'from agents.client_acquisition_pipeline import build_client_acquisition_pack; print(build_client_acquisition_pack({"business_type":"cafe","audience":"local customers","offer":"coffee","platforms":["Instagram"]}))'
```

For practical use, call `build_client_acquisition_pack(dict)` with a business brief.
The function is an offline deterministic prototype; it is not an online prospect finder
or a model-backed AI agent.

## Safety and limits
- No web browsing, scraping, email/DM sending, publishing, purchases, or account changes.
- Do not add guessed facts about a real business. Only supply a public fact after checking it.
- Missing details remain marked as missing. Outreach is not drafted if the personalization fact is absent.
- Portfolio output is fictional spec work and must be labelled as such.
- All copy and recommendations require human review; no client, lead, sale, or payment is claimed.
