# Work → Win → Payment Loop

## Purpose

One review-first loop joins the existing public-page Earnings Hunter to a durable local status ledger and a ranked action pack. It gives agents explicit tool permissions while keeping external side effects disabled.

## Tool use

See [tool_registry.json](../agents/tool_registry.json). Implemented tools include bounded public HTTPS page fetching, evidence extraction, risk-keyword quarantine, heuristic ranking, deterministic content drafts, client-pitch drafting from public business-level facts, CSV/Markdown export, and a local SQLite status/payment ledger.

Not connected: live web search from the agent runtime, logged-in work platforms, account creation, identity/liveness verification, applying, submission, outbound email/DM, marketplace publishing, and money movement. Do not mark these connected.

## Run a live discovery cycle

Run on a trusted local computer from the repository root:

~~~~bash
python agents/work_win_payment_loop.py cycle --limit 30
python agents/work_win_payment_loop.py status
~~~~

The cycle uses the existing agents/earnings_hunter.py module, refreshes stable opportunity IDs in a local SQLite ledger, and emits output/work_win_payment_queue.csv plus output/work_win_payment_report.md. It also emits the underlying earnings_opportunities.csv and source_status.csv.

For a no-network smoke test:

~~~~bash
python agents/work_win_payment_loop.py cycle --offline --limit 10
python -m unittest discover -s tests -v
~~~~

## Client prospect → pitch draft

Create a CSV from business-level information on a public business profile. Use the blank [prospect template](../templates/client_prospects_template.csv). Required columns are business_name, business_type, and observation; optional columns are public_profile_url and recommended_idea.

~~~~bash
python agents/work_win_payment_loop.py draft-client-pitches --input templates/client_prospects_template.csv
~~~~

Use genuine, recent, neutral observations. The script drafts personalised copy but never sends it. Do not scrape private/personal data, bulk-message, ignore opt-outs, invent a relationship, or promise sales results. The ₹499 starter offer is an experiment, not a market-verified price. Portfolio pieces must remain labelled SPEC.

## Status updates and confirmed payment records

Only record an action after the owner has really done it. First use a lead_id from the generated queue:

~~~~bash
python agents/work_win_payment_loop.py update --lead-id LEAD_ID --status applied_by_user --note "Applied manually on official page"
python agents/work_win_payment_loop.py update --lead-id LEAD_ID --status accepted --note "Provider approval confirmed in official account"
python agents/work_win_payment_loop.py payment-confirm --lead-id LEAD_ID --amount-inr 100 --method UPI --evidence-note "Actual credit checked by owner on 2026-10-26" --confirm-received
python agents/work_win_payment_loop.py status
~~~~

Replace the sample lead ID, amount, date and method with the real values. Only use --confirm-received after checking the actual credit in your own payment app/account. This command stores the owner's declaration; it does not independently verify the account, read payment notifications, or initiate a transfer. Never put a transaction reference, UPI ID, account number, screenshot, OTP, password or ID document in the repository.

## Status meanings

- **new / reviewed:** discovery lead, not an available job guarantee.
- **shortlisted / application_ready:** reviewed by owner; no application sent.
- **applied_by_user, task_started_by_user, submitted_by_user:** owner-reported steps.
- **accepted:** owner confirmed the provider accepted the work; not yet paid.
- **paid:** owner confirmed actual credit; tool did not independently verify it.
- **quarantined:** potential scam/risk term; cannot be promoted via the normal status command.

## GitHub Actions

Workflow: [Work → Win → Payment Loop](../.github/workflows/work-win-payment-loop.yml). It tests the tools, scans public pages, and uploads only public-source CSV/Markdown action packs for 14 days. Its runner is ephemeral; the private SQLite ledger is not uploaded. Workflow artifacts are not permanent storage.

The scheduled trigger only runs from GitHub's default branch. This workflow is currently on the feature branch and will not become a default-branch daily loop until the change is merged. A push to this feature branch or manual workflow dispatch can test it now. No merge or deployment was performed here.

## Acceptance criteria

- A live scan can fail to fetch a site yet still produces a transparent source-status record.
- Risky candidates are quarantined.
- Lead status survives repeated scans in a local SQLite database.
- paid cannot be set through a generic status update.
- Payment entry requires an explicit owner confirmation flag.
- Generated client messages remain drafts and are never sent by the tool.
- No credentials or payment database are uploaded as workflow artifacts.
