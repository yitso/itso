# Consumer Repository Guide

This repository is a build engine. Your real blog/content repository should contain:

- site config JSON
- markdown posts
- optional content-local static files

## Minimal content repository structure

```text
configs/
  site.json
content/
  posts/
    hello.md
```

Example `configs/site.json`:

```json
{
  "lang": "en",
  "date_locale": "en",
  "i18n_file": "i18n/en.json",
  "posts": "content/posts",
  "site": {
    "title": "My Site",
    "nav": "My Site"
  }
}
```

## Reusable workflow usage

In your content repository, create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Content Site

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    uses: yitso/itso/.github/workflows/build-engine.yml@main
    with:
      site_base: /${{ github.event.repository.name }}/
      content_repo: ${{ github.repository }}
      content_ref: ${{ github.ref_name }}
      site_config_path: configs/site.json
      output_dir: dist

  package-pages:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: site-dist
          path: dist
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist

  deploy:
    needs: package-pages
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

## Cross-organization/private repository notes

- For private content repositories across organizations, pass `content_repo_token` secret when calling reusable workflow.
- Pin a stable engine tag instead of `@main` once version tags are published.
