# Data Labeling & Microtask Earnings Engine — MVP

This folder contains a **lead discovery and work-tracking prototype**, not a payment bot. It does not log into platforms, complete human-only tasks, submit work, or send/receive money.

## Goals
1. Discover official public opportunities for data labeling, AI response evaluation, transcription, localization, QA and open-source bounties.
2. Keep task pay units explicit (per accepted task / per hour / per batch / unknown).
3. Rank only by source evidence and eligibility; quarantine upfront-fee, deposit, account-rental, OTP/password, fake-review and CAPTCHA-bypass offers.
4. Track genuine work from lead through acceptance and payout confirmation.
5. Make it possible to test parsers offline and inspect a CSV report.


## Higher-value India roles added in the latest source experiment

- [YPAI Data Annotator — India](https://freelancer.ypai.ai/jobs/openings/data-annotator-in): page advertises typical INR 550–800/hour for projects; annotation includes image/video/audio/text labeling. Applicant review, initial tests, project availability and exact rate in the invitation still apply.
- [YPAI Model Evaluator — India](https://freelancer.ypai.ai/jobs/openings/model-evaluator-in): page advertises typical INR 550–800/hour; requires strong reading comprehension, rubric-based evaluation and evidence-backed reasoning. Work depends on project supply.
- [YPAI Data Collection Contributor — India](https://freelancer.ypai.ai/jobs/openings/data-contributor-in): page advertises typical INR 550–800/hour; device, consent and project-specific capture conditions apply.
- [HumanSignal contributor portal](https://onboard.humansignal.com/): application and identity verification precede matching; rates apply only to eligible projects.
- [OpenTrain Python Software Engineering LLM Evaluator](https://www.opentrain.ai/jobs/python-software-engineering-llm-evaluator--cmub37q18000d0agmbhe9iifm/): specialist coding-evaluation role listed for India, but requires real Python/software engineering judgment; do not apply with invented experience.

**Rate interpretation:** these provider pages advertise typical rates or a posted role, not a guaranteed personal offer, accepted hours, or payout date. Confirm the current rate, work volume, selection process, fees (should be zero upfront), payout method, and payment schedule in the actual project invitation before accepting work. The scanner preserves a displayed range such as INR 550–800/hour instead of silently reducing it to a single number. Source pages can change; check the live page at the time of application.

## Run
```bash
python -m unittest discover -s tests -v
python agents/data_labeling_hunter.py --output-dir output
```

## State model
`discovered → current_listing_verified → eligibility_check → applied → qualification → approved → work_in_progress → submitted → accepted/rejected → payout_pending → paid`

A stage change is a record of the user's/provider's confirmed status. A discovered listing never counts as income. The tool cannot confirm a bank/UPI credit; the user must confirm it in their own payment app.

## Privacy and safety
- Do not commit government ID, tax information, bank details, UPI IDs, passwords, OTPs, cookies, session tokens or identity documents.
- Use only public listing pages or documented APIs that allow this use; respect platform terms and rate limits.
- Never bypass CAPTCHA, impersonate a participant, create fake accounts, fabricate qualifications/proof or mass-submit human evaluations.
- Don't pay deposits or unlock fees for work.
- Keep human approval for account actions, personal tests, original voice recordings, final submissions and financial actions.
