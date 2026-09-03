# Hosting: where the site is served from, and how to get real redirects

## Today

`bestdealsonline.us` is served by **GitHub Pages** from the `main` branch root
(server header `GitHub.com`; DNS at Namecheap points at GitHub, the Cloudflare
zone created in Feb 2026 was never activated because the nameservers were never
moved). Every push to `main` deploys in about a minute.

GitHub Pages cannot send HTTP 301s. The 755 retired doorway URLs from the July
consolidation are therefore HTML stubs (`scripts/rewrite_redirect_stubs.py`):
`<meta http-equiv="refresh" content="0;url=...">` plus `rel=canonical`, which
Google treats as a permanent redirect, plus a JavaScript `location.replace()`
so visitors move in well under 100 ms. `_redirects` and `_headers` are ignored
on GitHub Pages.

`_config.yml` keeps the strategy docs, build scripts, ops script, worker source
and extension source out of the published site. Only `*.html`, `assets/`,
`images/`, `blog/`, `data/products.json`, the sitemaps, `robots.txt`, `CNAME`
and the IndexNow key are meant to be public.

## The Cloudflare copy

`wrangler.jsonc` deploys the same tree as a Worker with static assets. A copy is
live at `https://bestdealsonline.richducat.workers.dev/` but the Git integration
has not built since 18 July 2026 (it still serves the pre-consolidation site).
`_headers` marks that host `X-Robots-Tag: noindex` so it can never be indexed
as a duplicate once builds resume.

## Moving the live domain to Cloudflare (gives real 301s)

1. In the Cloudflare dashboard, open the `bestdealsonline` Worker and fix the
   Workers Builds job (it has been failing or paused since July). Wait for a
   green build of `main`.
2. Verify on the preview host before touching DNS:
   - `/` and `/air-fryer.html` return 200
   - `/air-fryer-under-25.html` and `/air-fryer-under-25` return **301** to `/air-fryer.html`
   - `/air-fryer` returns 301 to `/air-fryer.html`
   - `/does-not-exist` returns 404 with the branded page
   If `/` does not resolve under `html_handling: "none"`, add a tiny Worker
   entrypoint that rewrites `/` to `/index.html` before `env.ASSETS.fetch()`.
3. Add `bestdealsonline.us` and `www.bestdealsonline.us` as custom domains on the
   Worker, then move the Namecheap nameservers to the ones Cloudflare shows for
   the zone. Keep the GitHub Pages site up until DNS has propagated.
4. Re-submit both sitemaps in Search Console and run
   `node scripts/indexnow_submit.mjs`.

Regenerate `_redirects` whenever stubs change: `python3 scripts/gen_redirects.py`
(it also fails loudly if any stub points at a missing page).
