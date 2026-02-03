# BestDealsOnline Amazon PA-API Worker (Cloudflare)

This worker provides live-ish product data (title/image/price) using Amazon Product Advertising API (PA-API).

## Why a Worker?
GitHub Pages can't safely store API secrets. A Worker lets us keep secrets in environment variables.

## Prereqs
- Amazon Associates account with tag: `bestdeals0ad2-20`
- Amazon PA-API credentials (Access Key + Secret). Note: PA-API access usually requires qualifying sales to maintain access.
- A Cloudflare account (free is fine)

## Env vars (set in Cloudflare dashboard)
- `PAAPI_ACCESS_KEY`
- `PAAPI_SECRET_KEY`
- `PAAPI_PARTNER_TAG` (set to `bestdeals0ad2-20`)
- `PAAPI_HOST` (e.g. `webservices.amazon.com`)
- `PAAPI_REGION` (e.g. `us-east-1`)

## Endpoints
- `GET /v1/deals?categories=Electronics,Home,Kitchen,Tools,Kids,Beauty,Fitness,Pets&limit=300`

Returns JSON:
```json
{ "items": [ { "id": "...", "title": "...", "category": "Kitchen", "price": 39.99, "currency": "USD", "imageUrl": "...", "affiliateLink": "..." } ] }
```

## Frontend
Update `DEALS_API_BASE` in `app/src/App.jsx` to your Worker URL before building.
