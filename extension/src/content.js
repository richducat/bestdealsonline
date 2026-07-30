// Ask Penny — content script. Runs only on Amazon product pages the user
// opens, reads the visible price/was/title from the DOM (no network calls,
// no crawling), scores it with the same DealTruth engine as
// bestdealsonline.us, and shows a floating verdict card.

import { checkDeal, money } from '../../app/src/dealcheck-core.js'

const SITE = 'https://bestdealsonline.us'
const AFF_TAG = 'bestdeals00d9-20'

const MOODS = {
  bad: { color: '#dc2626', soft: '#fef2f2', emoji: '🚩' },
  flat: { color: '#a8a29e', soft: '#f5f5f4', emoji: '😐' },
  good: { color: '#059669', soft: '#ecfdf5', emoji: '✅' },
  great: { color: '#047857', soft: '#ecfdf5', emoji: '🎉' },
  caution: { color: '#d97706', soft: '#fffbeb', emoji: '🧐' },
}

function text(sel) {
  const el = document.querySelector(sel)
  return el ? el.textContent.trim() : ''
}

function num(s) {
  const m = String(s || '').replace(/,/g, '').match(/\d+(?:\.\d{1,2})?/)
  return m ? Number(m[0]) : null
}

function readPage() {
  const price = num(
    text('#corePrice_feature_div .a-offscreen') ||
    text('#corePriceDisplay_desktop_feature_div .a-price .a-offscreen') ||
    text('#corePriceDisplay_mobile_feature_div .a-price .a-offscreen') ||
    text('span.a-price .a-offscreen')
  )
  let was = num(
    text('.basisPrice .a-offscreen') ||
    text('span[data-a-strike="true"] .a-offscreen') ||
    text('#corePriceDisplay_desktop_feature_div .a-text-price .a-offscreen') ||
    text('.a-text-price .a-offscreen')
  )
  if (was != null && price != null && was <= price) was = null
  const title = (text('#productTitle') || document.title.replace(/Amazon\.com\s*:?\s*/i, '')).slice(0, 110)
  return { price, was, title }
}

function targets(usual) {
  return { good: Math.floor(usual * 0.85), great: Math.floor(usual * 0.7) }
}

function el(tag, style, html) {
  const node = document.createElement(tag)
  if (style) node.style.cssText = style
  if (html != null) node.innerHTML = html
  return node
}

function render(page) {
  // "Usual" price: user-adjustable; starts as an estimate from the
  // crossed-out price (they run ~28% high) or the current price.
  let usual = page.was ? Math.round(page.was * 0.72) : page.price
  let estimated = true

  const host = el('div', [
    'position:fixed', 'right:18px', 'bottom:18px', 'z-index:2147483647',
    'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif',
    'max-width:340px', 'width:calc(100vw - 36px)',
  ].join(';'))
  const shadow = host.attachShadow({ mode: 'open' })

  function verdictHtml() {
    const result = checkDeal(usual, page.price, { claimedWas: page.was ?? undefined })
    const mood = MOODS[result.tier.mood]
    const { good, great } = targets(usual)
    const q = encodeURIComponent(page.title)
    const estNote = estimated ? ' (my estimate — adjust below)' : ''
    return `
      <div style="background:#fff;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,.18);overflow:hidden;border-top:5px solid ${mood.color}">
        <div style="display:flex;align-items:center;gap:8px;padding:12px 14px 0">
          <div style="width:28px;height:28px;border-radius:50%;background:#B85C38;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px">P</div>
          <div style="font-weight:700;font-size:13px;color:#382C22">Penny checked this price</div>
          <button id="penny-close" style="margin-left:auto;border:0;background:none;font-size:18px;color:#999;cursor:pointer;line-height:1">×</button>
        </div>
        <div style="padding:10px 14px 14px">
          <div style="font-size:17px;font-weight:800;color:${mood.color};line-height:1.25">${mood.emoji} ${result.action}</div>
          <div style="margin-top:6px;font-size:13px;color:#382C22;font-weight:600">${result.headline}</div>
          <div style="margin-top:4px;font-size:12.5px;color:#555;line-height:1.45">${result.subline}</div>
          <div style="margin-top:8px;font-size:12px;color:#555">A real deal on this: <b>${money(good)} or less</b> · jackpot: <b>${money(great)}</b></div>
          <div style="margin-top:10px;display:flex;align-items:center;gap:6px;font-size:12px;color:#555">
            usually costs${estNote}: $<input id="penny-usual" type="number" value="${usual}" style="width:64px;border:1px solid #ddd;border-radius:8px;padding:4px 6px;font-weight:700">
            <button id="penny-recheck" style="border:0;background:#382C22;color:#fff;border-radius:999px;padding:5px 10px;font-size:11px;font-weight:700;cursor:pointer">re-check</button>
          </div>
          <div style="margin-top:10px;display:flex;gap:10px;flex-wrap:wrap;font-size:11.5px">
            <a href="https://www.google.com/search?tbm=shop&q=${q}" target="_blank" rel="noopener" style="color:#B85C38;font-weight:700;text-decoration:underline">Can another store beat it?</a>
            <a href="${SITE}/deal-check.html" target="_blank" rel="noopener" style="color:#999;text-decoration:underline">bestdealsonline.us</a>
          </div>
          <div style="margin-top:8px;font-size:10px;color:#aaa;line-height:1.4">Estimate based on the prices shown on this page. As an Amazon Associate, BestDealsOnline earns from qualifying purchases.</div>
        </div>
      </div>`
  }

  function draw() {
    shadow.innerHTML = verdictHtml()
    shadow.getElementById('penny-close').addEventListener('click', () => host.remove())
    shadow.getElementById('penny-recheck').addEventListener('click', () => {
      const v = Number(shadow.getElementById('penny-usual').value)
      if (Number.isFinite(v) && v > 0) {
        usual = v
        estimated = false
        draw()
      }
    })
  }

  draw()
  document.documentElement.appendChild(host)
}

function main() {
  const page = readPage()
  if (!page.price) return // not a normal product page; stay silent
  render(page)
}

// Amazon renders late sometimes; try now, retry once shortly after.
if (document.querySelector('#productTitle')) main()
else setTimeout(main, 1500)
