# BestDealsOnline Growth Playbook — Free Organic Traffic to $10K/mo in Sales

Goal: **$10,000/month in Amazon sales volume** driven through affiliate links (tag `bestdeals00d9-20`).

## The math (what $10K/mo actually requires)

- Amazon converts roughly 8–12% of affiliate clicks into orders within the 24-hour cookie window.
- At a ~$45 average order value, $10K/mo ≈ **220 orders/mo ≈ 2,000–2,800 Amazon clicks/mo**.
- Deal/review pages send 25–40% of visitors to Amazon, so that's roughly **7,000–11,000 visits/mo**.
- From a near-zero indexed base (sitemap first submitted to Google 2026-07-09), expect a 4–9 month SEO ramp. The levers below compound; none are paid.

## Lever 1 — Daily trending-article engine (automated)

One new buyer-intent article every day, targeting **rising product searches** before competition saturates them. Automated via the `daily-trending-deal-article` scheduled task.

### Topic selection (each day, pick ONE)
Research via web search, in priority order:
1. Google Trends "rising"/"breakout" product queries (US) — shopping-related.
2. Amazon Movers & Shakers / Best Sellers categories mentioned in fresh coverage.
3. Seasonal/event-driven demand 2–6 weeks ahead of peak (Prime Day, back-to-school, holidays — search volume leads the event).
4. Long-tail "best X under $Y" or "X vs Y" queries with clear buying intent.

Rules:
- Buyer intent only (someone ready to purchase), not news/informational topics.
- Check the repo first — do not duplicate an existing page's target query (`ls blog/ *.html`).
- Prefer topics where we already have related pages to interlink (topic clusters beat orphans).

### Article requirements
- File: `blog/<kebab-case-slug>.html`, copy structure from `blog/gan-chargers-what-buyers-like-what-bugs-them-and-how-to-choose.html` (Tailwind CDN, canonical, OG tags, BlogPosting JSON-LD with real publish date, GA4 snippet, `/assets/track.js`).
- 1,200+ words. H1 matches target query intent; H2 sections; a short FAQ section (also add FAQPage JSON-LD).
- Every Amazon link: `https://www.amazon.com/s?k=<query>&tag=bestdeals00d9-20` (search links until PA-API access exists — never deep-link to a specific ASIN with claimed price/rating we can't verify).
- Affiliate disclosure sentence near the top, linking to `/affiliate-disclosure.html`.
- 3–5 internal links to related hub/category/blog pages; where natural, add a link *to* the new article from one related existing page.

### HARD content rules (never violate)
- **Never fabricate**: star ratings, review counts, review quotes, prices, discount percentages, or "reviewers say" claims that aren't verifiable. `data/products.json` placeholder ratings are fake — never surface them as real.
- Write buying guidance from product attributes and trade-offs (wattage, capacity, materials, sizing), not invented social proof.
- No fake urgency or countdowns.

### Publish sequence
1. `git pull --ff-only` on `main` in `/Users/richardducat/GITHUB/bestdealsonline`.
2. Write the article; update internal links.
3. `node scripts/gen-sitemap.mjs` (regenerates sitemap.xml including the new page).
4. Commit + push to `origin main` (GitHub Pages deploys automatically).
5. Wait ~2 minutes, confirm `https://bestdealsonline.us/blog/<slug>.html` returns 200.
6. `node scripts/indexnow_submit.mjs` (instant Bing/Yandex indexing; Google discovers via the submitted sitemap).

## Lever 2 — Make the existing 977 pages work

- Sitemap was submitted to GSC on 2026-07-09 (977 discovered). Watch **GSC → Pages** every ~2 weeks; pages stuck in "Discovered/Crawled – currently not indexed" need more internal links and content depth.
- Strengthen topic clusters: every hub page should link to its children and vice versa (`scripts/update_internal_links.py` exists).
- Refresh top pages: GSC → Performance → pages with impressions but low CTR → rewrite titles/descriptions toward the actual queries shown.

## Lever 3 — Free distribution channels (in ROI order)

1. **Pinterest** — the highest-ROI free channel for deals/product content. Create a business account, one vertical pin (2:3) per article/major page, keyword-rich titles/descriptions. Pins compound for months. Aim 1–3 pins/day.
2. **Email list** — owned traffic, immune to algorithm changes. Add a "deal alerts" signup (free tiers: Beehiiv/MailerLite), send a weekly top-deals digest.
3. **Reddit** — participate genuinely in r/buildapcsales, r/deals, product subreddits. Never drop affiliate links directly (ban risk + Reddit strips them); build profile karma, link to articles only where subs allow and it truly answers the question.
4. **Google Discover** — freshness + strong images + clear headlines already align with the daily engine; add a real 1200px-wide OG image per article when possible (current og-default.svg is weak for Discover).
5. **X/Facebook deal communities** — post genuinely good deals with the article link; low effort, modest return.
6. **YouTube Shorts/TikTok** — highest ceiling, highest effort; only after levers 1–3 are humming.

## Compliance guardrails (account survival = the whole business)

- Amazon Associates: **3 qualified sales in first 180 days** or the account closes; **10 sales in trailing 30 days** unlocks the Creators/PA-API (which unblocks the DealTruth live pipeline).
- Disclosure on every page with affiliate links (already sitewide — keep it).
- Don't state Amazon prices in content (they change; policy risk) — say "check today's price."
- Monitored by the `amazon-qualified-sales-check` scheduled task (every 5 days).

## KPIs (check monthly)

| Metric | Source | 90-day target |
|---|---|---|
| Indexed pages | GSC Pages | 300+ |
| Organic clicks/day | GSC Performance | 100+ |
| Amazon clicks/mo | Associates reports | 700+ |
| Qualified sales (trailing 30d) | Associates | 10+ (API unlock) |
