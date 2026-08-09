#!/usr/bin/env python3
"""Restyle blog pages to match homepage visual language."""

from __future__ import annotations

import datetime as dt
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
SITE = "https://bestdealsonline.us"

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
DESC_RE = re.compile(
    r"<meta\s+name=['\"]description['\"]\s+content=['\"]([\s\S]*?)['\"]\s*/?>",
    re.I,
)
CANON_RE = re.compile(
    r"<link\s+rel=['\"]canonical['\"]\s+href=['\"]([^'\"]+)['\"]\s*/?>",
    re.I,
)
MAIN_RE = re.compile(r"<main[^>]*>([\s\S]*?)</main>", re.I)
H1_RE = re.compile(r"<h1[^>]*>([\s\S]*?)</h1>", re.I)
UPDATED_RE = re.compile(r"\bupdated\s+(\d{4}-\d{2}-\d{2})", re.I)
POSTED_RE = re.compile(r"\bposted:\s*(\d{4}-\d{2}-\d{2})", re.I)
BADGE_RE = re.compile(r"Blog\s*[•|\\-]\s*([^•<]+)", re.I)
AMAZON_BLOCK_RE = re.compile(r"<div[^>]+data-section=['\"]blog_amazon_searches['\"][^>]*>", re.I)
PROSE_BLOCK_RE = re.compile(r"<div[^>]+class=['\"][^'\"]*\bprose\b[^'\"]*['\"][^>]*>", re.I)
MAX_W3_RE = re.compile(r"<div[^>]+class=['\"][^'\"]*\bmax-w-3xl\b[^'\"]*['\"][^>]*>", re.I)
ROOT_TAG_RE = re.compile(r"<([a-zA-Z0-9]+)\b[^>]*>", re.I)
FOOTER_RE = re.compile(r"<footer\b[\s\S]*?</footer>", re.I)
BODY_HTML_RE = re.compile(r"</?(?:body|html|main)\b[^>]*>", re.I)
TOP_BADGE_RE = re.compile(r"<p class=['\"][^'\"]*inline-flex[^'\"]*['\"][^>]*>[\s\S]*?</p>\s*", re.I)
TOP_DESC_RE = re.compile(
    r"<p class=['\"][^'\"]*(?:text-slate-600|text-blue-100)[^'\"]*['\"][^>]*>[\s\S]*?</p>\s*",
    re.I,
)
STYLE_WRAPPER_ARTICLE_RE = re.compile(
    r"^\s*<article class=['\"]container mx-auto px-4 py-10['\"]>\s*([\s\S]*?)\s*</article>\s*$",
    re.I,
)
STYLE_WRAPPER_CARD_RE = re.compile(
    r"^\s*<div class=['\"]max-w-4xl mx-auto bg-white rounded-2xl border border-slate-200 shadow-sm p-6 md:p-8['\"]>\s*([\s\S]*?)\s*</div>\s*$",
    re.I,
)
STYLE_WRAPPER_W3_RE = re.compile(
    r"^\s*<div class=['\"]max-w-3xl['\"]>\s*([\s\S]*?)\s*</div>\s*$",
    re.I,
)


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return " ".join(s.split()).strip()


def short_desc(s: str, max_len: int = 145) -> str:
    s = " ".join(s.split())
    if len(s) <= max_len:
        return s
    return s[: max_len - 1].rstrip() + "…"


def clean_title(title: str) -> str:
    title = strip_tags(title)
    suffix = " | BestDealsOnline"
    if title.endswith(suffix):
        return title[: -len(suffix)].strip()
    return title


def infer_category(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("kids", "toddler", "parents", "children")):
        return "Kids"
    if any(k in t for k in ("tool", "drill", "wrench", "socket", "garage")):
        return "Tools"
    if any(
        k in t
        for k in (
            "dash cam",
            "usb",
            "charger",
            "ssd",
            "tablet",
            "headphone",
            "smartwatch",
            "wireless",
            "phone",
            "laptop",
            "electronics",
        )
    ):
        return "Electronics"
    if any(
        k in t
        for k in (
            "air fryer",
            "coffee",
            "kitchen",
            "cooker",
            "thermometer",
            "skillet",
            "bento",
            "lunch box",
        )
    ):
        return "Kitchen"
    if any(k in t for k in ("home", "vacuum", "humidifier", "purifier", "smart home", "curtain")):
        return "Home"
    if "fitness" in t:
        return "Fitness"
    return "Deals"


def hero_svg(category: str) -> str:
    c = category.lower()
    if "elect" in c:
        return "/assets/hero/electronics.svg"
    if "home" in c:
        return "/assets/hero/home.svg"
    if "kitchen" in c:
        return "/assets/hero/kitchen.svg"
    if "tool" in c:
        return "/assets/hero/tools.svg"
    if "kids" in c:
        return "/assets/hero/kids.svg"
    if "beauty" in c:
        return "/assets/hero/beauty.svg"
    if "fitness" in c:
        return "/assets/hero/fitness.svg"
    if "pets" in c:
        return "/assets/hero/pets.svg"
    return "/assets/hero/default.svg"


def build_head(*, title: str, desc: str, canonical: str, og_type: str, blog_posting: dict | None = None) -> str:
    title_attr = html.escape(title, quote=True)
    desc_attr = html.escape(desc, quote=True)
    canonical_attr = html.escape(canonical, quote=True)

    posting_schema = ""
    if blog_posting:
        payload = json.dumps(blog_posting, indent=2)
        posting_schema = (
            "\n  <script type=\"application/ld+json\">\n"
            + "\n".join(f"    {line}" for line in payload.splitlines())
            + "\n  </script>\n"
        )

    org_schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Best Online Deals",
            "url": SITE,
            "logo": f"{SITE}/assets/og-default.svg",
            "sameAs": [],
        },
        indent=2,
    )
    website_schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Best Online Deals",
            "url": SITE,
        },
        indent=2,
    )

    return f"""<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
  <title>{title_attr}</title>
  <meta name="description" content="{desc_attr}" />
  <link rel="canonical" href="{canonical_attr}" />

  <meta property="og:title" content="{title_attr}" />
  <meta property="og:description" content="{desc_attr}" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:url" content="{canonical_attr}" />
  <meta property="og:image" content="{SITE}/assets/og-default.svg" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{SITE}/assets/og-default.svg" />

  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
  <style>:root{{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}</style>

  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-6GD5DK8067"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-6GD5DK8067', (function(){{try{{var A=/HeadlessChrome|Electron|Claude|PhantomJS|Puppeteer|Playwright|Selenium|Cypress|Lighthouse|GTmetrix|crawler|spider|bot/i;try{{if(navigator.webdriver===true||A.test(navigator.userAgent||'')){{return {{traffic_type:'internal'}};}}}}catch(e){{}}var K='bdo.internalTraffic';var q=new URLSearchParams(location.search).get('internal');if(q==='1'||q==='true'){{localStorage.setItem(K,'1');}}else if(q==='0'||q==='false'){{localStorage.removeItem(K);}}return localStorage.getItem(K)==='1'?{{traffic_type:'internal'}}:{{}};}}catch(e){{return {{}};}}}})());
  </script>
  <script defer src="/assets/track.js"></script>{posting_schema}

  <script type="application/ld+json">
{chr(10).join('    ' + line for line in org_schema.splitlines())}
  </script>

  <script type="application/ld+json">
{chr(10).join('    ' + line for line in website_schema.splitlines())}
  </script>
</head>"""


def chrome_open() -> str:
    return """<body class="bg-slate-950 text-slate-50">
  <div class="bg-slate-100 text-slate-700 text-xs border-b border-slate-200">
    <div class="container mx-auto px-4 py-2">
      <strong>Affiliate disclosure:</strong> When you buy through links on this site, we may earn a commission at no extra cost to you.
      <a class="underline inline-flex items-center min-h-10 px-1" href="/affiliate-disclosure.html">Details</a>
    </div>
  </div>

  <header class="bg-slate-900 text-white sticky top-0 z-40 shadow-lg">
    <div class="container mx-auto px-4 py-4 flex items-center justify-between gap-4">
      <a href="/" class="flex items-center gap-3">
        <span class="bg-yellow-500 text-slate-900 p-2 rounded-lg font-black">B</span>
        <span class="leading-tight">
          <span class="block font-extrabold tracking-tight text-lg">BestDealsOnline</span>
          <span class="block text-[10px] text-yellow-400 uppercase tracking-[0.25em]">Amazon Picks</span>
        </span>
      </a>
      <nav class="flex flex-wrap gap-2 text-sm text-slate-200 md:gap-4">
        <a class="inline-flex items-center justify-center min-h-10 px-3 py-2 rounded-full bg-white/5 hover:bg-white/10 hover:text-yellow-300 md:min-h-0 md:px-0 md:py-0 md:rounded-none md:bg-transparent md:hover:bg-transparent md:hover:text-yellow-400" href="/best-deals-online-today.html">Today</a>
        <a class="inline-flex items-center justify-center min-h-10 px-3 py-2 rounded-full bg-white/5 hover:bg-white/10 hover:text-yellow-300 md:min-h-0 md:px-0 md:py-0 md:rounded-none md:bg-transparent md:hover:bg-transparent md:hover:text-yellow-400" href="/electronics-deals.html">Electronics</a>
        <a class="inline-flex items-center justify-center min-h-10 px-3 py-2 rounded-full bg-white/5 hover:bg-white/10 hover:text-yellow-300 md:min-h-0 md:px-0 md:py-0 md:rounded-none md:bg-transparent md:hover:bg-transparent md:hover:text-yellow-400" href="/home-deals.html">Home</a>
        <a class="inline-flex items-center justify-center min-h-10 px-3 py-2 rounded-full bg-white/5 hover:bg-white/10 hover:text-yellow-300 md:min-h-0 md:px-0 md:py-0 md:rounded-none md:bg-transparent md:hover:bg-transparent md:hover:text-yellow-400" href="/kitchen-deals.html">Kitchen</a>
        <a class="inline-flex items-center justify-center min-h-10 px-3 py-2 rounded-full bg-white/5 hover:bg-white/10 hover:text-yellow-300 md:min-h-0 md:px-0 md:py-0 md:rounded-none md:bg-transparent md:hover:bg-transparent md:hover:text-yellow-400" href="/tools-deals.html">Tools</a>
        <a class="inline-flex items-center justify-center min-h-10 px-3 py-2 rounded-full bg-white/5 hover:bg-white/10 hover:text-yellow-300 md:min-h-0 md:px-0 md:py-0 md:rounded-none md:bg-transparent md:hover:bg-transparent md:hover:text-yellow-400" href="/blog/index.html">Blog</a>
      </nav>
    </div>
  </header>
"""


def chrome_footer() -> str:
    return """<footer class='border-t border-slate-200 bg-slate-50'>
  <div class='max-w-5xl mx-auto px-4 py-8 text-sm text-slate-500'>
    <div class='flex flex-col gap-3'>
      <div><strong>Affiliate disclosure:</strong> We may earn a commission when you buy through links on this site, at no extra cost to you. <span class='ml-2'><a class='underline inline-flex items-center min-h-10 px-1 hover:text-slate-900' href='/affiliate-disclosure.html'>Details</a></span></div>
      <div class='flex flex-wrap gap-x-4 gap-y-2'>
        <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/best-deals-online-today.html'>Today</a>
        <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/electronics-deals.html'>Electronics hub</a>
        <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/kitchen-deals.html'>Kitchen hub</a>
        <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/home-deals.html'>Home hub</a>
        <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/tools-deals.html'>Tools hub</a>
        <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/blog/index.html'>Blog</a>
      </div>
    </div>
  </div>
</footer>"""


def parse_first(pattern: re.Pattern[str], text: str, default: str = "") -> str:
    m = pattern.search(text)
    return m.group(1).strip() if m else default


def extract_balanced_element(text: str, start: int) -> str | None:
    open_m = ROOT_TAG_RE.match(text, start)
    if not open_m:
        return None

    tag = open_m.group(1).lower()
    token_re = re.compile(rf"</?{tag}\b[^>]*>", re.I)

    depth = 0
    for m in token_re.finditer(text, start):
        token = m.group(0)
        if token.startswith("</"):
            depth -= 1
            if depth == 0:
                return text[start : m.end()]
        elif not token.endswith("/>"):
            depth += 1

    return None


def extract_first_block(text: str, pattern: re.Pattern[str]) -> str | None:
    m = pattern.search(text)
    if not m:
        return None
    return extract_balanced_element(text, m.start())


def scrub_fragment(fragment: str) -> str:
    fragment = FOOTER_RE.sub("", fragment)
    fragment = BODY_HTML_RE.sub("", fragment)
    return fragment.strip()


def unwrap_style_wrappers(fragment: str) -> str:
    s = fragment.strip()
    for _ in range(8):
        prev = s
        m = STYLE_WRAPPER_ARTICLE_RE.match(s)
        if m:
            s = m.group(1).strip()
        m = STYLE_WRAPPER_CARD_RE.match(s)
        if m:
            s = m.group(1).strip()
        m = STYLE_WRAPPER_W3_RE.match(s)
        if m:
            s = m.group(1).strip()
        if s == prev:
            break
    return s


def strip_hero_duplicates(fragment: str) -> str:
    s = fragment.strip()
    s = TOP_BADGE_RE.sub("", s, count=1)
    s = re.sub(r"<h1[^>]*>[\s\S]*?</h1>\s*", "", s, count=1, flags=re.I)
    s = TOP_DESC_RE.sub("", s, count=1)
    return s.strip()


def extract_content_from_main(main_inner: str) -> str:
    if not main_inner:
        return ""

    s = main_inner
    s = re.split(r"</body>", s, maxsplit=1, flags=re.I)[0]
    s = re.split(r"<footer\b", s, maxsplit=1, flags=re.I)[0]
    s = scrub_fragment(s)

    amazon = extract_first_block(s, AMAZON_BLOCK_RE)
    prose = extract_first_block(s, PROSE_BLOCK_RE)
    if amazon and prose:
        return strip_hero_duplicates("\n\n".join((scrub_fragment(amazon), scrub_fragment(prose))))
    if prose:
        return strip_hero_duplicates(scrub_fragment(prose))

    w3 = extract_first_block(s, MAX_W3_RE)
    if w3:
        return strip_hero_duplicates(scrub_fragment(w3))

    s = unwrap_style_wrappers(s)
    s = strip_hero_duplicates(s)
    return scrub_fragment(s)


def collect_posts() -> list[dict[str, str]]:
    posts: list[dict[str, str]] = []
    for p in sorted(BLOG.glob("*.html")):
        if p.name == "index.html":
            continue
        html_txt = p.read_text(encoding="utf-8", errors="ignore")

        raw_title = parse_first(TITLE_RE, html_txt, p.stem.replace("-", " ").title())
        title = clean_title(raw_title)
        desc = parse_first(DESC_RE, html_txt, "Review-style buyer guide.")
        date = parse_first(UPDATED_RE, html_txt, parse_first(POSTED_RE, html_txt, ""))
        category = infer_category(title)

        posts.append(
            {
                "href": f"/blog/{p.name}",
                "title": title,
                "desc": desc,
                "date": date,
                "category": category,
                "thumb": hero_svg(category),
            }
        )

    posts.sort(key=lambda x: (x["date"], x["title"]), reverse=True)
    return posts


def restyle_index(path: Path, html_txt: str) -> str:
    title = "Blog | BestDealsOnline"
    desc = "Deal research, buyer patterns, and review-style category guides."
    canonical = f"{SITE}/blog/index.html"

    cards = []
    for post in collect_posts()[:30]:
        label = html.escape(post["title"])
        blurb = html.escape(short_desc(post["desc"]))
        category = html.escape(post["category"])
        href = html.escape(post["href"], quote=True)
        thumb = html.escape(post["thumb"], quote=True)

        cards.append(
            f"<a class='bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md p-4 flex items-start justify-between gap-4' href='{href}'>"
            f"<div class='flex items-start gap-4'>"
            f"<img src='{thumb}' width='120' height='80' loading='lazy' decoding='async' alt='{category}' class='w-20 h-16 rounded-md border border-slate-200 bg-slate-50 object-cover' />"
            f"<div><div class='text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500'>{category}</div>"
            f"<div class='font-bold text-slate-900 mt-1'>{label}</div>"
            f"<div class='text-sm text-slate-500 mt-1'>{blurb}</div></div></div>"
            "<span class='text-slate-400' aria-hidden='true'>→</span></a>"
        )

    page = f"""<!doctype html>
<html lang="en">
{build_head(title=title, desc=desc, canonical=canonical, og_type="website")}
{chrome_open()}
  <section class="bg-gradient-to-br from-indigo-900 via-blue-900 to-slate-900">
    <div class="container mx-auto px-4 py-10 md:py-14">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-end">
        <div class="lg:col-span-8">
          <p class="inline-flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/40 text-yellow-300 text-xs font-bold px-3 py-1 rounded-full mb-5">Blog • updated guides</p>
          <h1 class="text-3xl md:text-5xl font-extrabold tracking-tight">BestDealsOnline Blog</h1>
          <p class="text-blue-100 text-base md:text-lg mt-4 max-w-2xl">Review-style category guides, buyer behavior summaries, and quick links to live deal pages.</p>
        </div>
        <div class="hidden lg:block lg:col-span-4">
          <div class="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
            <img src="/assets/hero/electronics.svg" width="720" height="480" loading="lazy" decoding="async" alt="Blog" class="w-full h-auto opacity-95" />
          </div>
        </div>
      </div>
    </div>
  </section>

  <main class="bg-slate-50 text-slate-900">
    <div class="container mx-auto px-4 py-10">
      <section class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <h2 class="text-2xl font-extrabold">Latest posts</h2>
        <p class="text-slate-600 mt-2">Browse category research and quick-buy analysis.</p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          {''.join(cards)}
        </div>
      </section>
    </div>
    {chrome_footer()}
  </main>
</body>
</html>
"""
    return page


def restyle_post(path: Path, html_txt: str) -> str | None:
    full_title = parse_first(TITLE_RE, html_txt, "")
    desc = parse_first(DESC_RE, html_txt, "")
    canonical = parse_first(CANON_RE, html_txt, "")
    main_inner = parse_first(MAIN_RE, html_txt, "")
    if not (full_title and desc and canonical and main_inner):
        return None

    safe_title = clean_title(full_title)
    h1 = parse_first(H1_RE, html_txt, safe_title)
    h1 = strip_tags(h1) or safe_title

    badge = parse_first(BADGE_RE, html_txt, "")
    category = badge.title() if badge else infer_category(h1)
    published = parse_first(UPDATED_RE, html_txt, parse_first(POSTED_RE, html_txt, dt.date.today().isoformat()))

    cleaned = extract_content_from_main(main_inner)
    if not cleaned:
        return None

    blog_schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": h1,
        "datePublished": published,
        "dateModified": published,
        "author": {"@type": "Organization", "name": "BestDealsOnline"},
        "publisher": {"@type": "Organization", "name": "BestDealsOnline"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
    }

    page = f"""<!doctype html>
<html lang="en">
{build_head(title=full_title, desc=desc, canonical=canonical, og_type="article", blog_posting=blog_schema)}
{chrome_open()}
  <section class="bg-gradient-to-br from-indigo-900 via-blue-900 to-slate-900">
    <div class="container mx-auto px-4 py-10 md:py-14">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-end">
        <div class="lg:col-span-8">
          <p class="inline-flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/40 text-yellow-300 text-xs font-bold px-3 py-1 rounded-full mb-5">Blog • {html.escape(category)} • updated {html.escape(published)}</p>
          <h1 class="text-3xl md:text-5xl font-extrabold tracking-tight">{html.escape(h1)}</h1>
          <p class="text-blue-100 text-base md:text-lg mt-4 max-w-2xl">{html.escape(desc)}</p>
        </div>
        <div class="hidden lg:block lg:col-span-4">
          <div class="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
            <img src="{hero_svg(category)}" width="720" height="480" loading="lazy" decoding="async" alt="{html.escape(category)}" class="w-full h-auto opacity-95" />
          </div>
        </div>
      </div>
    </div>
  </section>

  <main class="bg-slate-50 text-slate-900">
    <article class="container mx-auto px-4 py-10">
      <div class="max-w-4xl mx-auto bg-white rounded-2xl border border-slate-200 shadow-sm p-6 md:p-8">
        {cleaned}
      </div>
    </article>
    {chrome_footer()}
  </main>
</body>
</html>
"""
    return page


def main() -> None:
    if not BLOG.exists():
        print("blog dir missing")
        return

    changed = 0
    for p in sorted(BLOG.glob("*.html")):
        html_txt = p.read_text(encoding="utf-8", errors="ignore")
        if p.name == "index.html":
            out = restyle_index(p, html_txt)
        else:
            out = restyle_post(p, html_txt)
            if out is None:
                continue

        if out != html_txt:
            p.write_text(out, encoding="utf-8")
            changed += 1

    print(f"restyled {changed} blog pages")


if __name__ == "__main__":
    main()
