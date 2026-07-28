#!/usr/bin/env python3
"""
Find the near-duplicate page families that Google is refusing to index.

Read-only. Writes a plan to /tmp; changes nothing in the repo.

Context: GSC on 2026-07-28 reported 193 indexed / 774 "Discovered - currently
not indexed". "Discovered - not indexed" means Google saw the URL in the
sitemap and chose not to spend crawl budget on it -- the classic signature of
thin, templated, near-duplicate pages.

Usage: python3 scripts/analyze_thin_clusters.py
"""
import re
import glob
import json
import difflib
from collections import defaultdict

PRICE_SUFFIX = re.compile(r"-(under|below|over)-\d+$")
QUALIFIER = re.compile(
    r"-(dorm|travel|small-apartment|apartment|office|home|beginners?|kids|"
    r"seniors?|students?|professionals?|budget|cheap)$"
)


def visible_words(path):
    h = open(path, encoding="utf-8", errors="ignore").read()
    for tag in ("script", "style", "head"):
        h = re.sub(r"(?is)<%s\b.*?</%s>" % (tag, tag), " ", h)
    t = re.sub(r"(?s)<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", t).split()


def stem(slug):
    """Strip price caps and qualifiers to find the family root."""
    s = slug
    for _ in range(3):
        s2 = PRICE_SUFFIX.sub("", s)
        s2 = QUALIFIER.sub("", s2)
        if s2 == s:
            break
        s = s2
    return s


def main():
    pages = {}
    for f in sorted(glob.glob("*.html")):
        slug = f[:-5]
        if slug in ("404", "index"):
            continue
        pages[slug] = visible_words(f)

    families = defaultdict(list)
    for slug in pages:
        families[stem(slug)].append(slug)

    multi = {k: sorted(v) for k, v in families.items() if len(v) > 1}
    singles = [k for k, v in families.items() if len(v) == 1]

    total_in_families = sum(len(v) for v in multi.values())

    print("=" * 76)
    print("THIN / NEAR-DUPLICATE CLUSTER ANALYSIS")
    print("=" * 76)
    print(f"Static pages analysed          : {len(pages)}")
    print(f"Distinct topic families        : {len(families)}")
    print(f"Families with >1 variant       : {len(multi)}")
    print(f"Pages living inside those      : {total_in_families}")
    print(f"Standalone pages               : {len(singles)}")

    # measure internal similarity per family
    rows = []
    for famname, members in multi.items():
        base = pages[members[0]]
        sims = []
        for other in members[1:]:
            sims.append(difflib.SequenceMatcher(None, base, pages[other]).ratio())
        avg = sum(sims) / len(sims)
        avg_words = sum(len(pages[m]) for m in members) / len(members)
        rows.append((famname, len(members), avg, avg_words))

    rows.sort(key=lambda r: (-r[1], -r[2]))

    print("\n" + "-" * 76)
    print(f"{'family':<34}{'pages':>6}{'avg similarity':>16}{'avg words':>12}")
    print("-" * 76)
    for famname, n, sim, w in rows[:25]:
        print(f"{famname:<34}{n:>6}{sim:>15.0%}{w:>12.0f}")
    if len(rows) > 25:
        print(f"... and {len(rows)-25} more families")

    near_dupe = [r for r in rows if r[2] >= 0.60]
    pages_in_near_dupe = sum(r[1] for r in near_dupe)
    reclaimable = pages_in_near_dupe - len(near_dupe)

    print("\n" + "=" * 76)
    print("CONSOLIDATION OPPORTUNITY")
    print("=" * 76)
    print(f"Families >=60% internally similar : {len(near_dupe)}")
    print(f"Pages inside them                 : {pages_in_near_dupe}")
    print(f"Merge to one strong page each     : {len(near_dupe)} pages kept")
    print(f"Pages to 301-redirect away        : {reclaimable}")
    print(f"\nResulting site: ~{len(pages)-reclaimable} pages, "
          f"each a real guide instead of {int(sum(r[3] for r in rows)/len(rows))} words of boilerplate.")

    plan = {
        "generated_for": "bestdealsonline.us consolidation",
        "keep_and_expand": [
            {"canonical": f"{fam}.html",
             "absorb": [m + ".html" for m in multi[fam] if m != fam] or
                       [m + ".html" for m in multi[fam][1:]],
             "variants": len(multi[fam]),
             "avg_similarity": round(sim, 3)}
            for fam, n, sim, w in near_dupe
        ],
    }
    out = "/tmp/consolidation_plan.json"
    with open(out, "w") as fh:
        json.dump(plan, fh, indent=2)
    print(f"\nFull merge plan written to {out}")
    print("(read-only analysis - no repo files were changed)")


if __name__ == "__main__":
    main()
