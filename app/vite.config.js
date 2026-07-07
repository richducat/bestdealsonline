import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { createReadStream, existsSync } from 'node:fs'
import { extname, join } from 'node:path'

const CONTENT_TYPES = {
  '.json': 'application/json',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
}

// In production the whole repo root (data/, images/, etc.) is served as
// static assets by Cloudflare, so absolute paths like /data/products.json
// or /images/categories/kitchen.webp resolve with zero build step. This
// dev-only middleware mirrors that locally, where the Vite root is app/
// (one level below the repo root) -- it serves those same repo-root
// directories instead of duplicating the files into app/public.
const REPO_ROOT_DIRS = ['/data/', '/images/']

function serveRepoRootAssets() {
  return {
    name: 'serve-repo-root-assets',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = req.url ?? ''
        if (!REPO_ROOT_DIRS.some((prefix) => url.startsWith(prefix))) return next()
        const filePath = join(process.cwd(), '..', url.split('?')[0])
        if (!existsSync(filePath)) return next()
        const contentType = CONTENT_TYPES[extname(filePath)]
        if (contentType) res.setHeader('Content-Type', contentType)
        createReadStream(filePath).pipe(res)
      })
    },
  }
}

// Relative base so the build works on GitHub Pages + custom domain.
export default defineConfig({
  base: './',
  plugins: [react(), serveRepoRootAssets()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
