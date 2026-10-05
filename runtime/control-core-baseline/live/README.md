# Live control-core source snapshot

Verified recapture of `/opt/maziyar-control-core` from `server.maziyarid.com`
after the Google approval authority promotion on 2026-10-05.

This directory is the Git snapshot of the **deployed** control-core source. It is
not a second scheduler or approval authority. Production remains
`/opt/maziyar-control-core` on the VPS.

## Verified production state

- `control_core.py` — 80,970 bytes / 1,430 lines
- SHA-256: `c414daf278048e7d88764a112605b39ab771a267aeac1880863383a6748b7e9a`
- mode: `0555 root:root`
- service: `maziyar-control-core.service`
- listener: loopback-only through the existing control-core configuration
- unauthenticated `/health`: HTTP 401 by design
- unauthenticated `/approvals`: HTTP 401 by design

## Approval extension

The live source now references the durable ADA approval tables installed through
the reviewed MariaDB migration. It does **not** create those tables inline.

Production MariaDB verification observed 42 tables, including:

- `ada_approval_tickets`
- `ada_approval_events`
- `ada_snapshots`
- `ada_mutation_journal`
- `ada_verifications`
- `ada_external_inputs`

Approval authority remains split by credential:

- `CONTROL_MS_ROBOT_TOKEN`: request/read/proof/consume path for Ms Robot
- `CONTROL_APPROVAL_TOKEN`: human list/grant/deny path
- `CONTROL_APPROVAL_SIGNING_KEY`: server-only one-time proof derivation
- existing `CONTROL_API_TOKEN`: does not grant approval operations

Secret values are not captured here.

## Human approval surfaces

The same authority can be operated through:

- paired/private Ada Telegram commands when the Telegram bot credential is
  configured;
- the root/operator `ada-google-approval` CLI as the current fallback.

The CLI deliberately cannot claim or consume approval proofs.

## Source-of-truth note

The previous September snapshot is superseded by this verified October
recapture. The candidate under
`runtime/control-core-baseline/candidates/google-approval/` remains useful as
review history, but this `live/` directory now reflects execution truth.
