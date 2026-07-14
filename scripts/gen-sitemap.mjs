import fs from 'node:fs/promises'
import path from 'node:path'
import { execFileSync } from 'node:child_process'

const ROOT = process.cwd()
const BASE_URL = 'https://bestdealsonline.us'
const DENIED_ROOT_HTML = new Set(['example-post.html'])
const PRIORITY_ROOT_HTML = new Set([
  'index.html',
  'about-best-online-deals.html',
  'affiliate-disclosure.html',
  'contact-best-online-deals.html',
  'privacy.html',
  'online-deals-methodology.html',
  'review-aggregation-guidelines.html',
  'best-deals-online-today.html',
  'best-deals-online.html',
  'best-deals-with-price-history.html',
  'electronics-deals.html',
  'home-deals.html',
  'kitchen-deals.html',
  'tools-deals.html',
  'kids-deals.html',
  'beauty-deals.html',
  'fitness-deals.html',
  'pets-deals.html',
])

function shouldSkip(filePath) {
  const rel = path.relative(ROOT, filePath).split(path.sep).join('/')
  return rel.startsWith('app/') || rel.startsWith('images/categories/') ||
    rel.startsWith('node_modules/') || rel.includes('/node_modules/') || rel.startsWith('.git/')
}

function shouldIncludeHtml(rel) {
  if (rel.startsWith('blog/')) return path.basename(rel) !== 'example-post.html'
  return !DENIED_ROOT_HTML.has(path.basename(rel))
}

async function* walk(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true })
  for (const entry of entries) {
    const filePath = path.join(dir, entry.name)
    if (shouldSkip(filePath)) continue
    if (entry.isDirectory()) yield* walk(filePath)
    else yield filePath
  }
}

function urlFor(rel) {
  const clean = rel.split(path.sep).join('/')
  return clean === 'index.html' ? `${BASE_URL}/` : `${BASE_URL}/${clean}`
}

function xmlEscape(value) {
  return value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
}

function gitLastModified(rel, fallbackDate) {
  try {
    const date = execFileSync('git', ['log', '-1', '--format=%cs', '--', rel], {
      cwd: ROOT,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    }).trim()
    return /^\d{4}-\d{2}-\d{2}$/.test(date) ? date : fallbackDate
  } catch {
    return fallbackDate
  }
}

function visibleWordCount(html) {
  return html
    .replace(/<(script|style|nav|footer)\b[^>]*>[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&[a-z0-9#]+;/gi, ' ')
    .trim()
    .split(/\s+/)
    .filter(Boolean).length
}

function renderUrlset(urls) {
  return `<?xml version="1.0" encoding="UTF-8"?>\n` +
    `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
    urls.map(({ loc, lastmod }) =>
      `  <url>\n    <loc>${xmlEscape(loc)}</loc>\n    <lastmod>${lastmod}</lastmod>\n  </url>`
    ).join('\n') +
    `\n</urlset>\n`
}

const urls = []
for await (const filePath of walk(ROOT)) {
  if (!filePath.endsWith('.html')) continue
  const rel = path.relative(ROOT, filePath).split(path.sep).join('/')
  if (rel.startsWith('app/dist/') || !shouldIncludeHtml(rel)) continue
  const stat = await fs.stat(filePath)
  const fallbackDate = stat.mtime.toISOString().slice(0, 10)
  const html = await fs.readFile(filePath, 'utf8')
  urls.push({
    rel,
    loc: urlFor(rel),
    lastmod: gitLastModified(rel, fallbackDate),
    words: visibleWordCount(html),
  })
}

urls.sort((a, b) => a.loc.localeCompare(b.loc))
const priorityUrls = urls.filter(({ rel, words }) =>
  rel.startsWith('blog/') || PRIORITY_ROOT_HTML.has(rel) || words >= 300
)

await fs.writeFile(path.join(ROOT, 'sitemap.xml'), renderUrlset(urls), 'utf8')
await fs.writeFile(path.join(ROOT, 'sitemap-priority.xml'), renderUrlset(priorityUrls), 'utf8')
console.log(`wrote sitemap.xml with ${urls.length} urls`)
console.log(`wrote sitemap-priority.xml with ${priorityUrls.length} high-value urls`)
