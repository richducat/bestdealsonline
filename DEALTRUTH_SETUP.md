# DealTruth Setup (MVP)

This repo now has a rule-based DealTruth scoring layer in the storefront (`app/src/dealtruth.js`) and UI output on every product card.

## Live Card Output
- `DealTruth Score: X/100`
- `Real discount: ... vs 90-day median`
- `Rarity: ... in 180-day history`
- `Confidence: High/Medium/Low (...)`
- Optional `Buy now / Wait` line with 7-day drop probability
- `Not a deal` callout when discount is weak or rarity is poor

## Compliance Guardrails
- Use approved sources only (PA-API or approved data feed).
- No scraping for pricing/reviews.
- Keep disclaimer visible: `Prices and availability subject to change.`

## Data Model
Use `worker/schema.sql` (D1) tables:
- `asins`
- `offers`
- `price_snapshots`
- `score_snapshots`
- `category_weight_overrides`

## Implemented Backend Endpoints
- `GET /v1/deals` returns latest ranked score snapshots
- `POST /v1/admin/ingest` triggers feed or payload ingest
- `GET /v1/weights` lists default + override weights
- `POST /v1/admin/weights` upserts category weight tuning

## Deployment Notes
- `worker/wrangler.toml` includes a 4-hour ingest cron.
- Set `VITE_DEALS_API_BASE` in frontend env to switch app data from local JSON to Worker API.

## MVP Data Flow
1. Pull current offers from PA-API (or approved feed) on a schedule.
2. Normalize to `EffectivePrice = item + shipping - coupon - promo - subscribe_save`.
3. Insert snapshots into `offers` and `price_snapshots`.
4. Compute DealTruth components and write `score_snapshots`.
5. Serve latest scored records to the app (`/v1/deals` or equivalent).

## Suggested Cron
- High-volume categories: every 4 hours
- Long-tail categories: every 8-12 hours
- Recompute scores immediately after each snapshot batch

## Ticket Breakdown
### Ticket A - Data + Storage
- Apply `worker/schema.sql` to D1.
- Add scheduled ingest job for tracked ASINs.
- Write normalized offer + price snapshots.

### Ticket B - Scoring Service
- Reuse DealTruth formulas from `app/src/dealtruth.js`.
- Persist score snapshots with component breakdowns.
- Expose confidence and buy/wait fields in API payload.

### Ticket C - UI
- Show score/explanation lines on each deal card.
- Keep cards rankable by DealTruth score.
- Keep timestamp/disclaimer visible.

### Ticket D - Compliance
- Keep `Prices and availability subject to change` on pages.
- Ensure only approved APIs feed price/review data.
