/* BestDealsOnline: lightweight analytics helpers
   - Outbound click tracking (Amazon links)
   - Basic engagement events (scroll depth)

   Requires gtag() to be present (loaded via gtag.js).
*/

(function () {
  if (window.__bdoTrackInitialized) return;
  window.__bdoTrackInitialized = true;

  function safe(fn) {
    try {
      fn();
    } catch (_) {}
  }

  function getClosest(el, selector) {
    while (el && el !== document.documentElement) {
      if (el.matches && el.matches(selector)) return el;
      el = el.parentElement;
    }
    return null;
  }

  function sectionFromEl(a) {
    const sec = getClosest(a, '[data-section]');
    return sec ? sec.getAttribute('data-section') : null;
  }

  function labelFromEl(a) {
    return (
      a.getAttribute('data-label') ||
      a.getAttribute('aria-label') ||
      (a.textContent || '').trim().slice(0, 120) ||
      a.href
    );
  }

  function isAmazonOutbound(url) {
    try {
      const u = new URL(url, window.location.href);
      return /(^|\.)amazon\.com$/i.test(u.hostname) || /(^|\.)amzn\.to$/i.test(u.hostname);
    } catch (_) {
      return false;
    }
  }

  // Outbound click tracking for Amazon links across all static pages.
  document.addEventListener(
    'click',
    function (e) {
      const a = e.target && e.target.closest ? e.target.closest('a') : null;
      if (!a || !a.href) return;
      if (!isAmazonOutbound(a.href)) return;

      safe(function () {
        if (typeof window.gtag !== 'function') return;
        window.gtag('event', 'outbound_click', {
          event_category: 'amazon',
          event_label: labelFromEl(a),
          link_url: a.href,
          section: sectionFromEl(a) || 'unknown',
          transport_type: 'beacon',
        });
      });
    },
    { capture: true }
  );

  // Scroll depth (25/50/75/90)
  const fired = new Set();
  function fireDepth(pct) {
    if (fired.has(pct)) return;
    fired.add(pct);
    safe(function () {
      if (typeof window.gtag !== 'function') return;
      window.gtag('event', 'scroll_depth', {
        event_category: 'engagement',
        event_label: String(pct),
        percent_scrolled: pct,
        transport_type: 'beacon',
      });
    });
  }

  function onScroll() {
    const doc = document.documentElement;
    const scrollTop = window.scrollY || doc.scrollTop || 0;
    const height = Math.max(1, doc.scrollHeight - doc.clientHeight);
    const pct = Math.round((scrollTop / height) * 100);

    if (pct >= 25) fireDepth(25);
    if (pct >= 50) fireDepth(50);
    if (pct >= 75) fireDepth(75);
    if (pct >= 90) fireDepth(90);
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('load', onScroll, { passive: true });

  const AMAZON_TAG = 'bestdeals0ad2-20';
  const AMAZON_ASIN_PATTERN = /^[A-Z0-9]{10}$/;

  function cleanPastedUrl(value) {
    return String(value || '')
      .trim()
      .replace(/^[\s<>"'([{]+/, '')
      .replace(/[\s>)"'\]},.!?;:]+$/, '');
  }

  function normalizeAmazonInputUrl(value, depth) {
    if ((depth || 0) > 2) return null;
    const rawInput = String(value || '').trim();
    if (!rawInput) return null;

    const embeddedUrlMatch = rawInput.match(/https?:\/\/[^\s<>"']+/i);
    const raw = cleanPastedUrl((embeddedUrlMatch && embeddedUrlMatch[0]) || rawInput);
    if (!raw) return null;

    const upper = raw.toUpperCase();
    if (AMAZON_ASIN_PATTERN.test(upper)) {
      return new URL(`https://www.amazon.com/dp/${upper}`);
    }

    const withProtocol = /^https?:\/\//i.test(raw) ? raw : `https://${raw}`;
    let parsed;
    try {
      parsed = new URL(withProtocol);
    } catch (_) {
      return null;
    }

    const hostname = parsed.hostname.toLowerCase();
    const isAmazonDomain = /(^|\.)amazon\./i.test(hostname);
    const isShortAmazonDomain = hostname === 'a.co' || hostname === 'amzn.to';
    if (!isAmazonDomain && !isShortAmazonDomain) return null;

    const nestedRaw = parsed.searchParams.get('url') || parsed.searchParams.get('u');
    if (nestedRaw) {
      const nested = normalizeAmazonInputUrl(nestedRaw, (depth || 0) + 1);
      if (nested) return nested;
    }

    return parsed;
  }

  function extractAsinFromAmazonUrl(url) {
    if (!url) return null;

    const explicitAsin = (url.searchParams.get('asin') || '').trim().toUpperCase();
    if (AMAZON_ASIN_PATTERN.test(explicitAsin)) return explicitAsin;
    const pdAsin = (url.searchParams.get('pd_rd_i') || '').trim().toUpperCase();
    if (AMAZON_ASIN_PATTERN.test(pdAsin)) return pdAsin;

    const patterns = [
      /\/dp\/([A-Z0-9]{10})(?:[/?]|$)/i,
      /\/gp\/product\/([A-Z0-9]{10})(?:[/?]|$)/i,
      /\/gp\/aw\/d\/([A-Z0-9]{10})(?:[/?]|$)/i,
      /\/gp\/aw\/dp\/([A-Z0-9]{10})(?:[/?]|$)/i,
      /\/exec\/obidos\/ASIN\/([A-Z0-9]{10})(?:[/?]|$)/i,
      /\/o\/ASIN\/([A-Z0-9]{10})(?:[/?]|$)/i,
      /\/product\/([A-Z0-9]{10})(?:[/?]|$)/i,
    ];

    for (let i = 0; i < patterns.length; i += 1) {
      const match = url.pathname.match(patterns[i]);
      if (match && match[1]) return match[1].toUpperCase();
    }

    const segments = url.pathname.split('/').filter(Boolean);
    for (let i = 0; i < segments.length; i += 1) {
      const cleaned = segments[i].replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
      if (AMAZON_ASIN_PATTERN.test(cleaned)) return cleaned;
    }

    return null;
  }

  function withAffiliateTracking(urlOrString, campaign) {
    let url;
    try {
      url = new URL(String(urlOrString));
    } catch (_) {
      return String(urlOrString || '');
    }

    if (!/(^|\.)amazon\./i.test(url.hostname)) return url.toString();
    url.searchParams.set('tag', AMAZON_TAG);
    url.searchParams.set('utm_source', 'bestdealsonline');
    url.searchParams.set('utm_medium', 'site');
    url.searchParams.set('utm_campaign', campaign || 'bdo_global_link_analyzer');
    return url.toString();
  }

  function amazonSearchLink(query, campaign) {
    const q = encodeURIComponent(String(query || 'amazon deals'));
    return `https://www.amazon.com/s?k=${q}&tag=${AMAZON_TAG}&utm_source=bestdealsonline&utm_medium=site&utm_campaign=${encodeURIComponent(
      campaign || 'bdo_global_link_analyzer_compare'
    )}`;
  }

  function guessQueryFromUrl(url, asin) {
    if (asin) return asin;
    const parts = (url.pathname || '')
      .split('/')
      .filter(Boolean)
      .map(function (part) {
        return part.replace(/[-_+]+/g, ' ').replace(/[^a-zA-Z0-9\s]/g, ' ').trim();
      })
      .filter(Boolean)
      .filter(function (part) {
        return !/^(dp|gp|product|aw|d|hz|stores?|s)$/i.test(part);
      });
    if (!parts.length) return 'amazon deals';
    return parts[0];
  }

  function createLinkAnalyzerWidget() {
    if (document.getElementById('bdo-link-analyzer-launcher')) return;

    const style = document.createElement('style');
    style.id = 'bdo-link-analyzer-style';
    style.textContent = `
      #bdo-link-analyzer-launcher{
        position:fixed;right:16px;bottom:16px;z-index:1200;border:none;border-radius:999px;
        background:#0f172a;color:#fff;min-height:48px;padding:0 16px;display:inline-flex;align-items:center;
        gap:8px;cursor:pointer;box-shadow:0 12px 30px rgba(15,23,42,.32);font:700 14px/1.1 Inter,system-ui,-apple-system,sans-serif
      }
      #bdo-link-analyzer-launcher:hover,#bdo-link-analyzer-launcher:focus-visible{background:#1e293b}
      #bdo-link-analyzer-launcher-label{display:inline}
      #bdo-link-analyzer-overlay{
        position:fixed;inset:0;z-index:1210;background:rgba(2,6,23,.54);backdrop-filter:blur(2px);
        display:none;align-items:flex-end;justify-content:center;padding:14px
      }
      #bdo-link-analyzer-overlay[data-open="true"]{display:flex}
      #bdo-link-analyzer-modal{
        width:min(620px,100%);background:#fff;border-radius:18px;border:1px solid #e2e8f0;box-shadow:0 25px 50px rgba(2,6,23,.35);
        overflow:hidden;font-family:Inter,system-ui,-apple-system,sans-serif
      }
      .bdo-analyzer-header{padding:16px 18px;background:linear-gradient(135deg,#0f172a,#1e293b);color:#fff}
      .bdo-analyzer-pill{display:inline-flex;align-items:center;font-size:10px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#fde047}
      .bdo-analyzer-title{margin:8px 0 0;font-size:20px;font-weight:800;line-height:1.2}
      .bdo-analyzer-sub{margin:6px 0 0;font-size:13px;line-height:1.35;color:#cbd5e1}
      .bdo-analyzer-body{padding:16px 18px}
      .bdo-analyzer-row{display:flex;gap:10px;flex-wrap:wrap}
      #bdo-link-analyzer-input{
        flex:1 1 280px;min-height:44px;padding:0 12px;border-radius:12px;border:1px solid #cbd5e1;background:#f8fafc;
        font-size:14px;color:#0f172a
      }
      #bdo-link-analyzer-input:focus{outline:none;border-color:#f59e0b;box-shadow:0 0 0 3px rgba(245,158,11,.18);background:#fff}
      .bdo-btn{
        min-height:44px;padding:0 16px;border:none;border-radius:12px;cursor:pointer;font-weight:800;font-size:14px;display:inline-flex;align-items:center;justify-content:center;text-decoration:none
      }
      .bdo-btn-primary{background:#facc15;color:#0f172a}
      .bdo-btn-primary:hover,.bdo-btn-primary:focus-visible{background:#fbbf24}
      .bdo-btn-dark{background:#0f172a;color:#fff}
      .bdo-btn-dark:hover,.bdo-btn-dark:focus-visible{background:#1e293b}
      .bdo-btn-ghost{background:#fff;color:#334155;border:1px solid #cbd5e1}
      .bdo-btn-ghost:hover,.bdo-btn-ghost:focus-visible{background:#f8fafc}
      #bdo-link-analyzer-result{margin-top:12px;border:1px solid #e2e8f0;border-radius:12px;padding:12px;background:#f8fafc}
      #bdo-link-analyzer-result[data-state="error"]{border-color:#fecaca;background:#fef2f2;color:#991b1b}
      .bdo-analyzer-meta{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#2563eb}
      .bdo-analyzer-copy{margin-top:6px;font-size:13px;color:#334155}
      .bdo-analyzer-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
      .bdo-close{
        position:absolute;right:10px;top:10px;width:34px;height:34px;border-radius:10px;border:1px solid rgba(255,255,255,.2);
        background:transparent;color:#fff;cursor:pointer
      }
      .bdo-close:hover,.bdo-close:focus-visible{background:rgba(255,255,255,.12)}
      @media (max-width:640px){
        #bdo-link-analyzer-launcher{right:12px;bottom:12px;min-height:46px;padding:0 13px}
        #bdo-link-analyzer-launcher-label{display:none}
        #bdo-link-analyzer-overlay{padding:0}
        #bdo-link-analyzer-modal{width:100%;border-radius:16px 16px 0 0;border-left:none;border-right:none;border-bottom:none}
      }
    `;
    document.head.appendChild(style);

    const launcher = document.createElement('button');
    launcher.id = 'bdo-link-analyzer-launcher';
    launcher.type = 'button';
    launcher.setAttribute('aria-label', 'Open Amazon Link Analyzer');
    launcher.innerHTML = '<span aria-hidden="true">+</span><span id="bdo-link-analyzer-launcher-label">Analyze link</span>';

    const overlay = document.createElement('div');
    overlay.id = 'bdo-link-analyzer-overlay';
    overlay.setAttribute('aria-hidden', 'true');
    overlay.innerHTML = `
      <div id="bdo-link-analyzer-modal" role="dialog" aria-modal="true" aria-labelledby="bdo-link-analyzer-title">
        <div class="bdo-analyzer-header" style="position:relative">
          <div class="bdo-analyzer-pill">Amazon Link Analyzer</div>
          <h2 class="bdo-analyzer-title" id="bdo-link-analyzer-title">Paste any product link</h2>
          <p class="bdo-analyzer-sub">Works with full Amazon URLs, a.co links, and raw ASIN input.</p>
          <button class="bdo-close" id="bdo-link-analyzer-close" type="button" aria-label="Close">x</button>
        </div>
        <div class="bdo-analyzer-body">
          <form id="bdo-link-analyzer-form" class="bdo-analyzer-row">
            <input id="bdo-link-analyzer-input" type="text" placeholder="https://www.amazon.com/dp/B0... or ASIN" />
            <button class="bdo-btn bdo-btn-primary" type="submit">Analyze</button>
          </form>
          <div id="bdo-link-analyzer-result" hidden></div>
          <p style="margin:10px 0 0;color:#64748b;font-size:12px">Use this on any page, then open the tagged product/comparison links directly.</p>
        </div>
      </div>
    `;

    document.body.appendChild(launcher);
    document.body.appendChild(overlay);

    const closeButton = overlay.querySelector('#bdo-link-analyzer-close');
    const form = overlay.querySelector('#bdo-link-analyzer-form');
    const input = overlay.querySelector('#bdo-link-analyzer-input');
    const result = overlay.querySelector('#bdo-link-analyzer-result');
    if (!closeButton || !form || !input || !result) return;

    function emitEvent(name, params) {
      safe(function () {
        if (typeof window.gtag !== 'function') return;
        window.gtag('event', name, params || {});
      });
    }

    function setOpen(open) {
      overlay.setAttribute('data-open', open ? 'true' : 'false');
      overlay.setAttribute('aria-hidden', open ? 'false' : 'true');
      if (open) {
        window.setTimeout(function () {
          if (input && typeof input.focus === 'function') input.focus();
        }, 40);
      }
    }

    function openWidget() {
      setOpen(true);
      emitEvent('link_analyzer_open', {
        event_category: 'link_analyzer',
        event_label: window.location.pathname || '/',
      });
    }

    function closeWidget() {
      setOpen(false);
    }

    function renderError(message) {
      if (!result) return;
      result.hidden = false;
      result.setAttribute('data-state', 'error');
      result.innerHTML = `<div>${message}</div>`;
    }

    function renderSuccess(data) {
      if (!result) return;
      result.hidden = false;
      result.setAttribute('data-state', 'ok');

      const asinLine = data.asin ? `<div class="bdo-analyzer-meta">ASIN ${data.asin}</div>` : '<div class="bdo-analyzer-meta">Amazon URL detected</div>';
      result.innerHTML = `
        ${asinLine}
        <div class="bdo-analyzer-copy">Ready. Open the product or compare against better-ranked alternatives.</div>
        <div class="bdo-analyzer-actions">
          <a class="bdo-btn bdo-btn-dark" href="${data.productLink}" target="_blank" rel="nofollow noopener noreferrer">Open product</a>
          <a class="bdo-btn bdo-btn-primary" href="${data.compareLink}" target="_blank" rel="nofollow noopener noreferrer">Find better deals</a>
          <button type="button" class="bdo-btn bdo-btn-ghost" id="bdo-link-analyzer-copy">Copy link</button>
        </div>
      `;

      const copyButton = result.querySelector('#bdo-link-analyzer-copy');
      if (copyButton) {
        copyButton.addEventListener('click', function () {
          safe(function () {
            navigator.clipboard.writeText(String(input.value || '').trim());
          });
          copyButton.textContent = 'Copied';
          window.setTimeout(function () {
            copyButton.textContent = 'Copy link';
          }, 1200);
        });
      }
    }

    function analyzeInput(rawInput) {
      const normalized = normalizeAmazonInputUrl(rawInput, 0);
      if (!normalized) {
        renderError('Paste a valid Amazon product URL or ASIN (example: amazon.com/dp/B0...).');
        return;
      }

      const asin = extractAsinFromAmazonUrl(normalized);
      const productLink = asin
        ? withAffiliateTracking(`https://www.amazon.com/dp/${asin}`, 'bdo_global_link_analyzer_product')
        : withAffiliateTracking(normalized.toString(), 'bdo_global_link_analyzer_product');
      const compareQuery = guessQueryFromUrl(normalized, asin);
      const compareLink = amazonSearchLink(`${compareQuery} deals`, 'bdo_global_link_analyzer_compare');

      renderSuccess({
        asin: asin || null,
        productLink,
        compareLink,
      });

      emitEvent('link_analyzer_submit', {
        event_category: 'link_analyzer',
        event_label: asin || 'url_only',
        has_asin: asin ? 'yes' : 'no',
      });
    }

    launcher.addEventListener('click', openWidget);
    closeButton.addEventListener('click', closeWidget);
    overlay.addEventListener('click', function (event) {
      if (event.target === overlay) closeWidget();
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && overlay.getAttribute('data-open') === 'true') closeWidget();
    });
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      const raw = String(input.value || '').trim();
      if (!raw) {
        renderError('Paste an Amazon product URL or ASIN first.');
        return;
      }
      analyzeInput(raw);
    });

    window.addEventListener('bdo-open-link-analyzer', openWidget);

    if (window.location.hash === '#link-analyzer') {
      openWidget();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createLinkAnalyzerWidget, { once: true });
  } else {
    createLinkAnalyzerWidget();
  }
})();
