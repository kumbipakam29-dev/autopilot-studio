# AutoPilot Studio CRM (₹0, local-first)

A small Python-standard-library CRM for researching prospects, recording source evidence, drafting personalized offers, and tracking clients/payments. It does **not** scrape websites, send messages, publish content, or claim leads are customers.

## Privacy and safe sourcing

- Actual lead/client data lives in local `crm/autopilot_crm.sqlite3`. That database is ignored by Git.
- Never commit real contact details, notes, client work, quotes, replies, or payment records to the public repository.
- Do not bulk-scrape Google Maps or Justdial. Google Maps terms prohibit exporting/scraping business listing content for use outside Maps; Justdial terms prohibit scraping/data mining and compiling listing collections. Use these services for manual discovery, then record only what you need and only where permitted. Prefer a business's own website/social profile and sources that explicitly permit reuse.
- Save a source URL and date checked for every lead. A listing is a lead, not a qualified prospect. Verify the business and current public contact channel before outreach.
- No bulk spam. Drafts remain unsent until a human explicitly approves the exact message and channel. Respect opt-outs and mark `do_not_contact`.
- Payment is verified only after evidence of an actual received payment; never infer it from a proposal or verbal promise.

## Requirements

Python 3.10+ (standard library only). From the repository root:

```bash
python crm/crm_cli.py init
python crm/crm_cli.py add --business "Example Cafe" --category cafe --city-area Ahmedabad --source-name "Official website" --source-url "https://example.com" --work-description "Cafe and takeaway" --offer-primary "12 social posts + 4 short Reels"
python crm/crm_cli.py list
python crm/crm_cli.py draft 1 --language Hinglish --tone friendly --offer "3 sample post concepts + monthly content package" --cta "Would you like me to share one sample concept?"
```

Import a CSV using the template:

```bash
python crm/crm_cli.py import-csv crm/import_template.csv
```

The template contains headers and no real lead data. Import skips exact duplicate business-name + source-URL pairs; spelling/case variants may still create separate records. Inspect `--help` for commands and options.

## Pipeline stages

`new → researched → audited → draft_ready → approved_to_contact → contacted → replied → meeting → proposal → client`

Other exception stages: `not_a_fit`, `do_not_contact`, `lost`. Only update to `approved_to_contact` after explicit user approval. This CRM does not send messages.

## Draft customization

Each draft can be tailored by business, category, city/area, observed public evidence, actual work, offer, language, tone, and call to action. Avoid claims about results, past clients, testimonials, or guaranteed growth unless independently verified and authorized.

## Current limitations

- Local single-user database; no cloud sync, background lead harvesting, automated scraping, outreach, or publishing.
- CSV import only imports records the operator is permitted to collect. Duplicate checks prevent common accidental repeats.
- Back up the SQLite file privately. Never upload it to GitHub.
