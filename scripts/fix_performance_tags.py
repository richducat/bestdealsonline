#!/usr/bin/env python3
"""Defer the render-blocking Tailwind CDN script and add preconnect hints
for Google Fonts across every static HTML page. Idempotent: safe to
re-run, only touches tags that still need fixing.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TAILWIND_RE = re.compile(r"<script src=([\"'])https://cdn\.tailwindcss\.com\1></script>")

FONTS_LINK_RE = re.compile(
    r"<link href=([\"'])https://fonts\.googleapis\.com/[^\"']*\1 rel=\1?stylesheet\1?>"
    r"|<link href=([\"'])https://fonts\.googleapis\.com/[^\"']*\2 rel=\2stylesheet\2>"
)
# Simpler, robust pattern: match the whole <link ... fonts.googleapis.com ...> tag regardless of quote style.
FONTS_LINK_ANY_RE = re.compile(r"<link href=[\"']https://fonts\.googleapis\.com/[^>]*>")

PRECONNECT_MARKER = "fonts.gstatic.com"


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    text = TAILWIND_RE.sub(lambda m: f"<script defer src={m.group(1)}https://cdn.tailwindcss.com{m.group(1)}></script>", text)

    if PRECONNECT_MARKER not in text:
        def add_preconnect(m: re.Match) -> str:
            tag = m.group(0)
            preconnect = (
                '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n  '
            )
            return preconnect + tag

        text = FONTS_LINK_ANY_RE.sub(add_preconnect, text, count=1)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    files = list(ROOT.glob("*.html")) + list((ROOT / "blog").glob("*.html"))
    for p in sorted(files):
        if fix_file(p):
            changed += 1
    print(f"updated {changed} of {len(files)} files")


if __name__ == "__main__":
    main()
