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

## Repository authority and naming

Canonical product name is Ms Robot. The historical repository identifier maziyarid/Canopy remains unchanged until AAX-42 completes source reconciliation.

This bridge is transport only. Ms Robot remains operations/data/UI; Ada remains governed intelligence/orchestration. The bridge must never grant scheduler, lease, shell, SQL, or approval authority.

Payloads containing obvious credential-bearing keys are rejected before persistence. Secrets remain in service-owned configuration only.
