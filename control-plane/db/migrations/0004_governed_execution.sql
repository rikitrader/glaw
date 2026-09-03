-- Governed execution foundation. Existing tables remain compatible and are not
-- rewritten; these tables add the command/receipt boundary around them.

CREATE TABLE IF NOT EXISTS policies (
  id TEXT NOT NULL,
  version TEXT NOT NULL,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'retired')),
  definition_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (id, version)
);

CREATE TABLE IF NOT EXISTS commands (
  id TEXT PRIMARY KEY,
  idempotency_key TEXT NOT NULL,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  client_id TEXT,
  matter_id TEXT REFERENCES matters(id),
  actor_id TEXT NOT NULL,
  actor_type TEXT NOT NULL CHECK (actor_type IN ('human', 'agent', 'service')),
  actor_role TEXT NOT NULL,
  policy_id TEXT NOT NULL,
  policy_version TEXT NOT NULL,
  action TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  risk_class TEXT NOT NULL CHECK (risk_class IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
  evidence_refs_json TEXT NOT NULL,
  approval_refs_json TEXT NOT NULL,
  expected_external_effect TEXT,
  status TEXT NOT NULL DEFAULT 'accepted' CHECK (status IN ('accepted', 'blocked', 'escalated', 'completed')),
  payload_hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT,
  UNIQUE (organization_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_commands_org_created
  ON commands(organization_id, created_at);
CREATE INDEX IF NOT EXISTS idx_commands_matter_created
  ON commands(matter_id, created_at);

CREATE TABLE IF NOT EXISTS command_receipts (
  id TEXT PRIMARY KEY,
  command_id TEXT NOT NULL REFERENCES commands(id),
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  idempotency_key TEXT NOT NULL,
  state TEXT NOT NULL CHECK (state IN ('accepted', 'authorized', 'authority_claimed', 'adapter_attempted', 'observed_effective', 'unknown', 'failed')),
  attempt INTEGER NOT NULL DEFAULT 0 CHECK (attempt >= 0),
  external_request_id TEXT,
  external_transaction_id TEXT,
  external_receipt TEXT,
  expected_state TEXT,
  observed_state TEXT,
  reconciliation_status TEXT NOT NULL DEFAULT 'NOT_REQUIRED' CHECK (reconciliation_status IN ('NOT_REQUIRED', 'PENDING', 'CONFIRMED', 'FAILED')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (organization_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_receipts_org_updated
  ON command_receipts(organization_id, updated_at);

CREATE TABLE IF NOT EXISTS authorization_decisions (
  id TEXT PRIMARY KEY,
  command_id TEXT NOT NULL REFERENCES commands(id),
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  decision TEXT NOT NULL CHECK (decision IN ('ALLOW', 'DENY', 'ESCALATE')),
  reason TEXT NOT NULL,
  policy_version TEXT NOT NULL,
  relationships_json TEXT NOT NULL,
  decided_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS governed_audit_events (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT,
  actor_id TEXT NOT NULL,
  trace_id TEXT NOT NULL,
  command_id TEXT,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  previous_hash TEXT,
  event_hash TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_governed_audit_org_created
  ON governed_audit_events(organization_id, created_at);
