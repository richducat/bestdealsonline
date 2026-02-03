// Cloudflare Worker skeleton for Amazon PA-API.
// NOTE: Signing requests for PA-API requires AWS Signature V4.
// We'll implement signing once you confirm where you want to deploy (Cloudflare Worker) and provide PA-API creds.

export default {
  async fetch(request, env) {
    const url = new URL(request.url)

    if (url.pathname === '/health') {
      return new Response(JSON.stringify({ ok: true }), {
        headers: { 'content-type': 'application/json' },
      })
    }

    if (url.pathname === '/v1/deals') {
      // Placeholder until PA-API signing is wired.
      return new Response(
        JSON.stringify({
          items: [],
          error: 'PA-API not configured yet. Set env vars and enable SigV4 signing implementation.',
        }),
        { headers: { 'content-type': 'application/json', 'access-control-allow-origin': '*' } }
      )
    }

    return new Response('Not found', { status: 404 })
  },
}
