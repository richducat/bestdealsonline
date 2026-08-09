#!/usr/bin/env python3
"""Generate SEO growth pages for methodology, trust, and ready-to-buy queries."""

from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://bestdealsonline.us"
TODAY = date.today().isoformat()

NAV = """
      <nav class=\"hidden md:flex flex-wrap gap-4 text-sm text-slate-200\">
        <a class=\"hover:text-yellow-400\" href=\"/best-deals-online-today.html\">Today</a>
        <a class=\"hover:text-yellow-400\" href=\"/best-deals-online.html\">Best Deals</a>
        <a class=\"hover:text-yellow-400\" href=\"/electronics-deals.html\">Electronics</a>
        <a class=\"hover:text-yellow-400\" href=\"/home-deals.html\">Home</a>
        <a class=\"hover:text-yellow-400\" href=\"/fitness-deals.html\">Fitness</a>
        <a class=\"hover:text-yellow-400\" href=\"/blog/index.html\">Blog</a>
      </nav>
""".strip()

FOOTER = """
<footer class='border-t border-slate-200'>
  <div class='max-w-5xl mx-auto px-4 py-8 text-sm text-slate-500'>
    <div class='flex flex-col gap-3'>
      <div>
        <strong>Affiliate disclosure:</strong> We may earn a commission when you buy through links on this site, at no extra cost to you.
        <span class='ml-2'><a class='underline inline-flex items-center min-h-10 px-1 hover:text-slate-900' href='/affiliate-disclosure.html'>Details</a></span>
      </div>
      <div class='flex flex-wrap gap-x-4 gap-y-2'>
        <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/best-deals-online-today.html'>Today</a>
        <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/online-deals-methodology.html'>Methodology</a>
        <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/best-deals-legit-or-scam.html'>Buyer beware</a>
        <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/review-aggregation-guidelines.html'>Review policy</a>
        <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/about-best-online-deals.html'>About</a>
        <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/contact-best-online-deals.html'>Contact</a>
        <a class='inline-flex items-center min-h-10 px-2 rounded-md hover:text-slate-900 hover:bg-slate-100' href='/privacy.html'>Privacy</a>
      </div>
    </div>
  </div>
</footer>
""".strip()


def card(href: str, title: str, desc: str) -> str:
    return (
        "<a class='bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md p-5 flex items-start justify-between gap-4'"
        f" href='{escape(href, quote=True)}'>"
        f"<div><div class='font-bold text-slate-900'>{escape(title)}</div>"
        f"<div class='text-sm text-slate-500 mt-1'>{escape(desc)}</div></div>"
        "<span class='text-slate-400' aria-hidden='true'>→</span></a>"
    )


def section_html(section: dict) -> str:
    heading = escape(section["heading"])
    paragraphs = "".join(f"<p class='text-slate-700 mt-3'>{escape(p)}</p>" for p in section.get("paragraphs", []))
    bullets = section.get("bullets", [])
    bullet_html = ""
    if bullets:
        bullet_html = "<ul class='list-disc pl-6 mt-3 space-y-2 text-slate-700'>" + "".join(
            f"<li>{escape(item)}</li>" for item in bullets
        ) + "</ul>"
    return (
        "<section class='bg-white rounded-2xl border border-slate-200 shadow-sm p-6 mt-6'>"
        f"<h2 class='text-2xl font-extrabold'>{heading}</h2>{paragraphs}{bullet_html}</section>"
    )


def faq_section(faqs: list[tuple[str, str]]) -> str:
    items = []
    for q, a in faqs:
        items.append(
            "<div>"
            f"<h3 class='font-bold text-slate-900'>{escape(q)}</h3>"
            f"<p class='text-slate-700 mt-1'>{escape(a)}</p>"
            "</div>"
        )
    return (
        "<section class='bg-white rounded-2xl border border-slate-200 shadow-sm p-6 mt-6'>"
        "<h2 class='text-2xl font-extrabold'>FAQ</h2>"
        "<div class='space-y-4 mt-4'>"
        + "".join(items)
        + "</div></section>"
    )


def faq_schema(faqs: list[tuple[str, str]]) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faqs
        ],
    }
    body = json.dumps(payload, indent=2)
    return (
        "      <script type=\"application/ld+json\">\n"
        + "\n".join(f"      {line}" for line in body.splitlines())
        + "\n      </script>"
    )


def item_list_schema(name: str, items: list[tuple[str, str]]) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "numberOfItems": len(items),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx,
                "name": item_name,
                "url": f"{SITE}{item_url}",
            }
            for idx, (item_name, item_url) in enumerate(items, start=1)
        ],
    }
    body = json.dumps(payload, indent=2)
    return (
        "      <script type=\"application/ld+json\">\n"
        + "\n".join(f"      {line}" for line in body.splitlines())
        + "\n      </script>"
    )


def page_html(spec: dict) -> str:
    canonical = f"{SITE}/{spec['slug']}"
    links = "".join(card(*entry) for entry in spec.get("links", []))
    sections = "".join(section_html(sec) for sec in spec.get("sections", []))

    faq_block = ""
    faq_jsonld = ""
    if spec.get("faqs"):
        faq_block = faq_section(spec["faqs"])
        faq_jsonld = "\n" + faq_schema(spec["faqs"])

    item_list_jsonld = ""
    if spec.get("item_list"):
        item_list_jsonld = "\n" + item_list_schema(spec["item_list"]["name"], spec["item_list"]["items"])

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no\" />
  <title>{escape(spec['title'])} | BestDealsOnline</title>
  <meta name=\"description\" content=\"{escape(spec['description'])}\" />
  <link rel=\"canonical\" href=\"{canonical}\" />

  <meta property=\"og:title\" content=\"{escape(spec['title'])} | BestDealsOnline\" />
  <meta property=\"og:description\" content=\"{escape(spec['description'])}\" />
  <meta property=\"og:type\" content=\"website\" />
  <meta property=\"og:url\" content=\"{canonical}\" />
  <meta property=\"og:image\" content=\"{SITE}/assets/og-default.svg\" />
  <meta name=\"twitter:card\" content=\"summary_large_image\" />
  <meta name=\"twitter:image\" content=\"{SITE}/assets/og-default.svg\" />

  <link rel=\"icon\" href=\"/assets/favicon.svg\" type=\"image/svg+xml\" />

  <script src=\"https://cdn.tailwindcss.com\"></script>
  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap\" rel=\"stylesheet\"> 
  <style>:root{{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}</style>

  <!-- Google tag (gtag.js) -->
  <script async src=\"https://www.googletagmanager.com/gtag/js?id=G-6GD5DK8067\"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-6GD5DK8067', (function(){{try{{var A=/HeadlessChrome|Electron|Claude|PhantomJS|Puppeteer|Playwright|Selenium|Cypress|Lighthouse|GTmetrix|crawler|spider|bot/i;try{{if(navigator.webdriver===true||A.test(navigator.userAgent||'')){{return {{traffic_type:'internal'}};}}}}catch(e){{}}var K='bdo.internalTraffic';var q=new URLSearchParams(location.search).get('internal');if(q==='1'||q==='true'){{localStorage.setItem(K,'1');}}else if(q==='0'||q==='false'){{localStorage.removeItem(K);}}return localStorage.getItem(K)==='1'?{{traffic_type:'internal'}}:{{}};}}catch(e){{return {{}};}}}})());
  </script>
  <script defer src=\"/assets/track.js\"></script>{faq_jsonld}{item_list_jsonld}
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
      {NAV}
    </div>
  </header>

  <section class=\"bg-gradient-to-br from-indigo-900 via-blue-900 to-slate-900\">
    <div class=\"container mx-auto px-4 py-10 md:py-14\">
      <div class=\"max-w-4xl\">
        <p class=\"inline-flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/40 text-yellow-300 text-xs font-bold px-3 py-1 rounded-full mb-5\">{escape(spec['badge'])}</p>
        <h1 class=\"text-3xl md:text-5xl font-extrabold tracking-tight\">{escape(spec['title'])}</h1>
        <p class=\"text-blue-100 text-base md:text-lg mt-4 max-w-2xl\">{escape(spec['intro'])}</p>
      </div>
    </div>
  </section>

  <main class=\"bg-slate-50 text-slate-900\">
    <div class=\"container mx-auto px-4 py-10\">
      <section class=\"bg-white rounded-2xl border border-slate-200 shadow-sm p-6\">
        <h2 class=\"text-2xl font-extrabold\">Start browsing</h2>
        <p class=\"text-slate-600 mt-2\">Internal pages to compare deals quickly and stay on trusted listings.</p>
        <div class=\"grid grid-cols-1 md:grid-cols-2 gap-4 mt-6\">{links}</div>
      </section>
      {sections}
      {faq_block}
      <div class=\"mt-6 text-sm text-slate-500\">Last updated: {TODAY}</div>
    </div>

    {FOOTER}
  </main>
</body>
</html>
"""


PAGES = [
    {
        "slug": "online-deals-methodology.html",
        "title": "Online Deals Methodology",
        "description": "How BestDealsOnline evaluates deal pages, trust signals, and buyer intent before recommending links.",
        "badge": "Methodology • transparent process",
        "intro": "This page explains how we pick deals, what we exclude, and how we keep roundup pages updated.",
        "links": [
            ("/best-deals-online-today.html", "Best online deals today", "Daily shortlist and live pricing links."),
            ("/deal-roundup-today.html", "Deal roundup today", "A focused list of high-intent categories."),
            ("/best-deals-with-price-history.html", "Best deals with price history", "How to validate value over time."),
            ("/best-deals-legit-or-scam.html", "Best deals legit or scam", "Fraud checks before you buy."),
        ],
        "sections": [
            {
                "heading": "How we pick deals",
                "bullets": [
                    "We prioritize categories with clear buyer intent and real replacement cycles.",
                    "We favor pages with current pricing links and complete comparison context.",
                    "We remove pages that feel outdated, thin, or hard to verify.",
                ],
            },
            {
                "heading": "What we do not do",
                "bullets": [
                    "We do not claim direct hands-on testing for every product page.",
                    "We do not publish unverified coupon claims or fake countdown urgency.",
                    "We do not hide affiliate disclosure or trust policy links.",
                ],
            },
        ],
        "faqs": [
            ("How often is this methodology reviewed?", "We review and update this process weekly and whenever major category coverage changes."),
            ("Do you guarantee the lowest price?", "No. We provide curated starting points and recommend checking price history before buying."),
            ("How do you keep trust high?", "We use transparent disclosure, policy links, and clearly dated updates on key pages."),
        ],
    },
    {
        "slug": "best-deals-legit-or-scam.html",
        "title": "Best Deals Legit or Scam",
        "description": "Buyer-beware guide for spotting scam listings, fake reviews, and suspicious price claims when shopping online deals.",
        "badge": "Buyer beware • scam checks",
        "intro": "Use this checklist to filter risky listings before you click buy.",
        "links": [
            ("/best-deals-with-price-history.html", "Best deals with price history", "Use historical pricing to avoid fake markdowns."),
            ("/discount-codes-vs-deals.html", "Discount codes vs deals", "Learn when coupon language is misleading."),
            ("/top-deals-sites-comparison.html", "Top deals sites comparison", "Compare trust signals by site type."),
            ("/review-aggregation-guidelines.html", "Review aggregation guidelines", "How we summarize review themes."),
        ],
        "sections": [
            {
                "heading": "Red flags to watch",
                "bullets": [
                    "Unrealistic discounts with no price history context.",
                    "Review spikes that cluster in a short time window.",
                    "Vague listings with missing specs, warranty, or return details.",
                    "Seller pages that changed name repeatedly or have limited history.",
                ],
            },
            {
                "heading": "Quick legitimacy checklist",
                "bullets": [
                    "Check seller history and recent review language quality.",
                    "Compare price trend against multiple sources.",
                    "Read low-star reviews first for recurring failure patterns.",
                ],
            },
        ],
        "faqs": [
            ("What is the fastest scam check?", "Compare current price to recent average and inspect low-star reviews for repeated complaints."),
            ("Are all low prices suspicious?", "No. Seasonal promotions can be valid, but they should still make sense against recent price history."),
        ],
    },
    {
        "slug": "review-aggregation-guidelines.html",
        "title": "Review Aggregation Guidelines",
        "description": "Editorial policy for summarizing reviews, assigning trust signals, and updating timestamps on BestDealsOnline pages.",
        "badge": "Editorial standards",
        "intro": "These rules explain how we aggregate public feedback without copying source reviews.",
        "links": [
            ("/online-deals-methodology.html", "Online deals methodology", "Full selection and update process."),
            ("/affiliate-disclosure.html", "Affiliate disclosure", "How commissions work on this site."),
            ("/privacy.html", "Privacy policy", "Data and tracking expectations."),
            ("/contact-best-online-deals.html", "Contact", "Report corrections or policy concerns."),
        ],
        "sections": [
            {
                "heading": "Aggregation rules",
                "bullets": [
                    "Summarize recurring themes rather than copying individual reviews.",
                    "Separate objective specs from subjective buyer sentiment.",
                    "Flag uncertainty when evidence is mixed or low volume.",
                ],
            },
            {
                "heading": "Trust signals we publish",
                "bullets": [
                    "Visible affiliate disclosure and policy links.",
                    "Page-level updated timestamps for major guides.",
                    "Clear category ownership and internal cross-links.",
                ],
            },
        ],
    },
    {
        "slug": "deal-roundup-today.html",
        "title": "Deal Roundup Today",
        "description": "Today’s deal roundup across electronics, home, fitness, and smart home categories with fast internal links.",
        "badge": "Daily roundup",
        "intro": "A quick daily deal roundup to jump into high-intent categories.",
        "links": [
            ("/dash-cam-under-100.html", "Dash cams under $100", "Popular problem-solution purchase intent."),
            ("/router-mesh-under-100.html", "Mesh Wi-Fi under $100", "Home network upgrade picks."),
            ("/security-camera-under-50.html", "Security cameras under $50", "Entry-level home security deals."),
            ("/adjustable-dumbbells-under-100.html", "Adjustable dumbbells under $100", "High-demand fitness category."),
        ],
        "sections": [
            {
                "heading": "How to use this page",
                "bullets": [
                    "Start with one category where you have an immediate buying need.",
                    "Compare 2-3 linked pages before checking out.",
                    "Validate recent pricing before treating a deal as urgent.",
                ],
            },
        ],
        "item_list": {
            "name": "Deal Roundup Today Top Picks",
            "items": [
                ("Dash cams under $100", "/dash-cam-under-100.html"),
                ("Mesh Wi-Fi under $100", "/router-mesh-under-100.html"),
                ("Security cameras under $50", "/security-camera-under-50.html"),
                ("Adjustable dumbbells under $100", "/adjustable-dumbbells-under-100.html"),
            ],
        },
    },
    {
        "slug": "weekly-deal-roundup.html",
        "title": "Weekly Deal Roundup",
        "description": "Weekly deal roundup for evergreen categories: electronics, home security, tools, and kitchen upgrades.",
        "badge": "Weekly roundup",
        "intro": "Use this weekly roundup for broader category planning and evergreen buys.",
        "links": [
            ("/electronics-deals.html", "Best deals on electronics", "Chargers, audio, networking, and accessories."),
            ("/home-deals.html", "Home deals", "Cleaning, comfort, and organization pages."),
            ("/tools-deals.html", "Best deals for tools", "DIY and maintenance essentials."),
            ("/kitchen-deals.html", "Kitchen deals", "Daily-use appliances and cookware."),
        ],
        "sections": [
            {
                "heading": "Weekly cadence",
                "paragraphs": [
                    "Roundups are refreshed weekly with a focus on stable categories that keep converting outside holiday events.",
                ],
            },
        ],
    },
    {
        "slug": "evergreen-deal-guides.html",
        "title": "Evergreen Deal Guides",
        "description": "Evergreen deal guides for categories with year-round buying intent, from phones and laptops to smart home and fitness.",
        "badge": "Evergreen guides",
        "intro": "These guides stay useful year-round and are updated when buying behavior shifts.",
        "links": [
            ("/best-deals-for-phones.html", "Best deals for phones", "Accessories and upgrade-friendly phone bundles."),
            ("/best-deals-for-laptops.html", "Best deals for laptops", "Work, school, and creator-focused picks."),
            ("/best-deals-for-smart-home.html", "Best deals for smart home", "Automation starters and add-ons."),
            ("/best-deals-for-home-security.html", "Best deals for home security", "Security cameras, doorbells, and sensors."),
        ],
        "sections": [
            {
                "heading": "Why evergreen matters",
                "paragraphs": [
                    "Evergreen pages capture buyer demand between seasonal peaks and help maintain ranking stability over time.",
                ],
            },
        ],
    },
    {
        "slug": "best-daily-deals-site.html",
        "title": "Best Daily Deals Site",
        "description": "A practical guide to using BestDealsOnline as a best daily deals site with category shortcuts and trust checks.",
        "badge": "Daily deals workflow",
        "intro": "Use this page to build a repeatable daily deal-check routine.",
        "links": [
            ("/best-deals-online-today.html", "Best online deals today", "Daily shortlist page."),
            ("/deal-roundup-today.html", "Deal roundup today", "Curated top categories."),
            ("/best-cheap-deals.html", "Best cheap deals", "Lower-ticket high-intent pages."),
            ("/best-online-deals-newsletter.html", "Best online deals newsletter", "Daily recap format."),
        ],
        "sections": [
            {
                "heading": "Daily process",
                "bullets": [
                    "Check today page first, then one category hub, then one under-$ page.",
                    "Save product targets so you can compare future pricing quickly.",
                    "Skip listings that fail basic scam and policy checks.",
                ],
            },
        ],
    },
    {
        "slug": "best-cheap-deals.html",
        "title": "Best Cheap Deals",
        "description": "Best cheap deals across under-$25 and under-$50 categories with strong purchase intent and frequent restocks.",
        "badge": "Budget picks",
        "intro": "Fast links for shoppers looking for best cheap deals without low-trust clutter.",
        "links": [
            ("/electronics-under-50.html", "Electronics under $50", "Chargers, audio, and desk upgrades."),
            ("/home-under-50.html", "Home under $50", "Daily-use home improvements."),
            ("/kitchen-under-50.html", "Kitchen under $50", "Small appliances and accessories."),
            ("/resistance-bands-under-25.html", "Fitness under $25", "High-value starter gear."),
        ],
        "sections": [
            {
                "heading": "Cheap deal filters",
                "bullets": [
                    "Prioritize proven categories with replacement demand.",
                    "Avoid products with thin warranty or weak seller history.",
                    "Check whether add-on items inflate total order cost.",
                ],
            },
        ],
    },
    {
        "slug": "best-deals-review-site.html",
        "title": "Best Deals Review Site",
        "description": "How BestDealsOnline works as a best deals review site by combining deal links, review summaries, and trust signals.",
        "badge": "Review-style coverage",
        "intro": "Our review-style pages summarize what buyers mention most and link directly to relevant deal pages.",
        "links": [
            ("/electronics-deals-reviews.html", "Electronics deals reviews", "Review-style summaries by category."),
            ("/home-gadget-deals.html", "Home gadget deals", "Home-focused review and deal pages."),
            ("/fitness-deal-tracker.html", "Fitness deal tracker", "Category page with weekly update flow."),
            ("/blog/index.html", "Blog guides", "Category explainers and buyer patterns."),
        ],
        "sections": [
            {
                "heading": "Review-style structure",
                "bullets": [
                    "Recurring buyer positives and complaints.",
                    "Common red flags and return reasons.",
                    "Internal links to live deal pages with current pricing.",
                ],
            },
        ],
    },
    {
        "slug": "top-deals-sites-comparison.html",
        "title": "Top Deals Sites Comparison",
        "description": "Top deals sites comparison framework: trust signals, pricing transparency, update frequency, and category depth.",
        "badge": "Comparison framework",
        "intro": "Use this checklist when comparing any deal site before relying on its recommendations.",
        "links": [
            ("/online-deals-methodology.html", "Online deals methodology", "Transparent selection criteria."),
            ("/best-deals-legit-or-scam.html", "Best deals legit or scam", "Scam detection checklist."),
            ("/review-aggregation-guidelines.html", "Review aggregation guidelines", "How review themes are summarized."),
            ("/best-deals-with-price-history.html", "Best deals with price history", "Historical validation workflow."),
        ],
        "sections": [
            {
                "heading": "Comparison criteria",
                "bullets": [
                    "Disclosure clarity and policy visibility.",
                    "Frequency of updates and stale-page cleanup.",
                    "Evidence-backed recommendations vs generic lists.",
                ],
            },
        ],
    },
    {
        "slug": "discount-codes-vs-deals.html",
        "title": "Discount Codes vs Deals",
        "description": "Discount codes vs deals: when coupons help, when direct pricing is better, and how to avoid fake savings signals.",
        "badge": "Coupon clarity",
        "intro": "Coupon language can hide weak pricing. This page helps you compare true savings.",
        "links": [
            ("/best-cheap-deals.html", "Best cheap deals", "Low-ticket categories with clearer pricing."),
            ("/best-deals-with-price-history.html", "Best deals with price history", "Validate true discount depth."),
            ("/best-deals-legit-or-scam.html", "Best deals legit or scam", "Fraud and manipulation checks."),
            ("/deal-roundup-today.html", "Deal roundup today", "Daily quick links with less coupon noise."),
        ],
        "sections": [
            {
                "heading": "When coupons win",
                "bullets": [
                    "Known brands with reliable list pricing and transparent code terms.",
                    "Stackable promotions where final cart price is clearly visible.",
                ],
            },
            {
                "heading": "When direct deals win",
                "bullets": [
                    "Commodity accessories where baseline pricing is already competitive.",
                    "Categories where fake MSRP is frequently used to inflate savings claims.",
                ],
            },
        ],
    },
    {
        "slug": "best-online-deals-newsletter.html",
        "title": "Best Online Deals Newsletter",
        "description": "Best online deals newsletter format with daily, weekly, and category-specific roundup sections you can follow quickly.",
        "badge": "Newsletter format",
        "intro": "This page mirrors the newsletter structure we use for daily and weekly deal highlights.",
        "links": [
            ("/best-deals-online-today.html", "Best online deals today", "Daily lead section."),
            ("/weekly-deal-roundup.html", "Weekly deal roundup", "Weekly recap section."),
            ("/electronics-deals.html", "Electronics deals", "High-demand category module."),
            ("/home-deals.html", "Home deals", "Evergreen home module."),
        ],
        "sections": [
            {
                "heading": "Newsletter sections",
                "bullets": [
                    "Top 5 today: highest-intent quick links.",
                    "Weekly trend: categories gaining buying momentum.",
                    "Buyer beware note: one scam pattern to avoid each issue.",
                ],
            },
        ],
    },
    {
        "slug": "home-gadget-deals.html",
        "title": "Home Gadget Deals",
        "description": "Home gadget deals guide covering cleaning, comfort, automation, and practical upgrades with internal comparison links.",
        "badge": "Home gadget review page",
        "intro": "A review-style page for home gadgets that maps buyer intent to practical categories.",
        "links": [
            ("/home-deals.html", "Home deals hub", "Main category for comfort and cleaning."),
            ("/best-deals-for-smart-home.html", "Best deals for smart home", "Automation-first gadget picks."),
            ("/best-deals-for-home-security.html", "Best deals for home security", "Cameras, sensors, and alerts."),
            ("/best-deals-with-price-history.html", "Best deals with price history", "Avoid fake markdowns."),
        ],
        "sections": [
            {
                "heading": "Top home gadget clusters",
                "bullets": [
                    "Cleaning upgrades: vacuums, steam mops, and leak sensors.",
                    "Comfort upgrades: humidifiers, air quality, and bedding add-ons.",
                    "Automation starters: smart plugs, bulbs, and routines.",
                ],
            },
        ],
    },
    {
        "slug": "fitness-deal-tracker.html",
        "title": "Fitness Deal Tracker",
        "description": "Fitness deal tracker page for weekly checks on dumbbells, bands, mats, and recovery tools.",
        "badge": "Category tracker",
        "intro": "Track recurring fitness categories with strong demand and predictable promotions.",
        "links": [
            ("/fitness-deals.html", "Fitness deals hub", "Main category page."),
            ("/adjustable-dumbbells-under-100.html", "Best deals for dumbbells", "Core strength category."),
            ("/resistance-bands-under-25.html", "Resistance bands under $25", "Budget accessory class."),
            ("/massage-gun-under-100.html", "Massage guns under $100", "Recovery-focused deals."),
        ],
        "sections": [
            {
                "heading": "Tracker workflow",
                "bullets": [
                    "Monitor weekly price movement in 4-6 core products per category.",
                    "Tag outlier drops that are likely to expire quickly.",
                    "Rotate featured links based on stock reliability and review quality.",
                ],
            },
        ],
    },
    {
        "slug": "electronics-deals-reviews.html",
        "title": "Electronics Deals Reviews",
        "description": "Review-style electronics deals page covering chargers, networking, audio, and accessories with buyer-intent links.",
        "badge": "Electronics review page",
        "intro": "Use this page for review-informed electronics categories that update quickly.",
        "links": [
            ("/electronics-deals.html", "Best deals on electronics", "Main electronics hub."),
            ("/best-deals-for-phones.html", "Best deals for phones", "Phone add-ons and charging pages."),
            ("/best-deals-for-laptops.html", "Best deals for laptops", "Laptop accessories and productivity gear."),
            ("/best-deals-for-smart-home.html", "Best deals for smart home", "Connected electronics for the home."),
        ],
        "sections": [
            {
                "heading": "Fast-moving electronics categories",
                "bullets": [
                    "Charging and power: USB-C, GaN, and batteries.",
                    "Connectivity: routers, mesh kits, and adapters.",
                    "Capture and audio: webcams, microphones, and speakers.",
                ],
            },
        ],
    },
    {
        "slug": "best-deals-with-price-history.html",
        "title": "Best Deals With Price History",
        "description": "How to find best deals with price history checks so discount claims are validated before purchase.",
        "badge": "Price validation",
        "intro": "A good deal is only good in context. Use historical pricing before checkout.",
        "links": [
            ("/deal-roundup-today.html", "Deal roundup today", "Daily list to validate with price history."),
            ("/weekly-deal-roundup.html", "Weekly deal roundup", "Broader set of categories to compare."),
            ("/best-deals-legit-or-scam.html", "Best deals legit or scam", "Fraud signals and seller checks."),
            ("/discount-codes-vs-deals.html", "Discount codes vs deals", "Separate real and artificial markdowns."),
        ],
        "sections": [
            {
                "heading": "Minimum price-history checks",
                "bullets": [
                    "Compare the current price to at least 30-day and 90-day trends.",
                    "Ignore percentage-off claims without a credible baseline.",
                    "Watch for bundle or accessory changes that hide true item pricing.",
                ],
            },
        ],
    },
    {
        "slug": "best-deals-for-phones.html",
        "title": "Best Deals for Phones",
        "description": "Best deals for phones focused on chargers, cables, mounts, protectors, and practical accessories.",
        "badge": "Phone accessories",
        "intro": "Phone deals are usually accessory-led. Focus on quality, compatibility, and verified pricing.",
        "links": [
            ("/usb-c-charger-under-50.html", "USB-C chargers under $50", "Fast charging essentials."),
            ("/wireless-charger-under-25.html", "Wireless chargers under $25", "Convenience picks."),
            ("/screen-protector-under-15.html", "Screen protectors under $15", "Low-ticket protection buys."),
            ("/phone-car-mount-under-20.html", "Phone car mounts under $20", "High-intent utility category."),
        ],
        "sections": [
            {
                "heading": "Phone deal priorities",
                "bullets": [
                    "Safety-certified charging gear first.",
                    "Compatibility across case and device size.",
                    "Review patterns around durability and heating.",
                ],
            },
        ],
    },
    {
        "slug": "best-deals-for-laptops.html",
        "title": "Best Deals for Laptops",
        "description": "Best deals for laptops including chargers, docks, stands, webcams, and productivity accessories.",
        "badge": "Laptop setup",
        "intro": "Laptop deal pages perform best when grouped by workflow: charging, ergonomics, and connectivity.",
        "links": [
            ("/usb-c-hub-under-50.html", "USB-C hubs under $50", "Connectivity expansion picks."),
            ("/laptop-stand-under-25.html", "Laptop stands under $25", "Ergonomic baseline upgrades."),
            ("/webcam-under-100.html", "Webcams under $100", "Meetings and streaming quality."),
            ("/wireless-keyboard-under-50.html", "Wireless keyboards under $50", "Desktop comfort setup."),
        ],
        "sections": [
            {
                "heading": "Laptop deal priorities",
                "bullets": [
                    "Device compatibility and port standards.",
                    "Thermal and power safety for chargers/docks.",
                    "Durability feedback from long-term user reviews.",
                ],
            },
        ],
    },
    {
        "slug": "best-deals-for-home-security.html",
        "title": "Best Deals for Home Security",
        "description": "Best deals for home security across cameras, doorbells, sensors, and alert devices.",
        "badge": "Home security",
        "intro": "Security categories convert when shoppers can compare reliability, app quality, and total cost quickly.",
        "links": [
            ("/security-camera-under-50.html", "Security cameras under $50", "Entry-level monitoring."),
            ("/video-doorbell-under-100.html", "Video doorbells under $100", "Doorstep visibility."),
            ("/water-leak-detector-under-50.html", "Water leak detectors under $50", "Early-warning protection."),
            ("/smart-lock-under-100.html", "Smart locks under $100", "Access control upgrades."),
        ],
        "sections": [
            {
                "heading": "Security deal checks",
                "bullets": [
                    "Subscription requirements and total ownership cost.",
                    "Notification speed and app stability.",
                    "Mounting and weather durability in low-star reviews.",
                ],
            },
        ],
    },
    {
        "slug": "best-deals-for-smart-home.html",
        "title": "Best Deals for Smart Home",
        "description": "Best deals for smart home basics including plugs, bulbs, speakers, sensors, and routines-friendly gadgets.",
        "badge": "Smart home",
        "intro": "Start with practical smart home categories that solve daily problems before buying larger systems.",
        "links": [
            ("/smart-plug-under-25.html", "Smart plugs under $25", "Low-risk entry point."),
            ("/smart-light-bulbs-under-25.html", "Smart bulbs under $25", "Simple automation starter."),
            ("/smart-speaker-under-50.html", "Smart speakers under $50", "Voice control hub devices."),
            ("/video-doorbell-under-100.html", "Video doorbells under $100", "Security + convenience overlap."),
        ],
        "sections": [
            {
                "heading": "Smart home bundle logic",
                "bullets": [
                    "Prioritize interoperability across ecosystems.",
                    "Avoid one-off gadgets without automation value.",
                    "Check update cadence and app reliability signals.",
                ],
            },
        ],
    },
    {
        "slug": "best-deals-subscription-box-offers.html",
        "title": "Best Deals Subscription Box Offers",
        "description": "Best deals subscription box offers checklist to evaluate recurring shipments, cancellation terms, and real savings.",
        "badge": "Subscription offers",
        "intro": "Subscription offers can be valuable, but only when renewal and cancellation terms are clear.",
        "links": [
            ("/discount-codes-vs-deals.html", "Discount codes vs deals", "Evaluate promo mechanics first."),
            ("/best-deals-with-price-history.html", "Best deals with price history", "Compare recurring vs one-time buys."),
            ("/top-deals-sites-comparison.html", "Top deals sites comparison", "Trust framework before subscribing."),
            ("/best-deals-legit-or-scam.html", "Best deals legit or scam", "Fraud prevention checklist."),
        ],
        "sections": [
            {
                "heading": "Subscription offer checks",
                "bullets": [
                    "Trial length, renewal date, and cancel path clarity.",
                    "Whether the first-box discount hides long-term overpricing.",
                    "Customer support responsiveness in recent reviews.",
                ],
            },
        ],
    },
    {
        "slug": "best-deals-for-tools.html",
        "title": "Best Deals for Tools",
        "description": "Best deals for tools across drills, tool sets, storage, and measurement gear with practical internal links.",
        "badge": "Tools",
        "intro": "Use this page to jump straight into high-intent tool categories with year-round demand.",
        "links": [
            ("/tools-deals.html", "Tools deals hub", "Main tools category page."),
            ("/cordless-drill-under-100.html", "Cordless drills under $100", "Core power tool category."),
            ("/tool-set-under-100.html", "Tool sets under $100", "Starter and replacement kits."),
            ("/socket-set-under-50.html", "Socket sets under $50", "DIY and garage essentials."),
        ],
        "sections": [
            {
                "heading": "Tool deal priorities",
                "bullets": [
                    "Reliability and warranty coverage over one-time discount size.",
                    "Category pages with clear use-case segmentation.",
                    "Accessory compatibility and battery ecosystem fit.",
                ],
            },
        ],
    },
    {
        "slug": "about-best-online-deals.html",
        "title": "About Best Online Deals",
        "description": "About BestDealsOnline: mission, editorial process, affiliate model, and how pages are updated.",
        "badge": "About",
        "intro": "BestDealsOnline is built to help shoppers find practical deals quickly with transparent disclosure.",
        "links": [
            ("/online-deals-methodology.html", "Online deals methodology", "How pages are selected and maintained."),
            ("/review-aggregation-guidelines.html", "Review aggregation guidelines", "How review themes are summarized."),
            ("/affiliate-disclosure.html", "Affiliate disclosure", "How commissions are earned."),
            ("/contact-best-online-deals.html", "Contact Best Online Deals", "Corrections and partnership requests."),
        ],
        "sections": [
            {
                "heading": "What we publish",
                "bullets": [
                    "Category hubs that route shoppers to high-intent deal pages.",
                    "Roundups and buyer-beware guides with transparent update dates.",
                    "Policy pages for disclosure, privacy, and review standards.",
                ],
            },
        ],
    },
    {
        "slug": "contact-best-online-deals.html",
        "title": "Contact Best Online Deals",
        "description": "Contact page for BestDealsOnline for correction requests, partnership questions, and editorial feedback.",
        "badge": "Contact",
        "intro": "Use this page for editorial corrections, trust concerns, or partnership inquiries.",
        "links": [
            ("/about-best-online-deals.html", "About Best Online Deals", "Mission and editorial model."),
            ("/online-deals-methodology.html", "Online deals methodology", "Selection and update criteria."),
            ("/review-aggregation-guidelines.html", "Review aggregation guidelines", "How we summarize feedback."),
            ("/privacy.html", "Privacy policy", "Data and usage expectations."),
        ],
        "sections": [
            {
                "heading": "How to contact us",
                "paragraphs": [
                    "For now, contact requests can be sent to contact@bestdealsonline.us with the page URL and issue details.",
                    "For correction requests, include supporting links so updates can be reviewed quickly.",
                ],
            },
        ],
    },
]


def main() -> None:
    written = 0
    for spec in PAGES:
        path = ROOT / spec["slug"]
        path.write_text(page_html(spec), encoding="utf-8")
        written += 1
    print(f"wrote={written}")


if __name__ == "__main__":
    main()
