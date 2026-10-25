# Agent Earning Experiment Log — 2026-10-26

## Experiment goal

Test whether the current AutoPilot agent tooling can discover legitimate public work leads, rank them, produce a review queue, and track progress without spending money or taking unsafe external actions.

## Run evidence

- GitHub Actions run: https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40224129155
- Result: workflow completed successfully; test step passed; live scan and artifact upload completed.
- Artifact: \`work-win-payment-loop-artifacts\`, run artifact ID 12610482003, available until 2026-11-08.
- Mode: live scan of curated public HTTPS sources.
- Unique queue rows: 30 across 9 source labels; 30 unique URLs.
- Triage: 26 \`LEAD_ONLY\`, 4 \`REVIEW_TERMS\`.
- Public rate evidence: 1 entry at ₹200; 3 entries at ₹2; 26 entries with no public amount extracted.
- The ₹200 entry is a lead to verify, not confirmed work. The three ₹2 entries are small per-task amounts; unit, volume, acceptance, and payout must be checked on the official page.
- No applications, messages, submissions, purchases, uploads, or payments were made. Confirmed revenue from this run: ₹0.

## Interpretation

This run demonstrates a working discovery-to-queue pipeline, not an earning agent that can independently complete tasks. Most extracted rows are lead-only and need eligibility/rate/payout verification. The queue contains several category or language pages, so the next iteration should deduplicate parent/category pages against specific project pages, verify whether the work is currently open, and rank by expected net value rather than page title alone.

The upstream Earnings Hunter report and the loop queue appear to disagree on the target-range match count. Treat the queue's explicit amount labels as extracted evidence only; reconcile that metric before using it for automated decisions.

## Next experiment backlog

1. Add source-level freshness and availability checks; don't label generic category pages as open jobs.
2. Deduplicate jobs by canonical URL and project ID, not merely page title.
3. Add a manual review field for eligibility, rate unit, acceptance rules, payout minimum, payment route, and whether the project is currently accepting applicants.
4. Run a separate client-acquisition experiment using public business-level facts; create sample audits and pitch drafts only. No automated DMs.
5. Add POD demand research as a separate experiment with original design briefs and rights checks; don't publish listings automatically.
6. Only count revenue after the owner confirms actual credit in their payment app. The ledger is owner-reported, not independently bank-verified.

## Free-hand experiment permissions

Allowed without further approval: public-page research within rate limits, local ranking, report generation, code/tests, draft creation, public business-level research, and non-destructive GitHub feature-branch commits.

Not allowed automatically: spending money, creating accounts, accepting legal terms, sharing identity documents, completing identity/liveness checks, applying or submitting work under the owner's identity, sending DMs/emails/comments, publishing to public accounts or marketplaces, merging/deploying public services, deleting data, or initiating/confirming a payment without the owner's explicit confirmation.

## Status vocabulary

- \`implemented\`: code exists.
- \`run_success\`: the specified workflow ran successfully.
- \`lead_only\`: possible opportunity; not confirmed available or eligible.
- \`owner_action_required\`: account, eligibility, identity, task completion, or submission must be done by the owner.
- \`owner_confirmed_paid\`: owner says actual credit arrived; not independent financial verification.
