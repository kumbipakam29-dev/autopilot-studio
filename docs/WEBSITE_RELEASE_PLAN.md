# Website release plan — AutoPilot Digital Studio

**Status:** Release is blocked. This file is a decision and validation plan, not proof of deployment.
**Last reviewed:** 2026-10-27

## Known draft changes
- PR #29: website pages and `.github/workflows/deploy-pages.yml`
- PR #34: a second, overlapping Pages deployment workflow
- PR #37: website QA workflow and checker; intentionally flags missing contact details
- PR #41: enquiry form with backend not configured; do not present it as working

## Safe release order
1. Choose a real public contact route (official Instagram profile, business email, or WhatsApp Business link). Confirm that the owner approves publishing it. Never invent contact information.
2. Review PR #29's two HTML pages for accuracy, mobile usability, accessibility, fictional-spec labels, and contact placeholders.
3. Keep exactly one Pages deployment workflow. Do not merge PR #34's overlapping workflow if PR #29's `deploy-pages.yml` is selected.
4. Incorporate the QA checker from PR #37 without importing duplicate copies of the website or prospect docs. Update the checker only if the contact route and current HTML structure justify the change.
5. Run the checker against the actual website files and run the Python unit tests. Record command output and failures.
6. Review GitHub Pages eligibility and repository settings. Do not assume a commercial service website is permitted without checking the applicable Pages terms.
7. Merge the reviewed changes only after the contact route and QA are resolved.
8. Confirm the Actions deployment run succeeded, find the actual Pages URL from repository settings/output, open it on mobile, and test all navigation/contact links.
9. Keep the site unpublished until the user explicitly approves public release and any public promotion.

## Contact-route decision
Accept one of:
- Official Instagram profile URL
- Business email address
- WhatsApp Business click-to-chat URL

If none is approved, leave the site as a private draft and continue preparing offline portfolio and outreach materials.

## Release checklist
- [ ] Public contact route supplied and approved
- [ ] Empty `mailto:` removed or replaced
- [ ] Portfolio samples remain clearly marked fictional spec work
- [ ] No unsupported client/results/testimonial claims
- [ ] One deployment workflow only
- [ ] Website checker passes on actual site
- [ ] Unit tests pass
- [ ] Hosting eligibility and repository settings reviewed
- [ ] Deployment run passes
- [ ] Public URL and contact route manually tested
- [ ] User approves public release

## Truth rules
A merged PR is not a deployed website. A configured workflow is not a successful deployment. A draft message is not outreach. A checkout link is not a received payment. Record evidence for each status transition.
