// Submit all sitemap URLs to IndexNow (instant indexing for Bing, Yandex,
// Seznam.cz, Naver, Yep -- Google does not participate in IndexNow and
// still requires normal crawling/sitemap discovery).
//
// Run this AFTER the site is deployed and the key file below is live at
// https://bestdealsonline.us/<key>.txt -- IndexNow verifies that file
// before accepting the submission.
//
// Usage: node scripts/indexnow_submit.mjs

import fs from 'node:fs/promises'

const HOST = 'bestdealsonline.us'
const KEY = '85a315150525886cabeaf02f8337ab90'
const KEY_LOCATION = `https://${HOST}/${KEY}.txt`

async function main() {
  const xml = await fs.readFile(new URL('../sitemap.xml', import.meta.url), 'utf8')
  const urls = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1])

  if (urls.length === 0) {
    throw new Error('No URLs found in sitemap.xml')
  }

  console.log(`Submitting ${urls.length} URLs to IndexNow...`)

  const res = await fetch('https://api.indexnow.org/indexnow', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({
      host: HOST,
      key: KEY,
      keyLocation: KEY_LOCATION,
      urlList: urls,
    }),
  })

  console.log(`IndexNow response: ${res.status} ${res.statusText}`)
  const text = await res.text()
  if (text) console.log(text)

  if (res.status !== 200 && res.status !== 202) {
    process.exitCode = 1
  }
}

main().catch((err) => {
  console.error(err)
  process.exitCode = 1
})
