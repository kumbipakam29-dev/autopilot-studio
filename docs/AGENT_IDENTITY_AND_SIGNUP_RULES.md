# Agent Identity & Account-Use Rules

Status: Operating policy for the AutoPilot Digital Studio experiments.
Scope: All agents, scripts, workflows, contractors, and connected tools.

## Core rule
Agents may research signup requirements and prepare account applications autonomously. They must not create, activate, verify, or operate an account in the owner's identity unless the owner has explicitly authorized that specific service and the action is permitted by that service's terms. A general request to work autonomously is not blanket consent to legal attestations, identity verification, or financial commitments.

## Allowed without additional approval
- Research public signup pages, eligibility, payout methods, fees, privacy terms, and country/language availability.
- Prepare draft profile fields and signup checklists using only facts already provided by the owner; mark unknown fields as unknown.
- Create local test accounts with fictional data only on services that explicitly permit test accounts; never misrepresent a test account as the owner.
- Prepare drafts, opportunity lists, and a queue of the exact owner actions needed.
- Use an already-authorized business profile or connected account only within its existing permissions and the platform's rules.

## Require explicit owner approval for each named service/action
- Submitting a real signup using the owner's name, email, phone number, business identity, biography, photo, or other identifying information.
- Accepting terms, making eligibility declarations, confirming age/residency, tax status, exclusivity, or other legal attestations.
- Connecting a social account, granting new permissions, creating a public profile, or publishing content.
- Sending messages, proposals, applications, or client outreach in the owner's name.
- Any paid upgrade, fee, deposit, subscription, purchase, or financial setting change.

Approval must identify the service and action. Approval for one service does not authorize other services.

## Always owner-only; agents must stop and request the owner's direct action
- Passwords, passkeys, recovery codes, one-time passwords (OTP), CAPTCHA, and security challenges.
- Government ID, selfie/liveness checks, biometric checks, proof of address, or identity-document upload.
- Bank-account details, card details, UPI PIN, payment authorization, tax identifiers, or signing financial/legal documents.
- Any step where the platform requires the account holder personally to verify, certify, consent, or perform a human-only task.
- Any attempt to evade a platform's eligibility rules, regional restrictions, anti-bot controls, or identity checks.

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
- Before granting a new OAuth/app permission, explain the requested scope and why it is needed; wait for approval.
- If suspicious requests, unexpected fees, unclear payout terms, or sensitive-data requests appear, stop and flag the item for review.

## Signup workflow
1. Discover the official domain and current eligibility/terms.
2. Produce a concise review card: service, purpose, country eligibility, requested identity fields, permissions, fees, payout method, data collected, risks, and exact next action.
3. Classify: `RESEARCH_ONLY`, `OWNER_APPROVAL_REQUIRED`, `OWNER_ONLY_VERIFICATION`, or `BLOCKED`.
4. Do not submit a real signup or make a binding declaration until the service-specific approval is recorded.
5. If approved, proceed only through permitted steps; pause for OTP/ID/biometrics/payment/legal attestation.
6. Record evidence and status without storing sensitive values. Mark account creation as complete only after the platform confirms it.

## Audit trail
Every attempted signup must record service/domain, date, agent/version, purpose, decision class, approval reference (if any), outcome, and a non-sensitive evidence URL or note. Never include credentials, OTPs, identity-document numbers, or full financial details.

## Default decision
If uncertain whether a step uses the owner's identity, creates a legal obligation, shares sensitive data, or changes account security/permissions, STOP and request specific approval. Autonomy means doing the safe research and preparation—not bypassing the owner's consent or platform safeguards.
