# Search Engine Setup (Google, Bing, Yahoo, DuckDuckGo)

This site's `sitemap.xml` is generated from all real content pages
(979 URLs -- see `scripts/gen-sitemap.mjs`). A second
`sitemap-priority.xml` gives crawlers a focused path to the strongest
category, editorial, trust, and substantial guide pages without removing
any valid URL from the complete sitemap. The steps below
get every search engine actually indexing them. None of this can be done
from the repo alone -- each step needs your own login for that engine's
webmaster console.

## 1) Google Search Console
1. Open [Google Search Console](https://search.google.com/search-console).
2. Add property: `bestdealsonline.us` (Domain property).
3. Copy the TXT record Google provides.
4. Add the TXT record in your DNS provider for `bestdealsonline.us`.
5. Wait for DNS propagation, then click **Verify**.
6. Open **Sitemaps** and submit both `https://bestdealsonline.us/sitemap.xml` and `https://bestdealsonline.us/sitemap-priority.xml`. Confirm both show **Success**.
7. Run URL inspection and **Request indexing** for a handful of important pages (homepage, a couple of category hubs, a couple of long-tail pages) to seed the crawl -- don't try to do this for all 977, Google will crawl the rest from the sitemap.
8. Monitor **Coverage** and **Page indexing** reports over the next 2-4 weeks. Google chooses what to index; submitting a URL makes it discoverable but does not guarantee inclusion. Persistent "Discovered - currently not indexed" at scale means the templated price-tier/seasonal pages need more original buyer value or consolidation, not repeated sitemap submissions.

## 2) Bing Webmaster Tools (covers Bing + powers Yahoo + DuckDuckGo)
Yahoo Search has been powered by Bing since 2019, and DuckDuckGo's core web
results also come from Bing (it runs its own crawler only for Instant
Answers, not a full independent index). **One Bing setup effectively
covers all three engines** -- there is no separate Yahoo or DuckDuckGo
webmaster console to configure.

1. Go to [bing.com/webmasters](https://www.bing.com/webmasters) and sign in.
2. Fastest path: **import directly from Google Search Console** (one click, reuses your GSC verification). Otherwise add the site manually and verify via meta tag, XML file upload, or DNS CNAME record.
3. Open **Sitemaps** and submit `https://bestdealsonline.us/sitemap.xml`. Bing re-crawls submitted sitemaps roughly weekly.
4. Bing Webmaster Tools also has a manual **URL submission / IndexNow** panel if you want to push individual URLs immediately instead of waiting for the next crawl.

## 3) IndexNow (instant push to Bing, Yandex, Seznam.cz, Naver, Yep)
This site is already wired for IndexNow:
- Key file: `85a315150525886cabeaf02f8337ab90.txt` at the domain root (required by the protocol so engines can verify you own the site before accepting submissions).
- Submission script: `scripts/indexnow_submit.mjs` -- reads `sitemap.xml` and POSTs the full URL list to IndexNow's bulk endpoint in one call.

**Google does not participate in IndexNow** (confirmed as of 2026) -- it
still requires normal crawling or sitemap discovery, so step 1 above is
still necessary for Google specifically.

**Run this once the branch below is merged and deployed** (submitting
before the enriched pages are live would just waste the "instant" crawl
on stale content):
```
node scripts/indexnow_submit.mjs
```
It's safe to re-run any time you add or change pages -- just regenerate
the sitemap first (`node scripts/gen-sitemap.mjs`) so it reflects the
current URL list.

## 4) After deploying, re-run these when content changes
```
node scripts/gen-sitemap.mjs        # regenerate complete and priority sitemaps
node scripts/check-indexability.mjs # validate targets, canonicals, dates, and coverage
node scripts/indexnow_submit.mjs    # push the updated URL list to Bing/Yandex/etc instantly
```

---

# Monetization next steps (need your own accounts -- can't be done from the repo)

The SEO fixes above get the existing ~977 pages indexed and linked
properly. These are the highest-ROI ways to add revenue beyond the
Amazon affiliate tag once organic traffic starts arriving, ordered by
effort/reward:

1. **Email capture ("deal alerts" list)** -- near-zero cost, compounds independent of search rankings. [beehiiv's free "Launch" plan](https://www.beehiiv.com/pricing) supports up to 2,500 subscribers with an embeddable HTML signup form and no card required -- currently the most generous free tier for this. Add a form to the newsletter/subscription pages once you have an account.
2. **Google AdSense** -- no official minimum traffic threshold, so it can go on the site as soon as you want. Requires creating an AdSense account and adding your publisher snippet.
3. **Skimlinks or Sovrn** -- one JS snippet auto-converts outbound links to 30-48k merchants beyond Amazon, useful since this is a multi-retailer "best deals" site. Low effort, broadens monetized retailer coverage without new page content.
4. **Journey by Mediavine** -- entry-level tier requiring 1,000 sessions/month, 70% ad revenue share. Apply once traffic ramps past that threshold.
5. **Additional direct retailer affiliate programs** (Walmart, Target, Best Buy, Home Depot) for the top few retailers besides Amazon that come up in your content -- more setup effort per program, but often better commission rates.
6. **Raptive (AdThrive)** -- requires 25,000 pageviews/month with majority US/UK/CA/AU/NZ traffic. Revisit once past that threshold.
7. **Ezoic** -- currently requires 250,000 monthly users, the highest bar of the display networks. Not worth pursuing until traffic is much larger.

**ads.txt**: once you add AdSense, Mediavine, Raptive, or Ezoic, you'll
need an `ads.txt` file at the domain root listing each network's entry
(they'll give you the exact line to add) -- this isn't strictly required
by law but all major ad networks require it to prevent ad-inventory
spoofing, and won't serve ads without it. No placeholder file is included
here since the entries are account-specific and a wrong one can block ad
serving.
