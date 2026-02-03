import { cpSync, existsSync, mkdirSync, rmSync } from 'node:fs'
import { join } from 'node:path'

// Copy build output into repo root so GitHub Pages (configured to /) serves it.
const distDir = join(process.cwd(), 'dist')
const repoRoot = join(process.cwd(), '..')

if (!existsSync(distDir)) {
  console.error('dist/ not found. Run build first.')
  process.exit(1)
}

// Remove old assets folder and index.html in root (but keep other static pages like drummer-deals.html)
const oldAssets = join(repoRoot, 'assets')
if (existsSync(oldAssets)) rmSync(oldAssets, { recursive: true, force: true })

const newAssets = join(distDir, 'assets')
if (existsSync(newAssets)) {
  mkdirSync(oldAssets, { recursive: true })
}

// Copy index.html and assets/
cpSync(join(distDir, 'index.html'), join(repoRoot, 'index.html'))
cpSync(join(distDir, 'assets'), join(repoRoot, 'assets'), { recursive: true })

console.log('Copied build output to repo root.')
