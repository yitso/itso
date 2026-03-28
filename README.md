# Itso 

## A Simple Static Blog System

It originally came from a piece of code I wrote back in 2017 while learning Flask, and I’ve been using it as the backend for my personal website ever since. I’ve thought many times about abandoning it and rewriting it, since its technical design may no longer fit modern web standards, but due to time constraints I never followed through. Now, however, I’ve made up my mind to start maintaining it.

## Engine Repository Model

This repository is designed to act as a build engine.

- Engine repository (this repo): templates, renderer, build workflow.
- Content repository: config file + markdown files.

The content repository calls this engine via reusable GitHub Actions workflow, builds static files, then deploys to GitHub Pages.

See:

- `docs/CONSUMER_REPO.md`
- `docs/BUILD_CONTRACT.md`

## Run Modes

This template now supports two modes:

1. Static-first mode (default for deployment): build full HTML and publish to GitHub Pages.
2. Optional Flask mode: keep local development or non-static deployment flexibility.

## Local Development

Install dependencies:

```bash
npm ci
pip install -r requirements.txt
```

Start Flask mode:

```bash
python main.py
```

By default, this starts at http://127.0.0.1:8000.

## Build Static Site

Build both frontend assets and static pages:

```bash
npm run build
```

Output folder:

```bash
dist/
```

Preview static output locally:

```bash
npx serve dist
```

## Theme Configuration (Pluggable)

Theme selection is configuration-driven and fixed at build/runtime startup.

1. Choose a theme id in site config:

```json
"theme": {
	"id": "default"
}
```

2. Define design tokens in `themes/<theme-id>.json`.
3. Optionally add theme extension CSS at `static/itso/themes/<theme-id>.css`.

The system automatically falls back to `themes/default.json` when a configured theme id is missing or invalid.

Optional token overrides can be added per site config:

```json
"theme": {
	"id": "default",
	"overrides": {
		"accent": "#7cf6cf"
	}
}
```

## GitHub Pages (Project Site)

For a repository site, set site base to `/<repo>/`.

One-off local test:

```bash
SITE_BASE="/your-repo/" VITE_BASE="/your-repo/static/itso/dist/" npm run build
```

Workflow file is included at `.github/workflows/deploy-pages.yml` and deploys on push to `main`.

## Reusable Workflow

Engine reusable workflow:

- `.github/workflows/build-engine.yml`

Use it from your content repository to build static pages from external markdown/config sources.

