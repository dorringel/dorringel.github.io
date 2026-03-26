# dorringel.github.io

Personal site (Jekyll on GitHub Pages). This README is for **authors / future you** — it is **not** published on the site (see `exclude` in `_config.yml`).

## New blog post

1. Add `_posts/YYYY-MM-DD-slug.md` with normal front matter (`title`, `description`, optional `permalink`, `redirect_from`, etc.).
2. Run **`python3 scripts/sync-llms-sidecars.py`** — creates/updates `_llms_sidecars/<slug>.md` so each post has a plain-text mirror at **`<canonical-post-url>/llms.txt`** (for tools / LLM-friendly text).
3. Commit **`_posts/...`** and **`_llms_sidecars/...`** together.
4. After deploy, spot-check **`https://dorringel.github.io/<your-post-path>/llms.txt`**.

## llms.txt overview

- **Site index:** `/llms.txt` — generated from `llms.md` (Liquid + `site.posts`).
- **Per post:** `…/llms.txt` — content from `_layouts/post-llms.html` (HTML body stripped from the post).

## Local preview

Requires Ruby/Jekyll (e.g. `bundle install && bundle exec jekyll serve`). GitHub Pages runs the same build on push.
