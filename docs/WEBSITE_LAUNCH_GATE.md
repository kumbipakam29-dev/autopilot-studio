# Website launch gate — AutoPilot Digital Studio

**Status:** BLOCKED pending a real business contact route and repository Pages configuration. This is an internal checklist, not a claim that the site is live.

## Verified repository facts
- The current `main` branch contains the agent runtime workflow and runtime README.
- Website pages and two candidate GitHub Pages deployment workflows currently exist in draft pull requests, not on `main`.
- The website draft contains an empty `mailto:` link. The contact note explicitly says email/WhatsApp is not connected.
- The website's fictional portfolio samples are labelled as spec work and must remain so.
- The existing Topmate toolkit URL is a digital-product checkout path, not a substitute for a confirmed service-enquiry contact route.

## Required before launch
1. Choose one deployment workflow only. Prefer `.github/workflows/deploy-pages.yml` from PR #29 if its checks are satisfactory; do not merge the overlapping workflow in PR #34 as well.
2. Configure a real contact route: business email, official Instagram profile, or WhatsApp Business link. Do not invent a phone number or email. Confirm the user approves which public contact detail to publish.
3. Replace the empty `mailto:` link and remove the warning that contact is not configured.
4. Ensure the portfolio page is linked and all samples are labelled fictional spec work.
5. Run the website QA script and the Python unit tests. Record actual results; do not infer passing from workflow configuration.
6. Merge the website and chosen deployment changes only after review.
7. In repository Settings → Pages, set Source to GitHub Actions if required by the chosen workflow.
8. Verify the resulting Pages deployment run succeeds and the public URL loads on mobile. Test the contact link itself before any promotion.
9. Only then prepare public promotion. Outreach and publishing still require explicit approval.

## Launch decision
- [ ] Public contact route supplied and approved
- [ ] One deployment workflow selected
- [ ] Website QA passes
- [ ] Python tests pass
- [ ] Deployment run succeeds
- [ ] Public site and contact route manually verified
- [ ] Public promotion approved

## Safety and truthfulness
No customer messages have been sent as part of this checklist. Do not claim the website is live, enquiries are working, customers exist, or payments were received without direct evidence.
