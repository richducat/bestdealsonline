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
            "title": "Portable SSDs vs External Hard Drives: What Buyers Say About Speed, Size, and Value",
            "description": "A neutral, review-informed comparison of portable SSDs and external hard drives under $100: speed, durability, and where each makes sense.",
            "category": "Electronics",
            "amz_queries": [
                ("Portable SSD deals", "portable ssd"),
                ("External hard drive 1TB", "external hard drive 1tb"),
                ("USB-C external SSD", "usb c external ssd"),
            ],
            "internal": [
                ("/electronics-deals.html", "Electronics hub"),
                ("/portable-ssd-under-100.html", "Portable SSDs under $100"),
                ("/external-hard-drive-under-75.html", "External hard drives under $75"),
                ("/electronics-under-100.html", "Electronics under $100"),
            ],
            "sections": [
                ("What SSD buyers consistently like", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Faster file transfers, especially for large photo/video libraries.</li>
<li class='mt-2 text-slate-700'>Smaller, lighter builds that are easier to toss in a bag.</li>
<li class='mt-2 text-slate-700'>Better drop resistance due to no moving parts.</li>
</ul>"""),
                ("What hard drive buyers like", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>More storage per dollar, especially at higher capacities.</li>
<li class='mt-2 text-slate-700'>Simple plug-and-play use for backups and archives.</li>
</ul>"""),
                ("Quick decision guide", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Pick an SSD for speed, travel, and day-to-day active files.</li>
<li class='mt-2 text-slate-700'>Pick an HDD for budget-friendly bulk storage and backups.</li>
<li class='mt-2 text-slate-700'>Check cable type (USB-C vs USB-A) and included adapters.</li>
</ul>"""),
            ],
        },
        {
            "title": "Kids Lunch Boxes and Bento Sets: What Reviewers Mention Most (Leaks, Size, Insulation)",
            "description": "A neutral, review-informed guide to kids lunch boxes and bento sets: what parents like, common complaints, and simple feature checks.",
            "category": "Kids",
            "amz_queries": [
                ("Kids lunch box", "kids lunch box"),
                ("Insulated kids lunch box", "insulated kids lunch box"),
                ("Bento lunch box for kids", "bento lunch box for kids"),
            ],
            "internal": [
                ("/kids-deals.html", "Kids hub"),
                ("/kids-lunch-box-under-25.html", "Kids lunch boxes under $25"),
                ("/bento-lunch-box-under-25.html", "Bento lunch boxes under $25"),
                ("/kids-backpack-under-30.html", "Kids backpacks under $30"),
            ],
            "sections": [
                ("What buyers like", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Insulation that keeps food cool until lunchtime.</li>
<li class='mt-2 text-slate-700'>Easy-to-clean liners and containers.</li>
<li class='mt-2 text-slate-700'>Sizes that fit standard backpacks without being bulky.</li>
</ul>"""),
                ("Common complaints", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Leaky seals on bento boxes when carried sideways.</li>
<li class='mt-2 text-slate-700'>Zippers or handles that wear out with daily use.</li>
</ul>"""),
                ("Simple checklist", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Leak resistance (especially for sauces or fruit).</li>
<li class='mt-2 text-slate-700'>Insulation thickness vs. available bag space.</li>
<li class='mt-2 text-slate-700'>Dishwasher-safe components where possible.</li>
</ul>"""),
            ],
        },
        {
            "title": "Cast Iron Skillets: What Reviewers Say About Weight, Seasoning, and Heat Retention",
            "description": "A neutral, review-informed guide to cast iron skillets: what buyers like, common complaints, and what features matter most.",
            "category": "Kitchen",
            "amz_queries": [
                ("Cast iron skillet", "cast iron skillet"),
                ("Pre-seasoned cast iron skillet", "pre seasoned cast iron skillet"),
                ("Cast iron skillet 10 inch", "cast iron skillet 10 inch"),
            ],
            "internal": [
                ("/kitchen-deals.html", "Kitchen hub"),
                ("/cast-iron-skillet-under-50.html", "Cast iron skillets under $50"),
                ("/cast-iron-skillet-under-100.html", "Cast iron skillets under $100"),
                ("/knife-sharpener-under-30.html", "Knife sharpeners under $30"),
            ],
            "sections": [
                ("What reviewers consistently like", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Heat retention and even browning for searing and baking.</li>
<li class='mt-2 text-slate-700'>Long lifespan when properly seasoned and dried.</li>
<li class='mt-2 text-slate-700'>Versatility: stovetop, oven, and even grill use.</li>
</ul>"""),
                ("Common complaints", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Weight: some buyers find lifting or flipping foods difficult.</li>
<li class='mt-2 text-slate-700'>Seasoning upkeep and rust if left wet.</li>
<li class='mt-2 text-slate-700'>Inconsistent factory seasoning on budget pans.</li>
</ul>"""),
                ("Quick buying checklist", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Size: 10–12 inch is the most common all-purpose range.</li>
<li class='mt-2 text-slate-700'>Handle length and helper handle for easier lifting.</li>
<li class='mt-2 text-slate-700'>Pre-seasoned vs. raw (most buyers prefer pre-seasoned).</li>
</ul>"""),
            ],
        },
        {
            "title": "Toddler Toys: What Parents Mention Most (Durability, Mess, Age Fit)",
            "description": "A neutral, review-informed guide to toddler toys based on common buyer feedback: durability, cleanup, and age-appropriate difficulty.",
            "category": "Kids",
            "amz_queries": [
                ("Toddler toys", "toddler toys"),
                ("Toddler learning toys", "toddler learning toys"),
                ("Montessori toys for toddlers", "montessori toys for toddlers"),
            ],
            "internal": [
                ("/kids-deals.html", "Kids hub"),
                ("/toddler-toys-under-50.html", "Toddler toys under $50"),
                ("/toddler-toys-under-25.html", "Toddler toys under $25"),
                ("/learning-toys-under-25.html", "Learning toys under $25"),
            ],
            "sections": [
                ("What parents like", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Durable builds that survive drops and rough play.</li>
<li class='mt-2 text-slate-700'>Open-ended play value (stacking, sorting, pretend play).</li>
<li class='mt-2 text-slate-700'>Easy cleanup with minimal tiny parts.</li>
</ul>"""),
                ("Common complaints", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Pieces that are too small or easy to lose.</li>
<li class='mt-2 text-slate-700'>Toys that are too advanced for the stated age range.</li>
<li class='mt-2 text-slate-700'>Batteries or noise levels that parents regret.</li>
</ul>"""),
                ("Quick buying checklist", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Age range: aim for the middle of your child’s age band.</li>
<li class='mt-2 text-slate-700'>Material: solid wood or thick plastic tends to last longer.</li>
<li class='mt-2 text-slate-700'>Storage: bins or bags help keep parts together.</li>
</ul>"""),
            ],
        },
        {
            "title": "GaN Chargers: What Buyers Like, What Bugs Them, and How to Choose",
            "description": "A neutral, review-informed guide to GaN chargers: common pros/cons, heat concerns, and how to match wattage to your devices.",
            "category": "Electronics",
            "amz_queries": [
                ("GaN charger deals", "gan charger"),
                ("GaN charger 65W", "gan charger 65w"),
                ("GaN charger 100W", "gan charger 100w"),
            ],
            "internal": [
                ("/electronics-deals.html", "Electronics hub"),
                ("/gan-charger-under-50.html", "GaN chargers under $50"),
                ("/gan-charger-under-100.html", "GaN chargers under $100"),
                ("/usb-c-charger-under-50.html", "USB-C chargers under $50"),
            ],
            "sections": [
                ("Why buyers like GaN chargers", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Smaller size for the same wattage compared to older bricks.</li>
<li class='mt-2 text-slate-700'>Multi-port models that power a laptop + phone at once.</li>
<li class='mt-2 text-slate-700'>Travel-friendly designs with foldable prongs.</li>
</ul>"""),
                ("Common complaints", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Heat under heavy load, especially at 100W+.</li>
<li class='mt-2 text-slate-700'>Power sharing: total wattage is split across ports.</li>
<li class='mt-2 text-slate-700'>Cable confusion (USB-C to USB-C required for full speed).</li>
</ul>"""),
                ("Quick pick checklist", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Match wattage to your laptop/phone requirements.</li>
<li class='mt-2 text-slate-700'>Look for PD and PPS support if your devices need it.</li>
<li class='mt-2 text-slate-700'>Check port layout so larger plugs don’t block neighbors.</li>
</ul>"""),
            ],
        },
        {
            "title": "Digital Meat Thermometers: What Reviewers Mention Most (Speed, Accuracy, Durability)",
            "description": "A neutral, review-informed guide to digital meat thermometers: response time, accuracy tips, and common pain points from buyers.",
            "category": "Kitchen",
            "amz_queries": [
                ("Digital meat thermometer", "digital meat thermometer"),
                ("Instant read thermometer", "instant read thermometer"),
                ("Meat thermometer for grilling", "meat thermometer for grilling"),
            ],
            "internal": [
                ("/kitchen-deals.html", "Kitchen hub"),
                ("/digital-meat-thermometer-under-25.html", "Digital meat thermometers under $25"),
                ("/digital-meat-thermometer-under-50.html", "Digital meat thermometers under $50"),
                ("/cast-iron-skillet-under-50.html", "Cast iron skillets under $50"),
            ],
            "sections": [
                ("What buyers like", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Fast read times that prevent overcooking.</li>
<li class='mt-2 text-slate-700'>Backlit screens for grilling at night.</li>
<li class='mt-2 text-slate-700'>Simple calibration guides and clear temp ranges.</li>
</ul>"""),
                ("Common complaints", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Inconsistent accuracy without occasional calibration.</li>
<li class='mt-2 text-slate-700'>Battery drain or loose battery doors.</li>
<li class='mt-2 text-slate-700'>Water resistance claims that don’t hold up to heavy washing.</li>
</ul>"""),
                ("Quick buying checklist", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Look for 3–5 second response time if you grill often.</li>
<li class='mt-2 text-slate-700'>Choose a model with a long probe for thicker cuts.</li>
<li class='mt-2 text-slate-700'>Keep a spare battery on hand.</li>
</ul>"""),
            ],
        },
        {
            "title": "Dash Cams: What Buyers Mention Most (Video Clarity, Night Vision, Heat, App)",
            "description": "A neutral, review-informed guide to dash cams based on common buyer feedback: video quality, night performance, heat tolerance, and app reliability.",
            "category": "Electronics",
            "amz_queries": [
                ("Dash cam deals", "dash cam"),
                ("Dual dash cam front and rear", "dual dash cam front and rear"),
                ("Dash cam with night vision", "dash cam with night vision"),
                ("Dash cam with wifi", "dash cam with wifi"),
            ],
            "internal": [
                ("/electronics-deals.html", "Electronics hub"),
                ("/dash-cam-under-100.html", "Dash cams under $100"),
                ("/micro-sd-card-under-25.html", "Micro SD cards under $25"),
                ("/electronics-under-100.html", "Electronics under $100"),
            ],
            "sections": [
                ("What buyers like", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Clear daytime footage and readable license plates at close range.</li>
<li class='mt-2 text-slate-700'>Compact designs that don’t block the windshield.</li>
<li class='mt-2 text-slate-700'>Easy pairing for downloading clips to a phone.</li>
</ul>"""),
                ("Common complaints", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Heat issues in hot climates causing shutdowns or battery swelling.</li>
<li class='mt-2 text-slate-700'>Night footage that looks grainy without good lighting.</li>
<li class='mt-2 text-slate-700'>Apps that are buggy or slow to transfer video.</li>
</ul>"""),
                ("Quick buying checklist", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Prefer capacitor-based models for better heat tolerance.</li>
<li class='mt-2 text-slate-700'>Check if you want front+rear coverage and the cable length for the rear cam.</li>
<li class='mt-2 text-slate-700'>Buy a reliable microSD card rated for continuous recording.</li>
</ul>"""),
            ],
        },
        {
            "title": "Air Purifiers Under $100: What Reviewers Say About Noise, Filters, and Room Size",
            "description": "A neutral summary of air purifier buyer feedback: noise levels, filter costs, and matching room size to your space.",
            "category": "Home",
            "amz_queries": [
                ("Air purifier under $100", "air purifier under 100"),
                ("HEPA air purifier", "hepa air purifier"),
                ("Air purifier for bedroom", "air purifier for bedroom"),
                ("Air purifier smoke", "air purifier smoke"),
            ],
            "internal": [
                ("/home-deals.html", "Home hub"),
                ("/air-purifier-under-100.html", "Air purifiers under $100"),
                ("/air-purifier-filter-under-25.html", "Air purifier filters under $25"),
                ("/home-air-purifier-under-100.html", "Home air purifiers under $100"),
            ],
            "sections": [
                ("What buyers like", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Noticeable reduction in odors and dust in small rooms.</li>
<li class='mt-2 text-slate-700'>Low-noise sleep modes for bedrooms.</li>
<li class='mt-2 text-slate-700'>Simple controls and filter-change indicators.</li>
</ul>"""),
                ("Common complaints", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Filter replacement costs that add up over time.</li>
<li class='mt-2 text-slate-700'>Overstated room-size claims for larger spaces.</li>
<li class='mt-2 text-slate-700'>Noticeable fan noise on higher speeds.</li>
</ul>"""),
                ("Simple checklist", """<ul class='list-disc pl-6'>
<li class='mt-2 text-slate-700'>Match coverage to your room size, not your whole home.</li>
<li class='mt-2 text-slate-700'>Check filter prices and how often replacements are needed.</li>
<li class='mt-2 text-slate-700'>If it’s for sleep, prioritize quiet modes under 30–35 dB.</li>
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
            f"<li class='mt-2'><a class='underline hover:text-slate-900' href='/{p.relative_to(ROOT).as_posix()}'>{html.escape(title)}</a></li>"
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
