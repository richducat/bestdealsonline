#!/usr/bin/env python3
"""Restyle legacy static pages to match the homepage vibe.

Goal (Phase 1): consistent design feel across ALL pages.

This script targets older "money pages" that still use the light header/body template.
It preserves the existing <main> inner HTML (cards/links), but wraps it with:
- dark branded header
- gradient hero with extracted H1/intro
- branded footer
- OG image + favicon meta

It intentionally does NOT touch:
- index.html (React app shell)
- *-deals.html hub pages (handled individually)
- blog/*
- best-deals-online*.html landing pages
- privacy/affiliate pages

Run:
  python3 scripts/restyle_legacy_pages.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://bestdealsonline.us"

EXCLUDE_NAMES = {
    "index.html",
}

EXCLUDE_PREFIXES = (
    "best-deals-online",
)

# We exclude hubs by suffix.
EXCLUDE_SUFFIXES = (
    "-deals.html",
)

# Basic extraction regexes
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
DESC_RE = re.compile(r"<meta\s+name=\"description\"\s+content=\"([\s\S]*?)\"\s*/?>", re.I)
CANON_RE = re.compile(r"<link\s+rel=\"canonical\"\s+href=\"([^\"]*)\"\s*/?>", re.I)
MAIN_RE = re.compile(r"<main[^>]*>(.*)</main>", re.I | re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.I | re.S)


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return " ".join(s.split()).strip()


def should_process(p: Path) -> bool:
    if p.name in EXCLUDE_NAMES:
        return False
    if p.name.startswith(EXCLUDE_PREFIXES):
        return False
    if p.name.endswith(EXCLUDE_SUFFIXES):
        return False
    if p.parts and "blog" in p.parts:
        return False
    # only process top-level html files
    if p.parent != ROOT:
        return False
    return True


def pick_hero_svg(canonical: str) -> str:
    # Choose a minimal SVG based on URL keywords. Keep it simple and predictable.
    u = canonical.lower()
    if "/electronics" in u or any(k in u for k in ["wifi", "router", "dash-cam", "projector", "headset", "keyboard", "mouse", "charger", "usb", "hdmi", "bluetooth", "speaker"]):
        return "/assets/hero/electronics.svg"
    if "/kitchen" in u or any(k in u for k in ["air-fryer", "coffee", "kettle", "rice-cooker", "cookware", "toaster", "blender", "meal-prep"]):
        return "/assets/hero/kitchen.svg"
    if "/tools" in u or any(k in u for k in ["drill", "tool", "screwdriver", "flashlight", "impact", "socket", "wrench", "laser-level"]):
        return "/assets/hero/tools.svg"
    # default to home for most remainder
    if "/home" in u or any(k in u for k in ["curtains", "bed", "mattress", "humidifier", "dehumidifier", "vacuum", "shower", "storage", "laundry", "pillow", "doormat", "trash", "smoke", "leak"]):
        return "/assets/hero/home.svg"
    return "/assets/hero/default.svg"


def build_page(*, title: str, description: str, canonical: str, h1: str, intro: str, main_inner: str) -> str:
    # Slight layout differentiation from hubs: hero has a right-side info panel + minimal SVG.
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no\" />
  <title>{title}</title>
  <meta name=\"description\" content=\"{description}\" />
  <link rel=\"canonical\" href=\"{canonical}\" />

  <meta property=\"og:title\" content=\"{title}\" />
  <meta property=\"og:description\" content=\"{description}\" />
  <meta property=\"og:type\" content=\"website\" />
  <meta property=\"og:url\" content=\"{canonical}\" />
  <meta property=\"og:image\" content=\"{SITE}/assets/og-default.svg\" />

  <meta name=\"twitter:card\" content=\"summary_large_image\" />
  <meta name=\"twitter:image\" content=\"{SITE}/assets/og-default.svg\" />

  <link rel=\"icon\" href=\"/assets/favicon.svg\" type=\"image/svg+xml\" />

  <script src=\"https://cdn.tailwindcss.com\"></script>
  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap\" rel=\"stylesheet\">
  <style>:root{{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}</style>
</head>
<body class=\"bg-slate-950 text-slate-50\">
  <div class=\"bg-slate-100 text-slate-700 text-xs border-b border-slate-200\">
    <div class=\"container mx-auto px-4 py-2\">
      <strong>Affiliate disclosure:</strong> When you buy through links on this site, we may earn a commission at no extra cost to you.
      <a class=\"underline\" href=\"/affiliate-disclosure.html\">Details</a>
    </div>
  </div>

  <header class=\"bg-slate-900 text-white sticky top-0 z-40 shadow-lg\">
    <div class=\"container mx-auto px-4 py-4 flex items-center justify-between gap-4\">
      <a href=\"/\" class=\"flex items-center gap-3\">
        <span class=\"bg-yellow-500 text-slate-900 p-2 rounded-lg font-black\">B</span>
        <span class=\"leading-tight\">
          <span class=\"block font-extrabold tracking-tight text-lg\">BestDealsOnline</span>
          <span class=\"block text-[10px] text-yellow-400 uppercase tracking-[0.25em]\">Amazon Picks</span>
        </span>
      </a>
      <nav class=\"hidden md:flex flex-wrap gap-4 text-sm text-slate-200\">
        <a class=\"hover:text-yellow-400\" href=\"/best-deals-online-today.html\">Today</a>
        <a class=\"hover:text-yellow-400\" href=\"/electronics-deals.html\">Electronics</a>
        <a class=\"hover:text-yellow-400\" href=\"/home-deals.html\">Home</a>
        <a class=\"hover:text-yellow-400\" href=\"/kitchen-deals.html\">Kitchen</a>
        <a class=\"hover:text-yellow-400\" href=\"/tools-deals.html\">Tools</a>
        <a class=\"hover:text-yellow-400\" href=\"/blog/index.html\">Blog</a>
      </nav>
    </div>
  </header>

  <section class=\"bg-gradient-to-br from-indigo-900 via-blue-900 to-slate-900\">
    <div class=\"container mx-auto px-4 py-10 md:py-14\">
      <div class=\"grid grid-cols-1 lg:grid-cols-12 gap-8 items-end\">
        <div class=\"lg:col-span-8\">
          <p class=\"inline-flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/40 text-yellow-300 text-xs font-bold px-3 py-1 rounded-full mb-5\">Updated often • live prices on Amazon</p>
          <h1 class=\"text-3xl md:text-5xl font-extrabold tracking-tight\">{h1}</h1>
          <p class=\"text-blue-100 text-base md:text-lg mt-4 max-w-2xl\">{intro}</p>
        </div>
        <div class=\"lg:col-span-4\">
          <div class=\"grid grid-cols-1 gap-4\">
            <div class=\"bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-sm\">
              <div class=\"text-xs uppercase tracking-[0.3em] text-yellow-300 font-bold\">Quick tips</div>
              <ul class=\"mt-3 space-y-2 text-sm text-blue-100\">
                <li>Open a query → compare live prices.</li>
                <li>Use “Related pages” to browse deeper.</li>
                <li>Check <a class=\"underline hover:text-yellow-200\" href=\"/best-deals-online-today.html\">Today</a> for the shortlist.</li>
              </ul>
            </div>

            <div class=\"hidden md:block bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm\">
              <img src=\"{pick_hero_svg(canonical)}\" width=\"720\" height=\"480\" loading=\"lazy\" decoding=\"async\" alt=\"\" class=\"w-full h-auto opacity-95\" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <main class=\"bg-slate-50 text-slate-900\">
    <div class=\"container mx-auto px-4 py-10\">
      {main_inner}
    </div>

    <footer class='border-t border-slate-200 bg-white'>
      <div class='container mx-auto px-4 py-8 text-sm text-slate-500'>
        <div class='flex flex-col gap-3'>
          <div>
            <strong>Affiliate disclosure:</strong> We may earn a commission when you buy through links on this site, at no extra cost to you.
            <span class='ml-2'><a class='underline inline-flex items-center min-h-10 px-1 hover:text-slate-900' href='/affiliate-disclosure.html'>Details</a></span>
            <div class='text-xs text-slate-400 mt-1'>As an Amazon Associate, we earn from qualifying purchases.</div>
          </div>
          <div class='flex flex-wrap gap-x-4 gap-y-2'>
            <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/best-deals-online-today.html'>Today</a>
            <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/best-deals-online.html'>Best deals online</a>
            <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/electronics-deals.html'>Electronics hub</a>
            <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/home-deals.html'>Home hub</a>
            <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/kitchen-deals.html'>Kitchen hub</a>
            <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/tools-deals.html'>Tools hub</a>
            <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/blog/index.html'>Blog</a>
            <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/privacy.html'>Privacy</a>
          </div>
        </div>
      </div>
    </footer>
  </main>
</body></html>
"""


def process_file(p: Path) -> bool:
    s = p.read_text(errors="ignore")

    # Only restyle legacy pages (light body class)
    if 'body class="bg-slate-50' not in s:
        return False

    title_m = TITLE_RE.search(s)
    desc_m = DESC_RE.search(s)
    canon_m = CANON_RE.search(s)
    main_m = MAIN_RE.search(s)

    if not (title_m and desc_m and canon_m and main_m):
        return False

    title = strip_tags(title_m.group(1))
    description = desc_m.group(1).strip()
    canonical = canon_m.group(1).strip()

    main_inner = main_m.group(1).strip()

    # Extract first H1 + first P from main
    h1 = ""
    intro = ""
    h1_m = H1_RE.search(main_inner)
    if h1_m:
        h1 = strip_tags(h1_m.group(1))
    p_m = P_RE.search(main_inner)
    if p_m:
        intro = strip_tags(p_m.group(1))

    # Remove the first h1/p from main content to avoid duplicates
    if h1_m:
        main_inner = H1_RE.sub("", main_inner, count=1)
    if p_m:
        main_inner = P_RE.sub("", main_inner, count=1)

    # Clean extra whitespace
    main_inner = re.sub(r"\n{3,}", "\n\n", main_inner).strip()

    if not h1:
        h1 = title.replace(" | BestDealsOnline", "").strip()
    if not intro:
        intro = description

    out = build_page(
        title=title,
        description=description,
        canonical=canonical,
        h1=h1,
        intro=intro,
        main_inner=main_inner,
    )

    p.write_text(out, encoding="utf-8")
    return True


def main():
    changed = []
    for p in sorted(ROOT.glob("*.html")):
        if not should_process(p):
            continue
        if process_file(p):
            changed.append(p.name)

    print(f"restyled {len(changed)} pages")
    if changed:
        print("\n".join(changed[:50]))


if __name__ == "__main__":
    main()
