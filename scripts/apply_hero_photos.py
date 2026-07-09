#!/usr/bin/env python3
"""Swap the abstract vector hero art on static pages for real lifestyle
photography (images/hero/<category>.jpg, Pexels-licensed, sidecar metadata
alongside each file), styled to match the homepage's arch photo treatment.

Transforms, on every root + blog page:
  1. The hero art container `bg-white/5 ... backdrop-blur-sm` -> arch-cropped
     photo frame.
  2. `<img src="/assets/hero/<cat>.svg" ...>` -> the matching category photo
     with a descriptive human alt text.

Idempotent: pages without hero SVG references are left untouched.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OLD_CONTAINER = '<div class="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">'
NEW_CONTAINER = '<div class="overflow-hidden rounded-t-[5rem] rounded-b-2xl border-4 border-white/30 shadow-xl">'

ALT = {
    "default": "A woman smiles while shopping on her laptop from her couch",
    "electronics": "A woman relaxes on her sofa listening to music with headphones",
    "home": "A woman enjoys a cup of coffee under a cozy blanket on her sofa",
    "kitchen": "A smiling woman whisks a bowl in her kitchen",
    "tools": "A woman paints a wall with a roller during a home project",
    "kids": "A mom plays with her two kids in a sunlit living room",
    "beauty": "A woman applies face cream during her morning routine",
    "fitness": "A smiling woman does an arm stretch before a workout",
    "pets": "A smiling woman sits on the couch with her husky",
}
# Pages referencing hero art with no matching photo fall back to the
# universal "woman shopping from her couch" image.
FALLBACK = "default"

IMG_RE = re.compile(
    r'<img src="/assets/hero/([a-z]+)\.svg" width="720" height="480" '
    r'loading="lazy" decoding="async" alt="[^"]*" class="w-full h-auto opacity-95" />'
)

AVAILABLE = {p.stem for p in (ROOT / "images/hero").glob("*.jpg")}


def replace_img(match):
    cat = match.group(1)
    if cat not in AVAILABLE:
        cat = FALLBACK
    return (
        f'<img src="/images/hero/{cat}.jpg" width="1200" height="800" '
        f'loading="lazy" decoding="async" alt="{ALT[cat]}" class="w-full h-full object-cover" />'
    )


def main():
    pages = imgs = containers = 0
    for pattern in ("*.html", "blog/*.html"):
        for path in sorted(ROOT.glob(pattern)):
            html = path.read_text(encoding="utf-8")
            if "/assets/hero/" not in html:
                continue
            new_html, n_img = IMG_RE.subn(replace_img, html)
            n_cont = new_html.count(OLD_CONTAINER)
            new_html = new_html.replace(OLD_CONTAINER, NEW_CONTAINER)
            if new_html != html:
                path.write_text(new_html, encoding="utf-8")
                pages += 1
                imgs += n_img
                containers += n_cont
    print(f"updated {pages} pages ({imgs} hero images, {containers} containers)")


if __name__ == "__main__":
    main()
