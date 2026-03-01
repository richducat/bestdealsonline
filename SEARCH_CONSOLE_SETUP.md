# Google Search Console Setup

## 1) Verify DNS ownership
1. Open [Google Search Console](https://search.google.com/search-console).
2. Add property: `bestdealsonline.us` (Domain property).
3. Copy the TXT record Google provides.
4. Add the TXT record in your DNS provider for `bestdealsonline.us`.
5. Wait for DNS propagation, then click **Verify**.

## 2) Submit sitemap
1. In Search Console, open **Sitemaps**.
2. Submit: `https://bestdealsonline.us/sitemap.xml`
3. Confirm status is **Success**.

## 3) Post-submit checks
1. Run URL inspection for:
   - `https://bestdealsonline.us/`
   - `https://bestdealsonline.us/best-deals-online.html`
   - `https://bestdealsonline.us/best-deals-online-today.html`
   - `https://bestdealsonline.us/online-deals-methodology.html`
2. Request indexing for important new pages.
3. Monitor Coverage and Enhancements over the next 7-14 days.
