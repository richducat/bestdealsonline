import React, { useEffect, useMemo, useState } from 'react'
import { scoreProductList } from './dealtruth'

function pickDailyProduct(products, nowMs = Date.now()) {
  const items = Array.isArray(products) ? products.filter((p) => p && p.affiliateLink) : []
  if (!items.length) return null

  // Stable per-day selection.
  const d = new Date(nowMs)
  const seed = Number(String(d.getFullYear()) + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0'))
  const idx = seed % items.length
  return items[idx]
}

function msUntilNextMidnight(nowMs = Date.now()) {
  const now = new Date(nowMs)
  const next = new Date(now)
  next.setHours(24, 0, 0, 0)
  return Math.max(0, next.getTime() - now.getTime())
}

function formatCountdown(ms) {
  const total = Math.max(0, Math.floor(ms / 1000))
  const d = Math.floor(total / 86400)
  const h = Math.floor((total % 86400) / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  if (d > 0) {
    return `${d}d ${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  }
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}
import {
  Search,
  ShoppingBag,
  Menu,
  X,
  Star,
  Tag,
  Heart,
  ArrowUpRight,
  Mail,
  Headphones,
  Armchair,
  Utensils,
  Activity,
  Briefcase,
  Monitor,
  Bed,
  BatteryCharging,
  Coffee,
  Footprints,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  ShieldCheck,
  Zap,
  Info,
  Clock,
  Pause,
  Play,
  Square,
  Settings,
  PlusCircle,
  Edit2,
  Trash2,
  Save,
  LogOut,
} from 'lucide-react'

// ===== CONFIG =====
const AMAZON_TAG = 'bestdeals0ad2-20'

// Data source
// For now (no PA-API keys), we use a static JSON file committed with the site.
// Later, we can swap this to a Worker-backed PA-API endpoint for live prices.
const PRODUCTS_JSON_URL = './data/products.json'
const DEALS_API_BASE = (import.meta.env.VITE_DEALS_API_BASE || '').replace(/\/+$/, '')

function resolveDealsUrl(limit = 300) {
  if (DEALS_API_BASE) {
    return `${DEALS_API_BASE}/v1/deals?limit=${encodeURIComponent(limit)}`
  }
  return PRODUCTS_JSON_URL
}

function trackOutboundClick({ url, label, category, section, productId, productTitle, position, campaign }) {
  try {
    if (typeof window !== 'undefined' && typeof window.gtag === 'function') {
      window.gtag('event', 'outbound_click', {
        event_category: category || 'outbound',
        event_label: label || productTitle || url,
        link_url: url,
        section: section || undefined,
        product_id: productId || undefined,
        product_title: productTitle || undefined,
        position: typeof position === 'number' ? position : undefined,
        campaign: campaign || undefined,
        transport_type: 'beacon',
      })
    }
  } catch (_) {}
}

function amazonSearchLink(query, campaign = 'bdo_storefront') {
  const q = encodeURIComponent(query)
  return `https://www.amazon.com/s?k=${q}&tag=${AMAZON_TAG}&utm_source=bestdealsonline&utm_medium=site&utm_campaign=${encodeURIComponent(
    campaign
  )}`
}

const AMAZON_ASIN_PATTERN = /^[A-Z0-9]{10}$/
const ANALYZER_PLACEHOLDER_TITLE = 'Amazon Product'
const ANALYZER_STOP_WORDS = new Set([
  'amazon',
  'with',
  'from',
  'that',
  'this',
  'your',
  'their',
  'best',
  'pack',
  'set',
  'the',
  'and',
  'for',
  'you',
  'are',
  'but',
  'its',
  'new',
])

const CATEGORY_KEYWORDS = {
  Electronics: ['charger', 'cable', 'monitor', 'headphones', 'earbuds', 'usb', 'power', 'wifi', 'router', 'speaker', 'camera'],
  Home: ['storage', 'blanket', 'curtain', 'lamp', 'organizer', 'cleaning', 'bedding', 'bathroom', 'furniture'],
  Kitchen: ['air fryer', 'blender', 'toaster', 'coffee', 'cookware', 'pan', 'knife', 'kitchen', 'grinder'],
  Tools: ['drill', 'wrench', 'tool', 'screwdriver', 'socket', 'measuring', 'workshop', 'hardware'],
  Kids: ['kids', 'toddler', 'baby', 'toy', 'school', 'stroller', 'nursery'],
  Beauty: ['skincare', 'serum', 'beauty', 'makeup', 'hair', 'grooming', 'shampoo'],
  Fitness: ['fitness', 'workout', 'dumbbell', 'yoga', 'exercise', 'gym', 'resistance'],
  Pets: ['pet', 'dog', 'cat', 'litter', 'leash', 'animal', 'food bowl'],
}

function cleanPastedUrl(value) {
  return String(value || '')
    .trim()
    .replace(/^[\s<>"'([{]+/, '')
    .replace(/[\s>)"'\]},.!?;:]+$/, '')
}

function normalizeAmazonInputUrl(value, depth = 0) {
  if (depth > 2) return null
  const rawInput = String(value || '').trim()
  if (!rawInput) return null

  // Handle pasted share text like: "Check this out https://a.co/d/abc123".
  const embeddedUrlMatch = rawInput.match(/https?:\/\/[^\s<>"']+/i)
  const raw = cleanPastedUrl(embeddedUrlMatch?.[0] || rawInput)
  if (!raw) return null

  const upper = raw.toUpperCase()
  if (AMAZON_ASIN_PATTERN.test(upper)) {
    return new URL(`https://www.amazon.com/dp/${upper}`)
  }

  const withProtocol = /^https?:\/\//i.test(raw) ? raw : `https://${raw}`
  let parsed
  try {
    parsed = new URL(withProtocol)
  } catch (_) {
    return null
  }

  const hostname = parsed.hostname.toLowerCase()
  const isAmazonDomain = /(^|\.)amazon\./i.test(hostname)
  const isShortAmazonDomain = hostname === 'a.co' || hostname === 'amzn.to'

  if (!isAmazonDomain && !isShortAmazonDomain) return null

  // Some Amazon links wrap the real destination in a query param.
  const nestedRaw = parsed.searchParams.get('url') || parsed.searchParams.get('u')
  if (nestedRaw) {
    const nested = normalizeAmazonInputUrl(nestedRaw, depth + 1)
    if (nested) return nested
  }

  return parsed
}

function extractAsinFromAmazonUrl(url) {
  if (!url) return null

  const explicitAsin = (url.searchParams.get('asin') || '').trim().toUpperCase()
  if (AMAZON_ASIN_PATTERN.test(explicitAsin)) return explicitAsin
  const pdAsin = (url.searchParams.get('pd_rd_i') || '').trim().toUpperCase()
  if (AMAZON_ASIN_PATTERN.test(pdAsin)) return pdAsin

  const patterns = [
    /\/dp\/([A-Z0-9]{10})(?:[/?]|$)/i,
    /\/gp\/product\/([A-Z0-9]{10})(?:[/?]|$)/i,
    /\/gp\/aw\/d\/([A-Z0-9]{10})(?:[/?]|$)/i,
    /\/gp\/aw\/dp\/([A-Z0-9]{10})(?:[/?]|$)/i,
    /\/gp\/video\/detail\/([A-Z0-9]{10})(?:[/?]|$)/i,
    /\/exec\/obidos\/ASIN\/([A-Z0-9]{10})(?:[/?]|$)/i,
    /\/o\/ASIN\/([A-Z0-9]{10})(?:[/?]|$)/i,
    /\/product\/([A-Z0-9]{10})(?:[/?]|$)/i,
  ]

  for (const pattern of patterns) {
    const match = url.pathname.match(pattern)
    if (match?.[1]) return match[1].toUpperCase()
  }

  const segments = url.pathname.split('/').filter(Boolean)
  for (const segment of segments) {
    const cleaned = segment.replace(/[^a-zA-Z0-9]/g, '').toUpperCase()
    if (AMAZON_ASIN_PATTERN.test(cleaned)) return cleaned
  }

  return null
}

function prettifyTitle(text) {
  return String(text || '')
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map((word) => {
      if (word.length <= 2) return word.toUpperCase()
      return `${word.charAt(0).toUpperCase()}${word.slice(1)}`
    })
    .join(' ')
}

function inferTitleFromAmazonUrl(url, asin) {
  if (!url) return asin ? `${ANALYZER_PLACEHOLDER_TITLE} ${asin}` : ANALYZER_PLACEHOLDER_TITLE

  const segments = url.pathname.split('/').filter(Boolean)
  let sourceText = ''

  const dpIndex = segments.findIndex((segment) => segment.toLowerCase() === 'dp')
  if (dpIndex > 0) {
    sourceText = segments[dpIndex - 1]
  }

  if (!sourceText) {
    const preferredSegment = segments.find((segment) => {
      const normalized = segment.trim().toLowerCase()
      if (!normalized) return false
      if (['gp', 'aw', 'dp', 'd', 'product', 's', 'a', 'hz', 'stores', 'store'].includes(normalized)) return false
      if (AMAZON_ASIN_PATTERN.test(segment.toUpperCase())) return false
      return /[a-z]/i.test(segment)
    })
    sourceText = preferredSegment || ''
  }

  if (!sourceText) {
    sourceText = url.searchParams.get('k') || url.searchParams.get('keywords') || url.searchParams.get('q') || ''
  }

  let decodedSource = sourceText
  try {
    decodedSource = decodeURIComponent(sourceText)
  } catch (_) {
    decodedSource = sourceText
  }

  const cleaned = decodedSource
    .replace(/[-_+]+/g, ' ')
    .replace(/[^a-zA-Z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

  if (!cleaned) return asin ? `${ANALYZER_PLACEHOLDER_TITLE} ${asin}` : ANALYZER_PLACEHOLDER_TITLE
  return prettifyTitle(cleaned)
}

function withAffiliateTracking(urlOrString, campaign) {
  let url
  try {
    url = urlOrString instanceof URL ? new URL(urlOrString.toString()) : new URL(String(urlOrString))
  } catch (_) {
    return String(urlOrString || '')
  }

  if (!/(^|\.)amazon\./i.test(url.hostname)) return url.toString()

  url.searchParams.set('tag', AMAZON_TAG)
  url.searchParams.set('utm_source', 'bestdealsonline')
  url.searchParams.set('utm_medium', 'site')
  url.searchParams.set('utm_campaign', campaign || 'bdo_link_analyzer')
  return url.toString()
}

function tokenizeText(text) {
  return String(text || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .map((token) => token.trim())
    .filter((token) => token.length >= 3 && !ANALYZER_STOP_WORDS.has(token))
}

function inferCategoryFromTitle(title) {
  const normalized = String(title || '').toLowerCase()
  if (!normalized) return 'Home'

  let bestCategory = 'Home'
  let bestScore = 0

  for (const [category, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
    const score = keywords.reduce((count, keyword) => (normalized.includes(keyword) ? count + 1 : count), 0)
    if (score > bestScore) {
      bestScore = score
      bestCategory = category
    }
  }

  return bestCategory
}

function relatedDealsForTitle(products, title, preferredCategory, limit = 4) {
  const queryTokens = tokenizeText(title)
  const querySet = new Set(queryTokens)
  const seen = new Set()
  const ranked = (products || [])
    .map((product) => {
      const titleTokens = tokenizeText(product?.title)
      const overlap = titleTokens.filter((token) => querySet.has(token)).length
      const sameCategory = preferredCategory && product?.category === preferredCategory ? 1 : 0
      const scoreBoost = (product?.dealTruth?.score ?? 0) / 100
      const rankScore = overlap * 3 + sameCategory * 1.5 + scoreBoost * 0.75

      return { product, rankScore, overlap, sameCategory }
    })
    .filter((entry) => entry.rankScore > 0)
    .sort((a, b) => b.rankScore - a.rankScore || (b.product?.dealTruth?.score ?? 0) - (a.product?.dealTruth?.score ?? 0))

  const deduped = []
  for (const entry of ranked) {
    const titleKey = String(entry.product?.title || '').trim().toLowerCase()
    const categoryKey = String(entry.product?.category || '').trim().toLowerCase()
    const key = `${titleKey}|${categoryKey}`
    if (!titleKey || seen.has(key)) continue
    seen.add(key)
    deduped.push(entry.product)
    if (deduped.length >= limit) break
  }
  return deduped
}

function topDealsFallback(products, preferredCategory, limit = 4) {
  const seen = new Set()
  const ranked = [...(products || [])].sort((a, b) => (b?.dealTruth?.score ?? 0) - (a?.dealTruth?.score ?? 0))
  const categoryFirst = preferredCategory
    ? [...ranked.filter((p) => p?.category === preferredCategory), ...ranked.filter((p) => p?.category !== preferredCategory)]
    : ranked

  const deduped = []
  for (const product of categoryFirst) {
    const titleKey = String(product?.title || '').trim().toLowerCase()
    const categoryKey = String(product?.category || '').trim().toLowerCase()
    const key = `${titleKey}|${categoryKey}`
    if (!titleKey || seen.has(key)) continue
    seen.add(key)
    deduped.push(product)
    if (deduped.length >= limit) break
  }
  return deduped
}

function isPlaceholderAnalyzerTitle(title, asin) {
  const normalized = String(title || '').trim().toLowerCase()
  if (!normalized) return true
  if (normalized === ANALYZER_PLACEHOLDER_TITLE.toLowerCase()) return true
  if (asin && normalized === `${ANALYZER_PLACEHOLDER_TITLE} ${String(asin).toLowerCase()}`) return true
  return false
}

function findCatalogProductByAsin(products, asin) {
  if (!asin) return null
  const normalizedAsin = String(asin).trim().toUpperCase()
  if (!normalizedAsin) return null
  return (products || []).find((product) => String(product?.asin || '').trim().toUpperCase() === normalizedAsin) || null
}

function normalizeProductTitleKey(title) {
  return String(title || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function dedupeProductsByTitleCategory(products) {
  const selectedByKey = new Map()

  for (const product of products || []) {
    if (!product) continue
    const titleKey = normalizeProductTitleKey(product.title)
    const categoryKey = String(product.category || '').trim().toLowerCase()
    const dedupeKey = `${categoryKey}|${titleKey}`
    if (!titleKey) continue

    const existing = selectedByKey.get(dedupeKey)
    if (!existing) {
      selectedByKey.set(dedupeKey, product)
      continue
    }

    const existingScore = existing?.dealTruth?.score ?? 0
    const currentScore = product?.dealTruth?.score ?? 0
    const existingReviews = existing?.reviews ?? 0
    const currentReviews = product?.reviews ?? 0

    if (currentScore > existingScore || (currentScore === existingScore && currentReviews > existingReviews)) {
      selectedByKey.set(dedupeKey, product)
    }
  }

  return Array.from(selectedByKey.values())
}

function diversifyProductsByCategory(products, categoryOrder = []) {
  const buckets = new Map()
  const extras = []
  const normalizedOrder = Array.isArray(categoryOrder) ? categoryOrder.filter(Boolean) : []

  for (const product of products || []) {
    const category = String(product?.category || '').trim()
    if (normalizedOrder.includes(category)) {
      if (!buckets.has(category)) buckets.set(category, [])
      buckets.get(category).push(product)
    } else {
      extras.push(product)
    }
  }

  const orderedCategories = [
    ...normalizedOrder.filter((category) => buckets.has(category)),
    ...Array.from(buckets.keys()).filter((category) => !normalizedOrder.includes(category)),
  ]

  const output = []
  let rowIndex = 0
  while (true) {
    let added = false
    for (const category of orderedCategories) {
      const bucket = buckets.get(category)
      if (bucket && rowIndex < bucket.length) {
        output.push(bucket[rowIndex])
        added = true
      }
    }
    if (!added) break
    rowIndex += 1
  }

  return output.concat(extras)
}

// Seed content (works even before API is wired)
const SEED_PRODUCTS = [
  {
    id: 'seed-1',
    title: 'Anker Portable Charger 20000mAh',
    description: 'High-capacity power bank (great travel pick).',
    category: 'Electronics',
    merchant: 'Amazon',
    rating: 4.7,
    reviews: 50000,
    iconName: 'BatteryCharging',
    affiliateLink: amazonSearchLink('Anker 20000mAh power bank'),
    type: 'deal',
  },
  {
    id: 'seed-2',
    title: 'Air Fryer (dual-basket style)',
    description: 'Dual-basket air fryers are a huge weeknight upgrade.',
    category: 'Kitchen',
    merchant: 'Amazon',
    rating: 4.6,
    reviews: 10000,
    iconName: 'Utensils',
    affiliateLink: amazonSearchLink('dual basket air fryer'),
    type: 'deal',
  },
]

const CATEGORIES = ['All', 'Electronics', 'Home', 'Kitchen', 'Tools', 'Kids', 'Beauty', 'Fitness', 'Pets']

const CATEGORY_IMAGE_MAP = {
  Electronics: '/images/categories/electronics.webp',
  Home: '/images/categories/home.webp',
  Kitchen: '/images/categories/kitchen.webp',
  Tools: '/images/categories/tools.webp',
  Kids: '/images/categories/kids.webp',
  Beauty: '/images/categories/beauty.webp',
  Fitness: '/images/categories/fitness.webp',
  Pets: '/images/categories/pets.webp',
}

const getCategoryImage = (category) => CATEGORY_IMAGE_MAP[category] || '/images/categories/home.webp'

const SORT_OPTIONS = [
  { label: 'DealTruth Score', value: 'dealtruth_desc' },
  { label: 'Recommended', value: 'recommended' },
  { label: 'Top Rated', value: 'rating_desc' },
  { label: 'Most Reviews', value: 'reviews_desc' },
  { label: 'Price: Low → High', value: 'price_asc' },
  { label: 'Price: High → Low', value: 'price_desc' },
]
const DEALS_PAGE_SIZE = 24

const GLOBAL_ONBOARDING_STEPS = [
  {
    title: 'Paste any Amazon link',
    body: 'Use Link Analyzer to paste a product URL or ASIN and run a DealTruth score.',
    anchor: 'link-analyzer',
  },
  {
    title: 'Read score and confidence',
    body: 'Check score, real discount context, rarity, and confidence before buying.',
    anchor: 'dealtruth',
  },
  {
    title: 'Compare ranked alternatives',
    body: 'Jump to trending and top picks to find stronger options with your affiliate links.',
    anchor: 'trending',
  },
]

const IconMap = {
  Headphones,
  Armchair,
  Utensils,
  Activity,
  Briefcase,
  Monitor,
  Bed,
  BatteryCharging,
  Coffee,
  Footprints,
  Tag,
  Heart,
}

const getIcon = (name) => IconMap[name] || Tag

function formatCompactCount(value) {
  const count = Number(value || 0)
  if (!Number.isFinite(count) || count <= 0) return '0'
  if (count >= 1_000_000) return `${(count / 1_000_000).toFixed(count % 1_000_000 === 0 ? 0 : 1).replace(/\.0$/, '')}m`
  if (count >= 1_000) return `${(count / 1_000).toFixed(count % 1_000 === 0 ? 0 : 1).replace(/\.0$/, '')}k`
  return String(Math.round(count))
}

function dealHighlightText(product, score) {
  const cat = String(product?.category || '').toLowerCase()
  if (score >= 60) {
    if (cat === 'electronics') return 'Ranked #1 for budget displays. Features strong color accuracy and clear everyday value.'
    if (cat === 'home') return 'A rare price drop for this top-rated home essential. Built for daily comfort and longevity.'
    if (cat === 'kitchen') return 'Rare price drop on a high-utility kitchen pick. Trending now with strong buyer feedback.'
    if (cat === 'tools') return 'Heavy-duty value pick with strong review trust. A dependable buy for repeat project use.'
    return 'Top-value pick with strong trust signals and review momentum across the latest feed.'
  }

  if (cat === 'electronics') return 'Rare price drop alert. Smart timing if you have this on your shortlist today.'
  if (cat === 'home') return 'A notable markdown on a consistently strong home pick. Worth checking while this price lasts.'
  if (cat === 'kitchen') return 'Forged quality at a lower-than-usual price point. Currently trending in kitchen essentials.'
  if (cat === 'tools') return 'A value-forward tools deal with durable build signals and reliable category performance.'
  return 'Rare price drop with healthy demand signals and a stronger-than-average value profile.'
}

const DisclosureBanner = () => {
  const [visible, setVisible] = useState(true)
  if (!visible) return null
  return (
    <div className="bg-slate-100 border-b border-slate-200 text-xs text-slate-600 py-2 px-4 flex justify-between items-center">
      <span>
        <strong>Affiliate Disclosure:</strong> BestDealsOnline.us is reader-supported. When you buy through links on our
        site, we may earn an affiliate commission at no extra cost to you.{' '}
        <a className="underline inline-flex items-center min-h-10 px-1" href="/affiliate-disclosure.html">Details</a>
      </span>
      <button
        onClick={() => setVisible(false)}
        className="text-slate-400 hover:text-slate-800 inline-flex items-center justify-center h-10 w-10"
        aria-label="Dismiss"
      >
        <X size={14} />
      </button>
    </div>
  )
}

const LoadingScreen = ({ message = 'Loading live deals...', progress = 30 }) => (
  <div className="fixed inset-0 z-[120] bg-slate-950/92 backdrop-blur-sm flex items-center justify-center px-4">
    <div className="w-full max-w-md rounded-2xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-yellow-400 text-slate-900 flex items-center justify-center">
          <Tag size={18} />
        </div>
        <div>
          <div className="text-white font-extrabold">BestDealsOnline</div>
          <div className="text-xs text-slate-300">DealTruth engine</div>
        </div>
      </div>
      <div className="mt-6 text-slate-100 font-semibold">{message}</div>
      <div className="mt-4 h-2 w-full rounded-full bg-white/10 overflow-hidden">
        <div
          className="h-full bg-yellow-400 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${Math.max(5, Math.min(100, progress))}%` }}
        />
      </div>
      <div className="mt-3 text-xs text-slate-400">
        Pulling latest catalog, scoring deals, and preparing rankings.
      </div>
    </div>
  </div>
)

const OnboardingModal = ({ open, onClose }) => {
  const [status, setStatus] = useState('stopped')
  const [stepIndex, setStepIndex] = useState(0)
  const currentStep = GLOBAL_ONBOARDING_STEPS[stepIndex]

  useEffect(() => {
    if (!open) {
      setStatus('stopped')
      setStepIndex(0)
    }
  }, [open])

  useEffect(() => {
    if (!open || status !== 'running') return undefined

    const targetId = GLOBAL_ONBOARDING_STEPS[stepIndex]?.anchor
    if (targetId) {
      const target = document.getElementById(targetId)
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }

    const timer = window.setTimeout(() => {
      setStepIndex((current) => {
        if (current >= GLOBAL_ONBOARDING_STEPS.length - 1) {
          setStatus('paused')
          return current
        }
        return current + 1
      })
    }, 2600)

    return () => window.clearTimeout(timer)
  }, [open, status, stepIndex])

  if (!open) return null

  return (
    <div className="fixed z-[110] left-4 right-4 bottom-4 sm:right-auto sm:w-[380px]">
      <div className="rounded-2xl border border-white/10 bg-slate-900/98 text-white shadow-2xl backdrop-blur-sm overflow-hidden">
        <div className="px-4 py-3 border-b border-white/10 flex items-start justify-between gap-3">
          <div>
            <div className="text-[11px] uppercase tracking-widest text-yellow-300 font-bold">Quick tour</div>
            <div className="text-sm text-slate-300 mt-0.5">Step {stepIndex + 1} of {GLOBAL_ONBOARDING_STEPS.length}</div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center justify-center h-8 w-8 rounded-lg border border-white/15 text-slate-200 hover:bg-white/10"
            aria-label="Close onboarding"
          >
            <X size={14} />
          </button>
        </div>

        <div className="px-4 py-3">
          <div className="font-extrabold text-base">{currentStep.title}</div>
          <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">{currentStep.body}</p>

          <div className="mt-3 flex gap-1.5">
            {GLOBAL_ONBOARDING_STEPS.map((step, index) => (
              <div
                key={step.title}
                className={`h-1.5 rounded-full flex-1 ${index === stepIndex ? 'bg-yellow-300' : 'bg-white/20'}`}
              />
            ))}
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {status === 'running' ? (
              <button
                type="button"
                onClick={() => setStatus('paused')}
                className="inline-flex items-center min-h-9 px-3 rounded-lg bg-yellow-400 text-slate-900 text-sm font-extrabold hover:bg-yellow-300"
              >
                <Pause size={13} className="mr-1.5" /> Pause
              </button>
            ) : (
              <button
                type="button"
                onClick={() => {
                  if (status === 'stopped') setStepIndex(0)
                  setStatus('running')
                }}
                className="inline-flex items-center min-h-9 px-3 rounded-lg bg-yellow-400 text-slate-900 text-sm font-extrabold hover:bg-yellow-300"
              >
                <Play size={13} className="mr-1.5" /> {status === 'paused' ? 'Resume' : 'Start'}
              </button>
            )}

            <button
              type="button"
              onClick={() => {
                setStatus('stopped')
                setStepIndex(0)
              }}
              className="inline-flex items-center min-h-9 px-3 rounded-lg border border-white/20 text-white text-sm font-bold hover:bg-white/10"
            >
              <Square size={13} className="mr-1.5" /> Stop
            </button>

            <button
              type="button"
              onClick={() => setStepIndex((current) => Math.max(0, current - 1))}
              className="inline-flex items-center min-h-9 px-3 rounded-lg border border-white/20 text-white text-sm font-bold hover:bg-white/10"
            >
              Back
            </button>

            <button
              type="button"
              onClick={() => setStepIndex((current) => Math.min(GLOBAL_ONBOARDING_STEPS.length - 1, current + 1))}
              className="inline-flex items-center min-h-9 px-3 rounded-lg border border-white/20 text-white text-sm font-bold hover:bg-white/10"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

const Navbar = ({ onSearch, mobileMenuOpen, setMobileMenuOpen }) => (
  <nav className="bg-slate-900 text-white sticky top-0 z-40 shadow-lg">
    <div className="container mx-auto px-4 py-3">
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="w-full md:w-auto flex justify-between items-center">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => window.scrollTo(0, 0)}>
            <div className="bg-yellow-500 text-slate-900 p-2 rounded-lg">
              <Tag size={20} className="font-bold" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-xl leading-none tracking-tight">BestDealsOnline</span>
              <span className="text-xs text-yellow-400 uppercase tracking-widest">Amazon Picks</span>
            </div>
          </div>
          <button
            className="md:hidden text-white inline-flex items-center justify-center h-10 w-10"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Menu"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        <div className={`${mobileMenuOpen ? 'flex' : 'hidden'} md:flex relative w-full md:w-1/2 flex-col md:flex-row gap-4 md:gap-0`}>
          <div className="relative w-full">
            <input
              type="text"
              placeholder="Search picks..."
              className="w-full py-2.5 px-4 pr-12 rounded-full text-slate-800 focus:outline-none focus:ring-2 focus:ring-yellow-500 transition-all shadow-inner bg-slate-100 focus:bg-white"
              onChange={(e) => onSearch(e.target.value)}
            />
            <button className="absolute right-1 top-1 bg-yellow-500 hover:bg-yellow-400 text-slate-900 rounded-full p-1.5 w-10 h-10 flex items-center justify-center transition-colors" aria-label="Search">
              <Search size={16} />
            </button>
          </div>
        </div>

        <div className={`${mobileMenuOpen ? 'flex' : 'hidden'} md:flex flex-col md:flex-row items-center gap-4 md:gap-6 text-sm font-medium w-full md:w-auto mt-4 md:mt-0`}>
          <a href="/" className="hover:text-yellow-400 transition-colors">Home</a>
          <a href="#categories" className="hover:text-yellow-400 transition-colors">Categories</a>
          <a href="/blog/index.html" className="hover:text-yellow-400 transition-colors">Blog</a>
          <a href="/best-deals-online-today.html" className="hover:text-yellow-400 transition-colors">Today</a>
          <a href="/drummer-deals.html" className="hover:text-yellow-400 transition-colors">Drummer Deals</a>
        </div>
      </div>
    </div>
  </nav>
)

const Hero = ({ apiStatus, products }) => {
  const [nowMs, setNowMs] = useState(() => Date.now())

  useEffect(() => {
    const tick = () => setNowMs(Date.now())
    tick()
    const timer = window.setInterval(tick, 1000)
    return () => window.clearInterval(timer)
  }, [])

  const dayKey = useMemo(() => new Date(nowMs).toDateString(), [nowMs])
  const deal = useMemo(() => pickDailyProduct(products, nowMs), [products, dayKey, nowMs])
  const countdown = useMemo(() => formatCountdown(msUntilNextMidnight(nowMs)), [nowMs])

  return (
    <div className="bg-gradient-to-br from-indigo-900 via-blue-900 to-slate-900 text-white py-10 md:py-16 relative overflow-hidden">
      <div className="container mx-auto px-4 flex flex-col md:flex-row items-center relative z-10">
        <div className="md:w-1/2 mb-10 md:mb-0 text-center md:text-left">
          <div className="inline-flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/50 text-yellow-400 text-xs font-bold px-3 py-1 rounded-full mb-6 backdrop-blur-sm">
            <Clock size={12} /> <span>Updated: {new Date().toLocaleDateString()}</span>
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold mb-4 leading-tight tracking-tight">
            General Amazon deals.<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-yellow-200">
              Fast picks across categories.
            </span>
          </h1>
          <p className="text-blue-100 text-lg mb-6 max-w-lg mx-auto md:mx-0 leading-relaxed">
            Curated picks across categories. Click through to see live pricing on Amazon.
          </p>
        </div>

        <div className="md:w-1/2 flex justify-center relative">
          {deal ? (
            <div className="relative w-72 md:w-96 bg-gradient-to-tr from-white/10 to-white/5 backdrop-blur-md rounded-3xl border border-white/10 p-6 md:p-8 shadow-2xl transform rotate-3 hover:rotate-0 transition-transform duration-700" data-section="deal_of_day">
              <div className="flex items-center justify-between gap-3">
                <div className="text-xs font-extrabold uppercase tracking-[0.25em] text-yellow-300">Deal of the day</div>
                <div className="text-xs text-blue-100">Resets in</div>
              </div>

              <div className="mt-3">
                <div className="font-mono text-2xl md:text-3xl font-extrabold text-yellow-200">{countdown}</div>
                <div className="text-sm text-blue-100/90 mt-1">24-hour countdown</div>
              </div>

              <div className="mt-5 flex items-center gap-4">
                <div className="w-24 h-20 md:w-28 md:h-24 rounded-2xl overflow-hidden border border-white/10 bg-white/5">
                  <img
                    src={getCategoryImage(deal.category)}
                    alt={deal.title}
                    className="w-full h-full object-cover"
                    loading="eager"
                    fetchPriority="high"
                    decoding="async"
                  />
                </div>
                <div className="flex-1 min-w-0 text-left">
                  <div className="text-[10px] font-bold uppercase tracking-[0.25em] text-blue-100/80">{deal.category || 'Amazon'}</div>
                  <div className="text-lg md:text-xl font-extrabold leading-tight mt-1 line-clamp-2">{deal.title}</div>
                  {deal.description ? <div className="text-xs text-blue-100/80 mt-2 line-clamp-2">{deal.description}</div> : null}
                </div>
              </div>

              <a
                href={deal.affiliateLink}
                target="_blank"
                rel="nofollow noopener noreferrer"
                onClick={() =>
                  trackOutboundClick({
                    url: deal.affiliateLink,
                    label: `Deal of day: ${deal.title}`,
                    category: deal.category || 'outbound',
                    section: 'deal_of_day',
                    productId: deal.id,
                    productTitle: deal.title,
                    position: 0,
                    campaign: 'deal_of_day',
                  })
                }
                className="mt-6 w-full inline-flex items-center justify-center bg-yellow-400 hover:bg-yellow-500 text-slate-900 font-extrabold px-4 py-3 rounded-2xl transition-colors shadow-sm hover:shadow-md"
              >
                Check price on Amazon <ExternalLink size={16} className="ml-2" />
              </a>

              <div className="text-[11px] text-blue-100/80 mt-3">
                Rotates daily. Always check live pricing + recent reviews on Amazon.
              </div>
            </div>
          ) : (
            <div className="relative w-72 h-72 md:w-96 md:h-96 bg-gradient-to-tr from-white/10 to-white/5 backdrop-blur-md rounded-3xl border border-white/10 p-8 flex items-center justify-center shadow-2xl transform rotate-3 hover:rotate-0 transition-transform duration-700 group cursor-pointer">
              <ShoppingBag
                size={140}
                className="text-yellow-400 drop-shadow-[0_10px_10px_rgba(0,0,0,0.5)] group-hover:scale-110 transition-transform duration-500"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const DealLens = () => {
  const [q, setQ] = useState('')

  const base = (q || '').trim()
  const query = base.length ? base : 'deals'

  const amazonCouponsLink = (searchText, campaign) => {
    const q = encodeURIComponent(searchText)
    // Amazon coupon hub supports in-page search via searchText.
    // We still include our affiliate tag in case it's honored on downstream clicks.
    return `https://www.amazon.com/coupons?searchText=${q}&tag=${AMAZON_TAG}&utm_source=bestdealsonline&utm_medium=site&utm_campaign=${encodeURIComponent(
      campaign
    )}`
  }

  const linkFor = (label, href, campaign) => {
    return (
      <a
        href={href}
        target="_blank"
        rel="nofollow noopener noreferrer"
        onClick={() =>
          trackOutboundClick({
            url: href,
            label,
            category: 'coupons',
            section: 'deal_lens',
            campaign,
          })
        }
        className="inline-flex items-center justify-center px-3 py-2 rounded-xl bg-slate-900 text-white font-bold text-sm hover:bg-slate-800 transition-colors"
      >
        {label} <ExternalLink size={14} className="ml-2" />
      </a>
    )
  }

  return (
    <div className="bg-white border-y border-slate-200 mb-10" data-section="deal_lens">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col lg:flex-row lg:items-center gap-3 lg:gap-6">
          <div className="flex-1">
            <div className="text-xs font-extrabold uppercase tracking-[0.25em] text-slate-500">Deal Lens</div>
            <div className="text-lg font-extrabold text-slate-900 mt-1">Coupons + hidden discounts (fast)</div>
            <div className="text-sm text-slate-600 mt-1">Type what you want and open Amazon in “coupon mode”.</div>
          </div>

          <div className="flex-1">
            <label className="block text-xs font-bold text-slate-600 mb-2" htmlFor="deal-lens-q">Search</label>
            <input
              id="deal-lens-q"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="e.g., USB-C charger, air fryer, kids headphones"
              className="w-full py-3 px-4 rounded-2xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-yellow-400"
            />
          </div>

          <div className="flex flex-wrap gap-2 justify-start lg:justify-end">
            {linkFor('Coupons hub', amazonCouponsLink(query, 'deal_lens_coupons_hub'), 'deal_lens_coupons_hub')}
            {linkFor('Coupon-eligible', amazonCouponsLink(`${query} coupon`, 'deal_lens_coupon_eligible'), 'deal_lens_coupon_eligible')}
            {linkFor('Subscribe & Save', amazonSearchLink(`${query} subscribe and save`, 'deal_lens_sns'), 'deal_lens_sns')}
            {linkFor("Today's deals", amazonSearchLink(`${query} deals today`, 'deal_lens_today'), 'deal_lens_today')}
          </div>
        </div>
      </div>
    </div>
  )
}

const AnalyzerLauncherSection = () => {
  const openAnalyzer = () => {
    if (typeof window === 'undefined') return
    window.dispatchEvent(new CustomEvent('bdo-open-link-analyzer'))
    window.setTimeout(() => {
      if (!document.getElementById('bdo-link-analyzer-overlay')) {
        window.location.hash = 'link-analyzer'
      }
    }, 50)
  }

  return (
    <section id="link-analyzer" className="container mx-auto px-4 mt-8 scroll-mt-32" data-section="link_analyzer">
      <div className="rounded-2xl border border-slate-200 bg-gradient-to-r from-slate-900 to-slate-800 text-white p-5 md:p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 text-[11px] font-extrabold uppercase tracking-[0.2em] text-yellow-300">
              <Search size={12} /> Amazon Link Analyzer
            </div>
            <h2 className="text-xl md:text-2xl font-extrabold mt-2">Use the popup from any page</h2>
            <p className="text-slate-200 text-sm mt-1 max-w-2xl">
              Open the floating analyzer, paste any Amazon URL or ASIN, and jump straight to the product or better-tagged comparisons.
            </p>
          </div>
          <button
            type="button"
            onClick={openAnalyzer}
            className="inline-flex items-center justify-center min-h-11 px-5 rounded-xl bg-yellow-400 text-slate-900 font-extrabold hover:bg-yellow-300 transition-colors"
          >
            Open analyzer popup <ArrowUpRight size={15} className="ml-2" />
          </button>
        </div>
      </div>
    </section>
  )
}

const ProductCard = ({ product, tracking }) => {
  const [imageFailed, setImageFailed] = useState(false)
  const dealTruth = product.dealTruth
  const confidenceScore = Math.max(0, Math.min(100, Number(dealTruth?.score ?? 0)))
  const rating = Number(product?.rating || 0)
  const formattedReviews = formatCompactCount(product?.reviews)
  const link = product?.affiliateLink || amazonSearchLink(product?.title || 'amazon deals', 'bdo_trending_card')
  const highlight = dealHighlightText(product, confidenceScore)
  const isTopValue = confidenceScore >= 60
  const badgeClasses = isTopValue
    ? 'border-emerald-200 bg-emerald-100 text-emerald-800'
    : 'border-amber-200 bg-amber-100 text-amber-800'
  const badgeLabel = isTopValue ? 'Top Value' : 'Price Drop'

  useEffect(() => {
    setImageFailed(false)
  }, [product?.imageUrl])
  const showFallbackImage = !product?.imageUrl || imageFailed

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-[0_6px_18px_rgba(15,23,42,0.06)] hover:shadow-[0_16px_30px_rgba(15,23,42,0.1)] transition-all duration-300 flex flex-col h-full group relative overflow-hidden">
      <div className="absolute top-3 left-3 z-10">
        <span className="inline-flex items-center rounded-md bg-slate-900 text-white text-[10px] font-extrabold tracking-widest uppercase px-3 py-1">
          Amazon
        </span>
      </div>

      <div className="relative h-60 bg-slate-50 border-b border-slate-200 overflow-hidden flex items-center justify-center p-6">
        <img
          src={showFallbackImage ? getCategoryImage(product.category) : product.imageUrl}
          alt={product.title}
          className={showFallbackImage ? 'w-full h-full object-cover' : 'max-h-44 max-w-full object-contain'}
          loading="lazy"
          onError={() => setImageFailed(true)}
        />
      </div>

      <div className="p-5 md:p-6 flex-grow flex flex-col">
        <div className="flex items-center justify-between mb-3">
          <div className="text-[11px] font-extrabold text-blue-700 uppercase tracking-[0.18em]">
            {product.category}
          </div>
          <div className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-600">
            <Star size={13} className="text-amber-400 fill-amber-400" />
            <span className="font-bold text-slate-700">{rating ? rating.toFixed(1) : '0.0'}</span>
            <span className="text-xs text-slate-400">({formattedReviews})</span>
          </div>
        </div>

        <h3 className="font-extrabold text-slate-900 mb-3 leading-tight text-lg line-clamp-2">
          {product.title}
        </h3>

        <p className="text-slate-600 text-sm leading-relaxed line-clamp-2">{highlight}</p>

        <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center justify-between gap-3">
            <div className="inline-flex items-center gap-1.5 text-sm font-bold text-slate-700">
              <ShieldCheck size={15} className="text-emerald-500" />
              Deal Confidence
            </div>
            <div className="text-xl font-extrabold text-slate-900">{confidenceScore}/100</div>
          </div>
          <div className="mt-2 h-1.5 rounded-full bg-slate-200 overflow-hidden">
            <div className="h-full rounded-full bg-amber-500" style={{ width: `${confidenceScore}%` }} />
          </div>
          <div className="mt-3 flex items-center justify-between gap-2">
            <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-[11px] font-extrabold uppercase tracking-wide ${badgeClasses}`}>
              {isTopValue ? <ShieldCheck size={12} /> : <Zap size={12} />}
              {badgeLabel}
            </div>
            <div className="inline-flex items-center gap-1 text-xs text-slate-500 italic">
              <Clock size={12} />
              Updated 12m ago
            </div>
          </div>
        </div>

        <div className="mt-auto pt-5">
          <a
            href={link}
            target="_blank"
            rel="nofollow noopener noreferrer"
            onClick={() =>
              trackOutboundClick({
                url: link,
                label: product.title,
                category: product.category || 'outbound',
                section: tracking?.section,
                productId: product.id,
                productTitle: product.title,
                position: tracking?.position,
                campaign: tracking?.campaign,
              })
            }
            className="block w-full bg-yellow-400 hover:bg-yellow-300 text-slate-900 text-center text-lg font-extrabold py-3 rounded-xl transition-colors flex items-center justify-center gap-2 shadow-sm"
          >
            View Today's Deal <ExternalLink size={16} />
          </a>
          <div className="mt-2 text-center text-xs text-slate-400 inline-flex w-full items-center justify-center gap-1">
            Price from Amazon <Info size={12} />
          </div>
        </div>
      </div>
    </div>
  )
}

const CompactProductCard = ({ product, tracking }) => {
  const [imageFailed, setImageFailed] = useState(false)
  const dealTruth = product.dealTruth
  const link = product?.affiliateLink || amazonSearchLink(product?.title || 'amazon deals', 'bdo_top_picks')

  useEffect(() => {
    setImageFailed(false)
  }, [product?.imageUrl])

  return (
    <a
      href={link}
      target="_blank"
      rel="nofollow noopener noreferrer"
      onClick={() =>
        trackOutboundClick({
          url: link,
          label: product.title,
          category: product.category || 'outbound',
          section: tracking?.section,
          productId: product.id,
          productTitle: product.title,
          position: tracking?.position,
          campaign: tracking?.campaign,
        })
      }
      className="min-w-[240px] max-w-[240px] bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-all p-4 flex flex-col gap-2"
    >
      <div className="flex items-center justify-between">
        <div className="text-[10px] font-bold text-blue-600 uppercase tracking-widest bg-blue-50 px-2 py-0.5 rounded">
          {product.category}
        </div>
        <ExternalLink size={14} className="text-slate-400" />
      </div>
      <div className="h-20 rounded-lg bg-gradient-to-b from-gray-50 to-white border border-slate-100 overflow-hidden flex items-center justify-center">
        {product.imageUrl && !imageFailed ? (
          <img
            src={product.imageUrl}
            alt={product.title}
            className="max-h-16 object-contain"
            loading="lazy"
            onError={() => setImageFailed(true)}
          />
        ) : (
          <img
            src={getCategoryImage(product.category)}
            alt={`${product.category} lifestyle`}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        )}
      </div>
      <div className="font-bold text-slate-800 text-sm line-clamp-2">{product.title}</div>
      <div className="text-[11px] font-bold text-indigo-700">
        {dealTruth?.score != null ? `DealTruth ${dealTruth.score}/100` : 'DealTruth pending'}
      </div>
      <div className="text-xs text-slate-500">{dealTruth?.decision?.label ? dealTruth.decision.label : 'Check price on Amazon'}</div>
    </a>
  )
}

const JumpBar = () => (
  <div className="bg-white/80 backdrop-blur border-b border-slate-200 sticky top-[60px] md:top-[74px] z-30">
    <div className="container mx-auto px-4 py-2 flex gap-2 overflow-x-auto hide-scrollbar">
      <a href="#categories" className="px-3 py-2 rounded-full text-sm font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 whitespace-nowrap">Categories</a>
      <a href="#budget" className="px-3 py-2 rounded-full text-sm font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 whitespace-nowrap">Budget</a>
      <a href="#top-picks" className="px-3 py-2 rounded-full text-sm font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 whitespace-nowrap">Top Picks</a>
      <a href="#trending" className="px-3 py-2 rounded-full text-sm font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 whitespace-nowrap">Trending</a>
      <a href="#link-analyzer" className="px-3 py-2 rounded-full text-sm font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 whitespace-nowrap">Link Analyzer</a>
      <a href="#dealtruth" className="px-3 py-2 rounded-full text-sm font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 whitespace-nowrap">How DealTruth Works</a>
      <a href="/blog/index.html" className="px-3 py-2 rounded-full text-sm font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 whitespace-nowrap">Blog</a>
    </div>
  </div>
)
const CategoryTiles = ({ onPick }) => {
  const tiles = [
    { key: 'Electronics', img: '/images/categories/electronics.webp', blurb: 'Chargers, audio, smart home' },
    { key: 'Home', img: '/images/categories/home.webp', blurb: 'Sleep, organization, comfort' },
    { key: 'Kitchen', img: '/images/categories/kitchen.webp', blurb: 'Meal prep, appliances, coffee' },
    { key: 'Tools', img: '/images/categories/tools.webp', blurb: 'DIY essentials & kits' },
    { key: 'Kids', img: '/images/categories/kids.webp', blurb: 'School & toys' },
    { key: 'Beauty', img: '/images/categories/beauty.webp', blurb: 'Skincare & grooming' },
    { key: 'Fitness', img: '/images/categories/fitness.webp', blurb: 'Home gym basics' },
    { key: 'Pets', img: '/images/categories/pets.webp', blurb: 'Pet comfort & care' },
  ]

  return (
    <div className="container mx-auto px-4 mt-10 relative z-20">
      <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-4 md:p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl md:text-2xl font-extrabold text-slate-900">Browse categories</h2>
          <div className="text-xs text-slate-500">Tap a category to jump into picks</div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {tiles.map((t) => (
            <button
              key={t.key}
              onClick={() => onPick(t.key)}
              className="text-left bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-blue-100 transition-all duration-300 flex flex-col h-full group overflow-hidden"
            >
              <div className="relative h-44 bg-gradient-to-b from-gray-50 to-white flex items-center justify-center overflow-hidden">
                <img
                  src={t.img}
                  alt={t.key}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  loading="lazy"
                />
                <div className="absolute top-3 left-3">
                  <span className="bg-slate-900/90 text-white text-[10px] font-bold px-2 py-1 rounded backdrop-blur-md">
                    Category
                  </span>
                </div>
              </div>

              <div className="p-5 flex-grow flex flex-col">
                <div className="text-[10px] font-bold text-blue-600 uppercase tracking-widest bg-blue-50 px-2 py-0.5 rounded w-fit mb-2">
                  {t.key}
                </div>
                <div className="font-bold text-slate-800 text-lg leading-tight mb-2">{t.key} Picks</div>
                <div className="text-sm text-slate-600 mb-4">{t.blurb}</div>

                <div className="mt-auto">
                  <div className="w-full bg-yellow-400 hover:bg-yellow-500 text-slate-900 text-center font-bold py-3 rounded-lg transition-colors flex items-center justify-center gap-2 shadow-sm hover:shadow-md">
                    View {t.key} <ArrowUpRight size={16} />
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

const UnderBudget = ({ title, query }) => (
  <a
    href={amazonSearchLink(query, 'bdo_under_budget')}
    target="_blank"
    rel="nofollow noopener noreferrer"
    onClick={() =>
      trackOutboundClick({
        url: amazonSearchLink(query, 'bdo_under_budget'),
        label: title,
        category: 'budget',
        section: 'homepage_budget',
        campaign: 'bdo_under_budget',
      })
    }
    className="bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-all p-4 flex items-center justify-between"
  >
    <div>
      <div className="font-extrabold text-slate-900">{title}</div>
      <div className="text-xs text-slate-500">Click to see live prices on Amazon</div>
    </div>
    <ExternalLink size={18} className="text-slate-400" />
  </a>
)

const UnderBudgetRow = () => (
  <div className="container mx-auto px-4 pt-10">
    <div className="flex items-center justify-between mb-4">
      <h2 className="text-xl md:text-2xl font-extrabold text-slate-900">Shop by budget</h2>
      <div className="text-xs text-slate-500">Quick filters that convert</div>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
      <UnderBudget title="Under $25 finds" query="best deals under 25" />
      <UnderBudget title="Under $50 upgrades" query="best deals under 50" />
      <UnderBudget title="Under $100 big wins" query="best deals under 100" />
    </div>
  </div>
)

const TopPicks = ({ products }) => {
  const cats = ['Electronics', 'Home', 'Kitchen', 'Tools', 'Kids', 'Beauty', 'Fitness', 'Pets']
  const byCat = new Map(
    cats.map((cat) => [
      cat,
      products
        .filter((product) => product.category === cat)
        .sort((a, b) => (b?.dealTruth?.score ?? 0) - (a?.dealTruth?.score ?? 0))
        .slice(0, 6),
    ])
  )

  return (
    <div className="container mx-auto px-4 pt-10">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-extrabold text-slate-900">Top Picks</h2>
        
      </div>

      <div className="grid gap-6">
        {cats.map((cat) => (
          <div key={cat} className="min-w-0">
            <div className="flex items-baseline justify-between mb-2 w-full min-w-0">
              <div className="font-bold text-slate-800">{cat}</div>
              <div className="text-xs text-slate-500">Top {byCat.get(cat).length}</div>
            </div>
            <div className="flex w-full min-w-0 max-w-full gap-4 overflow-x-auto pb-2 hide-scrollbar">
              {byCat.get(cat).map((p, i) => (
                <CompactProductCard
                  key={p.id}
                  product={p}
                  tracking={{
                    section: `top_picks_${cat.toLowerCase()}`,
                    position: i,
                    campaign: `top_picks_${cat.toLowerCase()}`,
                  }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

const DealTruthGuide = ({ products, className = 'mt-14' }) => {
  const stats = useMemo(() => {
    const total = products.length
    let full = 0
    let shortWindow = 0
    let provisional = 0

    for (const product of products) {
      const mode = product?.dealTruth?.baselineMode
      if (mode === '90d') {
        full += 1
      } else if (mode && mode !== 'none') {
        shortWindow += 1
      } else {
        provisional += 1
      }
    }

    return {
      total,
      full,
      shortWindow,
      provisional,
      fullPct: total ? Math.round((full / total) * 100) : 0,
    }
  }, [products])

  return (
    <section className={`${className} rounded-3xl border border-slate-200 bg-gradient-to-br from-white via-slate-50 to-blue-50 p-6 md:p-10 shadow-sm`}>
      <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 bg-slate-900 text-white text-xs font-extrabold tracking-[0.2em] uppercase rounded-full px-3 py-1">
            <Tag size={12} /> DealTruth Explainer
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-slate-900 mt-4">Real Value, No Marketing Fluff.</h2>
          <p className="text-slate-700 mt-3 leading-relaxed">
            Most deal sites just chase the biggest "off MSRP" sticker. We ignore the stickers and look at the math.
            We rank every deal based on what actually matters: your final price, seller reputation, and whether that
            "discount" is actually just a Tuesday price hike in disguise.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
          <div className="bg-white border border-slate-200 rounded-xl px-3 py-2">
            <div className="text-slate-500 uppercase tracking-wider font-bold">Full 90-day history</div>
            <div className="text-slate-900 font-extrabold text-lg">{stats.full}</div>
            <div className="text-slate-500 mt-0.5">Verified price trends.</div>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl px-3 py-2">
            <div className="text-slate-500 uppercase tracking-wider font-bold">Short-window alerts</div>
            <div className="text-slate-900 font-extrabold text-lg">{stats.shortWindow}</div>
            <div className="text-slate-500 mt-0.5">Recent volatility tracked.</div>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl px-3 py-2">
            <div className="text-slate-500 uppercase tracking-wider font-bold">Provisional scores</div>
            <div className="text-slate-900 font-extrabold text-lg">{stats.provisional}</div>
            <div className="text-slate-500 mt-0.5">New deals under active audit.</div>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4 mt-8">
        <div className="bg-white rounded-2xl border border-slate-200 p-5">
          <div className="font-extrabold text-slate-900 text-lg">1) We Kill the "Fake" Discount</div>
          <p className="text-slate-600 text-sm mt-2">
            Retailers love "anchor prices" - that fake MSRP no one actually pays. We calculate True Cost
            (price + shipping - coupons) and compare it against observed prices from the last 90 days.
            If the "discount" is not real, we flag it.
          </p>
        </div>
        <div className="bg-white rounded-2xl border border-slate-200 p-5">
          <div className="font-extrabold text-slate-900 text-lg">2) Rarity Meets Reliability</div>
          <p className="text-slate-600 text-sm mt-2">
            Is this price a once-a-year event or just a once-a-week cycle? Every deal card shows how rare the
            price is and how much we trust the underlying data.
          </p>
        </div>
        <div className="bg-white rounded-2xl border border-slate-200 p-5">
          <div className="font-extrabold text-slate-900 text-lg">3) Stop Guessing, Start Knowing</div>
          <p className="text-slate-600 text-sm mt-2">
            Do not get FOMO from a red "Sale" badge. Our model estimates the odds of a near-term price drop and
            tells you whether it is a Buy Now moment or a smarter Wait and Save setup.
          </p>
        </div>
      </div>

      <div className="mt-7 bg-slate-900 text-white rounded-2xl p-5 md:p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="font-extrabold text-lg">The Score Guide</div>
          <div className="text-slate-200 text-sm mt-2 space-y-1">
            <p><span className="font-bold text-white">80+</span> (The Unicorn): Exceptional value. Buy it before it is gone.</p>
            <p><span className="font-bold text-white">65-79</span> (Strong Buy): A solid win. Better than 90% of typical sales.</p>
            <p><span className="font-bold text-white">50-64</span> (Watchlist): Decent, but we have seen better. Maybe wait for a coupon.</p>
            <p><span className="font-bold text-white">Below 50</span> (The Pass): Marketing noise. You are not actually saving money.</p>
            <p className="pt-1 text-yellow-200">
              Pro Tip: Look for the "Provisional" tag on brand-new listings - we are still gathering data to increase confidence.
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <a href="/best-deals-with-price-history.html" className="inline-flex items-center min-h-10 px-4 rounded-xl bg-yellow-400 text-slate-900 font-extrabold hover:bg-yellow-300 transition-colors">
            Why price history matters <ArrowUpRight size={16} className="ml-1.5" />
          </a>
          <a href="/best-deals-legit-or-scam.html" className="inline-flex items-center min-h-10 px-4 rounded-xl border border-white/20 text-white font-bold hover:bg-white/10 transition-colors">
            Deal safety checks <ArrowUpRight size={16} className="ml-1.5" />
          </a>
        </div>
      </div>
    </section>
  )
}

const Footer = () => (
  <footer className="bg-slate-950 text-slate-400 py-16 border-t border-slate-900 text-sm">
    <div className="container mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-12">
      <div>
        <div className="flex items-center gap-2 mb-6 text-white">
          <div className="bg-yellow-500 text-slate-900 p-1.5 rounded font-bold">
            <Tag size={16} />
          </div>
          <span className="font-bold text-lg">BestDealsOnline</span>
        </div>
        <p className="mb-6 leading-relaxed">
          Amazon-only picks and under-$ guides. Click through to see live prices on Amazon.
        </p>
      </div>
      <div>
        <h4 className="text-white font-bold mb-6 text-base">Hubs</h4>
        <ul className="space-y-3">
          <li><a href="/electronics-deals.html" className="inline-flex items-center min-h-10 px-2 rounded-md hover:text-yellow-400 hover:bg-slate-900 transition-colors">Electronics</a></li>
          <li><a href="/kitchen-deals.html" className="inline-flex items-center min-h-10 px-2 rounded-md hover:text-yellow-400 hover:bg-slate-900 transition-colors">Kitchen</a></li>
          <li><a href="/home-deals.html" className="inline-flex items-center min-h-10 px-2 rounded-md hover:text-yellow-400 hover:bg-slate-900 transition-colors">Home</a></li>
          <li><a href="/fitness-deals.html" className="inline-flex items-center min-h-10 px-2 rounded-md hover:text-yellow-400 hover:bg-slate-900 transition-colors">Fitness</a></li>
          <li><a href="/kids-deals.html" className="inline-flex items-center min-h-10 px-2 rounded-md hover:text-yellow-400 hover:bg-slate-900 transition-colors">Kids</a></li>
          <li><a href="/pets-deals.html" className="inline-flex items-center min-h-10 px-2 rounded-md hover:text-yellow-400 hover:bg-slate-900 transition-colors">Pets</a></li>
          <li><a href="/tools-deals.html" className="inline-flex items-center min-h-10 px-2 rounded-md hover:text-yellow-400 hover:bg-slate-900 transition-colors">Tools</a></li>
          <li><a href="/beauty-deals.html" className="inline-flex items-center min-h-10 px-2 rounded-md hover:text-yellow-400 hover:bg-slate-900 transition-colors">Beauty</a></li>
        </ul>
      </div>
      <div>
        <h4 className="text-white font-bold mb-6 text-base">Links</h4>
        <ul className="space-y-3">
          <li><a href="/affiliate-disclosure.html" className="inline-flex items-center min-h-10 px-2 rounded-md hover:text-yellow-400 hover:bg-slate-900 transition-colors">Affiliate disclosure</a></li>
          <li><a href="/privacy.html" className="inline-flex items-center min-h-10 px-2 rounded-md hover:text-yellow-400 hover:bg-slate-900 transition-colors">Privacy</a></li>
          <li><a href="/drummer-deals.html" className="inline-flex items-center min-h-10 px-2 rounded-md hover:text-yellow-400 hover:bg-slate-900 transition-colors">Drummer Deals</a></li>
        </ul>
      </div>
      <div>
        <h4 className="text-white font-bold mb-6 text-base">Amazon Associate disclosure</h4>
        <p className="leading-relaxed mb-4 text-xs">
          As an Amazon Associate, we earn from qualifying purchases.
        </p>
        <p className="leading-relaxed mb-0 text-xs">
          This site may earn a commission when you buy through links (at no extra cost to you).{' '}
          <a className="underline inline-flex items-center min-h-10 px-1 hover:text-yellow-400" href="/affiliate-disclosure.html">Details</a>
        </p>
        <p className="leading-relaxed mt-4 mb-0 text-xs">
          Prices and availability are subject to change.
        </p>
      </div>
    </div>

    <div className="container mx-auto px-4 mt-16 pt-8 border-t border-slate-900 flex flex-col md:flex-row justify-between items-center text-xs text-slate-500">
      <p>&copy; {new Date().getFullYear()} BestDealsOnline.us. All rights reserved.</p>
    </div>
  </footer>
)

async function fetchProductsJson(limit = 300) {
  const res = await fetch(resolveDealsUrl(limit), { headers: { Accept: 'application/json' } })
  if (!res.ok) throw new Error(`products.json fetch failed: ${res.status}`)
  return await res.json()
}

const App = () => {
  const [products, setProducts] = useState(SEED_PRODUCTS)
  const [apiStatus, setApiStatus] = useState('not configured')
  const [isInitialLoading, setIsInitialLoading] = useState(true)
  const [loadingMessage, setLoadingMessage] = useState('Loading live deals...')
  const [loadingProgress, setLoadingProgress] = useState(12)
  const [onboardingOpen, setOnboardingOpen] = useState(false)

  const [selectedCategory, setSelectedCategory] = useState('All')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortOption, setSortOption] = useState('dealtruth_desc')
  const [visibleCount, setVisibleCount] = useState(DEALS_PAGE_SIZE)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    ;(async () => {
      const startedAt = Date.now()
      try {
        setLoadingMessage('Connecting to live deals feed...')
        setLoadingProgress(22)
        const data = await fetchProductsJson(300)
        setLoadingMessage('Scoring deals with DealTruth...')
        setLoadingProgress(70)
        if (data?.items?.length) {
          setProducts(data.items)
          setApiStatus(DEALS_API_BASE ? `worker api (${data.items.length})` : `static catalog (${data.items.length})`)
        } else {
          setApiStatus(DEALS_API_BASE ? 'worker api (empty)' : 'static catalog (empty)')
        }
      } catch (e) {
        setApiStatus('offline (using seed items)')
        setLoadingMessage('Using fallback catalog...')
        setLoadingProgress(78)
      } finally {
        setLoadingMessage('Preparing interface...')
        setLoadingProgress(96)
        const elapsed = Date.now() - startedAt
        const minLoadingMs = 800
        if (elapsed < minLoadingMs) {
          await new Promise((resolve) => window.setTimeout(resolve, minLoadingMs - elapsed))
        }
        setLoadingProgress(100)
        setIsInitialLoading(false)
      }
    })()
  }, [])

  useEffect(() => {
    setVisibleCount(DEALS_PAGE_SIZE)
  }, [selectedCategory, searchQuery, sortOption])

  const scoredProducts = useMemo(() => scoreProductList(products), [products])
  const uniqueProducts = useMemo(() => dedupeProductsByTitleCategory(scoredProducts), [scoredProducts])

  const processedProducts = useMemo(() => {
    let result = uniqueProducts.filter((product) => {
      const matchesCategory = selectedCategory === 'All' || product.category === selectedCategory
      const matchesSearch =
        (product.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (product.category || '').toLowerCase().includes(searchQuery.toLowerCase())
      return matchesCategory && matchesSearch
    })

    switch (sortOption) {
      case 'dealtruth_desc':
      case 'recommended':
        result.sort((a, b) => {
          const scoreDelta = (b?.dealTruth?.score ?? 0) - (a?.dealTruth?.score ?? 0)
          if (scoreDelta !== 0) return scoreDelta
          return (b.reviews || 0) - (a.reviews || 0)
        })
        break
      case 'price_asc':
        result.sort((a, b) => (a.price ?? Number.POSITIVE_INFINITY) - (b.price ?? Number.POSITIVE_INFINITY))
        break
      case 'price_desc':
        result.sort((a, b) => (b.price ?? 0) - (a.price ?? 0))
        break
      case 'rating_desc':
        result.sort((a, b) => (b.rating || 0) - (a.rating || 0))
        break
      case 'reviews_desc':
        result.sort((a, b) => (b.reviews || 0) - (a.reviews || 0))
        break
      default:
        break
    }

    const shouldDiversify =
      selectedCategory === 'All' &&
      !String(searchQuery || '').trim() &&
      (sortOption === 'dealtruth_desc' || sortOption === 'recommended')

    if (shouldDiversify) {
      result = diversifyProductsByCategory(
        result,
        CATEGORIES.filter((category) => category !== 'All')
      )
    }

    return result
  }, [selectedCategory, searchQuery, sortOption, uniqueProducts])

  const visibleProducts = useMemo(() => processedProducts.slice(0, visibleCount), [processedProducts, visibleCount])
  const hasMoreProducts = visibleProducts.length < processedProducts.length

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 font-sans text-slate-800">
      {isInitialLoading ? <LoadingScreen message={loadingMessage} progress={loadingProgress} /> : null}
      {!isInitialLoading ? <OnboardingModal open={onboardingOpen} onClose={() => setOnboardingOpen(false)} /> : null}
      <DisclosureBanner />
      <Navbar onSearch={setSearchQuery} mobileMenuOpen={mobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen} />

      <main className="flex-grow">
        <Hero apiStatus={apiStatus} products={uniqueProducts} />

        <JumpBar />

        {selectedCategory === 'All' && !searchQuery && (
          <>
            <div id="categories" className="scroll-mt-32" />
            <CategoryTiles
              onPick={(cat) => {
                setSelectedCategory(cat)
                window.scrollTo({ top: 0, behavior: 'smooth' })
              }}
            />
          </>
        )}

        <div className="bg-white border-b border-slate-200 sticky top-[60px] md:top-[74px] z-30 shadow-sm">
          <div className="container mx-auto px-4 py-3 flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex gap-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0 hide-scrollbar">
              {CATEGORIES.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-full text-sm font-semibold transition-all whitespace-nowrap border ${
                    selectedCategory === category
                      ? 'bg-slate-900 text-white border-slate-900 shadow-md'
                      : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50 hover:border-slate-300'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2 w-full md:w-auto">
              <span className="text-sm text-slate-500 hidden md:inline">Sort by:</span>
              <div className="relative w-full md:w-52">
                <select
                  className="w-full appearance-none bg-white border border-slate-200 text-slate-700 py-2 px-4 pr-8 rounded-lg text-sm focus:outline-none focus:border-blue-500 cursor-pointer"
                  value={sortOption}
                  onChange={(e) => setSortOption(e.target.value)}
                >
                  {SORT_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
                <ChevronDown size={14} className="absolute right-3 top-3 text-slate-400 pointer-events-none" />
              </div>
            </div>
          </div>
        </div>

        <div id="trending" />
        <div className="container mx-auto px-4 py-10">
          <div className="flex flex-col md:flex-row md:items-start justify-between mb-8 gap-4">
            <div>
              <div className="inline-flex items-center gap-2 text-[11px] font-extrabold uppercase tracking-[0.2em] text-blue-600">
                <span className="inline-flex items-center justify-center w-6 h-6 rounded-md bg-blue-600 text-white">
                  <Activity size={12} />
                </span>
                Live Feed
              </div>
              <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 mt-3">
                {selectedCategory === 'All' ? "Today's Top Value Finds" : `${selectedCategory} Top Value Finds`}
              </h2>
              <p className="text-slate-500 text-lg mt-3 max-w-3xl">
                Ranked by <span className="font-extrabold text-slate-800">DealTruth™</span> &mdash; we analyze pricing history, seller trust, and review quality so you don&apos;t have to.
              </p>
            </div>
            <span className="inline-flex items-center gap-1.5 text-sm font-extrabold text-slate-500 uppercase tracking-wider bg-white px-5 py-3 rounded-full border border-slate-200 self-start md:self-auto">
              {visibleProducts.length} of {processedProducts.length} items
              <ChevronRight size={14} />
            </span>
          </div>

          {processedProducts.length > 0 ? (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {visibleProducts.map((product, i) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    tracking={{
                      section: selectedCategory === 'All' ? 'trending_all' : `trending_${String(selectedCategory).toLowerCase()}`,
                      position: i,
                      campaign: selectedCategory === 'All' ? 'trending_all' : `trending_${String(selectedCategory).toLowerCase()}`,
                    }}
                  />
                ))}
              </div>
              {hasMoreProducts && (
                <div className="mt-8 flex flex-col items-center gap-3">
                  <p className="text-sm text-slate-500">
                    {processedProducts.length - visibleProducts.length} more deals available
                  </p>
                  <button
                    onClick={() => setVisibleCount((count) => count + DEALS_PAGE_SIZE)}
                    className="inline-flex items-center justify-center min-h-10 px-6 py-3 rounded-xl bg-slate-900 text-white font-bold hover:bg-slate-800 transition-colors shadow-sm"
                  >
                    Show more deals
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-24 bg-white rounded-2xl border border-dashed border-slate-200 shadow-sm">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-slate-50 rounded-full mb-6">
                <Search size={40} className="text-slate-300" />
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">No results</h3>
              <p className="text-slate-500 max-w-md mx-auto mb-6">Try another category or clear your search.</p>
              <button
                onClick={() => {
                  setSelectedCategory('All')
                  setSearchQuery('')
                }}
                className="bg-slate-900 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-slate-800 transition-colors"
              >
                Clear
              </button>
            </div>
          )}

          <div className="mt-16 bg-indigo-900 text-white py-14 rounded-3xl relative overflow-hidden">
            <div className="container mx-auto px-6 text-center relative z-10">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-white/10 rounded-full mb-6 backdrop-blur-sm">
                <Mail size={32} className="text-yellow-400" />
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Join the VIP List</h2>
              <p className="text-indigo-200 mb-8 max-w-xl mx-auto text-lg">We’ll add email capture once you’re ready.</p>
              <div className="flex flex-col sm:flex-row justify-center gap-3 max-w-md mx-auto">
                <input
                  type="email"
                  placeholder="Enter your email address"
                  className="px-6 py-4 rounded-xl text-slate-900 w-full focus:outline-none focus:ring-4 focus:ring-yellow-500/50 shadow-lg"
                />
                <button className="bg-yellow-500 hover:bg-yellow-400 text-slate-900 font-bold px-8 py-4 rounded-xl transition-colors whitespace-nowrap shadow-lg">
                  Subscribe
                </button>
              </div>
            </div>
          </div>
        </div>

        {selectedCategory === 'All' && !searchQuery && (
          <>
            <div id="budget" />
            <UnderBudgetRow />
            <div id="top-picks" />
            <TopPicks products={uniqueProducts} />
          </>
        )}

        <div className="mt-10">
          <DealLens />
        </div>

        <AnalyzerLauncherSection />

        <div id="dealtruth" className="scroll-mt-32" />
        <div className="container mx-auto px-4 pt-8 pb-10">
          <DealTruthGuide products={uniqueProducts} className="mt-0" />
        </div>
      </main>

      <Footer />

      {!isInitialLoading && !onboardingOpen ? (
        <button
          type="button"
          onClick={() => setOnboardingOpen(true)}
          className="fixed bottom-4 left-4 z-[110] inline-flex items-center justify-center min-h-11 px-4 rounded-xl bg-slate-900 text-white font-bold shadow-lg hover:bg-slate-800 transition-colors"
        >
          Quick tour
        </button>
      ) : null}
    </div>
  )
}

export default App
