# Memory Contract

## Meaning of “never forget”

Not every historical fact is injected into every prompt. The enforceable guarantee is:

> No consequential task may begin without a valid context receipt proving the current mandatory records for its exact scopes were loaded.

### Deterministic Layer A
Bootstrap loads ACTIVE P0/P1 records for:
- global `*`
- matching project
- matching site
- matching task type
- matching agent
- active Qalam release dependency
- current project state/lane

This layer never depends on embeddings.

### Scoped freshness
Each scope has its own monotonically increasing version. A receipt stores every scope/version it used. A change to `site:teznevise.ir` invalidates jobs that loaded that site, but does not invalidate an unrelated Royadarman analytics task. A global policy change invalidates everyone because everyone depends on `global:*`.

### Supersession
History is preserved. New canonical records supersede old ones. Normal bootstrap retrieves only ACTIVE records; historical queries may inspect superseded versions.

### Authority and provenance
P0/P1 promotion is controlled. Agent observations, scraped text, and semantic recall cannot automatically become canonical policy. Provenance is explicit (`PROPOSED`, `OBSERVED`, `CONFIRMED`, `VERIFIED`, etc.).

### External mirrors
XMemo and Engram are asynchronous mirrors/search aids. Mirror failure does not redefine truth. They never override Context Core.
