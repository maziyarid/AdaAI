# Control-core Agiflow ACK lease fencing

Live baseline SHA-256:
aec6639acf761dfb01a72feb670b4d841c25fb1e8000abdea41bca0dcf4a94f3.

Prepared candidate SHA-256:
7cb3d84c7010d4902c96cd2eee5cb1df43b050519abb7d962e7a08d5836721cb.

The preparation script checks that exact live baseline, replaces four unique
anchors, validates Python syntax and creates a new candidate. It does not
install or restart anything. A changed baseline requires reconciliation rather
than weakening the hash guard.

For Agiflow, an ACK must carry the owner and attempt generation issued by
control-core. The server rejects missing/malformed bindings, another owner,
an earlier attempt, or an expired lease. Its final SQL update is also bound
to status, owner, attempt and unexpired lease, and must affect exactly one row.
This preserves control-core as the only claim/lease authority.

Other target services keep their existing API parameters. The final conditional
update also prevents an expired claim from updating their rows. Terminal ACK
repetition is a read-only return; an older Agiflow generation still fails.

Agiflow ACK is supported through the paired HTTP consumer. The existing legacy
`ack-sync` CLI cannot supply the fenced owner/attempt parameters and therefore
fails closed for Agiflow; do not use it to bypass the HTTP contract. Its other
target-service interfaces are preserved.

## Verification

pytest ops/control-core-hardening/tests

The isolated rehearsal runs the staged queue/claim/ACK functions against a new
MariaDB datadir and Unix socket under /tmp, with networking disabled and a
disposable marker. It validates wrong-owner rejection, lease expiry, same-worker
reclaim fencing, valid success and repeated terminal ACK. It destroys the
database and does not import production environment configuration.

    /opt/maziyar-control-core/venv/bin/python \
      ops/control-core-hardening/isolated_ack_rehearsal.py \
      --candidate /tmp/ada-closure-evidence-20260930/control_core.candidate.py

## Activation and rollback

Explicit approval is required before live control-core replacement/restart.
Recheck the baseline hash, preserve the current root-only source backup and
coordinate with the existing jobs/leases. Install the paired server and consumer
changes together in one controlled window. No SQL migration or new scheduler
is needed for this protocol change.

Record pre/post service health and source hashes. Perform only an explicitly
approved disposable live external-sync canary before allowing queue replay.
Neither a provider probe nor a green offline suite authorises draining queued
records or sending their messages.

If checks fail, stop only the consumer timer, restore the previous core source,
restart the existing core under the normal operator procedure, and retain all
queue/evidence records. Keep the consumer parked while the provider denies
access; reverting to the old code must not restart the known hot loop.
