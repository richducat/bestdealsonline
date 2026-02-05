import React, { useEffect, useMemo, useState } from 'react'

function pickDailyProduct(products) {
  const items = Array.isArray(products) ? products.filter((p) => p && p.affiliateLink) : []
  if (!items.length) return null

  // Stable per-day selection.
  const d = new Date()
  const seed = Number(String(d.getFullYear()) + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0'))
  const idx = seed % items.length
  return items[idx]
}

function msUntilNextMidnight() {
  const now = new Date()
  const next = new Date(now)
  next.setHours(24, 0, 0, 0)
  return Math.max(0, next.getTime() - now.getTime())
}

function formatCountdown(ms) {
  const total = Math.max(0, Math.floor(ms / 1000))
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
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
  CheckCircle,
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
  ExternalLink,
  Copy,
  Clock,
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
  { label: 'Recommended', value: 'recommended' },
  { label: 'Top Rated', value: 'rating_desc' },
  { label: 'Most Reviews', value: 'reviews_desc' },
  { label: 'Price: Low → High', value: 'price_asc' },
  { label: 'Price: High → Low', value: 'price_desc' },
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

const DisclosureBanner = () => {
  const [visible, setVisible] = useState(true)
  if (!visible) return null
  return (
    <div className="bg-slate-100 border-b border-slate-200 text-xs text-slate-600 py-2 px-4 flex justify-between items-center">
      <span>
        <strong>Affiliate Disclosure:</strong> BestDealsOnline.us is reader-supported. When you buy through links on our
        site, we may earn an affiliate commission at no extra cost to you. <a className="underline" href="/affiliate-disclosure.html">Details</a>
      </span>
      <button onClick={() => setVisible(false)} className="text-slate-400 hover:text-slate-800" aria-label="Dismiss">
        <X size={14} />
      </button>
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
          <button className="md:hidden text-white" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} aria-label="Menu">
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
            <button className="absolute right-1 top-1 bg-yellow-500 hover:bg-yellow-400 text-slate-900 rounded-full p-1.5 w-8 h-8 flex items-center justify-center transition-colors" aria-label="Search">
              <Search size={16} />
            </button>
          </div>
        </div>

        <div className={`${mobileMenuOpen ? 'flex' : 'hidden'} md:flex flex-col md:flex-row items-center gap-4 md:gap-6 text-sm font-medium w-full md:w-auto mt-4 md:mt-0`}>
          <a href="/drummer-deals.html" className="hover:text-yellow-400 transition-colors flex items-center gap-1">
            <ArrowUpRight size={16} className="text-yellow-400" /> Drummer Deals
          </a>
          <button className="flex items-center gap-2 hover:text-yellow-400 transition-colors">
            <Heart size={18} /> <span className="md:inline">Saved</span>
          </button>
        </div>
      </div>
    </div>
  </nav>
)

const Hero = ({ apiStatus, products }) => {
  const deal = useMemo(() => pickDailyProduct(products), [products])
  const [msLeft, setMsLeft] = useState(msUntilNextMidnight())

  useEffect(() => {
    const t = setInterval(() => setMsLeft(msUntilNextMidnight()), 1000)
    return () => clearInterval(t)
  }, [])

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
                <div className="font-mono text-2xl md:text-3xl font-extrabold text-yellow-200">{formatCountdown(msLeft)}</div>
                <div className="text-sm text-blue-100/90 mt-1">24-hour countdown</div>
              </div>

              <div className="mt-5 flex items-center gap-4">
                <div className="w-24 h-20 md:w-28 md:h-24 rounded-2xl overflow-hidden border border-white/10 bg-white/5">
                  <img
                    src={deal.imageUrl || getCategoryImage(deal.category)}
                    alt={deal.title}
                    className="w-full h-full object-cover"
                    loading="lazy"
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

  const linkFor = (label, queryText, campaign) => {
    const href = amazonSearchLink(queryText, campaign)
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
            {linkFor('Coupon deals', `${query} coupon`, 'deal_lens_coupon')}
            {linkFor('Clip coupons', `clip coupon ${query}`, 'deal_lens_clip')}
            {linkFor('Today\'s deals', `${query} deals today`, 'deal_lens_today')}
          </div>
        </div>
      </div>
    </div>
  )
}

const ProductCard = ({ product, tracking }) => {
  const [copied, setCopied] = useState(false)
  const Icon = getIcon(product.iconName)

  const handleCopyCode = (e) => {
    e.preventDefault()
    if (product.couponCode) {
      navigator.clipboard.writeText(product.couponCode)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const price = product?.price ? `$${Number(product.price).toFixed(2)}` : null

  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-blue-100 transition-all duration-300 flex flex-col h-full group relative overflow-hidden">
      <div className="absolute top-0 left-0 z-10 p-3">
        <span className="bg-slate-900/90 text-white text-[10px] font-bold px-2 py-1 rounded backdrop-blur-md">
          Amazon
        </span>
      </div>

      <div className="relative p-6 bg-gradient-to-b from-gray-50 to-white rounded-t-xl overflow-hidden h-56 flex items-center justify-center">
        {product.imageUrl ? (
          <img src={product.imageUrl} alt={product.title} className="max-h-40 object-contain" loading="lazy" />
        ) : (
          <div className="w-full h-full relative overflow-hidden rounded-xl">
            <img
              src={getCategoryImage(product.category)}
              alt={`${product.category} lifestyle`}
              className="w-full h-full object-cover"
              loading="lazy"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900/40 via-slate-900/10 to-transparent" />
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-white">
              <Icon size={64} strokeWidth={1.5} className="text-white/90 drop-shadow" />
              <div className="text-[11px] font-bold uppercase tracking-widest text-white/90 drop-shadow">
                {product.category}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="p-5 flex-grow flex flex-col">
        <div className="flex justify-between items-start mb-2">
          <div className="text-[10px] font-bold text-blue-600 uppercase tracking-widest bg-blue-50 px-2 py-0.5 rounded">
            {product.category}
          </div>
        </div>

        <h3 className="font-bold text-slate-800 mb-2 leading-tight hover:text-blue-600 transition-colors cursor-pointer text-lg line-clamp-2">
          {product.title}
        </h3>

        <div className="flex items-center mb-3">
          <div className="flex gap-0.5">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                size={12}
                className={`${i < Math.floor(product.rating || 0) ? 'text-yellow-400 fill-yellow-400' : 'text-gray-200'}`}
              />
            ))}
          </div>
          <span className="text-xs text-slate-400 ml-2 font-medium">({(product.reviews || 0).toLocaleString()})</span>
        </div>

        {product.description && <p className="text-sm text-slate-600 mb-4 line-clamp-2">{product.description}</p>}

        <div className="mt-auto">
          {price ? (
            <div className="flex items-end gap-2 mb-3">
              <span className="text-2xl font-extrabold text-slate-900">{price}</span>
              <span className="text-xs text-slate-500 ml-auto">Live via API</span>
            </div>
          ) : (
            <div className="text-xs text-slate-500 mb-3">Price loads from Amazon when available.</div>
          )}

          {product.type === 'coupon' ? (
            <div className="flex gap-2">
              <div className="relative flex-grow">
                <div className="border-2 border-dashed border-blue-200 bg-blue-50 rounded-lg text-center py-2.5 font-mono text-sm font-bold text-blue-800 select-all">
                  {product.couponCode}
                </div>
              </div>
              <button
                onClick={handleCopyCode}
                className={`px-4 rounded-lg font-bold transition-all flex items-center justify-center ${
                  copied ? 'bg-green-500 text-white' : 'bg-slate-900 text-white hover:bg-slate-800'
                }`}
              >
                {copied ? <CheckCircle size={18} /> : <Copy size={18} />}
              </button>
            </div>
          ) : (
            <a
              href={product.affiliateLink}
              target="_blank"
              rel="nofollow noopener noreferrer"
              onClick={() =>
                trackOutboundClick({
                  url: product.affiliateLink,
                  label: product.title,
                  category: product.category || 'outbound',
                  section: tracking?.section,
                  productId: product.id,
                  productTitle: product.title,
                  position: tracking?.position,
                  campaign: tracking?.campaign,
                })
              }
              className="block w-full bg-yellow-400 hover:bg-yellow-500 text-slate-900 text-center font-bold py-3 rounded-lg transition-colors flex items-center justify-center gap-2 shadow-sm hover:shadow-md"
            >
              Check price on Amazon <ExternalLink size={16} />
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

const CompactProductCard = ({ product, tracking }) => {
  const Icon = getIcon(product.iconName)
  return (
    <a
      href={product.affiliateLink}
      target="_blank"
      rel="nofollow noopener noreferrer"
      onClick={() =>
        trackOutboundClick({
          url: product.affiliateLink,
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
        {product.imageUrl ? (
          <img src={product.imageUrl} alt={product.title} className="max-h-16 object-contain" loading="lazy" />
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
      <div className="text-xs text-slate-500">Check price on Amazon</div>
    </a>
  )
}

const JumpBar = () => (
  <div className="bg-white/80 backdrop-blur border-b border-slate-200 sticky top-[60px] md:top-[74px] z-30">
    <div className="container mx-auto px-4 py-2 flex gap-2 overflow-x-auto hide-scrollbar">
      <a href="#categories" className="px-3 py-1.5 rounded-full text-sm font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 whitespace-nowrap">Categories</a>
      <a href="#budget" className="px-3 py-1.5 rounded-full text-sm font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 whitespace-nowrap">Budget</a>
      <a href="#top-picks" className="px-3 py-1.5 rounded-full text-sm font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 whitespace-nowrap">Top Picks</a>
      <a href="#trending" className="px-3 py-1.5 rounded-full text-sm font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 whitespace-nowrap">Trending</a>
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
  const byCat = new Map(cats.map((c) => [c, []]))
  for (const p of products) {
    if (byCat.has(p.category) && byCat.get(p.category).length < 10) {
      byCat.get(p.category).push(p)
    }
  }

  return (
    <div className="container mx-auto px-4 pt-10">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-extrabold text-slate-900">Top Picks</h2>
        
      </div>

      <div className="grid gap-6">
        {cats.map((cat) => (
          <div key={cat}>
            <div className="flex items-baseline justify-between mb-2">
              <div className="font-bold text-slate-800">{cat}</div>
              <div className="text-xs text-slate-500">Top {byCat.get(cat).length}</div>
            </div>
            <div className="flex gap-4 overflow-x-auto pb-2 hide-scrollbar">
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
          <li><a href="/electronics-deals.html" className="hover:text-yellow-400 transition-colors">Electronics</a></li>
          <li><a href="/kitchen-deals.html" className="hover:text-yellow-400 transition-colors">Kitchen</a></li>
          <li><a href="/home-deals.html" className="hover:text-yellow-400 transition-colors">Home</a></li>
          <li><a href="/fitness-deals.html" className="hover:text-yellow-400 transition-colors">Fitness</a></li>
          <li><a href="/kids-deals.html" className="hover:text-yellow-400 transition-colors">Kids</a></li>
          <li><a href="/pets-deals.html" className="hover:text-yellow-400 transition-colors">Pets</a></li>
          <li><a href="/tools-deals.html" className="hover:text-yellow-400 transition-colors">Tools</a></li>
          <li><a href="/beauty-deals.html" className="hover:text-yellow-400 transition-colors">Beauty</a></li>
        </ul>
      </div>
      <div>
        <h4 className="text-white font-bold mb-6 text-base">Links</h4>
        <ul className="space-y-3">
          <li><a href="/affiliate-disclosure.html" className="hover:text-yellow-400 transition-colors">Affiliate disclosure</a></li>
          <li><a href="/privacy.html" className="hover:text-yellow-400 transition-colors">Privacy</a></li>
          <li><a href="/drummer-deals.html" className="hover:text-yellow-400 transition-colors">Drummer Deals</a></li>
        </ul>
      </div>
      <div>
        <h4 className="text-white font-bold mb-6 text-base">Amazon Associate disclosure</h4>
        <p className="leading-relaxed mb-4 text-xs">
          As an Amazon Associate, we earn from qualifying purchases.
        </p>
        <p className="leading-relaxed mb-0 text-xs">
          This site may earn a commission when you buy through links (at no extra cost to you).{' '}
          <a className="underline hover:text-yellow-400" href="/affiliate-disclosure.html">Details</a>
        </p>
      </div>
    </div>

    <div className="container mx-auto px-4 mt-16 pt-8 border-t border-slate-900 flex flex-col md:flex-row justify-between items-center text-xs text-slate-500">
      <p>&copy; {new Date().getFullYear()} BestDealsOnline.us. All rights reserved.</p>
    </div>
  </footer>
)

async function fetchProductsJson() {
  const res = await fetch(PRODUCTS_JSON_URL, { headers: { Accept: 'application/json' } })
  if (!res.ok) throw new Error(`products.json fetch failed: ${res.status}`)
  return await res.json()
}

const App = () => {
  const [products, setProducts] = useState(SEED_PRODUCTS)
  const [apiStatus, setApiStatus] = useState('not configured')

  const [selectedCategory, setSelectedCategory] = useState('All')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortOption, setSortOption] = useState('recommended')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    ;(async () => {
      try {
        const data = await fetchProductsJson()
        if (data?.items?.length) {
          setProducts(data.items)
          setApiStatus('static catalog (300)')
        } else {
          setApiStatus('static catalog (empty)')
        }
      } catch (e) {
        setApiStatus('offline (using seed items)')
      }
    })()
  }, [])

  const processedProducts = useMemo(() => {
    let result = products.filter((product) => {
      const matchesCategory = selectedCategory === 'All' || product.category === selectedCategory
      const matchesSearch =
        (product.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (product.category || '').toLowerCase().includes(searchQuery.toLowerCase())
      return matchesCategory && matchesSearch
    })

    switch (sortOption) {
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

    return result
  }, [selectedCategory, searchQuery, sortOption, products])

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 font-sans text-slate-800">
      <DisclosureBanner />
      <Navbar onSearch={setSearchQuery} mobileMenuOpen={mobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen} />

      <main className="flex-grow">
        <Hero apiStatus={apiStatus} products={products} />

        <JumpBar />

        <div className="mt-10">
          <DealLens />
        </div>

        {selectedCategory === 'All' && !searchQuery && (
          <>
            <div id="categories" className="scroll-mt-32" />
            <CategoryTiles
              onPick={(cat) => {
                setSelectedCategory(cat)
                window.scrollTo({ top: 0, behavior: 'smooth' })
              }}
            />
            <div id="budget" />
            <UnderBudgetRow />
            <div id="top-picks" />
            <TopPicks products={products} />
          </>
        )}

        <div className="bg-white border-b border-slate-200 sticky top-[60px] md:top-[74px] z-30 shadow-sm">
          <div className="container mx-auto px-4 py-3 flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex gap-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0 hide-scrollbar">
              {CATEGORIES.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-all whitespace-nowrap border ${
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
          <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
            <div>
              <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                {selectedCategory === 'All' ? 'Trending Picks' : `${selectedCategory} Picks`}
              </h2>
              <p className="text-slate-500 text-sm mt-1">300-item feed across your chosen categories (via API).</p>
            </div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider bg-white px-3 py-1 rounded-full border border-slate-200 self-start md:self-auto">
              {processedProducts.length} items
            </span>
          </div>

          {processedProducts.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
              {processedProducts.map((product, i) => (
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
      </main>

      <Footer />
    </div>
  )
}

export default App
