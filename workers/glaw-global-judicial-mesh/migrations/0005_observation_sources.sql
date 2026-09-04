ALTER TABLE judge_observations ADD COLUMN source_id TEXT;
CREATE INDEX IF NOT EXISTS idx_judge_observations_source ON judge_observations(source_id);
