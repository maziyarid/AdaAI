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
-- Payload stores evidence_id / close_grant_id only — never verified flags
-- or caller-supplied verifier/closer identities.
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

-- HMAC-issued evidence is the only Review proof. Callers cannot construct
-- a verified=true object; projection looks up id and verifies signature.
CREATE TABLE IF NOT EXISTS ada_agiflow_evidence (
  id CHAR(36) NOT NULL,
  durable_job_id VARCHAR(191) NOT NULL,
  live_hash VARCHAR(128) NOT NULL,
  verifier_identity VARCHAR(128) NOT NULL,
  source VARCHAR(32) NOT NULL,
  signature CHAR(64) NOT NULL,
  issued_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY idx_ada_agiflow_evidence_job (durable_job_id, issued_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- One-time human close grants are the only Done proof. consumed is fail-closed.
CREATE TABLE IF NOT EXISTS ada_agiflow_close_grants (
  id CHAR(36) NOT NULL,
  durable_job_id VARCHAR(191) NOT NULL,
  evidence_id CHAR(36) NOT NULL,
  closer_identity VARCHAR(128) NOT NULL,
  signature CHAR(64) NOT NULL,
  consumed TINYINT(1) NOT NULL DEFAULT 0,
  issued_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  consumed_at TIMESTAMP(6) NULL,
  PRIMARY KEY (id),
  KEY idx_ada_agiflow_grant_job (durable_job_id, consumed),
  KEY idx_ada_agiflow_grant_evidence (evidence_id)
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
