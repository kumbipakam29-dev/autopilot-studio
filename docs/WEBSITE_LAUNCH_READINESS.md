# Website Launch Readiness — AutoPilot Digital Studio

Last reviewed: 2026-10-26

## Current assessment

The draft homepage exists at `website/index.html` on the website feature branch. It has a responsive layout, service descriptions, proposed packages, fictional portfolio samples labelled as spec work, process/FAQ sections, and no guaranteed-results claims.

**It is not ready to promote to customers yet.** The contact section currently includes an empty `mailto:` link and a note that contact email/WhatsApp is not connected. The only functioning button points to the existing AI Job Search Toolkit on Topmate, which is a separate digital product and not a service enquiry route.

## Launch blockers
1. Choose a business contact route that the owner can access: a dedicated business email, an official business WhatsApp link, or a public enquiry form. Do not invent contact details or use a private number without approval.
2. Replace the empty `mailto:` anchor and remove the “not connected” warning only after the new contact route has been tested.
3. Keep the Topmate job toolkit as a clearly separate digital product link; do not present it as a service enquiry or social-content checkout.
4. Verify package scope and proposed prices before publishing as an active offer. Current amounts are drafts.
5. Confirm GitHub Pages settings and check the deployed URL and mobile layout. A workflow file alone does not mean Pages is configured or the site is live.

## Pre-launch QA checklist
- [ ] Main page loads over HTTPS on mobile and desktop.
- [ ] All navigation anchors resolve.
- [ ] No empty links or placeholder contact details remain.
- [ ] Service enquiry path opens the intended channel and a test submission/message can be received.
- [ ] Topmate button clearly identifies the AI Job Search Toolkit as a separate product.
- [ ] Prices and deliverables match the owner-approved offer.
- [ ] Fictional portfolio samples remain labelled “spec work”.
- [ ] No invented testimonials, customer logos, client results or performance promises.
- [ ] Deployment workflow succeeds and the public URL is checked.
- [ ] No secrets, personal data or private lead lists are committed to the public repository.

## Conversion tracking (manual until a safe integration exists)
Record only verifiable events: enquiry received, reply sent, scope agreed, invoice/payment link sent, payment received. Keep prospects' personal contact data out of the public repository. A click is not a lead; an enquiry is not a sale; only verified payment counts as revenue.

## Free hosting reference
GitHub Pages supports public repositories on GitHub Free, but a maintainer must configure the Pages publishing source and the deployment must succeed. See the official instructions: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
