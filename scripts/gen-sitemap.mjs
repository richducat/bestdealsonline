import fs from 'node:fs/promises'
import path from 'node:path'

const ROOT = process.cwd()
const BASE_URL = 'https://bestdealsonline.us'

function shouldSkip(filePath) {
  const rel = path.relative(ROOT, filePath)
  if (rel.startsWith('app/')) return true
  if (rel.startsWith('images/categories/')) return true
  if (rel.startsWith('node_modules/')) return true
  if (rel.includes('/node_modules/')) return true
  if (rel.startsWith('.git/')) return true
  return false
}

async function* walk(dir) {
  const ents = await fs.readdir(dir, { withFileTypes: true })
  for (const ent of ents) {
    const p = path.join(dir, ent.name)
    if (shouldSkip(p)) continue
    if (ent.isDirectory()) {
      yield* walk(p)
    } else {
      yield p
    }
  }
}

function urlFor(relPath) {
  // ensure forward slashes
  const clean = relPath.split(path.sep).join('/')
  // index.html at root maps to /
  if (clean === 'index.html') return `${BASE_URL}/`
  return `${BASE_URL}/${clean}`
}

const urls = []
for await (const filePath of walk(ROOT)) {
  if (!filePath.endsWith('.html')) continue
  const rel = path.relative(ROOT, filePath)
  // exclude app/dist if ever copied
  if (rel.startsWith('app/dist/')) continue
  urls.push({
    loc: urlFor(rel),
  })
}

urls.sort((a, b) => a.loc.localeCompare(b.loc))

const lastmod = new Date().toISOString().slice(0, 10)

const xml = `<?xml version="1.0" encoding="UTF-8"?>\n` +
  `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
  urls
    .map((u) => `  <url>\n    <loc>${u.loc}</loc>\n    <lastmod>${lastmod}</lastmod>\n  </url>`)
    .join('\n') +
  `\n</urlset>\n`

await fs.writeFile(path.join(ROOT, 'sitemap.xml'), xml, 'utf8')
console.log(`wrote sitemap.xml with ${urls.length} urls`)
