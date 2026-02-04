#!/usr/bin/env python3
from pathlib import Path
import html

SITE = "https://bestdealsonline.us"
TAG = "bestdeals0ad2-20"

NAV = """
      <nav class=\"text-sm text-slate-200 flex flex-wrap gap-4\">\n        <a class=\"hover:text-yellow-400\" href=\"/\">Home</a>\n        <a class=\"hover:text-yellow-400\" href=\"/electronics-deals.html\">Electronics</a>\n        <a class=\"hover:text-yellow-400\" href=\"/kitchen-deals.html\">Kitchen</a>\n        <a class=\"hover:text-yellow-400\" href=\"/home-deals.html\">Home Deals</a>\n        <a class=\"hover:text-yellow-400\" href=\"/fitness-deals.html\">Fitness</a>\n        <a class=\"hover:text-yellow-400\" href=\"/kids-deals.html\">Kids</a>\n        <a class=\"hover:text-yellow-400\" href=\"/pets-deals.html\">Pets</a>\n        <a class=\"hover:text-yellow-400\" href=\"/tools-deals.html\">Tools</a>\n        <a class=\"hover:text-yellow-400\" href=\"/beauty-deals.html\">Beauty</a>\n        <a class=\"hover:text-yellow-400\" href=\"/drummer-deals.html\">Drummer Deals</a>\n      </nav>
""".strip("\n")

FOOTER = """<footer class='border-t border-slate-200'><div class='max-w-5xl mx-auto px-4 py-8 text-sm text-slate-500'><div class='flex flex-col gap-3'><div><strong>Affiliate disclosure:</strong> We may earn a commission when you buy through links on this site, at no extra cost to you.</div><div class='flex flex-wrap gap-x-4 gap-y-2'><a class='hover:text-slate-900' href='/electronics-deals.html'>Electronics hub</a><a class='hover:text-slate-900' href='/kitchen-deals.html'>Kitchen hub</a><a class='hover:text-slate-900' href='/home-deals.html'>Home hub</a><a class='hover:text-slate-900' href='/fitness-deals.html'>Fitness hub</a><a class='hover:text-slate-900' href='/kids-deals.html'>Kids hub</a><a class='hover:text-slate-900' href='/pets-deals.html'>Pets hub</a><a class='hover:text-slate-900' href='/tools-deals.html'>Tools hub</a><a class='hover:text-slate-900' href='/beauty-deals.html'>Beauty hub</a></div></div></div></footer>"""


def amazon_search_url(query: str, campaign_slug: str) -> str:
    q = html.escape(query)
    # url-encode spaces as %20, dollars as %24
    from urllib.parse import quote
    return (
        f"https://www.amazon.com/s?k={quote(query)}"
        f"&tag={TAG}&utm_source=bestdealsonline&utm_medium=seo&utm_campaign=bdo_{campaign_slug}"
    )


def card_link(href: str, title: str, desc: str, outbound: bool) -> str:
    arrow = "↗" if outbound else "→"
    rel = "nofollow noopener noreferrer" if outbound else ""
    target = " target='_blank'" if outbound else ""
    rel_attr = f" rel='{rel}'" if outbound else ""
    return (
        f"<a class='bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-md p-5 flex items-start justify-between gap-4' href='{href}'{target}{rel_attr}>"
        f"<div><div class='font-bold text-slate-900'>{html.escape(title)}</div>"
        f"<div class='text-sm text-slate-500 mt-1'>{html.escape(desc)}</div></div>"
        f"<span class='text-slate-400' aria-hidden='true'>{arrow}</span></a>"
    )


def build_page(slug: str, title: str, description: str, intro: str, quick_amz_label: str, quick_amz_query: str, quick_internal_href: str, quick_internal_label: str, queries: list[tuple[str,str]], related_links: list[tuple[str,str]]):
    canonical = f"{SITE}/{slug}"
    # quick links
    quick1 = (
        f"<a class='bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-md p-4' "
        f"href='{amazon_search_url(quick_amz_query, slug)}' target='_blank' rel='nofollow noopener noreferrer'>"
        f"<div class='text-xs uppercase tracking-widest text-blue-600 font-bold'>Quick link</div>"
        f"<div class='font-extrabold mt-1'>{html.escape(quick_amz_label)}</div>"
        f"<div class='text-sm text-slate-500 mt-1'>See live prices</div></a>"
    )
    quick2 = (
        "<a class='bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-md p-4' href='/'>"
        "<div class='text-xs uppercase tracking-widest text-blue-600 font-bold'>Browse</div>"
        "<div class='font-extrabold mt-1'>Back to homepage</div>"
        "<div class='text-sm text-slate-500 mt-1'>All categories</div></a>"
    )
    quick3 = (
        f"<a class='bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-md p-4' href='{quick_internal_href}'>"
        f"<div class='text-xs uppercase tracking-widest text-blue-600 font-bold'>Related</div>"
        f"<div class='font-extrabold mt-1'>{html.escape(quick_internal_label)}</div>"
        f"<div class='text-sm text-slate-500 mt-1'>More long-tail lists</div></a>"
    )

    cards = []
    for q, desc in queries:
        cards.append(card_link(amazon_search_url(q, slug), q, desc, True))

    related = "\n".join(
        [
            f"<a class='px-3 py-1.5 rounded-full border border-slate-200 bg-white hover:bg-slate-50' href='{href}'>{html.escape(label)}</a>"
            for href, label in related_links
        ]
    )

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{html.escape(title)} (2026) | Best Deals Online</title>
  <meta name=\"description\" content=\"{html.escape(description)}\" />
  <link rel=\"canonical\" href=\"{canonical}\" />
  <meta property=\"og:title\" content=\"{html.escape(title)} (2026) | Best Deals Online\" />
  <meta property=\"og:description\" content=\"{html.escape(description)}\" />
  <meta property=\"og:type\" content=\"website\" />
  <meta property=\"og:url\" content=\"{canonical}\" />
  <meta name=\"twitter:card\" content=\"summary\" />
  <script src=\"https://cdn.tailwindcss.com\"></script>
  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap\" rel=\"stylesheet\">
  <style> :root {{ font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }} </style>
</head>
<body class=\"bg-slate-50 text-slate-900\">
  <header class=\"bg-slate-900 text-white\">
    <div class=\"max-w-5xl mx-auto px-4 py-5 flex items-center justify-between\">
      <a href=\"/\" class=\"font-extrabold tracking-tight\">BestDealsOnline</a>
{NAV}
    </div>
  </header>
  <main class=\"max-w-5xl mx-auto px-4 py-10\">

<h1 class='text-3xl md:text-4xl font-extrabold tracking-tight mb-3'>{html.escape(title)}</h1>
<p class='text-slate-600 leading-relaxed mb-8'>{html.escape(intro)}</p>
<div class='grid grid-cols-1 md:grid-cols-3 gap-4 mb-10'>
{quick1}
{quick2}
{quick3}
</div>
<section class='mb-10'>
<h2 class='text-2xl font-extrabold mb-3'>{html.escape(title)} (high intent)</h2>
<div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
""" + "\n".join(cards) + """
</div>
</section>
<section class='mt-12'>
<h2 class='text-xl font-extrabold mb-3'>Related pages</h2>
<div class='flex flex-wrap gap-2 text-sm'>
{related}
</div></section>
</main>
{FOOTER}
</body></html>
"""


def main():
    root = Path(__file__).resolve().parents[1]
    pages = [
        {
            "slug": "toaster-oven-under-100.html",
            "title": "Best Toaster Oven Deals Under $100",
            "description": "Toaster ovens under $100 that are worth considering. Click through to see live prices on Amazon.",
            "intro": "Toaster ovens are a high-intent kitchen upgrade. Use these common under-$100 searches to compare sizes, features, and live prices quickly.",
            "quick_amz_label": "Shop toaster ovens on Amazon",
            "quick_amz_query": "toaster oven under $100",
            "quick_internal_href": "/kitchen-under-100.html",
            "quick_internal_label": "Kitchen under $100",
            "queries": [
                ("toaster oven under $100", "The core query shoppers use."),
                ("compact toaster oven under $100", "For small counters and apartments."),
                ("air fryer toaster oven under $100", "Combo units people compare heavily."),
                ("toaster oven with convection under $100", "Often searched for crisping/baking."),
                ("4 slice toaster oven under $100", "Size-specific intent."),
                ("best toaster oven under $100", "Top-pick comparison searches."),
            ],
            "related": [
                ("/kitchen-deals.html", "Kitchen deals hub"),
                ("/air-fryer-under-100.html", "Air fryers under $100"),
                ("/blender-under-100.html", "Blenders under $100"),
                ("/coffee-maker-under-100.html", "Coffee makers under $100"),
                ("/nonstick-cookware-under-100.html", "Nonstick cookware under $100"),
            ],
        },
        {
            "slug": "immersion-blender-under-50.html",
            "title": "Best Immersion Blender Deals Under $50",
            "description": "Immersion blenders under $50 for soups, sauces, and smoothies. Click through to see live prices on Amazon.",
            "intro": "Immersion blenders are a small, everyday kitchen tool with lots of price competition. These searches cover the most common under-$50 intents.",
            "quick_amz_label": "Shop immersion blenders on Amazon",
            "quick_amz_query": "immersion blender under $50",
            "quick_internal_href": "/kitchen-under-50.html",
            "quick_internal_label": "Kitchen under $50",
            "queries": [
                ("immersion blender under $50", "The main budget query."),
                ("hand blender under $50", "Alternate wording shoppers use."),
                ("immersion blender with whisk under $50", "Attachment-focused intent."),
                ("immersion blender for soup under $50", "Cooking use-case."),
                ("stainless steel immersion blender under $50", "Material preference."),
                ("best immersion blender under $50", "Top pick comparisons."),
            ],
            "related": [
                ("/kitchen-deals.html", "Kitchen deals hub"),
                ("/blender-under-100.html", "Blenders under $100"),
                ("/nonstick-cookware-under-100.html", "Nonstick cookware under $100"),
                ("/meal-prep-containers-under-25.html", "Meal prep containers under $25"),
                ("/electric-kettle-under-50.html", "Electric kettles under $50"),
            ],
        },
        {
            "slug": "food-scale-under-25.html",
            "title": "Best Food Scale Deals Under $25",
            "description": "Food scales under $25 for meal prep and baking. Click through to see live prices on Amazon.",
            "intro": "Food scales are an evergreen, high-utility buy for meal prep and baking. These under-$25 searches cover the most common features shoppers want.",
            "quick_amz_label": "Shop food scales on Amazon",
            "quick_amz_query": "food scale under $25",
            "quick_internal_href": "/meal-prep-containers-under-25.html",
            "quick_internal_label": "Meal prep containers under $25",
            "queries": [
                ("food scale under $25", "The core query."),
                ("digital food scale under $25", "Most shoppers want digital."),
                ("food scale for baking under $25", "Baking-focused intent."),
                ("food scale with tare under $25", "Feature-specific searches."),
                ("kitchen scale under $25", "Common alternate wording."),
                ("gram scale for cooking under $25", "Precision use-case."),
            ],
            "related": [
                ("/kitchen-deals.html", "Kitchen deals hub"),
                ("/bento-lunch-box-under-25.html", "Bento lunch boxes under $25"),
                ("/meal-prep-containers-under-25.html", "Meal prep containers under $25"),
                ("/kitchen-under-50.html", "Kitchen under $50"),
                ("/coffee-maker-under-100.html", "Coffee makers under $100"),
            ],
        },
        {
            "slug": "bluetooth-speaker-under-50.html",
            "title": "Best Bluetooth Speaker Deals Under $50",
            "description": "Bluetooth speakers under $50 that are worth considering. Click through to see live prices on Amazon.",
            "intro": "Bluetooth speakers are a classic under-$50 electronics buy. Use these common searches to compare portable vs. louder home options.",
            "quick_amz_label": "Shop Bluetooth speakers on Amazon",
            "quick_amz_query": "bluetooth speaker under $50",
            "quick_internal_href": "/electronics-under-50.html",
            "quick_internal_label": "Electronics under $50",
            "queries": [
                ("bluetooth speaker under $50", "The main budget query."),
                ("waterproof bluetooth speaker under $50", "Outdoor/portable intent."),
                ("portable bluetooth speaker under $50", "Travel-friendly options."),
                ("loud bluetooth speaker under $50", "Performance-focused searches."),
                ("bluetooth speaker with bass under $50", "Sound signature preference."),
                ("best bluetooth speaker under $50", "Top pick comparisons."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/wireless-earbuds-under-50.html", "Wireless earbuds under $50"),
                ("/power-bank-under-50.html", "Power banks under $50"),
                ("/usb-c-charger-under-50.html", "USB‑C chargers under $50"),
                ("/electronics-under-100.html", "Electronics under $100"),
            ],
        },
        {
            "slug": "gaming-mouse-under-50.html",
            "title": "Best Gaming Mouse Deals Under $50",
            "description": "Gaming mice under $50 for work and play. Click through to see live prices on Amazon.",
            "intro": "Gaming mice under $50 are an evergreen value category. These searches cover wired vs. wireless, grip styles, and popular feature intents.",
            "quick_amz_label": "Shop gaming mice on Amazon",
            "quick_amz_query": "gaming mouse under $50",
            "quick_internal_href": "/electronics-under-50.html",
            "quick_internal_label": "Electronics under $50",
            "queries": [
                ("gaming mouse under $50", "The core query."),
                ("wireless gaming mouse under $50", "Cable-free setups."),
                ("lightweight gaming mouse under $50", "FPS-focused intent."),
                ("gaming mouse for small hands under $50", "Fit and comfort."),
                ("rgb gaming mouse under $50", "Feature styling."),
                ("best gaming mouse under $50", "Top pick comparisons."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/mechanical-keyboard-under-100.html", "Mechanical keyboards under $100"),
                ("/webcam-under-100.html", "Webcams under $100"),
                ("/electronics-under-100.html", "Electronics under $100"),
                ("/usb-c-charger-under-50.html", "USB‑C chargers under $50"),
            ],
        },
        {
            "slug": "usb-microphone-under-100.html",
            "title": "Best USB Microphone Deals Under $100",
            "description": "USB microphones under $100 for streaming, meetings, and podcasts. Click through to see live prices on Amazon.",
            "intro": "USB mics are a popular upgrade for WFH calls, streaming, and beginner podcasts. These searches cover the most common under-$100 intents.",
            "quick_amz_label": "Shop USB microphones on Amazon",
            "quick_amz_query": "usb microphone under $100",
            "quick_internal_href": "/electronics-under-100.html",
            "quick_internal_label": "Electronics under $100",
            "queries": [
                ("usb microphone under $100", "The main budget query."),
                ("usb microphone for streaming under $100", "Creator-focused intent."),
                ("usb microphone for podcast under $100", "Beginner podcast searches."),
                ("usb microphone for zoom meetings under $100", "WFH calls."),
                ("usb microphone with mute button under $100", "Feature-specific intent."),
                ("best usb microphone under $100", "Top pick comparisons."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/webcam-under-100.html", "Webcams under $100"),
                ("/noise-cancelling-headphones-under-100.html", "Noise-cancelling headphones under $100"),
                ("/mechanical-keyboard-under-100.html", "Mechanical keyboards under $100"),
                ("/electronics-under-50.html", "Electronics under $50"),
            ],
        },
        {
            "slug": "smart-plug-under-25.html",
            "title": "Best Smart Plug Deals Under $25",
            "description": "Smart plugs under $25 for easy home automation. Click through to see live prices on Amazon.",
            "intro": "Smart plugs are one of the cheapest ways to add automation to lights and small appliances. These searches focus on the most common compatibility intents.",
            "quick_amz_label": "Shop smart plugs on Amazon",
            "quick_amz_query": "smart plug under $25",
            "quick_internal_href": "/electronics-under-50.html",
            "quick_internal_label": "Electronics under $50",
            "queries": [
                ("smart plug under $25", "The core query."),
                ("smart plug works with alexa under $25", "Assistant compatibility."),
                ("smart plug works with google home under $25", "Assistant compatibility."),
                ("outdoor smart plug under $25", "Seasonal/outdoor setups."),
                ("smart plug with energy monitoring under $25", "Feature-focused search."),
                ("best smart plug under $25", "Top pick comparisons."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/usb-c-charger-under-50.html", "USB‑C chargers under $50"),
                ("/power-bank-under-50.html", "Power banks under $50"),
                ("/home-under-50.html", "Home under $50"),
                ("/wifi-router-under-100.html", "Wi‑Fi routers under $100"),
            ],
        },
        {
            "slug": "stick-vacuum-under-100.html",
            "title": "Best Stick Vacuum Deals Under $100",
            "description": "Stick vacuums under $100 for quick cleanups. Click through to see live prices on Amazon.",
            "intro": "Stick vacuums are an evergreen home category for quick cleanups and small spaces. These searches cover corded vs. cordless and key feature intents.",
            "quick_amz_label": "Shop stick vacuums on Amazon",
            "quick_amz_query": "stick vacuum under $100",
            "quick_internal_href": "/home-under-100.html",
            "quick_internal_label": "Home under $100",
            "queries": [
                ("stick vacuum under $100", "The core query."),
                ("cordless stick vacuum under $100", "Cable-free convenience."),
                ("corded stick vacuum under $100", "Budget-friendly options."),
                ("stick vacuum for pet hair under $100", "Pet-hair intent."),
                ("lightweight stick vacuum under $100", "Small space/apartment intent."),
                ("best stick vacuum under $100", "Top pick comparisons."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/home-under-50.html", "Home under $50"),
                ("/pets-deals.html", "Pets deals hub"),
                ("/pet-grooming-brush-under-25.html", "Pet grooming brushes under $25"),
                ("/storage-ottoman-under-100.html", "Storage ottomans under $100"),
            ],
        },
        {
            "slug": "mattress-topper-under-100.html",
            "title": "Best Mattress Topper Deals Under $100",
            "description": "Mattress toppers under $100 for a quick sleep upgrade. Click through to see live prices on Amazon.",
            "intro": "Mattress toppers are one of the fastest ways to refresh a bed without buying a new mattress. These searches cover foam, cooling, and size intents under $100.",
            "quick_amz_label": "Shop mattress toppers on Amazon",
            "quick_amz_query": "mattress topper under $100",
            "quick_internal_href": "/bed-sheets-under-50.html",
            "quick_internal_label": "Bed sheets under $50",
            "queries": [
                ("mattress topper under $100", "The core query."),
                ("memory foam mattress topper under $100", "Most common material preference."),
                ("cooling mattress topper under $100", "Hot-sleeper intent."),
                ("queen mattress topper under $100", "Size-specific search."),
                ("mattress topper for back pain under $100", "Problem/benefit intent."),
                ("best mattress topper under $100", "Top pick comparisons."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/bed-sheet-set-under-50.html", "Bed sheet sets under $50"),
                ("/bed-sheets-under-50.html", "Bed sheets under $50"),
                ("/home-under-100.html", "Home under $100"),
                ("/blackout-curtains-under-50.html", "Blackout curtains under $50"),
            ],
        },
        {
            "slug": "desk-lamp-under-30.html",
            "title": "Best Desk Lamp Deals Under $30",
            "description": "Desk lamps under $30 for reading and home offices. Click through to see live prices on Amazon.",
            "intro": "Desk lamps are an evergreen home-office buy. These searches cover brightness, clamp styles, and common feature intents while staying under $30.",
            "quick_amz_label": "Shop desk lamps on Amazon",
            "quick_amz_query": "desk lamp under $30",
            "quick_internal_href": "/home-under-50.html",
            "quick_internal_label": "Home under $50",
            "queries": [
                ("desk lamp under $30", "The core query."),
                ("led desk lamp under $30", "Most popular style."),
                ("desk lamp with clamp under $30", "Space-saving setups."),
                ("desk lamp for reading under $30", "Use-case intent."),
                ("dimmable desk lamp under $30", "Feature-focused search."),
                ("best desk lamp under $30", "Top pick comparisons."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/led-floor-lamp-under-50.html", "LED floor lamps under $50"),
                ("/home-under-50.html", "Home under $50"),
                ("/electronics-under-50.html", "Electronics under $50"),
                ("/webcam-under-100.html", "Webcams under $100"),
            ],
        },
        {
            "slug": "massage-gun-under-100.html",
            "title": "Best Massage Gun Deals Under $100",
            "description": "Massage guns under $100 for post-workout recovery. Click through to see live prices on Amazon.",
            "intro": "Massage guns under $100 are a common recovery upgrade. These searches cover deep tissue, quiet motors, and athlete-focused intents.",
            "quick_amz_label": "Shop massage guns on Amazon",
            "quick_amz_query": "massage gun under $100",
            "quick_internal_href": "/fitness-deals.html",
            "quick_internal_label": "Fitness deals hub",
            "queries": [
                ("massage gun under $100", "The main budget query."),
                ("deep tissue massage gun under $100", "Intensity-focused searches."),
                ("quiet massage gun under $100", "Noise-sensitive shoppers."),
                ("massage gun for athletes under $100", "Training/recovery intent."),
                ("massage gun for back under $100", "Body-area intent."),
                ("best massage gun under $100", "Top pick comparisons."),
            ],
            "related": [
                ("/fitness-deals.html", "Fitness deals hub"),
                ("/foam-roller-under-25.html", "Foam rollers under $25"),
                ("/resistance-bands-under-25.html", "Resistance bands under $25"),
                ("/kettlebell-under-50.html", "Kettlebells under $50"),
                ("/adjustable-dumbbells-under-100.html", "Adjustable dumbbells under $100"),
            ],
        },
        {
            "slug": "ab-roller-under-25.html",
            "title": "Best Ab Roller Deals Under $25",
            "description": "Ab rollers under $25 for at-home core workouts. Click through to see live prices on Amazon.",
            "intro": "Ab rollers are a low-cost, high-intent fitness tool. These searches cover knee-pad bundles, stability wheels, and beginner-friendly options under $25.",
            "quick_amz_label": "Shop ab rollers on Amazon",
            "quick_amz_query": "ab roller under $25",
            "quick_internal_href": "/fitness-deals.html",
            "quick_internal_label": "Fitness deals hub",
            "queries": [
                ("ab roller under $25", "The core query."),
                ("ab wheel under $25", "Alternate wording shoppers use."),
                ("ab roller with knee pad under $25", "Bundle-focused intent."),
                ("dual wheel ab roller under $25", "Stability-focused searches."),
                ("ab roller for beginners under $25", "Beginner intent."),
                ("best ab roller under $25", "Top pick comparisons."),
            ],
            "related": [
                ("/fitness-deals.html", "Fitness deals hub"),
                ("/pull-up-bar-under-50.html", "Pull-up bars under $50"),
                ("/resistance-bands-under-25.html", "Resistance bands under $25"),
                ("/foam-roller-under-25.html", "Foam rollers under $25"),
                ("/yoga-mat-under-25.html", "Yoga mats under $25"),
            ],
        },
        {
            "slug": "kids-scooter-under-100.html",
            "title": "Best Kids Scooter Deals Under $100",
            "description": "Kids scooters under $100 for outdoor play. Click through to see live prices on Amazon.",
            "intro": "Kids scooters are a high-intent gift and outdoor play category. These searches cover folding scooters, 3-wheel balance, and age-specific intents under $100.",
            "quick_amz_label": "Shop kids scooters on Amazon",
            "quick_amz_query": "kids scooter under $100",
            "quick_internal_href": "/kids-deals.html",
            "quick_internal_label": "Kids deals hub",
            "queries": [
                ("kids scooter under $100", "The core query."),
                ("3 wheel scooter for kids under $100", "Balance-focused intent."),
                ("folding scooter for kids under $100", "Portability and storage."),
                ("kids scooter with light up wheels under $100", "Feature-focused searches."),
                ("kids scooter for 5 year old under $100", "Age-specific intent."),
                ("best kids scooter under $100", "Top pick comparisons."),
            ],
            "related": [
                ("/kids-deals.html", "Kids deals hub"),
                ("/toddler-balance-bike-under-100.html", "Toddler balance bikes under $100"),
                ("/kids-helmet-under-30.html", "Kids helmets under $30"),
                ("/kids-backpack-under-30.html", "Kids backpacks under $30"),
                ("/board-games-under-25.html", "Board games under $25"),
            ],
        },
        {
            "slug": "science-kits-under-25.html",
            "title": "Best Science Kit Deals Under $25",
            "description": "Science kits under $25 for hands-on learning. Click through to see live prices on Amazon.",
            "intro": "Science kits are evergreen for gifts and at-home learning. These searches cover age ranges, STEM keywords, and popular themes while staying under $25.",
            "quick_amz_label": "Shop science kits on Amazon",
            "quick_amz_query": "science kit under $25",
            "quick_internal_href": "/learning-toys-under-25.html",
            "quick_internal_label": "Learning toys under $25",
            "queries": [
                ("science kit under $25", "The core query."),
                ("stem science kit under $25", "STEM-focused intent."),
                ("science kit for kids age 8-12 under $25", "Age-range searches."),
                ("volcano science kit under $25", "Classic theme."),
                ("crystal growing kit under $25", "Popular activity."),
                ("best science kit under $25", "Top pick comparisons."),
            ],
            "related": [
                ("/kids-deals.html", "Kids deals hub"),
                ("/learning-toys-under-25.html", "Learning toys under $25"),
                ("/building-block-sets-under-50.html", "Building block sets under $50"),
                ("/board-games-under-25.html", "Board games under $25"),
                ("/kids-tablet-under-100.html", "Kids tablets under $100"),
            ],
        },
        {
            "slug": "dog-toys-under-25.html",
            "title": "Best Dog Toy Deals Under $25",
            "description": "Dog toys under $25 for chew, fetch, and enrichment. Click through to see live prices on Amazon.",
            "intro": "Dog toys are a high-frequency purchase category. These searches cover tough chews, puzzle toys, and size intents under $25.",
            "quick_amz_label": "Shop dog toys on Amazon",
            "quick_amz_query": "dog toys under $25",
            "quick_internal_href": "/pets-deals.html",
            "quick_internal_label": "Pets deals hub",
            "queries": [
                ("dog toys under $25", "The core query."),
                ("tough dog toys under $25", "Chewer-focused intent."),
                ("indestructible dog toy under $25", "Common wording for heavy chewers."),
                ("dog puzzle toys under $25", "Enrichment intent."),
                ("dog toys for large dogs under $25", "Size-specific searches."),
                ("best dog toys under $25", "Top pick comparisons."),
            ],
            "related": [
                ("/pets-deals.html", "Pets deals hub"),
                ("/dog-bed-under-50.html", "Dog beds under $50"),
                ("/dog-grooming-kit-under-50.html", "Dog grooming kits under $50"),
                ("/pet-water-fountain-under-50.html", "Pet water fountains under $50"),
                ("/pet-car-seat-cover-under-50.html", "Pet car seat covers under $50"),
            ],
        },
        {
            "slug": "pet-nail-grinder-under-30.html",
            "title": "Best Pet Nail Grinder Deals Under $30",
            "description": "Pet nail grinders under $30 for at-home grooming. Click through to see live prices on Amazon.",
            "intro": "Nail grinders are a popular at-home grooming tool. These searches cover quiet models, dog vs. cat use, and beginner-friendly features under $30.",
            "quick_amz_label": "Shop pet nail grinders on Amazon",
            "quick_amz_query": "pet nail grinder under $30",
            "quick_internal_href": "/pet-grooming-brush-under-25.html",
            "quick_internal_label": "Pet grooming brushes under $25",
            "queries": [
                ("pet nail grinder under $30", "The core query."),
                ("dog nail grinder under $30", "Dog-focused intent."),
                ("cat nail grinder under $30", "Cat-focused intent."),
                ("quiet dog nail grinder under $30", "Noise-sensitive shoppers."),
                ("rechargeable nail grinder for dogs under $30", "Power/charging intent."),
                ("best pet nail grinder under $30", "Top pick comparisons."),
            ],
            "related": [
                ("/pets-deals.html", "Pets deals hub"),
                ("/pet-grooming-brush-under-25.html", "Pet grooming brushes under $25"),
                ("/dog-grooming-kit-under-50.html", "Dog grooming kits under $50"),
                ("/cat-litter-mat-under-25.html", "Cat litter mats under $25"),
                ("/pet-water-fountain-under-50.html", "Pet water fountains under $50"),
            ],
        },
        {
            "slug": "cordless-screwdriver-under-50.html",
            "title": "Best Cordless Screwdriver Deals Under $50",
            "description": "Cordless screwdrivers under $50 for home projects. Click through to see live prices on Amazon.",
            "intro": "Cordless screwdrivers are an evergreen DIY tool. These searches cover compact drivers, bit sets, and household assembly intents under $50.",
            "quick_amz_label": "Shop cordless screwdrivers on Amazon",
            "quick_amz_query": "cordless screwdriver under $50",
            "quick_internal_href": "/tools-deals.html",
            "quick_internal_label": "Tools deals hub",
            "queries": [
                ("cordless screwdriver under $50", "The core query."),
                ("electric screwdriver under $50", "Alternate wording."),
                ("compact cordless screwdriver under $50", "Small-space and light-duty intent."),
                ("cordless screwdriver with bits under $50", "Bundle-focused intent."),
                ("rechargeable screwdriver under $50", "Charging convenience."),
                ("best cordless screwdriver under $50", "Top pick comparisons."),
            ],
            "related": [
                ("/tools-deals.html", "Tools deals hub"),
                ("/cordless-drill-under-100.html", "Cordless drills under $100"),
                ("/tool-set-under-100.html", "Tool sets under $100"),
                ("/tool-box-under-50.html", "Tool boxes under $50"),
                ("/tape-measure-under-25.html", "Tape measures under $25"),
            ],
        },
        {
            "slug": "laser-level-under-100.html",
            "title": "Best Laser Level Deals Under $100",
            "description": "Laser levels under $100 for DIY and home improvement. Click through to see live prices on Amazon.",
            "intro": "Laser levels are a high-intent DIY tool category. These searches cover green vs. red lasers, self-leveling features, and tripod bundles under $100.",
            "quick_amz_label": "Shop laser levels on Amazon",
            "quick_amz_query": "laser level under $100",
            "quick_internal_href": "/tools-deals.html",
            "quick_internal_label": "Tools deals hub",
            "queries": [
                ("laser level under $100", "The core query."),
                ("self leveling laser level under $100", "Feature-focused intent."),
                ("green laser level under $100", "Visibility preference."),
                ("laser level with tripod under $100", "Bundle intent."),
                ("cross line laser level under $100", "Common laser type."),
                ("best laser level under $100", "Top pick comparisons."),
            ],
            "related": [
                ("/tools-deals.html", "Tools deals hub"),
                ("/oscillating-multi-tool-under-100.html", "Oscillating multi-tools under $100"),
                ("/socket-set-under-50.html", "Socket sets under $50"),
                ("/torque-wrench-under-100.html", "Torque wrenches under $100"),
                ("/impact-driver-under-100.html", "Impact drivers under $100"),
            ],
        },
        {
            "slug": "niacinamide-serum-under-25.html",
            "title": "Best Niacinamide Serum Deals Under $25",
            "description": "Niacinamide serums under $25 that are worth considering. Click through to see live prices on Amazon.",
            "intro": "Niacinamide is an evergreen skincare ingredient for oil control and barrier support. These searches cover common strengths and skin-type intents under $25.",
            "quick_amz_label": "Shop niacinamide serums on Amazon",
            "quick_amz_query": "niacinamide serum under $25",
            "quick_internal_href": "/skincare-under-25.html",
            "quick_internal_label": "Skincare under $25",
            "queries": [
                ("niacinamide serum under $25", "The core query."),
                ("niacinamide 10% serum under $25", "Strength-specific intent."),
                ("niacinamide serum for oily skin under $25", "Skin-type intent."),
                ("niacinamide serum for acne under $25", "Problem-focused searches."),
                ("niacinamide serum for pores under $25", "Benefit-focused intent."),
                ("best niacinamide serum under $25", "Top pick comparisons."),
            ],
            "related": [
                ("/beauty-deals.html", "Beauty deals hub"),
                ("/skincare-under-25.html", "Skincare under $25"),
                ("/vitamin-c-serum-under-25.html", "Vitamin C serums under $25"),
                ("/retinol-serum-under-25.html", "Retinol serums under $25"),
                ("/skincare-fridge-under-50.html", "Skincare fridges under $50"),
            ],
        },
        {
            "slug": "sunscreen-under-25.html",
            "title": "Best Sunscreen Deals Under $25",
            "description": "Sunscreens under $25 for daily use. Click through to see live prices on Amazon.",
            "intro": "Sunscreen is one of the most evergreen skincare categories. These searches focus on SPF level, mineral vs. chemical, and face vs. body intents under $25.",
            "quick_amz_label": "Shop sunscreens on Amazon",
            "quick_amz_query": "sunscreen under $25",
            "quick_internal_href": "/skincare-under-25.html",
            "quick_internal_label": "Skincare under $25",
            "queries": [
                ("sunscreen under $25", "The core query."),
                ("mineral sunscreen under $25", "Mineral-only preference."),
                ("face sunscreen under $25", "Face-specific intent."),
                ("sunscreen spf 50 under $25", "SPF-strength intent."),
                ("sunscreen for sensitive skin under $25", "Skin sensitivity intent."),
                ("best sunscreen under $25", "Top pick comparisons."),
            ],
            "related": [
                ("/beauty-deals.html", "Beauty deals hub"),
                ("/skincare-under-25.html", "Skincare under $25"),
                ("/makeup-organizer-under-25.html", "Makeup organizers under $25"),
                ("/vitamin-c-serum-under-25.html", "Vitamin C serums under $25"),
                ("/retinol-serum-under-25.html", "Retinol serums under $25"),
            ],
        },
    ]

    # Note: one related link points to /kids-helmet-under-30.html which doesn't exist yet.
    # We'll swap that below to an existing page to avoid broken links.

    for page in pages:
        slug = page["slug"]
        out = root / slug
        if out.exists():
            continue
        related = [(h, l) for (h, l) in page["related"] if h != f"/{slug}"]
        # fix missing kids helmet page
        related = [("/kids-headphones-under-50.html", "Kids headphones under $50") if h == "/kids-helmet-under-30.html" else (h, l) for h, l in related]
        html_txt = build_page(
            slug=slug,
            title=page["title"],
            description=page["description"],
            intro=page["intro"],
            quick_amz_label=page["quick_amz_label"],
            quick_amz_query=page["quick_amz_query"],
            quick_internal_href=page["quick_internal_href"],
            quick_internal_label=page["quick_internal_label"],
            queries=page["queries"],
            related_links=related,
        )
        out.write_text(html_txt, encoding="utf-8")
        print("wrote", out.name)


if __name__ == "__main__":
    main()
