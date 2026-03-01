import { cpSync, existsSync, mkdirSync } from 'node:fs'
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

// Copy index.html and assets/
cpSync(join(distDir, 'index.html'), join(repoRoot, 'index.html'))
cpSync(join(distDir, 'assets'), join(repoRoot, 'assets'), { recursive: true })

console.log('Copied build output to repo root.')
