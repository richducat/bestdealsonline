#!/usr/bin/env python3
"""Generate Pinterest-ready pin images (1000x1500 PNG) for blog articles.

For each blog post, builds a branded vertical card: the article's hero photo
up top, serif headline + call-to-action on cream below, in the site's warm
palette. Renders via headless Chrome into images/pins/<slug>.png.

Pins are the raw material for the free-traffic Pinterest engine described in
GROWTH_PLAYBOOK.md — upload each pin with its article URL as the destination.

Usage: python3 scripts/gen_pins.py [slug ...]   (default: every blog post)
"""

import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images/pins"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1000px; height:1500px; overflow:hidden; }}
body {{ font-family:Inter,-apple-system,sans-serif; background:#FAF5EE; display:flex; flex-direction:column; }}
.photo {{ height:820px; overflow:hidden; position:relative; }}
.photo img {{ width:100%; height:100%; object-fit:cover; }}
.badge {{ position:absolute; top:28px; left:28px; background:rgba(250,245,238,.95); color:#B85C38;
  font-weight:800; font-size:22px; letter-spacing:.18em; text-transform:uppercase; padding:12px 22px; border-radius:999px; }}
.body {{ flex:1; padding:52px 60px 0; display:flex; flex-direction:column; }}
h1 {{ font-family:Georgia,'Times New Roman',serif; font-weight:600; font-size:64px; line-height:1.12; color:#382C22; letter-spacing:-0.01em; }}
.sub {{ margin-top:26px; font-size:30px; line-height:1.45; color:#6B584A; }}
.cta {{ margin-top:auto; margin-bottom:48px; display:flex; align-items:center; gap:18px; }}
.chip {{ width:64px; height:64px; border-radius:50%; background:#B85C38; color:#FAF5EE;
  font-family:Georgia,serif; font-weight:700; font-size:34px; display:flex; align-items:center; justify-content:center; }}
.site {{ font-weight:800; font-size:28px; color:#382C22; }}
.site small {{ display:block; font-weight:700; font-size:18px; color:#B85C38; letter-spacing:.14em; }}
</style></head><body>
<div class="photo"><img src="{img}"><span class="badge">{badge}</span></div>
<div class="body">
  <h1>{title}</h1>
  <div class="sub">{sub}</div>
  <div class="cta"><span class="chip">B</span>
    <span class="site">BestDealsOnline<small>BESTDEALSONLINE.US</small></span></div>
</div></body></html>"""


def pin_for(page: Path):
    h = page.read_text(encoding="utf-8")
    title = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    img = re.search(r'<img src="(/images/(?:topics|hero)/[^"]+)"', h)
    desc = re.search(r'<meta name="description" content="([^"]*)"', h)
    if not title or not img:
        return None
    t = html.unescape(re.sub(r"<[^>]+>", "", title.group(1))).strip()
    # Keep pin headlines punchy: cut trailing colon-clauses beyond ~70 chars.
    if len(t) > 74 and ":" in t:
        t = t.split(":")[0]
    sub = html.unescape(desc.group(1)).strip() if desc else ""
    if len(sub) > 150:
        sub = sub[:147].rsplit(" ", 1)[0] + "…"
    return t, (ROOT / img.group(1).lstrip("/")).as_uri(), sub


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    slugs = sys.argv[1:]
    pages = [ROOT / "blog" / f"{s}.html" for s in slugs] if slugs else sorted((ROOT / "blog").glob("*.html"))
    made = 0
    for page in pages:
        if page.name == "index.html" or not page.exists():
            continue
        info = pin_for(page)
        if not info:
            continue
        t, img_uri, sub = info
        html_doc = TEMPLATE.format(img=img_uri, badge="Buyer research", title=html.escape(t), sub=html.escape(sub))
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
            f.write(html_doc)
            tmp = f.name
        out = OUT / f"{page.stem}.png"
        subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", f"--screenshot={out}",
             "--window-size=1000,1500", "--hide-scrollbars", "--allow-file-access-from-files", f"file://{tmp}"],
            capture_output=True,
        )
        if out.exists() and out.stat().st_size > 30000:
            made += 1
        else:
            print(f"FAILED: {page.stem}")
    print(f"generated {made} pins in images/pins/")


if __name__ == "__main__":
    main()
