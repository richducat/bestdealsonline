# DealTruth Checker — Roadmap

The checker (homepage `#demo` section + standalone `/deal-check.html`) is now the
site's signature tool. Both surfaces run the exact same engine: `app/src/dealtruth.js`
(scoring) wrapped by `app/src/dealcheck-core.js` (verdict tiers, fake-discount
detection, share text, tally). The build copies both into `/assets/` so the static
page imports them as native ESM — one engine, no drift.

## What shipped (v1, fully client-side)

- **Six honest verdict tiers** driving color + headline: Fake discount / Overpriced /
  Everyday price / Small dip / Solid deal / Strong deal / Almost too good. Fixes the
  old contradiction where the demo said "not a deal" and "Buy now" simultaneously.
- **Fake-discount detection**: optional "Amazon's crossed-out was price" input →
  claimed-vs-real bar pair ("The sticker claims 47% · Real drop 4%"). This is the
  shareable lie-detector moment; positioning backed by the 2025 Amazon fake-list-price
  lawsuit news cycle.
- **Animated 0–100 score ring** with count-up reveal (variable-reward loop).
- **120-day example price chart** with usual-price line and today's price dot.
- **Loss-aversion framing**: "You'd overpay $X" / "saves you $X" instead of raw %.
- **Percentile sentence** ("beats N% of the last 6 months") — score semantics anyone
  can repeat to a friend (SeatGeek/AllAboardDeals pattern).
- **Amazon URL paste** → ASIN extraction → deep links to CamelCamelCamel/Keepa for
  verification (borrowed credibility, zero API).
- **localStorage tally**: "N checks run · $X of overpaying dodged" (streak substitute).
- **Copy-verdict share text** with site URL.
- SEO: `/deal-check.html` targets "amazon deal checker / fake discount checker /
  is this a good deal" with WebApplication + FAQPage schema. Research finding: the
  "fake discount checker" query family is ranked by news articles, not tools — a
  functioning tool page can own it.

## Retention hooks not yet built (next, still no backend)

1. **Watchlist**: after a Wait/Everyday verdict, "come back Friday" — store items in
   localStorage with a re-check nudge date; one-tap re-run. (Honey Droplist pattern.)
2. **Share card image**: canvas-render the verdict as a fixed-ratio PNG for the
   "I caught a fake discount" screenshot.
3. **More tool-page variants wrapping the same widget**: `/fake-discount-checker.html`,
   `/buy-now-or-wait.html` — one page per query family (pricehistory.app pattern).
4. **Threshold alerts** (needs email or push): "tell me when this hits $X".

## Extension path (v2)

The whole engine is dependency-free ESM — it drops straight into a Manifest V3
content script. The extension reads the on-page price + list price on any Amazon
product page (DOM read, not scraping via automated sessions — the user is present on
the page they're viewing) and overlays the DealTruth verdict chip. Zero backend.
Distribution insight: pricehistory.app grew on a URL-prefix trick; the extension is
the same convenience one step closer.

Compliance note: keep the extension read-only on pages the user visits; no background
crawling, no automated price polling of Amazon (Associates OA prohibition — same
constraint documented in DEALTRUTH_SETUP.md).

## App path (v3)

Wrap the same engine in an iOS share-sheet extension: user shares an Amazon listing
to the app → verdict screen. Real price history requires the Creators API
(10 sales/30 days gate — see DEALTRUTH_SETUP.md); until then the app is the manual
checker + watchlist + push nudges.

## Real data (the unlock for everything)

`worker/` (D1 + scoring pipeline) is built and verified. Once the Associates account
crosses 10 qualified sales/30 days → Creators API → `VITE_DEALS_API_BASE` flip →
every surface (site cards, checker, extension, app) gets real history instead of
simulated examples. The checker's "example" disclaimers come off at that point.

## Known algorithm quirks (engine, not fixed — demo layer works around them)

- Score spans only ~27–85 across the full input space; "out of 100" is aspirational.
  Verdict tiers now carry the meaning instead of the raw number.
- Monotonicity glitches at extreme low prices (today ≤ $7 on high typical prices
  jumps score 60→85) — cosmetic in the demo range ($5 slider floor).
- Price hikes flatline at ~29 regardless of severity — the Overpriced tier copy
  carries the severity instead.
