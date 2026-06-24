# Evidence Confirm Productionization RR-09 A5 R1-R4 Live/PDF Re-evidence

Verdict token:

`RR_09_A5_R1_R4_LIVE_REEVIDENCE_PROCESSOR_LOCATOR_NOT_ADOPTED_NOT_READY`

## Scope

Gate: `RR-09 A5 R1-R4 Live/PDF Re-evidence after A5 no-live fixes`.

User authorization:

`授权 RR-09 A5 R1-R4 live/PDF re-evidence after A5 no-live fixes`

This gate executed only the authorized repository-bounded R1-R4 evidence path:

`FundDataExtractor.extract(..., force_refresh=True)` -> `project_chapter_facts(...)` -> `run_repository_bounded_evidence_confirm(...)` -> `summarize_value_match_diagnostics(...)`.

The output below is safe aggregate metadata only. It excludes raw annual-report excerpts, raw scalar token values, full structured field values, PDF/cache paths, source URLs, source-helper internals, provider payloads, report body text, secrets and tracebacks.

No product CLI command, provider/LLM command, checklist support, report-body rendering, V2/ECQ/quality-gate semantic change, push, PR mutation, tag, release or readiness promotion was performed.

## Command

The live command used the accepted callable surfaces and returned exit code `0`.

Command shape:

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

## Source And Reference Pathway Evidence

All samples loaded through EID single-source metadata and admitted source provenance:

| Residual | Sample | Selected source | Source mode | Fallback enabled | Fallback used | Metadata admitted |
|---|---|---|---|---:|---:|---:|
| R1 | `004393 / 2025` | `eid` | `single_source_only` | false | false | true |
| R2 | `004194 / 2024` | `eid` | `single_source_only` | false | false | true |
| R3 | `006597 / 2024` | `eid` | `single_source_only` | false | false | true |
| R4 | `110020 / 2024` | `eid` | `single_source_only` | false | false | true |

Reference materialization:

| Residual | Sample | Reference status | Reference count | Row-level refs | Section-level refs | Table-level refs | Reference issue count |
|---|---|---|---:|---:|---:|---:|---:|
| R1 | `004393 / 2025` | pass | 144 | 6 | 22 | 116 | 140 |
| R2 | `004194 / 2024` | pass | 144 | 6 | 22 | 116 | 140 |
| R3 | `006597 / 2024` | fail | 195 | 5 | 28 | 162 | 195 |
| R4 | `110020 / 2024` | pass | 158 | 6 | 29 | 123 | 154 |

Reference issue reasons:

| Residual | `anchor_not_applicable` | `missing_section` | `semantic_row_locator_degraded_to_section_excerpt` | `semantic_row_locator_degraded_to_table_excerpt` |
|---|---:|---:|---:|---:|
| R1 | 2 | 0 | 22 | 116 |
| R2 | 2 | 0 | 22 | 116 |
| R3 | 2 | 3 | 28 | 162 |
| R4 | 2 | 0 | 29 | 123 |

Interpretation:

- A1-C coarse fallback still materializes references for R1/R2/R4 and keeps R3 fail-closed for `missing_section=3`.
- The dominant runtime locator surface remains semantic row locator downgrade, not Processor `field=` row locator materialization.

## Processor Locator Adoption Evidence

A5 targeted field-compatible Processor locator adoption. The live R1-R4 projections did not contain recognized Processor row locators:

| Residual | Sample | Recognized Processor row locator anchors | Processor row locator rows | Processor locator issue reasons |
|---|---|---:|---:|---|
| R1 | `004393 / 2025` | 0 | 0 | none |
| R2 | `004194 / 2024` | 0 | 0 | none |
| R3 | `006597 / 2024` | 0 | 0 | none |
| R4 | `110020 / 2024` | 0 | 0 | none |

Aggregate:

| Metric | Count |
|---|---:|
| `recognized_processor_row_locator_anchors` | 0 |
| `processor_row_locator_rows` | 0 |
| `processor_row_locator_*` issue count | 0 |

Direct conclusion:

- A5 no-live code can filter field-locator-capable anchors when such anchors exist.
- The real R1-R4 runtime projection did not expose those `field=` Processor locators to the materializer.
- Therefore A5 did not change the live R1-R4 residual surface.

## Strict V2 Result

Strict deterministic V2 remains fail for all four samples:

| Residual | Sample | Overall status | Score | Fail facts | Warn facts | Not applicable facts | V2 issue count |
|---|---|---|---:|---:|---:|---:|---:|
| R1 | `004393 / 2025` | fail | 40 | 8 | 26 | 19 | 230 |
| R2 | `004194 / 2024` | fail | 40 | 15 | 20 | 18 | 238 |
| R3 | `006597 / 2024` | fail | 40 | 15 | 17 | 21 | 284 |
| R4 | `110020 / 2024` | fail | 40 | 15 | 24 | 14 | 280 |

Dimension counts:

| Residual | `value_match:fail` | `value_match:pass` | `value_match:not_applicable` | `missing_evidence:pass` | `anchor_precision:warn` |
|---|---:|---:|---:|---:|---:|
| R1 | 8 | 26 | 19 | 34 | 34 |
| R2 | 15 | 20 | 18 | 35 | 35 |
| R3 | 15 | 17 | 21 | 32 | 32 |
| R4 | 15 | 24 | 14 | 39 | 39 |

Compared with the accepted A2-S2 baseline, `coarse_reference_insufficient` did not decrease:

| Residual | A2-S2 baseline | A5 live current | Delta |
|---|---:|---:|---:|
| R1 | 8 | 8 | 0 |
| R2 | 15 | 15 | 0 |
| R3 | 15 | 15 | 0 |
| R4 | 15 | 15 | 0 |
| Total | 53 | 53 | 0 |

## Value Diagnostic Buckets

Failing field classification remained stable:

| Residual | `structured.fee_schedule` | `structured.nav_benchmark_performance` | `structured.manager_alignment` | `structured.manager_strategy_text` |
|---|---:|---:|---:|---:|
| R1 | 0 | 4 | 2 | 2 |
| R2 | 7 | 4 | 2 | 2 |
| R3 | 7 | 4 | 2 | 2 |
| R4 | 7 | 4 | 2 | 2 |

Safe unmatched value paths by failing field:

| Source field | Safe unmatched value paths |
|---|---|
| `structured.fee_schedule` | `value.custody_fee`, `value.management_fee` |
| `structured.nav_benchmark_performance` | `value.benchmark_return_rate`, `value.nav_growth_rate` |
| `structured.manager_alignment` | `value.employee_holding`, `value.manager_holding` |
| `structured.manager_strategy_text` | `value.market_outlook`, `value.strategy_summary` |

The diagnostic did not expose any `processor_row_locator_*` protocol failure. The issue is absence of Processor locator adoption in the live projection, not a Processor locator parser/materializer failure.

## Root Cause Update

The A5 live/PDF evidence rejects the hypothesis that R1-R4 residuals are still blocked by unsupported `field=...; table_id=...; row=...` Processor locators at the materializer.

The current direct evidence supports a narrower root cause:

1. Live R1-R4 projections contain no recognized Processor `field=` row locator anchors.
2. The materializer therefore cannot exercise A5 field-compatible row-locator behavior.
3. References still rely on semantic row locator downgrade to table/section excerpts.
4. `coarse_reference_insufficient` remains unchanged at `53`.

This is now a projection/runtime locator adoption gap. A follow-up plan should trace why the product projection path used by `FundDataExtractor.extract(...)` and `project_chapter_facts(...)` does not carry Processor `field=` locators for these fields, rather than changing V2 thresholds or treating the materializer parser as the blocking layer.

## Residuals

| Residual | Status after A5 live/PDF | Destination |
|---|---|---|
| R1-R4 `coarse_reference_insufficient` | open; unchanged `53 -> 53` | Follow-up projection/runtime locator adoption planning gate. |
| Processor `field=` locator parser/materializer protocol | not proven blocking in live R1-R4; no recognized Processor locators surfaced | Keep current A5 no-live code; do not route next fix to parser unless later evidence shows malformed locators. |
| R3 `missing_section=3` | still present in reference build issues | Separate R3 missing-section diagnostic/fix gate if prioritized. |
| B1 `017641 / 2024` product CLI block | not executed | Separate B1 runtime product CLI re-evidence gate. |
| Checklist Evidence Confirm support | deferred | Separate gate. |
| Report-body Evidence Confirm rendering | deferred | Separate gate. |
| Provider-backed semantic production default | deferred | Separate gate. |
| Tag/release/readiness | blocked | Separate release-boundary authorization and accepted readiness evidence. |

## Next Entry Point

`RR-09 A6 Projection / Runtime Locator Adoption Planning Gate`

The next gate should be planning-only first and should use direct code/runtime evidence to answer:

- whether live R1-R4 fields are produced by legacy annual processors, FDD processors, or a mixed projection path;
- why no `field=` Processor locators survive into `project_chapter_facts(...)`;
- whether the fix belongs in Processor extraction, `StructuredFundDataBundle` projection, or `ChapterEvidenceAnchor` projection;
- how to preserve no-`field=` family anchors while adding row-precise locators for field-locator-capable families.

Release/readiness remains `NOT_READY`.

Completion token:

`RR_09_A5_R1_R4_LIVE_REEVIDENCE_PROCESSOR_LOCATOR_NOT_ADOPTED_NOT_READY`
