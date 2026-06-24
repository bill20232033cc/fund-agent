# Evidence Confirm Productionization RR-09 A1 R1-R4 Live/PDF Re-evidence

Verdict token:

`RR_09_A1_R1_R4_LIVE_PDF_REEVIDENCE_VALUE_MATCH_RESIDUAL_NOT_READY`

## Scope

Gate: `RR-09 A1 R1-R4 Live/PDF Re-evidence Gate`.

User authorization: `授权 RR-09 A1 repository-bounded live/PDF fact diagnostics`.

This gate re-ran repository-bounded product fact diagnostics for the four RR-S2 product CLI residual samples after accepted A1-C no-live implementation and aggregate deepreview:

| Residual | Sample |
|---|---|
| R1 | `004393 / 2025` |
| R2 | `004194 / 2024` |
| R3 | `006597 / 2024` |
| R4 | `110020 / 2024` |

Annual-report access stayed inside `FundDocumentRepository` through `FundDataExtractor` and `run_repository_bounded_evidence_confirm()`. The diagnostic used the product fact projection shape used by `fund-analysis analyze`: `FundDataExtractor.extract(...)`, `project_chapter_facts(...)`, repository-bounded reference materialization, then V2 Evidence Confirm.

No provider/LLM command, direct PDF/cache/source-helper access, checklist support, report-body rendering, quality-gate semantic change, PR mutation, push, tag, release, or readiness promotion was performed.

## Commands

Executed live/PDF refresh diagnostic:

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
summary = summarize_evidence_confirm_diagnostics(runner_result.evidence_confirm_result)
...
PY
```

Executed cached fine-grained diagnostic for dimension/source-field buckets:

```bash
uv run python - <<'PY'
...
bundle = await FundDataExtractor().extract(fund_code, report_year, force_refresh=False)
projection = project_chapter_facts(bundle)
runner_result = await run_repository_bounded_evidence_confirm(
    EvidenceConfirmRepositoryRunRequest(
        fund_code=fund_code,
        report_year=report_year,
        projection=projection,
        force_refresh=False,
    )
)
...
PY
```

Both commands exited `0` and emitted only safe aggregate metadata.

## Source And Reference Pathway Evidence

All four samples loaded through EID single-source metadata and admitted source provenance:

| Residual | Sample | Selected source | Source mode | Fallback enabled | Fallback used | Metadata admitted |
|---|---|---|---|---:|---:|---:|
| R1 | `004393 / 2025` | `eid` | `single_source_only` | false | false | true |
| R2 | `004194 / 2024` | `eid` | `single_source_only` | false | false | true |
| R3 | `006597 / 2024` | `eid` | `single_source_only` | false | false | true |
| R4 | `110020 / 2024` | `eid` | `single_source_only` | false | false | true |

A1-C fixed the previous zero-reference materialization failure:

| Residual | Sample | Runner status | Pathway status | Reference status | Reference count | Reference issue severity |
|---|---|---|---|---|---:|---|
| R1 | `004393 / 2025` | fail | fail | pass | 144 | informational only |
| R2 | `004194 / 2024` | fail | fail | pass | 144 | informational only |
| R3 | `006597 / 2024` | fail | fail | pass | 132 | informational only |
| R4 | `110020 / 2024` | fail | fail | pass | 158 | informational only |

Reference materializer issue reason counts:

| Residual | `semantic_row_locator_degraded_to_table_excerpt` | `semantic_row_locator_degraded_to_section_excerpt` | `anchor_not_applicable` |
|---|---:|---:|---:|
| R1 | 122 | 22 | 2 |
| R2 | 122 | 22 | 2 |
| R3 | 110 | 22 | 2 |
| R4 | 129 | 29 | 2 |

The previous blocking reasons `unsupported_row_locator_format` and `row_locator_without_table_id` did not recur in the compact diagnostics. The materializer now emits coarse table/section proof references and preserves row-locator downgrade as informational materializer issues plus V2 E1 warnings.

## V2 Evidence Confirm Result

Strict Evidence Confirm remains fail for all four samples:

| Residual | Checked facts | Failed facts | Warning facts | Not applicable facts | V2 issue count | Dominant failing dimensions |
|---|---:|---:|---:|---:|---:|---|
| R1 | 53 | 8 | 26 | 19 | 236 | `value_match:fail=8`, `anchor_precision:warn=34` |
| R2 | 53 | 15 | 20 | 18 | 244 | `value_match:fail=15`, `anchor_precision:warn=35` |
| R3 | 53 | 18 | 14 | 21 | 229 | `value_match:fail=15`, `missing_evidence:fail=3`, `anchor_precision:warn=29` |
| R4 | 53 | 15 | 24 | 14 | 286 | `value_match:fail=15`, `anchor_precision:warn=39` |

Failing source-field buckets:

| Residual | Failing buckets |
|---|---|
| R1 | `structured.nav_benchmark_performance:value_match=4`; `structured.manager_alignment:value_match=2`; `structured.manager_strategy_text:value_match=2` |
| R2 | `structured.fee_schedule:value_match=7`; `structured.nav_benchmark_performance:value_match=4`; `structured.manager_alignment:value_match=2`; `structured.manager_strategy_text:value_match=2` |
| R3 | `structured.fee_schedule:value_match=7`; `structured.nav_benchmark_performance:value_match=4`; `structured.manager_alignment:value_match=2`; `structured.manager_strategy_text:value_match=2`; `structured.bond_risk_evidence:missing_evidence=3` |
| R4 | `structured.fee_schedule:value_match=7`; `structured.nav_benchmark_performance:value_match=4`; `structured.manager_alignment:value_match=2`; `structured.manager_strategy_text:value_match=2` |

## Interpretation

Accepted A1-C improvement:

- Source/PDF provenance is still admitted for all R1-R4 samples.
- Repository-bounded reference materialization no longer produces `reference_count=0`.
- The prior A1 root cause `projection_attachment_defect` from unsupported semantic row locators is no longer the dominant failure shape.

Current residual classification:

- R1, R2 and R4 now fail because of deterministic V2 `value_match` mismatch buckets, with expected E1 `anchor_precision` warnings from coarse reference degradation.
- R3 also has `structured.bond_risk_evidence` `missing_evidence:fail=3`, separate from the value-match failures.
- This evidence does not prove the product facts are false. It proves the current deterministic fact/reference comparison still cannot pass for these fields after references are materialized.

This gate therefore rejects release/readiness and routes to a narrower value-match / remaining missing-evidence diagnostic before any fix.

## Residuals

| Residual | Status | Destination |
|---|---|---|
| R1-R4 zero-reference projection attachment defect | closed for current evidence | A1-C materializer fix produced nonzero references and pass reference build status. |
| R1/R2/R4 strict Evidence Confirm fail | open | `value_match` diagnostic / fix planning gate. |
| R3 strict Evidence Confirm fail | open | `value_match` diagnostic plus `bond_risk_evidence` missing-evidence diagnostic / fix planning gate. |
| E1 row-locator downgrade warnings | expected residual | Preserve as precision warning unless a later row-precise extractor/materializer gate proves exact rows. |
| `017641 / 2024` runtime product CLI re-evidence | open | Separate B1 runtime re-evidence authorization. |
| Checklist Evidence Confirm support | deferred | Separate gate. |
| Report-body Evidence Confirm rendering | deferred | Separate gate. |
| Provider-backed semantic production default | deferred | Separate gate. |
| Tag/release/readiness | blocked | Separate release-boundary authorization and accepted readiness evidence. |

## Safety

The recorded evidence uses only safe aggregate metadata:

- sample id,
- source provenance booleans/enums,
- status/count fields,
- stable reason codes,
- dimension names,
- source field ids,
- chapter/fact ids,
- root-cause buckets.

No raw annual-report excerpts, PDF/cache paths, source-helper internals, provider payloads, report body text, API keys, URLs, or traceback are included.

## Next Entry Point

`RR-09 A2 R1-R4 Value-match / Bond-risk Missing-evidence Diagnostic Planning Gate / RR-09 B1 Runtime Re-evidence Authorization`

Do not implement a fix in this evidence gate. Do not claim release/readiness.

Completion token:

`RR_09_A1_R1_R4_LIVE_PDF_REEVIDENCE_VALUE_MATCH_RESIDUAL_NOT_READY`
