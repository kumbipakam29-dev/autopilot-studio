# GitHub Pages website deployment

This repository's business site draft is in `website/index.html`. The workflow `.github/workflows/deploy-website.yml` can deploy that folder to GitHub Pages after it is merged to `main`.

## Before it can go live
1. Review and merge the website pull request and this deployment-workflow pull request.
2. In the repository, open **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Open **Actions** and run **Deploy AutoPilot Studio website to GitHub Pages** with **Run workflow**, or push a later change under `website/`.
5. Wait for the workflow to finish successfully. Open the Pages URL shown by the deployment job and check it on a phone.
6. Test every navigation link, package detail, contact method, and form before sharing the site.

## Important contact requirement
The current draft website may contain a placeholder instead of a working contact address. Do not publish it as a finished sales site until the owner has chosen and verified a contact method. Do not invent an email address or put credentials in HTML.

## Free-tier / public-repository caveats
- GitHub Pages is static hosting. It does not provide a backend, email sending, CRM, private lead storage, or a payment processor.
- Public repository content can be viewed by anyone. Never place private prospect data, client files, tokens, or account credentials in the website or repository.
- Hosting availability and terms can vary by account and repository settings; confirm GitHub's current Pages terms before using it for a commercial business site.
- A successful workflow means deployment completed; it does not prove the contact channel works or that customers have visited the site.

## Workflow behavior
- Runs on pushes to `main` that change `website/**` or this workflow file.
- Can also be started manually from the Actions tab.
- Requires GitHub Pages to be enabled and the source set to GitHub Actions.
