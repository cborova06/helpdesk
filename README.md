div align=center markdown=1

img src=.githubhd-logo.svg alt=BRV Helpdesk logo width=80
h1BRV Helpdeskh1

Ticketing, knowledge sharing and automation tailored for BRV customers

a href=httpswww.brvsoftware.com.trilk-talebinizi-olusturunDocumentationa
div

## What is BRV Helpdesk
BRV Helpdesk is our customized service desk built on the Helpdesk codebase. It keeps agent workflows fast, streamlines SLAs and automation, and gives you fine-grained control over ticket routing, KB sharing, and reply templates.

### What makes it different

- Company branding & language Every screen, canned response and knowledge base card reflects BRV’s tone and visual identity.
- Noise-free automation Assignment rules, SLA priorities and email templates are tuned for our teams.
- Content-first knowledge base Articles live alongside tickets so customers self-serve on common issues before escalating.
- Agent productivity tooling Shortcuts, canned responses and bulk actions were added where our teams needed them.

### Screens in focus

![Agent List View](.githubAgentListView.png)
![Knowledge Base](.githubKB.png)
![Article Search](.githubSearch2.png)

## Installation

These instructions assume you already have a working bench setup with Frappe version 15 or newer.

1. Create or switch to your bench `bench new-bench brv-bench && cd brv-bench` (skip if already inside your main bench).
2. Clonepull the latest app `bench get-app httpsgithub.comcborova06helpdesk --branch main`.
3. Install the app on your desired site `bench --site your-site install-app helpdesk`.
4. Run `bench build` and `bench restart` to apply the web assets and load the fixes.

If your site is not yet created, `bench new-site helpdesk.local` will handle databaseuser setup before step 3.

## Deployment & hosting guidance

We run BRV Helpdesk alongside other services in our own infrastructure

- Offline deployments Use `bench setup production user` inside the bench directory, then configure Nginx and Supervisor using the generated files.
- Containerized development Point the local `appshelpdeskdesk` frontend at your bench site using `yarn dev --host your-dev-host` and reverse-proxy it through Nginx if necessary.
- Secrets & environment Keep API keys inside `sitescommon_site_config.json` and never commit them. Use `bench set-config` for runtime values so they are replicated across deployments.

## Development workflow

### Backend changes

1. Work from `homefrappefrappe-benchappshelpdesk`.
2. Run `bench start` and use `bench --site site console` to iterate on doctypes, scripts, and workflows.
3. Capture new fixtures under `helpdeskfixtures` when you customize settings so they can be versioned.

### Frontend changes

1. Open a new terminal `cd appshelpdeskdesk`.
2. Install dependencies once with `yarn install`.
3. Run `yarn dev` (or `yarn dev --host hostname`) to start Vite and preview against your backend.
4. Commit Vue component edits and run `bench build --app helpdesk` before deploying.

### Tests and QA

- Run `bench run-tests --app helpdesk` for Python doctests and unit tests.
- Frontend assets can be checked with `yarn test` inside `desk`.
- Use `bench doctor` to confirm schema integrity before release.

## Compatibility

 Helpdesk branch  Frappe version 
---------------------------------
 main             v15+           

## Need help

- Reach the internal BRV Helpdesk channel with specifics on the ticket or automation issue.
- Share reproducible steps and stack traces when reporting bugs so we can act faster.

If you have documentation to add, update this README or the `docs` folder so future contributors get the same context.
