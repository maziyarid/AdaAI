# AAX-11 — staged portfolio-dispatcher supervision

This directory is a deployment package, not a deployed service.

The dispatcher unit runs the existing durable dispatcher under systemd with
Restart=on-failure. The dispatcher already writes pd_heartbeat every 60 seconds.
A two-minute watchdog opens factory.sqlite3 read-only and only recommends a
restart for a missing, invalid, or stale dispatcher heartbeat. Expired leases
and open circuits are surfaced as degraded evidence but do not cause restart
loops. The recovery unit is rate-limited to three activations per hour.

## Fail-closed deployment rule

The staged dispatcher unit both declares DISPATCH_ENABLED=false and forces it again
in ExecStart via /usr/bin/env. The ExecStart override is the fail-closed boundary:
an operator environment file cannot enable live dispatch. Installing these units therefore gives supervised observation mode
only. Changing that line is a separate production decision requiring the AAX-10
replacement/retirement gates and explicit human approval.

Do not enable or start these units merely because they exist in the repository.

## Pre-deploy validation

Run the focused pytest file and systemd-analyze verify over all four staged
units. A production install/start remains outside repository validation. After
an approved install, AAX-11 still requires a supervised stale-heartbeat recovery
test, a fresh heartbeat read-back, proof of zero duplicate production mutation,
and Agiflow projection evidence before closure.
