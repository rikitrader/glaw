ALTER TABLE judge_profile_reviews ADD COLUMN prediction_id TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_judge_profile_reviews_prediction ON judge_profile_reviews(tenant_id, prediction_id) WHERE prediction_id IS NOT NULL;
