ALTER TABLE hanke_runs ADD COLUMN review_status TEXT NOT NULL DEFAULT 'PENDING' CHECK (review_status IN ('PENDING', 'APPROVED', 'REJECTED'));
ALTER TABLE hanke_runs ADD COLUMN reviewer_id TEXT;
ALTER TABLE hanke_runs ADD COLUMN review_note TEXT;
ALTER TABLE hanke_runs ADD COLUMN reviewed_at TEXT;
