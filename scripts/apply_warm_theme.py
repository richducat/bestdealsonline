#!/usr/bin/env python3
"""Inject the warm-theme stylesheet + Fraunces font into every static page,
and point social-share images at the real OG image.

Idempotent: pages already carrying warm-theme.css are left alone. The SPA
homepage (root index.html) is skipped -- it is themed at build time in app/.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FONT_LINK = (
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700'
    '&display=swap" rel="stylesheet">'
)
THEME_LINK = '<link rel="stylesheet" href="/assets/warm-theme.css">'
ICON_LINKS = (
    '<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">\n'
    '  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">'
)
# Large image previews make pages eligible for rich Google Discover cards.
ROBOTS_META = '<meta name="robots" content="max-image-preview:large">'
INJECT = f"  {FONT_LINK}\n  {THEME_LINK}\n  {ICON_LINKS}\n  {ROBOTS_META}\n</head>"

OG_OLD = "https://bestdealsonline.us/assets/og-default.svg"
OG_NEW = "https://bestdealsonline.us/assets/og-home.jpg"
# Only swap share-card images; the schema.org Organization logo keeps the SVG.
OG_META_RE = re.compile(
    r'(<meta (?:property="og:image"|name="twitter:image") content=")' + re.escape(OG_OLD) + r'(")'
)

SKIP = {ROOT / "index.html", ROOT / "example-post.html"}


def page_files():
    for pattern in ("*.html", "blog/*.html"):
        for path in sorted(ROOT.glob(pattern)):
            if path in SKIP:
                continue
            yield path


def main():
    themed = og_swapped = 0
    for path in page_files():
        html = path.read_text(encoding="utf-8")
        orig = html

        if "warm-theme.css" not in html and "</head>" in html:
            html = html.replace("</head>", INJECT, 1)
            themed += 1
        elif "apple-touch-icon" not in html and "</head>" in html:
            # Pages themed before icons existed still need the icon links.
            html = html.replace("</head>", f"  {ICON_LINKS}\n</head>", 1)
        if 'name="robots"' not in html and "</head>" in html:
            html = html.replace("</head>", f"  {ROBOTS_META}\n</head>", 1)

        html, n = OG_META_RE.subn(r"\g<1>" + OG_NEW + r"\g<2>", html)
        if n:
            og_swapped += 1

        if html != orig:
            path.write_text(html, encoding="utf-8")

    print(f"themed {themed} pages, og image swapped on {og_swapped} pages")


if __name__ == "__main__":
    main()
