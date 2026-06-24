# Evidence Confirm Productionization RR-09 A4 Live/PDF Re-evidence

Verdict token:

`RR_09_A4_R1_R4_LIVE_PDF_REEVIDENCE_NO_RUNTIME_IMPROVEMENT_NOT_READY`

## Scope

Gate: `RR-09 A4 R1-R4 live/PDF re-evidence after A4-S1 no-live fixes`.

User authorization:

`授权 RR-09 A4 R1-R4 live/PDF re-evidence after A4-S1 no-live fixes`

Accepted prerequisite:

- A4-S1 implementation commit: `04c9124`
- A4-S1 controller judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a4-code-review-controller-judgment-20260624.md`
- Authorization precheck: `docs/reviews/evidence-confirm-productionization-rr-09-a4-r1-r4-live-reevidence-authorization-precheck-20260624.md`

This gate re-ran repository-bounded product fact diagnostics for R1-R4 after A4-S1 no-live materializer support for Processor-style row locators.

No product CLI command, provider/LLM command, checklist support, report-body rendering, V2/ECQ/quality-gate semantic change, push, PR mutation, tag, release or readiness promotion was performed.

## Command

Executed authorized live/PDF re-evidence:

```bash
uv run python - <<'PY'
...
bundle = await FundDataExtractor().extract(fund_code, report_year, force_refresh=True)
projection = project_chapter_facts(bundle)
runner_result = await run_repository_bounded_evidence_confirm(
    EvidenceConfirmRepositoryRunRequest(
        fund_code=fund_code,
        report_year=report_year,
        projection=projection,
        force_refresh=False,
    )
)
diagnostic = summarize_value_match_diagnostics(...)
...
PY
```

Execution result:

- First wrapper attempt exited `1` because the local evidence summarizer tried to read a non-existent `EvidenceConfirmRepositoryRunResult.parsed_report` attribute. This was a local summary-script defect, not a repository/source/PDF/V2 result.
- Corrected wrapper exited `0`.
- Output type: safe aggregate JSON only.
- No raw annual-report excerpt, raw scalar token value, full structured value, PDF/cache path, URL, source-helper internals, provider payload, report body text or secret was emitted.

## Source Pathway

All four samples loaded through EID single-source metadata and admitted source provenance:

| Residual | Sample | Selected source | Source mode | Fallback enabled | Fallback used | Metadata admitted |
|---|---|---|---|---:|---:|---:|
| R1 | `004393 / 2025` | `eid` | `single_source_only` | false | false | true |
| R2 | `004194 / 2024` | `eid` | `single_source_only` | false | false | true |
| R3 | `006597 / 2024` | `eid` | `single_source_only` | false | false | true |
| R4 | `110020 / 2024` | `eid` | `single_source_only` | false | false | true |

No fallback, identity mismatch, schema drift, integrity error, unsupported source or ambiguous repository failure was observed in the safe runner output.

## Reference Materialization

| Residual | Sample | Reference status | Reference count | Row-level refs | Processor row refs | Section downgrade issues | Table downgrade issues | Anchor not applicable | Missing section |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| R1 | `004393 / 2025` | pass | 144 | 6 | 0 | 22 | 116 | 2 | 0 |
| R2 | `004194 / 2024` | pass | 144 | 6 | 0 | 22 | 116 | 2 | 0 |
| R3 | `006597 / 2024` | fail | 195 | 5 | 0 | 28 | 162 | 2 | 3 |
| R4 | `110020 / 2024` | pass | 158 | 6 | 0 | 29 | 123 | 2 | 0 |

Interpretation:

- A4-S1 did not regress source provenance.
- A4-S1 did not regress reference counts.
- A4-S1 did not materialize any Processor-style row locator in the current R1-R4 runtime projections: `processor_row_locator_rows=0` for all four samples.
- No `processor_row_locator_*` blocking issue appeared in the safe output.
- R3 still has `missing_section=3`.

## Strict V2 Result

Strict deterministic V2 still fails for all four samples:

| Residual | Sample | Overall status | Score | Fail facts | Warn facts | Not applicable facts | V2 issue count |
|---|---|---|---:|---:|---:|---:|---:|
| R1 | `004393 / 2025` | fail | 40 | 8 | 26 | 19 | 230 |
| R2 | `004194 / 2024` | fail | 40 | 15 | 20 | 18 | 238 |
| R3 | `006597 / 2024` | fail | 40 | 15 | 17 | 21 | 284 |
| R4 | `110020 / 2024` | fail | 40 | 15 | 24 | 14 | 280 |

Dimension counts:

| Residual | `value_match:fail` | `value_match:pass` | `value_match:not_applicable` | `missing_evidence:fail` | `anchor_precision:warn` |
|---|---:|---:|---:|---:|---:|
| R1 | 8 | 26 | 19 | 0 | 34 |
| R2 | 15 | 20 | 18 | 0 | 35 |
| R3 | 15 | 17 | 21 | 0 | 32 |
| R4 | 15 | 24 | 14 | 0 | 39 |

Failing source-field buckets:

| Residual | Failing buckets |
|---|---|
| R1 | `structured.nav_benchmark_performance:value_match=4`; `structured.manager_alignment:value_match=2`; `structured.manager_strategy_text:value_match=2` |
| R2 | `structured.fee_schedule:value_match=7`; `structured.nav_benchmark_performance:value_match=4`; `structured.manager_alignment:value_match=2`; `structured.manager_strategy_text:value_match=2` |
| R3 | `structured.fee_schedule:value_match=7`; `structured.nav_benchmark_performance:value_match=4`; `structured.manager_alignment:value_match=2`; `structured.manager_strategy_text:value_match=2` |
| R4 | `structured.fee_schedule:value_match=7`; `structured.nav_benchmark_performance:value_match=4`; `structured.manager_alignment:value_match=2`; `structured.manager_strategy_text:value_match=2` |

## Diagnostic Classification

| Residual | Diagnostic records | `coarse_reference_insufficient` | `not_applicable` |
|---|---:|---:|---:|
| R1 | 34 | 8 | 26 |
| R2 | 35 | 15 | 20 |
| R3 | 32 | 15 | 17 |
| R4 | 39 | 15 | 24 |

Field classification:

| Residual | `structured.fee_schedule` | `structured.nav_benchmark_performance` | `structured.manager_alignment` | `structured.manager_strategy_text` | `structured.bond_risk_evidence` |
|---|---:|---:|---:|---:|---:|
| R1 | 0 | `coarse_reference_insufficient=4` | `coarse_reference_insufficient=2` | `coarse_reference_insufficient=2` | 0 |
| R2 | `coarse_reference_insufficient=7` | `coarse_reference_insufficient=4` | `coarse_reference_insufficient=2` | `coarse_reference_insufficient=2` | 0 |
| R3 | `coarse_reference_insufficient=7` | `coarse_reference_insufficient=4` | `coarse_reference_insufficient=2` | `coarse_reference_insufficient=2` | `not_applicable=3` |
| R4 | `coarse_reference_insufficient=7` | `coarse_reference_insufficient=4` | `coarse_reference_insufficient=2` | `coarse_reference_insufficient=2` | 0 |

Interpretation:

- A4-S1 no-live behavior is implemented and covered by no-live tests, but it did not activate on the current R1-R4 runtime projection surface.
- The runtime residual remains `coarse_reference_insufficient`.
- The strongest next hypothesis is that current product projections for R1-R4 are not carrying recognized Processor-style `field=...; table_id=...; row=...` locators into the Evidence Confirm materializer path, or not on the failing facts/anchors.
- R3 `missing_section=3` remains open.

## Residuals

| Residual | Status after A4 live/PDF re-evidence | Destination |
|---|---|---|
| R1 strict V2 fail | open | Projection/locator adoption or row-material residual planning. |
| R2 strict V2 fail | open | Projection/locator adoption or row-material residual planning. |
| R3 strict V2 fail | open | Projection/locator adoption plus `missing_section=3` diagnostic. |
| R4 strict V2 fail | open | Projection/locator adoption or row-material residual planning. |
| A4-S1 Processor row materialization on R1-R4 | not observed | Diagnose why current runtime projection does not carry recognized Processor row locators to failing facts. |
| B1 `017641 / 2024` product CLI residual | separate | Separate B1 runtime residual gate. |
| Checklist Evidence Confirm support | deferred | Separate gate. |
| Report-body Evidence Confirm rendering | deferred | Separate gate. |
| Provider-backed semantic production default | deferred | Separate gate. |
| Tag/release/readiness | blocked | Separate release-boundary authorization and accepted readiness evidence. |

## Completion

This gate does not authorize a fix and does not claim readiness.

Next destination:

`RR-09 A5 Projection Locator Adoption / R3 Missing-section Residual Planning Gate`

Completion token:

`RR_09_A4_R1_R4_LIVE_PDF_REEVIDENCE_NO_RUNTIME_IMPROVEMENT_NOT_READY`
