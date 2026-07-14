import fs from 'node:fs/promises'
import path from 'node:path'

const ROOT = process.cwd()
const SITE = 'https://bestdealsonline.us'
const sitemap = await fs.readFile(path.join(ROOT, 'sitemap.xml'), 'utf8')
const priority = await fs.readFile(path.join(ROOT, 'sitemap-priority.xml'), 'utf8')
const urls = [...sitemap.matchAll(/<loc>(.*?)<\/loc>/g)].map((match) => match[1])
const priorityUrls = [...priority.matchAll(/<loc>(.*?)<\/loc>/g)].map((match) => match[1])
const dates = [...sitemap.matchAll(/<lastmod>(.*?)<\/lastmod>/g)].map((match) => match[1])
const errors = []

if (urls.length !== new Set(urls).size) errors.push('sitemap.xml contains duplicate URLs')
if (priorityUrls.length !== new Set(priorityUrls).size) errors.push('sitemap-priority.xml contains duplicate URLs')
if (dates.length !== urls.length) errors.push('one or more sitemap URLs has no lastmod')
if (new Set(dates).size < 2) errors.push('all sitemap lastmod values are identical')

for (const url of urls) {
  const pathname = new URL(url).pathname
  const rel = pathname === '/' ? 'index.html' : decodeURIComponent(pathname.slice(1))
  const filePath = path.join(ROOT, rel)
  let html
  try { html = await fs.readFile(filePath, 'utf8') }
  catch { errors.push(`${url}: target file is missing`); continue }
  const expectedCanonical = pathname === '/' ? `${SITE}/` : `${SITE}${pathname}`
  const canonical = html.match(/<link\s+rel=["']canonical["']\s+href=["']([^"']+)/i)?.[1]
  if (canonical !== expectedCanonical) errors.push(`${url}: canonical is ${canonical ?? 'missing'}`)
  if (/<meta\s+name=["']robots["'][^>]*noindex/i.test(html)) errors.push(`${url}: noindex conflicts with sitemap`)
}

for (const url of priorityUrls) {
  if (!urls.includes(url)) errors.push(`${url}: priority URL is absent from full sitemap`)
}

if (errors.length) {
  console.error(errors.slice(0, 30).join('\n'))
  if (errors.length > 30) console.error(`...and ${errors.length - 30} more`)
  process.exit(1)
}

console.log(`indexability check passed: ${urls.length} full URLs, ${priorityUrls.length} priority URLs, ${new Set(dates).size} lastmod dates`)
