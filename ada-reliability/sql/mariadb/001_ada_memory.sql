-- Additive MariaDB 10.11 migration for Ada memory/context.
-- Does NOT drop or alter existing maziyar-control-core tables.
-- Prefix: ada_  — keep control-core jobs/schedules/leases as the queue authority.

CREATE TABLE IF NOT EXISTS ada_scope_versions (
  scope_type VARCHAR(32) NOT NULL,
  scope_id VARCHAR(191) NOT NULL,
  version BIGINT NOT NULL DEFAULT 1,
  updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (scope_type, scope_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO ada_scope_versions (scope_type, scope_id, version) VALUES ('global', '*', 1);

CREATE TABLE IF NOT EXISTS ada_memory_records (
  id CHAR(36) NOT NULL,
  canonical_key VARCHAR(191) NOT NULL,
  record_type VARCHAR(64) NOT NULL,
  scope_type VARCHAR(32) NOT NULL,
  scope_id VARCHAR(191) NOT NULL DEFAULT '*',
  priority TINYINT NOT NULL,
  authority VARCHAR(64) NOT NULL,
  provenance VARCHAR(32) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
  privacy_class VARCHAR(32) NOT NULL DEFAULT 'LOCAL_ONLY',
  title VARCHAR(512) NOT NULL,
  content MEDIUMTEXT NOT NULL,
  summary TEXT NULL,
  source_type VARCHAR(64) NULL,
  source_reference VARCHAR(512) NULL,
  creator VARCHAR(128) NOT NULL,
  verifier VARCHAR(128) NULL,
  valid_from TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  valid_until TIMESTAMP(6) NULL,
  supersedes_id CHAR(36) NULL,
  superseded_by CHAR(36) NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  checksum CHAR(64) NOT NULL,
  PRIMARY KEY (id),
  KEY idx_ada_memory_bootstrap (scope_type, scope_id, status, priority),
  KEY idx_ada_memory_canonical (canonical_key, scope_type, scope_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_memory_versions (
  id BIGINT NOT NULL AUTO_INCREMENT,
  memory_id CHAR(36) NOT NULL,
  version_no INT NOT NULL,
  snapshot JSON NOT NULL,
  changed_by VARCHAR(128) NOT NULL,
  change_reason VARCHAR(255) NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_ada_memver (memory_id, version_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_project_states (
  project_id VARCHAR(191) NOT NULL,
  lane VARCHAR(64) NOT NULL DEFAULT 'main',
  objective TEXT NULL,
  verified_status VARCHAR(64) NULL,
  completed_work JSON NOT NULL,
  active_decisions JSON NOT NULL,
  blockers JSON NOT NULL,
  next_action TEXT NULL,
  state_version BIGINT NOT NULL DEFAULT 1,
  updated_by VARCHAR(128) NOT NULL,
  updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (project_id, lane)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
