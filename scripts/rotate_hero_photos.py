#!/usr/bin/env python3
"""Rotate hero photos across pages so the same faces don't repeat everywhere.

Each category has several photo variants in images/hero/ (<cat>.jpg,
<cat>-2.jpg, ...). The variant for a page is picked deterministically from
a hash of the page's filename, so reruns are stable and a page keeps its
photo across regenerations. Alt text tracks the chosen photo.

Idempotent: run any time after generating new pages (after
apply_hero_photos.py has given them a base hero photo).
"""

import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERO_DIR = ROOT / "images/hero"

ALT = {
    "default": "A woman smiles while shopping on her laptop from her couch",
    "default-2": "Shopping online with a credit card, headphones and phone at hand",
    "default-3": "A woman browses deals on her laptop in a sunlit living room",
    "default-4": "A smiling woman unpacks a delivery box at home",
    "electronics": "A woman relaxes on her sofa listening to music with headphones",
    "electronics-2": "A woman enjoys music on her headphones",
    "electronics-3": "A smiling woman listens to music with white headphones",
    "home": "A woman enjoys a cup of coffee under a cozy blanket on her sofa",
    "home-2": "A woman relaxes on her couch with her phone and laptop",
    "home-3": "A smiling woman organizes her kitchen shelves",
    "kitchen": "A smiling woman whisks a bowl in her kitchen",
    "kitchen-2": "Two women cook together in a cozy kitchen",
    "kitchen-3": "Taking a fresh-baked dish out of the oven",
    "tools": "A woman paints a wall with a roller during a home project",
    "tools-2": "Assembling a table at home with a screwdriver",
    "tools-3": "A woman paints a wall in a warm peach tone",
    "kids": "A mom plays with her two kids in a sunlit living room",
    "kids-2": "A family shares hot drinks together in the living room",
    "kids-3": "A mom laughs while playing with her baby on the couch",
    "beauty": "A woman applies face cream during her morning routine",
    "beauty-2": "A woman uses a gua sha tool in the mirror",
    "beauty-3": "A woman does her skincare routine at the bathroom mirror",
    "fitness": "A smiling woman does an arm stretch before a workout",
    "fitness-2": "A smiling woman works out with a resistance band",
    "fitness-3": "A woman does lunges on a yoga mat in her living room",
    "pets": "A smiling woman sits on the couch with her husky",
    "pets-2": "A woman gently pets her dog on the sofa",
    "pets-3": "A woman works on her laptop with her shiba inu beside her",
}

# variants per category, sorted so "<cat>.jpg" is first
VARIANTS = {}
for p in sorted(HERO_DIR.glob("*.jpg")):
    base = re.sub(r"-\d+$", "", p.stem)
    VARIANTS.setdefault(base, []).append(p.stem)

# Topic-specific photos (images/topics/<slug>.jpg + .meta.json sidecars with
# alt text). A page whose filename contains a topic slug gets that photo --
# subject relevance beats generic lifestyle imagery. Longest slug wins so
# "kids-headphones" beats "headphones" and "immersion-blender" beats
# "blender".
import json

TOPIC_DIR = ROOT / "images/topics"
TOPICS = {}
for p in sorted(TOPIC_DIR.glob("*.jpg")):
    meta_path = p.with_suffix(".jpg.meta.json")
    alt = ""
    if meta_path.exists():
        alt = json.loads(meta_path.read_text()).get("alt", "")
    TOPICS[p.stem] = alt
# Pages about air fryer accessories share the air-fryer photo.
TOPIC_ALIASES = {"air-fryer-accessories": "air-fryer"}
MATCH_SLUGS = sorted(set(TOPICS) | set(TOPIC_ALIASES), key=len, reverse=True)

IMG_RE = re.compile(
    r'(<img src="/images/(?:hero|topics)/)([a-z-]+?(?:-\d+)?)(\.jpg"[^>]*? alt=")([^"]*)(")'
)


def topic_for(filename):
    # singular slugs also match their plural forms in filenames
    for slug in MATCH_SLUGS:
        if slug in filename:
            return TOPIC_ALIASES.get(slug, slug)
    return None


def main():
    pages = swapped = topical = 0
    for pattern in ("*.html", "blog/*.html"):
        for path in sorted(ROOT.glob(pattern)):
            html = path.read_text(encoding="utf-8")
            if "/images/hero/" not in html and "/images/topics/" not in html:
                continue
            topic = topic_for(path.name)

            def repl(m):
                nonlocal topical
                if topic:
                    topical += 1
                    return f'<img src="/images/topics/{topic}{m.group(3)}{TOPICS[topic]}{m.group(5)}'
                base = re.sub(r"-\d+$", "", m.group(2))
                variants = VARIANTS.get(base)
                if not variants:
                    return m.group(0)
                pick = variants[zlib.crc32(path.name.encode()) % len(variants)]
                return f'<img src="/images/hero/{pick}{m.group(3)}{ALT.get(pick, m.group(4))}{m.group(5)}'

            new = IMG_RE.sub(repl, html)
            if new != html:
                path.write_text(new, encoding="utf-8")
                swapped += 1
            pages += 1
    print(f"checked {pages} pages, rewrote {swapped} ({topical} topic-matched)")


if __name__ == "__main__":
    main()
