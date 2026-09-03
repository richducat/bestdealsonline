#!/usr/bin/env python3
"""One-off, idempotent fixes from the 2026-09-01 traffic audit.

1. BreadcrumbList "item" URLs that pointed at extensionless self-URLs on four
   guides now use the .html canonical.
2. The flagship fake-discount post carried a second FAQPage block with four
   laptop-backpack questions that are not on the page (copied from the
   backpack article). FAQ markup for content that is not on the page violates
   Google's structured-data policy; the block is removed. The post's own
   FAQPage (matching its "Quick answers" section) stays.
3. The homepage crawlable block (index.html and the Vite template
   app/index.html, so rebuilds keep it) now links the 23 rewritten buying
   guides and the deal checker, which had zero inbound links from the homepage.
4. extension/test/mock-product.html gets noindex; it is a test harness that
   the sitemap generator was submitting to Google as a product page.
5. scripts/gen-sitemap.mjs skips the extension/ tree.

Run from the repo root: python3 scripts/apply_audit_fixes.py
"""
import glob
import os
import re

BASE = "https://bestdealsonline.us"


def read(p):
    return open(p, encoding="utf-8", errors="ignore").read()


def write(p, s):
    open(p, "w", encoding="utf-8").write(s)


def fix_breadcrumbs():
    n = 0
    for f in glob.glob("*.html"):
        src = read(f)

        def sub(m):
            slug = m.group(1)
            return m.group(0) if not os.path.exists(slug + ".html") else f'"item": "{BASE}/{slug}.html"'

        out = re.sub(r'"item": "' + re.escape(BASE) + r'/([a-z0-9-]+)"', sub, src)
        if out != src:
            write(f, out)
            n += 1
    print(f"breadcrumb item URLs fixed on {n} pages")


def fix_fake_discount_faq():
    f = "blog/how-to-spot-a-fake-amazon-discount-in-10-seconds.html"
    src = read(f)
    block_re = re.compile(r'\s*<script type="application/ld\+json">\s*\{[^<]*?"@type": "FAQPage"[^<]*?</script>', re.S)
    removed = 0

    def sub(m):
        nonlocal removed
        if "laptop backpack" in m.group(0):
            removed += 1
            return "\n"
        return m.group(0)

    out = block_re.sub(sub, src)
    if out != src:
        write(f, out)
    print(f"fake-discount post: removed {removed} off-topic FAQPage block(s)")


GUIDES = [
    ("air-fryer", "Air fryers"),
    ("blackout-curtains", "Blackout curtains"),
    ("bluetooth-speaker", "Bluetooth speakers"),
    ("bluetooth-tracker", "Bluetooth trackers"),
    ("coffee-maker", "Coffee makers"),
    ("dash-cam", "Dash cams"),
    ("electric-kettle", "Electric kettles"),
    ("entryway-bench", "Entryway benches"),
    ("kids-backpack", "Kids backpacks"),
    ("kids-desk-chair", "Kids desk chairs"),
    ("kids-headphones", "Kids headphones"),
    ("laptop-docking-station", "Laptop docking stations"),
    ("learning-toys", "Learning toys"),
    ("power-bank", "Power banks"),
    ("rice-cooker", "Rice cookers"),
    ("screen-protector", "Screen protectors"),
    ("toaster-oven", "Toaster ovens"),
    ("usb-c-cable", "USB-C cables"),
    ("usb-c-charger", "USB-C chargers"),
    ("webcam", "Webcams"),
    ("weighted-blanket", "Weighted blankets"),
    ("wifi-router", "Wi-Fi routers"),
    ("wireless-charger", "Wireless chargers"),
]


def fix_homepage_block():
    items = "\n".join(f'          <li><a href="/{slug}.html">{name} buying guide</a></li>'
                      for slug, name in GUIDES if os.path.exists(slug + ".html"))
    block = (
        "        <h2>Buying guides</h2>\n"
        "        <ul>\n" + items + "\n        </ul>\n"
        "        <h2>Tools</h2>\n"
        "        <ul>\n"
        '          <li><a href="/deal-check.html">Amazon deal checker: is this price actually a discount?</a></li>\n'
        '          <li><a href="/blog/how-to-spot-a-fake-amazon-discount-in-10-seconds.html">How to spot a fake Amazon discount in 10 seconds</a></li>\n'
        "        </ul>\n"
    )
    for f in ("index.html", "app/index.html"):
        src = read(f)
        if "<h2>Buying guides</h2>" in src:
            continue
        anchor = "        <h2>More</h2>\n"
        if anchor not in src:
            print(f"{f}: crawlable block anchor not found, skipped")
            continue
        write(f, src.replace(anchor, block + anchor, 1))
        print(f"{f}: added buying-guide and tool links to the crawlable block")


def fix_mock_page():
    f = "extension/test/mock-product.html"
    src = read(f)
    if 'name="robots"' not in src:
        src = src.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">', 1)
        write(f, src)
        print("mock-product.html: noindex added")


def fix_sitemap_generator():
    f = "scripts/gen-sitemap.mjs"
    src = read(f)
    if "rel.startsWith('extension/')" in src:
        return
    src = src.replace(
        "  return rel.startsWith('app/') || rel.startsWith('images/categories/') ||",
        "  // extension/ holds the Chrome extension source, store kit and its test harness page — never site content.\n"
        "  return rel.startsWith('app/') || rel.startsWith('images/categories/') || rel.startsWith('extension/') ||",
        1,
    )
    write(f, src)
    print("gen-sitemap.mjs: extension/ excluded")


if __name__ == "__main__":
    fix_breadcrumbs()
    fix_fake_discount_faq()
    fix_homepage_block()
    fix_mock_page()
    fix_sitemap_generator()
