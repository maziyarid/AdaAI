# ADR 0001 — MariaDB, not PostgreSQL, for Phase 1

Status: accepted  
Date: 2026-09-16

The live control plane already uses MariaDB 10.11. Deploying the prototype PostgreSQL Context Core would create two sources of truth.

Phase 1 adds `ada_*` tables to the existing MariaDB instance and keeps `maziyar-control-core` as the job/scheduler authority.

PostgreSQL/pgvector is deferred until the reliability contract is proven and a deliberate migration is approved.
