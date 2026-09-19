#!/usr/bin/env python3
"""Maziyar durable control core.

Local-only HTTP/CLI service backed by MariaDB. It keeps operator reachability
separate from service health and provides durable journal, job, schedule,
snapshot, finding, forecast, sync, and audit objects.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import hmac
import html
import json
import math
import os
import re
import signal
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse, urlencode

import pymysql
from pymysql.cursors import DictCursor

UTC = dt.timezone.utc
STOP = threading.Event()

PORTFOLIO_SITES = (
    "https://teznevise.ir/",
    "https://teznevisan-official.ir/",
    "https://bluethesis.ir/",
    "https://kanoon-research.ir/",
    "https://morihub.ir/",
    "https://fasthesis.ir/",
    "https://drbastaninejad.com/",
)

# Fixed targets only: job payloads can never turn the supervisor into an SSRF
# primitive. An HTTP 401 is healthy for protected MCP resources.
HEALTH_TARGETS = (
    ("control-core", "http://127.0.0.1:8770/health", (401,)),
    ("mistral-worker", "http://127.0.0.1:9102/healthz", (200,)),
    ("wp-mcp", "https://mcp.maziyarid.com/wp-mcp", (401,)),
    ("vps-mcp", "https://mcp.maziyarid.com/vps-mcp", (401,)),
    # ClickUp returns 400 (not 401) for a deliberately credential-free probe;
    # either response proves network/API reachability without storing a token.
    ("clickup-network", "https://api.clickup.com/api/v2/user", (400, 401)),
    # A credential-free 403 still proves DNS/TLS/API-edge reachability; auth health is tracked separately.
    ("google-api-network", "https://www.googleapis.com/discovery/v1/apis", (200, 403)),
)


def now() -> dt.datetime:
    return dt.datetime.now(UTC).replace(tzinfo=None)


def jdump(value) -> str:
    def default(obj):
        if isinstance(obj, (dt.datetime, dt.date)):
            return obj.isoformat() + ("Z" if isinstance(obj, dt.datetime) and obj.tzinfo is None else "")
        if isinstance(obj, dt.timedelta):
            return obj.total_seconds()
        raise TypeError(type(obj).__name__)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, default=default)


def jid() -> str:
    return str(uuid.uuid4())


def db():
    return pymysql.connect(
        host=os.getenv("CONTROL_DB_HOST", "127.0.0.1"),
        port=int(os.getenv("CONTROL_DB_PORT", "3306")),
        user=os.environ["CONTROL_DB_USER"],
        password=os.environ["CONTROL_DB_PASSWORD"],
        database=os.environ["CONTROL_DB_NAME"],
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
        connect_timeout=5,
        read_timeout=30,
        write_timeout=30,
        init_command="SET time_zone='+00:00'",
    )


SCHEMA = [
"""CREATE TABLE IF NOT EXISTS schema_migrations (
 version INT PRIMARY KEY, applied_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS agent_events (
 id CHAR(36) PRIMARY KEY, stable_id VARCHAR(191) NOT NULL, run_id VARCHAR(191), agent VARCHAR(64) NOT NULL,
 event_type VARCHAR(96) NOT NULL, entity_type VARCHAR(96), entity_id VARCHAR(191), payload_json JSON NOT NULL,
 created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6), UNIQUE KEY uq_agent_event_stable (stable_id),
 KEY ix_agent_events_entity (entity_type, entity_id, created_at), KEY ix_agent_events_agent (agent, created_at)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS canonical_tasks (
 id CHAR(36) PRIMARY KEY, stable_id VARCHAR(191) NOT NULL, project VARCHAR(191) NOT NULL, task VARCHAR(512) NOT NULL,
 status VARCHAR(64) NOT NULL, priority VARCHAR(32) NOT NULL, owner_agent VARCHAR(64), blockers_json JSON,
 dependencies_json JSON, qa_state VARCHAR(64), evidence_json JSON, next_action TEXT, affected_asset VARCHAR(512),
 external_clickup_id VARCHAR(191), source_updated_at DATETIME(6), created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
 updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
 UNIQUE KEY uq_canonical_task_stable (stable_id), KEY ix_canonical_clickup (external_clickup_id)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS jobs (
 id CHAR(36) PRIMARY KEY, stable_id VARCHAR(191) NOT NULL, idempotency_key VARCHAR(191) NOT NULL,
 agent VARCHAR(64) NOT NULL, job_type VARCHAR(96) NOT NULL, payload_json JSON NOT NULL, status VARCHAR(32) NOT NULL,
 priority INT NOT NULL DEFAULT 100, attempts INT NOT NULL DEFAULT 0, max_attempts INT NOT NULL DEFAULT 5,
 available_at DATETIME(6) NOT NULL, locked_by VARCHAR(191), lease_until DATETIME(6), last_error TEXT,
 created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6), updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
 finished_at DATETIME(6), UNIQUE KEY uq_jobs_stable (stable_id), UNIQUE KEY uq_jobs_idempotency (idempotency_key),
 KEY ix_jobs_claim (status, available_at, priority, created_at), KEY ix_jobs_lease (lease_until)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS job_results (
 id CHAR(36) PRIMARY KEY, job_id CHAR(36) NOT NULL, attempt INT NOT NULL, status VARCHAR(32) NOT NULL,
 result_json JSON, error_text TEXT, started_at DATETIME(6) NOT NULL, finished_at DATETIME(6) NOT NULL,
 UNIQUE KEY uq_job_result_attempt (job_id, attempt), CONSTRAINT fk_result_job FOREIGN KEY (job_id) REFERENCES jobs(id)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS schedules (
 id CHAR(36) PRIMARY KEY, stable_id VARCHAR(191) NOT NULL, agent VARCHAR(64) NOT NULL, job_type VARCHAR(96) NOT NULL,
 payload_json JSON NOT NULL, interval_seconds INT NOT NULL, enabled TINYINT(1) NOT NULL DEFAULT 1,
 next_run_at DATETIME(6) NOT NULL, last_run_at DATETIME(6), max_attempts INT NOT NULL DEFAULT 5,
 created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6), updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
 UNIQUE KEY uq_schedules_stable (stable_id), KEY ix_schedules_due (enabled, next_run_at)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS dead_letter_queue (
 id CHAR(36) PRIMARY KEY, job_id CHAR(36) NOT NULL, stable_id VARCHAR(191) NOT NULL, agent VARCHAR(64) NOT NULL,
 job_type VARCHAR(96) NOT NULL, payload_json JSON NOT NULL, attempts INT NOT NULL, error_text TEXT,
 quarantined_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6), resolved_at DATETIME(6), resolution_note TEXT,
 UNIQUE KEY uq_dlq_job (job_id)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS service_health (
 service_name VARCHAR(128) PRIMARY KEY, state VARCHAR(32) NOT NULL, circuit_state VARCHAR(32) NOT NULL DEFAULT 'closed',
 consecutive_failures INT NOT NULL DEFAULT 0, last_checked_at DATETIME(6) NOT NULL, last_success_at DATETIME(6),
 last_failure_at DATETIME(6), next_retry_at DATETIME(6), details_json JSON, updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS operator_reachability (
 id CHAR(36) PRIMARY KEY, state VARCHAR(64) NOT NULL, evidence_json JSON NOT NULL,
 observed_at DATETIME(6) NOT NULL, previous_state VARCHAR(64), transition_notified_at DATETIME(6),
 KEY ix_operator_observed (observed_at)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS operator_state (
 id TINYINT PRIMARY KEY, operator_state VARCHAR(64) NOT NULL DEFAULT 'OPERATOR_UNCONFIRMED',
 operator_last_seen DATETIME(6), operator_absence_seconds BIGINT NOT NULL DEFAULT 0,
 operator_absence_verified TINYINT(1) NOT NULL DEFAULT 0, iran_connectivity_state VARCHAR(64) NOT NULL DEFAULT 'UNKNOWN',
 netblocks_evidence JSON, secondary_connectivity_evidence JSON, unattended_blackout_state VARCHAR(64) NOT NULL DEFAULT 'INACTIVE',
 last_transition_at DATETIME(6), updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS cache_manifest (
 id CHAR(36) PRIMARY KEY, cache_key VARCHAR(191) NOT NULL, source VARCHAR(512) NOT NULL, fetched_at DATETIME(6) NOT NULL,
 expires_at DATETIME(6), checksum_sha256 CHAR(64) NOT NULL, version VARCHAR(128), storage_ref VARCHAR(1024), metadata_json JSON,
 UNIQUE KEY uq_cache_key_version (cache_key, checksum_sha256), KEY ix_cache_expiry (expires_at)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS harvest_provider_state (
 provider VARCHAR(64) PRIMARY KEY, state VARCHAR(64) NOT NULL, last_checked_at DATETIME(6), last_success_at DATETIME(6),
 last_error TEXT, next_retry_at DATETIME(6), details_json JSON, updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS tool_harvest_queue (
 id CHAR(36) PRIMARY KEY, stable_id VARCHAR(191) NOT NULL, priority INT NOT NULL DEFAULT 2, provider VARCHAR(64) NOT NULL,
 scope_name VARCHAR(191) NOT NULL, target VARCHAR(1024) NOT NULL, data_types VARCHAR(1024) NOT NULL, status VARCHAR(32) NOT NULL DEFAULT 'QUEUED',
 last_harvested DATETIME(6), capacity_text VARCHAR(1024), purpose TEXT, result_artifact VARCHAR(2048), last_error TEXT, notes TEXT,
 attempts INT NOT NULL DEFAULT 0, last_attempt_at DATETIME(6), next_attempt_at DATETIME(6), created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
 updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6), UNIQUE KEY uq_harvest_stable(stable_id),
 KEY ix_harvest_due(status,priority,next_attempt_at), KEY ix_harvest_provider(provider,status)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS data_snapshots (
 id CHAR(36) PRIMARY KEY, stable_id VARCHAR(191) NOT NULL, source VARCHAR(512) NOT NULL, site VARCHAR(191),
 fetched_at DATETIME(6) NOT NULL, expires_at DATETIME(6), checksum_sha256 CHAR(64) NOT NULL,
 version VARCHAR(128), data_json JSON, storage_ref VARCHAR(1024), UNIQUE KEY uq_snapshot_stable (stable_id),
 KEY ix_snapshot_site_source (site, source, fetched_at)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS intelligence_findings (
 id CHAR(36) PRIMARY KEY, stable_id VARCHAR(191) NOT NULL, source VARCHAR(512) NOT NULL,
 retrieved_at DATETIME(6) NOT NULL, expires_at DATETIME(6), site VARCHAR(191), subject VARCHAR(1024),
 baseline_json JSON, current_json JSON, delta_json JSON, confidence DECIMAL(5,4), likely_cause TEXT,
 opportunity_score DECIMAL(8,3), risk_score DECIMAL(8,3), recommended_action TEXT, evidence_refs_json JSON,
 created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6), UNIQUE KEY uq_finding_stable (stable_id),
 KEY ix_finding_site_time (site, retrieved_at)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS forecasts (
 id CHAR(36) PRIMARY KEY, stable_id VARCHAR(191) NOT NULL, site VARCHAR(191) NOT NULL, metric VARCHAR(191) NOT NULL,
 horizon_days INT NOT NULL, p10 DECIMAL(20,6), p50 DECIMAL(20,6), p90 DECIMAL(20,6), model VARCHAR(191) NOT NULL,
 inputs_json JSON NOT NULL, assumptions_json JSON NOT NULL, data_freshness_json JSON, confidence DECIMAL(5,4),
 issued_at DATETIME(6) NOT NULL, actual_value DECIMAL(20,6), forecast_error DECIMAL(20,6), evaluated_at DATETIME(6),
 UNIQUE KEY uq_forecast_stable (stable_id), KEY ix_forecast_site_metric (site, metric, issued_at)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS content_gate_states (
 id CHAR(36) PRIMARY KEY, asset_key VARCHAR(512) NOT NULL, gate_name VARCHAR(191) NOT NULL, state VARCHAR(64) NOT NULL,
 qa_agent VARCHAR(64), evidence_json JSON, updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
 UNIQUE KEY uq_content_gate (asset_key, gate_name)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS green_buffers (
 id CHAR(36) PRIMARY KEY, site VARCHAR(191) NOT NULL, buffer_type VARCHAR(128) NOT NULL, current_count INT NOT NULL,
 minimum_count INT NOT NULL, measured_at DATETIME(6) NOT NULL, depletion_rate DECIMAL(12,4), metadata_json JSON,
 UNIQUE KEY uq_green_buffer (site, buffer_type)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS pending_external_sync (
 id CHAR(36) PRIMARY KEY, stable_id VARCHAR(191) NOT NULL, target_service VARCHAR(128) NOT NULL,
 entity_type VARCHAR(96) NOT NULL, entity_id VARCHAR(191) NOT NULL, operation VARCHAR(64) NOT NULL,
 payload_json JSON NOT NULL, idempotency_key VARCHAR(191) NOT NULL, source_updated_at DATETIME(6),
 status VARCHAR(32) NOT NULL DEFAULT 'pending', attempts INT NOT NULL DEFAULT 0, max_attempts INT NOT NULL DEFAULT 5,
 available_at DATETIME(6) NOT NULL, expected_external_version VARCHAR(191), observed_external_version VARCHAR(191),
 locked_by VARCHAR(191), lease_until DATETIME(6), completed_at DATETIME(6), last_error TEXT,
 created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6), updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
 UNIQUE KEY uq_sync_stable (stable_id), UNIQUE KEY uq_sync_idempotency (idempotency_key),
 KEY ix_sync_due (status, available_at), KEY ix_sync_lease (lease_until)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS audit_log (
 id CHAR(36) PRIMARY KEY, stable_id VARCHAR(191) NOT NULL, actor VARCHAR(128) NOT NULL, action VARCHAR(191) NOT NULL,
 entity_type VARCHAR(96), entity_id VARCHAR(191), before_hash CHAR(64), after_hash CHAR(64), details_json JSON NOT NULL,
 created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6), UNIQUE KEY uq_audit_stable (stable_id),
 KEY ix_audit_entity (entity_type, entity_id, created_at)
) ENGINE=InnoDB""",
]


def init_db():
    conn = db()
    try:
        with conn.cursor() as cur:
            for stmt in SCHEMA:
                cur.execute(stmt)
            cur.execute("INSERT IGNORE INTO schema_migrations(version) VALUES (1)")
            for stmt in (
                "ALTER TABLE pending_external_sync ADD COLUMN IF NOT EXISTS max_attempts INT NOT NULL DEFAULT 5 AFTER attempts",
                "ALTER TABLE pending_external_sync ADD COLUMN IF NOT EXISTS expected_external_version VARCHAR(191) NULL AFTER available_at",
                "ALTER TABLE pending_external_sync ADD COLUMN IF NOT EXISTS observed_external_version VARCHAR(191) NULL AFTER expected_external_version",
                "ALTER TABLE pending_external_sync ADD COLUMN IF NOT EXISTS locked_by VARCHAR(191) NULL AFTER observed_external_version",
                "ALTER TABLE pending_external_sync ADD COLUMN IF NOT EXISTS lease_until DATETIME(6) NULL AFTER locked_by",
                "ALTER TABLE pending_external_sync ADD COLUMN IF NOT EXISTS completed_at DATETIME(6) NULL AFTER lease_until",
                "ALTER TABLE pending_external_sync ADD INDEX IF NOT EXISTS ix_sync_lease (lease_until)",
            ):
                cur.execute(stmt)
            cur.execute("INSERT IGNORE INTO schema_migrations(version) VALUES (2)")
        conn.commit()
    finally:
        conn.close()


def audit(cur, action, entity_type=None, entity_id=None, details=None, stable_id=None):
    cur.execute(
        "INSERT IGNORE INTO audit_log(id,stable_id,actor,action,entity_type,entity_id,details_json) VALUES(%s,%s,%s,%s,%s,%s,%s)",
        (jid(), stable_id or jid(), os.getenv("CONTROL_ACTOR", "control-core"), action, entity_type, entity_id, jdump(details or {})),
    )


def append_event(agent, event_type, payload, stable_id, run_id=None, entity_type=None, entity_id=None):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT IGNORE INTO agent_events(id,stable_id,run_id,agent,event_type,entity_type,entity_id,payload_json) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                (jid(), stable_id, run_id, agent, event_type, entity_type, entity_id, jdump(payload)),
            )
            audit(cur, "append_event", entity_type, entity_id, {"agent": agent, "event_type": event_type}, "audit:" + stable_id)
        conn.commit()
    finally:
        conn.close()


def queue_external_sync(target_service, entity_type, entity_id, operation, payload,
                        idempotency_key, stable_id=None, expected_external_version=None,
                        max_attempts=5):
    """Idempotently queue a connector-mediated external mutation."""
    stable_id = stable_id or "sync:" + idempotency_key
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT IGNORE INTO pending_external_sync
                (id,stable_id,target_service,entity_type,entity_id,operation,payload_json,idempotency_key,
                 status,attempts,max_attempts,available_at,expected_external_version)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'pending',0,%s,%s,%s)""",
                (jid(), stable_id, target_service, entity_type, entity_id, operation,
                 jdump(payload), idempotency_key, max(1, min(int(max_attempts), 20)), now(),
                 expected_external_version),
            )
            inserted = bool(cur.rowcount)
            cur.execute("SELECT * FROM pending_external_sync WHERE idempotency_key=%s", (idempotency_key,))
            row = cur.fetchone()
            audit(cur, "external_sync.queue", entity_type, entity_id,
                  {"target_service": target_service, "operation": operation, "inserted": inserted},
                  "audit:external-sync:queue:" + stable_id)
        conn.commit()
        return row
    finally:
        conn.close()


def claim_external_sync(worker_id, target_service="clickup", lease_seconds=300):
    """Claim one due sync item; expired leases return to pending."""
    lease_seconds = max(30, min(int(lease_seconds), 3600))
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE pending_external_sync
                   SET status='pending',locked_by=NULL,lease_until=NULL,
                       last_error=COALESCE(last_error,'lease expired; safely requeued')
                   WHERE status='in_progress' AND lease_until<%s""", (now(),),
            )
            cur.execute(
                """SELECT id FROM pending_external_sync
                   WHERE target_service=%s AND status='pending' AND available_at<=%s AND attempts<max_attempts
                   ORDER BY created_at,id LIMIT 1 FOR UPDATE SKIP LOCKED""",
                (target_service, now()),
            )
            found = cur.fetchone()
            if not found:
                conn.commit()
                return None
            cur.execute(
                """UPDATE pending_external_sync
                   SET status='in_progress',locked_by=%s,lease_until=DATE_ADD(%s,INTERVAL %s SECOND),attempts=attempts+1
                   WHERE id=%s AND status='pending'""",
                (worker_id, now(), lease_seconds, found["id"]),
            )
            cur.execute("SELECT * FROM pending_external_sync WHERE id=%s", (found["id"],))
            row = cur.fetchone()
            audit(cur, "external_sync.claim", row["entity_type"], row["entity_id"],
                  {"worker_id": worker_id, "attempt": row["attempts"], "lease_seconds": lease_seconds},
                  f"audit:external-sync:claim:{row['stable_id']}:{row['attempts']}")
        conn.commit()
        return row
    finally:
        conn.close()


def ack_external_sync(target, outcome, observed_external_version=None, error=None):
    """Acknowledge a leased item after connector-side verification."""
    if outcome not in ("succeeded", "retry", "conflict", "quarantined"):
        raise ValueError("invalid external-sync outcome")
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pending_external_sync WHERE id=%s OR stable_id=%s FOR UPDATE", (target, target))
            row = cur.fetchone()
            if not row:
                raise KeyError("external sync item not found")
            if row["status"] in ("succeeded", "conflict", "quarantined"):
                conn.commit()
                return row
            if row["status"] != "in_progress":
                raise RuntimeError("external sync item is not leased")
            final_outcome = outcome
            completed = None
            available = row["available_at"]
            if outcome == "retry":
                if int(row["attempts"]) >= int(row["max_attempts"]):
                    final_outcome = "quarantined"
                    completed = now()
                else:
                    available = now() + dt.timedelta(seconds=min(900, 2 ** min(int(row["attempts"]), 9)))
                    final_outcome = "pending"
            else:
                completed = now()
            cur.execute(
                """UPDATE pending_external_sync
                   SET status=%s,available_at=%s,observed_external_version=%s,locked_by=NULL,lease_until=NULL,
                       completed_at=%s,last_error=%s WHERE id=%s""",
                (final_outcome, available, observed_external_version, completed, error, row["id"]),
            )
            audit(cur, "external_sync.ack", row["entity_type"], row["entity_id"],
                  {"outcome": final_outcome, "attempt": row["attempts"],
                   "expected_external_version": row.get("expected_external_version"),
                   "observed_external_version": observed_external_version, "error": error},
                  f"audit:external-sync:ack:{row['stable_id']}:{row['attempts']}:{final_outcome}")
            cur.execute("SELECT * FROM pending_external_sync WHERE id=%s", (row["id"],))
            updated = cur.fetchone()
        conn.commit()
        return updated
    finally:
        conn.close()


def rebuild_tasks():
    """Rebuild canonical tasks only from journaled task.upsert events."""
    conn = db()
    rebuilt = 0
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM agent_events WHERE event_type='task.upsert' ORDER BY created_at,id")
            for event in cur.fetchall():
                p = json.loads(event["payload_json"])
                stable = event["entity_id"] or p.get("stable_id") or event["stable_id"]
                cur.execute(
                    """INSERT INTO canonical_tasks(id,stable_id,project,task,status,priority,owner_agent,blockers_json,dependencies_json,qa_state,evidence_json,next_action,affected_asset,external_clickup_id,source_updated_at)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE project=VALUES(project),task=VALUES(task),status=VALUES(status),priority=VALUES(priority),owner_agent=VALUES(owner_agent),blockers_json=VALUES(blockers_json),dependencies_json=VALUES(dependencies_json),qa_state=VALUES(qa_state),evidence_json=VALUES(evidence_json),next_action=VALUES(next_action),affected_asset=VALUES(affected_asset),external_clickup_id=VALUES(external_clickup_id),source_updated_at=VALUES(source_updated_at)""",
                    (jid(), stable, p["project"], p["task"], p.get("status","pending"), p.get("priority","normal"), p.get("owner_agent",event["agent"]), jdump(p.get("blockers",[])), jdump(p.get("dependencies",[])), p.get("qa_state"), jdump(p.get("evidence",[])), p.get("next_action"), p.get("affected_asset"), p.get("external_clickup_id"), event["created_at"]),
                )
                rebuilt += 1
            audit(cur,"rebuild_tasks",details={"events_replayed":rebuilt},stable_id="audit:rebuild:"+jid())
        conn.commit(); return rebuilt
    finally:
        conn.close()


def create_job(agent, job_type, payload, idempotency_key, priority=100, max_attempts=5, stable_id=None):
    stable_id = stable_id or "job:" + idempotency_key
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT IGNORE INTO jobs(id,stable_id,idempotency_key,agent,job_type,payload_json,status,priority,max_attempts,available_at) VALUES(%s,%s,%s,%s,%s,%s,'queued',%s,%s,%s)",
                (jid(), stable_id, idempotency_key, agent, job_type, jdump(payload), priority, max_attempts, now()),
            )
            cur.execute("SELECT * FROM jobs WHERE idempotency_key=%s", (idempotency_key,))
            row = cur.fetchone()
            audit(cur, "create_job", "job", row["id"], {"idempotency_key": idempotency_key}, "audit:create:" + stable_id)
        conn.commit()
        return row
    finally:
        conn.close()


def seed_schedules():
    rows = [
        ("schedule:blackout-sentinel", "BLACKOUT_SENTINEL", "blackout_sentinel.run", 300),
        ("schedule:project-controller", "PROJECT_CONTROLLER", "project_controller.run", 600),
        ("schedule:clickup-state-steward", "CLICKUP_STATE_STEWARD", "clickup_state_steward.run", 600),
        ("schedule:seo-scout", "SEO_SCOUT", "seo_scout.run", 3600),
        ("schedule:temp-tool-harvester", "TEMP_TOOL_HARVESTER", "temp_tool_harvester.run", 900),
        ("schedule:oracle-daily", "ORACLE_FORECASTER", "oracle_forecaster.run", 86400),
    ]
    conn = db()
    try:
        with conn.cursor() as cur:
            for stable, agent, typ, interval in rows:
                cur.execute(
                    """INSERT INTO schedules(id,stable_id,agent,job_type,payload_json,interval_seconds,next_run_at)
                    VALUES(%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE agent=VALUES(agent),job_type=VALUES(job_type),payload_json=VALUES(payload_json),interval_seconds=VALUES(interval_seconds)""",
                    (jid(), stable, agent, typ, jdump({"identity": agent}), interval, now()),
                )
        conn.commit()
    finally:
        conn.close()


def release_due_schedules():
    conn = db()
    released = 0
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM schedules WHERE enabled=1 AND next_run_at<=%s FOR UPDATE", (now(),))
            rows = cur.fetchall()
            for row in rows:
                bucket = int(time.time() // row["interval_seconds"])
                idem = f"schedule:{row['stable_id']}:{bucket}"
                cur.execute(
                    "INSERT IGNORE INTO jobs(id,stable_id,idempotency_key,agent,job_type,payload_json,status,priority,max_attempts,available_at) VALUES(%s,%s,%s,%s,%s,%s,'queued',100,%s,%s)",
                    (jid(), "job:" + idem, idem, row["agent"], row["job_type"], jdump(json.loads(row["payload_json"])), row["max_attempts"], now()),
                )
                released += cur.rowcount
                cur.execute("UPDATE schedules SET last_run_at=%s,next_run_at=DATE_ADD(%s,INTERVAL interval_seconds SECOND) WHERE id=%s", (now(), now(), row["id"]))
        conn.commit()
        return released
    finally:
        conn.close()


def claim_job(worker_id, lease_seconds=120):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE jobs SET status='queued',locked_by=NULL,lease_until=NULL WHERE status='running' AND lease_until<%s", (now(),))
            cur.execute("SELECT id FROM jobs WHERE status='queued' AND available_at<=%s ORDER BY priority ASC,created_at ASC LIMIT 1 FOR UPDATE SKIP LOCKED", (now(),))
            row = cur.fetchone()
            if not row:
                conn.commit(); return None
            cur.execute("UPDATE jobs SET status='running',locked_by=%s,lease_until=DATE_ADD(%s,INTERVAL %s SECOND),attempts=attempts+1 WHERE id=%s", (worker_id, now(), lease_seconds, row["id"]))
            cur.execute("SELECT * FROM jobs WHERE id=%s", (row["id"],))
            job = cur.fetchone()
        conn.commit(); return job
    finally:
        conn.close()


def fetch_fixed(url, timeout=20, limit=1048576):
    started = time.monotonic()
    req = urllib.request.Request(url, headers={"User-Agent": "Maziyar-Control-Core/2.0"})
    try:
        response = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as exc:
        response = exc
    with response:
        body = response.read(limit)
        status = int(response.status)
        headers = {k.lower(): v for k, v in response.headers.items() if k.lower() in (
            "content-type", "etag", "last-modified", "location", "www-authenticate", "x-robots-tag"
        )}
        final_url = response.geturl()
    return {
        "status": status,
        "final_url": final_url,
        "latency_ms": round((time.monotonic() - started) * 1000, 1),
        "headers": headers,
        "body": body,
    }


def record_service_probe(service, ok, details):
    conn = db()
    transition = None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM service_health WHERE service_name=%s FOR UPDATE", (service,))
            before = cur.fetchone()
            failures = 0 if ok else int((before or {}).get("consecutive_failures", 0)) + 1
            state = "healthy" if ok else "degraded"
            circuit = "closed" if ok else ("open" if failures >= 3 else "closed")
            retry = None if ok or failures < 3 else now() + dt.timedelta(seconds=min(900, 30 * (2 ** min(failures - 3, 5))))
            cur.execute(
                """INSERT INTO service_health(service_name,state,circuit_state,consecutive_failures,last_checked_at,last_success_at,last_failure_at,next_retry_at,details_json)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE state=VALUES(state),circuit_state=VALUES(circuit_state),consecutive_failures=VALUES(consecutive_failures),last_checked_at=VALUES(last_checked_at),last_success_at=COALESCE(VALUES(last_success_at),last_success_at),last_failure_at=COALESCE(VALUES(last_failure_at),last_failure_at),next_retry_at=VALUES(next_retry_at),details_json=VALUES(details_json)""",
                (service, state, circuit, failures, now(), now() if ok else None, None if ok else now(), retry, jdump(details)),
            )
            if not before or before["state"] != state or before["circuit_state"] != circuit:
                transition = {"service": service, "from": None if not before else before["state"], "to": state, "circuit": circuit}
                audit(cur, "service.transition", "service", service, transition, "audit:service:" + service + ":" + jid())
        conn.commit()
    finally:
        conn.close()
    if transition:
        transition_key = now().strftime("%Y%m%dT%H%M%S") + ":" + hashlib.sha256(jdump(transition).encode()).hexdigest()[:20]
        append_event("BLACKOUT_SENTINEL", "service.transition", transition,
                     "event:service:" + service + ":" + transition_key,
                     entity_type="service", entity_id=service)
    return transition



def get_operator_state():
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT IGNORE INTO operator_state(id) VALUES(1)")
            cur.execute("SELECT * FROM operator_state WHERE id=1")
            row = cur.fetchone()
        conn.commit()
        return row
    finally:
        conn.close()


def build_operator_recovery_digest(start_at, end_at):
    if not start_at:
        return {"absence_start": None, "return_at": end_at, "note": "no_prior_verified_heartbeat"}
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status,COUNT(*) n FROM jobs WHERE created_at>%s AND created_at<=%s GROUP BY status", (start_at, end_at))
            jobs = {r["status"]: r["n"] for r in cur.fetchall()}
            cur.execute("SELECT event_type,COUNT(*) n FROM agent_events WHERE created_at>%s AND created_at<=%s GROUP BY event_type ORDER BY n DESC LIMIT 50", (start_at, end_at))
            events = {r["event_type"]: r["n"] for r in cur.fetchall()}
            cur.execute("SELECT COUNT(*) n FROM dead_letter_queue WHERE quarantined_at>%s AND quarantined_at<=%s", (start_at, end_at))
            dlq_added = cur.fetchone()["n"]
            cur.execute("SELECT status,COUNT(*) n FROM pending_external_sync WHERE created_at>%s AND created_at<=%s GROUP BY status", (start_at, end_at))
            external_sync = {r["status"]: r["n"] for r in cur.fetchall()}
            cur.execute("SELECT COUNT(*) n FROM audit_log WHERE action='service.transition' AND created_at>%s AND created_at<=%s", (start_at, end_at))
            service_transitions = cur.fetchone()["n"]
        return {"absence_start": start_at, "return_at": end_at, "jobs": jobs, "events": events, "dlq_added": dlq_added,
                "external_sync": external_sync, "service_transitions": service_transitions}
    finally:
        conn.close()


def consumed_grok_operator_state():
    """Return the last explicitly consumed Grok state without inferring absence."""
    current = get_operator_state()
    return {
        **current,
        "authority": "GROK_ONLY",
        "source": "durable_consumed_state",
        "state_change": False,
    }


def consume_grok_failover_state(state, source_message_id, source_user_id, details=None):
    """Consume only an authenticated Grok state-change record from ClickUp."""
    expected_user_id = os.environ.get("GROK_CLICKUP_USER_ID", "4595254")
    if not source_message_id:
        raise ValueError("source_message_id_required")
    if str(source_user_id) != expected_user_id:
        raise PermissionError("unauthenticated_grok_source")

    normalized = str(state or "").strip().upper()
    if normalized in ("UNATTENDED_BLACKOUT", "FAILOVER_TRUE", "TRUE"):
        desired = "UNATTENDED_BLACKOUT"
        unattended = "ACTIVE"
    elif normalized in ("OPERATOR_RETURNED", "FAILOVER_FALSE", "FALSE", "OPERATOR_AVAILABLE"):
        desired = "OPERATOR_AVAILABLE"
        unattended = "INACTIVE"
    else:
        raise ValueError("unsupported_grok_state")

    observed = now()
    evidence = {
        "source": "grok_clickup_authenticated",
        "source_message_id": str(source_message_id),
        "source_user_id": str(source_user_id),
        "reported_state": normalized,
        "details": details or {},
        "observed_at": observed,
    }
    conn = db()
    transition = False
    previous = None
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT IGNORE INTO operator_state(id) VALUES(1)")
            cur.execute("SELECT * FROM operator_state WHERE id=1 FOR UPDATE")
            before = cur.fetchone()
            previous = before["operator_state"]
            transition = previous != desired
            cur.execute(
                """UPDATE operator_state
                   SET operator_state=%s,
                       operator_last_seen=IF(%s='OPERATOR_AVAILABLE',%s,operator_last_seen),
                       operator_absence_seconds=0,
                       operator_absence_verified=0,
                       iran_connectivity_state='GROK_REPORTED',
                       netblocks_evidence=NULL,
                       secondary_connectivity_evidence=NULL,
                       unattended_blackout_state=%s,
                       last_transition_at=IF(%s,NOW(6),last_transition_at)
                   WHERE id=1""",
                (desired, desired, observed, unattended, 1 if transition else 0),
            )
            if transition:
                cur.execute(
                    "INSERT INTO operator_reachability(id,state,evidence_json,observed_at,previous_state) VALUES(%s,%s,%s,%s,%s)",
                    (jid(), desired, jdump(evidence), observed, previous),
                )
            audit(
                cur,
                "operator.grok_state_consumed",
                "operator",
                "maziyar",
                evidence,
                "audit:operator:grok:" + str(source_message_id),
            )
        conn.commit()
    finally:
        conn.close()

    if transition:
        append_event(
            "PROJECT_CONTROLLER",
            "operator.grok_state_consumed",
            {"from": previous, "to": desired, **evidence},
            "event:operator:grok:" + str(source_message_id),
            entity_type="operator",
            entity_id="maziyar",
        )
    return consumed_grok_operator_state()


def run_sentinel(job):
    results = []
    transitions = []
    for service, url, expected in HEALTH_TARGETS:
        existing = rows("SELECT state,circuit_state,next_retry_at FROM service_health WHERE service_name=%s", (service,))
        if existing and existing[0]["circuit_state"] == "open" and existing[0]["next_retry_at"] and existing[0]["next_retry_at"] > now():
            results.append({"service": service, "ok": False, "skipped": True,
                            "reason": "circuit_open", "next_retry_at": existing[0]["next_retry_at"]})
            continue
        try:
            probe = fetch_fixed(url, timeout=15, limit=65536)
            ok = probe["status"] in expected
            if service in ("wp-mcp", "vps-mcp"):
                challenge = probe["headers"].get("www-authenticate", "")
                ok = ok and "resource_metadata=" in challenge and 'scope="mcp:tools"' in challenge
            details = {k: v for k, v in probe.items() if k != "body"}
        except Exception as exc:
            ok = False
            details = {"error": type(exc).__name__ + ": " + str(exc)[:300]}
        transition = record_service_probe(service, ok, details)
        results.append({"service": service, "ok": ok, **details})
        if transition:
            transitions.append(transition)
    operator = consumed_grok_operator_state()
    append_event("BLACKOUT_SENTINEL", "sentinel.observation",
                 {"services": results, "operator": operator, "transitions": transitions},
                 "event:" + job["idempotency_key"], entity_type="supervisor", entity_id="blackout-sentinel")
    return {"checked": sum(1 for r in results if not r.get("skipped")),
            "skipped": sum(1 for r in results if r.get("skipped")),
            "healthy": sum(1 for r in results if r["ok"]), "transitions": transitions,
            "operator": operator}


def extract_page_facts(body):
    text = body.decode("utf-8", "replace")
    def first(pattern):
        match = re.search(pattern, text, re.I | re.S)
        return re.sub(r"\s+", " ", match.group(1)).strip()[:1000] if match else None
    return {
        "title": first(r"<title[^>]*>(.*?)</title>"),
        "canonical": first(r"<link[^>]+rel=[\"']canonical[\"'][^>]+href=[\"']([^\"']+)") or
                     first(r"<link[^>]+href=[\"']([^\"']+)[\"'][^>]+rel=[\"']canonical[\"']"),
        "robots": first(r"<meta[^>]+name=[\"']robots[\"'][^>]+content=[\"']([^\"']+)") or
                  first(r"<meta[^>]+content=[\"']([^\"']+)[\"'][^>]+name=[\"']robots[\"']"),
        "h1": first(r"<h1[^>]*>(.*?)</h1>"),
    }


def store_snapshot(source, site, data, checksum, expires_at, stable_id):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute("""INSERT IGNORE INTO data_snapshots(id,stable_id,source,site,fetched_at,expires_at,checksum_sha256,version,data_json)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (jid(), stable_id, source, site, now(), expires_at, checksum, "public-http-v1", jdump(data)))
        conn.commit()
    finally:
        conn.close()


def run_scout(job):
    findings = 0
    snapshots = 0
    bucket = int(time.time() // 3600)
    for home in PORTFOLIO_SITES:
        site = urlparse(home).netloc
        for kind, url in (("homepage", home), ("robots", home + "robots.txt"), ("sitemap", home + "sitemap_index.xml")):
            source = "public-http:" + kind
            try:
                probe = fetch_fixed(url, timeout=25)
                body = probe.pop("body")
                checksum = hashlib.sha256(body).hexdigest()
                data = {**probe, "bytes": len(body), "facts": extract_page_facts(body) if kind == "homepage" else {}}
                previous = rows("SELECT checksum_sha256,data_json,stable_id FROM data_snapshots WHERE site=%s AND source=%s ORDER BY fetched_at DESC LIMIT 1", (site, source))
                # Preserve distinct raw revisions while deduplicating identical
                # bodies within an hourly collection bucket.
                stable = f"snapshot:{site}:{kind}:{bucket}:{checksum[:16]}"
                store_snapshot(source, site, data, checksum, now() + dt.timedelta(hours=2), stable)
                snapshots += 1
                if previous and previous[0]["checksum_sha256"] != checksum:
                    current_facts = data["facts"]
                    baseline = json.loads(previous[0]["data_json"])
                    before_semantic = {"status": baseline.get("status"), "final_url": baseline.get("final_url"), "x_robots_tag": baseline.get("headers", {}).get("x-robots-tag"), "facts": baseline.get("facts", {})}
                    after_semantic = {"status": data.get("status"), "final_url": data.get("final_url"), "x_robots_tag": data.get("headers", {}).get("x-robots-tag"), "facts": current_facts}
                    semantic_delta = {key: {"before": before_semantic.get(key), "after": after_semantic.get(key)} for key in before_semantic if before_semantic.get(key) != after_semantic.get(key)}
                    # Byte-level drift (nonces, timestamps, cache markup) is
                    # retained in raw snapshots but is not an SEO finding.
                    if not semantic_delta:
                        continue
                    finding_stable = f"finding:{site}:{kind}:{previous[0]['checksum_sha256'][:12]}:{checksum[:12]}"
                    conn = db()
                    try:
                        with conn.cursor() as cur:
                            cur.execute("""INSERT IGNORE INTO intelligence_findings(id,stable_id,source,retrieved_at,expires_at,site,subject,baseline_json,current_json,delta_json,confidence,likely_cause,opportunity_score,risk_score,recommended_action,evidence_refs_json)
                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (jid(), finding_stable, source, now(), now()+dt.timedelta(days=7), site, url, jdump(baseline), jdump(data), jdump({"checksum_changed":True,"facts_before":baseline.get("facts",{}),"facts_after":current_facts}), 0.75, "Public representation changed; cause not inferred", 0, 35 if kind=="homepage" else 20, "Review only if title/canonical/robots/status changed", jdump([previous[0]["stable_id"], stable])))
                            findings += cur.rowcount
                        conn.commit()
                    finally:
                        conn.close()
            except Exception as exc:
                record_service_probe("origin:" + site, False, {"kind": kind, "error": str(exc)[:300]})
        # Homepage is the origin health authority; subsidiary 404s do not mark it down.
        try:
            home_probe = rows("SELECT data_json FROM data_snapshots WHERE site=%s AND source='public-http:homepage' ORDER BY fetched_at DESC LIMIT 1", (site,))
            ok = bool(home_probe and 200 <= int(json.loads(home_probe[0]["data_json"])["status"]) < 400)
            record_service_probe("origin:" + site, ok, {"source":"seo_scout.homepage"})
        except Exception:
            pass
    append_event("SEO_SCOUT", "scout.completed", {"snapshots":snapshots,"new_findings":findings},
                 "event:" + job["idempotency_key"], entity_type="agent", entity_id="SEO_SCOUT")
    return {"snapshots": snapshots, "new_findings": findings, "production_writes": 0}


def run_controller(job):
    replayed = rebuild_tasks()
    stats = {
        "events": rows("SELECT COUNT(*) n FROM agent_events")[0]["n"],
        "canonical_tasks": rows("SELECT COUNT(*) n FROM canonical_tasks")[0]["n"],
        "pending_clickup": rows("SELECT COUNT(*) n FROM pending_external_sync WHERE target_service='clickup' AND status='pending'")[0]["n"],
        "clickup_mode": "connector-mediated-no-server-credential",
    }
    append_event("PROJECT_CONTROLLER", "controller.reconciled", {"events_replayed":replayed, **stats},
                 "event:" + job["idempotency_key"], entity_type="agent", entity_id="PROJECT_CONTROLLER")
    return {"events_replayed": replayed, **stats}


def run_oracle(job):
    counts = rows("SELECT status,COUNT(*) n FROM job_results WHERE finished_at>=DATE_SUB(%s,INTERVAL 30 DAY) GROUP BY status", (now(),))
    mapped = {r["status"]: int(r["n"]) for r in counts}
    success = mapped.get("succeeded", 0)
    total = sum(mapped.values())
    mean = (success + 1) / (total + 2)
    spread = 1.2815515655 * math.sqrt(max(0, mean * (1 - mean) / (total + 2)))
    lo, hi = max(0, mean - spread), min(1, mean + spread)
    issued = now()
    inserted = 0
    conn = db()
    try:
        with conn.cursor() as cur:
            for horizon in (7, 30, 90):
                stable = f"forecast:control-plane:job-success:{horizon}:{issued.date().isoformat()}"
                cur.execute("""INSERT IGNORE INTO forecasts(id,stable_id,site,metric,horizon_days,p10,p50,p90,model,inputs_json,assumptions_json,data_freshness_json,confidence,issued_at)
                VALUES(%s,%s,'control-plane','job_success_probability',%s,%s,%s,%s,'laplace-smoothed-binomial-normal-interval-v1',%s,%s,%s,%s,%s)""",
                (jid(), stable, horizon, lo, mean, hi, jdump({"window_days":30,"success":success,"total":total}), jdump({"stationary_rate":True,"no_traffic_claim":True,"sparse_data":total<30}), jdump({"as_of":issued,"source":"job_results"}), 0.35 if total<30 else 0.65, issued))
                inserted += cur.rowcount
        conn.commit()
    finally:
        conn.close()
    append_event("ORACLE_FORECASTER", "forecast.completed", {"inserted":inserted,"observations":total,"p10":lo,"p50":mean,"p90":hi},
                 "event:" + job["idempotency_key"], entity_type="agent", entity_id="ORACLE_FORECASTER")
    return {"inserted":inserted,"observations":total,"p10":lo,"p50":mean,"p90":hi,"organic_traffic_forecast":"withheld_no_authorized_data"}


def handle_job(job):
    payload = json.loads(job["payload_json"])
    if job["job_type"] == "test.echo":
        return {"echo": payload, "worker": socket.gethostname()}
    if job["job_type"] == "agent.tick":
        stable = f"event:{job['idempotency_key']}"
        append_event(job["agent"], "tick", payload, stable, entity_type="schedule", entity_id=job["agent"])
        return {"agent": job["agent"], "tick": "recorded"}
    if job["job_type"] == "blackout_sentinel.run":
        return run_sentinel(job)
    if job["job_type"] == "seo_scout.run":
        return run_scout(job)
    if job["job_type"] == "project_controller.run":
        return run_controller(job)
    if job["job_type"] == "clickup_state_steward.run":
        import clickup_state_steward
        return clickup_state_steward.run(job, db, now, jdump, jid, append_event, audit)
    if job["job_type"] == "oracle_forecaster.run":
        return run_oracle(job)
    if job["job_type"] == "temp_tool_harvester.run":
        import tool_harvester
        return tool_harvester.run(job, db, now, jdump, jid, append_event)
    if job["job_type"] == "mistral.chat":
        key = os.environ["MISTRAL_API_KEY"]
        base = os.getenv("MISTRAL_API_BASE", "https://api.mistral.ai").rstrip("/")
        body = {
            "model": payload.get("model") or os.getenv("MISTRAL_DEFAULT_MODEL", "mistral-small-latest"),
            "messages": [{"role": "user", "content": str(payload["prompt"])[:100000]}],
            "temperature": max(0, min(float(payload.get("temperature", 0)), 1.5)),
            "max_tokens": max(1, min(int(payload.get("max_tokens", 512)), 4096)),
        }
        req = urllib.request.Request(base + "/v1/chat/completions", data=jdump(body).encode(), method="POST", headers={"Authorization":"Bearer " + key,"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                data = json.loads(response.read())
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Mistral HTTP {exc.code}") from exc
        choice = (data.get("choices") or [{}])[0]
        return {"model": data.get("model", body["model"]), "text": choice.get("message", {}).get("content", ""), "finish_reason": choice.get("finish_reason"), "usage": data.get("usage")}
    if job["job_type"] == "test.fail":
        raise RuntimeError(payload.get("message", "intentional failure"))
    raise RuntimeError("unsupported job_type: " + job["job_type"])


def finish_job(job, ok, result=None, error=None):
    conn = db()
    try:
        with conn.cursor() as cur:
            status = "succeeded" if ok else ("dead" if job["attempts"] >= job["max_attempts"] else "queued")
            available = now() + dt.timedelta(seconds=min(900, 2 ** min(job["attempts"], 9)))
            cur.execute("INSERT INTO job_results(id,job_id,attempt,status,result_json,error_text,started_at,finished_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                        (jid(), job["id"], job["attempts"], "succeeded" if ok else "failed", jdump(result) if result is not None else None, error, now(), now()))
            cur.execute("UPDATE jobs SET status=%s,available_at=%s,locked_by=NULL,lease_until=NULL,last_error=%s,finished_at=%s WHERE id=%s",
                        (status, available, error, now() if status in ("succeeded", "dead") else None, job["id"]))
            if status == "dead":
                cur.execute("INSERT IGNORE INTO dead_letter_queue(id,job_id,stable_id,agent,job_type,payload_json,attempts,error_text) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                            (jid(), job["id"], "dlq:" + job["stable_id"], job["agent"], job["job_type"], job["payload_json"], job["attempts"], error))
            audit(cur, "finish_job", "job", job["id"], {"status": status, "attempt": job["attempts"]}, f"audit:finish:{job['id']}:{job['attempts']}")
        conn.commit()
    finally:
        conn.close()


def worker_loop():
    worker_id = socket.gethostname() + ":" + str(os.getpid())
    while not STOP.is_set():
        try:
            release_due_schedules()
            job = claim_job(worker_id)
            if not job:
                STOP.wait(2); continue
            try:
                finish_job(job, True, handle_job(job))
            except Exception as exc:
                finish_job(job, False, error=str(exc)[:8000])
        except Exception as exc:
            print(jdump({"level": "error", "event": "worker_loop", "error": str(exc)}), file=sys.stderr, flush=True)
            STOP.wait(5)


def rows(sql, args=()):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args); return cur.fetchall()
    finally:
        conn.close()


class API(BaseHTTPRequestHandler):
    server_version = "MaziyarControlCore/1.0"
    def log_message(self, fmt, *args):
        print(jdump({"event":"http","client":self.client_address[0],"message":fmt % args}), flush=True)
    def auth(self):
        expected = os.environ["CONTROL_API_TOKEN"]
        supplied = self.headers.get("Authorization", "").removeprefix("Bearer ")
        return hmac.compare_digest(expected, supplied)
    def sendj(self, code, value):
        raw = jdump(value).encode(); self.send_response(code); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def body(self):
        n = min(int(self.headers.get("Content-Length", "0")), 1048576)
        return json.loads(self.rfile.read(n) or b"{}")
    def dispatch(self):
        if not self.auth(): return self.sendj(401,{"error":"unauthorized"})
        u=urlparse(self.path); p=u.path.rstrip("/") or "/"; q=parse_qs(u.query)
        if self.command=="GET" and p=="/health": return self.sendj(200,{"status":"ok","backend":"mariadb","time":now().isoformat()+"Z"})
        if self.command=="GET" and p=="/queue/status":
            return self.sendj(200,{r["status"]:r["n"] for r in rows("SELECT status,COUNT(*) n FROM jobs GROUP BY status")})
        if self.command=="GET" and p=="/operator/state":
            return self.sendj(200,get_operator_state())
        if self.command=="POST" and p=="/operator/grok-state":
            a=self.body()
            reported = a.get("state")
            if reported is None and "unattended_blackout" in a:
                reported = "UNATTENDED_BLACKOUT" if a.get("unattended_blackout") is True else "OPERATOR_RETURNED"
            try:
                return self.sendj(200, consume_grok_failover_state(reported, a.get("source_message_id"), a.get("source_user_id"), a.get("details", {})))
            except PermissionError as exc:
                return self.sendj(403, {"error": str(exc)})
            except ValueError as exc:
                return self.sendj(400, {"error": str(exc)})
        if self.command=="GET" and p=="/external-sync":
            status=(q.get("status") or [None])[0]
            sql="SELECT id,stable_id,target_service,entity_type,entity_id,operation,idempotency_key,status,attempts,max_attempts,available_at,expected_external_version,observed_external_version,locked_by,lease_until,completed_at,last_error,created_at,updated_at FROM pending_external_sync"
            return self.sendj(200,rows(sql+(" WHERE status=%s" if status else "")+" ORDER BY created_at DESC LIMIT 200",(status,) if status else ()))
        if self.command=="POST" and p=="/external-sync":
            a=self.body(); return self.sendj(201,queue_external_sync(a["target_service"],a["entity_type"],a["entity_id"],a["operation"],a.get("payload",{}),a["idempotency_key"],a.get("stable_id"),a.get("expected_external_version"),int(a.get("max_attempts",5))))
        if self.command=="POST" and p=="/external-sync/claim":
            a=self.body(); item=claim_external_sync(a["worker_id"],a.get("target_service","clickup"),int(a.get("lease_seconds",300))); return self.sendj(200,item)
        if self.command=="POST" and p.startswith("/external-sync/") and p.endswith("/ack"):
            parts=p.split("/"); a=self.body()
            try: return self.sendj(200,ack_external_sync(parts[2],a["outcome"],a.get("observed_external_version"),a.get("error")))
            except KeyError: return self.sendj(404,{"error":"not_found"})
            except RuntimeError as exc: return self.sendj(409,{"error":str(exc)})
        if self.command=="GET" and p=="/jobs":
            return self.sendj(200,rows("SELECT id,stable_id,idempotency_key,agent,job_type,status,priority,attempts,max_attempts,available_at,created_at,updated_at,finished_at FROM jobs ORDER BY created_at DESC LIMIT 200"))
        if self.command=="GET" and p.startswith("/jobs/"):
            found=rows("SELECT * FROM jobs WHERE id=%s OR stable_id=%s",(p.split("/")[2],p.split("/")[2])); return self.sendj(200,found[0]) if found else self.sendj(404,{"error":"not_found"})
        if self.command=="POST" and p=="/jobs":
            a=self.body(); return self.sendj(201,create_job(a["agent"],a["job_type"],a.get("payload",{}),a["idempotency_key"],int(a.get("priority",100)),int(a.get("max_attempts",5)),a.get("stable_id")))
        if self.command=="POST" and p.startswith("/jobs/"):
            parts=p.split("/"); target=parts[2]; action=parts[3] if len(parts)>3 else ""; conn=db()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM jobs WHERE id=%s OR stable_id=%s",(target,target)); job=cur.fetchone()
                    if not job: return self.sendj(404,{"error":"not_found"})
                    if action=="cancel" and job["status"] in ("queued","running"):
                        cur.execute("UPDATE jobs SET status='cancelled',locked_by=NULL,lease_until=NULL,finished_at=%s WHERE id=%s",(now(),job["id"]))
                    elif action=="retry" and job["status"] in ("failed","dead","cancelled"):
                        cur.execute("UPDATE jobs SET status='queued',available_at=%s,locked_by=NULL,lease_until=NULL,finished_at=NULL,last_error=NULL WHERE id=%s",(now(),job["id"]))
                        cur.execute("UPDATE dead_letter_queue SET resolved_at=%s,resolution_note='retried' WHERE job_id=%s AND resolved_at IS NULL",(now(),job["id"]))
                    else: return self.sendj(409,{"error":"invalid_transition","status":job["status"]})
                    audit(cur,"job."+action,"job",job["id"],{},f"audit:job:{action}:{job['id']}:{jid()}")
                conn.commit(); return self.sendj(200,{"ok":True,"action":action,"job_id":job["id"]})
            finally: conn.close()
        if self.command=="GET" and p=="/schedules":
            return self.sendj(200,rows("SELECT id,stable_id,agent,job_type,interval_seconds,enabled,next_run_at,last_run_at,created_at,updated_at FROM schedules ORDER BY stable_id"))
        if self.command=="GET" and p.startswith("/schedules/"):
            found=rows("SELECT * FROM schedules WHERE id=%s OR stable_id=%s",(p.split("/")[2],p.split("/")[2])); return self.sendj(200,found[0]) if found else self.sendj(404,{"error":"not_found"})
        if self.command=="POST" and p=="/schedules":
            a=self.body(); conn=db()
            try:
                with conn.cursor() as cur:
                    sid=a.get("stable_id") or "schedule:"+jid(); cur.execute("INSERT INTO schedules(id,stable_id,agent,job_type,payload_json,interval_seconds,enabled,next_run_at,max_attempts) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(jid(),sid,a["agent"],a["job_type"],jdump(a.get("payload",{})),int(a["interval_seconds"]),1 if a.get("enabled",True) else 0,now(),int(a.get("max_attempts",5)))); audit(cur,"schedule.create","schedule",sid,a,"audit:schedule:create:"+sid)
                conn.commit(); return self.sendj(201,{"ok":True,"stable_id":sid})
            finally: conn.close()
        if self.command=="GET" and p in ("/audit","/logs"):
            return self.sendj(200,rows("SELECT stable_id,actor,action,entity_type,entity_id,created_at FROM audit_log ORDER BY created_at DESC LIMIT 200"))
        if self.command=="GET" and p=="/results":
            return self.sendj(200,rows("SELECT job_id,attempt,status,result_json,error_text,started_at,finished_at FROM job_results ORDER BY finished_at DESC LIMIT 200"))
        if self.command=="GET" and p=="/worker/status":
            return self.sendj(200,{"host":socket.gethostname(),"pid":os.getpid(),"queue":{r["status"]:r["n"] for r in rows("SELECT status,COUNT(*) n FROM jobs GROUP BY status")}})
        if self.command=="POST" and p.startswith("/schedules/"):
            parts=p.split("/"); sid=parts[2]; action=parts[3] if len(parts)>3 else ""
            conn=db()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM schedules WHERE id=%s OR stable_id=%s",(sid,sid)); s=cur.fetchone()
                    if not s: return self.sendj(404,{"error":"not_found"})
                    if action in ("pause","resume"):
                        cur.execute("UPDATE schedules SET enabled=%s WHERE id=%s",(1 if action=="resume" else 0,s["id"]))
                    elif action=="run-now":
                        idem=f"run-now:{s['stable_id']}:{jid()}"; create_job(s["agent"],s["job_type"],json.loads(s["payload_json"]),idem,max_attempts=s["max_attempts"])
                    else: return self.sendj(400,{"error":"unsupported_action"})
                conn.commit(); return self.sendj(200,{"ok":True,"action":action,"schedule":s["stable_id"]})
            finally: conn.close()
        return self.sendj(404,{"error":"not_found"})
    def do_GET(self):
        try: self.dispatch()
        except Exception as e: self.sendj(500,{"error":str(e)})
    def do_POST(self):
        try: self.dispatch()
        except Exception as e: self.sendj(500,{"error":str(e)})
    def do_PATCH(self):
        try:
            if not self.auth(): return self.sendj(401,{"error":"unauthorized"})
            p=urlparse(self.path).path.rstrip("/"); target=p.split("/")[2]; a=self.body(); allowed={"agent","job_type","payload_json","interval_seconds","enabled","max_attempts","next_run_at"}; fields=[]; vals=[]
            if "payload" in a: a["payload_json"]=jdump(a.pop("payload"))
            for k,v in a.items():
                if k in allowed: fields.append(k+"=%s"); vals.append(v)
            if not fields: return self.sendj(400,{"error":"no_fields"})
            conn=db()
            try:
                with conn.cursor() as cur:
                    vals.extend([target,target]); cur.execute("UPDATE schedules SET "+",".join(fields)+" WHERE id=%s OR stable_id=%s",vals)
                    if not cur.rowcount: return self.sendj(404,{"error":"not_found"})
                conn.commit(); return self.sendj(200,{"ok":True})
            finally: conn.close()
        except Exception as e: self.sendj(500,{"error":str(e)})
    def do_DELETE(self):
        try:
            if not self.auth(): return self.sendj(401,{"error":"unauthorized"})
            p=urlparse(self.path).path.rstrip("/"); target=p.split("/")[2]; conn=db()
            try:
                with conn.cursor() as cur: cur.execute("DELETE FROM schedules WHERE id=%s OR stable_id=%s",(target,target)); n=cur.rowcount
                conn.commit(); return self.sendj(200,{"ok":bool(n)}) if n else self.sendj(404,{"error":"not_found"})
            finally: conn.close()
        except Exception as e: self.sendj(500,{"error":str(e)})


def serve():
    init_db(); seed_schedules()
    t=threading.Thread(target=worker_loop,daemon=True); t.start()
    server=ThreadingHTTPServer((os.getenv("CONTROL_BIND","127.0.0.1"),int(os.getenv("CONTROL_PORT","8770"))),API)
    def stop(*_):
        STOP.set(); threading.Thread(target=server.shutdown,daemon=True).start()
    signal.signal(signal.SIGTERM,stop); signal.signal(signal.SIGINT,stop)
    server.serve_forever()


def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("init-db"); sub.add_parser("seed-schedules"); sub.add_parser("rebuild-tasks"); sub.add_parser("serve")
    p=sub.add_parser("append-event"); p.add_argument("--agent",required=True); p.add_argument("--event-type",required=True); p.add_argument("--stable-id",required=True); p.add_argument("--payload",default="{}")
    p=sub.add_parser("create-job"); p.add_argument("--agent",required=True); p.add_argument("--job-type",required=True); p.add_argument("--idempotency-key",required=True); p.add_argument("--payload",default="{}"); p.add_argument("--max-attempts",type=int,default=5)
    p=sub.add_parser("queue-sync"); p.add_argument("--target-service",default="clickup"); p.add_argument("--entity-type",required=True); p.add_argument("--entity-id",required=True); p.add_argument("--operation",required=True); p.add_argument("--idempotency-key",required=True); p.add_argument("--stable-id"); p.add_argument("--expected-external-version"); p.add_argument("--payload",default="{}"); p.add_argument("--max-attempts",type=int,default=5)
    p=sub.add_parser("claim-sync"); p.add_argument("--worker-id",required=True); p.add_argument("--target-service",default="clickup"); p.add_argument("--lease-seconds",type=int,default=300)
    p=sub.add_parser("ack-sync"); p.add_argument("--target",required=True); p.add_argument("--outcome",required=True,choices=("succeeded","retry","conflict","quarantined")); p.add_argument("--observed-external-version"); p.add_argument("--error")
    p=sub.add_parser("status")
    a=ap.parse_args()
    if a.cmd=="init-db": init_db(); print("ok")
    elif a.cmd=="seed-schedules": seed_schedules(); print("ok")
    elif a.cmd=="rebuild-tasks": print(rebuild_tasks())
    elif a.cmd=="serve": serve()
    elif a.cmd=="append-event": append_event(a.agent,a.event_type,json.loads(a.payload),a.stable_id); print("ok")
    elif a.cmd=="create-job": print(jdump(create_job(a.agent,a.job_type,json.loads(a.payload),a.idempotency_key,max_attempts=a.max_attempts)))
    elif a.cmd=="queue-sync": print(jdump(queue_external_sync(a.target_service,a.entity_type,a.entity_id,a.operation,json.loads(a.payload),a.idempotency_key,a.stable_id,a.expected_external_version,a.max_attempts)))
    elif a.cmd=="claim-sync": print(jdump(claim_external_sync(a.worker_id,a.target_service,a.lease_seconds)))
    elif a.cmd=="ack-sync": print(jdump(ack_external_sync(a.target,a.outcome,a.observed_external_version,a.error)))
    elif a.cmd=="status":
        print(jdump({
            "jobs": rows("SELECT status,COUNT(*) n FROM jobs GROUP BY status"),
            "schedules": rows("SELECT stable_id,agent,enabled,next_run_at,last_run_at FROM schedules ORDER BY stable_id"),
            "events": rows("SELECT COUNT(*) n FROM agent_events"),
            # Preserve historical totals while exposing the operational truth.
            "dlq": rows("SELECT COUNT(*) n FROM dead_letter_queue"),
            "dlq_resolution": rows(
                "SELECT IF(resolved_at IS NULL,'unresolved','resolved') status,COUNT(*) n "
                "FROM dead_letter_queue GROUP BY status"
            ),
            "operational": {
                "unresolved_dlq": rows(
                    "SELECT COUNT(*) n FROM dead_letter_queue WHERE resolved_at IS NULL"
                )[0]["n"],
                "dead_jobs_with_unresolved_dlq": rows(
                    "SELECT COUNT(*) n FROM jobs j JOIN dead_letter_queue d ON d.job_id=j.id "
                    "WHERE j.status='dead' AND d.resolved_at IS NULL"
                )[0]["n"],
            },
        }))


if __name__=="__main__": main()
