# CI Failure Triage — 2026-10-26

## Findings

The two failures in runs #137 / #104 (run IDs `40233958512` and `40233958689`) shared the same root cause: the full unit-test suite included two stale ledger tests that attempted illegal stage jumps from `discovered`.

- `test_minutes_accumulate` attempted `discovered -> eligibility_check`, skipping `current_listing_verified`.
- `test_user_confirmed_paid_stage` attempted `discovered -> paid`, bypassing all work and payout stages.

The ledger's transition guard was behaving as designed. The fix is to make the tests follow the valid state machine, not weaken the guard. The current test suite uses a helper that advances through the legal stages before confirming payout.

## Latest verification

Latest inspected PR head: `3f12599d798171604773967a21b1bbe31988d4b1`.

All six main workflows on this head completed successfully:
- [Agent registry validation #129](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40235026035)
- [Agent runtime tests #112](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40235026048)
- [Data Labeling Earnings Hunter #139](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40235026026)
- [Device-adaptive router tests #45](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40235026036)
- [Public portal tests #133](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40235026070)
- [Work Win Payment Loop #106](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40235026038)

The [Android debug APK build #160](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40235022915) also succeeded. Its [debug APK artifact](https://github.com/kumbipakam29-dev/autopilot-studio/actions/runs/40235022915/artifacts/12615075170) is available until 2027-01-23; artifact SHA-256: `0d057ff0ed1327643aa39e727c8f96602de969b2300d63d4fbc12f226388f654`.

## Remaining limitations

- Passing tests prove code paths and guards, not that a paid task was accepted or that money was received.
- The latest inspected live public scan checked 25 pages without logging in or submitting forms. Its report is a lead list, not verified jobs or guaranteed earnings.
- The Work Win ledger reported 30 discovered leads and zero owner-confirmed payments in that run.
- Scheduled GitHub Actions workflows on this feature branch are not evidence of an always-on service; scheduled activation depends on the repository's default-branch workflow configuration.
- PR #17 remains open/draft and unmerged. No public portal deployment, outbound messages, or public posts were performed.
