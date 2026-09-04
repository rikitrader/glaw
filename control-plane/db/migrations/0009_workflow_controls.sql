ALTER TABLE workflow_runs ADD COLUMN control_state TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (control_state IN ('ACTIVE','PAUSED','FROZEN','TERMINATED'));

CREATE TABLE IF NOT EXISTS workflow_control_events (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT NOT NULL REFERENCES matters(id),
  run_id TEXT NOT NULL REFERENCES workflow_runs(id),
  actor_id TEXT NOT NULL,
  action TEXT NOT NULL CHECK (action IN ('PAUSE','RESUME','FREEZE','TERMINATE')),
  previous_state TEXT NOT NULL,
  next_state TEXT NOT NULL,
  reason TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_workflow_control_events_run ON workflow_control_events(run_id, created_at);
