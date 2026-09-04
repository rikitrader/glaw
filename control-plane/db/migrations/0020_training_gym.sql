CREATE TABLE IF NOT EXISTS gym_experiments (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  name TEXT NOT NULL,
  gym_version TEXT NOT NULL,
  dataset_version TEXT NOT NULL,
  task_id TEXT NOT NULL,
  models_json TEXT NOT NULL,
  episodes_per_model INTEGER NOT NULL CHECK (episodes_per_model > 0),
  concurrency INTEGER NOT NULL CHECK (concurrency > 0),
  seed_strategy TEXT NOT NULL CHECK (seed_strategy IN ('paired','random')),
  status TEXT NOT NULL CHECK (status IN ('DRAFT','RUNNING','CANCELLING','CANCELLED','COMPLETED')),
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (organization_id, id)
);
CREATE INDEX IF NOT EXISTS idx_gym_experiments_org_status ON gym_experiments(organization_id, status, updated_at);

CREATE TABLE IF NOT EXISTS gym_episodes (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  experiment_id TEXT NOT NULL REFERENCES gym_experiments(id),
  task_id TEXT NOT NULL,
  seed INTEGER NOT NULL,
  status TEXT NOT NULL,
  attempt INTEGER NOT NULL DEFAULT 0,
  idempotency_key TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_gym_episodes_org_status ON gym_episodes(organization_id, status, updated_at);
CREATE INDEX IF NOT EXISTS idx_gym_episodes_experiment ON gym_episodes(experiment_id, created_at);

CREATE TABLE IF NOT EXISTS gym_episode_transitions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  episode_id TEXT NOT NULL REFERENCES gym_episodes(id),
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  from_status TEXT NOT NULL,
  to_status TEXT NOT NULL,
  reason TEXT,
  metadata_json TEXT,
  occurred_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_gym_transitions_episode ON gym_episode_transitions(organization_id, episode_id, occurred_at);

CREATE TABLE IF NOT EXISTS gym_trajectory_refs (
  episode_id TEXT PRIMARY KEY REFERENCES gym_episodes(id),
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  object_key TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  step_count INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gym_evaluations (
  id TEXT PRIMARY KEY,
  episode_id TEXT NOT NULL REFERENCES gym_episodes(id),
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  evaluator_version TEXT NOT NULL,
  automatic_score REAL NOT NULL CHECK (automatic_score >= 0 AND automatic_score <= 1),
  human_score REAL CHECK (human_score IS NULL OR (human_score >= 0 AND human_score <= 1)),
  dimensions_json TEXT NOT NULL,
  failures_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE (episode_id, evaluator_version)
);
CREATE INDEX IF NOT EXISTS idx_gym_evaluations_org_episode ON gym_evaluations(organization_id, episode_id, created_at);

ALTER TABLE gym_episodes ADD COLUMN lease_owner TEXT;
ALTER TABLE gym_episodes ADD COLUMN lease_until TEXT;
CREATE INDEX IF NOT EXISTS idx_gym_episodes_claimable ON gym_episodes(status, lease_until, created_at);
