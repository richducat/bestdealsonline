#!/usr/bin/env python3
"""Fix accidental backslash-escaped quotes in generated HTML.

Some injected blocks ended up with literal sequences like class=\"...\".
Browsers may still render, but it's sloppy and can cause odd behavior.

Run:
  python3 scripts/unescape_html_attrs.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    changed = 0
    for p in ROOT.glob('*.html'):
        s = p.read_text(errors='ignore')
        if '\\"' not in s:
            continue
        s2 = s.replace('\\"', '"')
        if s2 != s:
            p.write_text(s2, encoding='utf-8')
            changed += 1
    print('fixed', changed, 'files')


if __name__ == '__main__':
    main()
