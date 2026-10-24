# Earnings Task Ledger

A local JSON ledger for tracking user-confirmed task stages and time spent. It deliberately does not store UPI IDs, bank details, identity documents, passwords, OTPs, cookies or platform sessions.

```bash
python agents/earning_task_ledger.py add JOB-001 "Data annotation task" "https://official.example/job" --currency INR --amount 100 --unit "per task"
python agents/earning_task_ledger.py update JOB-001 eligibility_check --minutes 5
python agents/earning_task_ledger.py update JOB-001 applied --minutes 10
python agents/earning_task_ledger.py update JOB-001 accepted --accepted-amount 100
python agents/earning_task_ledger.py update JOB-001 payout_pending
python agents/earning_task_ledger.py update JOB-001 paid --payout-amount 100 --confirm-payout
```

Use the final command only after checking your own bank/UPI app and confirming the credit. This command records your confirmation; it does not verify your account or transfer funds.
