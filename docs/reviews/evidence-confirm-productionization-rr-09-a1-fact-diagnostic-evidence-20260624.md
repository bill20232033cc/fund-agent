# Evidence Confirm Productionization RR-09 A1 R1-R4 Fact-level Diagnostic Evidence

Verdict token:

`RR_09_A1_R1_R4_FACT_DIAGNOSTIC_PROJECTION_ATTACHMENT_DEFECT_NOT_READY`

## Scope

Gate: `RR-09 A1 R1-R4 Fact-level Diagnostic Authorization`.

User authorization: `授权 RR-09 A1 repository-bounded live/PDF fact diagnostics`.

This gate ran repository-bounded product fact diagnostics for all four RR-S2 product CLI residual samples:

| Residual | Sample |
|---|---|
| R1 | `004393 / 2025` |
| R2 | `004194 / 2024` |
| R3 | `006597 / 2024` |
| R4 | `110020 / 2024` |

Annual-report access stayed inside `FundDocumentRepository` through `FundDataExtractor` and `run_repository_bounded_evidence_confirm()`. The diagnostic used the same product fact projection shape as `fund-analysis analyze`: `FundDataExtractor.extract(...)` followed by `project_chapter_facts(...)`, then repository-bounded reference materialization and V2 Evidence Confirm.

No provider/LLM command, direct PDF/cache/source-helper access, checklist support, report-body rendering, quality-gate semantic change, PR mutation, push, tag, release, or readiness promotion was performed.

## Command

The executed diagnostic shape was:

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
        force_refresh=True,
    )
)
summary = summarize_evidence_confirm_diagnostics(runner_result.evidence_confirm_result)
...
PY
```

The first run completed with exit code 0 but emitted a long safe JSON payload that exceeded the tool display window. A second compact run completed with exit code 0 and emitted only aggregate safe metadata. The compact run used `force_refresh=False` after the authorized refresh run, still through the same repository-bounded path.

## Evidence Summary

All four samples loaded through EID single-source metadata and had admitted source provenance:

| Residual | Sample | Selected source | Source mode | Fallback enabled | Fallback used | Metadata admitted |
|---|---|---|---|---:|---:|---:|
| R1 | `004393 / 2025` | `eid` | `single_source_only` | false | false | true |
| R2 | `004194 / 2024` | `eid` | `single_source_only` | false | false | true |
| R3 | `006597 / 2024` | `eid` | `single_source_only` | false | false | true |
| R4 | `110020 / 2024` | `eid` | `single_source_only` | false | false | true |

All four samples failed before useful references were materialized:

| Residual | Sample | Runner status | Pathway status | Reference status | Reference count |
|---|---|---|---|---|---:|
| R1 | `004393 / 2025` | fail | fail | fail | 0 |
| R2 | `004194 / 2024` | fail | fail | fail | 0 |
| R3 | `006597 / 2024` | fail | fail | fail | 0 |
| R4 | `110020 / 2024` | fail | fail | fail | 0 |

Reference materializer issue reason counts:

| Residual | `unsupported_row_locator_format` | `row_locator_without_table_id` | `anchor_not_applicable` |
|---|---:|---:|---:|
| R1 | 122 | 22 | 2 |
| R2 | 122 | 22 | 2 |
| R3 | 110 | 22 | 2 |
| R4 | 129 | 29 | 2 |

V2 compact diagnostic:

| Residual | Checked facts | Failed facts | Not applicable facts | Issue count | Dimension failures | Root-cause bucket |
|---|---:|---:|---:|---:|---|---|
| R1 | 53 | 34 | 19 | 68 | `missing_evidence:fail=34`, `source_support:fail=34` | `projection_attachment_defect=68` |
| R2 | 53 | 35 | 18 | 70 | `missing_evidence:fail=35`, `source_support:fail=35` | `projection_attachment_defect=70` |
| R3 | 53 | 32 | 21 | 61 | `missing_evidence:fail=32`, `source_support:fail=29` | `projection_attachment_defect=61` |
| R4 | 53 | 39 | 14 | 78 | `missing_evidence:fail=39`, `source_support:fail=39` | `projection_attachment_defect=78` |

Dominant impacted source fields were stable across samples:

- `structured.basic_identity`
- `structured.fee_schedule`
- `structured.nav_benchmark_performance`
- `structured.holdings_snapshot`
- `structured.share_change`
- `structured.benchmark`
- `structured.holder_structure`
- `structured.manager_alignment`
- `structured.manager_strategy_text`
- `structured.risk_characteristic_text`

R3 additionally surfaced `structured.bond_risk_evidence`; R4 additionally surfaced `structured.tracking_error`.

## Interpretation

This diagnostic rejects two candidate explanations for R1-R4 as the dominant current cause:

- Not a source/PDF availability failure: source metadata was admitted for all four samples, selected source was `eid`, source mode was `single_source_only`, and fallback was disabled/unused.
- Not a proven deterministic V2 value-matching false-positive: the dominant failing V2 dimensions were `missing_evidence` and `source_support`, with no `value_match` false-positive pattern needed to explain the failures.

The accepted diagnostic classification is:

`projection_attachment_defect`

More precisely, product fact projection emits anchors whose locator metadata cannot currently be materialized by the repository-bounded reference builder. The direct symptoms are `unsupported_row_locator_format` and `row_locator_without_table_id`, yielding `reference_count=0`, followed by V2 `missing_evidence` / `source_support` failures.

This does not prove that the underlying product facts are false. It proves that the current projection/reference attachment layer cannot consistently attach those product facts to repository-materialized annual-report references.

## Residuals

| Residual | Status | Destination |
|---|---|---|
| R1-R4 unclassified EC `fail` under `warn` | closed as unclassified | Classified as `projection_attachment_defect`; route to targeted product projection / anchor locator / reference materializer fix planning. |
| R1-R4 release blocker | still open | Needs targeted fix and re-evidence before release/readiness. |
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
- chapter ids,
- root-cause buckets.

No raw annual-report excerpts, PDF/cache paths, source-helper internals, provider payloads, report body text, API keys, URLs, or traceback are included.

## Next Entry Point

`RR-09 A1-C R1-R4 Projection / Anchor Locator / Reference Materializer Fix Planning Gate`

Do not implement the fix in this evidence gate. Do not claim release/readiness.

Completion token:

`RR_09_A1_R1_R4_FACT_DIAGNOSTIC_PROJECTION_ATTACHMENT_DEFECT_NOT_READY`
