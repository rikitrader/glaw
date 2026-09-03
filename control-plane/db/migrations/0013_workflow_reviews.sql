CREATE TABLE IF NOT EXISTS workflow_reviews (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT NOT NULL REFERENCES matters(id),
  workflow_id TEXT NOT NULL,
  run_id TEXT,
  team TEXT NOT NULL CHECK (team IN ('RED_TEAM','BLUE_TEAM')),
  state TEXT NOT NULL CHECK (state IN ('OPEN','IN_REVIEW','SURVIVED','REPAIRED','BLOCKED','CLOSED')),
  severity TEXT NOT NULL CHECK (severity IN ('INFO','LOW','MODERATE','HIGH','CRITICAL')),
  summary TEXT NOT NULL,
  evidence_refs_json TEXT NOT NULL DEFAULT '[]',
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_workflow_reviews_scope
  ON workflow_reviews(organization_id, workflow_id, team, updated_at DESC);
