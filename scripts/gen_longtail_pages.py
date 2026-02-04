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

        # ==== NEW HIGH-INTENT PAGES (fast clicks/commissions) ====
        {
            "slug": "dash-cam-under-100.html",
            "title": "Best Dash Cam Deals Under $100",
            "description": "Dash cams under $100 that people actually buy. Click through to see live prices on Amazon.",
            "intro": "Dash cams are a classic high-intent purchase. These under-$100 searches focus on the features shoppers compare most: front+rear, night vision, Wi‑Fi, and parking mode.",
            "quick_amz_label": "Shop dash cams on Amazon",
            "quick_amz_query": "dash cam under $100",
            "quick_internal_href": "/electronics-under-100.html",
            "quick_internal_label": "Electronics under $100",
            "queries": [
                ("dash cam under $100", "The core budget query."),
                ("dual dash cam front and rear under $100", "Front+rear coverage intent."),
                ("dash cam with night vision under $100", "Night driving comparisons."),
                ("dash cam with wifi under $100", "App + transfer intent."),
                ("dash cam with gps under $100", "Speed/location logging intent."),
                ("best dash cam under $100", "Top-pick comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/electronics-under-100.html", "Electronics under $100"),
                ("/power-bank-under-50.html", "Power banks under $50"),
                ("/usb-c-charger-under-50.html", "USB‑C chargers under $50"),
                ("/webcam-under-100.html", "Webcams under $100"),
            ],
        },
        {
            "slug": "mini-projector-under-100.html",
            "title": "Best Mini Projector Deals Under $100",
            "description": "Mini projectors under $100 for movies, dorms, and travel. Click through to see live prices on Amazon.",
            "intro": "Mini projectors are a heavily-searched impulse upgrade. These queries cover the most common buyer intents: portability, brightness, and phone compatibility.",
            "quick_amz_label": "Shop mini projectors on Amazon",
            "quick_amz_query": "mini projector under $100",
            "quick_internal_href": "/electronics-under-100.html",
            "quick_internal_label": "Electronics under $100",
            "queries": [
                ("mini projector under $100", "The core query."),
                ("portable projector under $100", "Portability intent."),
                ("projector for bedroom under $100", "Room use-case intent."),
                ("projector compatible with iphone under $100", "Phone compatibility intent."),
                ("wifi projector under $100", "Wireless casting intent."),
                ("best mini projector under $100", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/bluetooth-speaker-under-50.html", "Bluetooth speakers under $50"),
                ("/noise-cancelling-headphones-under-100.html", "Noise-cancelling headphones under $100"),
                ("/webcam-under-100.html", "Webcams under $100"),
                ("/electronics-under-50.html", "Electronics under $50"),
            ],
        },
        {
            "slug": "portable-monitor-under-100.html",
            "title": "Best Portable Monitor Deals Under $100",
            "description": "Portable monitors under $100 for work and travel. Click through to see live prices on Amazon.",
            "intro": "Portable monitors are a high-intent WFH/travel purchase. These under-$100 searches focus on size, USB‑C, and compatibility.",
            "quick_amz_label": "Shop portable monitors on Amazon",
            "quick_amz_query": "portable monitor under $100",
            "quick_internal_href": "/electronics-under-100.html",
            "quick_internal_label": "Electronics under $100",
            "queries": [
                ("portable monitor under $100", "The core query."),
                ("usb c portable monitor under $100", "USB‑C single-cable intent."),
                ("15.6 inch portable monitor under $100", "Size-specific intent."),
                ("portable monitor for laptop under $100", "Use-case intent."),
                ("portable monitor for macbook under $100", "Compatibility intent."),
                ("best portable monitor under $100", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/usb-c-charger-under-50.html", "USB‑C chargers under $50"),
                ("/mechanical-keyboard-under-100.html", "Mechanical keyboards under $100"),
                ("/wireless-earbuds-under-50.html", "Wireless earbuds under $50"),
                ("/electronics-under-100.html", "Electronics under $100"),
            ],
        },
        {
            "slug": "gaming-headset-under-50.html",
            "title": "Best Gaming Headset Deals Under $50",
            "description": "Gaming headsets under $50 for PC/console chat. Click through to see live prices on Amazon.",
            "intro": "Gaming headsets are an evergreen, high-volume purchase. These searches capture budget buyers looking for mic quality, comfort, and platform compatibility.",
            "quick_amz_label": "Shop gaming headsets on Amazon",
            "quick_amz_query": "gaming headset under $50",
            "quick_internal_href": "/electronics-under-50.html",
            "quick_internal_label": "Electronics under $50",
            "queries": [
                ("gaming headset under $50", "The core query."),
                ("ps5 gaming headset under $50", "Console-specific intent."),
                ("xbox gaming headset under $50", "Console-specific intent."),
                ("pc gaming headset under $50", "Platform-specific intent."),
                ("wireless gaming headset under $50", "Wireless preference."),
                ("best gaming headset under $50", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/wireless-earbuds-under-50.html", "Wireless earbuds under $50"),
                ("/usb-microphone-under-100.html", "USB microphones under $100"),
                ("/gaming-mouse-under-50.html", "Gaming mice under $50"),
                ("/mechanical-keyboard-under-100.html", "Mechanical keyboards under $100"),
            ],
        },
        {
            "slug": "wireless-mouse-under-25.html",
            "title": "Best Wireless Mouse Deals Under $25",
            "description": "Wireless mice under $25 for work and school. Click through to see live prices on Amazon.",
            "intro": "A wireless mouse is a small, easy conversion product—people buy it when they’re already shopping. These searches cover silent-click, ergonomic, and laptop-friendly intent.",
            "quick_amz_label": "Shop wireless mice on Amazon",
            "quick_amz_query": "wireless mouse under $25",
            "quick_internal_href": "/electronics-under-50.html",
            "quick_internal_label": "Electronics under $50",
            "queries": [
                ("wireless mouse under $25", "The core budget query."),
                ("silent click wireless mouse under $25", "Noise-sensitive intent."),
                ("ergonomic wireless mouse under $25", "Comfort intent."),
                ("bluetooth mouse under $25", "Bluetooth preference."),
                ("wireless mouse for laptop under $25", "Use-case intent."),
                ("best wireless mouse under $25", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/mechanical-keyboard-under-100.html", "Mechanical keyboards under $100"),
                ("/webcam-under-100.html", "Webcams under $100"),
                ("/usb-c-charger-under-50.html", "USB‑C chargers under $50"),
                ("/gaming-mouse-under-50.html", "Gaming mice under $50"),
            ],
        },
        {
            "slug": "phone-tripod-under-25.html",
            "title": "Best Phone Tripod Deals Under $25",
            "description": "Phone tripods under $25 for filming, TikTok, and calls. Click through to see live prices on Amazon.",
            "intro": "Phone tripods are a cheap, high-conversion accessory. These searches cover height, remote shutter, and portability.",
            "quick_amz_label": "Shop phone tripods on Amazon",
            "quick_amz_query": "phone tripod under $25",
            "quick_internal_href": "/electronics-under-50.html",
            "quick_internal_label": "Electronics under $50",
            "queries": [
                ("phone tripod under $25", "The core query."),
                ("tripod with remote for phone under $25", "Remote shutter intent."),
                ("portable phone tripod under $25", "Travel intent."),
                ("phone tripod tall under $25", "Height intent."),
                ("phone tripod for video under $25", "Use-case intent."),
                ("best phone tripod under $25", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/webcam-under-100.html", "Webcams under $100"),
                ("/usb-microphone-under-100.html", "USB microphones under $100"),
                ("/bluetooth-speaker-under-50.html", "Bluetooth speakers under $50"),
                ("/electronics-under-50.html", "Electronics under $50"),
            ],
        },
        {
            "slug": "air-fryer-liners-under-25.html",
            "title": "Best Air Fryer Liner Deals Under $25",
            "description": "Air fryer liners under $25 to reduce mess and cleanup time. Click through to see live prices on Amazon.",
            "intro": "Air fryer accessories convert well because they’re small add-ons people buy after they already own a fryer. These searches cover silicone vs. disposable and size compatibility.",
            "quick_amz_label": "Shop air fryer liners on Amazon",
            "quick_amz_query": "air fryer liners under $25",
            "quick_internal_href": "/air-fryer-accessories-under-50.html",
            "quick_internal_label": "Air fryer accessories under $50",
            "queries": [
                ("air fryer liners under $25", "The core query."),
                ("silicone air fryer liners under $25", "Reusable preference."),
                ("disposable air fryer liners under $25", "Convenience intent."),
                ("air fryer parchment liners under $25", "Material-specific intent."),
                ("air fryer liners for 6 qt under $25", "Size compatibility intent."),
                ("best air fryer liners under $25", "Comparison searches."),
            ],
            "related": [
                ("/kitchen-deals.html", "Kitchen deals hub"),
                ("/air-fryer-under-100.html", "Air fryers under $100"),
                ("/air-fryer-accessories-under-50.html", "Air fryer accessories under $50"),
                ("/kitchen-under-50.html", "Kitchen under $50"),
                ("/nonstick-cookware-under-100.html", "Nonstick cookware under $100"),
            ],
        },
        {
            "slug": "heated-blanket-under-50.html",
            "title": "Best Heated Blanket Deals Under $50",
            "description": "Heated blankets under $50 for cozy nights. Click through to see live prices on Amazon.",
            "intro": "Heated blankets have strong seasonal demand and high buyer intent. These searches cover size, safety features, and softness.",
            "quick_amz_label": "Shop heated blankets on Amazon",
            "quick_amz_query": "heated blanket under $50",
            "quick_internal_href": "/home-under-50.html",
            "quick_internal_label": "Home under $50",
            "queries": [
                ("heated blanket under $50", "The core query."),
                ("electric blanket under $50", "Alternate wording."),
                ("heated throw blanket under $50", "Throw blanket intent."),
                ("heated blanket with auto shut off under $50", "Safety feature intent."),
                ("soft heated blanket under $50", "Material/feel intent."),
                ("best heated blanket under $50", "Comparison searches."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/bed-sheets-under-50.html", "Bed sheets under $50"),
                ("/blackout-curtains-under-50.html", "Blackout curtains under $50"),
                ("/home-under-50.html", "Home under $50"),
                ("/mattress-topper-under-100.html", "Mattress toppers under $100"),
            ],
        },
        {
            "slug": "dehumidifier-under-100.html",
            "title": "Best Dehumidifier Deals Under $100",
            "description": "Dehumidifiers under $100 for damp rooms. Click through to see live prices on Amazon.",
            "intro": "Dehumidifiers are a high-intent home improvement buy. These queries target small-room and feature-focused shoppers under $100.",
            "quick_amz_label": "Shop dehumidifiers on Amazon",
            "quick_amz_query": "dehumidifier under $100",
            "quick_internal_href": "/home-under-100.html",
            "quick_internal_label": "Home under $100",
            "queries": [
                ("dehumidifier under $100", "The core query."),
                ("small dehumidifier under $100", "Small-room intent."),
                ("mini dehumidifier under $100", "Compact intent."),
                ("dehumidifier for bathroom under $100", "Use-case intent."),
                ("quiet dehumidifier under $100", "Noise-sensitive intent."),
                ("best dehumidifier under $100", "Comparison searches."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/air-purifier-under-100.html", "Air purifiers under $100"),
                ("/humidifier-under-50.html", "Humidifiers under $50"),
                ("/home-under-100.html", "Home under $100"),
                ("/shower-head-under-50.html", "Shower heads under $50"),
            ],
        },
        {
            "slug": "electric-screwdriver-under-50.html",
            "title": "Best Electric Screwdriver Deals Under $50",
            "description": "Electric screwdrivers under $50 for quick DIY fixes. Click through to see live prices on Amazon.",
            "intro": "An electric screwdriver is a high-conversion tool upgrade. These searches focus on bit sets, torque, and compact form factors under $50.",
            "quick_amz_label": "Shop electric screwdrivers on Amazon",
            "quick_amz_query": "electric screwdriver under $50",
            "quick_internal_href": "/tools-deals.html",
            "quick_internal_label": "Tools deals hub",
            "queries": [
                ("electric screwdriver under $50", "The core query."),
                ("cordless electric screwdriver under $50", "Cordless preference."),
                ("electric screwdriver with bits under $50", "Bundle intent."),
                ("small electric screwdriver under $50", "Compact intent."),
                ("electric screwdriver set under $50", "Set intent."),
                ("best electric screwdriver under $50", "Comparison searches."),
            ],
            "related": [
                ("/tools-deals.html", "Tools deals hub"),
                ("/cordless-screwdriver-under-50.html", "Cordless screwdrivers under $50"),
                ("/tool-set-under-100.html", "Tool sets under $100"),
                ("/cordless-drill-under-100.html", "Cordless drills under $100"),
                ("/flashlight-under-50.html", "Flashlights under $50"),
            ],
        },

        # ==== BATCH 2: ELECTRONICS + HOME (fast clicks/commissions) ====
        {
            "slug": "security-camera-under-50.html",
            "title": "Best Security Camera Deals Under $50",
            "description": "Security cameras under $50 for apartments and small setups. Click through to see live prices on Amazon.",
            "intro": "Budget security cams convert well because shoppers want quick peace of mind. These searches focus on indoor cams, night vision, and phone alerts.",
            "quick_amz_label": "Shop security cameras on Amazon",
            "quick_amz_query": "security camera under $50",
            "quick_internal_href": "/electronics-under-50.html",
            "quick_internal_label": "Electronics under $50",
            "queries": [
                ("security camera under $50", "The core budget query."),
                ("indoor security camera under $50", "Indoor setup intent."),
                ("wifi security camera under $50", "Wireless preference."),
                ("security camera with night vision under $50", "Night vision intent."),
                ("pet camera under $50", "Pet monitoring intent."),
                ("best security camera under $50", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/smart-plug-under-25.html", "Smart plugs under $25"),
                ("/wifi-router-under-100.html", "Wi‑Fi routers under $100"),
                ("/webcam-under-100.html", "Webcams under $100"),
                ("/electronics-under-50.html", "Electronics under $50"),
            ],
        },
        {
            "slug": "video-doorbell-under-100.html",
            "title": "Best Video Doorbell Deals Under $100",
            "description": "Video doorbells under $100 to see who’s at the door. Click through to see live prices on Amazon.",
            "intro": "Doorbells are high-intent home security buys. These searches focus on wireless installs, motion alerts, and compatibility.",
            "quick_amz_label": "Shop video doorbells on Amazon",
            "quick_amz_query": "video doorbell under $100",
            "quick_internal_href": "/electronics-under-100.html",
            "quick_internal_label": "Electronics under $100",
            "queries": [
                ("video doorbell under $100", "The core query."),
                ("wireless video doorbell under $100", "No-wires intent."),
                ("battery video doorbell under $100", "Battery-powered preference."),
                ("video doorbell with chime under $100", "Bundle intent."),
                ("video doorbell compatible with alexa under $100", "Smart home compatibility."),
                ("best video doorbell under $100", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/security-camera-under-50.html", "Security cameras under $50"),
                ("/wifi-router-under-100.html", "Wi‑Fi routers under $100"),
                ("/smart-plug-under-25.html", "Smart plugs under $25"),
                ("/electronics-under-100.html", "Electronics under $100"),
            ],
        },
        {
            "slug": "electric-toothbrush-under-25.html",
            "title": "Best Electric Toothbrush Deals Under $25",
            "description": "Electric toothbrushes under $25 for a cheap upgrade. Click through to see live prices on Amazon.",
            "intro": "Electric toothbrushes are a simple, high-conversion upgrade product. These searches cover battery, rechargeable, and travel intent under $25.",
            "quick_amz_label": "Shop electric toothbrushes on Amazon",
            "quick_amz_query": "electric toothbrush under $25",
            "quick_internal_href": "/electronics-under-50.html",
            "quick_internal_label": "Electronics under $50",
            "queries": [
                ("electric toothbrush under $25", "The core query."),
                ("rechargeable electric toothbrush under $25", "Rechargeable preference."),
                ("electric toothbrush for travel under $25", "Travel intent."),
                ("electric toothbrush with timer under $25", "Feature intent."),
                ("kids electric toothbrush under $25", "Kids intent."),
                ("best electric toothbrush under $25", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/usb-c-charger-under-50.html", "USB‑C chargers under $50"),
                ("/wireless-earbuds-under-50.html", "Wireless earbuds under $50"),
                ("/electronics-under-50.html", "Electronics under $50"),
                ("/kids-headphones-under-50.html", "Kids headphones under $50"),
            ],
        },
        {
            "slug": "surge-protector-under-25.html",
            "title": "Best Surge Protector Deals Under $25",
            "description": "Surge protectors under $25 for desks and home offices. Click through to see live prices on Amazon.",
            "intro": "Surge protectors are evergreen, practical buys. These searches cover outlet count, USB ports, and desk-friendly form factors.",
            "quick_amz_label": "Shop surge protectors on Amazon",
            "quick_amz_query": "surge protector under $25",
            "quick_internal_href": "/electronics-under-50.html",
            "quick_internal_label": "Electronics under $50",
            "queries": [
                ("surge protector under $25", "The core query."),
                ("power strip surge protector under $25", "Alternate wording."),
                ("surge protector with usb under $25", "USB port intent."),
                ("flat plug surge protector under $25", "Furniture/space intent."),
                ("surge protector for desk under $25", "Desk setup intent."),
                ("best surge protector under $25", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/usb-c-charger-under-50.html", "USB‑C chargers under $50"),
                ("/smart-plug-under-25.html", "Smart plugs under $25"),
                ("/wireless-mouse-under-25.html", "Wireless mice under $25"),
                ("/mechanical-keyboard-under-100.html", "Mechanical keyboards under $100"),
            ],
        },
        {
            "slug": "usb-hub-under-25.html",
            "title": "Best USB Hub Deals Under $25",
            "description": "USB hubs under $25 for laptops and desktops. Click through to see live prices on Amazon.",
            "intro": "USB hubs convert well because they solve an immediate problem: not enough ports. These searches cover USB‑C hubs and multiport adapters.",
            "quick_amz_label": "Shop USB hubs on Amazon",
            "quick_amz_query": "usb hub under $25",
            "quick_internal_href": "/electronics-under-50.html",
            "quick_internal_label": "Electronics under $50",
            "queries": [
                ("usb hub under $25", "The core query."),
                ("usb c hub under $25", "USB‑C laptop intent."),
                ("usb hub with hdmi under $25", "Display adapter intent."),
                ("powered usb hub under $25", "Power preference."),
                ("usb hub for macbook under $25", "Compatibility searches."),
                ("best usb hub under $25", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/portable-monitor-under-100.html", "Portable monitors under $100"),
                ("/usb-c-charger-under-50.html", "USB‑C chargers under $50"),
                ("/wireless-mouse-under-25.html", "Wireless mice under $25"),
                ("/mechanical-keyboard-under-100.html", "Mechanical keyboards under $100"),
            ],
        },
        {
            "slug": "wireless-charger-under-25.html",
            "title": "Best Wireless Charger Deals Under $25",
            "description": "Wireless chargers under $25 for nightstands and desks. Click through to see live prices on Amazon.",
            "intro": "Wireless chargers are simple add-ons that often convert quickly. These searches cover MagSafe-style, fast charging, and multi-device pads.",
            "quick_amz_label": "Shop wireless chargers on Amazon",
            "quick_amz_query": "wireless charger under $25",
            "quick_internal_href": "/electronics-under-50.html",
            "quick_internal_label": "Electronics under $50",
            "queries": [
                ("wireless charger under $25", "The core query."),
                ("fast wireless charger under $25", "Speed intent."),
                ("wireless charger for iphone under $25", "iPhone intent."),
                ("wireless charger for samsung under $25", "Android intent."),
                ("3 in 1 wireless charger under $25", "Multi-device intent."),
                ("best wireless charger under $25", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/power-bank-under-50.html", "Power banks under $50"),
                ("/usb-c-charger-under-50.html", "USB‑C chargers under $50"),
                ("/wireless-mouse-under-25.html", "Wireless mice under $25"),
                ("/electronics-under-50.html", "Electronics under $50"),
            ],
        },
        {
            "slug": "smart-speaker-under-50.html",
            "title": "Best Smart Speaker Deals Under $50",
            "description": "Smart speakers under $50 for music and voice control. Click through to see live prices on Amazon.",
            "intro": "Smart speakers can be impulse buys during promotions. These searches cover Alexa/Google compatibility, sound, and room size.",
            "quick_amz_label": "Shop smart speakers on Amazon",
            "quick_amz_query": "smart speaker under $50",
            "quick_internal_href": "/electronics-under-50.html",
            "quick_internal_label": "Electronics under $50",
            "queries": [
                ("smart speaker under $50", "The core query."),
                ("alexa speaker under $50", "Alexa intent."),
                ("google assistant speaker under $50", "Google intent."),
                ("smart speaker with good sound under $50", "Sound quality intent."),
                ("smart speaker for bedroom under $50", "Room use-case."),
                ("best smart speaker under $50", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/bluetooth-speaker-under-50.html", "Bluetooth speakers under $50"),
                ("/smart-plug-under-25.html", "Smart plugs under $25"),
                ("/wifi-router-under-100.html", "Wi‑Fi routers under $100"),
                ("/electronics-under-50.html", "Electronics under $50"),
            ],
        },
        {
            "slug": "router-mesh-under-100.html",
            "title": "Best Mesh Wi‑Fi Deals Under $100",
            "description": "Mesh Wi‑Fi systems under $100 to fix dead zones. Click through to see live prices on Amazon.",
            "intro": "Mesh Wi‑Fi is a problem/solution purchase. These searches target buyers trying to fix weak signal and dead zones on a budget.",
            "quick_amz_label": "Shop mesh Wi‑Fi on Amazon",
            "quick_amz_query": "mesh wifi under $100",
            "quick_internal_href": "/wifi-router-under-100.html",
            "quick_internal_label": "Wi‑Fi routers under $100",
            "queries": [
                ("mesh wifi under $100", "The core query."),
                ("mesh wifi system under $100", "Alternate wording."),
                ("mesh wifi for apartment under $100", "Apartment intent."),
                ("dual band mesh wifi under $100", "Spec intent."),
                ("wifi extender mesh under $100", "Related searches."),
                ("best mesh wifi under $100", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/wifi-router-under-100.html", "Wi‑Fi routers under $100"),
                ("/smart-plug-under-25.html", "Smart plugs under $25"),
                ("/security-camera-under-50.html", "Security cameras under $50"),
                ("/electronics-under-100.html", "Electronics under $100"),
            ],
        },
        {
            "slug": "wireless-keyboard-under-50.html",
            "title": "Best Wireless Keyboard Deals Under $50",
            "description": "Wireless keyboards under $50 for work and school. Click through to see live prices on Amazon.",
            "intro": "Wireless keyboards are an easy desk upgrade that converts well. These searches focus on compact layouts, Bluetooth, and quiet keys.",
            "quick_amz_label": "Shop wireless keyboards on Amazon",
            "quick_amz_query": "wireless keyboard under $50",
            "quick_internal_href": "/electronics-under-50.html",
            "quick_internal_label": "Electronics under $50",
            "queries": [
                ("wireless keyboard under $50", "The core query."),
                ("bluetooth keyboard under $50", "Bluetooth preference."),
                ("wireless keyboard for mac under $50", "Compatibility intent."),
                ("compact wireless keyboard under $50", "Space-saving intent."),
                ("quiet wireless keyboard under $50", "Noise intent."),
                ("best wireless keyboard under $50", "Comparison searches."),
            ],
            "related": [
                ("/electronics-deals.html", "Electronics deals hub"),
                ("/wireless-mouse-under-25.html", "Wireless mice under $25"),
                ("/mechanical-keyboard-under-100.html", "Mechanical keyboards under $100"),
                ("/usb-hub-under-25.html", "USB hubs under $25"),
                ("/portable-monitor-under-100.html", "Portable monitors under $100"),
            ],
        },

        # Home batch
        {
            "slug": "steam-mop-under-100.html",
            "title": "Best Steam Mop Deals Under $100",
            "description": "Steam mops under $100 for sealed floors. Click through to see live prices on Amazon.",
            "intro": "Steam mops are a problem/solution home-cleaning buy. These searches target buyers who want a fast, chemical-free clean on a budget.",
            "quick_amz_label": "Shop steam mops on Amazon",
            "quick_amz_query": "steam mop under $100",
            "quick_internal_href": "/home-under-100.html",
            "quick_internal_label": "Home under $100",
            "queries": [
                ("steam mop under $100", "The core query."),
                ("steam mop for tile under $100", "Floor-type intent."),
                ("steam mop for hardwood under $100", "Hardwood intent."),
                ("steam mop with detachable handheld under $100", "Feature intent."),
                ("lightweight steam mop under $100", "Ease-of-use intent."),
                ("best steam mop under $100", "Comparison searches."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/stick-vacuum-under-100.html", "Stick vacuums under $100"),
                ("/storage-ottoman-under-100.html", "Storage ottomans under $100"),
                ("/home-under-100.html", "Home under $100"),
                ("/blackout-curtains-under-50.html", "Blackout curtains under $50"),
            ],
        },
        {
            "slug": "space-heater-under-50.html",
            "title": "Best Space Heater Deals Under $50",
            "description": "Space heaters under $50 for bedrooms and offices. Click through to see live prices on Amazon.",
            "intro": "Space heaters have strong seasonal demand and high buyer intent. These searches cover safety features, room size, and quiet operation.",
            "quick_amz_label": "Shop space heaters on Amazon",
            "quick_amz_query": "space heater under $50",
            "quick_internal_href": "/home-under-50.html",
            "quick_internal_label": "Home under $50",
            "queries": [
                ("space heater under $50", "The core query."),
                ("space heater for bedroom under $50", "Bedroom intent."),
                ("quiet space heater under $50", "Noise-sensitive intent."),
                ("space heater with thermostat under $50", "Feature intent."),
                ("ceramic space heater under $50", "Type intent."),
                ("best space heater under $50", "Comparison searches."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/heated-blanket-under-50.html", "Heated blankets under $50"),
                ("/home-under-50.html", "Home under $50"),
                ("/blackout-curtains-under-50.html", "Blackout curtains under $50"),
                ("/desk-lamp-under-30.html", "Desk lamps under $30"),
            ],
        },
        {
            "slug": "air-purifier-filter-under-25.html",
            "title": "Best Air Purifier Filter Deals Under $25",
            "description": "Air purifier filters under $25 (replacement filters). Click through to see live prices on Amazon.",
            "intro": "Replacement filters are a cheap, high-intent add-on. These searches capture buyers who already own a purifier and need a refill.",
            "quick_amz_label": "Shop air purifier filters on Amazon",
            "quick_amz_query": "air purifier filter under $25",
            "quick_internal_href": "/air-purifier-under-100.html",
            "quick_internal_label": "Air purifiers under $100",
            "queries": [
                ("air purifier filter under $25", "The core query."),
                ("hepa filter replacement under $25", "HEPA replacement intent."),
                ("air purifier replacement filter under $25", "Alternate wording."),
                ("air purifier filter for smoke under $25", "Smoke/allergen intent."),
                ("air purifier filter for allergies under $25", "Allergy intent."),
                ("best air purifier filter under $25", "Comparison searches."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/air-purifier-under-100.html", "Air purifiers under $100"),
                ("/home-air-purifier-under-100.html", "Home air purifiers under $100"),
                ("/humidifier-under-50.html", "Humidifiers under $50"),
                ("/dehumidifier-under-100.html", "Dehumidifiers under $100"),
            ],
        },
        {
            "slug": "mattress-protector-under-25.html",
            "title": "Best Mattress Protector Deals Under $25",
            "description": "Mattress protectors under $25 to protect from spills and sweat. Click through to see live prices on Amazon.",
            "intro": "Mattress protectors are cheap add-ons with high conversion. These searches focus on waterproof, cooling, and fit.",
            "quick_amz_label": "Shop mattress protectors on Amazon",
            "quick_amz_query": "mattress protector under $25",
            "quick_internal_href": "/bed-sheets-under-50.html",
            "quick_internal_label": "Bed sheets under $50",
            "queries": [
                ("mattress protector under $25", "The core query."),
                ("waterproof mattress protector under $25", "Waterproof intent."),
                ("cooling mattress protector under $25", "Cooling intent."),
                ("mattress protector queen under $25", "Size intent."),
                ("mattress protector twin under $25", "Size intent."),
                ("best mattress protector under $25", "Comparison searches."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/bed-sheets-under-50.html", "Bed sheets under $50"),
                ("/bed-sheet-set-under-50.html", "Bed sheet sets under $50"),
                ("/mattress-topper-under-100.html", "Mattress toppers under $100"),
                ("/blackout-curtains-under-50.html", "Blackout curtains under $50"),
            ],
        },
        {
            "slug": "pillow-under-25.html",
            "title": "Best Pillow Deals Under $25",
            "description": "Pillows under $25 for sleep upgrades. Click through to see live prices on Amazon.",
            "intro": "Pillows are a frequent, low-friction purchase. These searches cover side sleepers, cooling, and memory foam under $25.",
            "quick_amz_label": "Shop pillows on Amazon",
            "quick_amz_query": "pillow under $25",
            "quick_internal_href": "/home-under-50.html",
            "quick_internal_label": "Home under $50",
            "queries": [
                ("pillow under $25", "The core query."),
                ("memory foam pillow under $25", "Material intent."),
                ("cooling pillow under $25", "Cooling intent."),
                ("pillow for side sleepers under $25", "Sleep position intent."),
                ("pillow for neck pain under $25", "Problem intent."),
                ("best pillow under $25", "Comparison searches."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/bed-sheets-under-50.html", "Bed sheets under $50"),
                ("/blackout-curtains-under-50.html", "Blackout curtains under $50"),
                ("/home-under-50.html", "Home under $50"),
                ("/mattress-topper-under-100.html", "Mattress toppers under $100"),
            ],
        },
        {
            "slug": "closet-organizer-under-50.html",
            "title": "Best Closet Organizer Deals Under $50",
            "description": "Closet organizers under $50 to tidy small spaces. Click through to see live prices on Amazon.",
            "intro": "Closet organizers are a strong home-organization category. These searches cover shelves, hanging organizers, and small closets.",
            "quick_amz_label": "Shop closet organizers on Amazon",
            "quick_amz_query": "closet organizer under $50",
            "quick_internal_href": "/home-under-50.html",
            "quick_internal_label": "Home under $50",
            "queries": [
                ("closet organizer under $50", "The core query."),
                ("hanging closet organizer under $50", "Hanging organizer intent."),
                ("closet shelves under $50", "Shelving intent."),
                ("closet organizer for small closet under $50", "Small-space intent."),
                ("closet storage bins under $50", "Bin intent."),
                ("best closet organizer under $50", "Comparison searches."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/home-under-50.html", "Home under $50"),
                ("/storage-ottoman-under-100.html", "Storage ottomans under $100"),
                ("/desk-lamp-under-30.html", "Desk lamps under $30"),
                ("/blackout-curtains-under-50.html", "Blackout curtains under $50"),
            ],
        },
        {
            "slug": "shower-caddy-under-25.html",
            "title": "Best Shower Caddy Deals Under $25",
            "description": "Shower caddies under $25 for organization. Click through to see live prices on Amazon.",
            "intro": "Shower caddies are cheap, easy conversions. These searches cover rustproof materials, corner caddies, and adhesive mounts.",
            "quick_amz_label": "Shop shower caddies on Amazon",
            "quick_amz_query": "shower caddy under $25",
            "quick_internal_href": "/shower-head-under-50.html",
            "quick_internal_label": "Shower heads under $50",
            "queries": [
                ("shower caddy under $25", "The core query."),
                ("rustproof shower caddy under $25", "Rustproof intent."),
                ("corner shower caddy under $25", "Corner intent."),
                ("adhesive shower caddy under $25", "No-drill intent."),
                ("hanging shower caddy under $25", "Hanging intent."),
                ("best shower caddy under $25", "Comparison searches."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/shower-head-under-50.html", "Shower heads under $50"),
                ("/home-under-50.html", "Home under $50"),
                ("/bed-sheets-under-50.html", "Bed sheets under $50"),
                ("/storage-ottoman-under-100.html", "Storage ottomans under $100"),
            ],
        },
        {
            "slug": "laundry-hamper-under-25.html",
            "title": "Best Laundry Hamper Deals Under $25",
            "description": "Laundry hampers under $25 for bedrooms and dorms. Click through to see live prices on Amazon.",
            "intro": "Laundry hampers are common dorm/bedroom purchases. These searches cover collapsible, rolling, and small-space options under $25.",
            "quick_amz_label": "Shop laundry hampers on Amazon",
            "quick_amz_query": "laundry hamper under $25",
            "quick_internal_href": "/home-under-50.html",
            "quick_internal_label": "Home under $50",
            "queries": [
                ("laundry hamper under $25", "The core query."),
                ("collapsible laundry hamper under $25", "Collapsible intent."),
                ("laundry basket under $25", "Alternate wording."),
                ("laundry hamper with lid under $25", "Feature intent."),
                ("laundry hamper for dorm under $25", "Dorm intent."),
                ("best laundry hamper under $25", "Comparison searches."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/home-under-50.html", "Home under $50"),
                ("/closet-organizer-under-50.html", "Closet organizers under $50"),
                ("/storage-ottoman-under-100.html", "Storage ottomans under $100"),
                ("/desk-lamp-under-30.html", "Desk lamps under $30"),
            ],
        },
        {
            "slug": "shoe-rack-under-50.html",
            "title": "Best Shoe Rack Deals Under $50",
            "description": "Shoe racks under $50 to keep entryways clean. Click through to see live prices on Amazon.",
            "intro": "Shoe racks are a straightforward home-organization buy. These searches cover entryway racks, metal racks, and multi-tier organizers.",
            "quick_amz_label": "Shop shoe racks on Amazon",
            "quick_amz_query": "shoe rack under $50",
            "quick_internal_href": "/home-under-50.html",
            "quick_internal_label": "Home under $50",
            "queries": [
                ("shoe rack under $50", "The core query."),
                ("entryway shoe rack under $50", "Entryway intent."),
                ("shoe organizer under $50", "Alternate wording."),
                ("metal shoe rack under $50", "Material intent."),
                ("shoe rack for small space under $50", "Small-space intent."),
                ("best shoe rack under $50", "Comparison searches."),
            ],
            "related": [
                ("/home-deals.html", "Home deals hub"),
                ("/home-under-50.html", "Home under $50"),
                ("/closet-organizer-under-50.html", "Closet organizers under $50"),
                ("/blackout-curtains-under-50.html", "Blackout curtains under $50"),
                ("/storage-ottoman-under-100.html", "Storage ottomans under $100"),
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
