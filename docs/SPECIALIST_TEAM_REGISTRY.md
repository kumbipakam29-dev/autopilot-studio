# Specialist team registry (45 role definitions)

This is an additive, versioned catalogue for three teams:

- **15 social media specialists** — planning, captions, Reels, creative briefs, localization, analytics, accessibility, and human-reviewed community response drafts.
- **15 automatic error-handling specialists** — CI triage, traceback classification, log summaries, bounded retry advice, regression localization, configuration diagnostics, and knowledge-base curation.
- **15 cybersecurity defense specialists** — authorized asset inventory, dependency and static-code review, secret-leak prevention, threat modeling, defensive incident triage, privacy, backups, and remediation tracking.

## Important runtime distinction

`registered` means the role is described in the catalogue; it does **not** mean an autonomous worker is running, connected to an account, or earning money. All entries remain `execution_status: planned` and draft-only. The catalogue grants no permission to publish posts, send messages, change accounts, pay, delete data, or alter security controls. Human review is required before external actions.

Cybersecurity roles are limited to defensive work on assets the operator is authorized to assess. They do not provide unrestricted scanning, exploitation, credential collection, persistence, evasion, or unauthorized access.

## Validation

Run locally with Python 3.12 or compatible:

```bash
python scripts/validate_specialist_team_registry.py
python -m unittest discover -s tests -p 'test_specialist_team_registry.py' -v
```

The Agent registry validation workflow runs these checks on relevant pushes and pull requests. Passing validation proves the catalogue structure and permission defaults only—not runtime activation or real-world security.
