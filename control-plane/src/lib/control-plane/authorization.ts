import type { ControlPlaneDb } from "./db";
import type { RequestPrincipal } from "./auth";

export type AuthorizationDecision = "ALLOW" | "DENY" | "ESCALATE";
export type Relation = "member" | "assigned" | "reviewer" | "owner" | "admin" | "client" | "privileged" | "walled";

export type AuthorizationResult = { decision: AuthorizationDecision; reason: string; policyVersion: string; relationshipsEvaluated: string[]; decisionId: string };

const MAX_DEPTH = 8;

/** Bounded recursive relationship evaluation. Deny is the safe default. */
export async function authorizeRelation(db: ControlPlaneDb, principal: RequestPrincipal, action: string, resourceType: string, resourceId: string, policyVersion: string): Promise<AuthorizationResult> {
  const relationshipsEvaluated = [`tenant:${principal.tenantId}`, `subject:user:${principal.actorId}`, `${resourceType}:${resourceId}`];
  const decisionId = crypto.randomUUID();
  const deny = (reason: string): AuthorizationResult => ({ decision: "DENY", reason, policyVersion, relationshipsEvaluated, decisionId });
  if (!principal.tenantId || !principal.actorId || !resourceType || !resourceId) return deny("incomplete authorization scope");

  let rows: Array<{ subject_type: string; subject_id: string; relation: Relation; resource_type: string; resource_id: string }>;
  try {
    const result = await db.prepare(`WITH RECURSIVE principals(kind, id, depth) AS (
      SELECT 'user', ?, 0 UNION ALL
      SELECT t.resource_type, t.resource_id, p.depth + 1 FROM authorization_tuples t JOIN principals p ON t.subject_type = p.kind AND t.subject_id = p.id
      WHERE t.tenant_id = ? AND t.relation = 'member' AND t.revoked_at IS NULL AND p.depth < ?
    ), resources(kind, id, depth) AS (
      SELECT ?, ?, 0 UNION ALL
      SELECT e.parent_type, e.parent_id, r.depth + 1 FROM authorization_edges e JOIN resources r ON e.child_type = r.kind AND e.child_id = r.id
      WHERE e.tenant_id = ? AND e.revoked_at IS NULL AND r.depth < ?
    ) SELECT t.subject_type, t.subject_id, t.relation, t.resource_type, t.resource_id FROM authorization_tuples t
      JOIN principals p ON t.subject_type = p.kind AND t.subject_id = p.id JOIN resources r ON t.resource_type = r.kind AND t.resource_id = r.id
      WHERE t.tenant_id = ? AND t.revoked_at IS NULL`).bind(principal.actorId, principal.tenantId, MAX_DEPTH, resourceType, resourceId, principal.tenantId, MAX_DEPTH, principal.tenantId).all<typeof rows[number]>();
    rows = result.results;
  } catch {
    return deny("authorization graph unavailable; failed closed");
  }
  rows.forEach((row) => relationshipsEvaluated.push(`${row.relation}:${row.resource_type}:${row.resource_id}`, `${row.subject_type}:${row.subject_id}`));
  if (rows.some((row) => row.relation === "walled" || (row.relation === "privileged" && principal.actorType !== "human"))) return deny("ethical wall or privilege policy blocks this actor");
  const grants = rows.map((row) => row.relation);
  const allowed = grants.includes("admin") || grants.includes("owner") || grants.includes("assigned") || grants.includes("reviewer") || (action.endsWith(".read") && grants.includes("member"));
  if (!allowed) return deny("no active relationship grants this resource");
  const consequential = action.endsWith(".send") || action.endsWith(".file") || action.endsWith(".execute") || action.endsWith(".delete");
  return { decision: consequential ? "ESCALATE" : "ALLOW", reason: consequential ? "relationship exists but action requires approval" : "recursive relationship grants bounded access", policyVersion, relationshipsEvaluated, decisionId };
}
