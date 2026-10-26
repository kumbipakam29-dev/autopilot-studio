# AutoPilot Studio — WhatsApp automation and plugins

## What this change adds

- A dependency-free plugin registry with explicit enablement and health status.
- WhatsApp Cloud API webhook verification and signature-check helpers.
- Extraction of incoming text messages and basic sales/support/pricing triage.
- A reply-draft record that is NOT sent automatically.

## Important status

This is integration scaffolding, not a connected production bot. It does not
create Meta assets, deploy a public HTTPS endpoint, send WhatsApp messages,
or connect an AI model. No customer messages are sent by these modules.

## Zero-budget test path

1. Use Meta's official WhatsApp Business Platform Developer Hub and its free
   test number/environment: https://whatsappbusiness.com/developers/developer-hub/
2. Create/configure the Meta app and WhatsApp test assets in Meta's dashboard.
3. Deploy the webhook behind a public HTTPS URL. Configure the callback URL and
   WHATSAPP_VERIFY_TOKEN in the host and Meta dashboard.
4. Store META_APP_SECRET, the WhatsApp access token, phone-number ID and any
   other credentials as deployment secrets/environment variables only. Never
   commit real tokens, OTPs or customer data.
5. Verify X-Hub-Signature-256 with verify_signature before parsing webhook
   JSON. Return HTTP 200 for accepted webhook events and log errors without
   logging secrets.
6. Route extracted messages through the plugin registry. Keep replies as drafts
   until the AI reply engine, opt-in/policy checks, rate limits and audit logs
   are implemented and tested.
7. Test with a Meta test number first. Do not switch a personal WhatsApp
   Business App number to the Platform without reviewing migration/number
   requirements and the impact on the existing app.

## Environment variable names

- WHATSAPP_VERIFY_TOKEN — private webhook challenge token.
- META_APP_SECRET — used to validate webhook signatures.
- WHATSAPP_ACCESS_TOKEN — Meta-issued API token; required only for sending.
- WHATSAPP_PHONE_NUMBER_ID — Meta Cloud API phone-number ID.

Do not place values in this document or commit a .env file.

## Next implementation steps

- Add a small HTTPS web adapter appropriate to the chosen hosting target.
- Add unit tests for webhook challenge verification, signature rejection,
  duplicate event handling and message extraction.
- Add a durable lead/message store with retention controls.
- Add an AI provider interface and draft/review/sending policy.
- Add an outbound Cloud API client with explicit enable flag and test-number
  safeguards, then add delivery-status webhook handling.
- Register WhatsApp and future integrations (CRM, email, social publishing)
  through the same plugin registry with truthful connection health checks.
