#!/usr/bin/env python3
"""
Create/update _llms_sidecars/*.md for each _posts/*.md so each post gets
  <post canonical URL>/llms.txt
Plain text is rendered by _layouts/post-llms.html from the post body (HTML stripped).

Run after adding a post:  python3 scripts/sync-llms-sidecars.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"
SIDE = ROOT / "_llms_sidecars"

POST_NAME_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.md$")
PERMALINK_RE = re.compile(r"^permalink:\s*(.+?)\s*$", re.MULTILINE)


def extract_permalink(raw: str) -> str | None:
    m = PERMALINK_RE.search(raw)
    if not m:
        return None
    s = m.group(1).strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    return s.strip() or None


def default_base_from_name(filename: str) -> str | None:
    m = POST_NAME_RE.match(filename)
    if not m:
        return None
    y, mo, d, slug = m.groups()
    return f"/{y}/{mo}/{d}/{slug}"


def main() -> int:
    if not POSTS.is_dir():
        print("No _posts/", file=sys.stderr)
        return 1
    SIDE.mkdir(exist_ok=True)
    for path in sorted(POSTS.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        perm = extract_permalink(raw)
        if perm:
            base = perm.strip()
            if not base.startswith("/"):
                base = "/" + base
            base = base.rstrip("/")
        else:
            b = default_base_from_name(path.name)
            if not b:
                print("skip (bad name):", path.name, file=sys.stderr)
                continue
            base = b
        llms_url = f"{base}/llms.txt"
        m = POST_NAME_RE.match(path.name)
        slug = m.group(4) if m else path.stem
        stub = SIDE / f"{slug}.md"
        rel = f"_posts/{path.name}"
        content = f"""---
layout: post-llms
post_path: {rel}
permalink: {llms_url}
markdown: false
---
"""
        prev = stub.read_text(encoding="utf-8") if stub.exists() else None
        if prev != content:
            stub.write_text(content, encoding="utf-8")
            print("wrote", stub.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
