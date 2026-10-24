# Data Labeling & Microtask Earnings Engine — MVP

This folder contains a **lead discovery and work-tracking prototype**, not a payment bot. It does not log into platforms, complete human-only tasks, submit work, or send/receive money.

## Goals
1. Discover official public opportunities for data labeling, AI response evaluation, transcription, localization, QA and open-source bounties.
2. Keep task pay units explicit (per accepted task / per hour / per batch / unknown).
3. Rank only by source evidence and eligibility; quarantine upfront-fee, deposit, account-rental, OTP/password, fake-review and CAPTCHA-bypass offers.
4. Track genuine work from lead through acceptance and payout confirmation.
5. Make it possible to test parsers offline and inspect a CSV report.

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
