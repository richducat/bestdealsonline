import { dealTruthScore } from './dealtruth.js'

// Shared logic for the DealTruth checker — used by the homepage React widget
// and (copied to /assets/ at build time) by the standalone /deal-check.html
// page, so both always run the exact same engine and speak with one voice.

const DAY_MS = 24 * 60 * 60 * 1000

// Deterministic seeded PRNG so the example history is stable across
// re-renders instead of jittering on every slider move.
function seededRandom(seed) {
  let s = seed % 2147483647
  if (s <= 0) s += 2147483646
  return () => {
    s = (s * 16807) % 2147483647
    return (s - 1) / 2147483646
  }
}

// Builds a plausible 120-day price history ending at todayPrice, mostly
// hovering near typicalPrice with small daily noise plus a short promo
// dip — fed into the real dealTruthScore() algorithm so the checker runs
// genuine scoring logic on a clearly-labeled example.
export function buildExampleHistory(typicalPrice, todayPrice) {
  const rand = seededRandom(Math.round(typicalPrice * 97 + todayPrice * 13) || 1)
  const days = 120
  const history = []
  const now = Date.now()
  const dipStart = 20 + Math.floor(rand() * 60)
  const dipDepth = 0.06 + rand() * 0.08
  for (let i = days; i >= 1; i -= 1) {
    const noise = (rand() - 0.5) * 0.05
    const inDip = i <= dipStart && i > dipStart - 4
    const factor = 1 + noise - (inDip ? dipDepth : 0)
    const price = Math.max(1, Math.round(typicalPrice * factor * 100) / 100)
    history.push({ price, timestamp: now - i * DAY_MS })
  }
  history.push({ price: Math.max(1, Math.round(todayPrice * 100) / 100), timestamp: now })
  return history
}

// Verdict tiers. The engine score stays visible, but the tier drives
// color and headline so the tool never contradicts itself (the old demo
// could say "this isn't a deal" and "Buy now" in the same breath).
export const TIERS = {
  fake: { key: 'fake', label: 'Fake discount', mood: 'bad' },
  overpriced: { key: 'overpriced', label: 'Overpriced', mood: 'bad' },
  everyday: { key: 'everyday', label: 'Everyday price', mood: 'flat' },
  mild: { key: 'mild', label: 'Small dip', mood: 'flat' },
  solid: { key: 'solid', label: 'Solid deal', mood: 'good' },
  strong: { key: 'strong', label: 'Strong deal', mood: 'great' },
  verify: { key: 'verify', label: 'Almost too good', mood: 'caution' },
}

export function money(n) {
  const abs = Math.abs(n)
  return abs >= 100 ? `$${Math.round(abs)}` : `$${abs.toFixed(abs % 1 ? 2 : 0)}`
}

// checkDeal(typical, today, options)
//   typical  — what the product actually sells for day to day
//   today    — the price on screen right now
//   options.claimedWas — Amazon's crossed-out "was/list" price, if entered.
//     When present we compare the *claimed* discount against the *real*
//     one and call out sticker theater explicitly.
export function checkDeal(typical, today, options = {}) {
  const claimedWas = Number.isFinite(options.claimedWas) && options.claimedWas > 0 ? options.claimedWas : null

  const priceHistory = buildExampleHistory(typical, today)
  const engine = dealTruthScore({
    title: 'Example product',
    rating: 4.3,
    reviews: 2400,
    priceHistory,
    offer: {
      itemPrice: today,
      isPrime: true,
      soldByAmazon: true,
      shipsFromAmazon: true,
      ...(claimedWas ? { listPrice: claimedWas } : {}),
    },
  })

  const delta = typical - today // positive = real savings
  const discount = typical > 0 ? delta / typical : 0
  const claimedDiscount = claimedWas && claimedWas > 0 ? (claimedWas - today) / claimedWas : null

  // "Fake discount": the sticker claims a big cut but the price barely
  // moved vs what it actually sells for (or got worse). The claimed "was"
  // being far above the real typical price is the tell.
  const claimGap = claimedDiscount != null ? claimedDiscount - Math.max(0, discount) : null
  const isFake =
    claimedDiscount != null &&
    claimedDiscount >= 0.15 &&
    (discount < 0.05 || (claimedWas / Math.max(1, typical) >= 1.35 && discount < 0.15))

  let tier
  if (isFake) tier = TIERS.fake
  else if (discount < -0.02) tier = TIERS.overpriced
  else if (discount < 0.05) tier = TIERS.everyday
  else if (discount < 0.15) tier = TIERS.mild
  else if (discount < 0.35) tier = TIERS.solid
  else if (discount <= 0.6) tier = TIERS.strong
  else tier = TIERS.verify

  const pct = Math.round(Math.abs(discount) * 100)
  const claimedPct = claimedDiscount != null ? Math.round(claimedDiscount * 100) : null

  let headline
  let subline

  if (tier.key === 'fake') {
    headline = `That "${claimedPct}% off" is sticker theater`
    subline =
      discount < 0
        ? `The sale tag says ${claimedPct}% off, but against what this actually sells for you'd still overpay ${money(delta)}. The "was" price is doing the lying.`
        : `The sale tag says ${claimedPct}% off, but the real drop vs its everyday price is ${pct}%. The discount lives in the sticker, not the price.`
  } else if (tier.key === 'overpriced') {
    headline = `You'd overpay ${money(delta)}`
    subline = `Today's price is ${pct}% above what this normally sells for. Walk away — this is how "sale season" quietly costs you money.`
  } else if (tier.key === 'everyday') {
    headline = 'This is just the normal price'
    subline = 'No real savings here. If you need it, buy it — but nothing about this price should rush you.'
  } else if (tier.key === 'mild') {
    headline = `A small dip — saves you ${money(delta)}`
    subline = `${pct}% off is inside this product's normal wobble. It hits this price all the time; you're not missing anything by waiting.`
  } else if (tier.key === 'solid') {
    headline = `A real deal — saves you ${money(delta)}`
    subline = `${pct}% below its usual price is a genuine discount, not sticker theater.`
  } else if (tier.key === 'strong') {
    headline = `A strong drop — saves you ${money(delta)}`
    subline = `${pct}% off is the kind of price that shows up a few times a year. If you were going to buy it anyway, this is the moment.`
  } else {
    headline = `${pct}% off is almost too good`
    subline = `Discounts this deep are sometimes real clearance — and sometimes an inflated "was" price, a counterfeit, or a hijacked listing. Check the seller name and recent reviews before you jump.`
  }

  // Percentile sentence, All-Aboard-Deals style: score semantics anyone
  // can repeat to a friend.
  const percentile = engine.percentile180
  const beatsPct = percentile != null ? Math.round((1 - percentile) * 100) : null
  const percentileLine =
    beatsPct != null && discount >= 0.05
      ? `Today's price beats ${beatsPct}% of the last 6 months of prices in this example.`
      : null

  // Only surface the engine's buy/wait call when it agrees with the tier —
  // never "Buy now" on something we just said isn't a deal.
  const showDecision =
    (tier.key === 'solid' || tier.key === 'strong') && engine.decision?.text ? engine.decision : null

  return {
    engine,
    score: engine.score,
    tier,
    discount,
    claimedDiscount,
    claimGap,
    delta,
    headline,
    subline,
    percentileLine,
    decision: showDecision,
    history: priceHistory,
    baseline: engine.baseline90,
    lines: {
      discount: engine.explanations.discountLine,
      rarity: engine.explanations.rarityLine,
      confidence: engine.explanations.confidenceLine,
    },
  }
}

// Pulls an ASIN out of a pasted Amazon URL so we can hand the user a
// price-history verification link without any API.
export function parseAmazonUrl(raw) {
  const text = String(raw || '').trim()
  if (!text) return null
  const asinMatch = text.match(/(?:\/dp\/|\/gp\/product\/|\/gp\/aw\/d\/|asin=)([A-Z0-9]{10})(?:[/?&#]|$)/i)
  if (!asinMatch) return null
  const asin = asinMatch[1].toUpperCase()

  // Human-ish product words from the slug, e.g. /Anker-USB-C-Charger/dp/...
  let slugWords = null
  const slugMatch = text.match(/amazon\.[a-z.]+\/([^/]{4,})\/dp\//i)
  if (slugMatch && !/^(dp|gp)$/i.test(slugMatch[1])) {
    slugWords = decodeURIComponent(slugMatch[1]).replace(/-/g, ' ').replace(/\s+/g, ' ').trim()
  }

  return {
    asin,
    slugWords,
    camelUrl: `https://camelcamelcamel.com/product/${asin}`,
    keepaUrl: `https://keepa.com/#!product/1-${asin}`,
  }
}

// Compact share/copy text for a verdict.
export function verdictShareText(typical, today, result) {
  const claimed =
    result.claimedDiscount != null ? ` Sticker claimed ${Math.round(result.claimedDiscount * 100)}% off.` : ''
  const reality =
    result.delta >= 0
      ? `Real savings vs its usual price: ${money(result.delta)}.`
      : `You'd actually overpay ${money(result.delta)}.`
  return `DealTruth check: usually $${typical}, today $${today} — ${result.tier.label} (${result.score}/100).${claimed} ${reality} bestdealsonline.us/deal-check.html`
}

// localStorage running tally — the "you can't shop without this" hook.
// Counts checks and dollars of overpaying dodged (fake/overpriced
// verdicts where the tool told you not to bite).
const TALLY_KEY = 'dealtruth-tally-v1'

export function readTally() {
  try {
    const raw = localStorage.getItem(TALLY_KEY)
    if (!raw) return { checks: 0, avoided: 0 }
    const parsed = JSON.parse(raw)
    return {
      checks: Number.isFinite(parsed.checks) ? parsed.checks : 0,
      avoided: Number.isFinite(parsed.avoided) ? parsed.avoided : 0,
    }
  } catch {
    return { checks: 0, avoided: 0 }
  }
}

export function recordCheck(result) {
  try {
    const tally = readTally()
    tally.checks += 1
    if (result.tier.key === 'overpriced' || (result.tier.key === 'fake' && result.delta < 0)) {
      tally.avoided += Math.abs(result.delta)
    }
    localStorage.setItem(TALLY_KEY, JSON.stringify(tally))
    return tally
  } catch {
    return readTally()
  }
}
