-- Additive failed-run outbox (AAX-15). Execution recovery, NOT Agiflow projection.
-- DISTINCT from ada_agiflow_outbox (AAX-12 / 005_ada_agiflow_projection.sql).
-- Does not create jobs, schedules or leases. Not a second scheduler.
-- Do not apply to production without the migration runbook and approval.
--
-- LIVE HOLD (2026-09-19): the current recovery authority already stores
-- pd_worker_runs / pd_outbox in /srv/maziyar-wp-mcp/state/factory.sqlite3.
-- Live control-core MariaDB has no pd_* tables, but that does NOT mean recovery
-- is absent. pd_outbox overlaps this migration's failure/retry/lease/idempotency
-- responsibilities. Do NOT apply 006 while the SQLite recovery outbox is active.
-- First choose and prove one authority (map/migrate/retire the SQLite outbox or
-- redesign 006). Never run two runtime recovery outboxes.

CREATE TABLE IF NOT EXISTS ada_failed_runs (
  id CHAR(36) NOT NULL,
  idempotency_key CHAR(64) NOT NULL,
  run_id VARCHAR(191) NOT NULL,
  worker VARCHAR(128) NOT NULL,
  schedule_id VARCHAR(191) NULL,
  durable_job_id VARCHAR(191) NULL,
  factory_task_id VARCHAR(191) NULL,
  packet_id VARCHAR(191) NULL,
  artifact_id VARCHAR(191) NULL,
  failure_class VARCHAR(64) NOT NULL,
  failure_reason TEXT NOT NULL,
  lifecycle VARCHAR(32) NOT NULL,
  attempt_count INT NOT NULL DEFAULT 0,
  max_attempts INT NOT NULL DEFAULT 5,
  first_failed_at TIMESTAMP(6) NOT NULL,
  last_failed_at TIMESTAMP(6) NOT NULL,
  next_retry_at TIMESTAMP(6) NULL,
  reset_condition VARCHAR(255) NULL,
  external_sync_state VARCHAR(32) NOT NULL DEFAULT 'none',
  mutation_kind VARCHAR(64) NOT NULL DEFAULT 'none',
  mutation_idempotency_key CHAR(64) NULL,
  sync_marker VARCHAR(96) NOT NULL,
  payload JSON NOT NULL,
  last_error TEXT NULL,
  lease_owner VARCHAR(128) NULL,
  lease_until TIMESTAMP(6) NULL,
  claim_generation INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_ada_failed_runs_idem (idempotency_key),
  KEY idx_ada_failed_runs_claim (lifecycle, next_retry_at),
  KEY idx_ada_failed_runs_job (durable_job_id),
  KEY idx_ada_failed_runs_run (run_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Claim is a store-level compare-and-set, not read-then-write. MariaDB:
--   UPDATE ada_failed_runs
--      SET lifecycle='inflight', lease_owner=?, lease_until=?,
--          claim_generation=claim_generation+1
--    WHERE id=?
--      AND lifecycle IN ('queued','retryable')
--      AND (next_retry_at IS NULL OR next_retry_at <= ?)
--   (affected rows = 1 means this worker owns the retry; 0 means lost the race)
--
-- Lease expire/reclaim is the same class of CAS. A detached inflight copy
-- must not overwrite a newer claim. MariaDB:
--   UPDATE ada_failed_runs
--      SET lifecycle='retryable', lease_owner=NULL, lease_until=NULL,
--          next_retry_at=?
--    WHERE id=?
--      AND lifecycle='inflight'
--      AND lease_owner <=> ?
--      AND lease_until <=> ?
--      AND (lease_until IS NULL OR lease_until <= ?)
--      AND claim_generation <=> ?
--   (affected rows = 0 means another worker already reclaimed)
--
-- Result transitions (succeed/park/requeue/dead-letter) and mutation-ledger
-- writes are the same class of CAS. A delayed engine_retry must not overwrite
-- a newer claim or completed state. MariaDB apply_if_claim:
--   UPDATE ada_failed_runs
--      SET lifecycle=?, lease_owner=NULL, lease_until=NULL, ...
--    WHERE id=?
--      AND claim_generation <=> ?
--   (affected rows = 0 means another worker reclaimed this generation)
-- Mutation-ledger inserts belong in the same transaction as this UPDATE.
-- Do not apply this migration here; AAX-7 rehearsal only.

CREATE TABLE IF NOT EXISTS ada_failed_run_events (
  id BIGINT NOT NULL AUTO_INCREMENT,
  failed_run_id CHAR(36) NOT NULL,
  event_type VARCHAR(64) NOT NULL,
  details JSON NOT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY idx_ada_failed_run_events (failed_run_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
