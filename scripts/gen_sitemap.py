#!/usr/bin/env python3
from pathlib import Path
import datetime

SITE = "https://bestdealsonline.us"


def main():
    root = Path(__file__).resolve().parents[1]
    htmls = sorted([p.name for p in root.glob("*.html")])
    blog_dir = root / "blog"
    blog_htmls = []
    if blog_dir.exists():
        blog_htmls = sorted([str(p.relative_to(root)) for p in blog_dir.rglob("*.html")])

    urls = []
    urls.append(("/", "daily", "1.0"))

    for name in htmls:
        if name == "index.html":
            continue
        path = f"/{name}"
        if name.endswith("-deals.html"):
            urls.append((path, "weekly", "0.7"))
        else:
            urls.append((path, "weekly", "0.6"))

    # blog pages
    for rel in blog_htmls:
        path = "/" + rel.replace("\\", "/")
        # blog index gets higher priority
        if rel.endswith("index.html"):
            urls.append((path, "weekly", "0.6"))
        else:
            urls.append((path, "monthly", "0.5"))


    out = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"]
    for path, freq, prio in urls:
        out.append("  <url>")
        out.append(f"    <loc>{SITE}{path}</loc>")
        out.append(f"    <changefreq>{freq}</changefreq>")
        out.append(f"    <priority>{prio}</priority>")
        out.append("  </url>")
    out.append("</urlset>")

    (root / "sitemap.xml").write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
