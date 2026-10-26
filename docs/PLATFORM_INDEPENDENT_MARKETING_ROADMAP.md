# Platform-Independent Marketing & Communication Plan

**For:** AutoPilot Digital Studio  
**Budget target:** ₹0  
**Status:** Research/design proposal; no external account is connected and no messages/posts have been sent.

## Core principle

Do not make the business dependent on Meta Business Suite, Facebook Pages, Instagram, or WhatsApp Cloud API. Keep the website, content library, lead tracker, campaign calendar, analytics exports, and automation code in our own GitHub repository. Treat each social network or messaging provider as an optional adapter. If one platform blocks access or changes its API, the business should still be able to publish elsewhere, contact opted-in leads through another permitted channel, and export its data.

Open source software does not grant access to private platform APIs. Each network can still require developer approval, OAuth, account eligibility, app review, rate limits, and/or paid API access. Never bypass these controls or automate login through unofficial methods.

## Recommended zero-budget architecture

1. **Owned content source of truth:** Markdown/CSV files in this repository. Store campaign copy, captions, creative paths, target channel, planned date, approval state, source links, and post URL after the user verifies publication.
2. **Website:** static HTML/CSS/JS under website/. Keep it portable to any static host. Do not assume GitHub Pages is suitable for a commercial business site without checking its current terms. A public repository alone is not a deployed website.
3. **Content production:** existing Python standard-library scripts and human-reviewed templates; export ready-to-paste captions, hashtags, CTA, alt text, and platform-specific versions.
4. **Scheduling:** GitHub Actions can run linting, build reports and prepare a daily content pack. It should not be treated as an always-on server or as a way to bypass network rules. Scheduled jobs can be delayed or disabled; review current free-tier limits.
5. **Publishing adapters:** each platform is optional and disabled until its official API, permission, credentials, content formats and tests are verified. Start with export/manual posting. Never store access tokens in source files or logs; use GitHub Actions secrets only after the owner explicitly sets them.
6. **Lead management:** versioned CSV template with consent/source/date/status/next-action fields. Keep private customer data out of a public repo; use a local private file and export sanitized metrics only.
7. **Email:** use a real mailbox for individual, relevant business outreach. The repo can draft personalized emails and record the next action; sending requires a configured mail provider and consent/legal compliance. Newsletter systems such as listmonk or Mautic are self-hosted software, not free email delivery: they still need hosting and a legitimate SMTP/sending provider. Avoid bulk cold email, purchased lists and deceptive headers.
8. **WhatsApp:** keep a plain wa.me click-to-chat link as an optional contact route when the owner has configured the correct business number. This opens the user's WhatsApp app and does not provide automation or send messages by itself. For automation, official WhatsApp Business Platform/Cloud API still depends on Meta and its account/API policies; there is no legitimate open-source project that removes that dependency. Use email, website contact, phone, or other opt-in channels as fallbacks.
9. **Cross-platform social:** prepare and export content for LinkedIn, YouTube, TikTok, Pinterest, Reddit (only where community rules allow promotion), Telegram, Discord, Bluesky, Mastodon and other channels as relevant. Prefer networks whose official API/access is available without paid usage for the specific task; verify current terms before enabling. An open-source scheduler may unify workflow but cannot guarantee free publishing to every network.
10. **Analytics:** store only observed counts and source links; do not infer sales from views or mark a post published until its public URL or owner confirmation is recorded.

## Open-source projects to evaluate (not yet installed or connected)

- **Pendpost:** https://github.com/pendpost/pendpost — MIT-licensed, local-first planner with approval gates; repository describes publishing engines for several networks. Evaluate installation requirements, supported versions and official API requirements before use.
- **Postbase:** https://github.com/postbasehq/postbase — open-source scheduler; its repository lists X, LinkedIn, Bluesky, Mastodon, TikTok and YouTube as available, with Instagram/Facebook/Threads described as coming soon at research time. Do not assume Meta channels work today.
- **OpenPost:** https://github.com/getopenpost/openpost — self-hosted publishing platform with many integrations; each integration has different permissions and feature limits. Check current repository status, licence and deployment needs.
- **Listmonk:** https://github.com/knadh/listmonk — mailing-list/newsletter manager; requires a server/database and SMTP sending service. It is not an email account or free delivery provider.
- **Mautic:** https://github.com/mautic/mautic — larger marketing automation platform; hosting, maintenance, and mail delivery are still required.
- **Matomo:** https://github.com/matomo-org/matomo — self-hosted web analytics; hosting and privacy/cookie compliance still apply.
- **Umami:** https://github.com/umami-software/umami — lightweight analytics; self-hosting requires infrastructure, and hosted plans have their own limits.
- **Chatwoot:** https://github.com/chatwoot/chatwoot — customer messaging inbox; self-hosting and each channel's provider API remain required. It is not a WhatsApp API replacement.
- **Matrix / Element:** https://github.com/element-hq/element-web — alternative open communication ecosystem for communities who choose to use it, not a replacement for reaching people who only use WhatsApp.

Do not add all of these to production at once. The current ₹0 environment may not have an always-on server, database, domain, SMTP relay or GPU. Installing heavy stacks on GitHub-hosted runners is not a durable deployment strategy.

## Platform matrix

| Need | Zero-budget first step | What still depends on external providers |
|---|---|---|
| Company website | Portable static site in repo; check eligible free host terms | Hosting terms, custom domain if desired |
| Content creation | Local templates + repository | Image/video tools and licences if used |
| Social posting | Channel-ready exports + manual publishing checklist | Platform accounts, APIs, permissions and rules |
| Scheduling | GitHub Actions generates reminders/content pack | Actions availability; actual publication needs approved adapter |
| Email outreach | Personalized draft + real mailbox | Mailbox access, deliverability, anti-spam laws |
| Newsletter | Build consent-based list; evaluate listmonk | Server, SMTP provider, unsubscribe and compliance |
| WhatsApp contact | Owner-configured click-to-chat link | WhatsApp app/number and user action |
| WhatsApp automation | Keep disabled until approved official API setup | Meta Business Platform, WABA/number setup, policies and possible fees |
| Alternative chat | Email/contact form/phone; optional Telegram/Discord/Matrix | Recipient must use the chosen channel; bots still need tokens/config |
| Paid advertising | Start with organic posts and track results | Ads accounts, billing, ad platform approval and actual ad budget |
| Analytics | UTM links + manual public metrics log | Analytics access and privacy compliance |

## Ads without Meta dependence

- Start with organic marketing and measurable links; the business has a ₹0 budget.
- Prepare ad creative/copy that can later be adapted to Google Ads, LinkedIn Ads, Reddit Ads, Pinterest Ads, or other suitable networks after checking current minimum spend, account eligibility and targeting rules.
- No paid campaign can be launched for ₹0 if the platform requires a spend balance. Do not create campaigns, enter payment details or change billing settings without explicit approval.
- Avoid ad automation that scrapes personal data, creates fake engagement, evades review, or targets sensitive attributes.

## Outreach and privacy rules

- Contact only relevant businesses using publicly listed business contact channels, one-to-one and with a useful personalized reason.
- Do not buy lists, scrape private contact details, send repeated bulk messages, or treat public availability as consent for newsletters.
- Track opt-outs and never contact an opted-out lead again.
- Keep lead names/contact details out of this public repository. Use anonymized IDs in public reports.
- Do not claim customers, published posts, clicks, conversions, or revenue unless verified.

## Implementation phases

### Phase 1 — no API keys
- Keep content, campaign calendar, approved copy and sanitized lead statistics in repo.
- Add a portable content pack exporter and CSV template.
- Add validation tests: every post has a platform, content, approval status, intended date, and publication evidence field.
- Produce copy-ready assets for channels that can be posted manually.

### Phase 2 — safe optional adapters
- For each network, document official API docs, supported post types, app review requirements, rate limits, access cost, credential scopes and tests.
- Add adapters one by one; default disabled. A missing secret or failed auth must stop publishing and preserve the draft.
- Keep a human approval gate before external publishing and advertising.

### Phase 3 — email/contact automation
- Begin with individual email drafts and click-to-chat links.
- Add a sending provider only after verified free-tier terms, consent workflow, unsubscribe/bounce handling and approval. Never commit SMTP credentials.
- Keep WhatsApp automation optional, not a critical dependency.

### Phase 4 — measurement
- Record post URL, timestamp, reach/engagement where available, link clicks and verified leads.
- Report results with their source and date; no inferred revenue.

## Acceptance criteria

- [ ] Business content remains readable/exportable if every social account is disconnected.
- [ ] No secret, contact list, or customer data is committed to the public repository.
- [ ] Drafting and build/report generation run without paid API keys.
- [ ] External publishing is disabled unless a provider-specific adapter has been tested and approved.
- [ ] No system claims that a message/post was sent or a sale happened without evidence.
- [ ] Website and campaign files can be moved to another host without a rewrite.
- [ ] WhatsApp/Meta is optional; alternative contact routes remain available.

## Sources checked on 26 October 2026

- Pendpost repository: https://github.com/pendpost/pendpost
- Postbase repository: https://github.com/postbasehq/postbase
- OpenPost repository: https://github.com/getopenpost/openpost
- Listmonk repository: https://github.com/knadh/listmonk
- Mautic repository: https://github.com/mautic/mautic
- Chatwoot repository: https://github.com/chatwoot/chatwoot
- Matomo repository: https://github.com/matomo-org/matomo
- Umami repository: https://github.com/umami-software/umami
- Social scheduler comparison notes: https://www.postbase.so/blog/best-open-source-social-media-schedulers
- Open-source email tool comparison: https://opensourcepicks.com/categories/email-marketing/

This document is a research plan, not proof that any of these external tools has been installed, connected, deployed, or tested in this repository.
