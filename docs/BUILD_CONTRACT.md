# Build Contract

This document defines the input and output contract for engine builds.

## Inputs

Build command:

```bash
python -m app.build --static --skip-assets --site-config <path>
```

Environment variables:

- `CONTENT_ROOT`: root path where content repository is available.
- `SITE_BASE`: deployment base path (for GitHub Pages project sites, use `/<repo>/`).
- `STATIC_SITE_DIR`: output directory (default `dist`).
- `VITE_BASE`: frontend asset base path (usually `${SITE_BASE}static/itso/dist/`).

Config requirements (`site config` JSON):

- Must include `posts` field.
- `posts` can be relative to `CONTENT_ROOT`.
- Optional `theme.id` selects a theme definition from `themes/<id>.json`.
- Optional `theme.overrides` merges token overrides into the selected theme.
- Optional `pinned_post_ids` (list of up to 3 article ids) pins posts to the top of listings.
- Optional `base_url` (absolute URL, no trailing slash) enables `sitemap.xml` and `robots.txt` generation.

Theme files:

- Theme definitions directory defaults to `themes/` (override with `THEMES_DIR` or `--themes-dir`).
- Missing/invalid theme id falls back to `themes/default.json`.
- Optional extra theme stylesheet can be provided at `static/itso/themes/<id>.css`.

## Article Front Matter

Supported front matter is YAML. Required fields:

- `id` (lowercase letters, numbers, and dashes; must be unique across all posts)

Core fields:

- `title`
- `date` (recommended: `YYYY-MM-DD`)
- `summary`
- `tags` (list of strings; drives tag index pages)

Optional cover image:

- `cover` (string path, or object with `src` and `alt`; aliases: `cover_image`, `featured_image`)

Optional promotion fields:

- `mirror`:
	- `platform`
	- `url`
	- `label`
- `social_links` (list):
	- `name`
	- `url`
	- `label`
- `call_to_action`:
	- `title`
	- `text`
	- `label`
	- `url`

## Outputs

Output directory contains:

- `index.html`
- `posts/index.html`
- `posts/<slug>/index.html`
- `tags/index.html`
- `tags/<slug>/index.html`
- `404.html`
- `static/**`
- `build-manifest.json`
- `.nojekyll`
- `sitemap.xml` (only when `base_url` is set in site config)
- `robots.txt` (only when `base_url` is set in site config)

## build-manifest.json

Fields:

- `generated_at`
- `site_base`
- `content_root`
- `site_config_path`
- `output_dir`
- `article_count`
- `html_count`
- `html_files`
- `warnings`

## Exit codes

- `0`: success
- `1`: input/config validation error
- `2`: command/subprocess execution error
