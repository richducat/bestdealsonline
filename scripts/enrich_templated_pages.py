#!/usr/bin/env python3
"""Add genuine, differentiated buying guidance to templated price-tier and
seasonal/use-case pages (the "<seed>-under-<price>.html" and
"<seed>-{dorm,travel,small-apartment,black-friday-deals,christmas-deals,
cyber-monday-deals}.html" families).

These pages were generated from a shared template that only swaps a number
or a keyword through the title/meta/H1/links -- everything else is
byte-identical between siblings. That's a real "thin/duplicate content"
risk for search engines and falls short of Amazon Associates' requirement
for "additional original content" around search-result links.

This script inserts one new, non-templated content section per page with
genuinely different buying guidance depending on the price tier or
use-case, reusing the seed phrase already embedded in the page. It is
idempotent: a marker comment is checked before writing, so re-running is
safe and won't double-insert.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = "<!-- enrichment:v1 -->"
ANCHOR_RE = re.compile(r"<section[^>]*class=[\"'][^\"']*mt-12[^\"']*[\"'][^>]*>")

PRICE_RE = re.compile(r"^(?P<seed>.+)-under-(?P<price>\d+)$")
VARIANT_RE = re.compile(
    r"^(?P<seed>.+)-(?P<variant>dorm|travel|small-apartment|black-friday-deals|christmas-deals|cyber-monday-deals)$"
)

PRICE_BANDS = [
    (20, "budget", "What to expect under ${price}"),
    (40, "value", "Why ${price} is the sweet spot"),
    (75, "midrange", "What extra money buys you at ${price}"),
    (100, "uppermid", "Is ${price} worth it for {seed_plural}?"),
    (10**9, "premium", "Buying {seed_plural} at the premium tier"),
]

IRREGULAR_PLURALS = {
    "box": "boxes",
    "watch": "watches",
    "bench": "benches",
}


def pluralize(phrase: str) -> str:
    words = phrase.split(" ")
    last = words[-1]
    lower = last.lower()
    if lower.endswith("s"):
        plural = last
    elif lower in IRREGULAR_PLURALS:
        plural = IRREGULAR_PLURALS[lower]
    elif re.search(r"(ch|sh|x|z)$", lower):
        plural = last + "es"
    elif re.search(r"[^aeiou]y$", lower):
        plural = last[:-1] + "ies"
    else:
        plural = last + "s"
    words[-1] = plural
    return " ".join(words)

PRICE_COPY = {
    "budget": (
        "At this price, most {seed} listings are entry-level: fewer premium materials, simpler "
        "features, and a shorter (or no) extended warranty. That's fine if you want a low-risk "
        "first buy, a replacement for something that broke, or a gift the recipient may not use "
        "constantly. Skim the star-rating breakdown rather than just the average -- a 4.3 built "
        "on thousands of reviews is safer than a 4.6 built on twelve. Watch for zero-review, "
        "unbranded sellers; a slightly higher price from an established brand is often worth it "
        "at this tier."
    ),
    "value": (
        "This is typically where {seed} shopping shifts from \"cheapest option\" to \"best "
        "value\" -- established brands start showing up alongside no-names, and build quality "
        "improves noticeably without a premium markup. It's the range most reviewers land on for "
        "everyday use rather than occasional/backup use. Compare at least two listings before "
        "buying: look at what review complaints mention (not just the star average), and confirm "
        "the seller ships from or is fulfilled by Amazon."
    ),
    "midrange": (
        "Stepping up to this range usually buys better materials, extra features, and stronger "
        "warranty coverage than the budget tier. It's worth the jump if you'll use {seed_plural} often, "
        "since the added durability pays for itself over repeated use rather than a one-off "
        "purchase. It's also worth checking whether a bundle (with accessories or an extended "
        "warranty) beats buying the base unit alone."
    ),
    "uppermid": (
        "You're close to what most Amazon shoppers pay at the high end for {seed_plural} -- expect the "
        "best-reviewed, most fully-featured options in the category, often with longer warranties "
        "or bundled accessories. This tier makes sense if you'll keep and use the item for years "
        "rather than replace it soon, or if it's for frequent/heavy use. If you're on the fence, "
        "check whether last month's price was meaningfully lower -- that tells you if now is a "
        "good time to buy or worth waiting on."
    ),
    "premium": (
        "At this price and up, you're typically paying for the best build quality, the longest "
        "warranties, and features aimed at heavy or professional-level use rather than casual "
        "buyers. It's worth it if you've already tried a cheaper option and outgrown it, or if "
        "you're buying a higher-end gift. Because the gap between \"good\" and \"best\" narrows "
        "the higher you go, spend a few extra minutes comparing two or three top-rated listings "
        "before you buy."
    ),
}

VARIANT_COPY = {
    "dorm": (
        "Buying {seed_plural} for a dorm room",
        "Dorm shopping comes with constraints most buying guides ignore: limited counter or floor "
        "space, shared bathrooms or kitchens, roommate noise tolerance, and -- depending on the "
        "school -- restrictions on certain appliances (some dorms ban space heaters or high-wattage "
        "devices, so check your housing handbook first). Compact size and low noise matter more "
        "than they would in an apartment, and easy cleanup matters more when you're sharing a "
        "space. Because dorm purchases are often first-time-away-from-home buys, a seller with a "
        "clear return policy is worth the small premium over an unbranded listing.",
    ),
    "travel": (
        "What matters when buying {seed_plural} for travel",
        "For travel, weight and packed size usually matter more than raw features -- check the "
        "listed dimensions and weight before assuming something fits in a carry-on or suitcase. "
        "If it's electronic, confirm dual-voltage or airline battery-size rules before buying, "
        "since that's a common reason travel purchases get returned. Durability for repeated "
        "packing and unpacking is worth checking in the reviews specifically -- search the review "
        "text for \"travel\" or \"suitcase\" rather than relying on the star average alone.",
    ),
    "small-apartment": (
        "Choosing {seed_plural} for a small apartment",
        "Small-space shopping is really a tradeoff between footprint and function: look for "
        "listings that specifically mention compact dimensions, wall-mount or under-cabinet "
        "options, or multi-use design, since those are built with apartment living in mind. "
        "Storage when the item isn't in use matters as much as its footprint while in use -- check "
        "whether it folds, stacks, or stores easily. Noise and shared-wall considerations (if "
        "you're in a multi-unit building) are also worth checking in reviews before buying.",
    ),
    "black-friday-deals": (
        "Timing a Black Friday deal on {seed_plural}",
        "Black Friday pricing on {seed_plural} typically starts appearing in the days just before the "
        "holiday and can shift hour to hour on the day itself, so check more than once rather than "
        "buying at the first discount you see. The deepest markdowns historically cluster on the "
        "most popular models, while lesser-known listings see smaller or no discount -- don't "
        "assume every item tagged as a \"deal\" is actually cheaper than its normal price. "
        "Comparing the price a week earlier to the sale price is the simplest way to tell if it's "
        "a real discount.",
    ),
    "christmas-deals": (
        "Buying {seed_plural} as a Christmas gift",
        "Gift shopping for {seed_plural} adds a few considerations beyond price: check the shipping "
        "cutoff date for guaranteed Christmas delivery before you buy, and prefer sellers with an "
        "easy gift-return or exchange policy in case sizing or preference is wrong. If you want to "
        "hide the price, look for listings that ship in plain packaging or without an included "
        "invoice. Buying earlier in December, rather than the last few days, also gives you more "
        "choice of sellers and shipping speeds.",
    ),
    "cyber-monday-deals": (
        "Is Cyber Monday the best time to buy {seed_plural}?",
        "Cyber Monday deals on {seed_plural} are usually online-exclusive and tend to be strongest on "
        "electronics and higher-price items rather than everyday small purchases -- it's worth "
        "comparing the Cyber Monday price against the Black Friday price for the same listing, "
        "since they aren't always different. Popular sizes and colors sell out faster on Cyber "
        "Monday than on any other shopping day, so if you already know what you want, buy early in "
        "the day rather than waiting. As with any single-day sale, check the item's price history "
        "if you can -- some \"deals\" are only modestly below the everyday price.",
    ),
}


def price_band(price: int) -> str:
    for ceiling, band, _heading in PRICE_BANDS:
        if price <= ceiling:
            return band
    return "premium"


def price_heading_template(band: str) -> str:
    for _ceiling, b, heading in PRICE_BANDS:
        if b == band:
            return heading
    return "Buying guide"


def build_section(seed_phrase: str, heading_tmpl: str, body_tmpl: str, price: int | None = None) -> str:
    seed_plural = pluralize(seed_phrase)
    fmt_args = {"seed": seed_phrase, "seed_plural": seed_plural}
    if price is not None:
        fmt_args["price"] = price
    heading_html = heading_tmpl.format(**fmt_args)
    body_html = body_tmpl.format(**fmt_args)
    return (
        f'      {MARKER}\n'
        f'      <section class="mb-10">\n'
        f'        <h2 class="text-2xl font-extrabold mb-3">{heading_html}</h2>\n'
        f'        <p class="text-slate-600 leading-relaxed max-w-3xl">{body_html}</p>\n'
        f'      </section>\n\n'
    )


def process_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return "already-enriched"
    anchor_match = ANCHOR_RE.search(text)
    if not anchor_match:
        return "no-anchor"

    stem = path.stem
    m = PRICE_RE.match(stem)
    price = None
    if m:
        seed_slug = m.group("seed")
        price = int(m.group("price"))
        band = price_band(price)
        heading = price_heading_template(band)
        body = PRICE_COPY[band]
    else:
        m = VARIANT_RE.match(stem)
        if not m:
            return "no-match"
        seed_slug = m.group("seed")
        variant = m.group("variant")
        heading, body = VARIANT_COPY[variant]

    seed_phrase = seed_slug.replace("-", " ")
    section = build_section(seed_phrase, heading, body, price=price)
    insert_at = anchor_match.start()
    new_text = text[:insert_at] + section + "      " + text[insert_at:]
    path.write_text(new_text, encoding="utf-8")
    return "enriched"


def main() -> None:
    counts: dict[str, int] = {}
    for p in sorted(ROOT.glob("*.html")):
        result = process_file(p)
        counts[result] = counts.get(result, 0) + 1
    for k, v in sorted(counts.items()):
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
