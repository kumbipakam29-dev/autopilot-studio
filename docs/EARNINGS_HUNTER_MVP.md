# Earnings Hunter — all-internet microtask discovery MVP

## Goal

This module is broader than print-on-demand. It scans a curated set of official public starting points for India-relevant AI data tasks, rating work, language projects, microtasks, and open-source bounties. It prefers explicit INR amounts in the ₹50–₹200 range and does not invent a rate when a page omits one.

## Run

python agents/earnings_hunter.py --limit 30
python -m unittest discover -s tests -v

The scheduled GitHub Actions workflow runs daily. Open the repository Actions tab, choose Earnings Hunter, open the latest successful run, and download its artifact. The artifact contains:
- earnings_opportunities.csv — ranked discovery leads with exact URL, source, rate evidence, risk flags, and next steps;
- source_status.csv — which public pages could be fetched;
- earnings_tracker_template.csv — a ledger template for work you actually complete;
- earnings_hunt_report.md — what ran and how to interpret the results.

## Discovery boundaries

Only official public starting pages and same-site links found in public HTML are inspected. Requests are bounded by time and size. The code does not submit forms, create accounts, log in, click apply/claim buttons, handle identity verification, bypass CAPTCHAs, or scrape private dashboards. Results are leads, not a guarantee that the provider currently has work or that a person is eligible.

## Safe work → evidence → repeat loop

1. Open the official task page from the CSV.
2. Confirm current task availability, accepted country/language, stated pay, deadline, acceptance criteria, and payout method.
3. Never pay a registration, deposit, training, or unlock fee. Do not misrepresent location with a VPN, create multiple accounts, submit fake reviews, copy proof, or use somebody else's account.
4. Do the actual work yourself, following the provider's rules. Use AI assistance only when that task's terms allow it.
5. Record time spent, evidence link/note, approval status, and actual INR earned in your private tracker.
6. Prioritize repeatable tasks only after an actual acceptance and payout have been verified.

## Current platform leads

- Karmyug AI: https://work.karmyug.in/ — public listings may include speech and data tasks; confirm the rate and approval rules for each task.
- TELUS Digital AI Community India: https://jobs.telusdigital.com/search/cfm5/ai-community/jobs/in/country/india — project-based applications and qualifications may be required.
- Clickworker: https://www.clickworker.com/clickworker/ — availability and payment methods vary by country; confirm the payout route before spending time.
- Microworkers: https://www.microworkers.com/ — KYC and withdrawal rules apply; submit only genuine proof.
- Toloka: https://toloka.ai/tolokers/ — check current geographic and project restrictions.
- OneForma: https://www.oneforma.com/jobs/ — projects and payment terms vary.
- CrowdGen by Appen: https://crowdgen.com/ — project-specific eligibility and payment terms.
- Gitcoin / Buidlbox bounty ecosystem: https://gitcoin.co/mechanisms/bounties — more skill-oriented bounties; rewards depend on acceptance and the live offer.

## What this does not claim

This MVP is a scheduled public-page discovery tool, not 500 independent intelligent models. It has no worker account credentials; no provider has granted permission to auto-complete tasks; and it cannot guarantee a first payment. Auto-submission is disabled because it could violate task rules or create fraudulent proof. The first milestone is one verified legitimate paid task completed and recorded by you. Official API integrations can be added only where the provider explicitly supports them.
