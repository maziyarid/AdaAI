# Agiflow external-sync consumer

Recovered on 2026-09-30 from the live consumer at
/srv/maziyar-wp-mcp/deploy/agiflow_external_sync_consumer.py.
Baseline SHA-256: 99cd36f199a7e10e28840c4ff6e90e2a4997e8ba93b73381557fc999a0447aaf.

Control-core pending_external_sync remains the queue, lease and replay authority.
This package does not introduce another scheduler or drain the queue during tests.

## Behaviour

The existing oneshot consumer uses one durable connector circuit file plus a
non-blocking process lock. HTTP 4xx failures other than 408/425/429 park the
connector; subsequent timer ticks do no network or queue work. Transient failures
back off from 60 seconds to at most 900 seconds. State is atomically replaced,
fsynced and mode 0600. Invalid state fails closed. The circuit is availability
metadata only; it holds no jobs, comments, credentials or recovery ownership.

Queue binding, core HTTP and lease errors are reported in the queue domain;
they cannot permanently latch a healthy Agiflow connector. A failed reset probe
preserves an existing permanent latch. Provider failures retain their own
classification even if the retry ACK fails. An incomplete bounded comment scan
can reconcile an existing marker, but cannot authorise a new comment.

If a bounded scan is incomplete and no marker is observed, the existing queue
item becomes quarantined with COMMENT_SCAN_LIMIT_EXCEEDED. Normal claims exclude
it, so later invocations do not rescan the same history. The connector remains
available for other items. The same rule applies to incomplete verification
after a create whose outcome is uncertain. Operator reconciliation must inspect
the existing task/marker before authorising a retry; never enqueue a replacement
with a new idempotency key. Queue records and their evidence are retained.

Provider bodies and queue payloads are excluded from stdout and circuit state.
Acknowledgements carry the server-issued owner and attempt generation; the
paired control-core patch rejects stale or expired claims. Before comment
creation, the consumer requires 80 seconds of remaining lease budget. An ACK
requires 20 seconds. A lost create response or ACK is reconciled against the existing stable comment
marker before a new comment is created. A permanent failure after a claim leaves
the item retryable in control-core while the connector itself is parked.

## Approval and activation

This package is staged. AAX-24 requires explicit production activation approval.
Deploy the paired control-core ACK patch from ops/control-core-hardening before
allowing normal queue consumption. Before install, confirm the live file still has the baseline hash, take a
root-only backup of that code and the current unit/drop-ins, and confirm no
consumer invocation is running. Do not back up or print environment secrets.

After approval, install both Python files together into
/srv/maziyar-wp-mcp/deploy as root-owned 0644 files. Reuse the existing
maziyar-agiflow-external-sync-consumer.service and timer; do not add a timer.
The existing service uses /usr/bin/python3 and writes only the permitted state
directory. Verify compatibility with that interpreter before install.

The default circuit path is
/srv/maziyar-wp-mcp/state/agiflow-consumer-circuit.json.
Expected first run with the currently blocked endpoint: PARKED / HTTP_403.
Following ticks must remain PARKED without more provider calls or queue claims.
Do not mark Agiflow delivery recovered while the provider denies access.

Repair the supported Agiflow integration with its owner. Do not spoof browser
signatures or route around its access restriction. Under the normal protected
service environment, --reset-circuit performs exactly one read-only probe.
It resets the latch only on success and never claims an item in that invocation.
--probe alone does not reset the circuit. Review the queued records before
permitting a separate normal --once invocation after reset.

## Rollback

Stop only the existing consumer timer, wait for its current oneshot to exit,
restore the backed-up code and unit/drop-ins, and reload systemd if units changed.
Leave all queue records, markers and circuit evidence intact. The old consumer
has a known retry-loop defect: keep its timer stopped until the access problem
is repaired. Rolling back code is not permission to resume the defective loop.

## Verification

pytest ops/agiflow-consumer/tests
Tests use isolated fakes/subprocesses; no production claim, ACK or comment occurs.
Live delivery and production restart/replay remain separate acceptance gates.
