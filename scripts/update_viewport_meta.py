#!/usr/bin/env python3
"""Normalize viewport meta across static pages.

User request: prevent mobile zoom breaking layout.
NOTE: user-scalable=no can reduce accessibility; applied per user request.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

# Replace any viewport meta with our normalized content
VIEWPORT_RE = re.compile(r"<meta\s+name=\"viewport\"\s+content=\"[^\"]*\"\s*/?>", re.I)
NEW = '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />'


def update_file(p: Path) -> bool:
    s = p.read_text(errors="ignore")
    if "name=\"viewport\"" not in s.lower():
        return False
    s2, n = VIEWPORT_RE.subn(NEW, s, count=1)
    if n and s2 != s:
        p.write_text(s2)
        return True
    return False


def main():
    changed = 0
    for p in ROOT.rglob("*.html"):
        # Skip very common vendor dirs if they exist
        if "node_modules" in p.parts:
            continue
        if update_file(p):
            changed += 1
    print(f"updated viewport meta in {changed} files")


if __name__ == "__main__":
    main()
