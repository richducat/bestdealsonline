#!/usr/bin/env python3
"""Rewrite every redirect stub (root *.html containing http-equiv="refresh") into a
minimal, fast, attribution-preserving redirect page.

Why: GitHub Pages cannot send HTTP 301s, so the 755 retired doorway URLs are
served as HTML stubs. The previous stubs loaded Google Fonts, warm-theme.css,
gtag.js and track.js before the meta refresh fired (0.75-1.75 s measured), and
sent a scroll/engagement stream for a page titled "Moved".

Design of the new stub:
- <meta http-equiv="refresh" content="0;url=..."> + rel=canonical first: Google
  treats an instant meta refresh as a permanent redirect; works with JS off.
- One GA4 config call so the session's landing page and referrer are recorded
  on the OLD url (attribution survives), then event_callback or a 450 ms cap
  calls location.replace() to the target, carrying query string and hash along.
- Nothing else is downloaded.

Idempotent. Run from the repo root: python3 scripts/rewrite_redirect_stubs.py
"""
import glob
import html
import re
import sys

GA_ID = "G-6GD5DK8067"
BASE = "https://bestdealsonline.us"

# Same internal/automation detection as scripts/inject-analytics.mjs, so a stub
# hit from the owner's devices or a headless browser is flagged the same way.
INTERNAL = (
    "(function(){try{var A=/HeadlessChrome|Electron|Claude|PhantomJS|Puppeteer|Playwright|Selenium|Cypress|Lighthouse|GTmetrix|crawler|spider|bot/i;"
    "try{if(navigator.webdriver===true||A.test(navigator.userAgent||'')){return {traffic_type:'internal'};}}catch(e){}"
    "var K='bdo.internalTraffic';var q=new URLSearchParams(location.search).get('internal');"
    "if(q==='1'||q==='true'){localStorage.setItem(K,'1');}else if(q==='0'||q==='false'){localStorage.removeItem(K);}"
    "return localStorage.getItem(K)==='1'?{traffic_type:'internal'}:{};}catch(e){return {};}})()"
)

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Moved: {title}</title>
<link rel="canonical" href="{canon}">
<meta http-equiv="refresh" content="0;url={target}">
<script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>
<script>
(function(){{
  var target='{target}';
  var done=false;
  function go(){{ if(done) return; done=true; try{{ location.replace(target+(location.search||'')+(location.hash||'')); }}catch(e){{ location.href=target; }} }}
  window.dataLayer=window.dataLayer||[];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js',new Date());
  var cfg={internal};
  cfg.event_callback=go; cfg.event_timeout=400;
  gtag('config','{ga}',cfg);
  setTimeout(go,450);
}})();
</script>
</head>
<body>
<p>This guide moved to <a href="{target}">{base}{target}</a>.</p>
</body>
</html>
"""

REFRESH_RE = re.compile(r'content="0;url=([^"]+)"')


def read(path):
    return open(path, encoding="utf-8", errors="ignore").read()


def main():
    stubs = []
    for f in sorted(glob.glob("*.html")):
        src = read(f)
        if 'http-equiv="refresh"' not in src:
            continue
        m = REFRESH_RE.search(src)
        if not m:
            print("SKIP (no refresh target):", f)
            continue
        target = m.group(1)
        if not target.startswith("/"):
            target = "/" + target
        if not target.endswith(".html"):
            target += ".html"
        stubs.append((f, target))

    missing = sorted({t for _, t in stubs if not glob.glob(t.lstrip("/"))})
    if missing:
        print("ERROR: refresh targets missing:", missing[:10])
        sys.exit(1)
    chains = [(f, t) for f, t in stubs if 'http-equiv="refresh"' in read(t.lstrip("/"))]
    if chains:
        print("ERROR: stub -> stub chains:", chains[:10])
        sys.exit(1)

    rewritten = 0
    for f, target in stubs:
        slug = target[1:-5].replace("-", " ")
        out = TEMPLATE.format(
            title=html.escape(slug), canon=BASE + target, target=target,
            ga=GA_ID, internal=INTERNAL, base=BASE,
        )
        if read(f) != out:
            open(f, "w", encoding="utf-8").write(out)
            rewritten += 1
    print(f"stubs: {len(stubs)}, rewritten: {rewritten}")


if __name__ == "__main__":
    main()
