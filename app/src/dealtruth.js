const DAY_MS = 24 * 60 * 60 * 1000

const WEIGHTS = {
  realDiscount: 0.35,
  rarity: 0.2,
  quality: 0.2,
  trust: 0.15,
  urgency: 0.1,
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
    const cleaned = trimmed.replace(/[$,]/g, '')
    const parsed = Number(cleaned)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
}

function toBoolean(value) {
  if (typeof value === 'boolean') return value
  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase()
    return normalized === 'true' || normalized === 'yes' || normalized === '1'
  }
  if (typeof value === 'number') return value !== 0
  return false
}

function parseTimestamp(value) {
  if (typeof value === 'number' && Number.isFinite(value)) {
    // Accept either seconds or milliseconds.
    if (value > 1e12) return value
    if (value > 1e9) return value * 1000
    return null
  }

  if (value instanceof Date) {
    const ms = value.getTime()
    return Number.isFinite(ms) ? ms : null
  }

  if (typeof value === 'string') {
    const ms = Date.parse(value)
    return Number.isFinite(ms) ? ms : null
  }

  return null
}

function median(values) {
  if (!Array.isArray(values) || !values.length) return null
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  if (sorted.length % 2 === 0) {
    return (sorted[mid - 1] + sorted[mid]) / 2
  }
  return sorted[mid]
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
  const clean = (values || []).filter((v) => Number.isFinite(v) && v > 0)
  if (clean.length < 2) return 0

  const logged = clean.map((v) => Math.log(v))
  const mean = logged.reduce((sum, v) => sum + v, 0) / logged.length
  const variance = logged.reduce((sum, v) => sum + (v - mean) ** 2, 0) / logged.length
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

function normalizeEffectivePrice(offer) {
  const source = offer?.offer || offer || {}
  const itemPrice =
    toNumber(source.effectivePrice) ??
    toNumber(source.itemPrice) ??
    toNumber(source.buyBoxPrice) ??
    toNumber(source.price) ??
    toNumber(source.listingPrice) ??
    toNumber(source.currentPrice)

  if (!Number.isFinite(itemPrice) || itemPrice <= 0) return null

  const shipping =
    toNumber(source.shipping) ?? toNumber(source.shippingPrice) ?? toNumber(source.shippingCost) ?? 0

  const coupon = amountFrom(
    source.coupon ?? source.couponAmount,
    itemPrice,
    false
  ) + amountFrom(source.couponPercent ?? source.couponPct, itemPrice, true)

  const promoDiscount = amountFrom(
    source.promoDiscount ?? source.promoDiscounts ?? source.promotion,
    itemPrice,
    false
  )

  const subscribeSave = amountFrom(
    source.subscribeSave ?? source.subscribeAndSaveAmount,
    itemPrice,
    false
  ) + amountFrom(source.subscribeSavePercent ?? source.subscribeAndSavePercent, itemPrice, true)

  const effective = itemPrice + shipping - coupon - promoDiscount - subscribeSave
  return Math.max(0, Number(effective.toFixed(2)))
}

function extractHistoryEntries(product) {
  const raw =
    product?.priceHistory ||
    product?.priceSnapshots ||
    product?.history ||
    product?.metrics?.priceHistory ||
    []

  if (!Array.isArray(raw)) return []

  const entries = raw
    .map((entry) => {
      if (typeof entry === 'number') {
        return { price: entry, timestamp: null }
      }

      if (entry && typeof entry === 'object') {
        const price =
          toNumber(entry.effectivePrice) ?? toNumber(entry.price) ?? toNumber(entry.value) ?? toNumber(entry.amount)
        const timestamp =
          parseTimestamp(entry.timestamp) ?? parseTimestamp(entry.ts) ?? parseTimestamp(entry.at) ?? parseTimestamp(entry.date)
        if (!Number.isFinite(price) || price <= 0) return null
        return { price, timestamp }
      }

      return null
    })
    .filter(Boolean)

  const hasTimestamps = entries.some((entry) => Number.isFinite(entry.timestamp))
  if (!hasTimestamps) return entries

  return entries.sort((a, b) => {
    const tsA = a.timestamp ?? 0
    const tsB = b.timestamp ?? 0
    return tsA - tsB
  })
}

function lastDays(entries, days, nowMs = Date.now()) {
  if (!Array.isArray(entries) || !entries.length) return []
  const withTs = entries.filter((entry) => Number.isFinite(entry.timestamp))
  if (!withTs.length) return entries

  const cutoff = nowMs - days * DAY_MS
  const filtered = withTs.filter((entry) => entry.timestamp >= cutoff)
  return filtered.length ? filtered : withTs
}

function priceValues(entries) {
  return (entries || []).map((entry) => entry.price).filter((value) => Number.isFinite(value) && value > 0)
}

function qualityScore(ratingValue, reviewCountValue) {
  const rating = toNumber(ratingValue) ?? 0
  const reviews = toNumber(reviewCountValue) ?? 0

  const normalizedRating = clamp((rating - 3.2) / 1.8, 0, 1)
  const normalizedReviews = clamp(Math.log10(Math.max(0, reviews) + 1) / Math.log10(50000 + 1), 0, 1)

  return clamp(0.7 * normalizedRating + 0.3 * normalizedReviews)
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

  const sellerRatingNorm = sellerRating > 1 ? clamp((sellerRating - 80) / 20, 0, 1) : clamp((sellerRating - 0.8) / 0.2, 0, 1)
  const sellerCountNorm = clamp(Math.log10(Math.max(0, sellerRatingCount) + 1) / Math.log10(5000 + 1), 0, 1)

  let score = 0.25
  if (isPrime) score += 0.2
  if (isFba) score += 0.15
  if (shipsFromAmazon) score += 0.15
  if (soldByAmazon) score += 0.15

  score += 0.2 * sellerRatingNorm + 0.1 * sellerCountNorm

  return clamp(score)
}

function listingAgeDays(product) {
  const source = product?.offer || product || {}
  const explicitDays =
    toNumber(source.brandAgeDays) ?? toNumber(source.listingAgeDays) ?? toNumber(source.sellerAgeDays)
  if (Number.isFinite(explicitDays) && explicitDays >= 0) return explicitDays

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
  const priceJustChanged = clamp(1 - (timeAtCurrentPriceHours || 0) / 168)
  return clamp(0.5 * rarity + 0.3 * (1 - volatilityNorm) + 0.2 * priceJustChanged)
}

function confidenceLabel({ historyCount, hasNinetyDay, hasOneEightyDay, volatility, trust, isPrime, priceKnown }) {
  const reasons = []
  let level = 'Low'

  if (!priceKnown) {
    return {
      level,
      reason: 'missing current price data',
      text: `${level} (missing current price data)`,
    }
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

  return {
    level,
    reason: reasons.join(' + '),
    text: `${level} (${reasons.join(' + ')})`,
  }
}

function roundPercent(value) {
  return Math.round((value || 0) * 100)
}

function rarityText(percentile180, hasHistory) {
  if (!hasHistory || percentile180 == null) return 'Rarity: not enough history yet'

  if (percentile180 <= 0.03) return 'Rarity: lowest price in 180 days'
  if (percentile180 <= 0.1) return 'Rarity: near 180-day low'
  if (percentile180 <= 0.25) return `Rarity: lower than ~${Math.round((1 - percentile180) * 100)}% of 180-day prices`

  return `Rarity: not rare (~${Math.round(percentile180 * 100)}th percentile in 180 days)`
}

function realDiscountText(realDiscountPct, baselineKnown) {
  if (!baselineKnown || realDiscountPct == null) {
    return 'Real discount: unavailable (building 90-day baseline)'
  }

  const pct = Math.round(Math.abs(realDiscountPct) * 100)
  if (realDiscountPct >= 0) {
    return `Real discount: ${pct}% below 90-day median`
  }

  return `Real discount: ${pct}% above 90-day median`
}

function lastPriceRunHours(entries, currentPrice) {
  if (!Array.isArray(entries) || !entries.length || !Number.isFinite(currentPrice)) return null

  const sorted = [...entries].sort((a, b) => (a.timestamp ?? 0) - (b.timestamp ?? 0))
  const withTimestamps = sorted.filter((entry) => Number.isFinite(entry.timestamp))
  if (!withTimestamps.length) return null

  const latest = withTimestamps[withTimestamps.length - 1]
  let oldestMatchingTs = latest.timestamp

  for (let i = withTimestamps.length - 1; i >= 0; i -= 1) {
    const entry = withTimestamps[i]
    const delta = Math.abs(entry.price - currentPrice)
    const tolerance = Math.max(0.01, currentPrice * 0.003)
    if (delta > tolerance) break
    oldestMatchingTs = entry.timestamp
  }

  const ms = latest.timestamp - oldestMatchingTs
  return Math.max(0, ms / (60 * 60 * 1000))
}

function dropStats(entries, days = 60) {
  if (!Array.isArray(entries) || entries.length < 2) {
    return { drops: 0, avgDropSize: 0 }
  }

  const recent = lastDays(entries, days)
  if (recent.length < 2) {
    return { drops: 0, avgDropSize: 0 }
  }

  let drops = 0
  let dropSum = 0

  for (let i = 1; i < recent.length; i += 1) {
    const prev = recent[i - 1].price
    const curr = recent[i].price
    if (!(Number.isFinite(prev) && Number.isFinite(curr) && prev > 0 && curr > 0)) continue

    if (curr < prev) {
      drops += 1
      dropSum += (prev - curr) / prev
    }
  }

  return {
    drops,
    avgDropSize: drops ? dropSum / drops : 0,
  }
}

function buyOrWait({ percentile180, volatility, dropsLast60d, avgDropSize, timeAtCurrentPriceHours, historyCount }) {
  if (historyCount < 12 || percentile180 == null) {
    return {
      label: null,
      dropChance7dPct: null,
      text: null,
    }
  }

  let dropProbability = 0.42

  if (percentile180 <= 0.1) dropProbability -= 0.24
  else if (percentile180 <= 0.2) dropProbability -= 0.1

  if (dropsLast60d >= 8) dropProbability += 0.2
  else if (dropsLast60d >= 4) dropProbability += 0.1

  if (avgDropSize >= 0.12) dropProbability += 0.12
  else if (avgDropSize >= 0.06) dropProbability += 0.06

  if (Number.isFinite(timeAtCurrentPriceHours) && timeAtCurrentPriceHours < 24) dropProbability -= 0.05

  if (volatility <= 0.1) dropProbability -= 0.08
  if (volatility >= 0.25) dropProbability += 0.08

  dropProbability = clamp(dropProbability, 0.02, 0.98)
  const dropChance7dPct = Math.round(dropProbability * 100)

  if (dropProbability <= 0.25) {
    return {
      label: 'Buy now',
      dropChance7dPct,
      text: `Buy now (only ~${dropChance7dPct}% chance it drops more in 7 days)`,
    }
  }

  if (dropProbability >= 0.55) {
    return {
      label: 'Wait',
      dropChance7dPct,
      text: `Wait (about ~${dropChance7dPct}% chance it drops more in 7 days)`,
    }
  }

  return {
    label: 'Either',
    dropChance7dPct,
    text: `Either way (~${dropChance7dPct}% chance of a better price in 7 days)`,
  }
}

export function dealTruthScore(product) {
  const offer = product?.offer || product || {}
  const historyEntries = extractHistoryEntries(product)
  const priceNow = normalizeEffectivePrice(offer)
  const fallbackCurrent = toNumber(product?.price)
  const effectivePriceNow = Number.isFinite(priceNow) ? priceNow : Number.isFinite(fallbackCurrent) ? fallbackCurrent : null

  const ninetyDayEntries = lastDays(historyEntries, 90)
  const oneEightyEntries = lastDays(historyEntries, 180)

  const history90Values = priceValues(ninetyDayEntries)
  const history180Values = priceValues(oneEightyEntries)

  const baseline90 = trimmedMedian(history90Values, 0.05)
  const hasBaseline = Number.isFinite(baseline90) && baseline90 > 0
  const has180History = history180Values.length > 0

  const realDiscountPct =
    hasBaseline && Number.isFinite(effectivePriceNow)
      ? (baseline90 - effectivePriceNow) / baseline90
      : null

  const percentile180 =
    has180History && Number.isFinite(effectivePriceNow)
      ? percentileRank(history180Values, effectivePriceNow)
      : null

  const rarity = percentile180 == null ? 0 : clamp(1 - percentile180)
  const volatility = stdDevLog(history180Values)

  const quality = qualityScore(offer.rating ?? product?.rating, offer.reviews ?? product?.reviews)
  const trust = sellerTrustScore(offer)

  const reviewCount = toNumber(offer.reviews ?? product?.reviews) ?? 0
  const listPrice =
    toNumber(offer.listPrice) ?? toNumber(offer.msrp) ?? toNumber(offer.wasPrice) ?? toNumber(product?.listPrice)

  const ageDays = listingAgeDays(product)

  const scamPenalty = scamRisk({
    realDiscount: Math.max(0, realDiscountPct ?? 0),
    reviewCount,
    listPrice,
    baseline90,
    volatility,
    ageDays,
  })

  const timeAtCurrentPriceHours = lastPriceRunHours(historyEntries, effectivePriceNow)
  const urgency = urgencyScore({ rarity, volatility, timeAtCurrentPriceHours })

  const boundedDiscount = clamp(realDiscountPct ?? 0)

  const rawScore =
    100 *
      (WEIGHTS.realDiscount * boundedDiscount +
        WEIGHTS.rarity * rarity +
        WEIGHTS.quality * quality +
        WEIGHTS.trust * trust +
        WEIGHTS.urgency * urgency) -
    100 * clamp(scamPenalty)

  const score = Math.round(clamp(rawScore, 0, 100))

  const isPrime = toBoolean(offer.isPrime ?? offer.prime)
  const confidence = confidenceLabel({
    historyCount: historyEntries.length,
    hasNinetyDay: hasBaseline,
    hasOneEightyDay: has180History,
    volatility,
    trust,
    isPrime,
    priceKnown: Number.isFinite(effectivePriceNow),
  })

  const { drops, avgDropSize } = dropStats(historyEntries, 60)
  const decision = buyOrWait({
    percentile180,
    volatility,
    dropsLast60d: drops,
    avgDropSize,
    timeAtCurrentPriceHours,
    historyCount: historyEntries.length,
  })

  const notMeaningfulDeal =
    realDiscountPct == null ? false : realDiscountPct < 0.05 || (percentile180 != null && percentile180 > 0.35)

  return {
    score,
    effectivePriceNow,
    baseline90,
    realDiscountPct,
    percentile180,
    rarity,
    volatility,
    quality,
    trust,
    urgency,
    scamPenalty,
    historyCount: historyEntries.length,
    confidence,
    notMeaningfulDeal,
    decision,
    explanations: {
      scoreLine: `DealTruth Score: ${score}/100`,
      discountLine: realDiscountText(realDiscountPct, hasBaseline),
      rarityLine: rarityText(percentile180, has180History),
      confidenceLine: `Confidence: ${confidence.text}`,
      decisionLine: decision.text,
    },
    components: {
      realDiscountPct: roundPercent(realDiscountPct ?? 0),
      rarityScore: roundPercent(rarity),
      qualityScore: roundPercent(quality),
      sellerTrustScore: roundPercent(trust),
      urgencyScore: roundPercent(urgency),
      scamPenalty: roundPercent(scamPenalty),
      dropChance7dPct: decision.dropChance7dPct,
      dropsLast60d: drops,
      avgDropSizePct: roundPercent(avgDropSize),
    },
  }
}

export function scoreProductList(items) {
  if (!Array.isArray(items)) return []
  return items.map((product) => ({
    ...product,
    dealTruth: dealTruthScore(product),
  }))
}
