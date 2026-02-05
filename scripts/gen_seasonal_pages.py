#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.gen_longtail_pages import build_page

SITE = "https://bestdealsonline.us"

CATEGORIES = {
    "electronics": "/electronics-deals.html",
    "kids": "/kids-deals.html",
    "kitchen": "/kitchen-deals.html",
    "home": "/home-deals.html",
    "tools": "/tools-deals.html",
    "beauty": "/beauty-deals.html",
    "fitness": "/fitness-deals.html",
    "pets": "/pets-deals.html",
}

SEASONS = [
    ("black-friday", "Black Friday"),
    ("cyber-monday", "Cyber Monday"),
    ("christmas", "Christmas"),
]

# Buyer-intent product stems (we only link to Amazon search results)
SEEDS_BY_CAT = {
    "electronics": [
        "usb c charger",
        "power bank",
        "wireless charger",
        "noise cancelling headphones",
        "bluetooth speaker",
        "dash cam",
        "webcam",
        "wifi router",
    ],
    "kids": [
        "kids headphones",
        "science kits for kids",
        "learning toys",
        "building block sets",
        "kids backpack",
    ],
    "kitchen": [
        "air fryer",
        "coffee maker",
        "rice cooker",
        "electric kettle",
        "toaster oven",
    ],
    "home": [
        "blackout curtains",
        "humidifier",
        "space heater",
        "storage bins",
        "bed sheets",
    ],
}


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def main(max_pages: int = 50):
    root = ROOT
    written = 0

    # Generate seasonal pages for the top categories first
    for cat in ["electronics", "kids", "kitchen", "home"]:
        hub = CATEGORIES[cat]
        for seed in SEEDS_BY_CAT.get(cat, []):
            for season_slug, season_label in SEASONS:
                # Example slug: usb-c-charger-black-friday-deals.html
                slug = f"{slugify(seed)}-{season_slug}-deals.html"
                out = root / slug
                if out.exists():
                    continue

                title = f"Best {seed.title()} Deals for {season_label} (Amazon Picks)"
                description = f"{seed.title()} deals for {season_label}. Click through to see live prices on Amazon (Amazon-only)."
                intro = (
                    f"{season_label} is when buyer intent spikes. Use these Amazon searches to compare {seed} options quickly—"
                    f"focus on specs, compatibility, and recent buyer feedback before you buy."
                )

                quick_amz_label = f"Shop {seed} deals for {season_label}"
                quick_amz_query = f"{seed} {season_label} deals"

                queries = [
                    (f"{seed} {season_label} deals", "Core seasonal intent"),
                    (f"best {seed} {season_label}", "Comparison intent"),
                    (f"{seed} sale {season_label}", "Sale intent"),
                    (f"{seed} deals today", "Bridge to evergreen intent"),
                ]

                related = [
                    (hub, f"{cat.title()} deals hub"),
                    ("/best-deals-online-today.html", "Best deals online today"),
                    ("/best-deals-online.html", "Best deals online"),
                ]

                html_txt = build_page(
                    slug=slug,
                    title=title,
                    description=description,
                    intro=intro,
                    quick_amz_label=quick_amz_label,
                    quick_amz_query=quick_amz_query,
                    quick_internal_href=hub,
                    quick_internal_label=f"{cat.title()} deals hub",
                    queries=queries,
                    related_links=related,
                )
                out.write_text(html_txt, encoding="utf-8")
                written += 1
                print("wrote", out.name)
                if written >= max_pages:
                    print(f"done: wrote {written} seasonal pages")
                    return

    print(f"done: wrote {written} seasonal pages")


if __name__ == "__main__":
    main()
