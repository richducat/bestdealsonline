#!/usr/bin/env python3
"""Generate ~200 new Amazon-only long-tail SEO pages.

Strategy:
- Programmatically combine proven shopping intents with budgets and use-cases.
- Avoid duplicates by skipping existing slugs.
- Use the existing build_page() from scripts/gen_longtail_pages.py for consistent styling.

After running:
- Run: node scripts/inject-analytics.mjs
- Run: node scripts/gen-sitemap.mjs
"""

from __future__ import annotations

from pathlib import Path
import re

# Reuse the existing HTML template builder
import sys

# Ensure repo root is on sys.path so we can import scripts/gen_longtail_pages.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.gen_longtail_pages import build_page

ROOT = Path(__file__).resolve().parents[1]

CATEGORIES = {
    "electronics": "/electronics-deals.html",
    "home": "/home-deals.html",
    "kitchen": "/kitchen-deals.html",
    "tools": "/tools-deals.html",
    "kids": "/kids-deals.html",
    "beauty": "/beauty-deals.html",
    "fitness": "/fitness-deals.html",
    "pets": "/pets-deals.html",
}

PRICE_POINTS = [15, 20, 25, 30, 50, 75, 100]

# High-intent seed queries by category (hand-picked; no keyword planner required)
SEEDS: dict[str, list[str]] = {
    "electronics": [
        "usb c charger",
        "usb c cable",
        "wireless charger",
        "power bank",
        "bluetooth speaker",
        "noise cancelling headphones",
        "gaming headset",
        "webcam",
        "wifi router",
        "surge protector",
        "smart plug",
        "smart light bulbs",
        "hdmi cable",
        "screen protector",
        "phone car mount",
        "dash cam",
    ],
    "home": [
        "bed sheets",
        "mattress topper",
        "blackout curtains",
        "storage bins",
        "shoe rack",
        "desk lamp",
        "humidifier",
        "space heater",
        "air purifier",
        "steam mop",
        "trash can",
        "shower curtain",
        "shower head",
        "doormat",
        "closet organizer",
    ],
    "kitchen": [
        "air fryer",
        "air fryer accessories",
        "rice cooker",
        "coffee maker",
        "electric kettle",
        "blender",
        "toaster oven",
        "food scale",
        "meal prep containers",
        "nonstick cookware",
        "bento lunch box",
        "immersion blender",
    ],
    "tools": [
        "cordless drill",
        "tool set",
        "toolbox",
        "socket set",
        "extension cord",
        "tape measure",
        "laser level",
        "flashlight",
        "work gloves",
        "cable management",
    ],
    "kids": [
        "kids headphones",
        "kids backpack",
        "science kits",
        "learning toys",
        "building block sets",
        "board games",
        "kids water bottle",
        "toddler balance bike",
    ],
    "beauty": [
        "vitamin c serum",
        "retinol serum",
        "niacinamide serum",
        "sunscreen",
        "makeup brush set",
        "blow dryer",
        "flat iron",
        "electric toothbrush",
        "skincare fridge",
    ],
    "fitness": [
        "adjustable dumbbells",
        "resistance bands",
        "yoga mat",
        "foam roller",
        "ab roller",
        "pull up bar",
        "kettlebell",
        "massage gun",
        "fitness tracker",
    ],
    "pets": [
        "dog bed",
        "cat tree",
        "cat litter box",
        "pet water fountain",
        "pet grooming brush",
        "dog grooming kit",
        "interactive cat toy",
        "pet car seat cover",
    ],
}

USE_CASES = [
    ("dorm", "for dorm rooms"),
    ("travel", "for travel"),
    ("small-apartment", "for small apartments"),
]


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def make_page(
    *,
    slug: str,
    title: str,
    description: str,
    intro: str,
    quick_amz_label: str,
    quick_amz_query: str,
    quick_internal_href: str,
    quick_internal_label: str,
    queries: list[tuple[str, str]],
    related: list[tuple[str, str]],
) -> str:
    return build_page(
        slug=slug,
        title=title,
        description=description,
        intro=intro,
        quick_amz_label=quick_amz_label,
        quick_amz_query=quick_amz_query,
        quick_internal_href=quick_internal_href,
        quick_internal_label=quick_internal_label,
        queries=queries,
        related_links=related,
    )


def main():
    root = ROOT

    # Build candidate list
    candidates: list[dict] = []

    for cat, hub in CATEGORIES.items():
        for seed in SEEDS[cat]:
            # Budget variants
            for p in PRICE_POINTS:
                q = f"{seed} under ${p}"
                slug = f"{slugify(seed)}-under-{p}.html"
                candidates.append(
                    {
                        "slug": slug,
                        "title": f"Best {seed.title()} Deals Under ${p}",
                        "description": f"{seed.title()} under ${p}. Click through to see live prices on Amazon.",
                        "intro": f"If you're shopping for {seed} under ${p}, these quick Amazon searches cover the highest-intent variations people actually buy.",
                        "quick_amz_label": f"Shop {seed} under ${p} on Amazon",
                        "quick_amz_query": q,
                        "quick_internal_href": hub,
                        "quick_internal_label": f"{cat.title()} deals hub",
                        "queries": [
                            (q, "Core query"),
                            (f"best {seed} under ${p}", "Comparison intent"),
                            (f"{seed} deal under ${p}", "Deal intent"),
                        ],
                        "related": [
                            (hub, f"{cat.title()} deals hub"),
                            ("/best-deals-online-today.html", "Best deals online today"),
                            ("/best-deals-online.html", "Best deals online"),
                        ],
                    }
                )

            # Use-case variants (no price)
            for use_slug, use_label in USE_CASES:
                q = f"{seed} {use_label}"
                slug = f"{slugify(seed)}-{use_slug}.html"
                candidates.append(
                    {
                        "slug": slug,
                        "title": f"Best {seed.title()} {use_label.title()} (Amazon Picks)",
                        "description": f"{seed.title()} {use_label} — curated search shortcuts. Click through to see live prices on Amazon.",
                        "intro": f"These are Amazon search shortcuts for {seed} {use_label}, built for fast comparisons and quick buying decisions.",
                        "quick_amz_label": f"Shop {seed} {use_label} on Amazon",
                        "quick_amz_query": q,
                        "quick_internal_href": hub,
                        "quick_internal_label": f"{cat.title()} deals hub",
                        "queries": [
                            (q, "Core use-case query"),
                            (f"best {seed} {use_label}", "Comparison intent"),
                        ],
                        "related": [
                            (hub, f"{cat.title()} deals hub"),
                            ("/best-deals-online-today.html", "Best deals online today"),
                        ],
                    }
                )

    # Deduplicate by slug (keep first)
    seen = set()
    uniq = []
    for c in candidates:
        if c["slug"] in seen:
            continue
        seen.add(c["slug"])
        uniq.append(c)

    written = 0
    for c in uniq:
        out = root / c["slug"]
        if out.exists():
            continue
        html_txt = make_page(
            slug=c["slug"],
            title=c["title"],
            description=c["description"],
            intro=c["intro"],
            quick_amz_label=c["quick_amz_label"],
            quick_amz_query=c["quick_amz_query"],
            quick_internal_href=c["quick_internal_href"],
            quick_internal_label=c["quick_internal_label"],
            queries=c["queries"],
            related=c["related"],
        )
        out.write_text(html_txt, encoding="utf-8")
        written += 1
        print("wrote", out.name)
        if written >= 200:
            break

    print(f"done: wrote {written} new pages")


if __name__ == "__main__":
    main()
