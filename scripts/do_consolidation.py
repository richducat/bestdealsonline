#!/usr/bin/env python3
"""Consolidate doorway families -> one canonical page each, with 301s."""
import re, json, pathlib, collections, urllib.parse, html, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUFFIX = re.compile(r'-(under|below)-(\d+)$|-(dorm|travel|small-apartment|black-friday-deals|christmas-deals|cyber-monday-deals|prime-day-deals|deals|gift|gifts)$')
LINK_RE = re.compile(r'https://www\.amazon\.com/s\?[^"\'\s<>]+')

def stem_of(b):
    s = b
    for _ in range(3):
        n = SUFFIX.sub('', s)
        if n == s: break
        s = n
    return s

def band(b):
    m = re.search(r'-(?:under|below)-(\d+)$', b); return int(m.group(1)) if m else None

def paras(src):
    s = re.sub(r'(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>', ' ', src)
    m = re.search(r'(?is)<main[^>]*>(.*?)</main>', s); s = m.group(1) if m else s
    out = []
    for x in re.findall(r'(?is)<p[^>]*>(.*?)</p>', s):
        t = html.unescape(re.sub(r'<[^>]+>', '', x)).strip(); t = re.sub(r'\s+', ' ', t)
        if len(t) > 60 and 'affiliate disclosure' not in t.lower(): out.append(t)
    return out

def shell(src):
    """Reuse the site's own head/nav/footer so the new page matches the design."""
    head = re.search(r'(?is)<head[^>]*>(.*?)</head>', src)
    nav  = re.search(r'(?is)(<nav[^>]*>.*?</nav>)', src)
    foot = re.search(r'(?is)(<footer[^>]*>.*?</footer>)', src)
    return (head.group(1) if head else ''), (nav.group(1) if nav else ''), (foot.group(1) if foot else '')

files = sorted(ROOT.glob('*.html'))
fam = collections.defaultdict(list)
for p in files: fam[stem_of(p.stem)].append(p)
fams = {k: v for k, v in fam.items() if len(v) >= 3}

redirects, made, log = [], 0, []
for stem, pages in sorted(fams.items()):
    src0 = sorted(pages, key=lambda p: (band(p.stem) or 9999))[0].read_text(encoding='utf-8', errors='ignore')
    head, nav, foot = shell(src0)
    title = re.search(r'(?is)<title[^>]*>(.*?)</title>', src0)
    noun = stem.replace('-', ' ')

    seen, sections, links = set(), collections.OrderedDict(), collections.OrderedDict()
    for p in sorted(pages, key=lambda x: (band(x.stem) or 9999, x.stem)):
        s = p.read_text(encoding='utf-8', errors='ignore')
        fresh = [t for t in paras(s) if not (t[:90].lower() in seen or seen.add(t[:90].lower()))]
        b = band(p.stem)
        label = f"Best {noun} under ${b}" if b else f"{noun.title()} buying guide"
        if fresh: sections.setdefault(label, []).extend(fresh)
        for m in LINK_RE.finditer(s): links.setdefault(m.group(0), True)

    body = [f'<h1>Best {noun.title()}: Prices, Picks and What to Look For</h1>']
    for label, ts in sections.items():
        body.append(f'<section><h2>{html.escape(label)}</h2>')
        body += [f'<p>{html.escape(t)}</p>' for t in ts]
        body.append('</section>')
    body.append('<section><h2>Where to buy</h2><ul>')
    body += [f'<li><a href="{html.escape(u)}" rel="nofollow sponsored">Check current {html.escape(noun)} prices on Amazon</a></li>' for u in list(links)[:12]]
    body.append('</ul></section>')

    canon_head = re.sub(r'(?is)<link[^>]+rel=["\']canonical["\'][^>]*>', '', head)
    canon_head = re.sub(r'(?is)<title[^>]*>.*?</title>', f'<title>Best {noun.title()} — Prices &amp; Picks | Best Deals Online</title>', canon_head)
    canon_head += f'\n<link rel="canonical" href="https://bestdealsonline.us/{stem}">'
    page = f'<!DOCTYPE html>\n<html lang="en">\n<head>{canon_head}</head>\n<body>\n{nav}\n<main>\n' + '\n'.join(body) + f'\n</main>\n{foot}\n</body>\n</html>\n'
    (ROOT / f'{stem}.html').write_text(page, encoding='utf-8')
    made += 1

    stub_head = f'<meta charset="utf-8"><meta name="robots" content="noindex,follow"><link rel="canonical" href="https://bestdealsonline.us/{stem}"><meta http-equiv="refresh" content="0;url=/{stem}"><title>Moved</title>'
    for p in pages:
        if p.stem == stem: continue
        redirects.append(f'/{p.stem}\t/{stem}\t301')
        p.write_text(f'<!DOCTYPE html><html lang="en"><head>{stub_head}</head><body><p>This guide moved to <a href="/{stem}">/{stem}</a>.</p></body></html>\n', encoding='utf-8')
    log.append({'family': stem, 'canonical': f'/{stem}', 'redirected': len(pages) - (1 if (ROOT/f'{stem}.html') in pages else 0)})

(ROOT / '_redirects').write_text('\n'.join(redirects) + '\n', encoding='utf-8')

# rebuild sitemap: only live, non-redirected URLs
live = sorted({p.stem for p in ROOT.glob('*.html')} - {r.split('\t')[0].lstrip('/') for r in redirects})
today = datetime.date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sm += [f'<url><loc>https://bestdealsonline.us/{u}</loc><lastmod>{today}</lastmod></url>' for u in live]
sm.append('</urlset>')
(ROOT / 'sitemap.xml').write_text('\n'.join(sm) + '\n', encoding='utf-8')

print(json.dumps({'families_consolidated': made, 'redirect_rules': len(redirects),
                  'urls_in_new_sitemap': len(live), 'sitemap_before': 956}, indent=1))
