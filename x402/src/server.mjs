import http from 'node:http';
import { loadAgents } from './catalog.mjs';
import { buildMatrix, quoteWork } from './pricing.mjs';
import { buildServiceMatrix, findService, GLAW_SERVICES, quoteService } from './services.mjs';
import { createCharge, getCharge, listCharges, updateCharge } from './store.mjs';
import { readJson, sendJson, notFound } from './http.mjs';
import {
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
import { handleMcpMessage } from './mcp.mjs';

const PORT = Number(process.env.PORT || 8742);
const agents = await loadAgents();
const byId = new Map(agents.map((agent) => [agent.id, agent]));

function baseUrl(req) {
  return process.env.GLAW_SERVICE_BASE_URL || `http://${req.headers.host || `localhost:${PORT}`}`;
}

function chargeSummary(charge) {
  return {
    id: charge.id,
    status: charge.status,
    payUrl: charge.payUrl,
    quote: charge.quote,
    matterId: charge.matterId,
    memo: charge.memo,
    payment: charge.payment,
    createdAt: charge.createdAt,
    updatedAt: charge.updatedAt,
  };
}

async function handlePay(req, res, url) {
  const charge = getCharge(url.pathname.split('/').pop());
  if (!charge) return notFound(res);
  if (charge.status === 'settled') return sendJson(res, 200, { ok: true, paid: true, charge: chargeSummary(charge) });
  if (!isX402Live()) return sendJson(res, 503, { ok: false, error: 'payments_unavailable' });

  const resourceUrl = `${baseUrl(req)}${url.pathname}`;
  const requirements = buildRequirements({
    amount: charge.quote.atomicAmount,
    resourceUrl,
    description: `GLAW ${charge.quote.agent.id} charge ${charge.id}`,
  });
  const payload = readPaymentPayload(req);
  if (!payload) {
    const body = paymentRequiredBody({ requirements: [requirements], resourceUrl, description: `GLAW work charge ${charge.id}` });
    return sendJson(res, 402, body, { 'PAYMENT-REQUIRED': encodeJsonB64(body) });
  }

  const auth = extractAuthorization(payload);
  const localValid = validateAuthorization(auth, requirements);
  if (!localValid.ok) return sendJson(res, 402, { ok: false, error: 'invalid_authorization', reason: localValid.reason });

  updateCharge(charge.id, { status: 'verifying' });
  const verified = await verifyPayment(payload, requirements);
  if (!verified.isValid) {
    const failed = updateCharge(charge.id, {
      status: 'failed',
      payment: { invalidReason: verified.invalidReason, payer: verified.payer || auth.from || null },
    });
    return sendJson(res, 402, { ok: false, error: verified.invalidReason || 'invalid_payment', charge: chargeSummary(failed) });
  }

  updateCharge(charge.id, { status: 'verified' });
  const settled = await settlePayment(payload, requirements);
  if (!settled.success) {
    const failed = updateCharge(charge.id, {
      status: 'failed',
      payment: { invalidReason: settled.errorReason, payer: verified.payer || auth.from || null },
    });
    return sendJson(res, 402, { ok: false, error: settled.errorReason || 'settlement_failed', charge: chargeSummary(failed) });
  }

  const paid = updateCharge(charge.id, {
    status: 'settled',
    payment: {
      network: requirements.network,
      chainId: chainIdFromNetwork(requirements.network),
      asset: requirements.asset,
      payTo: requirements.payTo,
      payer: verified.payer || auth.from || null,
      tx: settled.transactionHash || null,
      settledAt: new Date().toISOString(),
    },
  });
  const paymentResponse = { success: true, transaction: settled.transactionHash, network: requirements.network, payer: paid.payment.payer, requirements };
  return sendJson(res, 200, { ok: true, paid: true, charge: chargeSummary(paid) }, { 'PAYMENT-RESPONSE': encodeJsonB64(paymentResponse) });
}

async function route(req, res) {
  const url = new URL(req.url, baseUrl(req));
  try {
    if (req.method === 'GET' && url.pathname === '/health') {
      return sendJson(res, 200, {
        ok: true,
        agents: agents.length,
        x402: { live: isX402Live(), network: x402Network(), asset: x402Asset(), payToConfigured: Boolean(process.env.GLAW_PAY_TO) },
      });
    }
    if (req.method === 'GET' && url.pathname === '/.well-known/x402.json') {
      if (!isX402Live()) return sendJson(res, 503, { ok: false, error: 'payments_unavailable' });
      return sendJson(res, 200, {
        x402Version: 2,
        name: 'GLAW X402',
        description: 'X402 payment settlement for GLAW skill-agents.',
        network: x402Network(),
        chainId: chainIdFromNetwork(x402Network()),
        asset: x402Asset(),
        payTemplate: '/api/pay/{chargeId}',
      });
    }
    if (req.method === 'GET' && url.pathname === '/api/agents') {
      const domain = url.searchParams.get('domain');
      return sendJson(res, 200, { ok: true, agents: domain ? agents.filter((a) => a.domain === domain) : agents });
    }
    if (req.method === 'GET' && url.pathname === '/api/matrix') {
      return sendJson(res, 200, { ok: true, matrix: buildMatrix(agents) });
    }
    if (req.method === 'GET' && url.pathname === '/api/services') {
      const category = url.searchParams.get('category');
      const services = category ? GLAW_SERVICES.filter((service) => service.category === category) : GLAW_SERVICES;
      return sendJson(res, 200, { ok: true, services });
    }
    if (req.method === 'GET' && url.pathname === '/api/service-matrix') {
      return sendJson(res, 200, { ok: true, matrix: buildServiceMatrix(agents) });
    }
    if (req.method === 'POST' && url.pathname === '/api/quote') {
      const body = await readJson(req);
      const quote = body?.serviceId
        ? quoteService(findService(body.serviceId), agents, body || {})
        : quoteWork(byId.get(body?.agentId), body || {});
      return sendJson(res, 200, { ok: true, quote });
    }
    if (req.method === 'POST' && url.pathname === '/api/charges') {
      const body = await readJson(req);
      const quote = body?.serviceId
        ? quoteService(findService(body.serviceId), agents, body || {})
        : quoteWork(byId.get(body?.agentId), body || {});
      const charge = createCharge({ quote, matterId: body?.matterId, memo: body?.memo, baseUrl: baseUrl(req) });
      return sendJson(res, 201, { ok: true, charge: chargeSummary(charge) });
    }
    if (req.method === 'GET' && url.pathname === '/api/charges') {
      return sendJson(res, 200, { ok: true, charges: listCharges().map(chargeSummary) });
    }
    if ((req.method === 'GET' || req.method === 'POST') && url.pathname.startsWith('/api/pay/')) {
      return handlePay(req, res, url);
    }
    if (req.method === 'POST' && url.pathname === '/mcp') {
      const body = await readJson(req);
      if (Array.isArray(body)) {
        const out = [];
        for (const msg of body) {
          const answer = await handleMcpMessage({ msg, agents, baseUrl: baseUrl(req) });
          if (answer) out.push(answer);
        }
        return out.length ? sendJson(res, 200, out) : res.writeHead(202).end();
      }
      const answer = await handleMcpMessage({ msg: body, agents, baseUrl: baseUrl(req) });
      return answer ? sendJson(res, 200, answer) : res.writeHead(202).end();
    }
    if ((req.method === 'GET' || req.method === 'DELETE') && url.pathname === '/mcp') {
      return sendJson(res, 405, { jsonrpc: '2.0', id: null, error: { code: -32601, message: 'Use POST /mcp for stateless JSON-RPC.' } });
    }
    return notFound(res);
  } catch (e) {
    const status = e.status || 500;
    return sendJson(res, status, { ok: false, error: e.message || 'internal_error' });
  }
}

const server = http.createServer(route);
server.listen(PORT, () => {
  console.log(`GLAW X402 listening on http://localhost:${PORT}`);
});
