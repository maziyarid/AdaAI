# Qalam runtime routing — Ada Context Core is authoritative

Previous Qalam runtime used:

```text
Qalam → XMemo (primary) → Engram (secondary)
```

Ada Phase 1 changes the runtime to:

```text
Qalam
  ↓
Ada Context Core — authoritative memory, receipts, policy, state
  ↓
optional XMemo / Engram mirrors and history
```

## Rules

1. Bootstrap Context Core before loading writing overlays.
2. A writing task receipt MUST include the active Qalam release + content hash.
3. XMemo and Engram may receive async mirrors. Mirror failure does not block Ada.
4. Workers must not embed a replacement style system.
5. Teznevise zero-U+200C is a site overlay, not a global Persian rule.
6. fa-IR UX overlay (`ux-writing-fa-ir.md`) and `fa-ir-product-lexicon.md` remain canonical for product copy.

See `skills/qalam/REGISTRY.json` for hashed assets.
