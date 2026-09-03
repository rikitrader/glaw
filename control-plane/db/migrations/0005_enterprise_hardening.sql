-- Enterprise hardening primitives. Provider credentials and external effects
-- remain outside this database behind capability-scoped adapters.

CREATE TABLE IF NOT EXISTS authorization_tuples (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES organizations(id),
  subject_type TEXT NOT NULL,
  subject_id TEXT NOT NULL,
  relation TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  resource_id TEXT NOT NULL,
  policy_version TEXT NOT NULL,
  created_at TEXT NOT NULL,
  revoked_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_authz_active_tuple
  ON authorization_tuples(tenant_id, subject_type, subject_id, relation, resource_type, resource_id)
  WHERE revoked_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_authz_lookup
  ON authorization_tuples(tenant_id, subject_id, resource_type, resource_id, relation);

CREATE TABLE IF NOT EXISTS audit_export_manifests (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT,
  event_count INTEGER NOT NULL,
  root_hash TEXT NOT NULL,
  manifest_json TEXT NOT NULL,
  signature TEXT NOT NULL,
  signing_key_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  created_by TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS connector_operations (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT,
  command_id TEXT NOT NULL,
  connector_id TEXT NOT NULL,
  idempotency_key TEXT NOT NULL,
  state TEXT NOT NULL CHECK (state IN ('PREPARED', 'VALIDATED', 'HUMAN_APPROVED', 'SUBMITTED', 'RECEIPT_RECEIVED', 'LOOKUP_PERFORMED', 'CONFIRMED', 'RECONCILIATION_REQUIRED', 'FAILED')),
  external_request_id TEXT,
  external_transaction_id TEXT,
  expected_state_json TEXT NOT NULL,
  observed_state_json TEXT,
  reconciliation_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (tenant_id, connector_id, idempotency_key)
);
CREATE INDEX IF NOT EXISTS idx_connector_reconciliation
  ON connector_operations(tenant_id, state, updated_at);

CREATE TABLE IF NOT EXISTS model_policies (
  id TEXT NOT NULL,
  version TEXT NOT NULL,
  tenant_id TEXT NOT NULL REFERENCES organizations(id),
  allowed_providers_json TEXT NOT NULL,
  allowed_models_json TEXT NOT NULL,
  residency TEXT NOT NULL,
  max_cost_usd REAL,
  max_latency_ms INTEGER,
  min_benchmark_score REAL,
  allow_fallback INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'retired')),
  created_at TEXT NOT NULL,
  PRIMARY KEY (id, version)
);

CREATE TABLE IF NOT EXISTS region_policies (
  tenant_id TEXT PRIMARY KEY REFERENCES organizations(id),
  home_region TEXT NOT NULL,
  allowed_regions_json TEXT NOT NULL,
  deployment_mode TEXT NOT NULL,
  fencing_epoch INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL
);
