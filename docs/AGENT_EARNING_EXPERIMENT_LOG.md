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

## Fresh official-page cross-check (2026-10-26)

A separate current web check found these details; they are not applications and do not imply acceptance:

- YPAI Data Annotator, India: applications shown as open; typical project pay INR 550–800/hour, with batch/project gaps possible. Payment is every two weeks after approved work via PayPal, Wise or bank transfer. No fee should ever be paid. Official page: https://freelancer.ypai.ai/jobs/openings/data-annotator-in
- UserTest Pro: the ₹200 extracted by the crawler is not a reliable fixed rate for this platform. Its current official page lists study ranges: video ₹300–₹2,500+, audio ₹200–₹1,500+, usability ₹400–₹3,000+, depending on study length and matching. Weekly reward payout is described via Tremendous; no guaranteed minimum invites or monthly income. Official page: https://www.usertestpro.com/get-paid-to-test
- Karmyug AI: current jobs page lists Hindi and English recording at ₹2 per approved task, with positions shown for both; Bengali showed zero positions on the checked page. Approved-task rules and the live positions can change. Official page: https://work.karmyug.in/jobs

The web cross-check corrects the crawler interpretation: do not treat the UserTest Pro ₹200 string as a fixed task rate. This is an extraction-quality bug to fix in a future version.

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

Allowed without further approval: public-page research within rate limits, local ranking, report generation, code/tests, draft creation, public business-level research, non-destructive GitHub feature-branch commits, and routine free signup steps where the service permits assisted automation, all data is accurate and known, and no sensitive verification or binding declaration is required. Agents may continue through permitted, reversible steps without repeatedly asking for approval.

Stop for owner-only OTP/CAPTCHA, identity documents, selfie/liveness/biometrics, bank or payment credentials, legal attestations, fees, subscriptions, new sensitive permissions, or unclear terms. Do not invent missing profile facts. Do not send client outreach, publish publicly, apply/submit work in the owner's name, merge/deploy, delete data, or initiate/confirm payments unless the exact action is authorized and the platform permits it. See [Agent Identity & Signup Rules](AGENT_IDENTITY_AND_SIGNUP_RULES.md) and [Agent Training & Evaluation](AGENT_TRAINING_AND_EVALUATION.md).

## Status vocabulary

- \`implemented\`: code exists.
- \`run_success\`: the specified workflow ran successfully.
- \`lead_only\`: possible opportunity; not confirmed available or eligible.
- \`owner_action_required\`: account, eligibility, identity, task completion, or submission must be done by the owner.
- \`owner_confirmed_paid\`: owner says actual credit arrived; not independent financial verification.

## Agent improvement iteration — 2026-10-26

- Added [Agent Training & Evaluation Playbook](AGENT_TRAINING_AND_EVALUATION.md) defining task-specific tests, evidence standards, safety regression checks, quality metrics, and prototype-to-production release gates.
- Added the [Identity & Signup Rules](AGENT_IDENTITY_AND_SIGNUP_RULES.md) and linked both playbooks from the README.
- Fixed a ranking/extraction edge case in `agents/earnings_hunter.py`: endpoints of a visible rupee range such as `₹200–₹2,500+` are no longer treated as a standalone target-range rate. Added a regression test in `tests/test_earnings_hunter.py`.
- Changes are saved on `feat/public-agent-chat-portal`. A new CI result for these exact commits has not been verified yet, so the regression fix is implemented but not yet labelled tested.
- This is software/test-fixture improvement, not model training. The existing agents remain bounded scripts and deterministic handlers; no new external model, live platform login, or background worker was connected.

