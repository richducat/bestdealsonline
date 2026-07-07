#!/usr/bin/env python3
"""Add BreadcrumbList JSON-LD (Home > Category hub > Page) to every
enriched long-tail page, and CollectionPage + ItemList JSON-LD to the 8
category hub pages listing their full page inventory.

Both are accurate representations of what's actually on each page (real
nav hierarchy, real link lists) -- unlike Product/Offer schema, which
would misrepresent data this site doesn't have (no live price/availability
is displayed on-site). Idempotent via marker comments.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from categorize_seeds import CATEGORY_HUBS, classify  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://bestdealsonline.us"

BREADCRUMB_START = "<!-- breadcrumb-schema:start -->"
BREADCRUMB_END = "<!-- breadcrumb-schema:end -->"
COLLECTION_START = "<!-- collection-schema:start -->"
COLLECTION_END = "<!-- collection-schema:end -->"

PRICE_RE = re.compile(r"^(?P<seed>.+)-under-(?P<price>\d+)$")
VARIANT_RE = re.compile(
    r"^(?P<seed>.+)-(?P<variant>dorm|travel|small-apartment|black-friday-deals|christmas-deals|cyber-monday-deals)$"
)
HEAD_CLOSE_RE = re.compile(r"</head>", re.I)


def strip_marked(text: str, start: str, end: str) -> str:
    pattern = re.compile(r"[ \t]*" + re.escape(start) + r".*?" + re.escape(end) + r"[ \t]*\n?", re.S)
    return pattern.sub("", text)


def category_label(cat: str) -> str:
    return cat.title()


def inject_breadcrumbs() -> int:
    count = 0
    for p in sorted(ROOT.glob("*.html")):
        stem = p.stem
        m = PRICE_RE.match(stem)
        variant_label = None
        if m:
            seed_slug = m.group("seed")
        else:
            m = VARIANT_RE.match(stem)
            if not m:
                continue
            seed_slug = m.group("seed")

        seed_phrase = seed_slug.replace("-", " ")
        cat = classify(seed_phrase)
        hub_url = CATEGORY_HUBS[cat]
        page_title = seed_phrase.title()

        breadcrumb = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": f"{category_label(cat)} deals", "item": f"{SITE}{hub_url}"},
                {"@type": "ListItem", "position": 3, "name": page_title, "item": f"{SITE}/{p.name}"},
            ],
        }
        block = (
            f"  {BREADCRUMB_START}\n"
            f"  <script type=\"application/ld+json\">\n"
            f"  {json.dumps(breadcrumb, indent=2)}\n"
            f"  </script>\n"
            f"  {BREADCRUMB_END}\n"
        )

        text = p.read_text(encoding="utf-8")
        text = strip_marked(text, BREADCRUMB_START, BREADCRUMB_END)
        m2 = HEAD_CLOSE_RE.search(text)
        if not m2:
            continue
        new_text = text[: m2.start()] + block + text[m2.start() :]
        if new_text != text:
            p.write_text(new_text, encoding="utf-8")
            count += 1
    return count


def inject_hub_collections() -> int:
    # Reuse the same seed/page collection logic as build_hub_link_index.py
    seeds: dict[str, dict] = {}
    for p in sorted(ROOT.glob("*.html")):
        stem = p.stem
        m = PRICE_RE.match(stem)
        if m:
            seed_slug = m.group("seed")
            entry = seeds.setdefault(seed_slug, {"phrase": seed_slug.replace("-", " "), "urls": []})
            entry["urls"].append(f"/{p.name}")
            continue
        m = VARIANT_RE.match(stem)
        if m:
            seed_slug = m.group("seed")
            entry = seeds.setdefault(seed_slug, {"phrase": seed_slug.replace("-", " "), "urls": []})
            entry["urls"].append(f"/{p.name}")

    by_category: dict[str, list[str]] = {c: [] for c in CATEGORY_HUBS}
    for seed_slug, entry in seeds.items():
        cat = classify(entry["phrase"])
        by_category[cat].extend(entry["urls"])

    count = 0
    for cat, urls in by_category.items():
        hub_path = ROOT / CATEGORY_HUBS[cat].lstrip("/")
        if not hub_path.exists():
            continue
        urls = sorted(set(urls))
        item_list = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": f"{category_label(cat)} Deals",
            "url": f"{SITE}{CATEGORY_HUBS[cat]}",
            "mainEntity": {
                "@type": "ItemList",
                "numberOfItems": len(urls),
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "url": f"{SITE}{u}"}
                    for i, u in enumerate(urls)
                ],
            },
        }
        block = (
            f"  {COLLECTION_START}\n"
            f"  <script type=\"application/ld+json\">\n"
            f"  {json.dumps(item_list, indent=2)}\n"
            f"  </script>\n"
            f"  {COLLECTION_END}\n"
        )
        text = hub_path.read_text(encoding="utf-8")
        text = strip_marked(text, COLLECTION_START, COLLECTION_END)
        m = HEAD_CLOSE_RE.search(text)
        if not m:
            continue
        new_text = text[: m.start()] + block + text[m.start() :]
        hub_path.write_text(new_text, encoding="utf-8")
        count += 1
    return count


def main() -> None:
    n1 = inject_breadcrumbs()
    n2 = inject_hub_collections()
    print(f"breadcrumb schema added to {n1} pages; collection schema added to {n2} hubs")


if __name__ == "__main__":
    main()
