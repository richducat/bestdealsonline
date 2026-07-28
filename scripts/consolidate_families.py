#!/usr/bin/env python3
"""
Consolidate doorway-page families into one canonical guide each.

For each family (e.g. air-fryer-under-25/30/50/75/100 + seasonal variants):
  - pick a canonical URL (shortest, cleanest stem)
  - merge the UNIQUE body content from every sibling into price-band sections
  - collect the union of Amazon links, deduped, keeping the price filters
  - emit 301 rules into _redirects for every sibling -> canonical

Existing copy is reused, not regenerated. Nothing is deleted; siblings stay on
disk until the redirects are verified live.

Usage: python3 scripts/consolidate_families.py [--apply] [--limit N] [--only STEM]
"""
import re, sys, json, pathlib, collections, urllib.parse, html

APPLY  = "--apply" in sys.argv
LIMIT  = int(sys.argv[sys.argv.index("--limit")+1]) if "--limit" in sys.argv else None
ONLY   = sys.argv[sys.argv.index("--only")+1] if "--only" in sys.argv else None
ROOT   = pathlib.Path(__file__).resolve().parent.parent
OUT    = ROOT / "_consolidated"

SUFFIX = re.compile(r'-(under|below)-(\d+)$|-(dorm|travel|small-apartment|black-friday-deals|christmas-deals|cyber-monday-deals|prime-day-deals|deals|gift|gifts)$')
LINK_RE= re.compile(r'https://www\.amazon\.com/s\?([^"\'\s<>]+)')

def stem_of(base):
    s = base
    for _ in range(3):
        n = SUFFIX.sub('', s)
        if n == s: break
        s = n
    return s

def band_of(base):
    m = re.search(r'-(?:under|below)-(\d+)$', base)
    return int(m.group(1)) if m else None

def variant_of(base):
    m = re.search(r'-((?:dorm|travel|small-apartment|black-friday-deals|christmas-deals|cyber-monday-deals|prime-day-deals))$', base)
    return m.group(1) if m else None

def main_text(src):
    """Body prose with nav/footer/script stripped, as plain paragraphs."""
    body = re.sub(r'(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>', ' ', src)
    m = re.search(r'(?is)<main[^>]*>(.*?)</main>', body)
    if m: body = m.group(1)
    paras = re.findall(r'(?is)<p[^>]*>(.*?)</p>', body)
    out = []
    for p in paras:
        t = html.unescape(re.sub(r'<[^>]+>', '', p)).strip()
        t = re.sub(r'\s+', ' ', t)
        if len(t) > 60 and 'affiliate disclosure' not in t.lower():
            out.append(t)
    return out

def title_of(src):
    m = re.search(r'(?is)<title[^>]*>(.*?)</title>', src)
    return html.unescape(m.group(1)).strip() if m else ''

files = sorted(p for p in ROOT.glob('*.html'))
fam = collections.defaultdict(list)
for p in files:
    fam[stem_of(p.stem)].append(p)
fams = {k: v for k, v in fam.items() if len(v) >= 3}
if ONLY:  fams = {k: v for k, v in fams.items() if k == ONLY}
if LIMIT: fams = dict(sorted(fams.items(), key=lambda kv: -len(kv[1]))[:LIMIT])

report, redirects = [], []
OUT.mkdir(exist_ok=True)

for stem, pages in sorted(fams.items()):
    canon = min(pages, key=lambda p: (len(p.stem), p.stem))
    sibs  = [p for p in pages if p != canon]

    seen, bands, links, para_count = set(), {}, {}, 0
    for p in sorted(pages, key=lambda x: (band_of(x.stem) or 9999, x.stem)):
        src = p.read_text(encoding='utf-8', errors='ignore')
        fresh = []
        for t in main_text(src):
            key = t[:90].lower()
            if key in seen: continue
            seen.add(key); fresh.append(t); para_count += 1
        label = (f"Under ${band_of(p.stem)}" if band_of(p.stem)
                 else (variant_of(p.stem) or 'Overview').replace('-', ' ').title())
        if fresh: bands.setdefault(label, []).extend(fresh)
        for m in LINK_RE.finditer(src):
            q = urllib.parse.parse_qs(m.group(1).replace('&amp;', '&'))
            k = urllib.parse.unquote_plus(q.get('k', [''])[0])
            if k: links.setdefault((k, q.get('rh', [''])[0]), m.group(0))

    words = sum(len(t.split()) for v in bands.values() for t in v)
    report.append({
        'family': stem, 'pages': len(pages), 'canonical': canon.name,
        'redirected': len(sibs), 'sections': list(bands.keys()),
        'unique_paragraphs': para_count, 'merged_words': words,
        'unique_amazon_links': len(links),
        'meets_1200_gate': words >= 1200,
    })
    for s in sibs:
        redirects.append(f"/{s.stem}  /{canon.stem}  301")

    if APPLY:
        payload = {'stem': stem, 'canonical': canon.name, 'title': title_of(canon.read_text(encoding='utf-8', errors='ignore')),
                   'sections': bands, 'links': [{'k': k, 'rh': rh, 'url': u} for (k, rh), u in links.items()],
                   'redirect_from': [s.name for s in sibs]}
        (OUT / f'{stem}.json').write_text(json.dumps(payload, indent=1), encoding='utf-8')

tot_pages = sum(f['pages'] for f in report)
print(json.dumps({
    'mode': 'APPLIED (merge payloads written to _consolidated/)' if APPLY else 'DRY RUN',
    'families': len(report),
    'pages_in_families': tot_pages,
    'canonical_kept': len(report),
    'to_redirect': tot_pages - len(report),
    'families_meeting_1200_word_gate': sum(1 for f in report if f['meets_1200_gate']),
    'median_merged_words': sorted(f['merged_words'] for f in report)[len(report)//2] if report else 0,
    'sample': report[:4],
}, indent=1))
if APPLY and redirects:
    (OUT / '_redirects.partial').write_text('\n'.join(redirects) + '\n', encoding='utf-8')
    print(f"\nwrote {len(redirects)} redirect rules -> _consolidated/_redirects.partial")
