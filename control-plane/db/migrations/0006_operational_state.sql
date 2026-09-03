CREATE TABLE IF NOT EXISTS connector_attempts (
  id TEXT PRIMARY KEY,
  operation_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  attempt INTEGER NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('STARTED','SUCCEEDED','FAILED','TIMED_OUT')),
  external_request_id TEXT,
  error_code TEXT,
  error_message_redacted TEXT,
  started_at TEXT NOT NULL,
  completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_connector_attempts_operation ON connector_attempts(operation_id, attempt);

CREATE TABLE IF NOT EXISTS dead_letter_items (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  operation_id TEXT,
  kind TEXT NOT NULL,
  payload_hash TEXT NOT NULL,
  reason_code TEXT NOT NULL,
  state TEXT NOT NULL CHECK (state IN ('OPEN','REVIEWED','REPLAYED','DISCARDED')) DEFAULT 'OPEN',
  created_at TEXT NOT NULL,
  reviewed_at TEXT,
  reviewed_by TEXT
);

CREATE INDEX IF NOT EXISTS idx_dead_letter_items_tenant_state ON dead_letter_items(tenant_id, state, created_at);

CREATE TABLE IF NOT EXISTS model_deployments (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  provider TEXT NOT NULL,
  model TEXT NOT NULL,
  version TEXT NOT NULL,
  region TEXT NOT NULL,
  rollout_stage TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 0,
  benchmark_score REAL NOT NULL,
  config_hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (tenant_id, provider, model, version, region)
);

CREATE TABLE IF NOT EXISTS telemetry_metrics (
  id TEXT PRIMARY KEY,
  tenant_id TEXT,
  metric_name TEXT NOT NULL,
  metric_value REAL NOT NULL,
  unit TEXT NOT NULL,
  dimensions_json TEXT NOT NULL,
  trace_id TEXT,
  recorded_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_telemetry_metrics_name_time ON telemetry_metrics(metric_name, recorded_at);

CREATE TABLE IF NOT EXISTS region_replication_jobs (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  source_region TEXT NOT NULL,
  target_region TEXT NOT NULL,
  fencing_epoch INTEGER NOT NULL,
  cursor TEXT,
  state TEXT NOT NULL CHECK (state IN ('PENDING','RUNNING','SUCCEEDED','FAILED','FENCED')),
  last_error_redacted TEXT,
  updated_at TEXT NOT NULL
);

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
