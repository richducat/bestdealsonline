#!/usr/bin/env python3
"""Compatibility entry point for the canonical Node sitemap generator."""

from pathlib import Path
import subprocess


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    subprocess.run(["node", "scripts/gen-sitemap.mjs"], cwd=root, check=True)
