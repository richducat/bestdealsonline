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
- Rotate formats across the week (see "Pillar 2 — Viral-format content" below): buying guides,
  problem-solver listicles, worth-it/skip-it verdicts, seasonal countdowns 4–6 weeks ahead of peak,
  and fake-discount exposés framed around price-history honesty.

### Article requirements
- File: `blog/<kebab-case-slug>.html`, copy structure from `blog/gan-chargers-what-buyers-like-what-bugs-them-and-how-to-choose.html` (Tailwind CDN, canonical, OG tags, BlogPosting JSON-LD with real publish date, GA4 snippet, `/assets/track.js`).
- Keep the warm-theme head links the template carries (Fraunces font + `/assets/warm-theme.css`) and use `https://bestdealsonline.us/assets/og-home.jpg` for `og:image`/`twitter:image` — the sitewide brand look depends on both.
- 1,200+ words. H1 matches target query intent; H2 sections; a short FAQ section (also add FAQPage JSON-LD).
- Every Amazon link: `https://www.amazon.com/s?k=<query>&tag=bestdeals00d9-20` (search links until PA-API access exists — never deep-link to a specific ASIN with claimed price/rating we can't verify).
- Affiliate disclosure sentence near the top, linking to `/affiliate-disclosure.html`.
- 3–5 internal links to related hub/category/blog pages; where natural, add a link *to* the new article from one related existing page.

### HARD content rules (never violate)
- **Never fabricate**: star ratings, review counts, review quotes, prices, discount percentages, or "reviewers say" claims that aren't verifiable. `data/products.json` placeholder ratings are fake — never surface them as real.
- Write buying guidance from product attributes and trade-offs (wattage, capacity, materials, sizing), not invented social proof.
- No fake urgency or countdowns.
- **No SEO jargon in user-facing copy** — never render words like "intent," "high-converting," "long-tail," "query," or "conversions" to a shopper. Write like you're helping a friend decide. (After running any page generator, also run `python3 scripts/humanize_copy.py`.)

### Publish sequence
1. `git pull --ff-only` on `main` in `/Users/richardducat/GITHUB/bestdealsonline`.
2. Write the article; update internal links.
3. `node scripts/gen-sitemap.mjs` (regenerates sitemap.xml including the new page).
4. Commit + push to `origin main` (GitHub Pages deploys automatically).
5. Wait ~2 minutes, confirm `https://bestdealsonline.us/blog/<slug>.html` returns 200.
6. `node scripts/indexnow_submit.mjs` (instant Bing/Yandex indexing; Google discovers via the submitted sitemap).
7. `python3 scripts/gen_pins.py <slug>` then commit and push the new pin image — it lands in
   `images/pins/` ready for the day's Pinterest upload.

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

## Road to 10,000 visitors/week — the free-traffic system

Target: **10,000 visits/week (~43k/mo)**. Realistic timeline from a near-zero base: **5–8 months**
of compounding, with Pinterest as the accelerant. Nothing below costs money; everything costs
consistency.

### The honest math

| Source | At month 3 | At month 6–8 | Why it scales |
|---|---|---|---|
| Pinterest | 1,500/wk | 4,000–5,000/wk | Pins compound for months; 465M users; core demo = women 25–54 planning purchases |
| Google organic (979 pages + daily articles) | 700/wk | 3,000–4,000/wk | Long-tail rankings mature at months 3–6; daily fresh content widens the net |
| Google Discover | 0–300/wk | 500–1,500/wk | Freshness + large images + `max-image-preview:large` (now set sitewide); spiky but big when it hits |
| Reddit / Facebook groups / X | 300/wk | 500–1,000/wk | Value-first participation; occasional post that pops |
| Email list (owned) | 100/wk | 500+/wk | Every channel above feeds it; immune to algorithms |

### Pillar 1 — The Pinterest engine (highest priority, needs 30 min/day)

Setup (once, ~1 hour, requires the account owner):
1. Create a **Pinterest Business account** (free) → claim the website (adds an HTML tag or DNS record — I can inject the tag the moment you have it).
2. Create 10 boards mirroring the site: Kitchen Finds, Cozy Home, Mom Life Essentials, Beauty on a Budget, Kids' Gear That Lasts, Smart Shopping Tips, Under $25 Finds, Under $50 Finds, Fitness at Home, Pet Parents.

Operating loop (30 min/day, mostly done for you):
- **`images/pins/` holds ready-made 1000×1500 branded pins** for every blog article — `scripts/gen_pins.py` regenerates them and covers each new daily article automatically.
- Pin 3–5/day: 2 article pins + 1–2 repins of popular adjacent content. Every pin: keyword-rich title (use the article H1), 2–3 sentence description with search phrases ("air fryer buying guide", "kitchen gadgets worth it"), destination = the article URL.
- Rule: pins point at **articles and hub pages**, never raw Amazon links (Pinterest suppresses direct affiliate links).
- Expectation: months 1–2 feel dead (impressions, no clicks). Months 3–4 the compounding starts. Do not stop.

### Pillar 2 — Viral-format content (what actually gets shared in this niche)

The daily article engine now rotates in these proven formats (see article spec above):
1. **The fake-discount exposé** — "That '50% off' air fryer? It's been that price for 6 months." Righteous-anger content travels; it's also exactly our DealTruth thesis.
2. **Problem-solver listicles** — "9 under-$25 things that fix the most annoying part of your kitchen." Pinterest gold.
3. **Seasonal countdowns** — back-to-school (July–Aug), Halloween (Sept), Black Friday prep (Oct–Nov: "what's actually cheaper on BF vs. relabeled"), gift guides (Nov–Dec). Publish 4–6 weeks before peak.
4. **The "worth it / skip it" verdict** — one product, one clear call. Skimmable, screenshot-able.
5. **Real-price receipts** — once the PA-API unlocks, publish actual price-history charts; nobody else in this niche shows receipts.

### Pillar 3 — Community seeding (2 hrs/week, human required)

- **Reddit**: participate genuinely in r/Frugal, r/BuyItForLife, r/onebag, r/MealPrepSunday, r/Parenting, r/HomeImprovement. 90% helpful comments, 10% "I wrote up the research on this" links where subreddit rules allow. Never affiliate links directly.
- **Facebook groups**: "Amazon finds"-style groups have millions of members in the exact demo. Share the article (not the Amazon link) with a personal-voice caption.
- **X/Threads**: post the fake-discount exposés — screenshots + one punchy line. Tag nothing, sell nothing.

### Pillar 4 — Owned audience

Add a weekly "5 deals worth your time" email once traffic supports it (Beehiiv/MailerLite free tiers; needs account owner). Every article and pin should eventually feed this list — it's the only channel no algorithm can take away.

### Weekly cadence (what runs itself vs. what needs a human)

| When | What | Who |
|---|---|---|
| Daily 7am | Trending article published, themed, pinned-image generated | Automated ✅ |
| Daily (30 min) | Pin 3–5 pins, engage Pinterest | You |
| Every 5 days 9am | Amazon qualified-sales check | Automated ✅ |
| Weekly (2 hrs) | Reddit/FB participation + 1 exposé/listicle share | You |
| Every 2 weeks | GSC: Pages report + Performance queries → retitle underperformers | Ask me |
| Monthly | KPI review vs. milestones below | Ask me |

### Milestones (visits/week, measured in GA4)

- Week 4: 300–500 · Month 3: 1,500–2,500 · Month 5: 4,000–6,000 · **Month 6–8: 10,000**
- If a milestone misses by >50%: double Pinterest volume and shift article mix toward whichever format's CTR is winning in GSC.

## KPIs (check monthly)

| Metric | Source | 90-day target |
|---|---|---|
| Indexed pages | GSC Pages | 300+ |
| Organic clicks/day | GSC Performance | 100+ |
| Amazon clicks/mo | Associates reports | 700+ |
| Qualified sales (trailing 30d) | Associates | 10+ (API unlock) |
