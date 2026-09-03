CREATE INDEX IF NOT EXISTS idx_judge_observations_profile_scope ON judge_observations(tenant_id, judge_id, matter_id, observed_at);
CREATE INDEX IF NOT EXISTS idx_judge_sources_profile_scope ON judge_sources(tenant_id, judge_id, matter_id, retrieved_at);
CREATE INDEX IF NOT EXISTS idx_judge_case_profile_scope ON judge_case_observations(tenant_id, judge_id, matter_id, created_at);
CREATE INDEX IF NOT EXISTS idx_judge_predictions_profile_scope ON judge_predictions(tenant_id, judge_id, matter_id, created_at);
CREATE INDEX IF NOT EXISTS idx_judge_adversarial_profile_scope ON judge_adversarial_runs(tenant_id, judge_id, matter_id, created_at);
CREATE INDEX IF NOT EXISTS idx_judge_engine_profile_scope ON judge_engine_reports(tenant_id, judge_id, matter_id, created_at);
