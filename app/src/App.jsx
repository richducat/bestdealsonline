import React, { useMemo, useState } from 'react'
import {
  ArrowUpRight,
  BookOpen,
  ExternalLink,
  FileText,
  Info,
  Mail,
  Menu,
  Search,
  ShieldCheck,
  Tag,
  X,
} from 'lucide-react'

const CATEGORY_GUIDES = [
  {
    title: 'Electronics deals',
    href: '/electronics-deals.html',
    label: 'Category guide',
    description: 'Chargers, audio, monitors, routers, storage, and other everyday electronics.',
    image: '/images/categories/electronics.webp',
  },
  {
    title: 'Home deals',
    href: '/home-deals.html',
    label: 'Category guide',
    description: 'Comfort, organization, cleaning, bedding, and practical apartment upgrades.',
    image: '/images/categories/home.webp',
  },
  {
    title: 'Kitchen deals',
    href: '/kitchen-deals.html',
    label: 'Category guide',
    description: 'Coffee gear, cookware, prep tools, storage, and weeknight cooking essentials.',
    image: '/images/categories/kitchen.webp',
  },
  {
    title: 'Tools deals',
    href: '/tools-deals.html',
    label: 'Category guide',
    description: 'DIY kits, drills, measuring tools, repair basics, and workshop staples.',
    image: '/images/categories/tools.webp',
  },
  {
    title: 'Kids deals',
    href: '/kids-deals.html',
    label: 'Category guide',
    description: 'School gear, toys, headphones, lunchboxes, and everyday parent-friendly picks.',
    image: '/images/categories/kids.webp',
  },
  {
    title: 'Beauty deals',
    href: '/beauty-deals.html',
    label: 'Category guide',
    description: 'Skincare, grooming, hair tools, and routine products people actually repurchase.',
    image: '/images/categories/beauty.webp',
  },
  {
    title: 'Fitness deals',
    href: '/fitness-deals.html',
    label: 'Category guide',
    description: 'Home gym basics, recovery gear, trackers, and compact workout equipment.',
    image: '/images/categories/fitness.webp',
  },
  {
    title: 'Pets deals',
    href: '/pets-deals.html',
    label: 'Category guide',
    description: 'Bowls, litter gear, travel accessories, and comfort-focused pet essentials.',
    image: '/images/categories/pets.webp',
  },
]

const FEATURED_GUIDES = [
  {
    title: 'Best deals online today',
    href: '/best-deals-online-today.html',
    label: 'Roundup',
    description: 'A current shortlist of the most useful internal guides to start from.',
  },
  {
    title: 'Evergreen deal guides',
    href: '/evergreen-deal-guides.html',
    label: 'Roundup',
    description: 'Durable, year-round buyer-intent pages instead of flash-sale noise.',
  },
  {
    title: 'Price history guide',
    href: '/best-deals-with-price-history.html',
    label: 'Method',
    description: 'How to sanity-check discounts before clicking out to Amazon.',
  },
  {
    title: 'Buyer beware checklist',
    href: '/best-deals-legit-or-scam.html',
    label: 'Trust',
    description: 'Signals that separate a useful deal from a misleading one.',
  },
]

const RESEARCH_POSTS = [
  {
    title: 'USB-C chargers: what buyers like and what they complain about',
    href: '/blog/usb-c-chargers-what-buyers-like-what-they-complain-about-and-what-to-look-for.html',
    category: 'Electronics',
    description: 'A neutral summary of the tradeoffs shoppers mention most: heat, wattage, cables, and port sharing.',
  },
  {
    title: 'Wireless chargers: speed, heat, and reliability',
    href: '/blog/wireless-chargers-what-reviewers-say-about-speed-heat-and-reliability.html',
    category: 'Electronics',
    description: 'Practical buyer feedback about charging speed, alignment, and everyday desk use.',
  },
  {
    title: 'Robot vacuums: navigation, pet hair, and maintenance',
    href: '/blog/robot-vacuums-what-reviewers-actually-mention-navigation-pet-hair-maintenance.html',
    category: 'Home',
    description: 'What people consistently praise, what breaks trust, and when the category actually saves time.',
  },
  {
    title: 'Coffee makers under $100: taste, reliability, and cleaning',
    href: '/blog/coffee-makers-under-100-what-reviewers-care-about-taste-reliability-ease.html',
    category: 'Kitchen',
    description: 'A grounded guide to the issues buyers notice after the first week of ownership.',
  },
  {
    title: 'Kids headphones: comfort, volume limits, and durability',
    href: '/blog/kids-headphones-what-parents-and-buyers-mention-most-comfort-volume-limits-durability.html',
    category: 'Kids',
    description: 'The recurring parent concerns that matter more than marketing graphics.',
  },
  {
    title: 'Dash cams: video clarity, night vision, heat, and app quality',
    href: '/blog/dash-cams-what-buyers-mention-most-video-clarity-night-vision-heat-app.html',
    category: 'Electronics',
    description: 'A summary of the real complaints shoppers surface after installation.',
  },
]

const TRUST_LINKS = [
  {
    title: 'Affiliate disclosure',
    href: '/affiliate-disclosure.html',
    description: 'Exactly how this site makes money and the language Amazon requires.',
    icon: ShieldCheck,
  },
  {
    title: 'Online deals methodology',
    href: '/online-deals-methodology.html',
    description: 'How pages are selected, reviewed, and updated before they stay live.',
    icon: FileText,
  },
  {
    title: 'Review aggregation guidelines',
    href: '/review-aggregation-guidelines.html',
    description: 'How buyer feedback is summarized without pretending every product was hands-on tested.',
    icon: BookOpen,
  },
  {
    title: 'About Best Online Deals',
    href: '/about-best-online-deals.html',
    description: 'What this site publishes, what it does not claim, and why the pages exist.',
    icon: Info,
  },
  {
    title: 'Contact Best Online Deals',
    href: '/contact-best-online-deals.html',
    description: 'A public correction and feedback channel for readers and reviewers.',
    icon: Mail,
  },
  {
    title: 'Privacy policy',
    href: '/privacy.html',
    description: 'Analytics, cookies, and outbound-link expectations in plain language.',
    icon: ShieldCheck,
  },
]

function searchText(items) {
  return items
    .map((item) => [item.title, item.description, item.label, item.category].filter(Boolean).join(' '))
    .join(' ')
}

function matchesQuery(item, query) {
  if (!query) return true
  return searchText([item]).toLowerCase().includes(query)
}

const DisclosureBanner = () => {
  const [visible, setVisible] = useState(true)
  if (!visible) return null

  return (
    <div className="bg-slate-100 border-b border-slate-200 text-xs text-slate-700">
      <div className="container mx-auto px-4 py-2 flex items-start justify-between gap-3">
        <p className="leading-relaxed">
          <strong>Affiliate disclosure:</strong> BestDealsOnline may earn a commission when you buy through links on this
          site, at no extra cost to you. <a className="underline" href="/affiliate-disclosure.html">Details</a>.
        </p>
        <button
          type="button"
          onClick={() => setVisible(false)}
          className="inline-flex items-center justify-center h-8 w-8 rounded-md text-slate-500 hover:bg-slate-200 hover:text-slate-900"
          aria-label="Dismiss disclosure"
        >
          <X size={14} />
        </button>
      </div>
    </div>
  )
}

const NavLink = ({ href, children }) => (
  <a href={href} className="hover:text-yellow-300 transition-colors">
    {children}
  </a>
)

const Navbar = ({ query, setQuery }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <nav className="bg-slate-950 text-white sticky top-0 z-40 border-b border-slate-900">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between gap-4">
          <a href="/" className="flex items-center gap-3">
            <span className="bg-yellow-400 text-slate-950 p-2 rounded-lg">
              <Tag size={18} />
            </span>
            <span className="leading-tight">
              <span className="block font-extrabold tracking-tight text-lg">BestDealsOnline</span>
              <span className="block text-[10px] text-yellow-300 uppercase tracking-[0.28em]">Editorial Guides</span>
            </span>
          </a>

          <button
            type="button"
            className="md:hidden inline-flex items-center justify-center h-10 w-10 rounded-lg border border-white/10"
            onClick={() => setMobileMenuOpen((open) => !open)}
            aria-label="Toggle navigation"
          >
            {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
          </button>

          <div className="hidden md:flex items-center gap-6 text-sm font-semibold">
            <NavLink href="#guides">Guides</NavLink>
            <NavLink href="#research">Research</NavLink>
            <NavLink href="#trust">Trust</NavLink>
            <NavLink href="/about-best-online-deals.html">About</NavLink>
            <NavLink href="/contact-best-online-deals.html">Contact</NavLink>
          </div>
        </div>

        <div className="mt-4 relative">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search guides, research, and trust pages"
            className="w-full rounded-2xl border border-white/10 bg-slate-900 px-11 py-3 text-sm text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-yellow-400"
          />
        </div>

        {mobileMenuOpen ? (
          <div className="md:hidden mt-4 flex flex-col gap-3 text-sm font-semibold">
            <NavLink href="#guides">Guides</NavLink>
            <NavLink href="#research">Research</NavLink>
            <NavLink href="#trust">Trust</NavLink>
            <NavLink href="/about-best-online-deals.html">About</NavLink>
            <NavLink href="/contact-best-online-deals.html">Contact</NavLink>
          </div>
        ) : null}
      </div>
    </nav>
  )
}

const Hero = () => {
  const reviewedAt = new Intl.DateTimeFormat('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date())

  return (
    <section className="bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 text-white">
      <div className="container mx-auto px-4 py-14 md:py-20">
        <div className="grid lg:grid-cols-[1.3fr_0.9fr] gap-8 items-start">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-yellow-400/30 bg-yellow-400/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.24em] text-yellow-200">
              Reviewed {reviewedAt}
            </div>
            <h1 className="mt-5 text-4xl md:text-6xl font-extrabold tracking-tight leading-tight">
              Deal research first.
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-yellow-100">
                Amazon clicks second.
              </span>
            </h1>
            <p className="mt-5 max-w-2xl text-lg text-slate-200 leading-relaxed">
              BestDealsOnline publishes internal deal guides, category hubs, and buyer-feedback summaries before sending
              readers to Amazon. We do not promise universal hands-on testing, fake countdown clocks, or invented review
              metrics. We publish clear disclosure, a public methodology, and a visible contact path instead.
            </p>

            <div className="mt-7 flex flex-wrap gap-3">
              <a
                href="#guides"
                className="inline-flex items-center justify-center min-h-11 px-5 rounded-xl bg-yellow-400 text-slate-950 font-extrabold hover:bg-yellow-300 transition-colors"
              >
                Browse internal guides <ArrowUpRight size={15} className="ml-2" />
              </a>
              <a
                href="#trust"
                className="inline-flex items-center justify-center min-h-11 px-5 rounded-xl border border-white/15 text-white font-bold hover:bg-white/10 transition-colors"
              >
                Review our policies
              </a>
            </div>
          </div>

          <div className="grid gap-4">
            <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
              <div className="text-xs font-bold uppercase tracking-[0.22em] text-yellow-200">What you can verify</div>
              <ul className="mt-4 space-y-3 text-sm text-slate-200">
                <li>Visible affiliate disclosure on every major page.</li>
                <li>Public about, privacy, methodology, and contact pages.</li>
                <li>Internal guides and research before affiliate outbound clicks.</li>
              </ul>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
              <div className="text-xs font-bold uppercase tracking-[0.22em] text-yellow-200">Editorial stance</div>
              <p className="mt-4 text-sm text-slate-200 leading-relaxed">
                This site is built to help readers narrow choices, then verify live price, availability, and reviews on
                Amazon before buying. Internal pages stay focused on practical buyer intent, not keyword-stuffed search traps.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

const SectionHeader = ({ eyebrow, title, body }) => (
  <div className="max-w-3xl">
    <div className="text-xs font-bold uppercase tracking-[0.22em] text-slate-500">{eyebrow}</div>
    <h2 className="mt-3 text-3xl md:text-4xl font-extrabold tracking-tight text-slate-950">{title}</h2>
    <p className="mt-3 text-slate-600 text-lg leading-relaxed">{body}</p>
  </div>
)

const CategoryGuideCard = ({ guide }) => (
  <a
    href={guide.href}
    className="group overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-lg"
  >
    <div className="h-44 overflow-hidden bg-slate-100">
      <img
        src={guide.image}
        alt={guide.title}
        className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        loading="lazy"
      />
    </div>
    <div className="p-5">
      <div className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] text-slate-600">
        {guide.label}
      </div>
      <h3 className="mt-4 text-xl font-extrabold text-slate-950">{guide.title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-600">{guide.description}</p>
      <div className="mt-5 inline-flex items-center text-sm font-bold text-slate-900">
        Open guide <ArrowUpRight size={15} className="ml-1.5" />
      </div>
    </div>
  </a>
)

const FeatureCard = ({ item }) => (
  <a
    href={item.href}
    className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
  >
    <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-500">{item.label}</div>
    <h3 className="mt-3 text-xl font-extrabold text-slate-950">{item.title}</h3>
    <p className="mt-2 text-sm leading-relaxed text-slate-600">{item.description}</p>
    <div className="mt-4 inline-flex items-center text-sm font-bold text-slate-900">
      Read more <ArrowUpRight size={15} className="ml-1.5" />
    </div>
  </a>
)

const ResearchCard = ({ post }) => (
  <a
    href={post.href}
    className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
  >
    <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-blue-700">{post.category}</div>
    <h3 className="mt-3 text-xl font-extrabold text-slate-950">{post.title}</h3>
    <p className="mt-2 text-sm leading-relaxed text-slate-600">{post.description}</p>
    <div className="mt-4 inline-flex items-center text-sm font-bold text-slate-900">
      Open research <ArrowUpRight size={15} className="ml-1.5" />
    </div>
  </a>
)

const TrustCard = ({ item }) => {
  const Icon = item.icon

  return (
    <a
      href={item.href}
      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
    >
      <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-slate-950 text-yellow-300">
        <Icon size={18} />
      </div>
      <h3 className="mt-4 text-xl font-extrabold text-slate-950">{item.title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-600">{item.description}</p>
      <div className="mt-4 inline-flex items-center text-sm font-bold text-slate-900">
        Open page <ArrowUpRight size={15} className="ml-1.5" />
      </div>
    </a>
  )
}

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
          Research-led deal guides, buyer-feedback summaries, and internal category hubs designed to help readers verify
          live price and availability on Amazon before purchasing.
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
  const [query, setQuery] = useState('')
  const normalizedQuery = query.trim().toLowerCase()

  const filteredCategoryGuides = useMemo(
    () => CATEGORY_GUIDES.filter((item) => matchesQuery(item, normalizedQuery)),
    [normalizedQuery]
  )
  const filteredFeaturedGuides = useMemo(
    () => FEATURED_GUIDES.filter((item) => matchesQuery(item, normalizedQuery)),
    [normalizedQuery]
  )
  const filteredResearchPosts = useMemo(
    () => RESEARCH_POSTS.filter((item) => matchesQuery(item, normalizedQuery)),
    [normalizedQuery]
  )
  const filteredTrustLinks = useMemo(
    () => TRUST_LINKS.filter((item) => matchesQuery(item, normalizedQuery)),
    [normalizedQuery]
  )

  const hasResults =
    filteredCategoryGuides.length > 0 ||
    filteredFeaturedGuides.length > 0 ||
    filteredResearchPosts.length > 0 ||
    filteredTrustLinks.length > 0

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <DisclosureBanner />
      <Navbar query={query} setQuery={setQuery} />
      <Hero />

      <main>
        <section id="guides" className="container mx-auto px-4 py-12 md:py-16">
          <SectionHeader
            eyebrow="Internal Guides"
            title="Start with internal pages, not direct affiliate jumps."
            body="These are the category hubs and editorial roundups that explain what each area covers before any outbound click happens."
          />

          {!hasResults ? (
            <div className="mt-8 rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
              <div className="font-extrabold text-slate-950">No matching pages</div>
              <p className="mt-2 text-sm text-slate-600">Try a broader search like “kitchen”, “policy”, or “research”.</p>
            </div>
          ) : null}

          {filteredCategoryGuides.length > 0 ? (
            <div className="mt-8 grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
              {filteredCategoryGuides.map((guide) => (
                <CategoryGuideCard key={guide.href} guide={guide} />
              ))}
            </div>
          ) : null}

          {filteredFeaturedGuides.length > 0 ? (
            <div className="mt-10 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {filteredFeaturedGuides.map((item) => (
                <FeatureCard key={item.href} item={item} />
              ))}
            </div>
          ) : null}
        </section>

        <section id="research" className="border-y border-slate-200 bg-white">
          <div className="container mx-auto px-4 py-12 md:py-16">
            <SectionHeader
              eyebrow="Research"
              title="Recent buyer-feedback summaries."
              body="These posts are designed to surface recurring pros, complaints, and feature tradeoffs so shoppers can narrow the field before clicking to Amazon."
            />

            {filteredResearchPosts.length > 0 ? (
              <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {filteredResearchPosts.map((post) => (
                  <ResearchCard key={post.href} post={post} />
                ))}
              </div>
            ) : null}
          </div>
        </section>

        <section id="trust" className="container mx-auto px-4 py-12 md:py-16">
          <SectionHeader
            eyebrow="Trust Pages"
            title="Policy pages Amazon reviewers expect to find."
            body="The site now foregrounds disclosure, methodology, contact information, privacy details, and editorial guardrails so the public-facing experience looks complete and reviewable."
          />

          {filteredTrustLinks.length > 0 ? (
            <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {filteredTrustLinks.map((item) => (
                <TrustCard key={item.href} item={item} />
              ))}
            </div>
          ) : null}

          <div className="mt-10 rounded-3xl border border-slate-200 bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-6 md:p-8 text-white">
            <div className="flex items-start gap-3">
              <ShieldCheck size={20} className="mt-1 text-yellow-300" />
              <div>
                <h3 className="text-2xl font-extrabold">Reader expectation matters.</h3>
                <p className="mt-3 max-w-3xl text-sm md:text-base leading-relaxed text-slate-200">
                  BestDealsOnline should look like an editorial site with clear ownership and clear documentation, not a
                  thin layer of search-result redirects. This homepage now prioritizes internal content, public policy
                  pages, and transparent language about what the site does and does not claim.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}

export default App
