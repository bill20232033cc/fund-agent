# Evidence Confirm Productionization RR-09 A1 Controller Judgment

Verdict token:

`ACCEPT_RR_09_A1_R1_R4_FACT_DIAGNOSTIC_ROUTE_A1C_NOT_READY`

## Scope

Controller judgment for:

- Evidence artifact: `docs/reviews/evidence-confirm-productionization-rr-09-a1-fact-diagnostic-evidence-20260624.md`
- Gate: `RR-09 A1 R1-R4 Fact-level Diagnostic Authorization`
- User authorization: `授权 RR-09 A1 repository-bounded live/PDF fact diagnostics`

No source code, tests, production behavior, quality-gate semantics, provider/LLM path, checklist support, report-body rendering, PR state, tag, release, or readiness state was changed.

## Decision

Accept the A1 diagnostic evidence.

The A1 diagnostic covered all four R1-R4 samples, so the disposition is not single-sample-only:

| Residual | Sample | Diagnostic coverage |
|---|---|---|
| R1 | `004393 / 2025` | covered |
| R2 | `004194 / 2024` | covered |
| R3 | `006597 / 2024` | covered |
| R4 | `110020 / 2024` | covered |

Accepted facts:

- All four samples used EID `single_source_only` metadata with fallback disabled/unused and admitted source provenance.
- All four samples had `reference_count=0` because repository-bounded reference materialization rejected current product projection locators.
- Dominant materializer reasons were `unsupported_row_locator_format` and `row_locator_without_table_id`.
- V2 failures were dominated by `missing_evidence` and `source_support`.
- A0 helper classified the dominant root cause as `projection_attachment_defect`.

Accepted classification:

`A1-C projection/source attachment defect`

The current R1-R4 issue is no longer an unclassified product EC fail residual. It is a targeted product projection / anchor locator / reference materializer defect. This does not make R1-R4 release-ready; it only identifies the next fix route.

## Rejected Claims

- Do not claim source/PDF pathway failure for R1-R4; source provenance was admitted.
- Do not claim deterministic V2 false-positive as the dominant cause; no value-match pattern is needed to explain this diagnostic.
- Do not claim product facts are semantically correct or incorrect; the diagnostic did not inspect raw excerpts.
- Do not claim release/readiness; R1-R4 still require targeted fix and re-evidence.

## Residuals

| Residual | Status | Owner / next destination |
|---|---|---|
| R1-R4 EC `fail` under `warn` | classified, still release-blocking | `RR-09 A1-C R1-R4 Projection / Anchor Locator / Reference Materializer Fix Planning Gate`. |
| `017641 / 2024` quality-gate/runtime re-evidence | open | B1 runtime re-evidence authorization. |
| Checklist Evidence Confirm support | deferred | Separate gate. |
| Report-body Evidence Confirm rendering | deferred | Separate gate. |
| Provider-backed semantic production default | deferred | Separate gate. |
| Tag/release/readiness | blocked | Separate release-boundary authorization and accepted readiness evidence. |

## Next Entry Point

`RR-09 A1-C R1-R4 Projection / Anchor Locator / Reference Materializer Fix Planning Gate / RR-09 B1 Runtime Re-evidence Authorization`

Release/readiness remains `NOT_READY`.

Completion token:

`ACCEPT_RR_09_A1_R1_R4_FACT_DIAGNOSTIC_ROUTE_A1C_NOT_READY`
