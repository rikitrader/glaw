import { randomId, randomSecret, sha256hex } from './crypto.mjs';

export const SCOPES = {
  QUOTE_CREATE: 'quote:create',
  CHARGE_CREATE: 'charge:create',
  CHARGE_READ: 'charge:read',
  AGENT_READ: 'agent:read',
  MCP_CALL: 'mcp:call',
  ADMIN: 'admin:*',
};

function parseCredential(request) {
  const auth = request.headers.get('authorization') || '';
  if (auth.toLowerCase().startsWith('bearer ')) {
    const [key, secret] = auth.slice(7).trim().split(':');
    if (key && secret) return { key, secret };
  }
  const key = request.headers.get('x-api-key');
  const secret = request.headers.get('x-api-secret');
  return key && secret ? { key, secret } : null;
}

function hasScope(client, requiredScope) {
  if (!requiredScope) return true;
  const scopes = String(client.scopes || '').split(/[,\s]+/).filter(Boolean);
  return scopes.includes(SCOPES.ADMIN) || scopes.includes(requiredScope);
}

export async function authenticate(env, request, requiredScope) {
  const cred = parseCredential(request);
  if (!cred) return { ok: false, status: 401, error: 'missing_api_credentials' };
  const keyHash = await sha256hex(cred.key);
  const client = await env.DB.prepare(
    `SELECT * FROM api_clients WHERE key_hash = ? AND status = 'active'`
  ).bind(keyHash).first();
  if (!client) return { ok: false, status: 401, error: 'invalid_api_key' };
  const secretHash = await sha256hex(cred.secret);
  if (secretHash !== client.secret_hash) return { ok: false, status: 401, error: 'invalid_api_secret' };
  if (!hasScope(client, requiredScope)) return { ok: false, status: 403, error: 'scope_required', requiredScope };
  await env.DB.prepare(`UPDATE api_clients SET last_used_ms = ? WHERE id = ?`).bind(Date.now(), client.id).run();
  return { ok: true, client };
}

export async function requireAdmin(env, request) {
  const token = request.headers.get('x-admin-token');
  if (env.GLAW_ADMIN_BOOTSTRAP_TOKEN && token === env.GLAW_ADMIN_BOOTSTRAP_TOKEN) {
    return { ok: true, client: { id: 'bootstrap-admin', scopes: SCOPES.ADMIN } };
  }
  return authenticate(env, request, SCOPES.ADMIN);
}

export async function createApiClient(env, { name, scopes }) {
  const key = randomSecret('glawk');
  const secret = randomSecret('glaws');
  const now = Date.now();
  const row = {
    id: randomId('cli'),
    name: name || 'GLAW API Client',
    scopes: Array.isArray(scopes) && scopes.length ? scopes.join(' ') : `${SCOPES.QUOTE_CREATE} ${SCOPES.CHARGE_CREATE} ${SCOPES.CHARGE_READ} ${SCOPES.AGENT_READ} ${SCOPES.MCP_CALL}`,
  };
  await env.DB.prepare(
    `INSERT INTO api_clients (id, name, key_hash, secret_hash, scopes, status, created_ms)
     VALUES (?, ?, ?, ?, ?, 'active', ?)`
  ).bind(row.id, row.name, await sha256hex(key), await sha256hex(secret), row.scopes, now).run();
  return { ...row, key, secret, status: 'active', created_ms: now };
}
