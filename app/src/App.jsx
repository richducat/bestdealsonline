import React, { useEffect, useMemo, useState } from 'react'
import {
  ArrowUpRight,
  Baby,
  BookOpen,
  CalendarClock,
  ExternalLink,
  FileText,
  Gift,
  GitCompare,
  HelpCircle,
  Home,
  Menu,
  Newspaper,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Tag,
  Wallet,
  X,
} from 'lucide-react'
import { dealTruthScore } from './dealtruth.js'

const CATEGORIES = [
  {
    name: 'Electronics',
    href: '/electronics-deals.html',
    image: '/images/categories/electronics.webp',
    description: 'Chargers, audio, monitors, routers, and everyday electronics.',
  },
  {
    name: 'Home',
    href: '/home-deals.html',
    image: '/images/categories/home.webp',
    description: 'Comfort, organization, cleaning, and apartment upgrades.',
  },
  {
    name: 'Kitchen',
    href: '/kitchen-deals.html',
    image: '/images/categories/kitchen.webp',
    description: 'Coffee gear, cookware, prep tools, and weeknight essentials.',
  },
  {
    name: 'Tools',
    href: '/tools-deals.html',
    image: '/images/categories/tools.webp',
    description: 'DIY kits, drills, measuring tools, and workshop staples.',
  },
  {
    name: 'Kids',
    href: '/kids-deals.html',
    image: '/images/categories/kids.webp',
    description: 'School gear, toys, headphones, and parent-friendly picks.',
  },
  {
    name: 'Beauty',
    href: '/beauty-deals.html',
    image: '/images/categories/beauty.webp',
    description: 'Skincare, grooming, hair tools, and routine products.',
  },
  {
    name: 'Fitness',
    href: '/fitness-deals.html',
    image: '/images/categories/fitness.webp',
    description: 'Home gym basics, recovery gear, and compact equipment.',
  },
  {
    name: 'Pets',
    href: '/pets-deals.html',
    image: '/images/categories/pets.webp',
    description: 'Bowls, litter gear, travel accessories, and pet comfort.',
  },
]

// One representative, broadly-appealing research post per category with
// enough real-data coverage to pair meaningfully. Categories without a
// real post (Tools, Beauty, Fitness, Pets) are intentionally left out
// rather than force-matched to an unrelated post.
const RESEARCH_PAIRINGS = [
  {
    category: 'Electronics',
    title: 'USB-C chargers: what buyers like and complain about',
    href: '/blog/usb-c-chargers-what-buyers-like-what-they-complain-about-and-what-to-look-for.html',
    takeaway: 'The tradeoffs shoppers mention most: heat, wattage, cables, and port sharing.',
  },
  {
    category: 'Home',
    title: 'Robot vacuums: navigation, pet hair, and maintenance',
    href: '/blog/robot-vacuums-what-reviewers-actually-mention-navigation-pet-hair-maintenance.html',
    takeaway: 'What people consistently praise, what breaks trust, and when it actually saves time.',
  },
  {
    category: 'Kitchen',
    title: 'Coffee makers under $100: taste, reliability, ease',
    href: '/blog/coffee-makers-under-100-what-reviewers-care-about-taste-reliability-ease.html',
    takeaway: 'The issues buyers notice after the first week of daily use.',
  },
  {
    category: 'Kids',
    title: 'Kids headphones: comfort, volume limits, durability',
    href: '/blog/kids-headphones-what-parents-and-buyers-mention-most-comfort-volume-limits-durability.html',
    takeaway: 'The recurring parent concerns that matter more than marketing graphics.',
  },
]

const MORE_RESEARCH = [
  {
    title: 'Air fryer accessories: liners, racks, and cleanup fit',
    href: '/blog/air-fryer-accessories-what-buyers-like-liners-racks-cleanup-fit.html',
    category: 'Kitchen',
  },
  {
    title: 'Air fryers: capacity, cleanup, and noise tradeoffs',
    href: '/blog/air-fryers-the-most-common-pros-and-cons-buyers-mention-capacity-cleanup-noise.html',
    category: 'Kitchen',
  },
  {
    title: 'Air purifiers under $100: noise, filters, room size',
    href: '/blog/air-purifiers-under-100-what-reviewers-say-about-noise-filters-and-room-size.html',
    category: 'Home',
  },
  {
    title: 'Blackout curtains: light blocking, sizing, fabric',
    href: '/blog/blackout-curtains-what-reviewers-say-about-light-blocking-sizing-and-fabric.html',
    category: 'Home',
  },
  {
    title: 'Cast iron skillets: weight, seasoning, heat retention',
    href: '/blog/cast-iron-skillets-what-reviewers-say-about-weight-seasoning-and-heat-retention.html',
    category: 'Kitchen',
  },
  {
    title: 'Dash cams: video clarity, night vision, heat, app quality',
    href: '/blog/dash-cams-what-buyers-mention-most-video-clarity-night-vision-heat-app.html',
    category: 'Electronics',
  },
  {
    title: 'Digital meat thermometers: speed, accuracy, durability',
    href: '/blog/digital-meat-thermometers-what-reviewers-mention-most-speed-accuracy-durability.html',
    category: 'Kitchen',
  },
  {
    title: 'GaN chargers: what buyers like, what bugs them',
    href: '/blog/gan-chargers-what-buyers-like-what-bugs-them-and-how-to-choose.html',
    category: 'Electronics',
  },
  {
    title: 'Humidifiers under $50: upsides and maintenance warnings',
    href: '/blog/humidifiers-under-50-what-reviewers-like-and-what-they-warn-about.html',
    category: 'Home',
  },
  {
    title: 'Kids lunch boxes and bento sets: leaks, size, insulation',
    href: '/blog/kids-lunch-boxes-and-bento-sets-what-reviewers-mention-most-leaks-size-insulation.html',
    category: 'Kids',
  },
  {
    title: 'Kids smartwatches: safety, battery, parental controls',
    href: '/blog/kids-smartwatches-what-parents-care-about-safety-battery-controls.html',
    category: 'Kids',
  },
  {
    title: 'Kids tablets: durability, storage, parental controls',
    href: '/blog/kids-tablets-what-parents-mention-most-durability-storage-parental-controls.html',
    category: 'Kids',
  },
  {
    title: 'Learning toys and science kits: good vs. gimmicky',
    href: '/blog/learning-toys-and-science-kits-how-reviewers-separate-the-good-from-the-gimmicky.html',
    category: 'Kids',
  },
  {
    title: 'Portable SSDs vs. external hard drives: speed, size, value',
    href: '/blog/portable-ssds-vs-external-hard-drives-what-buyers-say-about-speed-size-and-value.html',
    category: 'Electronics',
  },
  {
    title: 'Power banks: capacity, speed, size, real-world use',
    href: '/blog/power-banks-pros-cons-from-buyer-reviews-capacity-speed-size-and-real-world-use.html',
    category: 'Electronics',
  },
  {
    title: 'Toddler toys: durability, mess, and age fit',
    href: '/blog/toddler-toys-what-parents-mention-most-durability-mess-age-fit.html',
    category: 'Kids',
  },
  {
    title: 'Wireless chargers: speed, heat, and reliability',
    href: '/blog/wireless-chargers-what-reviewers-say-about-speed-heat-and-reliability.html',
    category: 'Electronics',
  },
]

const TRUST_LINKS = [
  { title: 'Affiliate disclosure', href: '/affiliate-disclosure.html', icon: ShieldCheck },
  { title: 'How we pick deals', href: '/online-deals-methodology.html', icon: FileText },
  { title: 'Review policy', href: '/review-aggregation-guidelines.html', icon: BookOpen },
]

// Lets a product card link straight to the real research backing the
// hero's "we read the reviews" claim for that category, instead of the
// claim only living in a separate section disconnected from the picks.
// Categories with no real post (Tools, Beauty, Fitness, Pets) get no
// link rather than a fabricated one.
const CATEGORY_RESEARCH = Object.fromEntries(RESEARCH_PAIRINGS.map((p) => [p.category, p]))

// Lets any section reuse the category lifestyle photography by name.
const CATEGORY_IMAGES = Object.fromEntries(CATEGORIES.map((c) => [c.name, c.image]))

// Ten genuinely distinct ways people actually use this site, each
// pointing at a real page that already exists -- no invented features.
const USE_CASES = [
  {
    icon: Search,
    title: 'You already know what you want',
    body: 'Jump straight to a category hub and browse every price tier for that exact product, from budget to premium.',
    href: '/electronics-deals.html',
    linkLabel: 'Browse a category hub',
  },
  {
    icon: HelpCircle,
    title: "You're not sure if a price is actually good",
    body: 'That’s the whole reason DealTruth exists — see how we score a real discount against 90 days of price history below.',
    href: '#demo',
    linkLabel: 'Try the scoring demo',
  },
  {
    icon: Gift,
    title: "You're buying a gift and can't afford a dud",
    body: 'Read what actual owners complain about before you buy something you’ll never use again.',
    href: '/blog/index.html',
    linkLabel: 'Read buyer research',
  },
  {
    icon: Home,
    title: "You're furnishing a new place",
    body: 'Home and Kitchen hubs cover everything from a $15 doormat to a $150 espresso machine, organized by budget.',
    href: '/home-deals.html',
    linkLabel: 'Browse the Home hub',
  },
  {
    icon: Baby,
    title: "You're restocking kid gear",
    body: 'Headphones, tablets, smartwatches, lunch boxes — real parent feedback on the stuff that actually survives daily use.',
    href: '/kids-deals.html',
    linkLabel: 'Browse the Kids hub',
  },
  {
    icon: Wallet,
    title: "You're shopping on a hard budget cap",
    body: 'Every category is split by exact price ceiling — under $15, $25, $50, $100 — so you never see something out of range.',
    href: '/best-deals-with-price-history.html',
    linkLabel: 'See price-capped picks',
  },
  {
    icon: GitCompare,
    title: "You're deciding between two similar products",
    body: 'Our research posts break down the actual tradeoffs — like portable SSDs vs. external hard drives — not just specs.',
    href: '/blog/portable-ssds-vs-external-hard-drives-what-buyers-say-about-speed-size-and-value.html',
    linkLabel: 'Read a comparison',
  },
  {
    icon: CalendarClock,
    title: "You're timing a purchase around a sale",
    body: 'Black Friday, Cyber Monday, and Christmas guides tell you when discounts are historically real vs. relabeled.',
    href: '/best-deals-online-today.html',
    linkLabel: "See today's timing picks",
  },
  {
    icon: SlidersHorizontal,
    title: 'You want to sanity-check a deal before you click',
    body: 'Real discount percent, rarity over 180 days, and a buy-now-or-wait call — not a five-star badge.',
    href: '#demo',
    linkLabel: 'See how scoring works',
  },
  {
    icon: Newspaper,
    title: "You'd rather come back than buy on impulse",
    body: 'The research blog is evergreen — come back anytime for the next category before you make a decision.',
    href: '/blog/index.html',
    linkLabel: 'Browse all research',
  },
]

// Fixes common tech acronyms that data-generation left in Title Case
// ("Usb C Charger" -> "USB-C Charger"). Display-only; never touches
// the underlying data file.
const ACRONYM_FIXES = {
  usb: 'USB',
  tv: 'TV',
  ssd: 'SSD',
  sd: 'SD',
  gan: 'GaN',
  iphone: 'iPhone',
  led: 'LED',
  wifi: 'WiFi',
  '4k': '4K',
}

function cleanTitle(title) {
  return title
    .split(' ')
    .map((word) => ACRONYM_FIXES[word.toLowerCase()] ?? word)
    .join(' ')
    .replace(/\bUSB C\b/g, 'USB-C')
}

// Spreads picks across categories (round-robin) so the featured grid
// reads as curated rather than dumped in whatever order the feed returns.
function pickFeatured(items, count) {
  const seenTitles = new Set()
  const byCategory = new Map()
  for (const item of items) {
    if (seenTitles.has(item.title)) continue
    // Once real DealTruth data is connected, skip items that aren't
    // actually a meaningful discount rather than featuring them anyway.
    if (item.dealTruth?.notMeaningfulDeal) continue
    seenTitles.add(item.title)
    const bucket = byCategory.get(item.category) ?? []
    bucket.push(item)
    byCategory.set(item.category, bucket)
  }
  // With DealTruth scores available, feature the best deal in each
  // category first instead of whatever order the feed happened to return.
  for (const bucket of byCategory.values()) {
    if (bucket.some((item) => item.dealTruth)) {
      bucket.sort((a, b) => (b.dealTruth?.score ?? 0) - (a.dealTruth?.score ?? 0))
    }
  }
  const buckets = [...byCategory.values()]
  const picked = []
  let i = 0
  while (picked.length < count && buckets.some((b) => b.length > 0)) {
    const bucket = buckets[i % buckets.length]
    if (bucket.length > 0) picked.push(bucket.shift())
    i += 1
  }
  return picked
}

// Deterministic seeded PRNG so the demo's "example" history is stable
// across re-renders instead of jittering on every slider move.
function seededRandom(seed) {
  let s = seed % 2147483647
  if (s <= 0) s += 2147483646
  return () => {
    s = (s * 16807) % 2147483647
    return (s - 1) / 2147483646
  }
}

// Builds a plausible 120-day price history ending at todayPrice, mostly
// hovering near typicalPrice with small daily noise -- fed into the real
// dealTruthScore() algorithm so the interactive demo runs genuine scoring
// logic on a clearly-labeled example, never claiming to be a real product.
function buildExampleHistory(typicalPrice, todayPrice) {
  const rand = seededRandom(Math.round(typicalPrice * 97 + todayPrice * 13) || 1)
  const days = 120
  const history = []
  const now = Date.now()
  const DAY_MS = 24 * 60 * 60 * 1000
  for (let i = days; i >= 1; i -= 1) {
    const noise = (rand() - 0.5) * 0.05
    const price = Math.max(1, Math.round(typicalPrice * (1 + noise) * 100) / 100)
    history.push({ price, timestamp: now - i * DAY_MS })
  }
  history.push({ price: Math.max(1, Math.round(todayPrice * 100) / 100), timestamp: now })
  return history
}

function runExampleScore(typicalPrice, todayPrice) {
  const priceHistory = buildExampleHistory(typicalPrice, todayPrice)
  return dealTruthScore({
    title: 'Example product',
    rating: 4.3,
    reviews: 2400,
    priceHistory,
    offer: {
      itemPrice: todayPrice,
      isPrime: true,
      soldByAmazon: true,
      shipsFromAmazon: true,
    },
  })
}

// Set VITE_DEALS_API_BASE (e.g. https://bestdealsonline-worker.<account>.workers.dev)
// to switch from the static product list to live DealTruth-scored deals.
// Unset by default -- the site works exactly as it does today until this
// points at a deployed worker with a real price feed behind it.
const DEALS_API_BASE = import.meta.env.VITE_DEALS_API_BASE

function mapDealTruthItem(item) {
  return {
    id: item.id ?? item.asin,
    title: item.title,
    category: item.category,
    imageUrl: item.imageUrl,
    affiliateLink: item.affiliateLink,
    dealTruth: item.dealTruth ?? null,
  }
}

function useProducts() {
  const [state, setState] = useState({ items: [], loading: true, error: false })

  useEffect(() => {
    let cancelled = false

    const source = DEALS_API_BASE
      ? fetch(`${DEALS_API_BASE.replace(/\/$/, '')}/v1/deals?limit=300`)
          .then((res) => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            return res.json()
          })
          .then((data) => (data.items ?? []).map(mapDealTruthItem))
      : fetch('/data/products.json')
          .then((res) => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            return res.json()
          })
          .then((data) => (data.items ?? []).map((item) => ({ ...item, dealTruth: null })))

    source
      .then((items) => {
        if (!cancelled) setState({ items, loading: false, error: false })
      })
      .catch(() => {
        if (!cancelled) setState({ items: [], loading: false, error: true })
      })

    return () => {
      cancelled = true
    }
  }, [])

  return state
}

const DisclosureBanner = () => {
  const [visible, setVisible] = useState(true)
  if (!visible) return null

  return (
    <div className="bg-sand border-b border-linen text-xs text-cocoa">
      <div className="container mx-auto px-4 py-2 flex items-start justify-between gap-3">
        <p className="leading-relaxed">
          <strong>Affiliate disclosure:</strong> As an Amazon Associate, we earn from qualifying purchases.{' '}
          <a className="underline" href="/affiliate-disclosure.html">Details</a>.
        </p>
        <button
          type="button"
          onClick={() => setVisible(false)}
          className="inline-flex items-center justify-center h-8 w-8 rounded-md text-cocoa hover:bg-linen hover:text-ink shrink-0"
          aria-label="Dismiss disclosure"
        >
          <X size={14} />
        </button>
      </div>
    </div>
  )
}

const Navbar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <nav className="bg-cream/95 backdrop-blur text-ink sticky top-0 z-40 border-b border-linen">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between gap-4">
        <a href="/" className="flex items-center gap-3">
          <span className="bg-clay text-cream p-2 rounded-full">
            <Tag size={18} />
          </span>
          <span className="leading-tight">
            <span className="block font-display font-semibold tracking-tight text-xl">BestDealsOnline</span>
            <span className="block text-[10px] text-clay uppercase tracking-[0.28em]">Researched Amazon Picks</span>
          </span>
        </a>

        <button
          type="button"
          className="md:hidden inline-flex items-center justify-center h-11 w-11 rounded-full border border-linen text-cocoa"
          onClick={() => setMobileMenuOpen((open) => !open)}
          aria-label="Toggle navigation"
        >
          {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
        </button>

        <div className="hidden md:flex items-center gap-6 text-sm font-semibold text-cocoa">
          <a href="#deals" className="hover:text-clay transition-colors">Today's Picks</a>
          <a href="#demo" className="hover:text-clay transition-colors">How It Works</a>
          <a href="#categories" className="hover:text-clay transition-colors">Categories</a>
          <a href="#research" className="hover:text-clay transition-colors">Research</a>
          <a href="/blog/index.html" className="hover:text-clay transition-colors">Blog</a>
        </div>
      </div>

      {mobileMenuOpen ? (
        <div className="md:hidden px-4 pb-4 flex flex-col gap-1 text-sm font-semibold text-cocoa">
          <a href="#deals" className="min-h-11 flex items-center hover:text-clay">Today's Picks</a>
          <a href="#demo" className="min-h-11 flex items-center hover:text-clay">How It Works</a>
          <a href="#categories" className="min-h-11 flex items-center hover:text-clay">Categories</a>
          <a href="#research" className="min-h-11 flex items-center hover:text-clay">Research</a>
          <a href="/blog/index.html" className="min-h-11 flex items-center hover:text-clay">Blog</a>
        </div>
      ) : null}
    </nav>
  )
}

const CategoryChips = ({ counts }) => (
  <div className="mt-7 -mx-4 px-4 md:mx-0 md:px-0 flex gap-2 overflow-x-auto pb-2 md:flex-wrap md:overflow-visible">
    {CATEGORIES.map((cat) => (
      <a
        key={cat.href}
        href={cat.href}
        className="shrink-0 inline-flex items-center gap-1.5 px-4 py-2.5 min-h-11 rounded-full border border-linen bg-white/70 hover:bg-white hover:border-blush text-sm font-semibold text-cocoa hover:text-clay transition-colors whitespace-nowrap"
      >
        {cat.name}
        {counts[cat.name] ? <span className="text-clay">· {counts[cat.name]}</span> : null}
      </a>
    ))}
  </div>
)

// Hand-drawn underline flourish for the hero headline.
const Squiggle = () => (
  <svg
    aria-hidden="true"
    viewBox="0 0 220 14"
    className="mt-2 h-3 w-44 md:w-56 text-clay"
    fill="none"
  >
    <path
      d="M3 10C36 3 62 3 92 8c30 5 58 4 86-3 14-3.5 27-3 39 1"
      stroke="currentColor"
      strokeWidth="4"
      strokeLinecap="round"
    />
  </svg>
)

// Small four-point sparkle used as a decorative accent.
const SparkleMark = ({ className }) => (
  <svg aria-hidden="true" viewBox="0 0 24 24" className={className} fill="currentColor">
    <path d="M12 0c1.2 6.2 4.6 9.7 12 12-7.4 2.3-10.8 5.8-12 12-1.2-6.2-4.6-9.7-12-12 7.4-2.3 10.8-5.8 12-12Z" />
  </svg>
)

const Hero = ({ counts }) => (
  <section className="relative overflow-hidden bg-cream text-ink">
    {/* Soft blush wash behind the photo side. */}
    <div aria-hidden="true" className="pointer-events-none absolute -right-32 -top-40 h-[34rem] w-[34rem] rounded-full bg-blush/60 blur-3xl" />
    <div aria-hidden="true" className="pointer-events-none absolute -left-40 bottom-0 h-72 w-72 rounded-full bg-sand blur-3xl" />

    <div className="container mx-auto px-4 pt-10 pb-14 md:pt-16 md:pb-20 relative">
      <div className="grid lg:grid-cols-[1.05fr_0.95fr] gap-12 lg:gap-16 items-center">
        <div className="min-w-0">
          <div className="inline-flex items-center gap-2 rounded-full border border-blush bg-white/70 px-4 py-1.5 text-xs font-bold uppercase tracking-[0.2em] text-clay">
            <SparkleMark className="h-3 w-3" /> Researched deals, real life
          </div>
          <h1 className="mt-5 font-display text-[2.6rem] md:text-6xl font-semibold tracking-tight leading-[1.05]">
            We read the reviews
            <span className="block italic text-clay">so you don&rsquo;t have to.</span>
          </h1>
          <Squiggle />
          <p className="mt-5 max-w-xl text-lg text-cocoa leading-relaxed">
            300+ Amazon picks across Home, Kitchen, Beauty, Kids and more. We dig through what real buyers say breaks,
            holds up, and disappoints after week one — not just the star average.
          </p>
          <p className="mt-3 text-xs text-cocoa/70">
            As an Amazon Associate, we earn from qualifying purchases.
          </p>

          <div className="mt-7 flex flex-wrap items-center gap-5">
            <a
              href="#deals"
              className="inline-flex items-center justify-center min-h-12 px-7 rounded-full bg-clay text-cream font-bold hover:bg-claydark transition-colors text-base shadow-sm"
            >
              See Today's Picks <ArrowUpRight size={16} className="ml-2" />
            </a>
            <a
              href="/online-deals-methodology.html"
              className="inline-flex items-center min-h-12 text-sm font-bold text-cocoa underline decoration-blush decoration-2 underline-offset-4 hover:text-clay transition-colors"
            >
              How we pick <ArrowUpRight size={14} className="ml-1.5" />
            </a>
          </div>

          <CategoryChips counts={counts} />
        </div>

        {/* Editorial photo composition: arched hero image + overlapping accent. */}
        <div className="relative mx-auto w-full max-w-md lg:max-w-none">
          <SparkleMark className="absolute -top-6 right-8 h-6 w-6 text-clay/70" />
          <SparkleMark className="absolute top-10 -right-2 h-3.5 w-3.5 text-sage" />
          <div className="overflow-hidden rounded-t-[9rem] rounded-b-[2rem] border-8 border-white shadow-xl">
            <img
              src="/images/categories/home.webp"
              alt="A calm, sunlit living room with a cozy sofa and warm neutral decor"
              className="h-[24rem] md:h-[30rem] w-full object-cover"
              loading="eager"
              fetchPriority="high"
            />
          </div>
          <div className="absolute -bottom-8 -left-4 md:-left-10 w-36 md:w-48 overflow-hidden rounded-[1.75rem] border-8 border-white shadow-lg rotate-[-4deg]">
            <img
              src="/images/hero/default.jpg"
              alt="A woman smiles while shopping on her laptop from her couch"
              className="aspect-square w-full object-cover"
              loading="eager"
            />
          </div>
          <div className="absolute top-8 -left-3 md:-left-8 rounded-2xl bg-white/95 shadow-lg border border-linen px-4 py-3 rotate-[2deg]">
            <div className="text-[10px] font-bold uppercase tracking-[0.18em] text-clay">DealTruth check</div>
            <div className="mt-0.5 text-sm font-bold text-ink">Price history, not hype</div>
          </div>
        </div>
      </div>
    </div>
  </section>
)

const ProductCard = ({ item }) => {
  const research = CATEGORY_RESEARCH[item.category]

  return (
    <div className="rounded-3xl border border-linen bg-white shadow-sm overflow-hidden transition-all hover:-translate-y-0.5 hover:shadow-lg flex flex-col">
      <a
        href={item.affiliateLink}
        target="_blank"
        rel="nofollow noopener noreferrer"
        className="group flex flex-col flex-1"
      >
        <div className="aspect-square overflow-hidden bg-sand/60">
          <img
            src={item.imageUrl}
            alt={cleanTitle(item.title)}
            className="h-full w-full object-contain p-4 transition-transform duration-300 group-hover:scale-105"
            loading="lazy"
          />
        </div>
        <div className="p-4 flex flex-col flex-1">
          <div className="text-[11px] font-bold uppercase tracking-[0.14em] text-clay">{item.category}</div>
          <h3 className="mt-1.5 font-bold text-ink leading-snug">{cleanTitle(item.title)}</h3>
          {item.dealTruth && !item.dealTruth.notMeaningfulDeal ? (
            <div className="mt-2">
              <div className="inline-flex items-center gap-1 text-xs font-extrabold text-sagedark bg-sage/15 px-2 py-0.5 rounded-full">
                DealTruth {item.dealTruth.score}/100
              </div>
              <div className="mt-1 text-xs text-cocoa leading-snug">{item.dealTruth.explanations.discountLine}</div>
            </div>
          ) : null}
          <div className="mt-auto pt-3 inline-flex items-center justify-center min-h-11 rounded-full bg-ink text-cream text-sm font-bold group-hover:bg-clay transition-colors">
            View on Amazon <ExternalLink size={13} className="ml-1.5" />
          </div>
        </div>
      </a>
      {research ? (
        <a href={research.href} className="block px-4 py-2.5 border-t border-linen text-xs font-bold text-clay hover:bg-cream min-h-11 flex items-center">
          See what buyers say about {item.category.toLowerCase()} &rarr;
        </a>
      ) : null}
    </div>
  )
}

const ProductCardSkeleton = () => (
  <div className="rounded-3xl border border-linen bg-white overflow-hidden animate-pulse">
    <div className="aspect-square bg-sand" />
    <div className="p-4 space-y-2">
      <div className="h-2.5 w-16 bg-linen rounded" />
      <div className="h-4 w-3/4 bg-linen rounded" />
      <div className="h-9 w-full bg-sand rounded-full mt-3" />
    </div>
  </div>
)

const SectionHeader = ({ eyebrow, title, body }) => (
  <div className="max-w-3xl">
    <div className="text-xs font-bold uppercase tracking-[0.22em] text-clay">{eyebrow}</div>
    <h2 className="mt-3 font-display text-3xl md:text-[2.6rem] font-semibold tracking-tight leading-tight text-ink">{title}</h2>
    {body ? <p className="mt-3 text-cocoa text-lg leading-relaxed">{body}</p> : null}
  </div>
)

const FeaturedDeals = ({ items, loading, error }) => (
  <section id="deals" className="container mx-auto px-4 py-12 md:py-16">
    <SectionHeader
      eyebrow="Today's Picks"
      title="Start here."
      body="A mix from every category. Click through to see current pricing and availability on Amazon."
    />
    {error ? (
      <p className="mt-8 text-cocoa">
        Couldn't load today's picks right now — browse by{' '}
        <a className="underline font-bold" href="#categories">category</a> instead.
      </p>
    ) : (
      <div className="mt-8 grid gap-4 grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
        {loading
          ? Array.from({ length: 8 }).map((_, i) => <ProductCardSkeleton key={i} />)
          : items.map((item) => <ProductCard key={item.id} item={item} />)}
      </div>
    )}
  </section>
)

const CategoryTile = ({ cat, count }) => (
  <a
    href={cat.href}
    className="group overflow-hidden rounded-3xl border border-linen bg-white shadow-sm transition-all hover:-translate-y-1 hover:shadow-xl flex flex-col"
  >
    <div className="aspect-[4/3] overflow-hidden">
      <img
        src={cat.image}
        alt={`${cat.name} — ${cat.description}`}
        className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        loading="lazy"
      />
    </div>
    <div className="p-5 flex flex-col flex-1">
      <h3 className="font-display text-xl font-semibold text-ink flex items-center justify-between">
        {cat.name}
        <ArrowUpRight size={18} className="shrink-0 text-cocoa/50 transition-colors group-hover:text-clay" />
      </h3>
      <p className="mt-1.5 text-sm text-cocoa leading-snug">{cat.description}</p>
      {count ? <div className="mt-2 text-xs font-bold uppercase tracking-[0.14em] text-clay">{count} picks</div> : null}
    </div>
  </a>
)

const CategoryGrid = ({ counts }) => (
  <section id="categories" className="border-y border-linen bg-white">
    <div className="container mx-auto px-4 py-12 md:py-16">
      <SectionHeader
        eyebrow="Shop by Category"
        title="Go straight to what you need."
        body="Every room, routine, and person on your list — organized by budget once you're inside."
      />
      <div className="mt-8 grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        {CATEGORIES.map((cat) => (
          <CategoryTile key={cat.href} cat={cat} count={counts[cat.name]} />
        ))}
      </div>
    </div>
  </section>
)

const DEMO_PRESETS = [
  { label: 'Everyday price', typical: 40, today: 39 },
  { label: 'Solid deal', typical: 60, today: 42 },
  { label: 'Rare deep drop', typical: 80, today: 34 },
]

const DealTruthDemo = () => {
  const [typical, setTypical] = useState(60)
  const [today, setToday] = useState(42)

  const result = useMemo(() => runExampleScore(typical, today), [typical, today])
  const scoreColor = result.notMeaningfulDeal
    ? 'text-cocoa bg-linen'
    : result.score >= 70
      ? 'text-sagedark bg-sage/15'
      : result.score >= 45
        ? 'text-amber-700 bg-amber-50'
        : 'text-cocoa bg-linen'

  return (
    <section id="demo" className="border-y border-linen bg-sand">
      <div className="container mx-auto px-4 py-12 md:py-16">
        <SectionHeader
          eyebrow="How It Works"
          title="This is the real scoring algorithm. Try it."
          body="Drag the sliders below and watch the actual DealTruth engine compute a score, live, in your browser — the same code that scores every real pick on this site. The two numbers below are an example you control, not a real product."
        />

        <div className="mt-8 grid lg:grid-cols-2 gap-8 items-start">
          <div className="rounded-3xl border border-linen bg-white p-6">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-cocoa">
              <SlidersHorizontal size={14} /> Example price history — not a real product
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              {DEMO_PRESETS.map((preset) => (
                <button
                  key={preset.label}
                  type="button"
                  onClick={() => {
                    setTypical(preset.typical)
                    setToday(preset.today)
                  }}
                  className="px-3 py-2 min-h-11 rounded-full border border-linen bg-cream text-xs font-bold text-cocoa hover:border-clay hover:text-clay transition-colors"
                >
                  {preset.label}
                </button>
              ))}
            </div>

            <label className="block mt-6">
              <span className="text-sm font-bold text-ink">Typical price (last 90 days): ${typical}</span>
              <input
                type="range"
                min="10"
                max="200"
                value={typical}
                onChange={(e) => setTypical(Number(e.target.value))}
                className="w-full mt-2 accent-clay"
              />
            </label>

            <label className="block mt-5">
              <span className="text-sm font-bold text-ink">Today's price: ${today}</span>
              <input
                type="range"
                min="5"
                max="200"
                value={today}
                onChange={(e) => setToday(Number(e.target.value))}
                className="w-full mt-2 accent-clay"
              />
            </label>
          </div>

          <div className="rounded-3xl border border-linen bg-white p-6">
            <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-extrabold ${scoreColor}`}>
              <Sparkles size={15} /> DealTruth {result.score}/100
            </div>
            {result.notMeaningfulDeal ? (
              <p className="mt-4 text-sm font-bold text-cocoa">Not a meaningful deal at these numbers.</p>
            ) : null}
            <ul className="mt-4 space-y-3 text-sm text-cocoa">
              <li>{result.explanations.discountLine}</li>
              <li>{result.explanations.rarityLine}</li>
              <li>{result.explanations.confidenceLine}</li>
              <li className="font-bold text-ink">{result.explanations.decisionLine}</li>
            </ul>
            <p className="mt-6 text-xs text-cocoa/80 leading-relaxed">
              This is the same real-discount-vs-median, rarity-over-time, and buy-or-wait logic behind every scored pick on
              this site — see <a href="/online-deals-methodology.html" className="underline font-bold">our full methodology</a>.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}

const UseCaseCard = ({ useCase }) => {
  const Icon = useCase.icon
  return (
    <a
      href={useCase.href}
      className="rounded-3xl border border-linen bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md flex flex-col"
    >
      <div className="inline-flex h-11 w-11 items-center justify-center rounded-full bg-blush text-clay shrink-0">
        <Icon size={18} />
      </div>
      <h3 className="mt-4 font-bold text-ink leading-snug">{useCase.title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-cocoa flex-1">{useCase.body}</p>
      <div className="mt-4 inline-flex items-center text-sm font-bold text-clay">
        {useCase.linkLabel} <ArrowUpRight size={15} className="ml-1.5" />
      </div>
    </a>
  )
}

const UseCasesSection = () => (
  <section className="container mx-auto px-4 py-12 md:py-16">
    <SectionHeader
      eyebrow="Built For How You Actually Shop"
      title="Ten ways people use this site."
      body="Not everyone lands here for the same reason. Find yours."
    />
    <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {USE_CASES.map((useCase) => (
        <UseCaseCard key={useCase.title} useCase={useCase} />
      ))}
    </div>
  </section>
)

const ResearchPairingCard = ({ pairing }) => (
  <a
    href={pairing.href}
    className="group overflow-hidden rounded-3xl border border-linen bg-white shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-lg flex flex-col"
  >
    {CATEGORY_IMAGES[pairing.category] ? (
      <div className="aspect-[16/10] overflow-hidden">
        <img
          src={CATEGORY_IMAGES[pairing.category]}
          alt=""
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          loading="lazy"
        />
      </div>
    ) : null}
    <div className="p-5 flex flex-col flex-1">
      <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-clay">{pairing.category}</div>
      <h3 className="mt-2 text-lg font-bold text-ink leading-snug">{pairing.title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-cocoa flex-1">{pairing.takeaway}</p>
      <div className="mt-4 inline-flex items-center text-sm font-bold text-clay">
        Read the research <ArrowUpRight size={15} className="ml-1.5" />
      </div>
    </div>
  </a>
)

const ResearchSection = () => (
  <section id="research" className="container mx-auto px-4 py-12 md:py-16">
    <SectionHeader
      eyebrow="Backed by the Research"
      title="Real feedback. Not a star rating."
      body="Before you click through to Amazon, here's what actual reviewers say holds up — and what breaks after week one."
    />
    <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {RESEARCH_PAIRINGS.map((pairing) => (
        <ResearchPairingCard key={pairing.href} pairing={pairing} />
      ))}
    </div>

    <div className="mt-10">
      <div className="text-sm font-bold text-clay uppercase tracking-[0.18em]">More research</div>
      <div className="mt-4 grid gap-x-8 gap-y-3 md:grid-cols-2">
        {MORE_RESEARCH.map((post) => (
          <a
            key={post.href}
            href={post.href}
            className="flex items-baseline gap-3 py-1 text-sm text-cocoa hover:text-clay min-h-11"
          >
            <span className="text-cocoa/50 font-bold shrink-0">{post.category}</span>
            <span className="underline decoration-blush underline-offset-2">{post.title}</span>
          </a>
        ))}
      </div>
    </div>
  </section>
)

const TrustSection = () => (
  <section className="border-t border-linen bg-white">
    <div className="container mx-auto px-4 py-12 md:py-16">
      <div className="rounded-[2rem] border border-blush bg-blush/40 p-6 md:p-10 relative overflow-hidden">
        <SparkleMark className="absolute top-6 right-8 h-5 w-5 text-clay/50" />
        <div className="flex items-start gap-3">
          <ShieldCheck size={20} className="mt-1.5 text-clay shrink-0" />
          <div>
            <h3 className="font-display text-2xl font-semibold text-ink">Why trust this site</h3>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-cocoa">
              We publish the research before the affiliate link, not after — and we don't invent star ratings, review
              counts, or countdown timers to push a click. Check our methodology and policies yourself; they're always public.
            </p>
            <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm font-bold">
              {TRUST_LINKS.map((link) => {
                const Icon = link.icon
                return (
                  <a key={link.href} href={link.href} className="inline-flex items-center gap-1.5 min-h-11 text-cocoa hover:text-clay">
                    <Icon size={14} /> {link.title}
                  </a>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
)

const Footer = () => (
  <footer className="bg-ink text-linen border-t border-cocoa/40">
    <div className="container mx-auto px-4 py-12 grid gap-10 md:grid-cols-[1.2fr_0.9fr_1fr]">
      <div>
        <div className="flex items-center gap-3 text-cream">
          <span className="bg-clay text-cream p-2 rounded-full">
            <Tag size={16} />
          </span>
          <span className="font-display font-semibold text-xl">BestDealsOnline</span>
        </div>
        <p className="mt-4 max-w-md text-sm leading-relaxed text-linen/70">
          Research-led deal picks, buyer-feedback summaries, and category guides designed to help readers verify live
          price and availability on Amazon before purchasing.
        </p>
      </div>

      <div>
        <div className="text-cream font-bold">Core links</div>
        <ul className="mt-4 space-y-3 text-sm">
          <li><a href="/about-best-online-deals.html" className="hover:text-blush">About</a></li>
          <li><a href="/online-deals-methodology.html" className="hover:text-blush">Methodology</a></li>
          <li><a href="/review-aggregation-guidelines.html" className="hover:text-blush">Review policy</a></li>
          <li><a href="/blog/index.html" className="hover:text-blush">Research blog</a></li>
          <li><a href="/contact-best-online-deals.html" className="hover:text-blush">Contact</a></li>
        </ul>
      </div>

      <div>
        <div className="text-cream font-bold">Disclosure</div>
        <p className="mt-4 text-sm leading-relaxed text-linen/70">
          As an Amazon Associate, we earn from qualifying purchases.
        </p>
        <p className="mt-3 text-sm leading-relaxed text-linen/70">
          Prices and availability are subject to change. Always verify the current listing before you buy.
        </p>
        <a
          href="/affiliate-disclosure.html"
          className="mt-4 inline-flex items-center text-sm font-bold text-blush hover:text-cream"
        >
          Full disclosure <ExternalLink size={14} className="ml-1.5" />
        </a>
      </div>
    </div>
  </footer>
)

const App = () => {
  const { items, loading, error } = useProducts()

  const counts = useMemo(() => {
    const map = {}
    for (const item of items) {
      map[item.category] = (map[item.category] ?? 0) + 1
    }
    return map
  }, [items])

  const featured = useMemo(() => pickFeatured(items, 12), [items])

  return (
    <div className="min-h-screen bg-cream text-ink font-sans">
      <DisclosureBanner />
      <Navbar />
      <Hero counts={counts} />
      <main>
        <FeaturedDeals items={featured} loading={loading} error={error} />
        <DealTruthDemo />
        <UseCasesSection />
        <CategoryGrid counts={counts} />
        <ResearchSection />
        <TrustSection />
      </main>
      <Footer />
    </div>
  )
}

export default App
