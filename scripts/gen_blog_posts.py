#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from datetime import date
import html
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://bestdealsonline.us"

NAV = """
      <nav class=\"hidden md:flex flex-wrap gap-4 text-sm text-slate-200\">\n        <a class=\"hover:text-yellow-400\" href=\"/best-deals-online-today.html\">Today</a>\n        <a class=\"hover:text-yellow-400\" href=\"/electronics-deals.html\">Electronics</a>\n        <a class=\"hover:text-yellow-400\" href=\"/home-deals.html\">Home</a>\n        <a class=\"hover:text-yellow-400\" href=\"/kitchen-deals.html\">Kitchen</a>\n        <a class=\"hover:text-yellow-400\" href=\"/tools-deals.html\">Tools</a>\n        <a class=\"hover:text-yellow-400\" href=\"/kids-deals.html\">Kids</a>\n        <a class=\"hover:text-yellow-400\" href=\"/blog/index.html\">Blog</a>\n      </nav>
""".strip("\n")


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def page_html(*, slug: str, title: str, description: str, category: str, sections: list[tuple[str, str]], internal_links: list[tuple[str, str]], amz_queries: list[tuple[str, str]]):
    canonical = f"{SITE}/blog/{slug}"
    today = date.today().isoformat()

    def h2(t: str) -> str:
        return f"<h2 class='text-xl md:text-2xl font-extrabold text-slate-900 mt-10 mb-3'>{html.escape(t)}</h2>"

    def p(txt: str) -> str:
        return f"<p class='text-slate-700 leading-relaxed mt-3'>{html.escape(txt)}</p>"

    def li(txt: str) -> str:
        return f"<li class='mt-2 text-slate-700'>{html.escape(txt)}</li>"

    # Amazon search links (no product claims)
    amz_cards = []
    for label, query in amz_queries:
        from urllib.parse import quote
        href = (
            f"https://www.amazon.com/s?k={quote(query)}"
            f"&tag=bestdeals0ad2-20&utm_source=bestdealsonline&utm_medium=blog&utm_campaign={html.escape(slug)}"
        )
        amz_cards.append(
            f"<a class='bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-md p-5 flex items-start justify-between gap-4' "
            f"href='{href}' target='_blank' rel='nofollow noopener noreferrer'>"
            f"<div><div class='text-[10px] font-bold text-blue-600 uppercase tracking-[0.25em]'>Amazon search</div>"
            f"<div class='font-extrabold text-slate-900 mt-1'>{html.escape(label)}</div>"
            f"<div class='text-sm text-slate-600 mt-1'>See live pricing and reviews</div></div>"
            f"<span class='text-slate-400' aria-hidden='true'>↗</span></a>"
        )

    body_sections = []
    for heading, content in sections:
        body_sections.append(h2(heading) + "\n" + content)

    internal = "".join(
        f"<a class='text-sm underline hover:text-slate-900' href='{href}'>{html.escape(label)}</a>" for href, label in internal_links
    )

    return f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no' />
  <title>{html.escape(title)} | BestDealsOnline</title>
  <meta name='description' content='{html.escape(description)}' />
  <link rel='canonical' href='{canonical}' />

  <meta property='og:title' content='{html.escape(title)} | BestDealsOnline' />
  <meta property='og:description' content='{html.escape(description)}' />
  <meta property='og:type' content='article' />
  <meta property='og:url' content='{canonical}' />
  <meta property='og:image' content='https://bestdealsonline.us/assets/og-default.svg' />
  <meta name='twitter:card' content='summary_large_image' />
  <meta name='twitter:image' content='https://bestdealsonline.us/assets/og-default.svg' />

  <link rel='icon' href='/assets/favicon.svg' type='image/svg+xml' />
  <script src='https://cdn.tailwindcss.com'></script>
  <link href='https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap' rel='stylesheet'>
  <style>:root{{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}</style>

  <script type='application/ld+json'>
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": {html.escape(repr(title))},
    "datePublished": "{today}",
    "dateModified": "{today}",
    "author": {{"@type": "Organization", "name": "BestDealsOnline"}},
    "publisher": {{"@type": "Organization", "name": "BestDealsOnline"}},
    "mainEntityOfPage": {{"@type": "WebPage", "@id": "{canonical}"}}
  }}
  </script>
</head>
<body class='bg-slate-50 text-slate-900'>
  <div class='bg-slate-100 text-slate-700 text-xs border-b border-slate-200'>
    <div class='container mx-auto px-4 py-2'>
      <strong>Affiliate disclosure:</strong> When you buy through links on this site, we may earn a commission at no extra cost to you.
      <a class='underline' href='/affiliate-disclosure.html'>Details</a>
    </div>
  </div>

  <header class='bg-slate-900 text-white sticky top-0 z-40 shadow-lg'>
    <div class='container mx-auto px-4 py-4 flex items-center justify-between gap-4'>
      <a href='/' class='flex items-center gap-3'>
        <span class='bg-yellow-500 text-slate-900 p-2 rounded-lg font-black'>B</span>
        <span class='leading-tight'>
          <span class='block font-extrabold tracking-tight text-lg'>BestDealsOnline</span>
          <span class='block text-[10px] text-yellow-400 uppercase tracking-[0.25em]'>Amazon Picks</span>
        </span>
      </a>
      {NAV}
    </div>
  </header>

  <main class='container mx-auto px-4 py-10 max-w-4xl'>
    <div class='inline-flex items-center gap-2 bg-blue-50 border border-blue-200 text-blue-700 text-xs font-bold px-3 py-1 rounded-full'>
      Blog • {html.escape(category)} • updated {today}
    </div>

    <h1 class='text-3xl md:text-5xl font-extrabold tracking-tight mt-4'>{html.escape(title)}</h1>
    <p class='text-slate-600 mt-4 text-lg leading-relaxed'>{html.escape(description)}</p>

    <div class='grid grid-cols-1 md:grid-cols-2 gap-4 mt-8' data-section='blog_amazon_searches'>
      {''.join(amz_cards)}
    </div>

    <div class='prose max-w-none mt-6'>
      {''.join(body_sections)}

      <div class='mt-12 bg-white rounded-2xl border border-slate-100 p-6'>
        <div class='text-xs font-bold uppercase tracking-[0.25em] text-slate-500'>Related</div>
        <div class='mt-3 flex flex-wrap gap-x-4 gap-y-2' data-section='blog_related_internal'>
          {internal}
        </div>
      </div>

      <div class='mt-10 text-xs text-slate-500'>
        Note: This article summarizes common themes buyers mention in public reviews and product listings. It does not claim hands-on testing.
      </div>
    </div>
  </main>
</body>
</html>
"""


def main():
    blog_dir = ROOT / "blog"
    blog_dir.mkdir(exist_ok=True)

    posts = [
        # Electronics
        {
            "title": "USB-C Chargers: What Buyers Like, What They Complain About, and What to Look For",
            "description": "A neutral, review-informed guide to USB-C chargers: key features, common pros/cons, and how to choose one that matches your devices.",
            "category": "Electronics",
            "amz_queries": [
                ("USB-C charger deals", "usb c charger"),
                ("GaN USB-C charger", "gan usb c charger"),
                ("USB-C charger 65W", "usb c charger 65w"),
                ("USB-C charger 100W", "usb c charger 100w"),
            ],
            "internal": [
                ("/electronics-deals.html", "Electronics hub"),
                ("/usb-c-charger-under-50.html", "USB-C chargers under $50"),
                ("/surge-protector-under-25.html", "Surge protectors under $25"),
            ],
            "sections": [
                ("What reviewers consistently like", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Faster charging compared to older USB-A bricks, especially for modern phones and tablets.</li>
<li class='mt-2 text-slate-700'>Multi-port convenience (one charger for phone + earbuds + watch).</li>
<li class='mt-2 text-slate-700'>Smaller GaN designs that are easier to travel with.</li>
</ul>"""),
                ("Common complaints to watch for", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Heat: compact chargers can run warm, especially at higher wattage.</li>
<li class='mt-2 text-slate-700'>Port sharing: advertised wattage may be split across ports when charging multiple devices.</li>
<li class='mt-2 text-slate-700'>Cable confusion: USB-C to USB-C is often required for fast charging; old cables limit speed.</li>
</ul>"""),
                ("Feature checklist (simple)", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Wattage: match your laptop/phone needs (ex: 20W+ phones, 45–100W laptops).</li>
<li class='mt-2 text-slate-700'>PD support (Power Delivery) and PPS (often helps some Android fast charge).</li>
<li class='mt-2 text-slate-700'>Port types: USB-C first; USB-A optional for older devices.</li>
<li class='mt-2 text-slate-700'>Foldable prongs for travel.</li>
</ul>"""),
            ],
        },
        {
            "title": "Power Banks: Pros/Cons From Buyer Reviews (Capacity, Speed, Size, and Real-World Use)",
            "description": "A neutral guide to choosing a power bank using common buyer feedback: what matters for travel, commuting, and emergency backup.",
            "category": "Electronics",
            "amz_queries": [
                ("Power bank deals", "power bank"),
                ("Power bank 20000mAh", "power bank 20000mah"),
                ("Magnetic power bank", "magnetic power bank"),
            ],
            "internal": [
                ("/electronics-deals.html", "Electronics hub"),
                ("/power-bank-under-50.html", "Power banks under $50"),
                ("/usb-c-cable-under-15.html", "USB-C cables under $15"),
            ],
            "sections": [
                ("What people like", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Peace of mind: having 1–2 extra phone charges on demand.</li>
<li class='mt-2 text-slate-700'>USB-C input/output for faster recharge and modern compatibility.</li>
<li class='mt-2 text-slate-700'>Digital % displays are preferred over 4-dot indicators.</li>
</ul>"""),
                ("What people dislike", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Weight: higher capacity usually means bulky and heavy.</li>
<li class='mt-2 text-slate-700'>Advertised capacity vs usable capacity (real output is lower due to conversion losses).</li>
<li class='mt-2 text-slate-700'>Slow charging when using older USB-A ports/cables.</li>
</ul>"""),
                ("How to pick the right size", """<p class='text-slate-700 leading-relaxed mt-3'>If you want something pocketable, many buyers prefer smaller banks for daily carry. For travel, a larger capacity is more common. A good rule is to prioritize the form factor you will actually bring with you.</p>"""),
            ],
        },
        {
            "title": "Wireless Chargers: What Reviewers Say About Speed, Heat, and Reliability",
            "description": "A neutral summary of common buyer feedback about wireless chargers: real-world charging speed, heat, and what features matter.",
            "category": "Electronics",
            "amz_queries": [
                ("Wireless charger deals", "wireless charger"),
                ("MagSafe-compatible charger", "magsafe compatible wireless charger"),
                ("Wireless charger stand", "wireless charger stand"),
            ],
            "internal": [
                ("/electronics-deals.html", "Electronics hub"),
                ("/wireless-charger-under-25.html", "Wireless chargers under $25"),
                ("/phone-car-mount-under-20.html", "Phone car mounts under $20"),
            ],
            "sections": [
                ("Common pros", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Convenience: drop-and-go charging at the desk or bedside.</li>
<li class='mt-2 text-slate-700'>Stands help visibility for notifications and video calls.</li>
</ul>"""),
                ("Common cons", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Slower than wired charging, especially if alignment is finicky.</li>
<li class='mt-2 text-slate-700'>Heat can increase over long sessions; some buyers prefer units with better ventilation.</li>
</ul>"""),
                ("What to look for", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Compatibility with your phone (including cases).</li>
<li class='mt-2 text-slate-700'>Non-slip surface and stable base.</li>
<li class='mt-2 text-slate-700'>USB-C input and a decent wall adapter.</li>
</ul>"""),
            ],
        },

        # Kids
        {
            "title": "Kids Headphones: What Parents and Buyers Mention Most (Comfort, Volume Limits, Durability)",
            "description": "A neutral, review-informed guide to kids headphones: common pros/cons, what to look for, and how to avoid the most frequent issues.",
            "category": "Kids",
            "amz_queries": [
                ("Kids headphones", "kids headphones"),
                ("Kids headphones with mic", "kids headphones with mic"),
                ("Bluetooth kids headphones", "bluetooth kids headphones"),
            ],
            "internal": [
                ("/kids-deals.html", "Kids hub"),
                ("/kids-headphones-under-50.html", "Kids headphones under $50"),
                ("/kids-backpack-under-30.html", "Kids backpacks under $30"),
            ],
            "sections": [
                ("What buyers like", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Comfort padding and adjustable bands for longer use.</li>
<li class='mt-2 text-slate-700'>Simple controls and reliable pairing for Bluetooth models.</li>
<li class='mt-2 text-slate-700'>Foldable designs for backpacks.</li>
</ul>"""),
                ("Common complaints", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Build quality: hinges and cables can be failure points.</li>
<li class='mt-2 text-slate-700'>Volume limiting that is either too quiet or inconsistently enforced.</li>
<li class='mt-2 text-slate-700'>Mic quality for school calls varies a lot.</li>
</ul>"""),
            ],
        },
        {
            "title": "Learning Toys and Science Kits: How Reviewers Separate the Good From the Gimmicky",
            "description": "A neutral guide to choosing learning toys and science kits based on common buyer feedback: age fit, instructions, mess factor, and replay value.",
            "category": "Kids",
            "amz_queries": [
                ("Science kits for kids", "science kits for kids"),
                ("Learning toys", "learning toys"),
            ],
            "internal": [
                ("/kids-deals.html", "Kids hub"),
                ("/science-kits-under-25.html", "Science kits under $25"),
                ("/learning-toys-under-25.html", "Learning toys under $25"),
            ],
            "sections": [
                ("What tends to earn great reviews", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Clear instructions and enough materials to complete multiple activities.</li>
<li class='mt-2 text-slate-700'>Age-appropriate challenge (not too easy, not too frustrating).</li>
<li class='mt-2 text-slate-700'>Good packaging for storage between sessions.</li>
</ul>"""),
                ("Common pitfalls", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Tiny parts and short-lived activities that feel like a one-time novelty.</li>
<li class='mt-2 text-slate-700'>Instructions that assume supplies you don’t have at home.</li>
</ul>"""),
            ],
        },

        # Kitchen
        {
            "title": "Air Fryers: The Most Common Pros and Cons Buyers Mention (Capacity, Cleanup, Noise)",
            "description": "A neutral summary of air fryer buyer feedback: what people love, what annoys them, and which features matter most.",
            "category": "Kitchen",
            "amz_queries": [
                ("Air fryer deals", "air fryer"),
                ("Dual basket air fryer", "dual basket air fryer"),
                ("Air fryer accessories", "air fryer accessories"),
            ],
            "internal": [
                ("/kitchen-deals.html", "Kitchen hub"),
                ("/air-fryer-under-100.html", "Air fryers under $100"),
                ("/air-fryer-accessories-under-50.html", "Air fryer accessories under $50"),
            ],
            "sections": [
                ("Pros that show up again and again", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Crisp results faster than ovens for many foods.</li>
<li class='mt-2 text-slate-700'>Convenience for weeknights and small households.</li>
</ul>"""),
                ("Cons buyers mention", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Capacity confusion: basket size can be smaller than expected.</li>
<li class='mt-2 text-slate-700'>Cleanup: nonstick surfaces help, but some shapes are awkward to wash.</li>
<li class='mt-2 text-slate-700'>Noise and countertop space.</li>
</ul>"""),
            ],
        },
        {
            "title": "Coffee Makers Under $100: What Reviewers Care About (Taste, Reliability, Ease)",
            "description": "A neutral guide to coffee makers under $100 based on common buyer feedback: taste, reliability, cleaning, and daily usability.",
            "category": "Kitchen",
            "amz_queries": [
                ("Coffee maker under $100", "coffee maker under 100"),
                ("Single serve coffee maker", "single serve coffee maker"),
            ],
            "internal": [
                ("/kitchen-deals.html", "Kitchen hub"),
                ("/coffee-maker-under-100.html", "Coffee makers under $100"),
                ("/electric-kettle-under-50.html", "Electric kettles under $50"),
            ],
            "sections": [
                ("What buyers like", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Fast brew times and consistent temperature.</li>
<li class='mt-2 text-slate-700'>Simple controls and easy-to-clean parts.</li>
</ul>"""),
                ("What buyers dislike", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Plastic taste complaints when units run hot.</li>
<li class='mt-2 text-slate-700'>Carafes that drip or lids that are awkward to clean.</li>
</ul>"""),
            ],
        },

        # Home
        {
            "title": "Blackout Curtains: What Reviewers Say About Light Blocking, Sizing, and Fabric",
            "description": "A neutral, review-informed guide to blackout curtains: what matters for bedrooms, apartments, and shift-work sleep.",
            "category": "Home",
            "amz_queries": [
                ("Blackout curtains deals", "blackout curtains"),
                ("Thermal blackout curtains", "thermal blackout curtains"),
            ],
            "internal": [
                ("/home-deals.html", "Home hub"),
                ("/blackout-curtains-under-50.html", "Blackout curtains under $50"),
                ("/bed-sheet-set-under-50.html", "Bed sheet sets under $50"),
            ],
            "sections": [
                ("Pros buyers mention", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Better sleep and less glare for TVs/screens.</li>
<li class='mt-2 text-slate-700'>Some buyers report lower AC costs with thicker fabrics.</li>
</ul>"""),
                ("Cons buyers mention", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Sizing issues: length and width can be misunderstood.</li>
<li class='mt-2 text-slate-700'>Light leaks around the edges without proper curtain width.</li>
</ul>"""),
            ],
        },
        {
            "title": "Humidifiers Under $50: What Reviewers Like and What They Warn About",
            "description": "A neutral summary of humidifier buyer feedback: noise, cleaning effort, leak risk, and what features matter most.",
            "category": "Home",
            "amz_queries": [
                ("Humidifier under $50", "humidifier under 50"),
                ("Cool mist humidifier", "cool mist humidifier"),
            ],
            "internal": [
                ("/home-deals.html", "Home hub"),
                ("/humidifier-under-50.html", "Humidifiers under $50"),
                ("/home-air-purifier-under-100.html", "Home air purifiers under $100"),
            ],
            "sections": [
                ("What buyers like", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Quiet operation for bedrooms.</li>
<li class='mt-2 text-slate-700'>Simple refill and easy-to-read water levels.</li>
</ul>"""),
                ("What buyers dislike", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Cleaning: mineral buildup and mold risk if ignored.</li>
<li class='mt-2 text-slate-700'>Leaks when tanks are bumped or seals wear out.</li>
</ul>"""),
            ],
        },

        {
            "title": "Robot Vacuums: What Reviewers Actually Mention (Navigation, Pet Hair, Maintenance)",
            "description": "A neutral summary of robot vacuum buyer feedback: navigation, pet hair pickup, and ongoing maintenance.",
            "category": "Home",
            "amz_queries": [
                ("Robot vacuum deals", "robot vacuum"),
                ("Robot vacuum for pet hair", "robot vacuum pet hair"),
                ("Self-emptying robot vacuum", "self emptying robot vacuum"),
            ],
            "internal": [
                ("/home-deals.html", "Home hub"),
                ("/robot-vacuum-under-150.html", "Robot vacuums under $150"),
                ("/stick-vacuum-under-100.html", "Stick vacuums under $100"),
            ],
            "sections": [
                ("Why people still like robot vacuums", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Daily resets: crumbs and pet hair disappear without hauling out a full-size vacuum.</li>
<li class='mt-2 text-slate-700'>App zones and schedules keep high-traffic areas cleaner than weekly deep cleans alone.</li>
<li class='mt-2 text-slate-700'>Self-empty docks reduce how often you touch the dust bin.</li>
</ul>"""),
                ("Frustrations buyers mention", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Navigation still gets tripped up by cords, socks, and threshold lips.</li>
<li class='mt-2 text-slate-700'>Pet hair can clog brushes unless you clean rollers weekly.</li>
<li class='mt-2 text-slate-700'>Replacement filters and side brushes add to the real cost of ownership.</li>
</ul>"""),
                ("Maintenance takeaways", """<p class='text-slate-700 leading-relaxed mt-3'>Reviewers who stay happy treat robot vacuums like dishwashers: empty bins, wipe sensors, and run brush-clean cycles on a schedule. Skipping upkeep leads to failed navigation and weak suction.</p>"""),
            ],
        },
        {
            "title": "Kids Smartwatches: What Parents Care About (Safety, Battery, Controls)",
            "description": "A review-informed look at kids smartwatch feedback: GPS accuracy, call controls, battery life, and durability.",
            "category": "Kids",
            "amz_queries": [
                ("Kids smartwatch deals", "kids smartwatch"),
                ("Kids smartwatch GPS", "kids smartwatch gps"),
                ("Waterproof kids smartwatch", "waterproof kids smartwatch"),
            ],
            "internal": [
                ("/kids-deals.html", "Kids hub"),
                ("/kids-smartwatch-under-80.html", "Kids smartwatches under $80"),
                ("/kids-headphones-under-50.html", "Kids headphones under $50"),
            ],
            "sections": [
                ("Features parents actually appreciate", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>GPS + safe zones: alerts when kids leave preset areas.</li>
<li class='mt-2 text-slate-700'>Whitelisted contacts so unknown numbers can’t reach them.</li>
<li class='mt-2 text-slate-700'>Water-resistant cases that survive sprinklers and hand washing.</li>
</ul>"""),
                ("Common complaints", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Battery life drops fast if GPS pings are set to every few minutes.</li>
<li class='mt-2 text-slate-700'>Some carrier-specific models require monthly plan fees that catch parents off guard.</li>
<li class='mt-2 text-slate-700'>Apps can feel dated or buggy, especially on Android tablets.</li>
</ul>"""),
                ("Simple buying checklist", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Decide if you need LTE or Wi-Fi-only tracking.</li>
<li class='mt-2 text-slate-700'>Look for replaceable bands and shock protection for playground use.</li>
<li class='mt-2 text-slate-700'>Confirm the watch supports your carrier or comes with its own SIM.</li>
</ul>"""),
            ],
        },

    ]

    for post in posts:
        slug = slugify(post["title"]) + ".html"
        out = blog_dir / slug
        if out.exists():
            continue
        html_txt = page_html(
            slug=slug,
            title=post["title"],
            description=post["description"],
            category=post["category"],
            sections=post["sections"],
            internal_links=post["internal"],
            amz_queries=post["amz_queries"],
        )
        out.write_text(html_txt, encoding="utf-8")
        print("wrote", out.relative_to(ROOT))

    # Update blog index with newest posts
    items = []
    for p in sorted(blog_dir.glob("*.html")):
        if p.name == "index.html":
            continue
        items.append(p)

    # Simple index (latest first)
    links = []
    for p in sorted(items, key=lambda x: x.stat().st_mtime, reverse=True)[:50]:
        title = p.stem.replace("-", " ").title()
        links.append(
            f"<li class='mt-2'><a class='underline inline-flex items-center min-h-10 px-1 hover:text-slate-900' href='/{p.relative_to(ROOT).as_posix()}'>{html.escape(title)}</a></li>"
        )

    index_html = f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no' />
  <title>Blog | BestDealsOnline</title>
  <meta name='description' content='Neutral buying guides based on common buyer feedback and product features. Amazon-only deep links.' />
  <link rel='canonical' href='{SITE}/blog/index.html' />
  <meta property='og:title' content='Blog | BestDealsOnline' />
  <meta property='og:description' content='Neutral buying guides based on common buyer feedback and product features. Amazon-only deep links.' />
  <meta property='og:type' content='website' />
  <meta property='og:url' content='{SITE}/blog/index.html' />
  <meta property='og:image' content='https://bestdealsonline.us/assets/og-default.svg' />
  <meta name='twitter:card' content='summary_large_image' />
  <meta name='twitter:image' content='https://bestdealsonline.us/assets/og-default.svg' />

  <link rel='icon' href='/assets/favicon.svg' type='image/svg+xml' />
  <script src='https://cdn.tailwindcss.com'></script>
  <link href='https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap' rel='stylesheet'>
  <style>:root{{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}</style>
</head>
<body class='bg-slate-50 text-slate-900'>
  <div class='bg-slate-100 text-slate-700 text-xs border-b border-slate-200'>
    <div class='container mx-auto px-4 py-2'>
      <strong>Affiliate disclosure:</strong> When you buy through links on this site, we may earn a commission at no extra cost to you.
      <a class='underline' href='/affiliate-disclosure.html'>Details</a>
    </div>
  </div>

  <header class='bg-slate-900 text-white sticky top-0 z-40 shadow-lg'>
    <div class='container mx-auto px-4 py-4 flex items-center justify-between gap-4'>
      <a href='/' class='flex items-center gap-3'>
        <span class='bg-yellow-500 text-slate-900 p-2 rounded-lg font-black'>B</span>
        <span class='leading-tight'>
          <span class='block font-extrabold tracking-tight text-lg'>BestDealsOnline</span>
          <span class='block text-[10px] text-yellow-400 uppercase tracking-[0.25em]'>Amazon Picks</span>
        </span>
      </a>
      {NAV}
    </div>
  </header>

  <main class='container mx-auto px-4 py-10 max-w-4xl'>
    <h1 class='text-3xl md:text-5xl font-extrabold tracking-tight'>Blog</h1>
    <p class='text-slate-600 mt-4 text-lg'>Neutral buying guides based on common buyer feedback and product features (Amazon-only deep links).</p>

    <div class='mt-8 bg-white rounded-2xl border border-slate-100 p-6'>
      <div class='text-xs font-bold uppercase tracking-[0.25em] text-slate-500'>Latest posts</div>
      <ul class='mt-4'>{''.join(links)}</ul>
    </div>
  </main>
</body>
</html>
"""

    (blog_dir / "index.html").write_text(index_html, encoding="utf-8")
    print("updated blog/index.html")


if __name__ == "__main__":
    main()
