# Ada ↔ Ms Robot bridge contract v1

Ms Robot is the canonical product name for the system formerly called Canopy.

The bridge is a local durable event boundary. It is not an executor, scheduler, secret store, or source of runtime truth.

## Authority
- VPS/database/queues: runtime truth.
- Git: code truth.
- Agiflow: durable project/incident/decision coordination.
- Ada: conversational/operator and bounded reasoning layer.
- Ms Robot: operations UI, inquiry/analytics hub and agent workspace.
- Telegram: delivery/interaction channel only.

## Transport
Loopback HTTP on 127.0.0.1:9110.
State: /var/lib/ms-robot-bridge/events.sqlite3.
Schema: event-envelope.schema.json.

## Safe event families
- ada.alert.queued / ada.alert.recovered
- ada.operator.handoff
- ada.language_feedback.approved
- ms_robot.inquiry.created
- ms_robot.inquiry.routed
- ms_robot.analytics.signal
- ms_robot.medical_admin.event
- ms_robot.action.proposal
- ms_robot.delivery.failure

Ms Robot action proposals never execute by crossing this bridge. Consequential actions must pass Ada/control-plane authorisation separately.

## Idempotency
Every event must have a stable idempotency_key. Reusing a key with identical payload returns the existing event. Reusing it with a different payload fails closed.

## Privacy
Do not put credentials, OTPs, raw authentication headers, private keys, medical records, or full sensitive customer payloads in the bridge. Use references/IDs and minimum operational fields. Set sensitivity honestly.

## Consumer lifecycle
queued -> delivered -> acked.
A failed consumer can return fail; bounded failures eventually park the event as dead. No event is considered processed from silence alone.

### Scoped bounded listing

Authenticated `GET /v1/events` accepts an optional exact `project_key` and
`site_key` pair alongside target/state/limit. Both scope fields must occur once,
be nonblank, contain no control characters or surrounding whitespace, and fit
160 characters. Partial, blank, repeated or malformed scopes return 400.
Filtering happens before the existing bounded limit, so another tenant's backlog
cannot starve scoped intake. A scoped response confirms the exact pair in
`scope`; requests without either field retain the existing global response.
Scope is a consumer selection boundary, not a new credential or approval grant.

Transition paths percent-decode the event ID after splitting the raw path into
segments. Stable reference IDs containing a colon or slash remain addressable
when properly encoded; SQL continues to use parameterised identity lookup.
Authentication, queue states, attempt budgets and execution authority are
unchanged. Old bridge installations without a confirmed scoped-list capability
must not be used for the new tenant-scoped consumer.

### Exact event confirmation

Authenticated `GET /v1/events/<encoded-event-id>` requires one valid `target`
and the exact `project_key`/`site_key` pair. It returns `event` with the existing
public envelope fields and confirms the pair in `scope`. It can address queued,
delivered, acked and dead events, including an ACK whose response was lost.
Missing and out-of-scope identities both return 404. Malformed scope/target
returns 400; authentication precedes any identity lookup. The endpoint does not
change event state, attempts or timestamps and never returns `last_error`.

The consumer uses this lookup only for its bounded, durable pending receipts.
It validates the complete returned envelope and compares its canonical identity
fingerprint with the stored receipt before confirming an `acked` state locally.
Matching queued/delivered records may resume the ordinary receipt-first lifecycle.
Missing, changed, dead, malformed or unavailable records remain unconfirmed and
receive no transition from reconciliation. An ACK never grants action authority.
Legacy installations lacking this endpoint cannot automatically reconcile an
uncertain ACK; they must retain the receipt and require operator verification.

## Repository authority and naming

Canonical product name is Ms Robot. The historical repository identifier maziyarid/Canopy remains unchanged until AAX-42 completes source reconciliation.

This bridge is transport only. Ms Robot remains operations/data/UI; Ada remains governed intelligence/orchestration. The bridge must never grant scheduler, lease, shell, SQL, or approval authority.

Payloads containing obvious credential-bearing keys are rejected before persistence. Secrets remain in service-owned configuration only.
