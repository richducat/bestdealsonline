// Local-only mock of an approved price feed, used to seed the D1 pipeline
// with realistic price history for local testing. Not part of the deployed
// worker -- run standalone (`node local-mock-feed.mjs`) and point the
// worker's DEALS_FEED_URL at it via .dev.vars.
//
// Each GET /feed request advances a simulated calendar by one day and
// returns that day's synthetic price snapshot for a sample of real
// products (from data/products.json), so repeated ingest calls build up
// realistic 90/180-day price history: random daily drift plus occasional
// multi-day "sale" dips, the same shape real Amazon pricing behavior takes.

import { createServer } from 'node:http'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const PRODUCTS_PATH = join(__dirname, '..', 'data', 'products.json')
const PORT = 8898
const SIMULATED_DAYS = 120
const SAMPLE_SIZE = 60

const CATEGORY_PRICE_RANGE = {
  Electronics: [20, 180],
  Home: [15, 120],
  Kitchen: [15, 140],
  Tools: [12, 100],
  Kids: [10, 80],
  Beauty: [8, 60],
  Fitness: [15, 150],
  Pets: [10, 70],
}

function seededRandom(seed) {
  let s = seed % 2147483647
  if (s <= 0) s += 2147483646
  return () => {
    s = (s * 16807) % 2147483647
    return (s - 1) / 2147483646
  }
}

function hashToSeed(str) {
  let h = 0
  for (let i = 0; i < str.length; i += 1) {
    h = (h * 31 + str.charCodeAt(i)) | 0
  }
  return Math.abs(h) || 1
}

function loadSample() {
  const data = JSON.parse(readFileSync(PRODUCTS_PATH, 'utf8'))
  const seen = new Set()
  const byCategory = new Map()
  for (const item of data.items) {
    if (seen.has(item.title)) continue
    seen.add(item.title)
    const bucket = byCategory.get(item.category) ?? []
    bucket.push(item)
    byCategory.set(item.category, bucket)
  }
  const buckets = [...byCategory.values()]
  const sample = []
  let i = 0
  while (sample.length < SAMPLE_SIZE && buckets.some((b) => b.length > 0)) {
    const bucket = buckets[i % buckets.length]
    if (bucket.length > 0) sample.push(bucket.shift())
    i += 1
  }
  return sample.map((item, idx) => {
    const rand = seededRandom(hashToSeed(item.title))
    for (let w = 0; w < 5; w += 1) rand() // warm up
    const [lo, hi] = CATEGORY_PRICE_RANGE[item.category] ?? [15, 100]
    const regularPrice = Math.round((lo + rand() * (hi - lo)) * 100) / 100
    return {
      asin: `B0LOCAL${String(idx).padStart(5, '0')}`,
      title: item.title,
      category: item.category,
      imageUrl: item.imageUrl,
      affiliateLink: item.affiliateLink,
      merchant: 'Amazon',
      rating: item.rating,
      reviews: item.reviews,
      regularPrice,
      rand,
      saleDaysRemaining: 0,
      saleDiscountPct: 0,
    }
  })
}

const sample = loadSample()
let dayOffset = -SIMULATED_DAYS // days relative to "today" (0)

function priceForDay(product) {
  const { rand } = product
  // Random chance to enter a promotional dip if not already in one.
  if (product.saleDaysRemaining <= 0 && rand() < 0.06) {
    product.saleDaysRemaining = 2 + Math.floor(rand() * 8) // 2-9 days
    product.saleDiscountPct = 0.1 + rand() * 0.35 // 10-45% off
  }
  let price
  if (product.saleDaysRemaining > 0) {
    price = product.regularPrice * (1 - product.saleDiscountPct)
    product.saleDaysRemaining -= 1
  } else {
    // Small day-to-day drift around the regular price.
    const drift = (rand() - 0.5) * 0.04
    price = product.regularPrice * (1 + drift)
  }
  return Math.max(1, Math.round(price * 100) / 100)
}

// On the final ("today") call, force a spread of outcomes so the scoring
// output is genuinely varied instead of everything landing mid-pack.
function finalDayPrice(product, idx) {
  const bucket = idx % 3
  if (bucket === 0) {
    // Deep, rare discount -- should score well.
    return Math.round(product.regularPrice * (1 - (0.3 + product.rand() * 0.25)) * 100) / 100
  }
  if (bucket === 1) {
    // Mild/common discount.
    return Math.round(product.regularPrice * (1 - (0.05 + product.rand() * 0.1)) * 100) / 100
  }
  // At or above regular price -- should score poorly / "not a meaningful deal".
  return Math.round(product.regularPrice * (1 + product.rand() * 0.03) * 100) / 100
}

const server = createServer((req, res) => {
  if (!req.url.startsWith('/feed')) {
    res.writeHead(404)
    res.end('not found')
    return
  }

  const isFinalDay = dayOffset >= 0
  const observedDate = new Date(Date.now() + dayOffset * 24 * 60 * 60 * 1000)
  const observedAt = observedDate.toISOString()

  const items = sample.map((product, idx) => {
    const price = isFinalDay ? finalDayPrice(product, idx) : priceForDay(product)
    return {
      asin: product.asin,
      title: product.title,
      category: product.category,
      imageUrl: product.imageUrl,
      affiliateLink: product.affiliateLink,
      merchant: product.merchant,
      rating: product.rating,
      reviews: product.reviews,
      observedAt,
      offer: {
        sellerId: 'amazon',
        sellerName: 'Amazon.com',
        isPrime: true,
        isFba: true,
        shipsFromAmazon: true,
        soldByAmazon: true,
        condition: 'new',
        itemPrice: price,
        shipping: 0,
      },
    }
  })

  console.log(`day ${dayOffset} (${observedAt.slice(0, 10)}): served ${items.length} items${isFinalDay ? ' [FINAL]' : ''}`)
  if (!isFinalDay) dayOffset += 1

  res.writeHead(200, { 'Content-Type': 'application/json' })
  res.end(JSON.stringify({ items }))
})

server.listen(PORT, () => {
  console.log(`Mock feed server listening on http://127.0.0.1:${PORT}/feed`)
  console.log(`Simulating ${SIMULATED_DAYS} days of history for ${sample.length} products.`)
})
