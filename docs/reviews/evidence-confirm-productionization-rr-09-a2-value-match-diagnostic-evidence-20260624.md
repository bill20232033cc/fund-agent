# Evidence Confirm Productionization RR-09 A2-S2 Value-match Diagnostic Evidence

Verdict token:

`RR_09_A2_S2_VALUE_MATCH_DIAGNOSTIC_EVIDENCE_COARSE_REFERENCE_AND_BOND_RISK_GAP_NOT_READY`

## Scope

Gate: `RR-09 A2-S2 R1-R4 Live/PDF Value-match Diagnostic Evidence`.

User authorization:

`授权 RR-09 A2-S2 repository-bounded live/PDF value-match diagnostics for R1-R4`

This gate ran the accepted A2-S1 diagnostic helper on the four R1-R4 repository-bounded samples:

| Residual | Sample |
|---|---|
| R1 | `004393 / 2025` |
| R2 | `004194 / 2024` |
| R3 | `006597 / 2024` |
| R4 | `110020 / 2024` |

Annual-report access stayed inside the accepted product path:

`FundDataExtractor.extract(..., force_refresh=True)` -> `project_chapter_facts(...)` -> `run_repository_bounded_evidence_confirm(...)` -> `summarize_value_match_diagnostics(...)`.

The diagnostic output is safe aggregate metadata only. It includes sample IDs, source provenance enums/booleans, counts, source field IDs, fact/chapter IDs by stable IDs, token categories, safe value paths, reference granularity counts, locator downgrade flags and diagnostic classifications. It does not include raw annual-report excerpts, raw scalar token values, full structured values, PDF/cache paths, URLs, source-helper internals, provider payloads, report body text, secrets or tracebacks.

No provider/LLM command, product CLI command, checklist support, report-body rendering, quality-gate semantic change, PR mutation, push, tag, release or readiness promotion was performed.

## Commands

First diagnostic attempt:

```bash
uv run python - <<'PY'
...
runner_result.evidence_confirm_result.status
...
PY
```

Result:

- Exit code `1`.
- Failure reason: script bug only, `AttributeError: 'EvidenceConfirmResultV2' object has no attribute 'status'`.
- Impact: no evidence classification was accepted from this failed attempt.

Corrected diagnostic command:

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

Result:

- Full safe JSON command exited `0`; output was too large for the tool transcript and was truncated.
- Compact safe JSON command exited `0`; tables below are derived from the compact command output.
- Token/match source was `deterministic_v2_same_source_primitives`, reused from V2 rather than a parallel matcher.

## Source And Reference Pathway Evidence

All samples loaded through EID single-source metadata and admitted source provenance:

| Residual | Sample | Selected source | Source mode | Fallback enabled | Fallback used | Metadata admitted |
|---|---|---|---|---:|---:|---:|
| R1 | `004393 / 2025` | `eid` | `single_source_only` | false | false | true |
| R2 | `004194 / 2024` | `eid` | `single_source_only` | false | false | true |
| R3 | `006597 / 2024` | `eid` | `single_source_only` | false | false | true |
| R4 | `110020 / 2024` | `eid` | `single_source_only` | false | false | true |

Reference materialization remained pass for all four samples:

| Residual | Sample | Reference status | Reference count | Section downgrade issues | Table downgrade issues | Anchor not applicable |
|---|---|---:|---:|---:|---:|---:|
| R1 | `004393 / 2025` | pass | 144 | 22 | 122 | 2 |
| R2 | `004194 / 2024` | pass | 144 | 22 | 122 | 2 |
| R3 | `006597 / 2024` | pass | 132 | 22 | 110 | 2 |
| R4 | `110020 / 2024` | pass | 158 | 29 | 129 | 2 |

Interpretation:

- A1-C remains effective: the previous zero-reference projection/materialization defect did not recur.
- The remaining failures occur after references exist.
- All failing value-match records use downgraded section/table proof references rather than row-precise proof references, which is the direct input for the A2 classification below.

## Strict V2 Result

Strict deterministic V2 remains fail for all four samples:

| Residual | Sample | Overall status | Score | Fail facts | Warn facts | Not applicable facts | V2 issue count |
|---|---|---|---:|---:|---:|---:|---:|
| R1 | `004393 / 2025` | fail | 40 | 8 | 26 | 19 | 236 |
| R2 | `004194 / 2024` | fail | 40 | 15 | 20 | 18 | 244 |
| R3 | `006597 / 2024` | fail | 0 | 18 | 14 | 21 | 229 |
| R4 | `110020 / 2024` | fail | 40 | 15 | 24 | 14 | 286 |

Dimension counts:

| Residual | `value_match:fail` | `value_match:pass` | `value_match:not_applicable` | `missing_evidence:fail` | `anchor_precision:warn` |
|---|---:|---:|---:|---:|---:|
| R1 | 8 | 26 | 19 | 0 | 34 |
| R2 | 15 | 20 | 18 | 0 | 35 |
| R3 | 15 | 14 | 24 | 3 | 29 |
| R4 | 15 | 24 | 14 | 0 | 39 |

## A2 Diagnostic Classification

Aggregate classification:

| Residual | Diagnostic records | `coarse_reference_insufficient` | `bond_risk_group_anchor_projection_gap` | `not_applicable` |
|---|---:|---:|---:|---:|
| R1 | 34 | 8 | 0 | 26 |
| R2 | 35 | 15 | 0 | 20 |
| R3 | 32 | 15 | 3 | 14 |
| R4 | 39 | 15 | 0 | 24 |

Failing field classification:

| Residual | `structured.fee_schedule` | `structured.nav_benchmark_performance` | `structured.manager_alignment` | `structured.manager_strategy_text` | `structured.bond_risk_evidence` |
|---|---:|---:|---:|---:|---:|
| R1 | 0 | `coarse_reference_insufficient=4` | `coarse_reference_insufficient=2` | `coarse_reference_insufficient=2` | 0 |
| R2 | `coarse_reference_insufficient=7` | `coarse_reference_insufficient=4` | `coarse_reference_insufficient=2` | `coarse_reference_insufficient=2` | 0 |
| R3 | `coarse_reference_insufficient=7` | `coarse_reference_insufficient=4` | `coarse_reference_insufficient=2` | `coarse_reference_insufficient=2` | `bond_risk_group_anchor_projection_gap=3` |
| R4 | `coarse_reference_insufficient=7` | `coarse_reference_insufficient=4` | `coarse_reference_insufficient=2` | `coarse_reference_insufficient=2` | 0 |

Stable unmatched safe value paths by failing field:

| Source field | Safe unmatched value paths |
|---|---|
| `structured.fee_schedule` | `value.custody_fee`, `value.management_fee` |
| `structured.nav_benchmark_performance` | `value.benchmark_return_rate`, `value.nav_growth_rate` |
| `structured.manager_alignment` | `value.employee_holding`, `value.manager_holding` |
| `structured.manager_strategy_text` | `value.market_outlook`, `value.strategy_summary` |
| `structured.bond_risk_evidence` | group/internal paths under `value.anchors[]`, `value.groups[]`, `value.contract_*`, `value.satisfied_group_ids[]` |

Interpretation:

- R1 value-match failures classify as `coarse_reference_insufficient` only.
- R2 value-match failures classify as `coarse_reference_insufficient` only.
- R3 has both `coarse_reference_insufficient` value-match failures and a separate `bond_risk_group_anchor_projection_gap` missing-evidence failure.
- R4 value-match failures classify as `coarse_reference_insufficient` only.
- No failing bucket classified as `matcher_normalization_gap`, `value_shape_overbroad`, `anchor_attachment_mismatch`, `extractor_value_or_anchor_defect` or `undetermined_requires_live_excerpt_review` in the compact accepted output.

## Residuals

| Residual | Status after A2-S2 | Destination |
|---|---|---|
| R1-R4 zero-reference projection attachment defect | closed for current evidence | Already closed by A1-C and reconfirmed by nonzero references. |
| R1/R2/R4 strict V2 value-match fail | classified, still open | Coarse-reference / row-precision / materializer narrowing fix planning. |
| R3 strict V2 value-match fail | classified, still open | Coarse-reference / row-precision / materializer narrowing fix planning. |
| R3 `structured.bond_risk_evidence` missing-evidence fail | classified, still open | Bond-risk group anchor expansion from `BondRiskEvidenceValue.anchors` into `ChapterEvidenceAnchor`. |
| E1 row-locator downgrade warnings | expected residual | Preserve as precision warnings unless later row-precise extractor/materializer gate proves exact rows. |
| B1 runtime product CLI re-evidence for `017641 / 2024` | open | Separate runtime re-evidence authorization. |
| Checklist Evidence Confirm support | deferred | Separate gate. |
| Report-body Evidence Confirm rendering | deferred | Separate gate. |
| Provider-backed semantic production default | deferred | Separate gate. |
| Tag/release/readiness | blocked | Separate release-boundary authorization and accepted readiness evidence. |

## Next Entry Point

`RR-09 A3 Coarse-reference / Bond-risk Anchor Fix Planning Gate / RR-09 B1 Runtime Product CLI Re-evidence Authorization`

A3 should be planning-only first. It should decide whether the fix route is:

- row/table anchor precision improvement or materializer narrowing for `fee_schedule`, `nav_benchmark_performance`, `manager_alignment` and `manager_strategy_text`;
- bond-risk group anchor expansion from `BondRiskEvidenceValue.anchors` into `ChapterEvidenceAnchor` for R3;
- or an explicit residual decision if exact row precision is out of current release scope.

Do not claim release/readiness.

Completion token:

`RR_09_A2_S2_VALUE_MATCH_DIAGNOSTIC_EVIDENCE_COARSE_REFERENCE_AND_BOND_RISK_GAP_NOT_READY`
