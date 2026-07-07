import React, { useEffect, useMemo, useState } from 'react'
import {
  ArrowUpRight,
  BookOpen,
  ExternalLink,
  FileText,
  Menu,
  ShieldCheck,
  Tag,
  X,
} from 'lucide-react'

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
    seenTitles.add(item.title)
    const bucket = byCategory.get(item.category) ?? []
    bucket.push(item)
    byCategory.set(item.category, bucket)
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

function useProducts() {
  const [state, setState] = useState({ items: [], loading: true, error: false })

  useEffect(() => {
    let cancelled = false
    fetch('/data/products.json')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        if (!cancelled) setState({ items: data.items ?? [], loading: false, error: false })
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
    <div className="bg-slate-100 border-b border-slate-200 text-xs text-slate-700">
      <div className="container mx-auto px-4 py-2 flex items-start justify-between gap-3">
        <p className="leading-relaxed">
          <strong>Affiliate disclosure:</strong> As an Amazon Associate, we earn from qualifying purchases.{' '}
          <a className="underline" href="/affiliate-disclosure.html">Details</a>.
        </p>
        <button
          type="button"
          onClick={() => setVisible(false)}
          className="inline-flex items-center justify-center h-8 w-8 rounded-md text-slate-500 hover:bg-slate-200 hover:text-slate-900 shrink-0"
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
    <nav className="bg-slate-950 text-white sticky top-0 z-40 border-b border-slate-900">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between gap-4">
        <a href="/" className="flex items-center gap-3">
          <span className="bg-yellow-400 text-slate-950 p-2 rounded-lg">
            <Tag size={18} />
          </span>
          <span className="leading-tight">
            <span className="block font-extrabold tracking-tight text-lg">BestDealsOnline</span>
            <span className="block text-[10px] text-yellow-300 uppercase tracking-[0.28em]">Amazon Deal Picks</span>
          </span>
        </a>

        <button
          type="button"
          className="md:hidden inline-flex items-center justify-center h-11 w-11 rounded-lg border border-white/10"
          onClick={() => setMobileMenuOpen((open) => !open)}
          aria-label="Toggle navigation"
        >
          {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
        </button>

        <div className="hidden md:flex items-center gap-6 text-sm font-semibold">
          <a href="#deals" className="hover:text-yellow-300 transition-colors">Today's Picks</a>
          <a href="#categories" className="hover:text-yellow-300 transition-colors">Categories</a>
          <a href="#research" className="hover:text-yellow-300 transition-colors">Research</a>
          <a href="/blog/index.html" className="hover:text-yellow-300 transition-colors">Blog</a>
        </div>
      </div>

      {mobileMenuOpen ? (
        <div className="md:hidden px-4 pb-4 flex flex-col gap-1 text-sm font-semibold">
          <a href="#deals" className="min-h-11 flex items-center hover:text-yellow-300">Today's Picks</a>
          <a href="#categories" className="min-h-11 flex items-center hover:text-yellow-300">Categories</a>
          <a href="#research" className="min-h-11 flex items-center hover:text-yellow-300">Research</a>
          <a href="/blog/index.html" className="min-h-11 flex items-center hover:text-yellow-300">Blog</a>
        </div>
      ) : null}
    </nav>
  )
}

const CategoryChips = ({ counts }) => (
  <div className="mt-6 -mx-4 px-4 md:mx-0 md:px-0 flex gap-2 overflow-x-auto pb-2 md:flex-wrap md:overflow-visible">
    {CATEGORIES.map((cat) => (
      <a
        key={cat.href}
        href={cat.href}
        className="shrink-0 inline-flex items-center gap-1.5 px-4 py-2.5 min-h-11 rounded-full bg-white/10 hover:bg-white/20 text-sm font-semibold text-white transition-colors whitespace-nowrap"
      >
        {cat.name}
        {counts[cat.name] ? <span className="text-yellow-300">· {counts[cat.name]}</span> : null}
      </a>
    ))}
  </div>
)

const Hero = ({ counts }) => (
  <section className="bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 text-white">
    <div className="container mx-auto px-4 py-12 md:py-16">
      <div className="grid lg:grid-cols-[1.2fr_0.8fr] gap-10 items-center">
        <div className="min-w-0">
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight">
            We read the reviews.
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-yellow-100">
              You skip the regret.
            </span>
          </h1>
          <p className="mt-5 max-w-xl text-lg text-slate-200 leading-relaxed">
            300+ real Amazon finds across Electronics, Home, Kitchen, Tools, Kids, Beauty, Fitness &amp; Pets — each one
            backed by our own buyer-research, not a five-star badge.
          </p>
          <p className="mt-3 text-xs text-slate-400">
            As an Amazon Associate, we earn from qualifying purchases.
          </p>

          <div className="mt-7 flex flex-wrap items-center gap-5">
            <a
              href="#deals"
              className="inline-flex items-center justify-center min-h-12 px-6 rounded-xl bg-yellow-400 text-slate-950 font-extrabold hover:bg-yellow-300 transition-colors text-base"
            >
              See Today's Picks <ArrowUpRight size={16} className="ml-2" />
            </a>
            <a
              href="/online-deals-methodology.html"
              className="inline-flex items-center min-h-12 text-sm font-bold text-slate-200 hover:text-yellow-300 transition-colors"
            >
              How we pick <ArrowUpRight size={14} className="ml-1.5" />
            </a>
          </div>

          <CategoryChips counts={counts} />
        </div>

        <div className="hidden lg:grid gap-4">
          {CATEGORIES.slice(0, 3).map((cat) => (
            <div key={cat.href} className="rounded-2xl border border-white/10 bg-white/5 overflow-hidden flex items-center gap-4 p-3">
              <img
                src={cat.image}
                alt=""
                width="88"
                height="88"
                className="h-20 w-20 rounded-xl object-cover shrink-0"
                loading="eager"
              />
              <div>
                <div className="text-xs font-bold uppercase tracking-[0.18em] text-yellow-300">{cat.name}</div>
                <div className="text-sm text-slate-300 mt-1">{cat.description}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </section>
)

const ProductCard = ({ item }) => (
  <a
    href={item.affiliateLink}
    target="_blank"
    rel="nofollow noopener noreferrer"
    className="group rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden transition-all hover:-translate-y-0.5 hover:shadow-lg flex flex-col"
  >
    <div className="aspect-square overflow-hidden bg-slate-100">
      <img
        src={item.imageUrl}
        alt={cleanTitle(item.title)}
        className="h-full w-full object-contain p-4 transition-transform duration-300 group-hover:scale-105"
        loading="lazy"
      />
    </div>
    <div className="p-4 flex flex-col flex-1">
      <div className="text-[11px] font-bold uppercase tracking-[0.14em] text-slate-500">{item.category}</div>
      <h3 className="mt-1.5 font-extrabold text-slate-950 leading-snug">{cleanTitle(item.title)}</h3>
      <div className="mt-auto pt-3 inline-flex items-center justify-center min-h-11 rounded-xl bg-slate-950 text-white text-sm font-bold group-hover:bg-slate-800 transition-colors">
        View on Amazon <ExternalLink size={13} className="ml-1.5" />
      </div>
    </div>
  </a>
)

const ProductCardSkeleton = () => (
  <div className="rounded-2xl border border-slate-200 bg-white overflow-hidden animate-pulse">
    <div className="aspect-square bg-slate-100" />
    <div className="p-4 space-y-2">
      <div className="h-2.5 w-16 bg-slate-200 rounded" />
      <div className="h-4 w-3/4 bg-slate-200 rounded" />
      <div className="h-9 w-full bg-slate-100 rounded-xl mt-3" />
    </div>
  </div>
)

const SectionHeader = ({ eyebrow, title, body }) => (
  <div className="max-w-3xl">
    <div className="text-xs font-bold uppercase tracking-[0.22em] text-slate-500">{eyebrow}</div>
    <h2 className="mt-3 text-3xl md:text-4xl font-extrabold tracking-tight text-slate-950">{title}</h2>
    {body ? <p className="mt-3 text-slate-600 text-lg leading-relaxed">{body}</p> : null}
  </div>
)

const FeaturedDeals = ({ items, loading, error }) => (
  <section id="deals" className="container mx-auto px-4 py-12 md:py-16">
    <SectionHeader
      eyebrow="Today's Picks"
      title="Deals worth a look right now."
      body="A mix across every category. Tap through to see live pricing and availability on Amazon."
    />
    {error ? (
      <p className="mt-8 text-slate-600">
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
    className="group overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-lg flex items-center gap-4 p-4"
  >
    <img
      src={cat.image}
      alt=""
      width="72"
      height="72"
      className="h-16 w-16 rounded-xl object-cover shrink-0"
      loading="lazy"
    />
    <div className="min-w-0">
      <h3 className="font-extrabold text-slate-950">{cat.name}</h3>
      <p className="mt-1 text-sm text-slate-600 leading-snug line-clamp-2">{cat.description}</p>
      {count ? <div className="mt-1.5 text-xs font-bold text-slate-500">{count} picks</div> : null}
    </div>
    <ArrowUpRight size={16} className="ml-auto shrink-0 text-slate-400 group-hover:text-slate-900" />
  </a>
)

const CategoryGrid = ({ counts }) => (
  <section id="categories" className="border-y border-slate-200 bg-white">
    <div className="container mx-auto px-4 py-12 md:py-16">
      <SectionHeader eyebrow="Shop by Category" title="Every category, one tap away." />
      <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {CATEGORIES.map((cat) => (
          <CategoryTile key={cat.href} cat={cat} count={counts[cat.name]} />
        ))}
      </div>
    </div>
  </section>
)

const ResearchPairingCard = ({ pairing }) => (
  <a
    href={pairing.href}
    className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
  >
    <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-blue-700">{pairing.category}</div>
    <h3 className="mt-3 text-lg font-extrabold text-slate-950 leading-snug">{pairing.title}</h3>
    <p className="mt-2 text-sm leading-relaxed text-slate-600">{pairing.takeaway}</p>
    <div className="mt-4 inline-flex items-center text-sm font-bold text-slate-900">
      Read the research <ArrowUpRight size={15} className="ml-1.5" />
    </div>
  </a>
)

const ResearchSection = () => (
  <section id="research" className="container mx-auto px-4 py-12 md:py-16">
    <SectionHeader
      eyebrow="Backed by the Research"
      title="Not a star rating. Real buyer feedback."
      body="Before you click through, here's what actual reviewers say holds up and what doesn't, by category."
    />
    <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {RESEARCH_PAIRINGS.map((pairing) => (
        <ResearchPairingCard key={pairing.href} pairing={pairing} />
      ))}
    </div>

    <div className="mt-10">
      <div className="text-sm font-bold text-slate-500 uppercase tracking-[0.18em]">More research</div>
      <div className="mt-4 grid gap-x-8 gap-y-3 md:grid-cols-2">
        {MORE_RESEARCH.map((post) => (
          <a
            key={post.href}
            href={post.href}
            className="flex items-baseline gap-3 py-1 text-sm hover:text-slate-950 min-h-11"
          >
            <span className="text-slate-400 font-bold shrink-0">{post.category}</span>
            <span className="underline decoration-slate-300 underline-offset-2">{post.title}</span>
          </a>
        ))}
      </div>
    </div>
  </section>
)

const TrustSection = () => (
  <section className="border-t border-slate-200 bg-white">
    <div className="container mx-auto px-4 py-12 md:py-16">
      <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 md:p-8">
        <div className="flex items-start gap-3">
          <ShieldCheck size={20} className="mt-1 text-slate-700 shrink-0" />
          <div>
            <h3 className="text-xl font-extrabold text-slate-950">Why trust this site</h3>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-600">
              We publish internal category guides and buyer-feedback research before any outbound Amazon link, and we
              don't invent star ratings, review counts, or countdown timers to push a click. Full methodology, policy,
              and contact details are always public.
            </p>
            <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm font-bold">
              {TRUST_LINKS.map((link) => {
                const Icon = link.icon
                return (
                  <a key={link.href} href={link.href} className="inline-flex items-center gap-1.5 min-h-11 text-slate-700 hover:text-slate-950">
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
  <footer className="bg-slate-950 text-slate-300 border-t border-slate-900">
    <div className="container mx-auto px-4 py-12 grid gap-10 md:grid-cols-[1.2fr_0.9fr_1fr]">
      <div>
        <div className="flex items-center gap-3 text-white">
          <span className="bg-yellow-400 text-slate-950 p-2 rounded-lg">
            <Tag size={16} />
          </span>
          <span className="font-extrabold text-lg">BestDealsOnline</span>
        </div>
        <p className="mt-4 max-w-md text-sm leading-relaxed text-slate-400">
          Research-led deal picks, buyer-feedback summaries, and category guides designed to help readers verify live
          price and availability on Amazon before purchasing.
        </p>
      </div>

      <div>
        <div className="text-white font-bold">Core links</div>
        <ul className="mt-4 space-y-3 text-sm">
          <li><a href="/about-best-online-deals.html" className="hover:text-yellow-300">About</a></li>
          <li><a href="/online-deals-methodology.html" className="hover:text-yellow-300">Methodology</a></li>
          <li><a href="/review-aggregation-guidelines.html" className="hover:text-yellow-300">Review policy</a></li>
          <li><a href="/blog/index.html" className="hover:text-yellow-300">Research blog</a></li>
          <li><a href="/contact-best-online-deals.html" className="hover:text-yellow-300">Contact</a></li>
        </ul>
      </div>

      <div>
        <div className="text-white font-bold">Disclosure</div>
        <p className="mt-4 text-sm leading-relaxed text-slate-400">
          As an Amazon Associate, we earn from qualifying purchases.
        </p>
        <p className="mt-3 text-sm leading-relaxed text-slate-400">
          Prices and availability are subject to change. Always verify the current listing before you buy.
        </p>
        <a
          href="/affiliate-disclosure.html"
          className="mt-4 inline-flex items-center text-sm font-bold text-yellow-300 hover:text-yellow-200"
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
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <DisclosureBanner />
      <Navbar />
      <Hero counts={counts} />
      <main>
        <FeaturedDeals items={featured} loading={loading} error={error} />
        <CategoryGrid counts={counts} />
        <ResearchSection />
        <TrustSection />
      </main>
      <Footer />
    </div>
  )
}

export default App
