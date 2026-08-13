export const X402_VERSION = 2;

const USDC = {
  'eip155:8453': { asset: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913', name: 'USD Coin', version: '2' },
  'eip155:84532': { asset: '0x036CbD53842c5426634e7929541eC2318f3dCF7e', name: 'USDC', version: '2' },
};

export function x402Network(env = process.env) {
  return (env.X402_NETWORK || 'eip155:84532').trim();
}

export function x402Asset(env = process.env, network = x402Network(env)) {
  return (env.X402_ASSET || USDC[network]?.asset || '').trim();
}

export function isX402Live(env = process.env) {
  return /^(1|true|yes|on)$/i.test(String(env.GLAW_X402_ENABLED || '')) &&
    Boolean(env.GLAW_PAY_TO && env.X402_FACILITATOR_URL && x402Asset(env));
}

export function chainIdFromNetwork(network) {
  const match = /^eip155:(\d+)$/.exec(String(network || ''));
  return match ? Number(match[1]) : null;
}

export function buildRequirements({ amount, resourceUrl, description }, env = process.env) {
  const network = x402Network(env);
  const token = USDC[network];
  return {
    scheme: 'exact',
    network,
    amount,
    asset: x402Asset(env, network),
    payTo: env.GLAW_PAY_TO,
    maxTimeoutSeconds: 300,
    extra: {
      ...(token ? { name: token.name, version: token.version } : {}),
      resourceUrl,
      description,
    },
  };
}

export function paymentRequiredBody({ requirements, resourceUrl, description }) {
  return {
    x402Version: X402_VERSION,
    error: 'PAYMENT-SIGNATURE header is required',
    resource: { url: resourceUrl, description, mimeType: 'application/json' },
    accepts: requirements,
  };
}

export function encodeJsonB64(value) {
  const bytes = new TextEncoder().encode(JSON.stringify(value));
  let bin = '';
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}

export function decodeJsonB64(value) {
  try {
    const bin = atob(String(value).trim());
    const bytes = Uint8Array.from(bin, (c) => c.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes));
  } catch {
    return null;
  }
}

export function readPaymentPayload(req) {
  const raw = typeof req.headers?.get === 'function'
    ? req.headers.get('payment-signature') || req.headers.get('x-payment')
    : req.headers?.['payment-signature'] || req.headers?.['x-payment'];
  return raw ? decodeJsonB64(Array.isArray(raw) ? raw[0] : raw) : null;
}

export function extractAuthorization(payload) {
  const auth = payload?.payload?.authorization ?? payload?.authorization ?? null;
  return auth && typeof auth === 'object' ? auth : null;
}

export function validateAuthorization(auth, requirements, nowSec = Math.floor(Date.now() / 1000)) {
  if (!auth) return { ok: false, reason: 'missing_authorization' };
  const eq = (a, b) => String(a || '').toLowerCase() === String(b || '').toLowerCase();
  if (!eq(auth.to, requirements.payTo)) return { ok: false, reason: 'recipient_mismatch' };
  if (String(auth.value ?? '') !== String(requirements.amount)) return { ok: false, reason: 'amount_mismatch' };
  if (!auth.nonce) return { ok: false, reason: 'missing_nonce' };
  const before = auth.validBefore == null ? null : Number(auth.validBefore);
  const after = auth.validAfter == null ? null : Number(auth.validAfter);
  if (before != null && Number.isFinite(before) && before <= nowSec) return { ok: false, reason: 'authorization_expired' };
  if (after != null && Number.isFinite(after) && after > nowSec) return { ok: false, reason: 'authorization_not_yet_valid' };
  return { ok: true };
}

export async function authorizationHash(auth, requirements) {
  const canon = JSON.stringify({
    network: requirements.network,
    asset: String(requirements.asset || '').toLowerCase(),
    from: String(auth?.from || '').toLowerCase(),
    to: String(auth?.to || '').toLowerCase(),
    value: String(auth?.value ?? ''),
    nonce: String(auth?.nonce ?? ''),
  });
  const bytes = new TextEncoder().encode(canon);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

async function facilitatorPost(path, body, env = process.env) {
  const base = env.X402_FACILITATOR_URL?.replace(/\/+$/, '');
  if (!base) return null;
  const headers = { 'Content-Type': 'application/json' };
  if (env.X402_FACILITATOR_API_KEY) headers.Authorization = `Bearer ${env.X402_FACILITATOR_API_KEY}`;
  const res = await fetch(`${base}${path}`, { method: 'POST', headers, body: JSON.stringify(body) });
  const text = await res.text();
  const data = text ? JSON.parse(text) : {};
  return res.ok ? data : { ...data, _httpError: `HTTP ${res.status}` };
}

export async function verifyPayment(payload, requirements, env = process.env) {
  const data = await facilitatorPost('/verify', { paymentPayload: payload, paymentRequirements: requirements }, env);
  if (!data) return { isValid: false, invalidReason: 'facilitator_unreachable' };
  return { isValid: Boolean(data.isValid), payer: data.payer, invalidReason: data.invalidReason || data._httpError, raw: data };
}

export async function settlePayment(payload, requirements, env = process.env) {
  const data = await facilitatorPost('/settle', { paymentPayload: payload, paymentRequirements: requirements }, env);
  if (!data) return { success: false, errorReason: 'facilitator_unreachable' };
  const tx = data.transactionHash || data.transaction || data.txHash;
  const success = data.success === true || data.status === 'settled' || Boolean(tx);
  return { success, transactionHash: tx, status: data.status, errorReason: success ? undefined : data.errorReason || data.invalidReason || data._httpError, raw: data };
}
