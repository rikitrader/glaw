CREATE TABLE IF NOT EXISTS authorization_edges (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES organizations(id),
  child_type TEXT NOT NULL,
  child_id TEXT NOT NULL,
  parent_type TEXT NOT NULL,
  parent_id TEXT NOT NULL,
  relation TEXT NOT NULL,
  policy_version TEXT NOT NULL,
  created_at TEXT NOT NULL,
  revoked_at TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_authz_active_edge
  ON authorization_edges(tenant_id, child_type, child_id, parent_type, parent_id, relation)
  WHERE revoked_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_authz_edges_child
  ON authorization_edges(tenant_id, child_type, child_id, revoked_at);
