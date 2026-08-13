# GLAW X402 Deployment Placeholder

Created: 2026-08-13

## Current Status

Deployment was paused before publishing. The Worker implementation builds and dry-runs, but production deployment still needs Cloudflare resource binding and secrets.

Verified locally:

- `npm test` passes with 12 tests.
- `npx wrangler deploy --dry-run` passes.
- Local D1 migration applies successfully.
- Wrangler login is available for account `rikitrader@gmail.com`.
- Local catalog export sees 229 skill-agents.

## Check Before Deploy

1. Create or identify the production D1 database.
2. Replace `database_id` in `wrangler.jsonc`; it is currently `REPLACE_WITH_D1_DATABASE_ID`.
3. Set required Worker secrets:
   - `GLAW_ADMIN_BOOTSTRAP_TOKEN`
   - `WORK_AUTH_SECRET`
   - `GLAW_PAY_TO`
   - `X402_FACILITATOR_URL`
   - `X402_FACILITATOR_API_KEY` if the facilitator requires it
4. Decide whether `GLAW_X402_ENABLED` should remain `false` for first deploy or be switched to `true`.
5. Run remote D1 migration:
   - `npm run db:migrate:remote`
6. Deploy:
   - `npm run deploy`
7. Import local skills into production D1:
   - `GLAW_X402_URL=<deployed-url> GLAW_ADMIN_BOOTSTRAP_TOKEN=<token> npm run catalog:import`
8. Create first API client:
   - `POST /api/admin/clients` with `X-Admin-Token`
9. Smoke-test:
   - `GET /health`
   - `GET /api/matrix?mode=combined`
   - `GET /api/life`
   - authenticated `POST /api/quote`
   - authenticated `POST /api/charges`
   - `GET /.well-known/x402.json` only if live payments are enabled

## Notes

- Shell environment variables do not automatically become Worker bindings. Use `wrangler secret put` or `.dev.vars` for local Worker dev.
- The Worker seeds curated service agents automatically, but the full 229-agent local skill catalog requires `catalog:import`.
- Payment-gated execution depends on settled charges and signed work authorization tokens.
