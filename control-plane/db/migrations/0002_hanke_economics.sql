CREATE TABLE IF NOT EXISTS hanke_runs (
  run_id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT REFERENCES matters(id),
  workflow_id TEXT NOT NULL,
  status TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hanke_gate_records (
  run_id TEXT NOT NULL REFERENCES hanke_runs(run_id),
  gate_id TEXT NOT NULL,
  status TEXT NOT NULL,
  owner TEXT NOT NULL,
  evidence_ids_json TEXT NOT NULL,
  reason TEXT,
  recorded_at TEXT NOT NULL,
  PRIMARY KEY (run_id, gate_id)
);

CREATE TABLE IF NOT EXISTS hanke_run_events (
  run_id TEXT NOT NULL REFERENCES hanke_runs(run_id),
  sequence INTEGER NOT NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  PRIMARY KEY (run_id, sequence)
);

CREATE INDEX IF NOT EXISTS idx_hanke_runs_org_status ON hanke_runs(organization_id, status);
CREATE INDEX IF NOT EXISTS idx_hanke_gate_records_status ON hanke_gate_records(status);
