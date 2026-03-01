#!/usr/bin/env python3
"""Inject site-wide Organization and WebSite JSON-LD into static pages."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://bestdealsonline.us"

ORG_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Best Online Deals",
    "url": SITE_URL,
    "logo": f"{SITE_URL}/assets/og-default.svg",
    "sameAs": [],
}

WEBSITE_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "Best Online Deals",
    "url": SITE_URL,
}

LD_JSON_RE = re.compile(
    r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)

HEAD_CLOSE_RE = re.compile(r"</head>", re.IGNORECASE)


def render_json_ld(payload: dict) -> str:
    content = json.dumps(payload, indent=2)
    indented = "\n".join(f"    {line}" for line in content.splitlines())
    return f"  <script type=\"application/ld+json\">\n{indented}\n  </script>"


def has_schema_type(blocks: list[str], schema_type: str) -> bool:
    matcher = re.compile(
        rf"[\"']@type[\"']\s*:\s*[\"']{re.escape(schema_type)}[\"']",
        re.IGNORECASE,
    )
    return any(matcher.search(block) for block in blocks)


def inject_schema(html: str) -> str:
    blocks = [m.group(1) for m in LD_JSON_RE.finditer(html)]
    needs_org = not has_schema_type(blocks, "Organization")
    needs_website = not has_schema_type(blocks, "WebSite")

    if not needs_org and not needs_website:
        return html

    new_blocks: list[str] = []
    if needs_org:
        new_blocks.append(render_json_ld(ORG_SCHEMA))
    if needs_website:
        new_blocks.append(render_json_ld(WEBSITE_SCHEMA))

    close_head = HEAD_CLOSE_RE.search(html)
    if not close_head:
        return html

    insert = "\n" + "\n\n".join(new_blocks) + "\n"
    return html[: close_head.start()] + insert + html[close_head.start() :]


def iter_html_files():
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith("app/"):
            continue
        if "/node_modules/" in rel or rel.startswith("node_modules/"):
            continue
        yield p


def main() -> None:
    changed = 0
    scanned = 0

    for path in iter_html_files():
        scanned += 1
        before = path.read_text(encoding="utf-8", errors="ignore")
        after = inject_schema(before)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed += 1

    print(f"scanned={scanned} changed={changed}")


if __name__ == "__main__":
    main()
