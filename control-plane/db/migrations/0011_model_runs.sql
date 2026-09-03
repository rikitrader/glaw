CREATE TABLE IF NOT EXISTS model_runs (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT,
  workflow_id TEXT,
  task_type TEXT NOT NULL,
  provider TEXT NOT NULL,
  model TEXT NOT NULL,
  model_version TEXT NOT NULL,
  region TEXT,
  policy_version TEXT NOT NULL,
  benchmark_score REAL NOT NULL,
  estimated_cost_usd REAL NOT NULL,
  latency_ms INTEGER,
  status TEXT NOT NULL CHECK (status IN ('STARTED','SUCCEEDED','BLOCKED','FAILED')),
  request_hash TEXT NOT NULL,
  response_hash TEXT,
  created_at TEXT NOT NULL,
  completed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_model_runs_tenant_time ON model_runs(tenant_id, created_at);
