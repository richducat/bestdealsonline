#!/usr/bin/env python3
"""Insert a complete, compact link index into each category hub page so
every price-tier and seasonal/use-case page in that vertical gets a real
internal link from its hub -- not just the ~15-30 pages hand-picked into
the "Trending" / "Browse" sections.

This is what actually fixes the ~560 orphan pages (pages with zero
internal inbound links anywhere on the site): before this, hub pages
only linked to a handful of pages per category; this adds the rest as a
compact per-seed row of pill links (one row per product, one pill per
price tier / use case) so page weight stays reasonable even with 100+
pages per hub.

Idempotent: re-running replaces the previously-inserted index (marked by
HTML comments) rather than duplicating it.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from categorize_seeds import CATEGORY_HUBS, classify  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

START_MARKER = "<!-- hub-link-index:start -->"
END_MARKER = "<!-- hub-link-index:end -->"
FOOTER_RE = re.compile(r"<footer class='border-t")

PRICE_RE = re.compile(r"^(?P<seed>.+)-under-(?P<price>\d+)$")
VARIANT_RE = re.compile(
    r"^(?P<seed>.+)-(?P<variant>dorm|travel|small-apartment|black-friday-deals|christmas-deals|cyber-monday-deals)$"
)

VARIANT_LABELS = {
    "dorm": "Dorm",
    "travel": "Travel",
    "small-apartment": "Small apt",
    "black-friday-deals": "Black Friday",
    "christmas-deals": "Christmas",
    "cyber-monday-deals": "Cyber Monday",
}
VARIANT_ORDER = list(VARIANT_LABELS.keys())


def collect_seed_pages() -> dict[str, dict]:
    """Return {seed_slug: {"phrase": str, "pages": [(url, label, sort_key)]}}"""
    seeds: dict[str, dict] = {}
    for p in sorted(ROOT.glob("*.html")):
        stem = p.stem
        m = PRICE_RE.match(stem)
        if m:
            seed_slug = m.group("seed")
            price = int(m.group("price"))
            entry = seeds.setdefault(seed_slug, {"phrase": seed_slug.replace("-", " "), "pages": []})
            entry["pages"].append((f"/{p.name}", f"${price}", (0, price)))
            continue
        m = VARIANT_RE.match(stem)
        if m:
            seed_slug = m.group("seed")
            variant = m.group("variant")
            entry = seeds.setdefault(seed_slug, {"phrase": seed_slug.replace("-", " "), "pages": []})
            entry["pages"].append((f"/{p.name}", VARIANT_LABELS[variant], (1, VARIANT_ORDER.index(variant))))
    for entry in seeds.values():
        entry["pages"].sort(key=lambda t: t[2])
    return seeds


def build_index_section(category: str, rows: list[tuple[str, list[tuple[str, str]]]]) -> str:
    row_html = []
    for phrase, links in rows:
        pills = "".join(
            f"<a class='px-2.5 py-1 rounded-full border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700' href='{html.escape(url, quote=True)}'>{html.escape(label)}</a>"
            for url, label in links
        )
        row_html.append(
            "<div class='flex flex-wrap items-center gap-2 py-2 border-b border-slate-100 last:border-0'>"
            f"<span class='text-sm font-bold text-slate-900 min-w-[10rem] mr-1'>{html.escape(phrase.title())}</span>"
            f"<div class='flex flex-wrap gap-1.5'>{pills}</div>"
            "</div>"
        )
    return (
        f"{START_MARKER}\n"
        f"      <section class=\"mt-8 bg-white rounded-2xl border border-slate-200 shadow-sm p-6\">\n"
        f"        <h2 class=\"text-2xl font-extrabold\">Every {html.escape(category)} page</h2>\n"
        f"        <p class=\"text-slate-600 mt-2\">Every price tier and use-case page in this category -- {sum(len(l) for _, l in rows)} links across {len(rows)} products.</p>\n"
        f"        <div class=\"mt-6\">\n"
        + "\n".join(row_html)
        + "\n        </div>\n"
        f"      </section>\n"
        f"      {END_MARKER}\n"
    )


def strip_existing_index(text: str) -> str:
    pattern = re.compile(
        r"[ \t]*" + re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER) + r"[ \t]*\n?",
        re.S,
    )
    return pattern.sub("", text)


def main() -> None:
    seeds = collect_seed_pages()
    by_category: dict[str, list[tuple[str, list[tuple[str, str]]]]] = {c: [] for c in CATEGORY_HUBS}
    for seed_slug, entry in seeds.items():
        cat = classify(entry["phrase"])
        links = [(url, label) for url, label, _key in entry["pages"]]
        by_category[cat].append((entry["phrase"], links))

    for cat, rows in by_category.items():
        rows.sort(key=lambda r: r[0])
        hub_path = ROOT / CATEGORY_HUBS[cat].lstrip("/")
        if not hub_path.exists():
            print(f"SKIP {cat}: {hub_path} not found")
            continue
        text = hub_path.read_text(encoding="utf-8")
        text = strip_existing_index(text)
        section = build_index_section(cat, rows)
        m = FOOTER_RE.search(text)
        if not m:
            print(f"SKIP {cat}: no footer anchor found in {hub_path.name}")
            continue
        insert_at = m.start()
        new_text = text[:insert_at] + section + "    " + text[insert_at:]
        hub_path.write_text(new_text, encoding="utf-8")
        total_links = sum(len(l) for _, l in rows)
        print(f"{cat}: {len(rows)} products, {total_links} links -> {hub_path.name}")


if __name__ == "__main__":
    main()
