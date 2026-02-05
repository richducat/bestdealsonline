#!/usr/bin/env python3
import re
from pathlib import Path

SITE = "https://bestdealsonline.us"

# Replace the entire nav element (some pages may already have been partially transformed)
HEADER_NAV_RE = re.compile(r"<nav class=\"text-sm text-slate-200 flex[^\"]*\">.*?</nav>", re.S)
# Replace footer regardless of quote style
FOOTER_RE = re.compile(r"<footer[^>]*>.*?</footer>", re.S)

NEW_NAV = (
    "<nav class=\"text-sm text-slate-200 flex flex-wrap gap-4\">\n"
    "        <a class=\"hover:text-yellow-400\" href=\"/\">Home</a>\n"
    "        <a class=\"hover:text-yellow-400\" href=\"/best-deals-online-today.html\">Today</a>\n"
    "        <a class=\"hover:text-yellow-400\" href=\"/electronics-deals.html\">Electronics</a>\n"
    "        <a class=\"hover:text-yellow-400\" href=\"/kitchen-deals.html\">Kitchen</a>\n"
    "        <a class=\"hover:text-yellow-400\" href=\"/home-deals.html\">Home</a>\n"
    "        <a class=\"hover:text-yellow-400\" href=\"/tools-deals.html\">Tools</a>\n"
    "        <a class=\"hover:text-yellow-400\" href=\"/kids-deals.html\">Kids</a>\n"
    "        <a class=\"hover:text-yellow-400\" href=\"/beauty-deals.html\">Beauty</a>\n"
    "        <a class=\"hover:text-yellow-400\" href=\"/fitness-deals.html\">Fitness</a>\n"
    "        <a class=\"hover:text-yellow-400\" href=\"/pets-deals.html\">Pets</a>\n"
    "        <a class=\"hover:text-yellow-400\" href=\"/blog/index.html\">Blog</a>\n"
    "        <a class=\"hover:text-yellow-400\" href=\"/drummer-deals.html\">Drummer Deals</a>\n"
    "      </nav>"
)

NEW_FOOTER = (
    "<footer class='border-t border-slate-200'>"
    "<div class='max-w-5xl mx-auto px-4 py-8 text-sm text-slate-500'>"
    "<div class='flex flex-col gap-3'>"
    "<div><strong>Affiliate disclosure:</strong> We may earn a commission when you buy through links on this site, at no extra cost to you. <span class='ml-2'><a class='underline hover:text-slate-900' href='/affiliate-disclosure.html'>Details</a></span><div class='text-xs text-slate-400 mt-1'>As an Amazon Associate, we earn from qualifying purchases.</div></div>"
    "<div class='flex flex-wrap gap-x-4 gap-y-2'>"
    "<a class='hover:text-slate-900' href='/best-deals-online-today.html'>Today</a>"
    "<a class='hover:text-slate-900' href='/electronics-deals.html'>Electronics hub</a>"
    "<a class='hover:text-slate-900' href='/kitchen-deals.html'>Kitchen hub</a>"
    "<a class='hover:text-slate-900' href='/home-deals.html'>Home hub</a>"
    "<a class='hover:text-slate-900' href='/tools-deals.html'>Tools hub</a>"
    "<a class='hover:text-slate-900' href='/kids-deals.html'>Kids hub</a>"
    "<a class='hover:text-slate-900' href='/beauty-deals.html'>Beauty hub</a>"
    "<a class='hover:text-slate-900' href='/fitness-deals.html'>Fitness hub</a>"
    "<a class='hover:text-slate-900' href='/pets-deals.html'>Pets hub</a>"
    "<a class='hover:text-slate-900' href='/blog/index.html'>Blog</a>"
    "<a class='hover:text-slate-900' href='/affiliate-disclosure.html'>Affiliate disclosure</a>"
    "<a class='hover:text-slate-900' href='/privacy.html'>Privacy</a>"
    "</div>"
    "</div></div></footer>"
)

CATEGORY_RULES = {
    "kitchen": {
        "hub": ("/kitchen-deals.html", "Kitchen deals hub"),
        "core": [
            ("/kitchen-under-50.html", "Kitchen under $50"),
            ("/kitchen-under-100.html", "Kitchen under $100"),
            ("/air-fryer-under-100.html", "Air fryers under $100"),
            ("/air-fryer-accessories-under-50.html", "Air fryer accessories under $50"),
            ("/coffee-maker-under-100.html", "Coffee makers under $100"),
            ("/rice-cooker-under-100.html", "Rice cookers under $100"),
            ("/nonstick-cookware-under-100.html", "Nonstick cookware under $100"),
            ("/blender-under-100.html", "Blenders under $100"),
            ("/electric-kettle-under-50.html", "Electric kettles under $50"),
            ("/meal-prep-containers-under-25.html", "Meal prep containers under $25"),
            ("/bento-lunch-box-under-25.html", "Bento lunch boxes under $25"),
            ("/toaster-oven-under-100.html", "Toaster ovens under $100"),
            ("/immersion-blender-under-50.html", "Immersion blenders under $50"),
            ("/food-scale-under-25.html", "Food scales under $25"),
            ("/air-fryer-liners-under-25.html", "Air fryer liners under $25"),
        ],
    },
    "electronics": {
        "hub": ("/electronics-deals.html", "Electronics deals hub"),
        "core": [
            ("/electronics-under-50.html", "Electronics under $50"),
            ("/electronics-under-100.html", "Electronics under $100"),
            ("/wireless-earbuds-under-50.html", "Wireless earbuds under $50"),
            ("/noise-cancelling-headphones-under-100.html", "Noise-cancelling headphones under $100"),
            ("/wifi-router-under-100.html", "Wi‑Fi routers under $100"),
            ("/webcam-under-100.html", "Webcams under $100"),
            ("/mechanical-keyboard-under-100.html", "Mechanical keyboards under $100"),
            ("/power-bank-under-50.html", "Power banks under $50"),
            ("/usb-c-charger-under-50.html", "USB‑C chargers under $50"),
            ("/bluetooth-speaker-under-50.html", "Bluetooth speakers under $50"),
            ("/gaming-mouse-under-50.html", "Gaming mice under $50"),
            ("/usb-microphone-under-100.html", "USB microphones under $100"),
            ("/smart-plug-under-25.html", "Smart plugs under $25"),
            ("/dash-cam-under-100.html", "Dash cams under $100"),
            ("/mini-projector-under-100.html", "Mini projectors under $100"),
            ("/portable-monitor-under-100.html", "Portable monitors under $100"),
            ("/gaming-headset-under-50.html", "Gaming headsets under $50"),
            ("/wireless-mouse-under-25.html", "Wireless mice under $25"),
            ("/phone-tripod-under-25.html", "Phone tripods under $25"),
            ("/security-camera-under-50.html", "Security cameras under $50"),
            ("/video-doorbell-under-100.html", "Video doorbells under $100"),
            ("/surge-protector-under-25.html", "Surge protectors under $25"),
            ("/usb-hub-under-25.html", "USB hubs under $25"),
            ("/wireless-charger-under-25.html", "Wireless chargers under $25"),
            ("/smart-speaker-under-50.html", "Smart speakers under $50"),
            ("/router-mesh-under-100.html", "Mesh Wi‑Fi under $100"),
            ("/wireless-keyboard-under-50.html", "Wireless keyboards under $50"),
            ("/electric-toothbrush-under-25.html", "Electric toothbrushes under $25"),
            ("/smart-light-bulbs-under-25.html", "Smart bulbs under $25"),
            ("/led-strip-lights-under-25.html", "LED strip lights under $25"),
            ("/hdmi-cable-under-15.html", "HDMI cables under $15"),
            ("/usb-c-cable-under-15.html", "USB‑C cables under $15"),
            ("/bluetooth-adapter-under-25.html", "Bluetooth adapters under $25"),
            ("/phone-car-mount-under-20.html", "Phone car mounts under $20"),
            ("/mouse-pad-under-15.html", "Mouse pads under $15"),
            ("/screen-protector-under-15.html", "Screen protectors under $15"),
            ("/laptop-stand-under-25.html", "Laptop stands under $25"),
            ("/cable-management-under-15.html", "Cable management under $15"),
        ],
    },
    "home": {
        "hub": ("/home-deals.html", "Home deals hub"),
        "core": [
            ("/home-under-50.html", "Home under $50"),
            ("/home-under-100.html", "Home under $100"),
            ("/air-purifier-under-100.html", "Air purifiers under $100"),
            ("/home-air-purifier-under-100.html", "Home air purifiers under $100"),
            ("/humidifier-under-50.html", "Humidifiers under $50"),
            ("/blackout-curtains-under-50.html", "Blackout curtains under $50"),
            ("/bed-sheets-under-50.html", "Bed sheets under $50"),
            ("/bed-sheet-set-under-50.html", "Bed sheet sets under $50"),
            ("/shower-head-under-50.html", "Shower heads under $50"),
            ("/led-floor-lamp-under-50.html", "LED floor lamps under $50"),
            ("/storage-ottoman-under-100.html", "Storage ottomans under $100"),
            ("/stick-vacuum-under-100.html", "Stick vacuums under $100"),
            ("/mattress-topper-under-100.html", "Mattress toppers under $100"),
            ("/desk-lamp-under-30.html", "Desk lamps under $30"),
            ("/heated-blanket-under-50.html", "Heated blankets under $50"),
            ("/dehumidifier-under-100.html", "Dehumidifiers under $100"),
            ("/steam-mop-under-100.html", "Steam mops under $100"),
            ("/space-heater-under-50.html", "Space heaters under $50"),
            ("/air-purifier-filter-under-25.html", "Air purifier filters under $25"),
            ("/mattress-protector-under-25.html", "Mattress protectors under $25"),
            ("/pillow-under-25.html", "Pillows under $25"),
            ("/closet-organizer-under-50.html", "Closet organizers under $50"),
            ("/shower-caddy-under-25.html", "Shower caddies under $25"),
            ("/laundry-hamper-under-25.html", "Laundry hampers under $25"),
            ("/shoe-rack-under-50.html", "Shoe racks under $50"),
            ("/smoke-detector-under-25.html", "Smoke detectors under $25"),
            ("/carbon-monoxide-detector-under-25.html", "CO detectors under $25"),
            ("/water-leak-detector-under-50.html", "Water leak detectors under $50"),
            ("/smart-lock-under-100.html", "Smart locks under $100"),
            ("/trash-can-under-50.html", "Trash cans under $50"),
            ("/microfiber-cloths-under-15.html", "Microfiber cloths under $15"),
            ("/storage-bins-under-25.html", "Storage bins under $25"),
            ("/extension-cord-under-15.html", "Extension cords under $15"),
            ("/doormat-under-25.html", "Doormats under $25"),
            ("/shower-curtain-under-25.html", "Shower curtains under $25"),
        ],
    },
    "fitness": {
        "hub": ("/fitness-deals.html", "Fitness deals hub"),
        "core": [
            ("/fitness-tracker-under-50.html", "Fitness trackers under $50"),
            ("/adjustable-dumbbells-under-100.html", "Adjustable dumbbells under $100"),
            ("/kettlebell-under-50.html", "Kettlebells under $50"),
            ("/pull-up-bar-under-50.html", "Pull-up bars under $50"),
            ("/resistance-bands-under-25.html", "Resistance bands under $25"),
            ("/foam-roller-under-25.html", "Foam rollers under $25"),
            ("/yoga-mat-under-25.html", "Yoga mats under $25"),
            ("/yoga-mat-under-30.html", "Yoga mats under $30"),
            ("/massage-gun-under-100.html", "Massage guns under $100"),
            ("/ab-roller-under-25.html", "Ab rollers under $25"),
        ],
    },
    "kids": {
        "hub": ("/kids-deals.html", "Kids deals hub"),
        "core": [
            ("/kids-tablet-under-100.html", "Kids tablets under $100"),
            ("/kids-headphones-under-50.html", "Kids headphones under $50"),
            ("/kids-backpack-under-30.html", "Kids backpacks under $30"),
            ("/kids-water-bottle-under-25.html", "Kids water bottles under $25"),
            ("/toddler-balance-bike-under-100.html", "Toddler balance bikes under $100"),
            ("/car-seat-accessories-under-50.html", "Car seat accessories under $50"),
            ("/board-games-under-25.html", "Board games under $25"),
            ("/learning-toys-under-25.html", "Learning toys under $25"),
            ("/building-block-sets-under-50.html", "Building block sets under $50"),
            ("/kids-scooter-under-100.html", "Kids scooters under $100"),
            ("/science-kits-under-25.html", "Science kits under $25"),
        ],
    },
    "pets": {
        "hub": ("/pets-deals.html", "Pets deals hub"),
        "core": [
            ("/dog-bed-under-50.html", "Dog beds under $50"),
            ("/dog-grooming-kit-under-50.html", "Dog grooming kits under $50"),
            ("/pet-grooming-brush-under-25.html", "Pet grooming brushes under $25"),
            ("/pet-water-fountain-under-50.html", "Pet water fountains under $50"),
            ("/pet-car-seat-cover-under-50.html", "Pet car seat covers under $50"),
            ("/cat-litter-box-under-50.html", "Cat litter boxes under $50"),
            ("/cat-litter-mat-under-25.html", "Cat litter mats under $25"),
            ("/cat-tree-under-100.html", "Cat trees under $100"),
            ("/interactive-cat-toy-under-25.html", "Interactive cat toys under $25"),
            ("/dog-toys-under-25.html", "Dog toys under $25"),
            ("/pet-nail-grinder-under-30.html", "Pet nail grinders under $30"),
        ],
    },
    "tools": {
        "hub": ("/tools-deals.html", "Tools deals hub"),
        "core": [
            ("/tool-box-under-50.html", "Tool boxes under $50"),
            ("/toolbox-under-50.html", "Toolbox deals under $50"),
            ("/tool-set-under-100.html", "Tool sets under $100"),
            ("/cordless-drill-under-100.html", "Cordless drills under $100"),
            ("/impact-driver-under-100.html", "Impact drivers under $100"),
            ("/oscillating-multi-tool-under-100.html", "Oscillating multi-tools under $100"),
            ("/socket-set-under-50.html", "Socket sets under $50"),
            ("/torque-wrench-under-100.html", "Torque wrenches under $100"),
            ("/tape-measure-under-25.html", "Tape measures under $25"),
            ("/flashlight-under-50.html", "Flashlights under $50"),
            ("/cordless-screwdriver-under-50.html", "Cordless screwdrivers under $50"),
            ("/laser-level-under-100.html", "Laser levels under $100"),
            ("/electric-screwdriver-under-50.html", "Electric screwdrivers under $50"),
        ],
    },
    "beauty": {
        "hub": ("/beauty-deals.html", "Beauty deals hub"),
        "core": [
            ("/skincare-under-25.html", "Skincare under $25"),
            ("/retinol-serum-under-25.html", "Retinol serums under $25"),
            ("/vitamin-c-serum-under-25.html", "Vitamin C serums under $25"),
            ("/skincare-fridge-under-50.html", "Skincare fridges under $50"),
            ("/electric-toothbrush-under-50.html", "Electric toothbrushes under $50"),
            ("/blow-dryer-under-50.html", "Blow dryers under $50"),
            ("/hair-dryer-under-50.html", "Hair dryers under $50"),
            ("/flat-iron-under-50.html", "Flat irons under $50"),
            ("/makeup-brush-set-under-25.html", "Makeup brush sets under $25"),
            ("/makeup-organizer-under-25.html", "Makeup organizers under $25"),
            ("/niacinamide-serum-under-25.html", "Niacinamide serums under $25"),
            ("/sunscreen-under-25.html", "Sunscreens under $25"),
        ],
    },
    "drummer": {
        "hub": ("/drummer-deals.html", "Drummer deals hub"),
        "core": [("/", "Homepage")],
    },
}


def detect_category(filename: str) -> str:
    f = filename
    if f.endswith("-deals.html"):
        # hub pages are their own category
        if f.startswith("kitchen-"):
            return "kitchen"
        if f.startswith("electronics-"):
            return "electronics"
        if f.startswith("home-"):
            return "home"
        if f.startswith("fitness-"):
            return "fitness"
        if f.startswith("kids-"):
            return "kids"
        if f.startswith("pets-"):
            return "pets"
        if f.startswith("tools-"):
            return "tools"
        if f.startswith("beauty-"):
            return "beauty"
        if f.startswith("drummer-"):
            return "drummer"
    # simple keyword rules
    if any(k in f for k in ["air-fryer", "blender", "coffee-maker", "rice-cooker", "nonstick-cookware", "meal-prep", "bento", "electric-kettle", "toaster-oven", "immersion-blender", "food-scale", "air-fryer-liners"]):
        return "kitchen"
    if any(k in f for k in ["wireless-earbuds", "headphones", "wifi-router", "webcam", "mechanical-keyboard", "power-bank", "usb-c-charger", "bluetooth-speaker", "gaming-mouse", "usb-microphone", "smart-plug", "electronics-", "dash-cam", "projector", "portable-monitor", "gaming-headset", "wireless-mouse", "phone-tripod", "security-camera", "video-doorbell", "surge-protector", "usb-hub", "wireless-charger", "smart-speaker", "router-mesh", "wireless-keyboard", "electric-toothbrush-under-25", "smart-light-bulbs", "led-strip-lights", "hdmi-cable", "usb-c-cable", "bluetooth-adapter", "phone-car-mount", "mouse-pad", "screen-protector", "laptop-stand", "cable-management"]):
        return "electronics"
    if any(k in f for k in ["air-purifier", "humidifier", "blackout-curtains", "bed-sheet", "bed-sheets", "shower-head", "led-floor-lamp", "storage-ottoman", "stick-vacuum", "mattress-topper", "desk-lamp", "home-", "heated-blanket", "dehumidifier", "steam-mop", "space-heater", "air-purifier-filter", "mattress-protector", "pillow-under-25", "closet-organizer", "shower-caddy", "laundry-hamper", "shoe-rack", "smoke-detector", "carbon-monoxide-detector", "water-leak-detector", "smart-lock", "trash-can", "microfiber-cloths", "storage-bins", "extension-cord", "doormat", "shower-curtain"]):
        return "home"
    if any(k in f for k in ["dumbbells", "kettlebell", "pull-up", "resistance-bands", "foam-roller", "yoga-mat", "fitness-tracker", "massage-gun", "ab-roller", "fitness-"]):
        return "fitness"
    if any(k in f for k in ["kids-", "toddler-", "car-seat", "board-games", "learning-toys", "building-block", "kids-scooter", "science-kits"]):
        return "kids"
    if any(k in f for k in ["cat-", "dog-", "pet-", "pets-", "interactive-cat", "dog-toys", "pet-nail-grinder"]):
        return "pets"
    if any(k in f for k in ["tool", "cordless-drill", "impact-driver", "oscillating-multi-tool", "socket-set", "torque-wrench", "tape-measure", "flashlight", "cordless-screwdriver", "laser-level", "tools-", "electric-screwdriver"]):
        return "tools"
    if any(k in f for k in ["skincare", "retinol", "vitamin-c", "makeup", "blow-dryer", "hair-dryer", "flat-iron", "electric-toothbrush", "niacinamide-serum", "sunscreen", "beauty-"]):
        return "beauty"
    if "drummer" in f:
        return "drummer"
    return "home"


def build_related_section(category: str, filename: str) -> str:
    rules = CATEGORY_RULES[category]
    hub_href, hub_label = rules["hub"]
    candidates = [rules["hub"]] + rules["core"]

    # remove self
    self_href = f"/{filename}"
    candidates = [c for c in candidates if c[0] != self_href]

    # deterministic-ish selection for variety
    # rotate based on filename hash
    h = sum(ord(ch) for ch in filename)
    core = candidates[1:]
    start = h % max(1, len(core))
    rotated = core[start:] + core[:start]

    # pick 6 incl hub
    picked = [candidates[0]] + rotated[:5]

    links_html = "\n".join(
        [
            f"<a class='px-3 py-1.5 rounded-full border border-slate-200 bg-white hover:bg-slate-50' href='{href}'>{label}</a>"
            for href, label in picked
        ]
    )

    return (
        "<section class='mt-12'>\n"
        "<h2 class='text-xl font-extrabold mb-3'>Related pages</h2>\n"
        "<div class='flex flex-wrap gap-2 text-sm'>\n"
        f"{links_html}\n"
        "</div></section>"
    )


def main():
    root = Path(__file__).resolve().parents[1]
    html_files = sorted([p for p in root.glob("*.html") if p.name != "index.html"])

    for p in html_files:
        s = p.read_text(encoding="utf-8")

        # header nav (normalize to a single nav block)
        s2 = HEADER_NAV_RE.sub(NEW_NAV, s, count=1)
        # footer
        s2 = FOOTER_RE.sub(NEW_FOOTER, s2, count=1)

        # clean up any leftover duplicate closing </nav> tags from earlier transforms
        s2 = re.sub(r"(</nav>\s*){2,}", "</nav>\n", s2)

        # related section
        cat = detect_category(p.name)
        rel = build_related_section(cat, p.name)
        # replace existing related section (first occurrence)
        s2 = re.sub(r"<section class='mt-12'>.*?</section>", rel, s2, count=1, flags=re.S)

        if s2 != s:
            p.write_text(s2, encoding="utf-8")

    # index.html: update header/footer only
    idx = root / "index.html"
    if idx.exists():
        s = idx.read_text(encoding="utf-8")
        s2 = HEADER_NAV_RE.sub(NEW_NAV, s, count=1)
        s2 = FOOTER_RE.sub(NEW_FOOTER, s2, count=1)
        s2 = re.sub(r"(</nav>\s*){2,}", "</nav>\n", s2)
        if s2 != s:
            idx.write_text(s2, encoding="utf-8")


if __name__ == "__main__":
    main()
