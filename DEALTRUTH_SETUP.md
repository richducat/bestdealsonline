# DealTruth Setup

DealTruth is the site's price-history/discount-detection engine: instead of
showing a star rating, it scores each product on real discount vs. its
90-day median price, how rare that price is over 180 days, and gives a
"buy now vs. wait" call with a 7-day drop probability. This is the
legitimate version of "find the real deal" -- see the note on Amazon's
own per-user dynamic pricing below for why that's the version worth
building.

**Status as of this doc: the full pipeline (schema, ingest, scoring, API,
frontend) is built and verified working end-to-end locally.** The only
missing piece is a live Amazon price feed, which is blocked on an
eligibility requirement explained below -- not on anything left to build.

## Live Card Output (when connected)
- `DealTruth Score: X/100`
- `Real discount: X% below 90-day median`
- `Rarity: lowest price in 180 days` (or similar)
- `Confidence: High/Medium/Low (...)`
- `Buy now` / `Wait` / `Either` with a 7-day drop-chance percentage
- Cards where `notMeaningfulDeal` is true are excluded from "Today's Picks" entirely rather than shown with a bad score

## The Amazon data-access blocker (read this first)

Amazon's old Product Advertising API (PA-API) stopped accepting new
signups and fully retires May 15, 2026. Its replacement, the **Creators
API**, requires the Associates account to have **10 qualified sales in
the trailing 30 days** just to get access -- and access is suspended
again if sales drop below that in any rolling 30-day window.

That means: real price data requires real sales volume first. This is
also why the site does not and should not attempt to scrape Amazon or
use bots to check prices -- both violate the Associates Operating
Agreement (explicit prohibition on automated sessions/traffic) and
neither would work anyway, since any per-user price personalization
Amazon might do happens inside a shopper's own account, not something a
third-party site can trigger.

**The practical path:** get the SEO and homepage conversion work
driving real organic sales (already shipped), cross the 10-sales/30-day
threshold, apply for Creators API access, then flip the switch below.

## Compliance guardrails
- Use approved sources only (Creators API, once eligible). No scraping for pricing/reviews, ever.
- Keep the disclaimer visible: "Prices and availability subject to change."
- Never display a fabricated rating/review count -- the old static `data/products.json` has an identical 4.5★/1000-reviews placeholder on every item; DealTruth's real quality score (from actual Amazon rating/review data) replaces that once connected.

## Data model
`worker/schema.sql` (D1), already applied and tested:
- `asins` -- canonical product records
- `offers` -- normalized per-observation offer data
- `price_snapshots` -- historical effective price over time
- `score_snapshots` -- computed DealTruth scores per observation
- `category_weight_overrides` -- optional per-category scoring weight tuning
- `latest_scores` view -- what `/v1/deals` actually reads from

## Backend endpoints (implemented and tested)
- `GET /v1/deals` -- latest ranked score snapshots, joined with product info
- `POST /v1/admin/ingest` -- triggers a feed fetch + normalize + score cycle (requires `x-admin-key` header matching `ADMIN_API_KEY`)
- `GET /v1/weights` -- lists default + override scoring weights
- `POST /v1/admin/weights` -- upserts category weight tuning
- `GET /health` -- D1 connectivity + row count check

## Local testing (no Cloudflare account needed)
This was just used to verify the whole pipeline works:
```bash
cd worker
npx wrangler d1 execute bestdealsonline --local --config ./wrangler.toml --file=./schema.sql
cp .dev.vars.example .dev.vars   # fill in ADMIN_API_KEY + DEALS_FEED_URL=http://127.0.0.1:8898/feed
node local-mock-feed.mjs &        # simulates 120 days of realistic price history from data/products.json
npx wrangler dev --config ./wrangler.toml --port 8899 --local &
# repeat this ~120 times to build price history, the mock feed advances one simulated day per call:
for i in $(seq 1 121); do curl -s -X POST http://localhost:8899/v1/admin/ingest -H "x-admin-key: <your key>" -d '{"limit":300}' >/dev/null; done
curl -s "http://localhost:8899/v1/deals?limit=5" | python3 -m json.tool
```
Then in `app/`, set `VITE_DEALS_API_BASE=http://localhost:8899` in `.env.local` and run `npm run dev` -- the homepage will show real DealTruth badges on the highest-scoring item per category.

## Frontend integration (implemented)
`app/src/App.jsx` reads `VITE_DEALS_API_BASE` at build time:
- **Unset (current production state):** fetches `/data/products.json` exactly as before. No behavior change, no risk.
- **Set to a deployed worker URL:** fetches `${base}/v1/deals`, shows the DealTruth score + real-discount line on cards, and `pickFeatured()` prioritizes the best-scoring meaningful deal per category instead of an arbitrary pick.

## Going live once you have Creators API access
1. `cd worker && npx wrangler login`
2. `npx wrangler d1 create bestdealsonline` -- copy the returned `database_id` into `worker/wrangler.toml`, replacing `REPLACE_WITH_D1_DATABASE_ID`
3. `npx wrangler d1 execute bestdealsonline --remote --config ./wrangler.toml --file=./schema.sql`
4. `npx wrangler secret put ADMIN_API_KEY` (pick a strong random value)
5. Build the actual Creators-API-to-feed adapter (small script/worker that calls Creators API with OAuth2 and returns `{items: [...]}` in the shape `worker/index.js`'s `normalizeFeedItem` expects -- see that function for the exact fields) and deploy it somewhere reachable
6. `npx wrangler secret put DEALS_FEED_URL` -- point at that adapter
7. `npx wrangler deploy --config ./wrangler.toml`
8. In `app/.env.production` (or your CI/deploy env), set `VITE_DEALS_API_BASE` to the deployed worker's URL, then `npm run build:root` and push

## Suggested cron
- Already configured: every 4 hours (`worker/wrangler.toml` `[triggers]`)
- Recompute scores immediately after each snapshot batch (already how `ingestItems` works -- scoring happens inline per item, not as a separate pass)
