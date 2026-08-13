# GLAW X402

GLAW X402 treats every local `SKILL.md` as a billable AI agent. It exposes:

- `GET /api/agents` - skill catalog as agents.
- `GET /api/matrix` - charge matrix grouped by domain and billing tier.
- `GET /api/services` - curated GLAW service packages.
- `GET /api/service-matrix` - service-based charge matrix.
- `POST /api/quote` - priced work quote for one agent.
- `POST /api/charges` - create a charge and receive an X402 pay URL.
- `GET|POST /api/pay/:chargeId` - X402 payment-required and settlement endpoint.
- `POST /mcp` - stateless MCP JSON-RPC endpoint with agent/matrix/quote/charge tools.
- `GET /.well-known/x402.json` - X402 discovery when payment mode is live.

## Run

```bash
npm run db:migrate:local
npm run dev
```

For the legacy Node smoke server:

```bash
npm run start:node
```

Live X402 settlement requires:

- `GLAW_X402_ENABLED=true`
- `GLAW_PAY_TO=<receiver EVM address>`
- `X402_FACILITATOR_URL=<facilitator base URL>`
- optional `X402_FACILITATOR_API_KEY`
- `X402_NETWORK=eip155:84532` for Base Sepolia or `eip155:8453` for Base mainnet
- `GLAW_ADMIN_BOOTSTRAP_TOKEN` for first admin API-client creation
- `WORK_AUTH_SECRET` for signed work authorization tokens

Set secrets with Wrangler:

```bash
npx wrangler secret put GLAW_ADMIN_BOOTSTRAP_TOKEN
npx wrangler secret put WORK_AUTH_SECRET
npx wrangler secret put GLAW_PAY_TO
npx wrangler secret put X402_FACILITATOR_URL
npx wrangler secret put X402_FACILITATOR_API_KEY
```

Without live X402 config, the API still quotes, creates pending charges, and exposes the matrix, but `/api/pay/:chargeId` returns `503 payments_unavailable` instead of advertising an un-settleable 402.

## Production Flow

1. Run the D1 migration.
2. Create an API client:

```bash
curl -s -X POST http://localhost:8787/api/admin/clients \
  -H 'Content-Type: application/json' \
  -H 'X-Admin-Token: change-me' \
  -d '{"name":"local","scopes":["quote:create","charge:create","charge:read","agent:read","mcp:call"]}'
```

3. Create a quote/charge with `Authorization: Bearer <key>:<secret>`.
4. Pay `/api/pay/:chargeId` with X402.
5. Call `/api/authorize-work` for a settled charge.
6. Call `/api/execute` or MCP `glaw_execute_paid_work` with the work authorization token.

The Worker advances Conway-style agent life daily via cron. Paid agents become alive immediately; unpaid agents survive or become dormant based on live service/domain neighbors.

To import every local skill as an agent into D1:

```bash
GLAW_X402_URL=http://localhost:8787 GLAW_ADMIN_BOOTSTRAP_TOKEN=change-me npm run catalog:import
```

To inspect the generated payload without importing:

```bash
npm run catalog:export
```

## Charge Model

The matrix is deterministic:

- Base tier comes from the skill family, for example tax, litigation, SEC, finance, accounting, investigation, Cloudflare, or utility.
- Risk multiplier comes from title/description terms such as audit, filing, court, regulatory, forensic, or valuation.
- Unit pricing supports `task`, `hour`, `page`, `document`, `filing`, `model`, and `review`.

Charges are quoted and settled in USDC atomic units for X402 exact payments.

## Service Matrix

The curated service matrix sits above the raw skill-agent matrix. Quote a service
by passing `serviceId` instead of `agentId`:

```bash
curl -s -X POST http://localhost:8742/api/quote \
  -H 'Content-Type: application/json' \
  -d '{"serviceId":"sec-tokenization-review","unit":"review","quantity":1,"complexity":"adversarial"}'
```

Service IDs include `entity-formation`, `tax-strategy-memo`,
`irs-controversy`, `contract-drafting`, `sec-tokenization-review`,
`litigation-motion`, `forensic-reconstruction`, `audit-readiness`,
`valuation-409a`, `fund-formation`, `privacy-compliance`, and
`general-counsel-retainer`.
