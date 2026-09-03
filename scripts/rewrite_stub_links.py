#!/usr/bin/env python3
"""Point every internal link at a live page instead of a redirect stub.

After the Jul 28-29 consolidation, 41 real pages (category hubs, guides and
their ItemList JSON-LD) still carried 79 links to stub URLs, so a visitor
clicking a "$50" pill landed on a 200-status "Moved" page that refreshed to a
sibling "Under $25" page, and crawlers spent budget on the hop.

For every non-stub page in the root and blog/:
  * href="/slug.html", href="/slug", href="slug.html" and absolute
    https://bestdealsonline.us/slug(.html) references to a stub are rewritten
    to the stub's refresh target (chains collapsed).
  * "under $N" wording inside a rewritten anchor is updated to the target's
    price band, so the link text matches the page it opens.
  * hub price-pill rows are de-duplicated by target; the surviving pill keeps
    the label that matches the target's band.
  * ItemList JSON-LD blocks are de-duplicated by url and renumbered.

Idempotent. Run from the repo root: python3 scripts/rewrite_stub_links.py
"""
import glob
import json
import re

BASE = "https://bestdealsonline.us"
REFRESH_RE = re.compile(r'content="0;url=([^"]+)"')
BAND_RE = re.compile(r"-(?:under|below)-(\d+)$")


def read(path):
    return open(path, encoding="utf-8", errors="ignore").read()


def band(slug):
    m = BAND_RE.search(slug)
    return m.group(1) if m else None


def build_stub_map():
    stub_target = {}
    for f in glob.glob("*.html"):
        src = read(f)
        if 'http-equiv="refresh"' not in src:
            continue
        m = REFRESH_RE.search(src)
        if not m:
            continue
        t = m.group(1).lstrip("/")
        t = t[:-5] if t.endswith(".html") else t
        stub_target[f[:-5]] = t
    for s, t in list(stub_target.items()):
        seen = {s}
        while t in stub_target and t not in seen:
            seen.add(t)
            t = stub_target[t]
        stub_target[s] = t
    return stub_target


def rewrite_anchor_text(inner, old_band, new_band):
    if old_band and new_band and old_band != new_band:
        inner = re.sub(r"under \$" + re.escape(old_band) + r"\b", "under $" + new_band, inner, flags=re.I)
        inner = re.sub(r"Under \$" + re.escape(old_band) + r"\b", "Under $" + new_band, inner)
    return inner


def main():
    stub_target = build_stub_map()
    if not stub_target:
        print("no stubs found")
        return
    alt = "|".join(re.escape(s) for s in sorted(stub_target, key=len, reverse=True))
    # href forms: /slug.html, /slug, slug.html, https://bestdealsonline.us/slug(.html)
    href_re = re.compile(
        r'(href=["\'])(?:' + re.escape(BASE) + r')?/?(' + alt + r')(?:\.html)?(?=[#?"\'])'
    )
    # full anchors, so the text can follow the href
    anchor_re = re.compile(r"<a\b[^>]*>.*?</a>", re.S)
    abs_re = re.compile(r'(' + re.escape(BASE) + r')/(' + alt + r')(?:\.html)?(?=["\'\s<])')

    pages = [f for f in glob.glob("*.html") + glob.glob("blog/*.html")]
    changed_pages, changed_links = 0, 0

    for f in pages:
        src = read(f)
        if 'http-equiv="refresh"' in src:
            continue
        orig = src

        def fix_anchor(m):
            nonlocal changed_links
            a = m.group(0)
            hm = href_re.search(a)
            if not hm:
                return a
            old = hm.group(2)
            new = stub_target[old]
            a2 = href_re.sub(lambda mm: mm.group(1) + "/" + new + ".html", a, count=1)
            head_end = a2.index(">") + 1
            a2 = a2[:head_end] + rewrite_anchor_text(a2[head_end:], band(old), band(new))
            if a2 != a:
                changed_links += 1
            return a2

        src = anchor_re.sub(fix_anchor, src)

        # absolute references outside anchors (JSON-LD "url"/"item", og tags)
        def fix_abs(m):
            nonlocal changed_links
            changed_links += 1
            return m.group(1) + "/" + stub_target[m.group(2)] + ".html"

        src = abs_re.sub(fix_abs, src)

        # hub price-pill rows: dedupe pills by href, keep the label matching the target band
        pill_row_re = re.compile(r"(<div class='flex flex-wrap gap-1\.5'>)(.*?)(</div>)", re.S)
        pill_re = re.compile(r"<a class='([^']*)' href='([^']*)'>([^<]*)</a>")

        def fix_row(m):
            pills = pill_re.findall(m.group(2))
            if not pills:
                return m.group(0)
            by_href = {}
            for cls, href, label in pills:
                slug = href.lstrip("/")
                slug = slug[:-5] if slug.endswith(".html") else slug
                want = "$" + band(slug) if band(slug) else None
                cur = by_href.get(href)
                if cur is None:
                    by_href[href] = [cls, href, label]
                elif want and label == want and cur[2] != want:
                    by_href[href] = [cls, href, label]
            out = []
            for cls, href, label in by_href.values():
                slug = href.lstrip("/")
                slug = slug[:-5] if slug.endswith(".html") else slug
                want = "$" + band(slug) if band(slug) else None
                if label.startswith("$") and want and label != want:
                    label = want
                out.append(f"<a class='{cls}' href='{href}'>{label}</a>")
            return m.group(1) + "".join(out) + m.group(3)

        src = pill_row_re.sub(fix_row, src)

        # ItemList JSON-LD: dedupe by url and renumber
        def fix_ld(m):
            try:
                data = json.loads(m.group(2))
            except Exception:
                return m.group(0)
            if not (isinstance(data, dict) and data.get("@type") == "ItemList"):
                return m.group(0)
            items, seen = [], set()
            for it in data.get("itemListElement", []):
                key = it.get("url") or it.get("item")
                if key in seen:
                    continue
                seen.add(key)
                items.append(it)
            if len(items) == len(data.get("itemListElement", [])):
                return m.group(0)
            for i, it in enumerate(items, 1):
                it["position"] = i
            data["itemListElement"] = items
            return m.group(1) + "\n" + json.dumps(data, indent=2, ensure_ascii=False) + "\n" + m.group(3)

        src = re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)', fix_ld, src, flags=re.S)

        if src != orig:
            open(f, "w", encoding="utf-8").write(src)
            changed_pages += 1

    print(f"stub map: {len(stub_target)} stubs; rewrote {changed_links} links across {changed_pages} pages")

    # verify: no live page links to a stub any more
    leftovers = []
    for f in pages:
        src = read(f)
        if 'http-equiv="refresh"' in src:
            continue
        for m in href_re.finditer(src):
            leftovers.append((f, m.group(2)))
    print(f"remaining live->stub links: {len(leftovers)}")
    for f, s in leftovers[:20]:
        print("  ", f, "->", s)


if __name__ == "__main__":
    main()
