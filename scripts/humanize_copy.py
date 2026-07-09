#!/usr/bin/env python3
"""Strip internal SEO-planning jargon from user-facing copy sitewide.

The page generators leaked keyword-strategy vocabulary ("high intent",
"Core query", "Hardwood intent.", "Budget ladder") into shopper-facing
text. This rewrites it into plain language a shopper actually understands.
Idempotent; safe to rerun after generating new pages.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Ordered: exact phrases first, generic patterns last.
EXACT = [
    # Section heading + explainer over the search-card grids
    (">High-intent searches<", ">Popular searches<"),
    (
        ">Click a query to see live prices. These are the searches buyers actually type.<",
        ">Every card below opens the matching results on Amazon, so you can check today's price and read real reviews before you buy.<",
    ),
    # H2 suffix leaked from keyword planning
    (" (high intent)</h2>", "</h2>"),
    (" (high intent)<", "<"),
    # Group labels
    (">Comparison intent<", ">Compare options<"),
    (">Deal intent<", ">Deal hunting<"),
    (">Sale intent<", ">On sale now<"),
    (">Purchase intent<", ">Ready to buy<"),
    (">Top picks intent<", ">Top picks<"),
    (">Feature-focused intent<", ">Shop by feature<"),
    (">Core seasonal intent<", ">Seasonal favorites<"),
    (">Bridge to evergreen intent<", ">Year-round picks<"),
    (">Budget ladder<", ">Shop by budget<"),
    # Card subtitles with fixed wording
    (">The core query.<", ">The most popular version of this search.<"),
    (">Comparison-style search.<", ">Compare several options at once.<"),
    (">Value-focused intent.<", ">Best bang for your buck.<"),
    (">Deal-focused intent.<", ">Discount hunting.<"),
    (">Affordability intent.<", ">Budget friendly.<"),
    # Hub-page marketing-speak
    (" (fast clicks)<", "<"),
    ("High-intent categories + cheap add-ons that convert well.", "The picks shoppers click most, plus easy add-ons."),
    ("Cheap add-on conversions.", "An easy, inexpensive add-on."),
    ("Cheap, evergreen purchases.", "Inexpensive and always useful."),
    ("Big demand + lots of comparison shopping.", "A favorite — lots of options to compare."),
    ("Comparison-heavy category.", "Worth comparing a few options."),
    ("Comparison-heavy, high-value category.", "Worth comparing a few options."),
    # One-off hand-written variants
    ("The core query—high volume and frequent discounts.", "The most popular version of this search — discounts are frequent."),
    ("The core query shoppers use.", "The most popular version of this search."),
    (">Core query; strong intent.<", ">The most popular version of this search.<"),
    (">Alternate phrasing that still signals high intent.<", ">Another common way shoppers phrase it.<"),
    (">Seasonal; strong purchase intent.<", ">A seasonal favorite.<"),
    (">Includes battery and charger—high buyer intent.<", ">Includes battery and charger.<"),
    (" — higher intent<", "<"),
    (">High-intent utility category.<", ">A practical everyday category.<"),
    (">High-intent upgrade query with lots of choices.<", ">A popular upgrade with lots of choices.<"),
    (">High-intent query: wants a complete usable kit.<", ">For shoppers who want a complete, usable kit.<"),
    (">High-intent phrase for low-maintenance mats.<", ">For low-maintenance mats.<"),
    (">High-intent phrase for at-home training.<", ">For at-home training.<"),
    ('content="High-intent home upgrades under $50', 'content="Smart home upgrades under $50'),
    (" convert well because they’re ", " are "),
    (" convert well because they solve ", " solve "),
    (" are cheap desk add-ons and convert well.", " are cheap desk add-ons."),
    (
        "these high-intent search shortcuts make it easy to compare options and pricing quickly",
        "these ready-made searches make it easy to compare options and prices quickly",
    ),
    (
        "high-intent picks that tend to convert because they solve everyday problems",
        "simple picks people love because they solve everyday problems",
    ),
    ("Low-cost add-on that converts", "A low-cost add-on worth grabbing"),
]

# Any leftover "<X> intent." card subtitle -> "Focused on <x>."
GENERIC_SUBTITLE = re.compile(r">([^<>]{2,60}?) intent\.<")
# Any leftover "<X> intent" label (no period) -> just the descriptor
GENERIC_LABEL = re.compile(r">([^<>]{2,60}?) intent<")
# "Focused on X." subtitles are keyword-differentiators restated -- the card
# title already carries that information, so drop the whole subtitle div.
FOCUSED_DIV = re.compile(r"""<div class=['"]text-sm text-slate-500 mt-1['"]>Focused on [^<]*</div>""")
# "These searches target buyers ..." reads like an ad brief; flip it into
# a direct question to the shopper.
TARGET_WANT = re.compile(r"These searches target buyers who want ([^.<]+)\.")
TARGET_TRYING = re.compile(r"These searches target buyers trying to ([^.<]+)\.")


def lower_first(s):
    return s if s[:1].isupper() and s[1:2].isupper() else s[0].lower() + s[1:]


def humanize(html):
    for old, new in EXACT:
        html = html.replace(old, new)
    html = GENERIC_SUBTITLE.sub(lambda m: f">Focused on {lower_first(m.group(1))}.<", html)
    html = GENERIC_LABEL.sub(lambda m: f">{m.group(1)}<", html)
    html = FOCUSED_DIV.sub("", html)
    html = TARGET_WANT.sub(r"Want \1? Start with one of these searches.", html)
    html = TARGET_TRYING.sub(r"Trying to \1? These searches are a good place to start.", html)
    # Body-copy stragglers
    html = html.replace("high-intent searches", "popular searches")
    html = html.replace("high-intent variations", "specific versions")
    html = html.replace("highest-intent variations people actually buy", "specific versions people actually buy")
    html = html.replace(">Open a query → compare live prices.<", ">Tap any search below to compare live prices.<")
    html = html.replace(">More long-tail lists<", ">More pages like this<")
    html = html.replace("These long-tail searches help you compare", "These specific searches help you compare")
    html = html.replace(
        "This is one of the biggest electronics long-tail pools. Under $50 is where most “deal” shoppers live.",
        "Under $50 is where most deal shoppers land — there are tons of options here.",
    )
    html = html.replace(
        "People buy in sets, and replacements happen often—great long-tail traffic.",
        "People buy in sets, and replacements happen often.",
    )
    # Hand-written hero/meta sentences that leaked strategy language
    html = html.replace("high-intent school and work purchase", "school and work staple")
    html = html.replace("a high-intent category with frequent deal hunting", "a category with frequent real discounts")
    html = html.replace("Browse high-intent under-$", "Browse under-$")
    html = html.replace("Trash cans are surprisingly high-intent.", "Trash cans are a surprisingly considered purchase.")
    html = html.replace("Smart locks are high-intent security upgrades.", "Smart locks are a serious security upgrade.")
    html = html.replace("Toaster ovens are a high-intent kitchen upgrade.", "Toaster ovens are a popular kitchen upgrade.")
    html = html.replace(
        "Kids scooters are a high-intent gift and outdoor play category.",
        "Kids scooters are a favorite gift and outdoor play pick.",
    )
    html = html.replace(
        "Dehumidifiers are a high-intent home improvement buy.",
        "Dehumidifiers are a practical home improvement buy.",
    )
    html = html.replace("A focused list of high-intent categories.", "A focused list of popular categories.")
    html = html.replace(
        "These searches capture high-intent buyers under $25.",
        "These searches cover the most popular picks under $25.",
    )
    # Catch-all: any remaining strategy adjective reads fine as "popular"
    html = html.replace("high-intent", "popular").replace("High-intent", "Popular")
    html = html.replace("Black Friday is when buyer intent spikes.", "Black Friday is when everyone's hunting for deals.")
    html = html.replace("Cyber Monday is when buyer intent spikes.", "Cyber Monday is when everyone's hunting for deals.")
    html = html.replace("Christmas is when buyer intent spikes.", "Christmas is when everyone's shopping at once.")
    html = html.replace("categories with year-round buying intent", "categories people shop year-round")
    for old, new in LATE_EXACT:
        html = html.replace(old, new)
    # "size intents under $100" / "buyer intents: portability" etc.
    html = html.replace(" intents", " needs")
    html = html.replace("These queries", "These searches")
    return html


LATE_EXACT = [
    # Long hand-written hero sentences
    (
        "A wireless mouse is a small, easy conversion product—people buy it when they’re already shopping. These searches cover silent-click, ergonomic, and laptop-friendly intent.",
        "A wireless mouse is a small, easy upgrade. These searches cover silent-click, ergonomic, and laptop-friendly options.",
    ),
    ("A review-style page for home gadgets that maps buyer intent to practical categories.",
     "A review-style page that organizes home gadgets into practical categories."),
    ("Air fryers are one of the highest-intent kitchen searches.",
     "Air fryers are one of the most-searched kitchen upgrades."),
    ("so we link the common intent queries.", "so we link the most common searches."),
    ("These queries are pure intent.", "These searches get straight to the point."),
    ("These queries capture that intent.", "These searches capture exactly that."),
    ("Router buyers are in pain (slow internet). That’s high intent.",
     "Slow internet is painful — most people want a fix today."),
    ("Safety products are high intent and low hesitation.",
     "Safety products are bought quickly and confidently."),
    ("Space heaters have strong seasonal demand and high buyer intent.",
     "Space heaters are in high demand every winter."),
    ("Heated blankets have strong seasonal demand and high buyer intent.",
     "Heated blankets are in high demand every winter."),
    ("We prioritize categories with clear buyer intent and real replacement cycles.",
     "We prioritize things people actually shop for and replace regularly."),
    ("Under $100 is the highest-intent bracket for upgrades.",
     "Under $100 is the sweet spot for upgrades."),
    ("These searches capture high purchase intent.",
     "These searches get you to ready-to-buy options."),
    ("these buyer-intent searches make it easy",
     "these ready-made searches make it easy"),
    # Short card subtitles
    (">A common intent phrase for targeted use cases.<", ">A common way to search for specific needs.<"),
    (">A frequent parent intent query.<", ">A search parents use often.<"),
    (">A popular intent phrase used by many parents.<", ">A search parents use often.<"),
    (">Age-specific intent tends to convert well.<", ">Filtering by age helps you find the right fit.<"),
    (">Another common intent phrase.<", ">Another common way to search it.<"),
    (">Attachment-specific intent for curly hair routines.<", ">For curly hair routines.<"),
    (">Budget intent; huge demand.<", ">The budget favorite.<"),
    (">Common intent phrase when starting out.<", ">A common search when starting out.<"),
    (">Common intent phrase—check ingredient lists.<", ">A common search — check ingredient lists.<"),
    (">Comparison intent that often precedes purchase.<", ">Good for comparing before you buy.<"),
    (">Dorm intent can be very specific.<", ">Dorm needs can be very specific.<"),
    (">Evergreen intent for bedrooms and nurseries.<", ">A year-round favorite for bedrooms and nurseries.<"),
    (">Feature intent (some results will be “noise reducing”).<", ">Some results will be “noise reducing.”<"),
    (">Feature-driven intent for lounging spots.<", ">For cozy lounging spots.<"),
    (">High intent and broad demand.<", ">A popular, broad search.<"),
    (">High intent for easy installation.<", ">For easy installation.<"),
    (">High intent; durability preference.<", ">For shoppers who want durability.<"),
    (">High intent; lots of deal shopping.<", ">Discounts are common here.<"),
    (">High intent; often a replacement buy.<", ">Often a replacement buy.<"),
    (">High intent—compare review patterns and sizes.<", ">Compare reviews and sizes.<"),
    (">Higher-intent appliance shopping.<", ">Serious appliance shopping.<"),
    (">Higher-intent browse.<", ">A more specific browse.<"),
    (">Higher-intent comparisons.<", ">Side-by-side comparisons.<"),
    (">Higher-intent picks<", ">More specific picks<"),
    (">Higher-intent shoppers.<", ">For shoppers who know what they want.<"),
    (">Same intent for Android users.<", ">The same search for Android users.<"),
    (">School intent is high and repeatable.<", ">A back-to-school staple.<"),
    (">Similar intent; big volume.<", ">A similar, very popular search.<"),
    (">Size-specific intent for crates and kennels.<", ">Get the size right for crates and kennels.<"),
    (">Small-space intent is common for home gyms.<", ">Small-space setups are common for home gyms.<"),
    (">Specific intent for rehab-style use.<", ">For rehab-style use.<"),
    (">Specific intent query.<", ">A very specific search.<"),
    (">Strong intent + specific sizing.<", ">Be sure to check sizing.<"),
    (">Top 5 today: highest-intent quick links.<", ">Top 5 today: quick links.<"),
    (">Travel intent modifier.<", ">The travel version.<"),
    (">Use-case intent for runners and lifters.<", ">For runners and lifters.<"),
    (">Very common intent phrase.<", ">A very common search.<"),
    (">Very high purchase intent search.<", ">A common search when you're ready to buy.<"),
    (">Very strong intent query.<", ">A very specific search.<"),
    (">“Best” intent tends to be high-converting.<", ">Adding “best” surfaces top-rated options.<"),
    ("Steam mops are a problem/solution home-cleaning buy.", "A steam mop solves a real cleaning headache."),
    ("Leak detectors are a strong problem/solution buy", "Leak detectors solve a real worry"),
    ("Mesh Wi‑Fi is a problem/solution purchase", "Mesh Wi‑Fi fixes a real everyday frustration"),
]


def main():
    changed = 0
    for pattern in ("*.html", "blog/*.html"):
        for path in sorted(ROOT.glob(pattern)):
            html = path.read_text(encoding="utf-8")
            new = humanize(html)
            if new != html:
                path.write_text(new, encoding="utf-8")
                changed += 1
    print(f"humanized {changed} pages")


if __name__ == "__main__":
    main()
