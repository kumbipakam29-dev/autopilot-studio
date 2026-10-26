# Public portal deployment readiness (₹0-budget prototype)

## Recommendation

**Render Free Web Service is a candidate for a temporary demo only**, not production. Its official docs say free web services spin down after 15 minutes without inbound traffic, may take about a minute to wake, and have an ephemeral filesystem. Local SQLite files or other local writes would be lost on restart, redeploy, or spin-down. Free instances are explicitly not recommended for production.

Sources:
- https://render.com/docs/free
- https://render.com/docs/web-services
- https://render.com/docs/faq

## Candidate configuration (do not deploy without approval)

- Repository: \`kumbipakam29-dev/autopilot-studio\`
- Branch: \`feat/public-agent-chat-portal\`
- Root directory: \`public-portal\`
- Runtime: Python
- Build command: \`pip install -r requirements.txt\`
- Start command: \`uvicorn app:app --host 0.0.0.0 --port $PORT\`
- Health-check path: \`/api/health\`

The app resolves static files relative to \`app.py\`.

## Required environment configuration

- \`AUTOPILOT_APPROVAL_TOKEN\`: long, random secret stored only in the hosting provider's secret environment. Never commit it or place it in the browser.
- \`AUTOPILOT_APPROVAL_DB\`: path to a private persistent disk file if the provider supports one. The default \`/tmp\` path is ephemeral and is not suitable for reliable queue retention.

The approval queue stores redacted request text for up to seven days. Redaction is best-effort, not a guarantee; never enter credentials, OTPs, payment details, government IDs, or private customer data. Review decisions do not trigger external actions. Public exposure still requires a secure admin client and further security/privacy review.

## Safety and zero-budget gates

- Do not attach a payment method or choose a paid instance as part of this plan.
- Check current free-tier terms and dashboard billing settings before creating any service.
- Do not expose the app publicly until the owner explicitly approves the public deployment.
- Free-tier uptime and cold-start delays are not guaranteed.

## Ready / not ready

- Automated Python/API tests: must pass on the latest commit before considering the branch reviewable.
- Static asset paths: relative to the app file.
- Approval queue: SQLite persistence implemented; durability depends on configured storage.
- Approval API: token-gated and disabled if the token is not configured; no external action executor.
- Public deployment: **not performed**.
- Production readiness: **not ready**.
- First payment / revenue: not verified by this deployment work.

Review this file and current provider terms again before deployment; free-tier terms can change.
