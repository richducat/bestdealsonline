#!/usr/bin/env python3
from pathlib import Path
import datetime

SITE = "https://bestdealsonline.us"
# Known non-content root files that should never appear in the sitemap
# (placeholders, drafts, fixtures). Everything else at root is real
# content and gets included.
DENIED_ROOT_HTML = {
    "example-post.html",
}


def main():
    root = Path(__file__).resolve().parents[1]
    htmls = sorted([p.name for p in root.glob("*.html") if p.name not in DENIED_ROOT_HTML])
    blog_dir = root / "blog"
    blog_htmls = []
    if blog_dir.exists():
        blog_htmls = sorted(
            [str(p.relative_to(root)) for p in blog_dir.rglob("*.html") if p.name != "example-post.html"]
        )

    paths = ["/"]
    for name in htmls:
        if name == "index.html":
            continue
        paths.append(f"/{name}")
    for rel in blog_htmls:
        paths.append("/" + rel.replace("\\", "/"))
    paths.sort()

    lastmod = datetime.date.today().isoformat()

    out = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"]
    for path in paths:
        out.append("  <url>")
        out.append(f"    <loc>{SITE}{path}</loc>")
        out.append(f"    <lastmod>{lastmod}</lastmod>")
        out.append("  </url>")
    out.append("</urlset>")

    (root / "sitemap.xml").write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
