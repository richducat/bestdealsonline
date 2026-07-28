#!/usr/bin/env python3
"""Second pass: remove dangling stopwords and residual filler left in k= after
the price phrase was stripped. e.g. 'weighted blanket on' -> 'weighted blanket'."""
import re, sys, pathlib, urllib.parse, json, collections
APPLY = "--apply" in sys.argv
ROOT = pathlib.Path(__file__).resolve().parent.parent
EXTRA = re.compile(r'\b(affordable|great|good|value|nice|quality|awesome|amazing)\b', re.I)
DANGLE = re.compile(r'\b(on|for|the|a|an|of|to|in|with|and|or|at|by)\b\s*$', re.I)
LEAD = re.compile(r'^\s*\b(on|for|the|a|an|of|to|in|with|and|or|at|by)\b\s*', re.I)
LINK_RE = re.compile(r'(https://www\.amazon\.com/s\?)([^"\'\s<>]+)')
stats = collections.Counter(); fixed = []
def fix(m):
    prefix, qs = m.group(1), m.group(2)
    params = urllib.parse.parse_qs(qs.replace('&amp;','&'), keep_blank_values=True)
    if 'k' not in params: return m.group(0)
    kw = orig = urllib.parse.unquote_plus(params['k'][0])
    kw = EXTRA.sub('', kw)
    for _ in range(3):
        kw = DANGLE.sub('', kw.strip()); kw = LEAD.sub('', kw.strip())
    kw = re.sub(r'\s+', ' ', kw).strip(' -,')
    if not kw or kw == orig:
        if not kw: stats['would_empty_kept_original'] += 1
        return m.group(0)
    params['k'] = [kw]; stats['cleaned'] += 1
    if len(fixed) < 8: fixed.append({'from': orig, 'to': kw})
    order = ['k','rh'] + [p for p in params if p not in ('k','rh')]
    return prefix + '&'.join('%s=%s' % (p, urllib.parse.quote_plus(params[p][0], safe=':-'))
                             for p in order if p in params)
n = 0
for f in ROOT.rglob('*.html'):
    if '.git' in f.parts or 'node_modules' in f.parts: continue
    try: s = f.read_text(encoding='utf-8')
    except: continue
    o = LINK_RE.sub(fix, s)
    if o != s:
        n += 1
        if APPLY: f.write_text(o, encoding='utf-8')
print(json.dumps({'mode':'APPLIED' if APPLY else 'DRY RUN','files_changed':n,
                  'stats':dict(stats),'examples':fixed}, indent=1))
