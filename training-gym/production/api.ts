export const PRODUCTION_ROUTES = ['/live','/ready','/experiments','/experiments/:id','/experiments/:id/cancel','/episodes','/episodes/:id','/episodes/:id/rerun','/episodes/:id/trajectory','/reviews','/gyms','/tasks','/datasets','/exports'] as const;
export interface TenantContext { organizationId: string; actorId: string; role: 'OWNER'|'ADMIN'|'RESEARCHER'|'REVIEWER'|'VIEWER'|'SERVICE'; }
export function assertTenant(resourceOrganizationId: string, context: TenantContext): void { if (resourceOrganizationId !== context.organizationId) throw new Error('Tenant access denied'); }
