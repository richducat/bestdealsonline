#!/usr/bin/env python3
"""Enrich data/products.json with diverse product images.

Strategy:
1) Try Amazon search result image (m.media-amazon.com) from affiliate query.
2) Fallback to Wikimedia Commons free-stock image search.
3) Final fallback to local category image.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote_plus, urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_PATH = ROOT / "data" / "products.json"
CACHE_PATH = ROOT / "data" / "image_lookup_cache.json"

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

CATEGORY_FALLBACKS = {
    "Electronics": "/images/categories/electronics.webp",
    "Home": "/images/categories/home.webp",
    "Kitchen": "/images/categories/kitchen.webp",
    "Tools": "/images/categories/tools.webp",
    "Kids": "/images/categories/kids.webp",
    "Beauty": "/images/categories/beauty.webp",
    "Fitness": "/images/categories/fitness.webp",
    "Pets": "/images/categories/pets.webp",
}

# Parse visible search product images (these are the same URLs Amazon renders in results).
AMAZON_S_IMAGE_RE = re.compile(
    r'<img[^>]+class=\"[^\"]*s-image[^\"]*\"[^>]+src=\"([^\"]+)\"',
    re.IGNORECASE,
)

AMAZON_AC_JPG_RE = re.compile(
    r"^https://m\.media-amazon\.com/images/I/[A-Za-z0-9%+._,-]+\.jpg$",
    re.IGNORECASE,
)

WIKI_BAD_TITLE_TERMS = {
    "station",
    "train",
    "bus",
    "tram",
    "map",
    "logo",
    "diagram",
    "screenshot",
    "poster",
    "banner",
    "wallpaper",
}


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def item_query(item: dict[str, Any]) -> str:
    link = str(item.get("affiliateLink") or "")
    if link:
        try:
            parsed = urlparse(link)
            q = parse_qs(parsed.query).get("k", [""])[0].strip()
            if q:
                return q.replace("+", " ")
        except Exception:
            pass
    return str(item.get("title") or "").strip()


def normalize_amazon_image(url: str) -> str:
    # Upscale common Amazon search image variants to a larger render target.
    return re.sub(r"\._AC_[^./]+\.jpg$", "._AC_SL1200_.jpg", url, flags=re.IGNORECASE)


def stable_pick(values: list[str], seed: str, top_n: int = 6) -> str:
    if not values:
        return ""
    subset = values[:top_n] if len(values) > top_n else values
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    idx = int(digest[:8], 16) % len(subset)
    return subset[idx]


def fetch_text(url: str, *, timeout: float = 6.0) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "ignore")


def fetch_json(url: str, *, timeout: float = 6.0) -> dict[str, Any]:
    raw = fetch_text(url, timeout=timeout)
    return json.loads(raw)


def amazon_search_image(query: str, *, timeout: float = 6.0) -> str | None:
    try:
        url = f"https://www.amazon.com/s?{urlencode({'k': query})}"
        html = fetch_text(url, timeout=timeout)
    except (HTTPError, URLError, TimeoutError):
        return None
    except Exception:
        return None

    if "captcha" in html.lower():
        return None

    candidates: list[str] = []
    seen = set()
    for src in AMAZON_S_IMAGE_RE.findall(html):
        if not AMAZON_AC_JPG_RE.match(src):
            continue
        normalized = normalize_amazon_image(src)
        if normalized in seen:
            continue
        seen.add(normalized)
        candidates.append(normalized)

    if not candidates:
        return None

    return stable_pick(candidates, seed=query, top_n=8)


def wikimedia_stock_image(query: str, category: str, *, timeout: float = 6.0) -> str | None:
    search_term = f"{query} {category}".strip()
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": search_term,
        "gsrnamespace": "6",
        "gsrlimit": "12",
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": "900",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urlencode(params, quote_via=quote_plus)

    try:
        payload = fetch_json(url, timeout=timeout)
    except Exception:
        return None

    pages = (payload.get("query") or {}).get("pages") or {}
    if not pages:
        return None

    query_tokens = [t.lower() for t in re.findall(r"[a-z0-9]+", query) if len(t) > 2]
    category_tokens = [t.lower() for t in re.findall(r"[a-z0-9]+", category)]

    best_url = None
    best_score = -10_000

    for page in pages.values():
        title = str(page.get("title") or "").lower()
        info = (page.get("imageinfo") or [{}])[0]
        thumb = info.get("thumburl") or info.get("url")
        if not thumb:
            continue

        score = 0
        for t in query_tokens[:5]:
            if t in title:
                score += 3
        for t in category_tokens:
            if t in title:
                score += 1
        for bad in WIKI_BAD_TITLE_TERMS:
            if bad in title:
                score -= 8

        if score > best_score:
            best_score = score
            best_url = str(thumb)

    if best_url:
        return best_url
    return None


def main() -> None:
    data = read_json(PRODUCTS_PATH, {})
    items = data.get("items")
    if not isinstance(items, list):
        raise SystemExit("data/products.json missing items[]")

    cache = read_json(CACHE_PATH, {})
    if not isinstance(cache, dict):
        cache = {}

    amazon_count = 0
    wiki_count = 0
    category_count = 0
    reused_count = 0
    updated = 0
    amazon_enabled = True
    amazon_fail_streak = 0

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue

        query = item_query(item)
        category = str(item.get("category") or "").strip() or "Home"
        if not query:
            query = str(item.get("title") or category)

        cache_key = f"{query.lower()}::{category.lower()}"
        cached = cache.get(cache_key)

        if isinstance(cached, dict) and cached.get("imageUrl"):
            chosen_url = str(cached["imageUrl"])
            chosen_source = str(cached.get("imageSource") or "cache")
            reused_count += 1
        else:
            chosen_url = ""
            if amazon_enabled:
                chosen_url = amazon_search_image(query, timeout=5.0) or ""
            if chosen_url:
                chosen_source = "amazon-search"
                amazon_count += 1
                amazon_fail_streak = 0
            else:
                if amazon_enabled:
                    amazon_fail_streak += 1
                    if amazon_fail_streak >= 12:
                        amazon_enabled = False
                        print("amazon search appears throttled; switching to stock fallback", flush=True)

                chosen_url = wikimedia_stock_image(query, category, timeout=5.0) or ""
                if chosen_url:
                    chosen_source = "wikimedia-commons"
                    wiki_count += 1
                else:
                    chosen_url = CATEGORY_FALLBACKS.get(category, "/images/categories/home.webp")
                    chosen_source = "category-fallback"
                    category_count += 1

            cache[cache_key] = {"imageUrl": chosen_url, "imageSource": chosen_source}
            # Gentle pacing to reduce Amazon throttling.
            time.sleep(0.28)

        if item.get("imageUrl") != chosen_url or item.get("imageSource") != chosen_source:
            item["imageUrl"] = chosen_url
            item["imageSource"] = chosen_source
            updated += 1

        if (i + 1) % 25 == 0:
            print(f"processed {i+1}/{len(items)}", flush=True)
            write_json(CACHE_PATH, cache)
            write_json(PRODUCTS_PATH, data)

    data["generatedAt"] = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    write_json(PRODUCTS_PATH, data)
    write_json(CACHE_PATH, cache)

    print("done")
    print(
        json.dumps(
            {
                "items": len(items),
                "updated": updated,
                "amazon": amazon_count,
                "wikimedia": wiki_count,
                "categoryFallback": category_count,
                "cacheReused": reused_count,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
