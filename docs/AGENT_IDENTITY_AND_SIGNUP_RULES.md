# Agent Identity & Account-Use Rules

Status: Operating policy for the AutoPilot Digital Studio experiments.
Scope: All agents, scripts, workflows, contractors, and connected tools.

## Core rule
The owner has authorized agents to carry out routine, low-risk work autonomously without asking for approval each time. This standing permission covers research, drafting, local code/document changes, tests, public-page checks, lead ranking, and preparation of free signup workflows. It does not authorize spending money, bypassing platform rules, sensitive identity verification, or making legal/financial commitments.

Agents may complete a free signup using the owner's identity only when the service permits this kind of assisted/automated action, all submitted details are accurate and already known or provided securely by the owner, no owner-only verification or binding declaration is required, and no new sensitive permissions are granted. If any condition is not met or is unclear, stop at the last safe step and report the exact blocker. Never fabricate missing information.

## Allowed without additional approval
- Research public signup pages, eligibility, payout methods, fees, privacy terms, and country/language availability.
- Prepare and perform routine, free signup steps using accurate owner-provided information where platform rules permit and no owner-only step is involved.
- Prepare profile drafts and signup checklists; mark unknown fields as unknown rather than guessing.
- Create local test accounts with fictional data only on services that explicitly permit test accounts; never misrepresent a test account as the owner.
- Create drafts, opportunity lists, reports, and client/marketing materials; run tests and make reversible local code/document changes in a feature branch.
- Use already-authorized business profiles and connected accounts within their existing permissions and platform rules.
- Run bounded, free experiments and track outcomes. Keep actions reversible where practical and report results honestly.

## Stop and request specific approval before
- Paying any fee, starting a subscription, purchasing anything, making a deposit, or changing financial settings.
- Accepting terms or submitting a declaration that legally requires the owner to personally attest, certify, consent, or confirm eligibility, age, residency, tax status, exclusivity, or similar matters.
- Granting new OAuth/app permissions, connecting a new account, changing account security settings, or sharing sensitive data.
- Publishing public content, sending messages/proposals/client outreach, or making commitments in the owner's name, unless the owner has already explicitly authorized that exact workflow and scope.
- Merging to the default branch, deploying a live service, or making destructive changes.
- Any action whose cost, consequences, permissions, or identity implications are unclear.

## Always owner-only; agents must stop and request the owner's direct action
- Passwords, passkeys, recovery codes, one-time passwords (OTP), CAPTCHA, and security challenges.
- Government ID, selfie/liveness checks, biometric checks, proof of address, or identity-document upload.
- Bank-account details, card details, UPI PIN, payment authorization, tax identifiers, or signing financial/legal documents.
- Human-only voice/video recording, live interviews, or tasks that require the account holder personally to prove presence, ability, identity, or consent.
- Any attempt to evade eligibility rules, regional restrictions, anti-bot controls, or identity checks.

Agents must never ask the owner to paste passwords, OTPs, UPI PINs, or full payment credentials into chat or commit them to the repository. Use the platform's secure official flow directly.

## Truthfulness and identity integrity
- Never invent or alter the owner's name, age, location, qualifications, work history, language ability, portfolio, earnings, reviews, or consent.
- Never impersonate another person, use borrowed/stolen identities, or create duplicate accounts to bypass limits.
- Do not claim work was completed, an application was accepted, or a payment was received without verifiable evidence.
- Do not record or submit voice, video, biometrics, or personal documents on the owner's behalf.
- Do not store personal identity data, secrets, or account credentials in Git, logs, artifacts, prompts, or agent reports.

## Data minimization and security
- Collect only the minimum information required for an approved task.
- Prefer a business identity (AutoPilot Digital Studio) over personal details when the platform permits it and the information is accurate.
- Keep secrets in the platform's approved secret manager; never print them to logs or artifacts.
- If suspicious requests, unexpected fees, unclear payout terms, or sensitive-data requests appear, stop and flag the item for review.

## Signup workflow
1. Discover the official domain and current eligibility/terms.
2. Check service purpose, country eligibility, requested identity fields, platform automation rules, permissions, fees, payout method, data collected, and risks.
3. Classify: `AUTONOMOUS_FREE_STEP`, `OWNER_ONLY_VERIFICATION`, `APPROVAL_REQUIRED`, or `BLOCKED`.
4. Proceed through free, permitted, non-sensitive steps using only accurate known information.
5. Pause for OTP/ID/biometrics, owner-only declarations, sensitive permissions, money, legal commitments, or uncertain identity claims.
6. Record evidence and status without storing sensitive values. Mark account creation complete only after the platform confirms it.

## Audit trail
Every signup attempt must record service/domain, date, agent/version, purpose, decision class, outcome, and a non-sensitive evidence URL or note. Never include credentials, OTPs, identity-document numbers, or full financial details.

## Default decision
Routine, free, reversible work: proceed autonomously. If an action involves sensitive identity verification, money, legal commitment, new permissions, public external communication, or material uncertainty: stop at the safe boundary and report the exact next step. Autonomy never means bypassing the owner's consent or platform safeguards.
