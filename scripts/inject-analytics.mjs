import fs from 'node:fs/promises'
import path from 'node:path'

const ROOT = process.cwd()
const GA_ID = 'G-6GD5DK8067'

const GTAG_BLOCK = `
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=${GA_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', '${GA_ID}', (function(){try{var K='bdo.internalTraffic';var q=new URLSearchParams(location.search).get('internal');if(q==='1'||q==='true'){localStorage.setItem(K,'1');}else if(q==='0'||q==='false'){localStorage.removeItem(K);}return localStorage.getItem(K)==='1'?{traffic_type:'internal'}:{};}catch(e){return {};}})());
    </script>
    <script defer src="/assets/track.js"></script>
`

function shouldSkip(filePath) {
  // Skip built app artifacts.
  const rel = path.relative(ROOT, filePath)
  if (rel.startsWith('app/')) return true
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

function injectIntoHead(html) {
  if (html.includes(`gtag/js?id=${GA_ID}`) && html.includes('/assets/track.js')) return html

  // Put it near the end of <head> before </head>
  const closeHead = html.lastIndexOf('</head>')
  if (closeHead === -1) return html

  // If gtag exists but track.js doesn't, only add track.js.
  if (html.includes(`gtag/js?id=${GA_ID}`) && !html.includes('/assets/track.js')) {
    return html.slice(0, closeHead) + `\n    <script defer src="/assets/track.js"></script>\n` + html.slice(closeHead)
  }

  return html.slice(0, closeHead) + GTAG_BLOCK + html.slice(closeHead)
}

let updated = 0
let scanned = 0

for await (const filePath of walk(ROOT)) {
  if (!filePath.endsWith('.html')) continue
  scanned++
  const before = await fs.readFile(filePath, 'utf8')
  const after = injectIntoHead(before)
  if (after !== before) {
    await fs.writeFile(filePath, after, 'utf8')
    updated++
    console.log('updated', path.relative(ROOT, filePath))
  }
}

console.log(`done: scanned=${scanned} updated=${updated}`)
