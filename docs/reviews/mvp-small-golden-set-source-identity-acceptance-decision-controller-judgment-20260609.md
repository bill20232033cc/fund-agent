# Source Identity Acceptance Decision Controller Judgment

## Gate Metadata

- Gate: `source identity acceptance decision gate`.
- Classification: `standard`.
- Date: 2026-06-09.
- Decision artifact: `docs/reviews/mvp-small-golden-set-source-identity-acceptance-decision-20260609.md`.
- Decision manifest: `docs/reviews/mvp-small-golden-set-source-identity-acceptance-decision-20260609.json`.
- Reviews: `docs/reviews/mvp-small-golden-set-source-identity-acceptance-decision-review-ds-20260609.md`; `docs/reviews/mvp-small-golden-set-source-identity-acceptance-decision-review-mimo-20260609.md`.

## Judgment

Accepted.

The gate is accepted because the decision artifacts classify all five rows from the accepted docs-only manual evidence intake payload, preserve the approved source route policy, and keep all downstream unlocks row-field gated. EID remains a preferred official registry locator, not a mandatory extraction source or exclusive truth source. Official document URLs may originate from EID, fund-company official PDF, CNINFO PDF, or another official/first-party disclosure platform when the accepted identity anchors are recorded.

## Accepted Row Decisions

| fund_code | report_year | decision | unlock |
|---|---:|---|---|
| `004393` | 2024 | `matched` | retained excerpt fixture gate only |
| `004194` | 2024 | `matched_without_hash` | retained excerpt fixture gate only |
| `006597` | 2024 | `matched_without_hash` | retained excerpt fixture gate only |
| `110020` | 2024 | `matched_without_hash` | retained excerpt fixture gate only |
| `017641` | 2024 | `matched_without_hash` | retained excerpt fixture gate only |

## Boundary

This judgment does not accept exact/numeric extractor correctness, does not create retained excerpts or expected values, does not project fixtures, does not change extractors, and does not promote golden/readiness or quality gate semantics.

No source/PDF/network/FundDocumentRepository/live/provider/fallback access was authorized or performed in this gate. No provider/default/runtime/budget/config, Chapter calibration, Agent runtime expansion, multi-year, score-loop, release, merge, PR readiness, or external state change is accepted.

## Residuals

- `004194`, `006597`, `110020`, and `017641` remain `matched_without_hash`; PDF hash absence is a retained-excerpt gate residual, not an extractor correctness unlock.
- `017641` remains QDII and non-promotion-ready. This acceptance only concerns source identity routing into retained excerpt work.
- Exact/numeric correctness remains blocked until a later gate accepts matched source identity plus retained row-field excerpts and expected values.

## Next Entry

Next gate: `retained excerpt fixture gate for accepted rows only`.

The next gate may only retain minimal same-source excerpts, page or section anchors, and field-level expected values for accepted rows. It must not modify extractors or fixtures beyond the separately authorized retained excerpt fixture scope, and it must not write row-field extractor correctness tests until retained excerpts are accepted.
