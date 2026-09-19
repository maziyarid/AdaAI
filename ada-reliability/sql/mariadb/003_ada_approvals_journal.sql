CREATE TABLE IF NOT EXISTS ada_approval_tickets (
  id CHAR(36) NOT NULL,
  task_run_id CHAR(36) NOT NULL,
  parent_job CHAR(36) NULL,
  tool_name VARCHAR(128) NOT NULL,
  site_id VARCHAR(191) NULL,
  resource_id VARCHAR(191) NULL,
  payload_hash CHAR(64) NOT NULL,
  snapshot_hash CHAR(64) NULL,
  context_receipt_id CHAR(36) NOT NULL,
  dependency_hash CHAR(64) NOT NULL,
  state VARCHAR(32) NOT NULL DEFAULT 'PENDING',
  requested_by VARCHAR(128) NOT NULL,
  requester_identity VARCHAR(64) NOT NULL,
  approved_by VARCHAR(128) NULL,
  approver_identity VARCHAR(64) NULL,
  approval_id CHAR(36) NULL,
  one_time_token_hash CHAR(64) NULL,
  requested_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  decided_at TIMESTAMP(6) NULL,
  expires_at TIMESTAMP(6) NOT NULL,
  consumed_at TIMESTAMP(6) NULL,
  PRIMARY KEY (id),
  KEY idx_ada_approval_pending (state, expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_approval_events (
  id BIGINT NOT NULL AUTO_INCREMENT,
  approval_ticket_id CHAR(36) NOT NULL,
  event_type VARCHAR(32) NOT NULL,
  actor VARCHAR(128) NOT NULL,
  details JSON NOT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY idx_ada_appev (approval_ticket_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_snapshots (
  id CHAR(36) NOT NULL,
  task_run_id CHAR(36) NULL,
  site_id VARCHAR(191) NULL,
  resource_id VARCHAR(191) NULL,
  snapshot_hash CHAR(64) NOT NULL,
  storage_ref VARCHAR(512) NOT NULL,
  created_by VARCHAR(128) NOT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_mutation_journal (
  id CHAR(36) NOT NULL,
  task_run_id CHAR(36) NOT NULL,
  idempotency_key VARCHAR(191) NOT NULL,
  tool_name VARCHAR(128) NOT NULL,
  site_id VARCHAR(191) NULL,
  resource_id VARCHAR(191) NULL,
  payload_hash CHAR(64) NOT NULL,
  snapshot_id CHAR(36) NULL,
  expected_postcondition JSON NOT NULL,
  status VARCHAR(32) NOT NULL,
  remote_ref JSON NULL,
  last_error TEXT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_ada_journal_idem (idempotency_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_verifications (
  id CHAR(36) NOT NULL,
  site_id VARCHAR(191) NOT NULL,
  resource_id VARCHAR(191) NOT NULL,
  after_mutation_id CHAR(36) NULL,
  passed TINYINT(1) NOT NULL,
  stale TINYINT(1) NOT NULL DEFAULT 0,
  failures JSON NOT NULL,
  live_hash CHAR(64) NOT NULL,
  verifier_identity VARCHAR(64) NOT NULL DEFAULT 'verifier',
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY idx_ada_verif (site_id, resource_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_external_inputs (
  id CHAR(36) NOT NULL,
  source_uri TEXT NULL,
  source_kind VARCHAR(64) NOT NULL,
  trust_class VARCHAR(32) NOT NULL DEFAULT 'UNTRUSTED_EXTERNAL',
  content_hash CHAR(64) NOT NULL,
  content_text MEDIUMTEXT NULL,
  quarantine_status VARCHAR(32) NOT NULL DEFAULT 'QUARANTINED',
  injection_flags JSON NOT NULL,
  ingested_by VARCHAR(128) NOT NULL,
  ingested_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY idx_ada_ext_hash (content_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
