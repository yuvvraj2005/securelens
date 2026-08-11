-- Reference schema for the scan_results table.
-- In normal operation SQLAlchemy creates this automatically on startup
-- (see backend/app/database/db.py) — this file is documentation / a
-- starting point if you want to run SecureLens against Postgres or MySQL
-- instead of the default SQLite file.

CREATE TABLE IF NOT EXISTS scan_results (
    id           INTEGER PRIMARY KEY,
    target       VARCHAR NOT NULL,
    status       VARCHAR NOT NULL DEFAULT 'pending', -- pending|running|completed|failed
    score        INTEGER,
    grade        VARCHAR,
    risk_level   VARCHAR,
    error        TEXT,
    created_at   TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    report       TEXT -- full JSON report, populated once status = 'completed'
);

CREATE INDEX IF NOT EXISTS idx_scan_results_target ON scan_results (target);
CREATE INDEX IF NOT EXISTS idx_scan_results_status ON scan_results (status);
