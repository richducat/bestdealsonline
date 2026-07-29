import { cpSync, existsSync, mkdirSync, readdirSync, rmSync } from 'node:fs'
import { join } from 'node:path'

// Copy build output into repo root so GitHub Pages (configured to /) serves it.
const distDir = join(process.cwd(), 'dist')
const repoRoot = join(process.cwd(), '..')

if (!existsSync(distDir)) {
  console.error('dist/ not found. Run build first.')
  process.exit(1)
}

// Keep existing root assets (used by many static pages) and merge build assets into it.
const oldAssets = join(repoRoot, 'assets')
const newAssets = join(distDir, 'assets')
if (existsSync(newAssets)) {
  mkdirSync(oldAssets, { recursive: true })
}

// Every build emits a new content-hashed index-<hash>.js (and .css, if any),
// leaving the previous build's bundle orphaned with nothing referencing it.
// Prune those before copying the new one in so they don't accumulate forever
// -- only this app's hashed entry files match this naming, so nothing else
// under assets/ (favicon, hero art, track.js) is touched.
if (existsSync(oldAssets)) {
  for (const name of readdirSync(oldAssets)) {
    if (/^index-.*\.(js|css)$/.test(name)) {
      rmSync(join(oldAssets, name))
    }
  }
}

// Copy index.html and assets/
cpSync(join(distDir, 'index.html'), join(repoRoot, 'index.html'))
cpSync(join(distDir, 'assets'), join(repoRoot, 'assets'), { recursive: true })

// The standalone /deal-check.html page imports the scoring engine as
// native ESM straight from /assets/, so keep those copies in lockstep
// with the app's source on every build.
cpSync(join(process.cwd(), 'src', 'dealtruth.js'), join(repoRoot, 'assets', 'dealtruth.js'))
cpSync(join(process.cwd(), 'src', 'dealcheck-core.js'), join(repoRoot, 'assets', 'dealcheck-core.js'))

console.log('Copied build output to repo root.')
