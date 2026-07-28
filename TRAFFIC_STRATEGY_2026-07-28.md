# Traffic Strategy Reset — 2026-07-28

Supersedes the growth assumptions in `GROWTH_PLAYBOOK.md`. The playbook's
tactics are still right; its premise ("we have 977 pages working for us") is
wrong, and the paid-traffic question now has a hard answer.

---

## 1. What the data actually says

Pulled 2026-07-28 from Search Console, Associates Central, and the repo.

| Measure | Value | Read |
|---|---|---|
| Pages indexed by Google | **193** of 954 | The 2026-07-09 sitemap push worked — was ~6 |
| Discovered – currently not indexed | **774** | Google saw the URLs and declined to crawl |
| Clicks / impressions (90d) | 26 / 2,970 | 0.9% CTR, avg position 18.9 |
| Top 10 queries by impressions | **all brand or generic** | "bestdeals", "best deals", "is best deals legit" |
| Amazon clicks (30d) | 11 | 0 orders, 0 shipped, $0.00 |
| Static page median length | **293 words** | 99.7% are under 500 words |
| Pages in near-duplicate families | **744** across 126 families | ~59% identical to their siblings |
| Blog posts over 1,200 words | **4 of 26** | The other 22 are ~250-word stubs |

### The one sentence version

The site has 954 pages and essentially no product rankings, because 744 of
those pages are ~290-word variants of each other (`rice-cooker-under-25`,
`rice-cooker-under-30`, `rice-cooker-under-50`, ten deep), and Google has
responded by refusing to index 774 of them.

"Discovered – currently not indexed" is not a waiting room. It is Google
saying it looked at the URL pattern and decided the crawl wasn't worth it.
More pages of the same shape make that verdict *stronger*, not weaker.

The four real articles — the ones the daily task wrote — are the only content
on the site pulling its weight.

---

## 2. Paid ads: the answer is no, with one exception

Run `python3 scripts/paid_traffic_math.py` to reproduce all of this.

The blended commission rate for this site's actual content mix, from the real
rate card for store `bestdeals00d9-20`, is **3.33%** — kitchen 4.5%,
chargers/computers 2.5%, home/toys/fitness 3%, luggage 4%.

**What one visitor is worth:**

| Scenario | AOV | order/click | Amazon CTR | Max CPC |
|---|---|---|---|---|
| Pessimistic | $35 | 5% | 12% | **$0.007** |
| Base case | $45 | 9% | 22% | **$0.030** |
| Dream | $70 | 15% | 40% | **$0.140** |

**What a visitor costs:**

| Channel | CPC | vs. base case |
|---|---|---|
| Google Search — product terms | $0.90 | **30× underwater** |
| Google Search — cheapest long-tail | $0.35 | 12× underwater |
| Microsoft/Bing — long-tail | $0.22 | 7× underwater |
| Pinterest ads | $0.30 | 10× underwater |
| Taboola/Outbrain native | $0.06 | 2× underwater |

$500 into the *cheapest legitimate* channel (Bing long-tail) buys 2,273 visits,
returns about **$67**. You lose $433.

This is not a keyword-selection problem. The ceiling on what a visitor can be
worth ($0.03) sits below the floor of what any real ad platform charges. No
keyword, however cheap, fixes a 3.3% commission on a $45 basket. **Do not buy
traffic as a growth strategy.**

### The exception: buying the 3 sales that save the account

Different question, different answer.

Amazon closes the account if it doesn't see **3 qualified sales in the first
180 days** — deadline roughly September 2026. At the base-case funnel, 3 orders
needs about **152 visits**, or 33 Amazon clicks.

| Channel | Cost to buy ~152 visits |
|---|---|
| Bing long-tail | **$33** |
| Performance Max | $38 |
| Pinterest | $45 |
| Google Search long-tail | $53 |

Those 3 orders pay about **$4.49** in commission. You lose ~$30–50 on the
transaction — and you keep the account, the tag, the 193 indexed pages, and
every month of SEO compounding already banked. Losing the account in September
resets all of it to zero.

Spend $100–150, not $33, because 152 visits producing exactly 3 orders is an
*average*, not a guarantee — you want 2–3× the traffic for confidence.

**Rules if you do this** (Amazon's Operating Agreement):
- Ads must point at **your own pages**, never directly at an Amazon link.
- Never bid on "Amazon" or any Amazon trademark, and keep it out of ad copy.
- Point ads at the four real articles, not the thin pages — they're the only
  ones that convert.

This is account insurance, not marketing. Treat it as a one-time $150 expense
with a hard stop, and turn it off the moment 3 sales land.

---

## 3. Scaling without paid ads — what actually moves

In priority order. The first item is worth more than the rest combined.

### 3.1 Consolidate the 744 (highest impact, nothing else competes)

126 topic families × ~10 near-identical price-cap variants each. Merge each
family into **one genuinely good 1,200+ word guide** that covers every price
band in sections, and 301-redirect the variants into it.

- 954 pages → ~340, every one of them substantive
- Redirect equity consolidates instead of splitting 10 ways
- Removes the site-level "this domain makes thin pages" signal that is
  currently suppressing everything, including the good articles

`python3 scripts/analyze_thin_clusters.py` prints the families and writes a
merge plan to `/tmp/consolidation_plan.json`. **This is analysis only — it
changes nothing.** Say the word and I'll build the merge + redirect pass,
starting with the 20 biggest families so you can see the GSC response before
committing to all 126.

Expect 4–8 weeks before Google re-crawls and the effect shows.

### 3.2 Fix what the daily engine optimises for

Already changed in the scheduled task (`daily-trending-deal-article`):
- **Hard 1,200-word gate** with a measuring command — no more 250-word stubs
- **Must link the new article from 2+ already-indexed pages** — a new page
  linked only from unindexed thin pages doesn't get crawled

The task fires only while the desktop app is open, which is why July produced
7 articles in 20 days rather than 20. Either leave the app open, or accept
~3/week and stop calling it daily.

### 3.3 Rewrite for the queries you actually get

Every top query is navigational — people looking for *this site*, or the
hopeless head term "best deals". Zero product queries. That means the product
pages aren't competing at all. Two consequences:

- The "is best deals legit" query (50 impressions, 0 clicks) is a trust
  question with no page answering it. That's a free, easy win: an honest
  "who we are / how we make money" page.
- Ranking for "best deals" is not achievable and never was. Drop it.

### 3.4 The distribution levers that don't need Google

- **The exposé article** (`/blog/how-to-spot-a-fake-amazon-discount-in-10-seconds.html`)
  is affiliate-free and built for sharing. `marketing/seeding-kit.md` has the
  ready-to-paste Reddit/FB posts. This is the fastest path to real traffic in
  the next six weeks and it needs you, not automation.
- **Pinterest** — still blocked on you creating a Business account. 23 pins are
  rendered and waiting in `images/pins/`. Once you're logged in I can claim the
  site and set up boards.

---

## 4. What I'd do this week

1. **Submit the tax information** in Associates Central — it's blocking payment
   and it's a five-minute job.
2. **Decide on the $150 account-insurance ad spend.** Deadline is ~6 weeks out.
3. **Approve the consolidation** on the 20 largest families so we can measure
   the GSC response before doing all 126.
4. **Create the Pinterest Business account** — the pins are already built.
5. **Seed the exposé** in two subreddits using the seeding kit.

Items 1, 4 and 5 need you. Items 2 and 3 need a yes.
