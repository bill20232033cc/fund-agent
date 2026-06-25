# Evidence Confirm Productionization RR-09 A3 Live/PDF Re-evidence

Verdict token:

`RR_09_A3_R1_R4_LIVE_PDF_REEVIDENCE_STRICT_V2_STILL_FAIL_NOT_READY`

## Scope

Gate: `RR-09 R1-R4 live/PDF re-evidence after A3 no-live fixes`.

User authorization:

`授权 RR-09 R1-R4 live/PDF re-evidence after A3 no-live fixes`

This gate re-ran repository-bounded product fact diagnostics for the four R1-R4 samples after accepted A3 no-live fixes:

| Residual | Sample |
|---|---|
| R1 | `004393 / 2025` |
| R2 | `004194 / 2024` |
| R3 | `006597 / 2024` |
| R4 | `110020 / 2024` |

Annual-report access stayed inside the accepted product path:

`FundDataExtractor.extract(..., force_refresh=True)` -> `project_chapter_facts(...)` -> `run_repository_bounded_evidence_confirm(...)` -> `summarize_value_match_diagnostics(...)`.

No provider/LLM command, product CLI command, checklist support, report-body rendering, V2/ECQ/quality-gate semantic change, PR mutation, push, tag, release or readiness promotion was performed.

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
diagnostic = summarize_value_match_diagnostics(
    projection=projection,
    references=runner_result.reference_build_result.references,
    result=runner_result.evidence_confirm_result,
)
...
PY
```

Execution result:

- Exit code: `0`
- Output type: safe aggregate JSON only.
- No raw annual-report excerpt, raw scalar token value, full structured value, PDF/cache path, URL, source-helper internals, provider payload, report body text, secret or traceback was emitted.

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

| Residual | Sample | Reference status | Reference count | Section downgrade issues | Table downgrade issues | Anchor not applicable | Missing section |
|---|---|---|---:|---:|---:|---:|---:|
| R1 | `004393 / 2025` | pass | 144 | 22 | 116 | 2 | 0 |
| R2 | `004194 / 2024` | pass | 144 | 22 | 116 | 2 | 0 |
| R3 | `006597 / 2024` | fail | 195 | 28 | 162 | 2 | 3 |
| R4 | `110020 / 2024` | pass | 158 | 29 | 123 | 2 | 0 |

Interpretation:

- A3 did not regress source provenance.
- R1/R2/R4 reference materialization remains nonzero and pass.
- R3 now projects bond-risk group refs into ordinary annual-report anchors, increasing reference count from the A2-S2 baseline, but the reference builder now reports `missing_section=3`; this is a fail-closed reference-path residual for R3.

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

| Residual | Diagnostic records | `coarse_reference_insufficient` | `bond_risk_group_anchor_projection_gap` | `not_applicable` |
|---|---:|---:|---:|---:|
| R1 | 34 | 8 | 0 | 26 |
| R2 | 35 | 15 | 0 | 20 |
| R3 | 32 | 15 | 0 | 17 |
| R4 | 39 | 15 | 0 | 24 |

Field classification:

| Residual | `structured.fee_schedule` | `structured.nav_benchmark_performance` | `structured.manager_alignment` | `structured.manager_strategy_text` | `structured.bond_risk_evidence` |
|---|---:|---:|---:|---:|---:|
| R1 | 0 | `coarse_reference_insufficient=4` | `coarse_reference_insufficient=2` | `coarse_reference_insufficient=2` | 0 |
| R2 | `coarse_reference_insufficient=7` | `coarse_reference_insufficient=4` | `coarse_reference_insufficient=2` | `coarse_reference_insufficient=2` | 0 |
| R3 | `coarse_reference_insufficient=7` | `coarse_reference_insufficient=4` | `coarse_reference_insufficient=2` | `coarse_reference_insufficient=2` | `not_applicable=3` |
| R4 | `coarse_reference_insufficient=7` | `coarse_reference_insufficient=4` | `coarse_reference_insufficient=2` | `coarse_reference_insufficient=2` | 0 |

Interpretation:

- A3 closed the previous R3 `bond_risk_group_anchor_projection_gap` diagnostic class.
- A3 did not close strict V2 for R1-R4.
- The dominant remaining strict V2 blocker is still row/material precision: `coarse_reference_insufficient` for `fee_schedule`, `nav_benchmark_performance`, `manager_alignment` and `manager_strategy_text`.
- R3 also needs a follow-up on the new `missing_section=3` reference-builder issue before it can be treated as a clean reference pass.

## Residuals

| Residual | Status after A3 live/PDF re-evidence | Destination |
|---|---|---|
| R1 strict V2 fail | open | Row/material precision or residual disposition planning. |
| R2 strict V2 fail | open | Row/material precision or residual disposition planning. |
| R3 `bond_risk_group_anchor_projection_gap` | closed for current evidence | A3 group-anchor projection worked. |
| R3 strict V2 fail | open | Row/material precision plus `missing_section=3` reference-builder diagnostic. |
| R4 strict V2 fail | open | Row/material precision or residual disposition planning. |
| B1 `017641 / 2024` product CLI residual | separate evidence | See `docs/reviews/evidence-confirm-productionization-rr-09-b1-runtime-product-cli-reevidence-20260624.md`. |
| Checklist Evidence Confirm support | deferred | Separate gate. |
| Report-body Evidence Confirm rendering | deferred | Separate gate. |
| Provider-backed semantic production default | deferred | Separate gate. |
| Tag/release/readiness | blocked | Separate release-boundary authorization and accepted readiness evidence. |

## Completion

This gate does not authorize a fix and does not claim readiness.

Next destination:

`RR-09 A4 R1-R4 Row-material Precision / R3 Missing-section Residual Planning Gate`

Completion token:

`RR_09_A3_R1_R4_LIVE_PDF_REEVIDENCE_STRICT_V2_STILL_FAIL_NOT_READY`
