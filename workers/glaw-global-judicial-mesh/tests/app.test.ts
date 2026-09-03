import { describe, expect, it } from 'vitest';
import app from '../src/app';
import type { Env } from '../src/types';

const env = { ENVIRONMENT: 'local', COURTLISTENER_BASE_URL: 'https://example.test', CACHE: { get: async () => null, put: async () => undefined } } as unknown as Env;

describe('production safety routes', () => {
  it('fails closed when production API authentication is not configured', async () => {
    const response = await app.request('/v1/search', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ text: 'discovery' }) }, { ...env, ENVIRONMENT: 'production' });
    expect(response.status).toBe(503);
    expect(await response.json()).toMatchObject({ error: 'api_auth_not_configured' });
  });

  it('rejects judge profile access without tenant scope', async () => {
    const response = await app.request('/v1/judges/judge-1/profile', {}, env);
    expect(response.status).toBe(400);
    expect(await response.json()).toMatchObject({ error: 'tenant_required' });
  });

  it('rejects the judge directory without tenant scope', async () => {
    const response = await app.request('/v1/judges', {}, env);
    expect(response.status).toBe(400);
    expect(await response.json()).toMatchObject({ error: 'tenant_required' });
  });

  it('lists tenant-scoped judge profiles with directory filters', async () => {
    const DB = { prepare: (sql: string) => ({ bind: () => ({ all: async () => sql.includes('judge_profiles') ? { results: [{ payload_json: JSON.stringify({ tenantId: 'tenant-1', judgeId: 'judge-1', judgeName: 'Judge One', court: 'Circuit Court', county: 'Orange', judicialCircuit: 'Ninth', division: '77', profileAsOf: '2026-01-01', status: 'CURRENT', lastVerified: '2026-01-02' }) }, { payload_json: JSON.stringify({ tenantId: 'tenant-1', judgeId: 'judge-2', judgeName: 'Judge Two', court: 'County Court', county: 'Seminole', profileAsOf: '2026-01-01', status: 'NEEDS_VERIFICATION', lastVerified: '2026-01-01' }) }] } : { results: [] }, run: async () => ({}) }) }) } as unknown as Env['DB'];
    const response = await app.request('/v1/judges?county=Orange', { headers: { 'x-tenant-id': 'tenant-1' } }, { ...env, DB });
    expect(response.status).toBe(200);
    expect(await response.json()).toMatchObject({ judges: [{ judgeId: 'judge-1', status: 'CURRENT' }] });
  });

  it('rejects invalid judge-directory pagination', async () => {
    const response = await app.request('/v1/judges?limit=not-a-number', { headers: { 'x-tenant-id': 'tenant-1' } }, env);
    expect(response.status).toBe(400);
    expect(await response.json()).toMatchObject({ error: 'invalid_pagination' });
  });

  it('rejects matter creation without tenant scope', async () => {
    const response = await app.request('/v1/matters', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ matterId: 'matter-1' }) }, env);
    expect(response.status).toBe(400);
    expect(await response.json()).toMatchObject({ error: 'tenant_required' });
  });

  it('fails closed for an unknown matter on scoped reads', async () => {
    const DB = { prepare: () => ({ bind: () => ({ first: async () => null, run: async () => ({}) }) }) } as unknown as Env['DB'];
    const response = await app.request('/v1/matters/missing', { headers: { 'x-tenant-id': 'tenant-1' } }, { ...env, DB });
    expect(response.status).toBe(404);
    expect(await response.json()).toMatchObject({ error: 'matter_not_found_or_out_of_scope' });
  });

  it('fails closed for an unknown matter audit log', async () => {
    const DB = { prepare: () => ({ bind: () => ({ first: async () => null, all: async () => ({ results: [] }), run: async () => ({}) }) }) } as unknown as Env['DB'];
    const response = await app.request('/v1/matters/missing/audit-log', { headers: { authorization: 'Bearer admin-secret', 'x-tenant-id': 'tenant-1' } }, { ...env, DB, GLAW_API_KEY: 'api-secret', GLAW_ADMIN_API_KEY: 'admin-secret' });
    expect(response.status).toBe(404);
    expect(await response.json()).toMatchObject({ error: 'matter_not_found_or_out_of_scope' });
  });

  it('fails closed for unknown matter-scoped resource identifiers', async () => {
    const DB = { prepare: (sql: string) => ({ bind: () => ({ first: async () => sql.includes('FROM matters') ? { payload_json: JSON.stringify({ status: 'ACTIVE' }) } : null, all: async () => ({ results: [] }), run: async () => ({}) }) }) } as unknown as Env['DB'];
    const bindings = { ...env, DB };
    const artifact = await app.request('/v1/matters/matter-1/filings/missing', { headers: { 'x-tenant-id': 'tenant-1' } }, bindings);
    const eventReviews = await app.request('/v1/matters/matter-1/events/missing/reviews', { headers: { 'x-tenant-id': 'tenant-1' } }, bindings);
    const discoveryReviews = await app.request('/v1/matters/matter-1/discovery/missing/reviews', { headers: { 'x-tenant-id': 'tenant-1' } }, bindings);
    const gateEvents = await app.request('/v1/matters/matter-1/filings/missing/gate-events', { headers: { 'x-tenant-id': 'tenant-1' } }, bindings);
    expect(artifact.status).toBe(404);
    expect(await artifact.json()).toMatchObject({ error: 'artifact_not_found_or_out_of_scope' });
    expect(eventReviews.status).toBe(404);
    expect(await eventReviews.json()).toMatchObject({ error: 'event_not_found_or_out_of_scope' });
    expect(discoveryReviews.status).toBe(404);
    expect(await discoveryReviews.json()).toMatchObject({ error: 'discovery_object_not_found_or_out_of_scope' });
    expect(gateEvents.status).toBe(404);
    expect(await gateEvents.json()).toMatchObject({ error: 'artifact_not_found_or_out_of_scope' });
  });

  it('rejects a tenant that does not match the production tenant boundary', async () => {
    const response = await app.request('/v1/judges/judge-1/profile', { headers: { authorization: 'Bearer api-secret', 'x-tenant-id': 'other-tenant' } }, { ...env, ENVIRONMENT: 'production', GLAW_API_KEY: 'api-secret', GLAW_TENANT_ID: 'configured-tenant' });
    expect(response.status).toBe(403);
    expect(await response.json()).toMatchObject({ error: 'tenant_forbidden' });
  });

  it('requires tenant scope for every production API route', async () => {
    const response = await app.request('/v1/jobs/job-1', { headers: { authorization: 'Bearer api-secret' } }, { ...env, ENVIRONMENT: 'production', GLAW_API_KEY: 'api-secret', GLAW_TENANT_ID: 'configured-tenant' });
    expect(response.status).toBe(400);
    expect(await response.json()).toMatchObject({ error: 'tenant_required' });
  });

  it('requires configured admin credentials for profile writes', async () => {
    const response = await app.request('/v1/judges/judge-1/identity', { method: 'POST', headers: { 'content-type': 'application/json', 'x-tenant-id': 'tenant-1' }, body: JSON.stringify({ judgeName: 'Judge', court: 'Florida court', profileAsOf: '2026-01-01', status: 'CURRENT' }) }, env);
    expect(response.status).toBe(503);
    expect(await response.json()).toMatchObject({ error: 'admin_not_configured' });
  });

  it('requires the admin credential for observation ingestion', async () => {
    const response = await app.request('/v1/judges/judge-1/observations', { method: 'POST', headers: { 'content-type': 'application/json', authorization: 'Bearer api-secret', 'x-tenant-id': 'tenant-1' }, body: JSON.stringify({ dimension: 'discovery', proposition: 'scope', value: 'narrow', sourceClass: 'user-record', observedAt: '2026-01-01', confidence: 0.5 }) }, { ...env, GLAW_API_KEY: 'api-secret' });
    expect(response.status).toBe(503);
    expect(await response.json()).toMatchObject({ error: 'admin_not_configured' });
  });

  it('allows the separate admin credential to reach admin authorization', async () => {
    const DB = { prepare: () => ({ bind: () => ({ run: async () => ({}) }) }) } as unknown as Env['DB'];
    const response = await app.request('/v1/judges/judge-1/identity', { method: 'POST', headers: { 'content-type': 'application/json', authorization: 'Bearer admin-secret', 'x-tenant-id': 'tenant-1' }, body: JSON.stringify({ judgeName: 'Judge', court: 'Florida court', profileAsOf: '2026-01-01', status: 'CURRENT' }) }, { ...env, DB, GLAW_API_KEY: 'api-secret', GLAW_ADMIN_API_KEY: 'admin-secret' });
    expect(response.status).toBe(201);
  });

  it('fails safe when the rate-limit configuration is not numeric', async () => {
    const DB = { prepare: () => ({ bind: () => ({ first: async () => null, all: async () => ({ results: [] }), run: async () => ({}) }) }) } as unknown as Env['DB'];
    const response = await app.request('/v1/judges/judge-1/profile', { headers: { authorization: 'Bearer api-secret', 'x-tenant-id': 'tenant-1' } }, { ...env, DB, GLAW_API_KEY: 'api-secret', GLAW_RATE_LIMIT_PER_MINUTE: 'not-a-number' });
    expect(response.status).not.toBe(429);
  });

  it('denies unlisted production CORS origins and allows configured origins', async () => {
    const productionEnv = { ...env, ENVIRONMENT: 'production', GLAW_API_KEY: 'api-secret', GLAW_ALLOWED_ORIGINS: 'https://app.example.test' };
    const denied = await app.request('/health', { headers: { origin: 'https://evil.example.test' } }, productionEnv);
    const allowed = await app.request('/health', { headers: { origin: 'https://app.example.test' } }, productionEnv);
    expect(denied.headers.get('access-control-allow-origin')).toBeNull();
    expect(allowed.headers.get('access-control-allow-origin')).toBe('https://app.example.test');
  });

  it('does not fabricate a job status without a durable job store', async () => {
    const response = await app.request('/v1/jobs/job-1', {}, env);
    expect(response.status).toBe(501);
    expect(await response.json()).toMatchObject({ error: 'job_tracking_not_implemented' });
  });

  it('fails production readiness when required configuration is absent', async () => {
    const response = await app.request('/ready', {}, { ...env, ENVIRONMENT: 'production', DB: {} as Env['DB'], DOCUMENTS: {} as Env['DOCUMENTS'], GLAW_API_KEY: 'api-secret' });
    expect(response.status).toBe(503);
    expect(await response.json()).toMatchObject({ status: 'not_ready', checks: { configuration: 'failed' } });
  });

  it('requires all execution bindings before local readiness succeeds', async () => {
    const response = await app.request('/ready', {}, { ...env, DB: {} as Env['DB'], DOCUMENTS: {} as Env['DOCUMENTS'] });
    expect(response.status).toBe(503);
    expect(await response.json()).toMatchObject({ status: 'not_ready', checks: { queue: 'failed', vectors: 'failed', durableObjects: 'failed' } });
  });

  it('requires the prediction-review schema before readiness succeeds', async () => {
    const DB = { prepare: (sql: string) => ({ first: async () => sql.includes('SELECT 1') ? { ok: 1 } : { name: 'filing_gate_events' }, all: async () => sql.includes('discovery_objects') ? { results: [{ name: 'source_id' }] } : sql.includes('judge_profile_reviews') ? { results: [{ name: 'notes' }] } : { results: [] } }) } as unknown as Env['DB'];
    const bindings = { ...env, DB, DOCUMENTS: { head: async () => null }, INGESTION_QUEUE: {}, LEGAL_VECTORS: {}, ROUTER_COORDINATOR: {}, JUDGE_PROFILE_COORDINATOR: {}, MATTER_COORDINATOR: {} } as unknown as Env;
    const response = await app.request('/ready', {}, bindings);
    expect(response.status).toBe(503);
    expect(await response.json()).toMatchObject({ status: 'not_ready', checks: { schema: 'failed' } });
  });
});
