# Live control-core vs prototype divergence

Captured 2026-09-16 during Phase-1 implementation. Live VPS was not reachable from this sandbox (no SentinelX/SSH connector), so live facts below are from repository architecture docs verified on 2026-09-16 — not a fresh host dump.

| Topic | Prototype `ada-context-core/` | Live VPS (documented) | Phase-1 decision |
| --- | --- | --- | --- |
| Database | PostgreSQL + pgcrypto + jsonb + plpgsql | MariaDB 10.11 | Additive MariaDB `ada_*` tables. Do not install PostgreSQL. |
| Scheduler | New Context Core task_runs | `maziyar-control-core` jobs/schedules/leases/retries/DLQ | Keep live scheduler. Ada attaches receipts/approvals/journal. |
| Listen | 127.0.0.1:8791 | 127.0.0.1:8770 | Do not bind a second production control port. |
| Service | `ada-context-core.service` | `maziyar-control-core.service` | Do not deploy a parallel unit. |
| Worker | none | `maziyar-mistral-worker` :9102 | Wrap in shadow mode. Do not replace. |
| Memory freshness | scoped versions (good) | not present yet | Implement scoped receipts in Ada layer. |
| Provenance enum | includes TEMPORARY / DEPRECATED | n/a | Use mission enum: PROPOSED, OBSERVED, CONFIRMED, VERIFIED, CANONICAL, SUPERSEDED. |
| Recovery docs | PostgreSQL WAL | MariaDB binlog / PITR | MariaDB-only runbooks. |
| Qalam | pointer table only | files live in `maziyarid/agents` + archive | Mirrored into `skills/` with hashes. |
| Import of `/opt/maziyar-control-core` | not present | source on VPS | **Blocked** — no VPS read access this session. Adapter + captured behavior tests committed instead. |

Prototype contracts that we kept:

- fail closed
- scoped receipts
- HMAC inside one trust boundary with alg/key_id for later Ed25519
- untrusted external quarantine
- payload-bound approvals
- mutation journal idempotency
