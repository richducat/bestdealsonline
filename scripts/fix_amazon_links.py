#!/usr/bin/env python3
"""
Rewrite Amazon search links so the price cap becomes a real Amazon filter
instead of literal search text.

Before: /s?k=mesh%20wifi%20under%20%24100&tag=...
After:  /s?k=mesh+wifi&rh=p_36%3A-10000&tag=...

"under $100" as keyword text returns results up to $699. As rh=p_36 it
returns only items under $100. Verified against live Amazon 2026-07-28.

Usage:  python3 scripts/fix_amazon_links.py [--apply]
Default is a dry run that changes nothing.
"""
import re, sys, pathlib, urllib.parse, json, collections

APPLY = "--apply" in sys.argv
ROOT = pathlib.Path(__file__).resolve().parent.parent

# "under $100" / "under 100" / "below $50" / "less than $25"
PRICE_RE = re.compile(r'\b(?:under|below|less\s+than|upto|up\s+to)\s*\$?\s*(\d{1,5})\b', re.I)
# strip filler that hurts Amazon relevance
NOISE_RE = re.compile(r'\b(best|top|cheap|cheapest|deal|deals|sale|discount|budget)\b', re.I)

LINK_RE = re.compile(r'(https://www\.amazon\.com/s\?)([^"\'\s<>]+)')

stats = collections.Counter()
examples = []

def fix(match):
    prefix, qs = match.group(1), match.group(2)
    qs_clean = qs.replace('&amp;', '&')
    params = urllib.parse.parse_qs(qs_clean, keep_blank_values=True)

    if 'k' not in params:
        stats['skipped_no_k'] += 1
        return match.group(0)
    if 'rh' in params:                       # already filtered — leave alone
        stats['skipped_has_rh'] += 1
        return match.group(0)

    kw = urllib.parse.unquote_plus(params['k'][0])
    original_kw = kw

    m = PRICE_RE.search(kw)
    cap = None
    if m:
        cap = int(m.group(1))
        kw = PRICE_RE.sub('', kw)

    kw = NOISE_RE.sub('', kw)
    kw = re.sub(r'\s+', ' ', kw).strip(' -,')

    if not kw:                               # never emit an empty search
        kw = original_kw.strip()
        cap = cap if cap else None
        stats['kw_fallback'] += 1

    new = dict(params)
    new['k'] = [kw]
    if cap and 0 < cap <= 99999:
        new['rh'] = ['p_36:-%d' % (cap * 100)]
        stats['price_filter_added'] += 1
    else:
        stats['no_price_cap_found'] += 1

    order = ['k', 'rh'] + [p for p in new if p not in ('k', 'rh')]
    out = prefix + '&'.join(
        '%s=%s' % (p, urllib.parse.quote_plus(new[p][0], safe=':-'))
        for p in order if p in new
    )
    stats['rewritten'] += 1
    if len(examples) < 6 and cap:
        examples.append({'before': match.group(0)[:120], 'after': out[:120]})
    return out

files = [p for p in ROOT.rglob('*.html') if '.git' not in p.parts and 'node_modules' not in p.parts]
changed_files = 0
for f in files:
    try:
        src = f.read_text(encoding='utf-8')
    except Exception:
        stats['unreadable'] += 1
        continue
    out = LINK_RE.sub(fix, src)
    if out != src:
        changed_files += 1
        if APPLY:
            f.write_text(out, encoding='utf-8')

print(json.dumps({
    'mode': 'APPLIED' if APPLY else 'DRY RUN (no files changed)',
    'html_files_scanned': len(files),
    'files_that_would_change': changed_files,
    'stats': dict(stats),
    'examples': examples,
}, indent=1))
