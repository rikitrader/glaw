-- Server-authoritative workflow snapshots and action receipts.
-- The canvas remains an editor projection; this history is the source of truth.

CREATE TABLE IF NOT EXISTS workflow_versions (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT REFERENCES matters(id),
  workflow_id TEXT NOT NULL,
  revision INTEGER NOT NULL CHECK (revision > 0),
  revision_hash TEXT NOT NULL,
  policy_version TEXT NOT NULL,
  environment TEXT NOT NULL CHECK (environment IN ('sandbox','staging','production')),
  status TEXT NOT NULL CHECK (status IN ('DRAFT','PUBLISHED','REVOKED')),
  definition_json TEXT NOT NULL,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE (organization_id, workflow_id, revision)
);

CREATE INDEX IF NOT EXISTS idx_workflow_versions_scope
  ON workflow_versions(organization_id, workflow_id, revision DESC);

CREATE TABLE IF NOT EXISTS workflow_action_receipts (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  workflow_id TEXT NOT NULL,
  revision INTEGER NOT NULL,
  command_id TEXT NOT NULL,
  action TEXT NOT NULL CHECK (action IN ('SAVE_DRAFT','REQUEST_PUBLISH','PREPARE_DRY_RUN')),
  state TEXT NOT NULL CHECK (state IN ('accepted','authorized','approval_required','blocked','completed','failed')),
  payload_hash TEXT NOT NULL,
  external_effect TEXT NOT NULL DEFAULT 'NONE',
  reason TEXT,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE (organization_id, command_id)
);

CREATE INDEX IF NOT EXISTS idx_workflow_action_receipts_scope
  ON workflow_action_receipts(organization_id, workflow_id, created_at DESC);
