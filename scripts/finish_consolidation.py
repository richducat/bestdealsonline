#!/usr/bin/env python3
"""
Finish the doorway consolidation started in commit 7cca942.

1. Stub the 39 variants the first pass missed. Where a family's designated
   canonical is itself a price variant (e.g. smart-thermostat-under-120),
   create the true stem page (smart-thermostat.html) from its content and
   stub every variant into it.
2. Rewrite every internal link that points at a redirect stub so it points
   at the canonical page directly (351 pages carried 1,086 stub links).

Idempotent. Run from repo root: python3 scripts/finish_consolidation.py
"""
import re
import json
import glob

BASE = "https://bestdealsonline.us"
FAMILY_MAP = "/tmp/family_map.json"


def read(p):
    return open(p, encoding="utf-8", errors="ignore").read()


def is_stub(p):
    try:
        return 'http-equiv="refresh"' in read(p)
    except FileNotFoundError:
        return None


def make_stub(target_slug):
    t = f"/{target_slug}"
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        f'<link rel="canonical" href="{BASE}/{target_slug}">'
        f'<meta http-equiv="refresh" content="0;url={t}">'
        "<title>Moved</title></head><body>"
        f'<p>This guide moved to <a href="{t}">{t}</a>.</p></body></html>'
    )


def fix_head(html, slug):
    url = f"{BASE}/{slug}"
    html = re.sub(r'<link rel="canonical" href="[^"]*"\s*/?>',
                  f'<link rel="canonical" href="{url}">', html)
    html = re.sub(r'(<meta property="og:url" content=")[^"]*(")',
                  lambda m: m.group(1) + url + m.group(2), html)
    items = re.findall(r'"item":\s*"([^"]+)"', html)
    if items:
        html = html.replace(f'"item": "{items[-1]}"', f'"item": "{url}"')
    return html


def main():
    fam = json.load(open(FAMILY_MAP))

    created = stubbed = 0
    for canon, variants in fam.items():
        live = [v for v in variants if is_stub(v + ".html") is False]
        if not live and is_stub(canon + ".html") is not False:
            continue
        if re.search(r"-under-\d+$", canon):
            true_stem = re.sub(r"-under-\d+$", "", canon)
            if not glob.glob(true_stem + ".html"):
                src = canon + ".html" if is_stub(canon + ".html") is False else live[0] + ".html"
                open(true_stem + ".html", "w", encoding="utf-8").write(
                    fix_head(read(src), true_stem))
                created += 1
            for v in {canon, *live}:
                p = v + ".html"
                if is_stub(p) is False:
                    open(p, "w", encoding="utf-8").write(make_stub(true_stem))
                    stubbed += 1
        else:
            for v in live:
                open(v + ".html", "w", encoding="utf-8").write(make_stub(canon))
                stubbed += 1
    print(f"created {created} stem pages, stubbed {stubbed} more variants")

    # map every stub -> its target, then rewrite links sitewide
    stub_target = {}
    for f in glob.glob("*.html"):
        h = read(f)
        if 'http-equiv="refresh"' in h:
            m = re.search(r"url=/([a-z0-9-]+)", h)
            if m:
                stub_target[f[:-5]] = m.group(1)
    # collapse chains (stub -> stub -> real)
    for s, t in list(stub_target.items()):
        seen = {s}
        while t in stub_target and t not in seen:
            seen.add(t)
            t = stub_target[t]
        stub_target[s] = t
    print(f"stub map: {len(stub_target)} redirects")

    pat = re.compile(
        r'href="(/?)(' + "|".join(re.escape(s) for s in stub_target) + r')(\.html)?([#"?])')

    def sub(m):
        return f'href="/{stub_target[m.group(2)]}{m.group(4)}'

    fixed = links = 0
    for f in glob.glob("*.html") + glob.glob("blog/*.html"):
        h = read(f)
        if 'http-equiv="refresh"' in h:
            continue
        n, cnt = pat.subn(sub, h)
        if cnt:
            open(f, "w", encoding="utf-8").write(n)
            fixed += 1
            links += cnt
    print(f"rewrote {links} stub links across {fixed} pages")


if __name__ == "__main__":
    main()
