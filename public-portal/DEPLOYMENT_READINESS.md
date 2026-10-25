# Public portal deployment readiness (₹0-budget prototype)

## Recommendation

**Render Free Web Service is a candidate for a temporary demo only**, not production. Its official docs say free web services spin down after 15 minutes without inbound traffic, may take about a minute to wake, and have an ephemeral filesystem. Local SQLite files or other local writes would be lost on restart, redeploy, or spin-down. Free instances are explicitly not recommended for production.

Sources:
- https://render.com/docs/free
- https://render.com/docs/web-services
- https://render.com/docs/faq

## Candidate configuration (do not deploy without approval)

- Repository: `kumbipakam29-dev/autopilot-studio`
- Branch: `feat/public-agent-chat-portal`
- Root directory: `public-portal`
- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Health-check path: `/api/health`

The app resolves static files relative to `app.py`, so this root-directory configuration matches the current code.

## Safety and zero-budget gates

- Do not attach a payment method or choose a paid instance as part of this plan.
- Check the current free-tier terms and dashboard billing settings before creating any service.
- Do not expose the app publicly until the owner explicitly approves the public deployment.
- This MVP has no persistent approval queue, user login, durable data store, connected model, or external publishing integrations.
- Never enter passwords, OTPs, payment details, government IDs, or private customer information.
- A public demo should only be used for non-sensitive draft prompts. Free-tier uptime and cold-start delays are not guaranteed.

## Ready / not ready

- Automated Python/API tests: passing in GitHub Actions at the time of this note.
- Static asset paths: relative to the app file.
- Public deployment: **not performed**.
- Production readiness: **not ready**.
- First payment / revenue: not verified by this deployment work.

Review this file and the current provider terms again before deployment; free-tier terms can change.
