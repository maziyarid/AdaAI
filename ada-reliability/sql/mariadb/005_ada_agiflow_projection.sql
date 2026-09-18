-- Additive Agiflow projection tables (AAX-12 / ADR-0003).
-- These do not replace maziyar-control-core jobs, schedules or leases.
-- Do not apply to production without the migration runbook and approval.

CREATE TABLE IF NOT EXISTS ada_agiflow_task_map (
  durable_job_id VARCHAR(191) NOT NULL,
  agiflow_task_id VARCHAR(191) NOT NULL,
  agiflow_project_id VARCHAR(191) NOT NULL,
  last_projected_status VARCHAR(64) NULL,
  last_projected_version INT NOT NULL DEFAULT 0,
  previous_projected_status VARCHAR(64) NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (durable_job_id),
  UNIQUE KEY uq_ada_agiflow_task (agiflow_task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Outbox survives Agiflow outage. Replay is keyed by idempotency_key so
-- comments, tasks and status transitions are not duplicated.
CREATE TABLE IF NOT EXISTS ada_agiflow_outbox (
  id CHAR(36) NOT NULL,
  idempotency_key CHAR(64) NOT NULL,
  kind VARCHAR(32) NOT NULL,
  durable_job_id VARCHAR(191) NOT NULL,
  payload JSON NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
  attempts INT NOT NULL DEFAULT 0,
  last_error TEXT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  applied_at TIMESTAMP(6) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_ada_agiflow_outbox_idem (idempotency_key),
  KEY idx_ada_agiflow_outbox_pending (status, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_agiflow_projection_events (
  id BIGINT NOT NULL AUTO_INCREMENT,
  durable_job_id VARCHAR(191) NOT NULL,
  agiflow_task_id VARCHAR(191) NULL,
  event_type VARCHAR(64) NOT NULL,
  details JSON NOT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY idx_ada_agiflow_proj_job (durable_job_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
