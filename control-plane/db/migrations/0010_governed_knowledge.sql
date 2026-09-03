CREATE TABLE IF NOT EXISTS claims (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT NOT NULL REFERENCES matters(id),
  proposition TEXT NOT NULL,
  claim_type TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('SUPPORTED','DISPUTED','ASSUMED','UNSUPPORTED','BLOCKED')) DEFAULT 'ASSUMED',
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_claims_scope ON claims(organization_id, matter_id, status);

CREATE TABLE IF NOT EXISTS claim_evidence_links (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT NOT NULL REFERENCES matters(id),
  claim_id TEXT NOT NULL REFERENCES claims(id),
  evidence_id TEXT NOT NULL REFERENCES evidence_items(id),
  link_type TEXT NOT NULL CHECK (link_type IN ('SUPPORTS','CONTRADICTS','QUALIFIES')),
  created_at TEXT NOT NULL,
  UNIQUE (claim_id, evidence_id, link_type)
);

CREATE TABLE IF NOT EXISTS conflict_entities (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  canonical_name TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  aliases_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS conflict_relationships (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  from_entity_id TEXT NOT NULL REFERENCES conflict_entities(id),
  relation TEXT NOT NULL,
  to_entity_id TEXT NOT NULL REFERENCES conflict_entities(id),
  source_id TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_conflict_relationships_from ON conflict_relationships(organization_id, from_entity_id);

CREATE TABLE IF NOT EXISTS legal_holds (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT,
  scope_json TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('ACTIVE','RELEASED')) DEFAULT 'ACTIVE',
  issued_by TEXT NOT NULL,
  issued_at TEXT NOT NULL,
  released_at TEXT
);

CREATE TABLE IF NOT EXISTS retention_policies (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  resource_type TEXT NOT NULL,
  retention_days INTEGER NOT NULL,
  legal_hold_exempt INTEGER NOT NULL DEFAULT 0,
  version TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS model_benchmarks (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES organizations(id),
  deployment_id TEXT NOT NULL,
  suite TEXT NOT NULL,
  score REAL NOT NULL,
  sample_count INTEGER NOT NULL,
  evaluated_at TEXT NOT NULL,
  evaluator_version TEXT NOT NULL
);

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
