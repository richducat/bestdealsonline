# BestDealsOnline Worker (PA-API Feed + DealTruth)

Cloudflare Worker that ingests approved Amazon offer feeds into D1, computes DealTruth snapshots, and serves ranked deals.

## What it now does
- Scheduled ingest (cron) from an approved feed URL (`PAAPI_PROXY_URL` or `DEALS_FEED_URL`)
- Writes normalized `offers` + `price_snapshots`
- Computes and stores `score_snapshots`
- Serves latest scored deals from `GET /v1/deals`
- Supports per-category weight overrides for tuning

## Files
- Worker code: `worker/index.js`
- D1 schema: `worker/schema.sql`
- Wrangler config (cron + D1 binding): `worker/wrangler.toml`

## Required setup
1. Create D1 DB and apply schema:
```bash
cd worker
npx wrangler d1 execute bestdealsonline --file=./schema.sql
```
2. Set Worker secrets/vars:
- `PAAPI_PROXY_URL` or `DEALS_FEED_URL` (approved source endpoint)
- `DEALS_FEED_BEARER_TOKEN` (optional)
- `ADMIN_API_KEY` (recommended)
- `TRACKED_CATEGORIES` (optional, comma-separated)
- `INGEST_LIMIT` (optional, default 300)
- `CATEGORY_WEIGHT_OVERRIDES_JSON` (optional)

## Endpoints
- `GET /health`
- `GET /v1/deals?categories=Electronics,Home&limit=300`
- `GET /v1/weights`
- `POST /v1/admin/weights` (requires `x-admin-key` when `ADMIN_API_KEY` is set)
- `POST /v1/admin/ingest` (manual ingest trigger)

### Admin ingest payload options
- Trigger feed ingest:
```json
{ "categories": ["Electronics", "Home"], "limit": 300 }
```
- Direct ingest with explicit items:
```json
{ "items": [ { "asin": "B000000000", "title": "...", "offer": { "price": 19.99 } } ] }
```

## Cron
Configured in `worker/wrangler.toml`:
- `0 */4 * * *` (every 4 hours)

Adjust this schedule as needed.

## Frontend wiring
Set in `app/.env` (or build env):
```bash
VITE_DEALS_API_BASE=https://<your-worker-domain>
```
App will then fetch `GET /v1/deals` instead of local `data/products.json`.

## Compliance notes
- Use only approved APIs/feeds for Amazon pricing/reviews.
- Do not scrape Amazon pages for prohibited data extraction.
- Keep user-facing disclaimer: `Prices and availability are subject to change.`
