#!/usr/bin/env python3
"""Inject minimal SVG hero art into pages that use the homepage-style hero.

We keep this Amazon-compliant by using only our own SVG assets.

Run:
  python3 scripts/inject_hero_svgs.py
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

# Detect hero sections and inject a reusable image card.
HERO_CLASS = 'bg-gradient-to-br from-indigo-900 via-blue-900 to-slate-900'

IMG_SNIPPET = (
    "\n        <div class=\"hidden lg:block lg:col-span-4\">\n"
    "          <div class=\"bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm\">\n"
    "            <img src=\"{src}\" width=\"720\" height=\"480\" loading=\"lazy\" decoding=\"async\" alt=\"\" class=\"w-full h-auto opacity-95\" />\n"
    "          </div>\n"
    "        </div>\n"
)


def pick_svg(name: str) -> str:
    n = name.lower()
    if n.endswith('-deals.html'):
        if n.startswith('electronics-'):
            return '/assets/hero/electronics.svg'
        if n.startswith('home-'):
            return '/assets/hero/home.svg'
        if n.startswith('kitchen-'):
            return '/assets/hero/kitchen.svg'
        if n.startswith('tools-'):
            return '/assets/hero/tools.svg'
        return '/assets/hero/default.svg'

    if any(k in n for k in ['wifi','router','dash-cam','projector','headset','keyboard','mouse','charger','usb','hdmi','bluetooth','speaker','webcam','electronics']):
        return '/assets/hero/electronics.svg'
    if any(k in n for k in ['air-fryer','coffee','kettle','rice','cookware','toaster','blender','meal-prep','kitchen']):
        return '/assets/hero/kitchen.svg'
    if any(k in n for k in ['drill','tool','screwdriver','flashlight','impact','socket','wrench','laser-level','tools']):
        return '/assets/hero/tools.svg'
    if any(k in n for k in ['air-purifier','humidifier','dehumidifier','curtains','bed','mattress','vacuum','shower','storage','laundry','pillow','doormat','trash','smoke','leak','home']):
        return '/assets/hero/home.svg'
    return '/assets/hero/default.svg'


def inject(p: Path) -> bool:
    s = p.read_text(errors='ignore')
    if HERO_CLASS not in s:
        return False
    if '/assets/hero/' in s:
        return False

    hero_m = re.search(
        r'(<section class=\"' + re.escape(HERO_CLASS) + r'\">)([\s\S]*?)(</section>)',
        s,
    )
    if not hero_m:
        return False

    hero_open, hero_body, hero_close = hero_m.group(1), hero_m.group(2), hero_m.group(3)
    if '<img ' in hero_body:
        return False

    src = pick_svg(p.name)
    floating_block = (
        "\n      <div class=\"hidden lg:block mt-6\">\n"
        "        <div class=\"max-w-lg ml-auto bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm\">\n"
        f"          <img src=\"{src}\" width=\"720\" height=\"480\" loading=\"lazy\" decoding=\"async\" alt=\"\" class=\"w-full h-auto opacity-95\" />\n"
        "        </div>\n"
        "      </div>\n"
    )

    # If page already uses two-column hero grid, append image in right column.
    if 'lg:col-span-4' in hero_body and '<ul' in hero_body:
        hero_body2 = re.sub(
            r'(</ul>\s*</div>)',
            r"\1\n\n            <div class=\"hidden md:block bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm mt-4\">\n              <img src=\"" + src + r"\" width=\"720\" height=\"480\" loading=\"lazy\" decoding=\"async\" alt=\"\" class=\"w-full h-auto opacity-95\" />\n            </div>",
            hero_body,
            count=1,
            flags=re.S,
        )
        if hero_body2 == hero_body:
            return False
    else:
        # Common single-column hero: append a floating image card before closing section.
        container_close = re.search(r'(</div>\s*)$', hero_body)
        if not container_close:
            return False
        hero_body2 = hero_body[:container_close.start()] + floating_block + hero_body[container_close.start():]

    s2 = s[:hero_m.start(1)] + hero_open + hero_body2 + hero_close + s[hero_m.end(3):]
    p.write_text(s2, encoding='utf-8')
    return True


def main():
    changed = 0
    for p in ROOT.glob('*.html'):
        if inject(p):
            changed += 1
    print('injected hero SVG into', changed, 'pages')


if __name__ == '__main__':
    main()
