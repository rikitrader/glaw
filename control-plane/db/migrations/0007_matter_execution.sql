CREATE TABLE IF NOT EXISTS workflow_runs (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT NOT NULL REFERENCES matters(id),
  workflow_id TEXT NOT NULL REFERENCES workflows(id),
  workflow_version TEXT NOT NULL,
  state TEXT NOT NULL CHECK (state IN ('REQUESTED','PLANNED','EVIDENCE_ACQUIRED','ANALYZED','DRAFTED','RED_TEAMED','BLUE_TEAMED','JUDGED','HUMAN_REVIEW','APPROVED','BLOCKED','CLOSED','FAILED')),
  risk_class TEXT NOT NULL,
  policy_version TEXT NOT NULL,
  started_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_scope ON workflow_runs(organization_id, matter_id, updated_at);

CREATE TABLE IF NOT EXISTS workflow_tasks (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES workflow_runs(id),
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT NOT NULL REFERENCES matters(id),
  task_key TEXT NOT NULL,
  task_type TEXT NOT NULL,
  assigned_agent TEXT,
  state TEXT NOT NULL CHECK (state IN ('QUEUED','RUNNING','SUCCEEDED','REVIEW','BLOCKED','FAILED')),
  input_hash TEXT,
  output_hash TEXT,
  error_code TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (run_id, task_key)
);
CREATE INDEX IF NOT EXISTS idx_workflow_tasks_scope ON workflow_tasks(organization_id, matter_id, state, updated_at);

CREATE TABLE IF NOT EXISTS evidence_items (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT NOT NULL REFERENCES matters(id),
  source_type TEXT NOT NULL,
  source_id TEXT NOT NULL,
  source_version TEXT,
  document_hash TEXT,
  page INTEGER,
  paragraph INTEGER,
  exact_span TEXT,
  privilege_class TEXT NOT NULL DEFAULT 'UNKNOWN',
  validation_state TEXT NOT NULL CHECK (validation_state IN ('UNVERIFIED','VERIFIED','CONTRARY','QUARANTINED')) DEFAULT 'UNVERIFIED',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_evidence_scope ON evidence_items(organization_id, matter_id, validation_state);
