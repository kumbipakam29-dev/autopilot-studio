# CI Failure Triage — 2026-10-26

## Findings

The two failures in runs #137 / #104 (run IDs `40233958512` and `40233958689`) shared the same root cause: the full unit-test suite included two stale ledger tests that attempted illegal stage jumps from `discovered`.

- `test_minutes_accumulate` attempted `discovered -> eligibility_check`, skipping `current_listing_verified`.
- `test_user_confirmed_paid_stage` attempted `discovered -> paid`, bypassing all work and payout stages.

The ledger's transition guard was behaving as designed. The fix is to make the tests follow the valid state machine, not weaken the guard. The current test suite uses a helper that advances through the legal stages before confirming payout.

## Verification on the latest PR head

Latest inspected PR head: `ebcb5e66ca2b73c140b37f1aabafc7af3eaa4bfc`.

All inspected checks on that head completed successfully:
- Public portal tests
- Data Labeling Earnings Hunter
- Device-adaptive router tests
- Agent registry validation
- Agent runtime tests
- Work Win Payment Loop
- Android debug APK build

Relevant passing runs:
- [Data Labeling Earnings Hunter #138](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40234004406)
- [Work Win Payment Loop #105](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40234004286)
- [Agent runtime tests #111](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40234004330)
- [Android APK build](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40234000667)

## Remaining limitations

- Passing tests prove code paths and guards, not that a paid task was accepted or that money was received.
- Latest live public scan checked 25 pages without logging in or submitting forms. Its report is a lead list, not verified jobs or guaranteed earnings.
- The Work Win ledger reported 30 discovered leads and zero owner-confirmed payments in that run.
- Scheduled GitHub Actions workflows on this feature branch are not evidence of an always-on service; scheduled activation depends on the repository's default-branch workflow configuration.
- PR #17 remains open/draft and unmerged. No public portal deployment, outbound messages, or public posts were performed.
