# Direct-client microgig experiment: CSV/text labeling + QA

## Service hypothesis

Offer a small, clearly scoped CSV cleanup and text-labeling service to clients who have permission to share the data. Deliverables: a labeled CSV based on the client's written taxonomy, rationale notes for ambiguous labels, and a quality report checking duplicate IDs, missing fields, invalid labels and schema consistency.

The portfolio CSV at `portfolio/synthetic_customer_feedback_labeled.csv` contains **synthetic demo text**. It is not client data and is not evidence of prior paid work. Label correctness always depends on the buyer's actual written rubric; do not promise perfect accuracy.

## Experimental quotes — test only, not verified market rates

| Package | Test scope | Proposed first-client quote |
|---|---|---:|
| Starter | Up to 100 rows, one label, CSV + basic checks | ₹199 |
| Standard | Up to 300 rows, up to two labels, CSV + QA summary | ₹399 |
| QA Plus | Up to 500 rows, up to three labels, duplicate/empty/label checks + JSON report | ₹699 |

These prices are hypotheses, not guarantees that buyers will accept them. Agree scope, privacy, deadline, acceptance criteria, revisions and payment timing before beginning. No joining fee, deposit or paid unlock.

## Run the deterministic QA checker

```bash
python agents/annotation_quality_check.py --input portfolio/synthetic_customer_feedback_labeled.csv --report output/annotation-qa-report.json
python -m unittest discover -s tests -v
```

The checker validates structure and allowed values; it cannot prove semantic correctness. A human must review ambiguous cases against the client's taxonomy. Use only data the client is authorized to provide.

## Honest proposal template

> Hi — I can clean and label a small CSV using your exact intent/sentiment taxonomy, then return the labeled file plus a consistency report for duplicate IDs, missing fields and invalid labels. I can first validate a small sample against your written guidelines so we agree on edge cases before scaling. Please share the expected columns, label definitions, row count, deadline and acceptance/payment terms. I only work with data you have permission to share.

Send only to a few relevant, real listings or client requests; personalize each proposal and follow the marketplace's rules. Don't bulk-spam, invent paid experience, fabricate proof, or submit fake reviews.
