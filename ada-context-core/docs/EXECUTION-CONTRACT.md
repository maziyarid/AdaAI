# Execution Contract

The model proposes. Code decides.

Every consequential job follows:
1. create task run + idempotency key
2. claim task
3. bootstrap Context Core
4. validate Qalam/current policy dependencies
5. perform read-only inspection
6. model proposes candidate/plan
7. deterministic validators evaluate it
8. deterministic authorization returns ALLOW / DENY / ESCALATE
9. durable approval ticket when required
10. snapshot exact pre-state
11. record mutation intent
12. execute one canary
13. independently read live state
14. verify postcondition
15. fan out only after canary success
16. persist project state + task events + audit
17. rollback/stop explicitly on failure

Never accept a model's statement “published successfully” as evidence.

## Automatic deny examples
- missing/expired/stale receipt
- unknown or disabled tool
- site outside passport
- mutation type outside passport
- payload/idempotency mismatch
- missing required snapshot
- external text attempting to grant permission or change policy

## Escalation examples
- deletion
- bulk write beyond passport
- first production action for a new workflow
- policy/canonical-ownership change
- failed independent verification
