/* BestDealsOnline: lightweight analytics helpers
   - Outbound click tracking (Amazon links)
   - Basic engagement events (scroll depth)

   Requires gtag() to be present (loaded via gtag.js).
*/

(function () {
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
})();
