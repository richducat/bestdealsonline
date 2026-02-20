#!/usr/bin/env python3
"""Generate ~50 new buyer-intent under-$ pages focused on electronics, kitchen, home, and kids."""

from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.gen_longtail_pages import build_page  # type: ignore


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


DATA: list[dict] = [
    {
        "name": "Tablet Stand",
        "slug_base": "tablet stand",
        "query_base": "tablet stand",
        "description_template": "{name} under ${price} for desks, kitchens, and travel setups. Click through to see live prices on Amazon.",
        "intro_template": "Tablet stands are impulse upgrades for cooking, flights, and video calls. Under ${price} budgets still cover adjustable arms and weighted bases so screens stay steady.",
        "quick_internal_href": "/electronics-under-100.html",
        "quick_internal_label": "Electronics under $100",
        "related": [
            ("/electronics-deals.html", "Electronics deals hub"),
            ("/laptop-stand-under-25.html", "Laptop stands under $25"),
            ("/usb-c-charger-under-50.html", "USB-C chargers under $50"),
        ],
        "features": [
            {"query": "adjustable {base} under ${price}", "desc": "Height and viewing adjustments buyers keep asking for."},
            {"query": "foldable {base} under ${price}", "desc": "Backpack-friendly picks for work and travel."},
            {"query": "{base} with clamp under ${price}", "desc": "Secure mounts for desks and kitchen shelves."},
        ],
        "price_points": [30, 40, 60],
    },
    {
        "name": "USB-C Hub",
        "slug_base": "usb c hub",
        "query_base": "usb c hub",
        "description_template": "{name}s under ${price} for laptops that need more ports. Click through to see live prices on Amazon.",
        "intro_template": "USB-C hubs are quick fixes for single-port laptops. Under ${price}, shoppers still expect HDMI, power passthrough, and reliable build quality.",
        "quick_internal_href": "/electronics-under-100.html",
        "quick_internal_label": "Electronics under $100",
        "related": [
            ("/electronics-deals.html", "Electronics deals hub"),
            ("/usb-c-cable-under-15.html", "USB-C cables under $15"),
            ("/usb-c-charger-under-50.html", "USB-C chargers under $50"),
        ],
        "features": [
            {"query": "{base} with hdmi under ${price}", "desc": "People want dual-monitor support without breaking the budget."},
            {"query": "{base} with ethernet under ${price}", "desc": "Hardwired internet for apartments and dorms."},
            {"query": "powered {base} under ${price}", "desc": "Self-powered hubs for external drives and accessories."},
        ],
        "price_points": [40, 60, 90],
    },
    {
        "name": "Bluetooth Tracker",
        "slug_base": "bluetooth tracker",
        "query_base": "bluetooth tracker",
        "description_template": "{name}s under ${price} for keys, luggage, and pet collars. Click through to see live prices on Amazon.",
        "intro_template": "Bluetooth trackers are cheap insurance for keys and bags. Under ${price} searches focus on battery life, app range, and platform support.",
        "quick_internal_href": "/electronics-under-50.html",
        "quick_internal_label": "Electronics under $50",
        "related": [
            ("/electronics-deals.html", "Electronics deals hub"),
            ("/kids-backpack-under-30.html", "Kids backpacks under $30"),
            ("/power-bank-under-50.html", "Power banks under $50"),
        ],
        "features": [
            {"query": "{base} for keys under ${price}", "desc": "Everyday lost-key intent."},
            {"query": "{base} for luggage under ${price}", "desc": "Travelers want GPS handoff and loud alerts."},
            {"query": "{base} for pets under ${price}", "desc": "Collar clips and waterproof shells."},
        ],
        "price_points": [25, 35, 50],
    },
    {
        "name": "Smart Thermostat",
        "slug_base": "smart thermostat",
        "query_base": "smart thermostat",
        "description_template": "{name}s under ${price} for renters and homeowners who want lower bills. Click through to see live prices on Amazon.",
        "intro_template": "Smart thermostats unlock scheduling and remote control without a pro install. Under ${price}, buyers still expect app control and platform compatibility.",
        "quick_internal_href": "/home-deals.html",
        "quick_internal_label": "Home deals hub",
        "related": [
            ("/home-deals.html", "Home deals hub"),
            ("/smart-plug-under-50.html", "Smart plugs under $50"),
            ("/wifi-router-under-100.html", "Wi-Fi routers under $100"),
        ],
        "features": [
            {"query": "{base} works with alexa under ${price}", "desc": "Voice assistant compatibility remains a top filter."},
            {"query": "{base} with room sensor under ${price}", "desc": "People want remote sensors for hot and cold spots."},
            {"query": "{base} without c wire under ${price}", "desc": "Renters search for adapters or battery-powered installs."},
        ],
        "price_points": [120, 150],
    },
    {
        "name": "Portable SSD",
        "slug_base": "portable ssd",
        "query_base": "portable ssd",
        "description_template": "{name}s under ${price} for faster backups and video work. Click through to see live prices on Amazon.",
        "intro_template": "Portable SSDs are the go-to for creators and commuters. Under ${price} budgets cover 1TB drives, USB-C connectors, and drop protection.",
        "quick_internal_href": "/electronics-under-100.html",
        "quick_internal_label": "Electronics under $100",
        "related": [
            ("/electronics-deals.html", "Electronics deals hub"),
            ("/usb-c-cable-under-15.html", "USB-C cables under $15"),
            ("/power-bank-under-50.html", "Power banks under $50"),
        ],
        "features": [
            {"query": "{base} 1tb under ${price}", "desc": "Capacity-focused searches."},
            {"query": "rugged {base} under ${price}", "desc": "Creators want rubber bumpers and IP ratings."},
            {"query": "{base} for mac under ${price}", "desc": "Compatibility questions for Mac and iPad users."},
        ],
        "price_points": [80, 120, 150],
    },
    {
        "name": "Wi-Fi Range Extender",
        "slug_base": "wifi range extender",
        "query_base": "wifi range extender",
        "description_template": "{name}s under ${price} for dead spots, garages, and basements. Click through to see live prices on Amazon.",
        "intro_template": "Wi-Fi range extenders are quick fixes before investing in full mesh kits. Under ${price}, shoppers still compare ethernet ports, setup ease, and ISP compatibility.",
        "quick_internal_href": "/electronics-under-100.html",
        "quick_internal_label": "Electronics under $100",
        "related": [
            ("/electronics-deals.html", "Electronics deals hub"),
            ("/wifi-router-under-100.html", "Wi-Fi routers under $100"),
            ("/surge-protector-under-25.html", "Surge protectors under $25"),
        ],
        "features": [
            {"query": "{base} with ethernet port under ${price}", "desc": "People want wired backhaul for consoles and TVs."},
            {"query": "{base} for xfinity under ${price}", "desc": "ISP-specific compatibility checks."},
            {"query": "mesh {base} under ${price}", "desc": "Mesh-compatible extenders for multi-story homes."},
        ],
        "price_points": [40, 60, 80],
    },
    {
        "name": "Countertop Ice Maker",
        "slug_base": "countertop ice maker",
        "query_base": "countertop ice maker",
        "description_template": "{name}s under ${price} for kitchens, patios, and RV trips. Click through to see live prices on Amazon.",
        "intro_template": "Countertop ice makers are a summer impulse buy. Under ${price}, shoppers still expect decent output, insulated bins, and easier cleaning cycles.",
        "quick_internal_href": "/kitchen-deals.html",
        "quick_internal_label": "Kitchen deals hub",
        "related": [
            ("/kitchen-deals.html", "Kitchen deals hub"),
            ("/kitchen-under-100.html", "Kitchen under $100"),
            ("/home-under-100.html", "Home under $100"),
        ],
        "features": [
            {"query": "nugget {base} under ${price}", "desc": "Chewable ice obsession shows up in searches."},
            {"query": "self cleaning {base} under ${price}", "desc": "People want less maintenance."},
            {"query": "{base} for rv under ${price}", "desc": "Travelers care about footprint and power draw."},
        ],
        "price_points": [120, 150],
    },
    {
        "name": "Vacuum Sealer",
        "slug_base": "vacuum sealer",
        "query_base": "vacuum sealer",
        "description_template": "{name}s under ${price} for meal prep, bulk shopping, and freezer storage. Click through to see live prices on Amazon.",
        "intro_template": "Vacuum sealers pay for themselves if you freeze leftovers or bulk buys. Under ${price}, shoppers compare starter kits, bag storage, and pulse control.",
        "quick_internal_href": "/kitchen-under-100.html",
        "quick_internal_label": "Kitchen under $100",
        "related": [
            ("/kitchen-deals.html", "Kitchen deals hub"),
            ("/meal-prep-containers-under-25.html", "Meal prep containers under $25"),
            ("/food-scale-under-25.html", "Food scales under $25"),
        ],
        "features": [
            {"query": "{base} with starter kit under ${price}", "desc": "Beginners want rolls and bags included."},
            {"query": "{base} with bag storage under ${price}", "desc": "Countertop organization intent."},
            {"query": "{base} for hunters under ${price}", "desc": "Game processing and bulk meat packaging."},
        ],
        "price_points": [60, 80, 120],
    },
    {
        "name": "Slow Cooker",
        "slug_base": "slow cooker",
        "query_base": "slow cooker",
        "description_template": "{name}s under ${price} for set-it-and-forget-it meals. Click through to see live prices on Amazon.",
        "intro_template": "Slow cookers stay relevant because they simplify weeknight meals. Under ${price}, shoppers still expect programmable timers and easy-clean inserts.",
        "quick_internal_href": "/kitchen-under-100.html",
        "quick_internal_label": "Kitchen under $100",
        "related": [
            ("/kitchen-deals.html", "Kitchen deals hub"),
            ("/meal-prep-containers-under-25.html", "Meal prep containers under $25"),
            ("/nonstick-cookware-under-100.html", "Nonstick cookware under $100"),
        ],
        "features": [
            {"query": "programmable {base} under ${price}", "desc": "Timers and auto-warm modes."},
            {"query": "{base} with sear function under ${price}", "desc": "People want stovetop-safe inserts."},
            {"query": "{base} for meal prep under ${price}", "desc": "Batch cooking intent."},
        ],
        "price_points": [50, 75, 100],
    },
    {
        "name": "Stand Mixer",
        "slug_base": "stand mixer",
        "query_base": "stand mixer",
        "description_template": "{name}s under ${price} for home bakers who need dough power. Click through to see live prices on Amazon.",
        "intro_template": "Stand mixers are splurges, but under ${price} shoppers still compare metal gears, included attachments, and warranty support.",
        "quick_internal_href": "/kitchen-deals.html",
        "quick_internal_label": "Kitchen deals hub",
        "related": [
            ("/kitchen-deals.html", "Kitchen deals hub"),
            ("/kitchen-under-100.html", "Kitchen under $100"),
            ("/bento-lunch-box-under-25.html", "Bento lunch boxes under $25"),
        ],
        "features": [
            {"query": "tilt head {base} under ${price}", "desc": "Home bakers compare tilt-head vs bowl-lift."},
            {"query": "{base} with metal bowl under ${price}", "desc": "Stainless bowls beat plastic in reviews."},
            {"query": "{base} for bread dough under ${price}", "desc": "Kneading power is a top concern."},
        ],
        "price_points": [150, 200],
    },
    {
        "name": "Electric Griddle",
        "slug_base": "electric griddle",
        "query_base": "electric griddle",
        "description_template": "{name}s under ${price} for pancakes, smash burgers, and diner-style breakfasts. Click through to see live prices on Amazon.",
        "intro_template": "Electric griddles replace multiple pans for families. Under ${price}, shoppers still expect even heat, removable grease trays, and nonstick coatings.",
        "quick_internal_href": "/kitchen-under-100.html",
        "quick_internal_label": "Kitchen under $100",
        "related": [
            ("/kitchen-deals.html", "Kitchen deals hub"),
            ("/nonstick-cookware-under-100.html", "Nonstick cookware under $100"),
            ("/coffee-maker-under-100.html", "Coffee makers under $100"),
        ],
        "features": [
            {"query": "large {base} under ${price}", "desc": "Families want bigger cooking surfaces."},
            {"query": "{base} with warming tray under ${price}", "desc": "Buffet-style serving intent."},
            {"query": "ceramic {base} under ${price}", "desc": "Nonstick material preference."},
        ],
        "price_points": [60, 90],
    },
    {
        "name": "Food Processor",
        "slug_base": "food processor",
        "query_base": "food processor",
        "description_template": "{name}s under ${price} for chopping, dough, and meal prep. Click through to see live prices on Amazon.",
        "intro_template": "Food processors cover chopping, shredding, and dough work. Under ${price}, buyers still compare bowl capacity, blades, and dishwasher-safe parts.",
        "quick_internal_href": "/kitchen-under-100.html",
        "quick_internal_label": "Kitchen under $100",
        "related": [
            ("/kitchen-deals.html", "Kitchen deals hub"),
            ("/blender-under-100.html", "Blenders under $100"),
            ("/meal-prep-containers-under-25.html", "Meal prep containers under $25"),
        ],
        "features": [
            {"query": "{base} 12 cup under ${price}", "desc": "Capacity-focused shoppers."},
            {"query": "{base} with dough blade under ${price}", "desc": "Bread and pizza night intent."},
            {"query": "compact {base} under ${price}", "desc": "Small kitchen storage constraints."},
        ],
        "price_points": [80, 120, 150],
    },
    {
        "name": "Electric Pressure Cooker",
        "slug_base": "electric pressure cooker",
        "query_base": "electric pressure cooker",
        "description_template": "{name}s under ${price} for weeknight meals and batch cooking. Click through to see live prices on Amazon.",
        "intro_template": "Electric pressure cookers handle soups, rice, yogurt, and more. Under ${price}, buyers still expect stainless pots, safety valves, and preset programs.",
        "quick_internal_href": "/kitchen-deals.html",
        "quick_internal_label": "Kitchen deals hub",
        "related": [
            ("/kitchen-deals.html", "Kitchen deals hub"),
            ("/rice-cooker-under-100.html", "Rice cookers under $100"),
            ("/air-fryer-under-100.html", "Air fryers under $100"),
        ],
        "features": [
            {"query": "{base} air fryer combo under ${price}", "desc": "Multicooker combo intent."},
            {"query": "{base} 8 quart under ${price}", "desc": "Bigger families want capacity."},
            {"query": "stainless steel {base} under ${price}", "desc": "Pot material preference to avoid coatings."},
        ],
        "price_points": [100, 150],
    },
    {
        "name": "Robot Vacuum",
        "slug_base": "robot vacuum",
        "query_base": "robot vacuum",
        "description_template": "{name}s under ${price} for apartments, pets, and daily maintenance. Click through to see live prices on Amazon.",
        "intro_template": "Robot vacuums are now impulse upgrades thanks to lower prices. Under ${price}, shoppers still compare navigation, pet hair pickup, and battery runtime.",
        "quick_internal_href": "/home-deals.html",
        "quick_internal_label": "Home deals hub",
        "related": [
            ("/home-deals.html", "Home deals hub"),
            ("/pets-deals.html", "Pets deals hub"),
            ("/stick-vacuum-under-100.html", "Stick vacuums under $100"),
        ],
        "features": [
            {"query": "{base} for pet hair under ${price}", "desc": "Pet owners care about brush design."},
            {"query": "self emptying {base} under ${price}", "desc": "Dock convenience intent."},
            {"query": "{base} for carpet under ${price}", "desc": "People need suction that handles rugs."},
        ],
        "price_points": [120, 150],
    },
    {
        "name": "Standing Desk Converter",
        "slug_base": "standing desk converter",
        "query_base": "standing desk converter",
        "description_template": "{name}s under ${price} for turning any surface into a sit-stand workstation. Click through to see live prices on Amazon.",
        "intro_template": "Standing desk converters are the fastest way to upgrade home offices. Under ${price}, shoppers compare dual-monitor support, keyboard trays, and lift smoothness.",
        "quick_internal_href": "/home-deals.html",
        "quick_internal_label": "Home deals hub",
        "related": [
            ("/home-deals.html", "Home deals hub"),
            ("/electronics-deals.html", "Electronics deals hub"),
            ("/desk-lamp-under-50.html", "Desk lamps under $50"),
        ],
        "features": [
            {"query": "{base} dual monitor under ${price}", "desc": "People mention monitor weight limits."},
            {"query": "{base} with keyboard tray under ${price}", "desc": "Ergonomics still matter."},
            {"query": "electric {base} under ${price}", "desc": "Motorized lifts without spending enterprise money."},
        ],
        "price_points": [100, 150],
    },
    {
        "name": "Bathroom Storage Cabinet",
        "slug_base": "bathroom storage cabinet",
        "query_base": "bathroom storage cabinet",
        "description_template": "{name}s under ${price} for renters and small bathrooms. Click through to see live prices on Amazon.",
        "intro_template": "Bathroom storage cabinets help manage toiletries without drilling. Under ${price}, shoppers still expect adjustable shelves and slim footprints.",
        "quick_internal_href": "/home-under-100.html",
        "quick_internal_label": "Home under $100",
        "related": [
            ("/home-deals.html", "Home deals hub"),
            ("/storage-bins-under-50.html", "Storage bins under $50"),
            ("/closet-organizer-under-50.html", "Closet organizers under $50"),
        ],
        "features": [
            {"query": "over the toilet {base} under ${price}", "desc": "Space-saving intent."},
            {"query": "{base} with drawers under ${price}", "desc": "People need hidden storage."},
            {"query": "slim {base} under ${price}", "desc": "Small bathrooms need narrow footprints."},
        ],
        "price_points": [80, 120],
    },
    {
        "name": "Garage Shelving Unit",
        "slug_base": "garage shelving unit",
        "query_base": "garage shelving unit",
        "description_template": "{name}s under ${price} for totes, tools, and seasonal storage. Click through to see live prices on Amazon.",
        "intro_template": "Garage shelving units tame clutter without custom builds. Under ${price}, shoppers still compare weight limits, adjustable shelves, and rust resistance.",
        "quick_internal_href": "/home-deals.html",
        "quick_internal_label": "Home deals hub",
        "related": [
            ("/home-deals.html", "Home deals hub"),
            ("/tool-set-under-100.html", "Tool sets under $100"),
            ("/storage-bins-under-50.html", "Storage bins under $50"),
        ],
        "features": [
            {"query": "heavy duty {base} under ${price}", "desc": "Weight ratings are the first filter."},
            {"query": "{base} with wheels under ${price}", "desc": "Rolling shelves for flexible layouts."},
            {"query": "{base} for totes under ${price}", "desc": "Sized for popular plastic bins."},
        ],
        "price_points": [120, 150],
    },
    {
        "name": "Laundry Drying Rack",
        "slug_base": "laundry drying rack",
        "query_base": "laundry drying rack",
        "description_template": "{name}s under ${price} for delicates, sweaters, and energy savings. Click through to see live prices on Amazon.",
        "intro_template": "Laundry drying racks keep fabrics in better shape. Under ${price}, shoppers compare folding styles, wall mounts, and capacity for sweaters.",
        "quick_internal_href": "/home-under-100.html",
        "quick_internal_label": "Home under $100",
        "related": [
            ("/home-deals.html", "Home deals hub"),
            ("/closet-organizer-under-50.html", "Closet organizers under $50"),
            ("/storage-bins-under-50.html", "Storage bins under $50"),
        ],
        "features": [
            {"query": "folding {base} under ${price}", "desc": "Need easy storage between laundry days."},
            {"query": "wall mounted {base} under ${price}", "desc": "Apartments use wall space instead of floors."},
            {"query": "{base} for sweaters under ${price}", "desc": "Flat drying for delicates."},
        ],
        "price_points": [40, 60],
    },
    {
        "name": "Kids Smartwatch",
        "slug_base": "kids smartwatch",
        "query_base": "kids smartwatch",
        "description_template": "{name}s under ${price} for safety check-ins and kid-friendly games. Click through to see live prices on Amazon.",
        "intro_template": "Kids smartwatches give parents GPS pings without handing over a phone. Under ${price}, buyers still expect call controls, durable bands, and simple apps.",
        "quick_internal_href": "/kids-deals.html",
        "quick_internal_label": "Kids deals hub",
        "related": [
            ("/kids-deals.html", "Kids deals hub"),
            ("/kids-headphones-under-50.html", "Kids headphones under $50"),
            ("/kids-tablet-under-100.html", "Kids tablets under $100"),
        ],
        "features": [
            {"query": "{base} gps under ${price}", "desc": "Parents prioritize location tracking."},
            {"query": "{base} with calling under ${price}", "desc": "Two-way calling is a popular filter."},
            {"query": "waterproof {base} under ${price}", "desc": "Durability for playgrounds and pools."},
        ],
        "price_points": [50, 80],
    },
    {
        "name": "Kids Digital Camera",
        "slug_base": "kids digital camera",
        "query_base": "kids digital camera",
        "description_template": "{name}s under ${price} for road trips and STEM gifts. Click through to see live prices on Amazon.",
        "intro_template": "Kids digital cameras keep screens off phones. Under ${price}, shoppers look for rugged shells, simple menus, and fun filters.",
        "quick_internal_href": "/kids-deals.html",
        "quick_internal_label": "Kids deals hub",
        "related": [
            ("/kids-deals.html", "Kids deals hub"),
            ("/kids-backpack-under-30.html", "Kids backpacks under $30"),
            ("/kids-tablet-under-100.html", "Kids tablets under $100"),
        ],
        "features": [
            {"query": "waterproof {base} under ${price}", "desc": "Parents want drop and splash protection."},
            {"query": "{base} with printer under ${price}", "desc": "Instant-print novelty searches."},
            {"query": "vlogging {base} under ${price}", "desc": "Kids mimic creators and want flip screens."},
        ],
        "price_points": [60, 90],
    },
    {
        "name": "Indoor Climbing Set",
        "slug_base": "indoor climbing set",
        "query_base": "indoor climbing set",
        "description_template": "{name}s under ${price} for toddlers who need energy outlets indoors. Click through to see live prices on Amazon.",
        "intro_template": "Indoor climbing sets keep kids moving when the weather is bad. Under ${price}, parents still expect smooth finishes, foldable frames, and included slides.",
        "quick_internal_href": "/kids-deals.html",
        "quick_internal_label": "Kids deals hub",
        "related": [
            ("/kids-deals.html", "Kids deals hub"),
            ("/learning-toys-under-25.html", "Learning toys under $25"),
            ("/board-games-under-25.html", "Board games under $25"),
        ],
        "features": [
            {"query": "{base} with slide under ${price}", "desc": "Slides add replay value."},
            {"query": "toddler {base} under ${price}", "desc": "Sizing and weight limits for ages 2–5."},
            {"query": "foldable {base} under ${price}", "desc": "Parents want easy storage."},
        ],
        "price_points": [100, 150],
    },
    {
        "name": "Kids Desk",
        "slug_base": "kids desk",
        "query_base": "kids desk",
        "description_template": "{name}s under ${price} for homework corners and art stations. Click through to see live prices on Amazon.",
        "intro_template": "Kids desks carve out homework space even in small rooms. Under ${price}, parents compare storage cubbies, adjustable heights, and matching chairs.",
        "quick_internal_href": "/kids-deals.html",
        "quick_internal_label": "Kids deals hub",
        "related": [
            ("/kids-deals.html", "Kids deals hub"),
            ("/storage-bins-under-50.html", "Storage bins under $50"),
            ("/kids-headphones-under-50.html", "Kids headphones under $50"),
        ],
        "features": [
            {"query": "{base} with chair under ${price}", "desc": "Bundled chair + desk sets are popular."},
            {"query": "{base} with storage under ${price}", "desc": "Parents want cubbies for art supplies."},
            {"query": "adjustable {base} under ${price}", "desc": "Height-adjustable desks grow with kids."},
        ],
        "price_points": [80, 120],
    },
]


def main():
    written = 0
    for entry in DATA:
        name = entry["name"]
        base = entry.get("query_base", entry["slug_base"].lower())
        slug_base = slugify(entry["slug_base"])
        for price in entry["price_points"]:
            slug = f"{slug_base}-under-{price}.html"
            out = ROOT / slug
            if out.exists():
                print("skip existing", slug)
                continue
            title = f"Best {name} Deals Under ${price}"
            description = entry["description_template"].format(price=price, name=name, base=base)
            intro = entry["intro_template"].format(price=price, name=name, base=base)
            quick_amz_label = f"Shop {name} under ${price} on Amazon"
            quick_amz_query = f"{base} under ${price}"
            queries: list[tuple[str, str]] = [
                (f"{base} under ${price}", "Core budget query."),
                (f"best {base} under ${price}", "Comparison shoppers."),
                (f"{base} deals under ${price}", "Deal hunters checking promos."),
            ]
            for feat in entry["features"]:
                q = feat["query"].format(price=price, base=base, name=name)
                queries.append((q, feat["desc"]))
            related = entry["related"]
            html_txt = build_page(
                slug=slug,
                title=title,
                description=description,
                intro=intro,
                quick_amz_label=quick_amz_label,
                quick_amz_query=quick_amz_query,
                quick_internal_href=entry["quick_internal_href"],
                quick_internal_label=entry["quick_internal_label"],
                queries=queries[:6],
                related_links=related,
            )
            out.write_text(html_txt, encoding="utf-8")
            written += 1
            print("wrote", out.relative_to(ROOT))
    print(f"done: wrote {written} pages")


if __name__ == "__main__":
    main()
