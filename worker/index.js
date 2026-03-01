const DEFAULT_CATEGORIES = ['Electronics', 'Home', 'Kitchen', 'Tools', 'Kids', 'Beauty', 'Fitness', 'Pets']
const DEFAULT_LIMIT = 300
const MAX_LIMIT = 500
const DAY_MS = 24 * 60 * 60 * 1000

const DEFAULT_WEIGHTS = {
  realDiscount: 0.35,
  rarity: 0.2,
  quality: 0.2,
  trust: 0.15,
  urgency: 0.1,
}

const CORS_HEADERS = {
  'access-control-allow-origin': '*',
  'access-control-allow-methods': 'GET,POST,OPTIONS',
  'access-control-allow-headers': 'content-type,x-admin-key',
}

function clamp(value, min = 0, max = 1) {
  if (!Number.isFinite(value)) return min
  return Math.min(max, Math.max(min, value))
}

function toNumber(value) {
  if (typeof value === 'number') return Number.isFinite(value) ? value : null
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) return null
    const parsed = Number(trimmed.replace(/[$,]/g, ''))
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
}

function toBoolean(value) {
  if (typeof value === 'boolean') return value
  if (typeof value === 'number') return value !== 0
  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase()
    return normalized === '1' || normalized === 'true' || normalized === 'yes'
  }
  return false
}

function parseTimestamp(value) {
  if (typeof value === 'number' && Number.isFinite(value)) {
    if (value > 1e12) return value
    if (value > 1e9) return value * 1000
  }
  if (typeof value === 'string') {
    const ts = Date.parse(value)
    return Number.isFinite(ts) ? ts : null
  }
  return null
}

function isoNow() {
  return new Date().toISOString()
}

function normalizeCategory(value) {
  const text = String(value || '').trim()
  return text || 'Home'
}

function parseCategories(value) {
  if (!value) return []
  return String(value)
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean)
}

function normalizeLimit(value, fallback = DEFAULT_LIMIT) {
  const parsed = Number.parseInt(String(value || ''), 10)
  if (!Number.isFinite(parsed) || parsed <= 0) return fallback
  return Math.min(MAX_LIMIT, parsed)
}

function jsonResponse(payload, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      ...CORS_HEADERS,
      ...extraHeaders,
    },
  })
}

function normalizeWeights(raw) {
  const defaults = { ...DEFAULT_WEIGHTS }
  if (!raw || typeof raw !== 'object') return defaults

  const merged = {
    realDiscount: toNumber(raw.realDiscount) ?? toNumber(raw.real_discount_weight) ?? defaults.realDiscount,
    rarity: toNumber(raw.rarity) ?? toNumber(raw.rarity_weight) ?? defaults.rarity,
    quality: toNumber(raw.quality) ?? toNumber(raw.quality_weight) ?? defaults.quality,
    trust: toNumber(raw.trust) ?? toNumber(raw.trust_weight) ?? defaults.trust,
    urgency: toNumber(raw.urgency) ?? toNumber(raw.urgency_weight) ?? defaults.urgency,
  }

  const total =
    Math.max(0, merged.realDiscount) +
    Math.max(0, merged.rarity) +
    Math.max(0, merged.quality) +
    Math.max(0, merged.trust) +
    Math.max(0, merged.urgency)

  if (!Number.isFinite(total) || total <= 0) return defaults

  return {
    realDiscount: Math.max(0, merged.realDiscount) / total,
    rarity: Math.max(0, merged.rarity) / total,
    quality: Math.max(0, merged.quality) / total,
    trust: Math.max(0, merged.trust) / total,
    urgency: Math.max(0, merged.urgency) / total,
  }
}

function roundPct(value) {
  return Math.round((value || 0) * 100)
}

function median(values) {
  if (!Array.isArray(values) || !values.length) return null
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid]
}

function trimmedMedian(values, trimPercent = 0.05) {
  if (!Array.isArray(values) || !values.length) return null
  const sorted = [...values].sort((a, b) => a - b)
  const trimCount = Math.floor(sorted.length * clamp(trimPercent, 0, 0.45))
  const trimmed = sorted.slice(trimCount, sorted.length - trimCount)
  return median(trimmed.length ? trimmed : sorted)
}

function percentileRank(values, value) {
  if (!Array.isArray(values) || !values.length || !Number.isFinite(value)) return null
  const lessOrEqual = values.filter((entry) => entry <= value).length
  return clamp(lessOrEqual / values.length, 0, 1)
}

function stdDevLog(values) {
  const clean = values.filter((entry) => Number.isFinite(entry) && entry > 0)
  if (clean.length < 2) return 0

  const logs = clean.map((entry) => Math.log(entry))
  const mean = logs.reduce((sum, entry) => sum + entry, 0) / logs.length
  const variance = logs.reduce((sum, entry) => sum + (entry - mean) ** 2, 0) / logs.length
  return Math.sqrt(variance)
}

function amountFrom(value, basePrice = 0, defaultIsPercent = false) {
  if (value == null) return 0

  if (typeof value === 'object') {
    if (value.amount != null || value.value != null) {
      return Math.max(0, toNumber(value.amount ?? value.value) ?? 0)
    }
    if (value.percent != null || value.percentage != null || value.pct != null) {
      const pct = toNumber(value.percent ?? value.percentage ?? value.pct) ?? 0
      return Math.max(0, (basePrice * pct) / 100)
    }
  }

  if (typeof value === 'string' && value.includes('%')) {
    const pct = toNumber(value.replace('%', '')) ?? 0
    return Math.max(0, (basePrice * pct) / 100)
  }

  const numeric = toNumber(value) ?? 0
  if (defaultIsPercent) {
    const pct = numeric > 1 ? numeric : numeric * 100
    return Math.max(0, (basePrice * pct) / 100)
  }

  return Math.max(0, numeric)
}

function normalizeEffectivePrice(source) {
  const offer = source?.offer || source || {}
  const itemPrice =
    toNumber(offer.effectivePrice) ??
    toNumber(offer.itemPrice) ??
    toNumber(offer.buyBoxPrice) ??
    toNumber(offer.price) ??
    toNumber(offer.listingPrice) ??
    toNumber(offer.currentPrice)

  if (!Number.isFinite(itemPrice) || itemPrice <= 0) return null

  const shipping =
    toNumber(offer.shipping) ?? toNumber(offer.shippingPrice) ?? toNumber(offer.shippingCost) ?? 0

  const coupon = amountFrom(offer.coupon ?? offer.couponAmount, itemPrice, false) + amountFrom(offer.couponPercent ?? offer.couponPct, itemPrice, true)

  const promoDiscount = amountFrom(offer.promoDiscount ?? offer.promoDiscounts ?? offer.promotion, itemPrice, false)

  const subscribeSave =
    amountFrom(offer.subscribeSave ?? offer.subscribeAndSaveAmount, itemPrice, false) +
    amountFrom(offer.subscribeSavePercent ?? offer.subscribeAndSavePercent, itemPrice, true)

  const effective = itemPrice + shipping - coupon - promoDiscount - subscribeSave
  return Math.max(0, Number(effective.toFixed(2)))
}

function qualityScore(ratingValue, reviewCountValue) {
  const rating = toNumber(ratingValue) ?? 0
  const reviews = toNumber(reviewCountValue) ?? 0

  const ratingNorm = clamp((rating - 3.2) / 1.8, 0, 1)
  const reviewsNorm = clamp(Math.log10(Math.max(0, reviews) + 1) / Math.log10(50000 + 1), 0, 1)

  return clamp(0.7 * ratingNorm + 0.3 * reviewsNorm)
}

function sellerTrustScore(offer) {
  const source = offer?.offer || offer || {}
  const isPrime = toBoolean(source.isPrime ?? source.prime)
  const isFba = toBoolean(source.isFba ?? source.fba)
  const shipsFromAmazon = toBoolean(source.shipsFromAmazon || source.shipsFrom === 'Amazon')
  const soldByAmazon = toBoolean(source.soldByAmazon || source.soldBy === 'Amazon')

  const sellerRating = toNumber(source.sellerRating) ?? 0
  const sellerRatingCount =
    toNumber(source.sellerRatingCount) ?? toNumber(source.sellerCount) ?? toNumber(source.sellerReviewCount) ?? 0

  const sellerRatingNorm =
    sellerRating > 1 ? clamp((sellerRating - 80) / 20, 0, 1) : clamp((sellerRating - 0.8) / 0.2, 0, 1)
  const sellerCountNorm = clamp(Math.log10(Math.max(0, sellerRatingCount) + 1) / Math.log10(5000 + 1), 0, 1)

  let score = 0.25
  if (isPrime) score += 0.2
  if (isFba) score += 0.15
  if (shipsFromAmazon) score += 0.15
  if (soldByAmazon) score += 0.15

  score += 0.2 * sellerRatingNorm + 0.1 * sellerCountNorm

  return clamp(score)
}

function listingAgeDays(item) {
  const source = item?.offer || item || {}
  const explicit =
    toNumber(source.brandAgeDays) ?? toNumber(source.listingAgeDays) ?? toNumber(source.sellerAgeDays)
  if (Number.isFinite(explicit) && explicit >= 0) return explicit

  const created =
    parseTimestamp(source.createdAt) ?? parseTimestamp(source.firstSeenAt) ?? parseTimestamp(source.listedAt)
  if (!Number.isFinite(created)) return null

  return Math.max(0, Math.floor((Date.now() - created) / DAY_MS))
}

function scamRisk({ realDiscount, reviewCount, listPrice, baseline90, volatility, ageDays }) {
  let penalty = 0

  if (realDiscount > 0.6 && reviewCount < 80) penalty += 0.35
  if (realDiscount > 0.45 && Number.isFinite(ageDays) && ageDays < 45) penalty += 0.2
  if (realDiscount > 0.4 && volatility > 0.3) penalty += 0.25

  if (Number.isFinite(listPrice) && Number.isFinite(baseline90) && baseline90 > 0) {
    const anchorRatio = listPrice / baseline90
    if (anchorRatio > 1.6) penalty += 0.2
  }

  return clamp(penalty)
}

function urgencyScore({ rarity, volatility, timeAtCurrentPriceHours }) {
  const volatilityNorm = clamp(volatility / 0.35)
  const justChanged = clamp(1 - (timeAtCurrentPriceHours || 0) / 168)
  return clamp(0.5 * rarity + 0.3 * (1 - volatilityNorm) + 0.2 * justChanged)
}

function lastPriceRunHours(historyEntries, currentPrice) {
  if (!Array.isArray(historyEntries) || !historyEntries.length || !Number.isFinite(currentPrice)) return null

  const withTs = historyEntries.filter((entry) => Number.isFinite(entry.timestamp))
  if (!withTs.length) return null

  const sorted = [...withTs].sort((a, b) => a.timestamp - b.timestamp)
  const latest = sorted[sorted.length - 1]
  let oldestTs = latest.timestamp

  for (let i = sorted.length - 1; i >= 0; i -= 1) {
    const entry = sorted[i]
    const tolerance = Math.max(0.01, currentPrice * 0.003)
    if (Math.abs(entry.price - currentPrice) > tolerance) break
    oldestTs = entry.timestamp
  }

  return Math.max(0, (latest.timestamp - oldestTs) / (60 * 60 * 1000))
}

function dropStats(historyEntries, days = 60) {
  if (!Array.isArray(historyEntries) || historyEntries.length < 2) return { drops: 0, avgDropSize: 0 }

  const cutoff = Date.now() - days * DAY_MS
  const recent = historyEntries
    .filter((entry) => !Number.isFinite(entry.timestamp) || entry.timestamp >= cutoff)
    .sort((a, b) => (a.timestamp ?? 0) - (b.timestamp ?? 0))

  if (recent.length < 2) return { drops: 0, avgDropSize: 0 }

  let drops = 0
  let sum = 0
  for (let i = 1; i < recent.length; i += 1) {
    const prev = recent[i - 1].price
    const curr = recent[i].price
    if (!(Number.isFinite(prev) && Number.isFinite(curr) && prev > 0 && curr > 0)) continue
    if (curr < prev) {
      drops += 1
      sum += (prev - curr) / prev
    }
  }

  return { drops, avgDropSize: drops ? sum / drops : 0 }
}

function buyOrWait({ percentile180, volatility, dropsLast60d, avgDropSize, timeAtCurrentPriceHours, historyCount }) {
  if (historyCount < 12 || percentile180 == null) {
    return { label: null, dropChance7dPct: null, text: null }
  }

  let probability = 0.42

  if (percentile180 <= 0.1) probability -= 0.24
  else if (percentile180 <= 0.2) probability -= 0.1

  if (dropsLast60d >= 8) probability += 0.2
  else if (dropsLast60d >= 4) probability += 0.1

  if (avgDropSize >= 0.12) probability += 0.12
  else if (avgDropSize >= 0.06) probability += 0.06

  if (Number.isFinite(timeAtCurrentPriceHours) && timeAtCurrentPriceHours < 24) probability -= 0.05

  if (volatility <= 0.1) probability -= 0.08
  if (volatility >= 0.25) probability += 0.08

  probability = clamp(probability, 0.02, 0.98)
  const chance = Math.round(probability * 100)

  if (probability <= 0.25) {
    return { label: 'Buy now', dropChance7dPct: chance, text: `Buy now (only ~${chance}% chance it drops more in 7 days)` }
  }

  if (probability >= 0.55) {
    return { label: 'Wait', dropChance7dPct: chance, text: `Wait (about ~${chance}% chance it drops more in 7 days)` }
  }

  return { label: 'Either', dropChance7dPct: chance, text: `Either way (~${chance}% chance of a better price in 7 days)` }
}

function confidenceLabel({ historyCount, hasNinetyDay, hasOneEightyDay, volatility, trust, isPrime, priceKnown }) {
  const reasons = []
  let level = 'Low'

  if (!priceKnown) {
    return { level, reason: 'missing current price data', text: `${level} (missing current price data)` }
  }

  if (hasOneEightyDay && historyCount >= 45 && volatility <= 0.12 && trust >= 0.55) {
    level = 'High'
    reasons.push('stable price history')
    if (isPrime) reasons.push('Prime offer')
  } else if (hasNinetyDay && historyCount >= 20 && trust >= 0.4) {
    level = 'Medium'
    reasons.push('usable price history')
    if (isPrime) reasons.push('Prime offer')
  } else {
    if (historyCount < 20) reasons.push('limited price history')
    if (volatility > 0.25) reasons.push('high price volatility')
    if (!isPrime) reasons.push('offer quality unknown')
  }

  if (!reasons.length) reasons.push('balanced signal quality')

  return { level, reason: reasons.join(' + '), text: `${level} (${reasons.join(' + ')})` }
}

function buildHistoryEntries(snapshotRows, externalHistory) {
  const entries = []

  for (const row of snapshotRows || []) {
    const price = toNumber(row.effective_price)
    if (!Number.isFinite(price) || price <= 0) continue
    entries.push({
      price,
      timestamp: parseTimestamp(row.observed_at),
    })
  }

  if (Array.isArray(externalHistory)) {
    for (const entry of externalHistory) {
      if (typeof entry === 'number') {
        if (entry > 0) entries.push({ price: entry, timestamp: null })
        continue
      }
      if (!entry || typeof entry !== 'object') continue
      const price =
        toNumber(entry.effectivePrice) ?? toNumber(entry.price) ?? toNumber(entry.value) ?? toNumber(entry.amount)
      if (!Number.isFinite(price) || price <= 0) continue
      entries.push({
        price,
        timestamp:
          parseTimestamp(entry.timestamp) ?? parseTimestamp(entry.ts) ?? parseTimestamp(entry.at) ?? parseTimestamp(entry.date),
      })
    }
  }

  return entries.sort((a, b) => (a.timestamp ?? 0) - (b.timestamp ?? 0))
}

function buildDealTruth(item, historyEntries, weights) {
  const effectivePriceNow = normalizeEffectivePrice(item)
  const fallbackPrice = toNumber(item.price)
  const currentPrice = Number.isFinite(effectivePriceNow) ? effectivePriceNow : Number.isFinite(fallbackPrice) ? fallbackPrice : null

  const withPrice = historyEntries.filter((entry) => Number.isFinite(entry.price) && entry.price > 0)
  const withTs = withPrice.filter((entry) => Number.isFinite(entry.timestamp))
  const cutoff90 = Date.now() - 90 * DAY_MS
  const cutoff180 = Date.now() - 180 * DAY_MS

  const values90 = (withTs.length ? withTs.filter((entry) => entry.timestamp >= cutoff90) : withPrice).map((entry) => entry.price)
  const values180 = (withTs.length ? withTs.filter((entry) => entry.timestamp >= cutoff180) : withPrice).map((entry) => entry.price)

  const baseline90 = trimmedMedian(values90, 0.05)
  const hasBaseline = Number.isFinite(baseline90) && baseline90 > 0
  const has180 = values180.length > 0

  const realDiscountPct =
    hasBaseline && Number.isFinite(currentPrice)
      ? (baseline90 - currentPrice) / baseline90
      : null

  const percentile180 =
    has180 && Number.isFinite(currentPrice)
      ? percentileRank(values180, currentPrice)
      : null

  const rarity = percentile180 == null ? 0 : clamp(1 - percentile180)
  const volatility = stdDevLog(values180)

  const quality = qualityScore(item.rating, item.reviews)
  const trust = sellerTrustScore(item)

  const reviewCount = toNumber(item.reviews) ?? 0
  const listPrice = toNumber(item.listPrice) ?? toNumber(item.msrp) ?? toNumber(item.wasPrice)
  const ageDays = listingAgeDays(item)

  const scamPenalty = scamRisk({
    realDiscount: Math.max(0, realDiscountPct ?? 0),
    reviewCount,
    listPrice,
    baseline90,
    volatility,
    ageDays,
  })

  const runHours = lastPriceRunHours(historyEntries, currentPrice)
  const urgency = urgencyScore({ rarity, volatility, timeAtCurrentPriceHours: runHours })

  const boundedDiscount = clamp(realDiscountPct ?? 0)

  const scoreRaw =
    100 *
      (weights.realDiscount * boundedDiscount +
        weights.rarity * rarity +
        weights.quality * quality +
        weights.trust * trust +
        weights.urgency * urgency) -
    100 * clamp(scamPenalty)

  const score = Math.round(clamp(scoreRaw, 0, 100))

  const confidence = confidenceLabel({
    historyCount: withPrice.length,
    hasNinetyDay: hasBaseline,
    hasOneEightyDay: has180,
    volatility,
    trust,
    isPrime: toBoolean(item.isPrime ?? item.prime),
    priceKnown: Number.isFinite(currentPrice),
  })

  const stats = dropStats(historyEntries, 60)
  const decision = buyOrWait({
    percentile180,
    volatility,
    dropsLast60d: stats.drops,
    avgDropSize: stats.avgDropSize,
    timeAtCurrentPriceHours: runHours,
    historyCount: withPrice.length,
  })

  const notMeaningfulDeal =
    realDiscountPct == null ? false : realDiscountPct < 0.05 || (percentile180 != null && percentile180 > 0.35)

  const discountLine =
    realDiscountPct == null
      ? 'Real discount: unavailable (building 90-day baseline)'
      : realDiscountPct >= 0
        ? `Real discount: ${Math.round(Math.abs(realDiscountPct) * 100)}% below 90-day median`
        : `Real discount: ${Math.round(Math.abs(realDiscountPct) * 100)}% above 90-day median`

  const rarityLine =
    percentile180 == null
      ? 'Rarity: not enough history yet'
      : percentile180 <= 0.03
        ? 'Rarity: lowest price in 180 days'
        : percentile180 <= 0.1
          ? 'Rarity: near 180-day low'
          : percentile180 <= 0.25
            ? `Rarity: lower than ~${Math.round((1 - percentile180) * 100)}% of 180-day prices`
            : `Rarity: not rare (~${Math.round(percentile180 * 100)}th percentile in 180 days)`

  return {
    score,
    effectivePriceNow: currentPrice,
    baseline90,
    realDiscountPct,
    percentile180,
    rarity,
    volatility,
    quality,
    trust,
    urgency,
    scamPenalty,
    confidence,
    decision,
    notMeaningfulDeal,
    components: {
      realDiscountPct: roundPct(realDiscountPct ?? 0),
      rarityScore: roundPct(rarity),
      qualityScore: roundPct(quality),
      sellerTrustScore: roundPct(trust),
      urgencyScore: roundPct(urgency),
      scamPenalty: roundPct(scamPenalty),
      dropChance7dPct: decision.dropChance7dPct,
      dropsLast60d: stats.drops,
      avgDropSizePct: roundPct(stats.avgDropSize),
    },
    explanations: {
      scoreLine: `DealTruth Score: ${score}/100`,
      discountLine,
      rarityLine,
      confidenceLine: `Confidence: ${confidence.text}`,
      decisionLine: decision.text,
    },
  }
}

function normalizeFeedItem(raw, fallbackCategory) {
  if (!raw || typeof raw !== 'object') return null

  const asin = String(raw.asin || raw.id || '').trim()
  if (!asin) return null

  const offer = raw.offer && typeof raw.offer === 'object' ? raw.offer : raw
  const observedAt = raw.observedAt || raw.observed_at || isoNow()

  return {
    asin,
    observedAt,
    title: String(raw.title || '').trim() || null,
    description: String(raw.description || '').trim() || null,
    brand: String(raw.brand || '').trim() || null,
    category: normalizeCategory(raw.category || fallbackCategory),
    imageUrl: String(raw.imageUrl || raw.image_url || '').trim() || null,
    affiliateLink: String(raw.affiliateLink || raw.affiliate_link || '').trim() || null,
    merchant: String(raw.merchant || 'Amazon').trim() || 'Amazon',
    iconName: String(raw.iconName || raw.icon_name || '').trim() || null,
    rating: toNumber(raw.rating),
    reviews: toNumber(raw.reviews),
    priceHistory: Array.isArray(raw.priceHistory) ? raw.priceHistory : null,
    offer: {
      sellerId: String(offer.sellerId || offer.seller_id || '').trim() || '',
      sellerName: String(offer.sellerName || offer.seller_name || '').trim() || null,
      sellerRating: toNumber(offer.sellerRating || offer.seller_rating),
      sellerRatingCount: toNumber(offer.sellerRatingCount || offer.seller_rating_count || offer.sellerCount),
      isPrime: toBoolean(offer.isPrime ?? offer.prime),
      isFba: toBoolean(offer.isFba ?? offer.fba),
      shipsFromAmazon: toBoolean(offer.shipsFromAmazon),
      soldByAmazon: toBoolean(offer.soldByAmazon),
      condition: String(offer.condition || 'new').trim() || 'new',
      itemPrice: toNumber(offer.itemPrice ?? offer.price ?? offer.buyBoxPrice ?? offer.listingPrice),
      shipping: toNumber(offer.shipping ?? offer.shippingPrice ?? offer.shippingCost) ?? 0,
      coupon: amountFrom(offer.coupon ?? offer.couponAmount, toNumber(offer.price) ?? 0),
      promoDiscounts: amountFrom(offer.promoDiscount ?? offer.promoDiscounts ?? offer.promotion, toNumber(offer.price) ?? 0),
      subscribeSave: amountFrom(offer.subscribeSave ?? offer.subscribeAndSaveAmount, toNumber(offer.price) ?? 0),
      effectivePrice: normalizeEffectivePrice(offer),
      currency: String(offer.currency || raw.currency || 'USD').trim() || 'USD',
      raw: offer,
    },
  }
}

async function listCategoryWeightOverrides(db) {
  const { results } = await db
    .prepare(
      `SELECT category, real_discount_weight, rarity_weight, quality_weight, trust_weight, urgency_weight, updated_at
       FROM category_weight_overrides`
    )
    .all()
  return results || []
}

function parseEnvWeightOverrides(env) {
  if (!env?.CATEGORY_WEIGHT_OVERRIDES_JSON) return new Map()
  try {
    const parsed = JSON.parse(env.CATEGORY_WEIGHT_OVERRIDES_JSON)
    const map = new Map()
    for (const [category, weights] of Object.entries(parsed || {})) {
      map.set(normalizeCategory(category), normalizeWeights(weights))
    }
    return map
  } catch {
    return new Map()
  }
}

function buildDbOverrideMap(rows) {
  const map = new Map()
  for (const row of rows || []) {
    map.set(normalizeCategory(row.category), normalizeWeights(row))
  }
  return map
}

function getWeightsForCategory(category, dbOverrides, envOverrides) {
  const key = normalizeCategory(category)
  if (dbOverrides.has(key)) return dbOverrides.get(key)
  if (envOverrides.has(key)) return envOverrides.get(key)
  return DEFAULT_WEIGHTS
}

async function requireDb(env) {
  if (!env?.DB) {
    throw new Error('D1 binding `DB` is not configured')
  }
  return env.DB
}

async function fetchApprovedFeedItems(env, { categories, limit }) {
  const sourceUrl = env.PAAPI_PROXY_URL || env.DEALS_FEED_URL || ''
  if (!sourceUrl) {
    return {
      items: [],
      source: 'none',
      warning: 'No PAAPI_PROXY_URL or DEALS_FEED_URL configured',
    }
  }

  const url = new URL(sourceUrl)
  if (categories.length) {
    url.searchParams.set('categories', categories.join(','))
  }
  url.searchParams.set('limit', String(limit))

  const headers = {
    accept: 'application/json',
  }
  if (env.DEALS_FEED_BEARER_TOKEN) {
    headers.authorization = `Bearer ${env.DEALS_FEED_BEARER_TOKEN}`
  }

  const response = await fetch(url.toString(), { headers })
  if (!response.ok) {
    const body = await response.text()
    throw new Error(`feed fetch failed (${response.status}): ${body.slice(0, 300)}`)
  }

  const payload = await response.json()
  const items = Array.isArray(payload?.items) ? payload.items : []

  return {
    items,
    source: sourceUrl,
    warning: null,
  }
}

async function upsertAsin(db, item, observedAt) {
  await db
    .prepare(
      `INSERT INTO asins (
          asin, title, description, brand, category, image_url, affiliate_link, merchant, icon_name, rating, reviews, first_seen_at, last_seen_at, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
        ON CONFLICT(asin) DO UPDATE SET
          title = COALESCE(excluded.title, asins.title),
          description = COALESCE(excluded.description, asins.description),
          brand = COALESCE(excluded.brand, asins.brand),
          category = COALESCE(excluded.category, asins.category),
          image_url = COALESCE(excluded.image_url, asins.image_url),
          affiliate_link = COALESCE(excluded.affiliate_link, asins.affiliate_link),
          merchant = COALESCE(excluded.merchant, asins.merchant),
          icon_name = COALESCE(excluded.icon_name, asins.icon_name),
          rating = COALESCE(excluded.rating, asins.rating),
          reviews = COALESCE(excluded.reviews, asins.reviews),
          last_seen_at = excluded.last_seen_at,
          status = 'active'`
    )
    .bind(
      item.asin,
      item.title,
      item.description,
      item.brand,
      item.category,
      item.imageUrl,
      item.affiliateLink,
      item.merchant,
      item.iconName,
      item.rating,
      item.reviews,
      observedAt,
      observedAt
    )
    .run()
}

async function insertOffer(db, item, observedAt) {
  const effectivePrice =
    toNumber(item.offer.effectivePrice) ??
    normalizeEffectivePrice(item.offer) ??
    toNumber(item.offer.itemPrice)

  if (!Number.isFinite(effectivePrice) || effectivePrice <= 0) {
    return { offerId: null, effectivePrice: null }
  }

  const sellerId = item.offer.sellerId || ''
  const condition = item.offer.condition || 'new'

  await db
    .prepare(
      `INSERT OR IGNORE INTO offers (
        asin, observed_at, source, seller_id, seller_name, seller_rating, seller_rating_count,
        is_prime, is_fba, ships_from_amazon, sold_by_amazon, condition,
        item_price, shipping, coupon, promo_discounts, subscribe_save, effective_price, currency, offer_json
      ) VALUES (?, ?, 'paapi', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .bind(
      item.asin,
      observedAt,
      sellerId,
      item.offer.sellerName,
      item.offer.sellerRating,
      item.offer.sellerRatingCount,
      item.offer.isPrime ? 1 : 0,
      item.offer.isFba ? 1 : 0,
      item.offer.shipsFromAmazon ? 1 : 0,
      item.offer.soldByAmazon ? 1 : 0,
      condition,
      item.offer.itemPrice,
      item.offer.shipping ?? 0,
      item.offer.coupon ?? 0,
      item.offer.promoDiscounts ?? 0,
      item.offer.subscribeSave ?? 0,
      effectivePrice,
      item.offer.currency || 'USD',
      JSON.stringify(item.offer.raw || {})
    )
    .run()

  const { results } = await db
    .prepare(
      `SELECT id FROM offers
       WHERE asin = ? AND observed_at = ? AND seller_id = ? AND condition = ?
       ORDER BY id DESC LIMIT 1`
    )
    .bind(item.asin, observedAt, sellerId, condition)
    .all()

  return {
    offerId: results?.[0]?.id ?? null,
    effectivePrice,
  }
}

async function insertPriceSnapshot(db, item, observedAt, offerId, effectivePrice) {
  if (!Number.isFinite(effectivePrice) || effectivePrice <= 0) return

  await db
    .prepare(
      `INSERT INTO price_snapshots (
        asin, observed_at, offer_id, effective_price, buy_box_price, shipping, coupon, promo_discounts, subscribe_save, currency, source
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'paapi')
      ON CONFLICT(asin, observed_at) DO UPDATE SET
        offer_id = excluded.offer_id,
        effective_price = excluded.effective_price,
        buy_box_price = excluded.buy_box_price,
        shipping = excluded.shipping,
        coupon = excluded.coupon,
        promo_discounts = excluded.promo_discounts,
        subscribe_save = excluded.subscribe_save,
        currency = excluded.currency,
        source = excluded.source`
    )
    .bind(
      item.asin,
      observedAt,
      offerId,
      effectivePrice,
      item.offer.itemPrice,
      item.offer.shipping ?? 0,
      item.offer.coupon ?? 0,
      item.offer.promoDiscounts ?? 0,
      item.offer.subscribeSave ?? 0,
      item.offer.currency || 'USD'
    )
    .run()
}

async function loadRecentPriceHistory(db, asin, days = 200) {
  const cutoff = new Date(Date.now() - days * DAY_MS).toISOString()
  const { results } = await db
    .prepare(
      `SELECT observed_at, effective_price
       FROM price_snapshots
       WHERE asin = ? AND observed_at >= ?
       ORDER BY observed_at ASC`
    )
    .bind(asin, cutoff)
    .all()

  return results || []
}

async function insertScoreSnapshot(db, asin, observedAt, score) {
  await db
    .prepare(
      `INSERT INTO score_snapshots (
         asin, observed_at, dealtruth_score, effective_price, baseline_price_90d,
         real_discount_pct, percentile_180d, rarity_score, volatility, quality_score,
         seller_trust_score, urgency_score, scam_penalty, confidence_level,
         confidence_reason, buy_wait_label, drop_chance_7d, not_meaningful_deal, components_json
       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(asin, observed_at) DO UPDATE SET
         dealtruth_score = excluded.dealtruth_score,
         effective_price = excluded.effective_price,
         baseline_price_90d = excluded.baseline_price_90d,
         real_discount_pct = excluded.real_discount_pct,
         percentile_180d = excluded.percentile_180d,
         rarity_score = excluded.rarity_score,
         volatility = excluded.volatility,
         quality_score = excluded.quality_score,
         seller_trust_score = excluded.seller_trust_score,
         urgency_score = excluded.urgency_score,
         scam_penalty = excluded.scam_penalty,
         confidence_level = excluded.confidence_level,
         confidence_reason = excluded.confidence_reason,
         buy_wait_label = excluded.buy_wait_label,
         drop_chance_7d = excluded.drop_chance_7d,
         not_meaningful_deal = excluded.not_meaningful_deal,
         components_json = excluded.components_json`
    )
    .bind(
      asin,
      observedAt,
      score.score,
      score.effectivePriceNow,
      score.baseline90,
      score.realDiscountPct,
      score.percentile180,
      score.rarity,
      score.volatility,
      score.quality,
      score.trust,
      score.urgency,
      score.scamPenalty,
      score.confidence.level,
      score.confidence.reason,
      score.decision.label,
      score.decision.dropChance7dPct,
      score.notMeaningfulDeal ? 1 : 0,
      JSON.stringify({
        ...score.components,
        weights: score.weights,
        explanations: score.explanations,
      })
    )
    .run()
}

async function ingestItems(env, rawItems, context = {}) {
  const db = await requireDb(env)
  const dbOverrides = buildDbOverrideMap(await listCategoryWeightOverrides(db))
  const envOverrides = parseEnvWeightOverrides(env)

  const summary = {
    source: context.source || 'manual',
    observedAt: isoNow(),
    seen: 0,
    accepted: 0,
    skipped: 0,
    scored: 0,
    categories: {},
    warnings: [],
  }

  for (const raw of rawItems || []) {
    summary.seen += 1

    const item = normalizeFeedItem(raw, context.fallbackCategory)
    if (!item) {
      summary.skipped += 1
      continue
    }

    const observedAt = item.observedAt || isoNow()

    await upsertAsin(db, item, observedAt)

    const offerResult = await insertOffer(db, item, observedAt)
    if (!Number.isFinite(offerResult.effectivePrice) || offerResult.effectivePrice <= 0) {
      summary.skipped += 1
      continue
    }

    await insertPriceSnapshot(db, item, observedAt, offerResult.offerId, offerResult.effectivePrice)

    const snapshotRows = await loadRecentPriceHistory(db, item.asin, 220)
    const historyEntries = buildHistoryEntries(snapshotRows, item.priceHistory)

    const weights = getWeightsForCategory(item.category, dbOverrides, envOverrides)
    const score = buildDealTruth(
      {
        ...item,
        ...item.offer,
        rating: item.rating,
        reviews: item.reviews,
      },
      historyEntries,
      weights
    )
    score.weights = weights

    await insertScoreSnapshot(db, item.asin, observedAt, score)

    summary.accepted += 1
    summary.scored += 1
    summary.categories[item.category] = (summary.categories[item.category] || 0) + 1
  }

  if (!summary.accepted) {
    summary.warnings.push('No qualifying items with usable price data were ingested')
  }

  return summary
}

function parseDealsQuery(url) {
  const categories = parseCategories(url.searchParams.get('categories'))
  const limit = normalizeLimit(url.searchParams.get('limit'), DEFAULT_LIMIT)
  return { categories, limit }
}

function mapSnapshotRowToDeal(row) {
  let components = {}
  try {
    components = row.components_json ? JSON.parse(row.components_json) : {}
  } catch {
    components = {}
  }

  const realDiscountPct = toNumber(row.real_discount_pct)
  const percentile = toNumber(row.percentile_180d)
  const confidenceText = row.confidence_reason
    ? `${row.confidence_level || 'Low'} (${row.confidence_reason})`
    : `${row.confidence_level || 'Low'}`

  const discountLine =
    realDiscountPct == null
      ? 'Real discount: unavailable (building 90-day baseline)'
      : realDiscountPct >= 0
        ? `Real discount: ${Math.round(Math.abs(realDiscountPct) * 100)}% below 90-day median`
        : `Real discount: ${Math.round(Math.abs(realDiscountPct) * 100)}% above 90-day median`

  const rarityLine =
    percentile == null
      ? 'Rarity: not enough history yet'
      : percentile <= 0.03
        ? 'Rarity: lowest price in 180 days'
        : percentile <= 0.1
          ? 'Rarity: near 180-day low'
          : `Rarity: not rare (~${Math.round(percentile * 100)}th percentile in 180 days)`

  return {
    id: row.asin,
    asin: row.asin,
    title: row.title,
    description: row.description,
    category: row.category,
    brand: row.brand,
    merchant: row.merchant || 'Amazon',
    iconName: row.icon_name || 'Tag',
    rating: toNumber(row.rating),
    reviews: toNumber(row.reviews),
    price: toNumber(row.effective_price),
    currency: row.currency || 'USD',
    imageUrl: row.image_url,
    affiliateLink: row.affiliate_link,
    type: 'deal',
    dealTruth: {
      score: Number(row.dealtruth_score) || 0,
      effectivePriceNow: toNumber(row.effective_price),
      baseline90: toNumber(row.baseline_price_90d),
      realDiscountPct,
      percentile180: percentile,
      rarity: toNumber(row.rarity_score),
      volatility: toNumber(row.volatility),
      quality: toNumber(row.quality_score),
      trust: toNumber(row.seller_trust_score),
      urgency: toNumber(row.urgency_score),
      scamPenalty: toNumber(row.scam_penalty),
      confidence: {
        level: row.confidence_level || 'Low',
        reason: row.confidence_reason || '',
        text: confidenceText,
      },
      notMeaningfulDeal: toBoolean(row.not_meaningful_deal),
      decision: {
        label: row.buy_wait_label || null,
        dropChance7dPct: toNumber(row.drop_chance_7d),
        text: row.buy_wait_label
          ? row.buy_wait_label === 'Buy now'
            ? `Buy now (only ~${Math.round(toNumber(row.drop_chance_7d) || 0)}% chance it drops more in 7 days)`
            : row.buy_wait_label === 'Wait'
              ? `Wait (about ~${Math.round(toNumber(row.drop_chance_7d) || 0)}% chance it drops more in 7 days)`
              : `Either way (~${Math.round(toNumber(row.drop_chance_7d) || 0)}% chance of a better price in 7 days)`
          : null,
      },
      explanations: {
        scoreLine: `DealTruth Score: ${Number(row.dealtruth_score) || 0}/100`,
        discountLine,
        rarityLine,
        confidenceLine: `Confidence: ${confidenceText}`,
        decisionLine:
          row.buy_wait_label && Number.isFinite(toNumber(row.drop_chance_7d))
            ? row.buy_wait_label === 'Buy now'
              ? `Buy now (only ~${Math.round(toNumber(row.drop_chance_7d) || 0)}% chance it drops more in 7 days)`
              : row.buy_wait_label === 'Wait'
                ? `Wait (about ~${Math.round(toNumber(row.drop_chance_7d) || 0)}% chance it drops more in 7 days)`
                : `Either way (~${Math.round(toNumber(row.drop_chance_7d) || 0)}% chance of a better price in 7 days)`
            : null,
      },
      components,
    },
    observedAt: row.observed_at,
  }
}

async function getDealsFromDb(env, { categories, limit }) {
  const db = await requireDb(env)

  const binds = []
  let whereSql = ''
  if (categories.length) {
    whereSql = `WHERE a.category IN (${categories.map(() => '?').join(',')})`
    binds.push(...categories)
  }

  const sql = `
    SELECT
      ls.asin,
      ls.observed_at,
      ls.dealtruth_score,
      ls.effective_price,
      ls.baseline_price_90d,
      ls.real_discount_pct,
      ls.percentile_180d,
      ls.rarity_score,
      ls.volatility,
      ls.quality_score,
      ls.seller_trust_score,
      ls.urgency_score,
      ls.scam_penalty,
      ls.confidence_level,
      ls.confidence_reason,
      ls.buy_wait_label,
      ls.drop_chance_7d,
      ls.not_meaningful_deal,
      ls.components_json,
      a.title,
      a.description,
      a.brand,
      a.category,
      a.image_url,
      a.affiliate_link,
      a.merchant,
      a.icon_name,
      a.rating,
      a.reviews
    FROM latest_scores ls
    JOIN asins a ON a.asin = ls.asin
    ${whereSql}
    ORDER BY ls.dealtruth_score DESC, ls.observed_at DESC
    LIMIT ?
  `

  binds.push(limit)

  const { results } = await db.prepare(sql).bind(...binds).all()
  return (results || []).map(mapSnapshotRowToDeal)
}

function isAdminRequest(request, env) {
  const required = env.ADMIN_API_KEY
  if (!required) return true
  const provided = request.headers.get('x-admin-key') || ''
  return provided && provided === required
}

async function upsertCategoryWeights(env, payload) {
  const db = await requireDb(env)
  const category = normalizeCategory(payload?.category)
  const weights = normalizeWeights(payload?.weights)

  await db
    .prepare(
      `INSERT INTO category_weight_overrides (
        category, real_discount_weight, rarity_weight, quality_weight, trust_weight, urgency_weight, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(category) DO UPDATE SET
        real_discount_weight = excluded.real_discount_weight,
        rarity_weight = excluded.rarity_weight,
        quality_weight = excluded.quality_weight,
        trust_weight = excluded.trust_weight,
        urgency_weight = excluded.urgency_weight,
        updated_at = excluded.updated_at`
    )
    .bind(
      category,
      weights.realDiscount,
      weights.rarity,
      weights.quality,
      weights.trust,
      weights.urgency,
      isoNow()
    )
    .run()

  return { category, weights }
}

async function scheduledIngest(env, sourceLabel = 'scheduled') {
  const categories =
    parseCategories(env.TRACKED_CATEGORIES) || DEFAULT_CATEGORIES
  const normalizedCategories = categories.length ? categories : DEFAULT_CATEGORIES
  const limit = normalizeLimit(env.INGEST_LIMIT, DEFAULT_LIMIT)

  const feed = await fetchApprovedFeedItems(env, {
    categories: normalizedCategories,
    limit,
  })

  const summary = await ingestItems(env, feed.items, {
    source: sourceLabel,
    fallbackCategory: 'Home',
  })

  return {
    ...summary,
    feedSource: feed.source,
    feedWarning: feed.warning,
    categories: normalizedCategories,
    limit,
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url)

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS })
    }

    if (url.pathname === '/health') {
      try {
        const db = await requireDb(env)
        const { results } = await db.prepare('SELECT COUNT(*) AS count FROM asins').all()
        return jsonResponse({
          ok: true,
          d1: true,
          asins: Number(results?.[0]?.count || 0),
          timestamp: isoNow(),
        })
      } catch (error) {
        return jsonResponse({ ok: false, d1: false, error: String(error?.message || error) }, 500)
      }
    }

    if (url.pathname === '/v1/deals' && request.method === 'GET') {
      try {
        const query = parseDealsQuery(url)
        const items = await getDealsFromDb(env, query)

        return jsonResponse({
          generatedAt: isoNow(),
          count: items.length,
          items,
        })
      } catch (error) {
        return jsonResponse(
          {
            items: [],
            error: `Failed to load deals: ${String(error?.message || error)}`,
          },
          500
        )
      }
    }

    if (url.pathname === '/v1/weights' && request.method === 'GET') {
      try {
        const db = await requireDb(env)
        const rows = await listCategoryWeightOverrides(db)
        const envOverrides = parseEnvWeightOverrides(env)

        return jsonResponse({
          default: DEFAULT_WEIGHTS,
          databaseOverrides: rows,
          envOverrides: Object.fromEntries(envOverrides.entries()),
        })
      } catch (error) {
        return jsonResponse({ error: String(error?.message || error) }, 500)
      }
    }

    if (url.pathname === '/v1/admin/weights' && request.method === 'POST') {
      if (!isAdminRequest(request, env)) {
        return jsonResponse({ error: 'Unauthorized' }, 401)
      }

      try {
        const payload = await request.json()
        const result = await upsertCategoryWeights(env, payload)
        return jsonResponse({ ok: true, ...result })
      } catch (error) {
        return jsonResponse({ error: String(error?.message || error) }, 400)
      }
    }

    if (url.pathname === '/v1/admin/ingest' && request.method === 'POST') {
      if (!isAdminRequest(request, env)) {
        return jsonResponse({ error: 'Unauthorized' }, 401)
      }

      try {
        const payload = await request.json().catch(() => ({}))
        const categories = parseCategories(payload.categories)
        const limit = normalizeLimit(payload.limit, DEFAULT_LIMIT)

        const itemsFromPayload = Array.isArray(payload.items) ? payload.items : null

        if (itemsFromPayload && itemsFromPayload.length) {
          const summary = await ingestItems(env, itemsFromPayload, {
            source: 'manual_payload',
            fallbackCategory: 'Home',
          })
          return jsonResponse({ ok: true, summary })
        }

        const feed = await fetchApprovedFeedItems(env, {
          categories: categories.length ? categories : DEFAULT_CATEGORIES,
          limit,
        })

        const summary = await ingestItems(env, feed.items, {
          source: 'manual_feed',
          fallbackCategory: 'Home',
        })

        return jsonResponse({
          ok: true,
          summary: {
            ...summary,
            feedSource: feed.source,
            feedWarning: feed.warning,
          },
        })
      } catch (error) {
        return jsonResponse({ error: String(error?.message || error) }, 500)
      }
    }

    return new Response('Not found', { status: 404, headers: CORS_HEADERS })
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil(
      (async () => {
        try {
          await scheduledIngest(env, `cron:${event.cron || 'unknown'}`)
        } catch (error) {
          console.error('scheduled ingest failed', error)
        }
      })()
    )
  },
}
