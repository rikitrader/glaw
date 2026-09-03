CREATE TABLE IF NOT EXISTS judge_observations (id TEXT PRIMARY KEY, judge_id TEXT NOT NULL, matter_id TEXT, dimension TEXT NOT NULL, status TEXT NOT NULL, observed_at TEXT NOT NULL, payload_json TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_judge_observations_judge ON judge_observations(judge_id, observed_at);
CREATE TABLE IF NOT EXISTS judge_predictions (id TEXT PRIMARY KEY, judge_id TEXT NOT NULL, matter_id TEXT, issue TEXT NOT NULL, model TEXT NOT NULL, human_review TEXT NOT NULL, created_at TEXT NOT NULL, payload_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS judge_profile_reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, judge_id TEXT NOT NULL, reviewer TEXT NOT NULL, decision TEXT NOT NULL, notes TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
