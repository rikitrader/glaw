import { buildMatrix, quoteWork } from './pricing.mjs';
import { buildServiceMatrix, findService, GLAW_SERVICES, quoteService } from './services.mjs';
import { authenticate, createApiClient, requireAdmin, SCOPES } from './auth.mjs';
import { randomId, sha256hex, signWorkToken, verifyWorkToken } from './crypto.mjs';
import { grantPaidLife, tickLife, ensureLifeRows } from './life.mjs';
import {
  authorizationHash,
  buildRequirements,
  chainIdFromNetwork,
  encodeJsonB64,
  extractAuthorization,
  isX402Live,
  paymentRequiredBody,
  readPaymentPayload,
  settlePayment,
  validateAuthorization,
  verifyPayment,
  x402Asset,
  x402Network,
} from './x402.mjs';

function json(body, status = 200, headers = {}) {
  return Response.json(body, {
    status,
    headers: { 'Cache-Control': 'no-store', ...headers },
  });
}

async function readJson(request) {
  if (!request.body) return null;
  try {
    return await request.json();
  } catch {
    const err = new Error('invalid_json');
    err.status = 400;
    throw err;
  }
}

function baseUrl(request, env) {
  return env.GLAW_SERVICE_BASE_URL || new URL(request.url).origin;
}

function serviceAgentIds(service) {
  return service?.defaultAgentIds || [];
}

async function seedCatalog(env) {
  const now = Date.now();
  for (const service of GLAW_SERVICES) {
    await env.DB.prepare(
      `INSERT OR IGNORE INTO service_catalog
       (id, name, category, description, default_unit, risk_tier, active, created_ms, updated_ms)
       VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)`
    ).bind(service.id, service.name, service.category, service.description, service.unit, service.riskTier, now, now).run();
    const seededAgents = serviceAgentIds(service);
    for (const agentId of seededAgents) {
      await env.DB.prepare(
        `INSERT OR IGNORE INTO agent_catalog
         (id, name, domain, path, description, description_hash, active, created_ms, updated_ms)
         VALUES (?, ?, ?, NULL, ?, ?, 1, ?, ?)`
      ).bind(agentId, agentId, service.category, `Seeded from ${service.id}`, await sha256hex(`${service.id}:${agentId}`), now, now).run();
    }
    const matrix = buildServiceMatrix(seededAgents.map((id) => ({ id, name: id, domain: service.category, description: '' })));
    const row = matrix.rows.find((r) => r.id === service.id);
    await env.DB.prepare(
      `INSERT OR IGNORE INTO service_prices
       (id, service_id, version, base_usd, minimum_usd, list_usd, unit_rates_json, created_ms)
       VALUES (?, ?, 1, ?, ?, ?, ?, ?)`
    ).bind(randomId('spx'), service.id, service.baseUsd, service.minimumUsd, row?.listUsd || service.baseUsd, JSON.stringify(row?.unitRates || {}), now).run();
  }
  const agentIds = GLAW_SERVICES.flatMap(serviceAgentIds);
  await ensureLifeRows(env, agentIds);
  await seedEdges(env);
}

async function seedEdges(env) {
  for (const service of GLAW_SERVICES) {
    const ids = serviceAgentIds(service);
    for (const a of ids) {
      for (const b of ids) {
        if (a === b) continue;
        await env.DB.prepare(`INSERT OR IGNORE INTO agent_edges (a, b, reason) VALUES (?, ?, ?)`)
          .bind(a, b, `service:${service.id}`).run();
      }
    }
  }
}

async function agentsFromDb(env) {
  await seedCatalog(env);
  const rows = (await env.DB.prepare(
    `SELECT id, name, domain, path, description FROM agent_catalog WHERE active = 1 ORDER BY id`
  ).all()).results || [];
  return rows.map((r) => ({
    id: r.id,
    name: r.name,
    domain: r.domain,
    path: r.path,
    description: r.description || '',
  }));
}

async function createQuote(env, body) {
  const agents = await agentsFromDb(env);
  if (body?.serviceId) return quoteService(findService(body.serviceId), agents, body);
  const byId = new Map(agents.map((agent) => [agent.id, agent]));
  return quoteWork(byId.get(body?.agentId), body || {});
}

async function createCharge(env, request, client, body) {
  const idem = request.headers.get('idempotency-key') || body?.idempotencyKey || null;
  if (idem && client?.id) {
    const existing = await env.DB.prepare(
      `SELECT * FROM charges WHERE client_id = ? AND idempotency_key = ?`
    ).bind(client.id, idem).first();
    if (existing) return existing;
  }
  const quote = await createQuote(env, body);
  const id = randomId('glaw');
  const now = Date.now();
  const payUrl = `${baseUrl(request, env).replace(/\/+$/, '')}/api/pay/${id}`;
  await env.DB.prepare(
    `INSERT INTO charges
     (id, client_id, quote_id, quote_json, service_id, agent_id, matter_id, memo, status, amount_usd,
      amount_atomic, currency, pay_url, idempotency_key, created_ms, updated_ms)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'created', ?, ?, 'USDC', ?, ?, ?, ?)`
  ).bind(
    id,
    client?.id || null,
    quote.quoteId,
    JSON.stringify(quote),
    quote.service?.id || null,
    quote.agent?.id || null,
    body?.matterId || null,
    body?.memo || null,
    quote.totalUsd,
    quote.atomicAmount,
    payUrl,
    idem,
    now,
    now,
  ).run();
  return env.DB.prepare(`SELECT * FROM charges WHERE id = ?`).bind(id).first();
}

function chargeOut(row) {
  if (!row) return null;
  let quote = null;
  try { quote = JSON.parse(row.quote_json); } catch {}
  return {
    id: row.id,
    status: row.status,
    payUrl: row.pay_url,
    quote,
    matterId: row.matter_id,
    memo: row.memo,
    createdAt: new Date(row.created_ms).toISOString(),
    updatedAt: new Date(row.updated_ms).toISOString(),
  };
}

function paymentOut(row) {
  if (!row) return null;
  return {
    id: row.id,
    chargeId: row.charge_id,
    status: row.status,
    network: row.network,
    chainId: row.chain_id,
    asset: row.asset,
    amountUsd: row.amount_usd,
    amountAtomic: row.amount_atomic,
    payTo: row.pay_to,
    payer: row.payer,
    tx: row.tx_hash,
    invalidReason: row.invalid_reason,
  };
}

function sigOf(payload) {
  return String(payload?.payload?.signature || payload?.signature || '');
}

async function handlePay(env, request, chargeId) {
  const charge = await env.DB.prepare(`SELECT * FROM charges WHERE id = ?`).bind(chargeId).first();
  if (!charge) return json({ ok: false, error: 'not_found' }, 404);
  const settledPayment = await env.DB.prepare(
    `SELECT * FROM payments WHERE charge_id = ? AND status = 'settled' ORDER BY settled_ms DESC LIMIT 1`
  ).bind(chargeId).first();
  if (settledPayment) {
    return json({ ok: true, paid: true, charge: chargeOut(charge), payment: paymentOut(settledPayment) });
  }
  if (!isX402Live(env)) return json({ ok: false, error: 'payments_unavailable' }, 503);

  const quote = JSON.parse(charge.quote_json);
  const resourceUrl = `${baseUrl(request, env)}${new URL(request.url).pathname}`;
  const requirements = buildRequirements({
    amount: charge.amount_atomic,
    resourceUrl,
    description: `GLAW ${quote.service?.id || quote.agent?.id} charge ${charge.id}`,
  }, env);

  const payload = readPaymentPayload(request);
  if (!payload) {
    const body = paymentRequiredBody({ requirements: [requirements], resourceUrl, description: `GLAW work charge ${charge.id}` });
    return json(body, 402, { 'PAYMENT-REQUIRED': encodeJsonB64(body) });
  }

  const auth = extractAuthorization(payload);
  const valid = validateAuthorization(auth, requirements);
  if (!valid.ok) return json({ ok: false, error: 'invalid_authorization', reason: valid.reason }, 402);
  const authHash = await authorizationHash(auth, requirements);
  const idem = request.headers.get('idempotency-key') || null;
  const existing = await env.DB.prepare(
    `SELECT * FROM payments WHERE authorization_hash = ? OR (idempotency_key IS NOT NULL AND idempotency_key = ? AND charge_id = ?) LIMIT 1`
  ).bind(authHash, idem, chargeId).first();
  if (existing?.status === 'settled') {
    if (sigOf(payload) && sigOf(payload) === sigOf(JSON.parse(existing.payload_json || '{}'))) {
      return json({ ok: true, paid: true, idempotent: true, charge: chargeOut(charge), payment: paymentOut(existing) }, 200, {
        'PAYMENT-RESPONSE': encodeJsonB64({ success: true, transaction: existing.tx_hash, network: existing.network, payer: existing.payer }),
      });
    }
    return json({ ok: false, error: 'authorization_already_used' }, 409);
  }

  const paymentId = existing?.id || randomId('pay');
  const now = Date.now();
  if (!existing) {
    await env.DB.prepare(
      `INSERT INTO payments
       (id, charge_id, status, scheme, network, chain_id, asset, amount_atomic, amount_usd, pay_to, payer,
        authorization_hash, payload_json, idempotency_key, created_ms)
       VALUES (?, ?, 'required', 'exact', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(paymentId, chargeId, requirements.network, chainIdFromNetwork(requirements.network), requirements.asset,
      requirements.amount, charge.amount_usd, requirements.payTo, auth.from || null, authHash, JSON.stringify(payload), idem, now).run();
  }

  const verified = await verifyPayment(payload, requirements, env);
  if (!verified.isValid) {
    await env.DB.prepare(
      `UPDATE payments SET status = 'failed', payer = ?, invalid_reason = ?, facilitator_response = ? WHERE id = ?`
    ).bind(verified.payer || auth.from || null, verified.invalidReason || 'invalid_payment', JSON.stringify({ verify: verified.raw }), paymentId).run();
    return json({ ok: false, error: verified.invalidReason || 'invalid_payment' }, 402);
  }
  await env.DB.prepare(`UPDATE payments SET status = 'verified', payer = ?, verified_ms = ? WHERE id = ?`)
    .bind(verified.payer || auth.from || null, Date.now(), paymentId).run();

  const settled = await settlePayment(payload, requirements, env);
  if (!settled.success) {
    await env.DB.prepare(
      `UPDATE payments SET status = 'failed', invalid_reason = ?, facilitator_response = ? WHERE id = ?`
    ).bind(settled.errorReason || 'settlement_failed', JSON.stringify({ verify: verified.raw, settle: settled.raw }), paymentId).run();
    return json({ ok: false, error: settled.errorReason || 'settlement_failed' }, 402);
  }

  await env.DB.prepare(
    `UPDATE payments SET status = 'settled', tx_hash = ?, settled_ms = ?, facilitator_response = ? WHERE id = ?`
  ).bind(settled.transactionHash || null, Date.now(), JSON.stringify({ verify: verified.raw, settle: settled.raw }), paymentId).run();
  await env.DB.prepare(`UPDATE charges SET status = 'settled', updated_ms = ? WHERE id = ?`).bind(Date.now(), chargeId).run();
  await grantPaidLife(env, chargeId, quote.agents || [quote.agent?.id], charge.amount_usd);

  const paid = await env.DB.prepare(`SELECT * FROM payments WHERE id = ?`).bind(paymentId).first();
  return json({ ok: true, paid: true, charge: chargeOut({ ...charge, status: 'settled', updated_ms: Date.now() }), payment: paymentOut(paid) }, 200, {
    'PAYMENT-RESPONSE': encodeJsonB64({ success: true, transaction: settled.transactionHash, network: requirements.network, payer: verified.payer, requirements }),
  });
}

async function authorizeWork(env, request, client) {
  const body = await readJson(request);
  const charge = await env.DB.prepare(`SELECT * FROM charges WHERE id = ? AND status = 'settled'`).bind(body?.chargeId).first();
  if (!charge) return json({ ok: false, error: 'settled_charge_required' }, 402);
  const quote = JSON.parse(charge.quote_json);
  const agents = quote.agents || [quote.agent?.id].filter(Boolean);
  const lifeRows = (await env.DB.prepare(
    `SELECT agent_id, state FROM agent_life WHERE agent_id IN (${agents.map(() => '?').join(',')})`
  ).bind(...agents).all()).results || [];
  const dead = lifeRows.filter((r) => r.state !== 'alive').map((r) => r.agent_id);
  if (dead.length) return json({ ok: false, error: 'agent_not_alive', deadAgents: dead, charge: chargeOut(charge) }, 402);
  const now = Date.now();
  const ttl = Math.max(60, Number(env.WORK_AUTH_TTL_SECONDS || 86400));
  const auth = { id: randomId('wa'), charge_id: charge.id, client_id: client?.id || null, agents, expires_ms: now + ttl * 1000 };
  const token = await signWorkToken(auth, env.WORK_AUTH_SECRET || env.GLAW_ADMIN_BOOTSTRAP_TOKEN || 'dev-only-work-auth-secret');
  await env.DB.prepare(
    `INSERT OR REPLACE INTO work_authorizations
     (id, charge_id, client_id, authorized_agents_json, token_hash, expires_ms, created_ms)
     VALUES (?, ?, ?, ?, ?, ?, ?)`
  ).bind(auth.id, charge.id, client?.id || null, JSON.stringify(agents), await sha256hex(token), auth.expires_ms, now).run();
  return json({ ok: true, authorization: { ...auth, token } });
}

async function executePaidWork(env, request) {
  const body = await readJson(request);
  const token = body?.authorizationToken || request.headers.get('x-work-authorization');
  const payload = await verifyWorkToken(token, env.WORK_AUTH_SECRET || env.GLAW_ADMIN_BOOTSTRAP_TOKEN || 'dev-only-work-auth-secret');
  if (!payload) return json({ ok: false, error: 'invalid_work_authorization' }, 401);
  if (body?.agentId && !payload.agents.includes(body.agentId)) return json({ ok: false, error: 'agent_not_authorized' }, 403);
  const agentId = body?.agentId || payload.agents[0];
  const life = await env.DB.prepare(`SELECT * FROM agent_life WHERE agent_id = ?`).bind(agentId).first();
  if (!life || life.state !== 'alive') return json({ ok: false, error: 'agent_not_alive', agentId }, 402);
  await env.DB.prepare(`UPDATE work_authorizations SET consumed_ms = COALESCE(consumed_ms, ?) WHERE id = ?`).bind(Date.now(), payload.id).run();
  return json({
    ok: true,
    execution: {
      status: 'authorized',
      agentId,
      chargeId: payload.charge_id,
      concept: 'Conway paid-life gate: this agent survives because settled work kept it alive.',
      input: body?.input || null,
    },
  });
}

async function handleMcp(env, request) {
  const body = await readJson(request);
  const processOne = async (msg) => {
    const id = msg?.id ?? null;
    if (!msg || msg.jsonrpc !== '2.0') return { jsonrpc: '2.0', id, error: { code: -32600, message: 'Invalid Request' } };
    if (msg.id === undefined) return null;
    if (msg.method === 'initialize') return { jsonrpc: '2.0', id, result: { protocolVersion: '2026-07-28', capabilities: { tools: { listChanged: false } }, serverInfo: { name: 'glaw-x402', version: '0.2.0' } } };
    if (msg.method === 'ping') return { jsonrpc: '2.0', id, result: {} };
    const auth = await authenticate(env, request, SCOPES.MCP_CALL);
    if (!auth.ok) return { jsonrpc: '2.0', id, error: { code: -32001, message: auth.error, data: { status: auth.status } } };
    if (msg.method === 'tools/list') {
      return { jsonrpc: '2.0', id, result: { tools: [
        { name: 'glaw_charge_matrix', description: 'Return agent/service matrix.', inputSchema: { type: 'object', properties: { mode: { type: 'string' } } } },
        { name: 'glaw_quote_work', description: 'Quote GLAW work by agentId or serviceId.', inputSchema: { type: 'object', properties: { agentId: { type: 'string' }, serviceId: { type: 'string' } } } },
        { name: 'glaw_create_charge', description: 'Create an X402 charge.', inputSchema: { type: 'object', properties: { agentId: { type: 'string' }, serviceId: { type: 'string' } } } },
        { name: 'glaw_authorize_work', description: 'Issue work authorization for a settled charge.', inputSchema: { type: 'object', properties: { chargeId: { type: 'string' } }, required: ['chargeId'] } },
        { name: 'glaw_agent_life', description: 'Inspect agent life state.', inputSchema: { type: 'object', properties: { agentId: { type: 'string' } } } },
        { name: 'glaw_execute_paid_work', description: 'Authorize paid GLAW work execution.', inputSchema: { type: 'object', properties: { authorizationToken: { type: 'string' }, agentId: { type: 'string' } } } },
      ] } };
    }
    if (msg.method !== 'tools/call') return { jsonrpc: '2.0', id, error: { code: -32601, message: `Method not found: ${msg.method}` } };
    const args = msg.params?.arguments || {};
    const name = msg.params?.name;
    let data;
    if (name === 'glaw_charge_matrix') {
      const agents = await agentsFromDb(env);
      data = args.mode === 'agents' ? buildMatrix(agents) : args.mode === 'combined' ? { agents: buildMatrix(agents), services: buildServiceMatrix(agents) } : buildServiceMatrix(agents);
    } else if (name === 'glaw_quote_work') {
      data = await createQuote(env, args);
    } else if (name === 'glaw_create_charge') {
      data = chargeOut(await createCharge(env, request, auth.client, args));
    } else if (name === 'glaw_authorize_work') {
      const fakeReq = new Request(request.url, { method: 'POST', body: JSON.stringify(args), headers: request.headers });
      data = await (await authorizeWork(env, fakeReq, auth.client)).json();
    } else if (name === 'glaw_agent_life') {
      data = await lifeState(env, args.agentId);
    } else if (name === 'glaw_execute_paid_work') {
      const fakeReq = new Request(request.url, { method: 'POST', body: JSON.stringify(args), headers: request.headers });
      data = await (await executePaidWork(env, fakeReq)).json();
    } else {
      return { jsonrpc: '2.0', id, error: { code: -32601, message: `Unknown tool: ${name}` } };
    }
    return { jsonrpc: '2.0', id, result: { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }], structuredContent: data, isError: false } };
  };
  if (Array.isArray(body)) {
    const out = [];
    for (const msg of body) {
      const result = await processOne(msg);
      if (result) out.push(result);
    }
    return out.length ? json(out) : new Response(null, { status: 202 });
  }
  const result = await processOne(body);
  return result ? json(result) : new Response(null, { status: 202 });
}

async function lifeState(env, agentId) {
  await seedCatalog(env);
  if (agentId) {
    const row = await env.DB.prepare(`SELECT * FROM agent_life WHERE agent_id = ?`).bind(agentId).first();
    const edges = (await env.DB.prepare(`SELECT b, reason FROM agent_edges WHERE a = ? ORDER BY b`).bind(agentId).all()).results || [];
    return { agent: row, neighbors: edges };
  }
  const rows = (await env.DB.prepare(`SELECT * FROM agent_life ORDER BY state, energy DESC, agent_id`).all()).results || [];
  return { agents: rows };
}

async function importCatalog(env, request) {
  const body = await readJson(request);
  const agents = Array.isArray(body?.agents) ? body.agents : [];
  const now = Date.now();
  for (const agent of agents) {
    await env.DB.prepare(
      `INSERT INTO agent_catalog (id, name, domain, path, description, description_hash, active, created_ms, updated_ms)
       VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
       ON CONFLICT(id) DO UPDATE SET name = excluded.name, domain = excluded.domain, path = excluded.path,
       description = excluded.description, description_hash = excluded.description_hash, active = 1, updated_ms = excluded.updated_ms`
    ).bind(agent.id, agent.name || agent.id, agent.domain || 'general', agent.path || null, agent.description || '', await sha256hex(agent.description || ''), now, now).run();
  }
  await ensureLifeRows(env, agents.map((a) => a.id));
  await seedEdges(env);
  return json({ ok: true, imported: agents.length });
}

async function route(request, env, ctx) {
  const url = new URL(request.url);
  await seedCatalog(env);

  if (request.method === 'GET' && url.pathname === '/health') {
    return json({ ok: true, x402: { live: isX402Live(env), network: x402Network(env), asset: x402Asset(env), payToConfigured: Boolean(env.GLAW_PAY_TO) } });
  }
  if (request.method === 'GET' && url.pathname === '/.well-known/x402.json') {
    if (!isX402Live(env)) return json({ ok: false, error: 'payments_unavailable' }, 503);
    return json({ x402Version: 2, name: 'GLAW X402', network: x402Network(env), chainId: chainIdFromNetwork(x402Network(env)), asset: x402Asset(env), payTemplate: '/api/pay/{chargeId}' });
  }
  if (request.method === 'GET' && url.pathname === '/api/agents') {
    const agents = await agentsFromDb(env);
    const domain = url.searchParams.get('domain');
    return json({ ok: true, agents: domain ? agents.filter((a) => a.domain === domain) : agents });
  }
  if (request.method === 'GET' && url.pathname === '/api/services') {
    const category = url.searchParams.get('category');
    return json({ ok: true, services: category ? GLAW_SERVICES.filter((s) => s.category === category) : GLAW_SERVICES });
  }
  if (request.method === 'GET' && url.pathname === '/api/matrix') {
    const agents = await agentsFromDb(env);
    const mode = url.searchParams.get('mode') || 'combined';
    return json({ ok: true, matrix: mode === 'agents' ? buildMatrix(agents) : mode === 'services' ? buildServiceMatrix(agents) : { agents: buildMatrix(agents), services: buildServiceMatrix(agents) } });
  }
  if (request.method === 'GET' && url.pathname === '/api/life') return json({ ok: true, life: await lifeState(env) });
  if (request.method === 'GET' && url.pathname.startsWith('/api/life/')) return json({ ok: true, life: await lifeState(env, decodeURIComponent(url.pathname.split('/').pop())) });

  if (request.method === 'POST' && url.pathname === '/api/admin/clients') {
    const admin = await requireAdmin(env, request);
    if (!admin.ok) return json({ ok: false, error: admin.error }, admin.status);
    return json({ ok: true, client: await createApiClient(env, await readJson(request) || {}) }, 201);
  }
  if (request.method === 'POST' && url.pathname === '/api/admin/catalog/import') {
    const admin = await requireAdmin(env, request);
    if (!admin.ok) return json({ ok: false, error: admin.error }, admin.status);
    return importCatalog(env, request);
  }
  if (request.method === 'POST' && url.pathname === '/api/admin/life/tick') {
    const admin = await requireAdmin(env, request);
    if (!admin.ok) return json({ ok: false, error: admin.error }, admin.status);
    return json({ ok: true, tick: await tickLife(env) });
  }
  if (request.method === 'POST' && url.pathname === '/api/quote') {
    const auth = await authenticate(env, request, SCOPES.QUOTE_CREATE);
    if (!auth.ok) return json({ ok: false, error: auth.error }, auth.status);
    return json({ ok: true, quote: await createQuote(env, await readJson(request) || {}) });
  }
  if (request.method === 'POST' && url.pathname === '/api/charges') {
    const auth = await authenticate(env, request, SCOPES.CHARGE_CREATE);
    if (!auth.ok) return json({ ok: false, error: auth.error }, auth.status);
    return json({ ok: true, charge: chargeOut(await createCharge(env, request, auth.client, await readJson(request) || {})) }, 201);
  }
  if (request.method === 'GET' && url.pathname.startsWith('/api/charges/')) {
    const auth = await authenticate(env, request, SCOPES.CHARGE_READ);
    if (!auth.ok) return json({ ok: false, error: auth.error }, auth.status);
    const row = await env.DB.prepare(`SELECT * FROM charges WHERE id = ?`).bind(url.pathname.split('/').pop()).first();
    return row ? json({ ok: true, charge: chargeOut(row) }) : json({ ok: false, error: 'not_found' }, 404);
  }
  if ((request.method === 'GET' || request.method === 'POST') && url.pathname.startsWith('/api/pay/')) {
    return handlePay(env, request, url.pathname.split('/').pop());
  }
  if (request.method === 'POST' && url.pathname === '/api/authorize-work') {
    const auth = await authenticate(env, request, SCOPES.CHARGE_READ);
    if (!auth.ok) return json({ ok: false, error: auth.error }, auth.status);
    return authorizeWork(env, request, auth.client);
  }
  if (request.method === 'POST' && url.pathname === '/api/execute') return executePaidWork(env, request);
  if (request.method === 'POST' && url.pathname === '/mcp') return handleMcp(env, request);
  return json({ ok: false, error: 'not_found' }, 404);
}

export default {
  async fetch(request, env, ctx) {
    try {
      return await route(request, env, ctx);
    } catch (e) {
      console.error(JSON.stringify({ level: 'error', message: e?.message || String(e) }));
      return json({ ok: false, error: e?.message || 'internal_error' }, e?.status || 500);
    }
  },
  async scheduled(controller, env, ctx) {
    ctx.waitUntil(tickLife(env));
  },
};
