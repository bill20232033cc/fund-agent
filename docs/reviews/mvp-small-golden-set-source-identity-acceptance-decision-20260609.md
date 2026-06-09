# MVP Small Golden Set Source Identity Acceptance Decision

## Gate Metadata

- Gate: `source identity acceptance decision gate`.
- Classification: `standard`.
- Date: 2026-06-09.
- Input payload: `docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-20260609-source-payload.json`.
- Decision manifest: `docs/reviews/mvp-small-golden-set-source-identity-acceptance-decision-20260609.json`.

## Boundary

This gate performs docs-only row-level source identity decisions. It does not independently verify URLs or PDF contents, read/hash/download PDFs, call `FundDocumentRepository`, use network/EID/akshare/provider/fallback, modify fixtures or extractors, or accept exact/numeric correctness.

## Decision Policy

- `matched`: all required source identity anchors are present and user-provided PDF hash is present.
- `matched_without_hash`: all required source identity anchors are present, but PDF hash is not provided.
- `needs_manual_hash`: source identity anchors are otherwise sufficient, but a downstream gate requires hash before proceeding.
- `rejected_identity_mismatch`: title, publisher, fund code, fund name, share-class mapping, report year or document kind conflicts.
- `deferred_insufficient_evidence`: required source identity anchor is absent.

## Decisions

| fund_code | decision | document origin | hash status | retained excerpt gate |
|---|---|---|---|---|
| `004393` | `matched` | EID official PDF | `user_provided` | allowed |
| `004194` | `matched_without_hash` | EID official PDF | `not_provided` | allowed |
| `006597` | `matched_without_hash` | CNINFO PDF | `not_provided` | allowed |
| `110020` | `matched_without_hash` | fund-company official PDF | `not_provided` | allowed |
| `017641` | `matched_without_hash` | fund-company official PDF | `not_provided` | allowed |

## Non-Accepted Scope

- Matched or matched-without-hash status only unlocks the retained excerpt fixture gate.
- No row unlocks exact/numeric extractor correctness.
- No row receives expected values.
- No fixture projection is performed.
- No golden/readiness, quality gate, provider/default/runtime/budget/config, Agent runtime, multi-year or score-loop state changes.
- No fallback evidence is accepted as source truth.

## Residuals

- Four rows remain without user-provided PDF hash: `004194`, `006597`, `110020`, `017641`.
- The retained excerpt fixture gate must decide whether hash absence is acceptable for field-level excerpts, whether a row should pause as `needs_manual_hash`, or whether user-provided field excerpts are sufficient for the narrow row-field key.
- QDII row `017641` remains non-promotion-ready; acceptance here only concerns annual-report source identity.

## Next Entry

Next gate: `retained excerpt fixture gate for accepted rows only`.

Only rows with `matched` or `matched_without_hash` may enter. The gate must retain minimal same-source row-field excerpts and expected values before any row-field extractor correctness tests can be written.
