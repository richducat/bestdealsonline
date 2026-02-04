#!/usr/bin/env python3
"""Clean up awkward/developer-speak copy across static pages.

Goal: make language consumer-friendly while preserving meaning.

Run:
  python3 scripts/clean_copy.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    # Hub tiles
    "Curated long-tail entry point.": "Popular page for this category.",

    # Query card descriptions
    "Core query.": "The main search shoppers use.",
    "Spec modifier.": "Feature-focused search.",
    "Use-case intent.": "Use-case shoppers search for.",
    "Alternate wording.": "Same idea, different wording.",
    "Comparison searches.": "Comparison-style search.",

    # Overly SEO-y / disclaimer-y phrasing
    "Strong health-related intent without claims.": "Common search people use.",

    # Jargon arrows
    "Problem → buy": "Fix-a-problem pick",

    # Section headings
    "High-intent searches": "Quick price checks",

    # Hero badge (less "system" tone)
    "Updated often • live prices on Amazon": "Updated often • check live prices",
}


def main():
    changed = 0
    for p in ROOT.glob("*.html"):
        s = p.read_text(errors="ignore")
        s2 = s
        for old, new in REPLACEMENTS.items():
            s2 = s2.replace(old, new)
        if s2 != s:
            p.write_text(s2, encoding="utf-8")
            changed += 1
    print("updated", changed, "files")


if __name__ == "__main__":
    main()
