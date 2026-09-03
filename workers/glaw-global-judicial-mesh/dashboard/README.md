# GLAW Judicial Mesh Dashboard

Astro static operations dashboard for the Worker API.

```sh
npm install
PUBLIC_GLAW_API_BASE_URL=http://localhost:8787 npm run dev
```

The API token field stores a token only in browser session storage. Do not bake production API or admin keys into the dashboard build. In production, place the dashboard behind Cloudflare Access or an authenticated reverse proxy.
