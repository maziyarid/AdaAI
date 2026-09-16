# First real pilot — existing Mistral, shadow first

Do not replace Mistral yet. Prove that the execution contract fixes the current failure mode.

## Shadow phase
Choose one existing academic content job. Mistral receives the same task but has no production mutation tool. Capture:
- target URL/post ID proposal
- canonical-owner decision
- content candidate/diff
- intended tool call
- validator outputs
- authorization decision
- expected postcondition

Compare against the correct expected result and store the trace as AdaEval data.

## Canary phase
After shadow performance is acceptable, enable exactly one low-risk mutation, such as a non-critical metadata correction or approved draft update. Required:
- current receipt
- known site/resource
- snapshot
- idempotency key
- deterministic validators
- live readback
- explicit pass/fail

Do not start with deletion or “publish on all sites”.

## Promotion criteria
Only widen the worker passport after repeated canary success and zero silent verification failures. Then test a local model against the same AdaEval suite; the model is interchangeable, the safety contract is not.
