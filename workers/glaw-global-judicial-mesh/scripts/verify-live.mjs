const baseUrl = (process.env.GLAW_LIVE_BASE_URL ?? '').replace(/\/$/, '');
const apiKey = process.env.GLAW_LIVE_API_KEY ?? '';
const tenantId = process.env.GLAW_LIVE_TENANT_ID ?? '';
const otherTenantId = process.env.GLAW_LIVE_OTHER_TENANT_ID ?? 'glaw-isolation-probe-other-tenant';

if (!baseUrl || !apiKey || !tenantId) {
  console.error('Live verification requires GLAW_LIVE_BASE_URL, GLAW_LIVE_API_KEY, and GLAW_LIVE_TENANT_ID.');
  process.exit(2);
}

async function request(path, headers = {}) {
  const response = await fetch(`${baseUrl}${path}`, { headers });
  let body = null;
  try { body = await response.json(); } catch { /* status-only endpoint */ }
  return { response, body };
}

const health = await request('/health');
if (health.response.status !== 200 || health.body?.status !== 'ok') throw new Error(`health_check_failed:${health.response.status}`);
const ready = await request('/ready');
if (ready.response.status !== 200 || ready.body?.status !== 'ready' || Object.values(ready.body?.checks ?? {}).some((value) => value !== 'ok')) throw new Error(`readiness_check_failed:${ready.response.status}`);
const noTenant = await request('/v1/jobs/live-verification', { authorization: `Bearer ${apiKey}` });
if (noTenant.response.status !== 400 || noTenant.body?.error !== 'tenant_required') throw new Error(`tenant_required_check_failed:${noTenant.response.status}`);
const wrongTenant = await request('/v1/jobs/live-verification', { authorization: `Bearer ${apiKey}`, 'x-tenant-id': otherTenantId });
if (wrongTenant.response.status !== 403 || wrongTenant.body?.error !== 'tenant_forbidden') throw new Error(`tenant_isolation_check_failed:${wrongTenant.response.status}`);
const authorized = await request('/v1/jobs/live-verification', { authorization: `Bearer ${apiKey}`, 'x-tenant-id': tenantId });
if (authorized.response.status !== 501 || authorized.body?.error !== 'job_tracking_not_implemented') throw new Error(`authorized_route_check_failed:${authorized.response.status}`);
console.log(JSON.stringify({ status: 'passed', checks: ['health', 'readiness', 'tenant-required', 'tenant-isolation', 'authenticated-routing'], baseUrl }));
