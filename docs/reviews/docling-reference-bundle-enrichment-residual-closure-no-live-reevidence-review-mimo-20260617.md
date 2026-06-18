# Docling Reference Bundle Enrichment Residual Closure No-live Re-evidence Review - AgentMiMo - 2026-06-17

Gate: `Docling Reference Bundle Enrichment Residual Closure No-live Re-evidence Gate`
Role: AgentMiMo evidence review worker only.
Verdict: `PASS`
Release/readiness: `NOT_READY`

## Reviewed Artifacts

- `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json`
- `docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-20260617.md`

## Accepted Inputs

- `docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-controller-judgment-20260617.md`
- `docs/reviews/docling-source-truth-residual-closure-evidence-controller-judgment-20260616.md`
- `reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json`
- `reports/docling-baseline-support-source-truth-residual-closure/20260616/residual_closure_matrix.json`

## Findings

### F1 - Info - Residual rows show empty matched context paths

**Row:** All four residual rows (S5-F032, S6-F041, S6-F049, S6-F050)

**Observation:** The residual rows have `matched_row_label_path=[]`, `matched_column_header_path=[]`, `matched_table_context=[]` alongside `fund_layer_status=semantic_rule_rejected`. This is consistent with the helper's behavior: when `_evaluate_semantics()` finds that no source match satisfies the rule, it returns `semantic_rule_rejected` with empty matched tuples. However, the empty paths make it harder to diagnose *why* each row was rejected at the evidence level without re-running the helper or reading the code.

**Severity:** Info - not blocking. The `closure_reason` field provides the rejection rationale. The matched context is correctly empty because no single match satisfied all predicates. This is a diagnostics residual, not a correctness issue.

### F2 - Info - `reference_bundle_construction.same_row_share_class_proof` scope documented but not independently verified in review

**Row:** Matrix top-level `reference_bundle_construction.same_row_share_class_proof`

**Observation:** The evidence wrapper documents that when `ParsedTable` has a `份额级别` column, its same-row value is included in `row_label_path` for sibling value cells. This is how F020 (`manager_holding_range_A`) now closes: the matched row label path shows `['本基金基金经理持有 本开放式基金', '安信企业价值优选混合A']`, where `安信企业价值优选混合A` contains the share-class label `A` derived from the `份额级别` column. The reviewer confirmed the closed row's matched paths contain the expected share-class context, but did not independently audit the bundle construction code path.

**Severity:** Info - not blocking. The controller judgment already accepted this construction protocol. The matched path evidence for F020 is consistent with the documented behavior. The construction code audit remains a residual risk for future promotion gates, as noted in the 20260616 controller judgment.

No blocking findings.

## Validation

| Check | Result |
|---|---|
| `python -m json.tool` on matrix | passed, exit code 0 |
| `git diff --check` on target artifacts | passed, no output |
| Matrix JSON valid and parseable | confirmed |
| `rows_total=17` | confirmed: 17 rows in array |
| `closed_rows_total=13` | confirmed: 13 `disambiguated_source_body_match` |
| `residual_rows_total=4` | confirmed: 4 `semantic_assignment_residual` |
| `closure_dispositions` sum matches rows_total | confirmed: 13+4=17 |
| `summary.by_sample` totals match rows_total | confirmed: S1(3)+S4(3)+S5(4)+S6(7)=17 |
| `fund_layer_statuses` sum matches rows_total | confirmed: 13+4=17 |
| `source_layer_statuses` all `same_source_reference_loaded` | confirmed: 17/17 |
| `processed_layer_statuses` all `locator_context_available` | confirmed: 17/17 |
| `source_truth_status=not_proven` on all rows | confirmed: set has only `not_proven` |
| `candidate_only=True` | confirmed |
| `not_baseline_promotion=True` | confirmed |
| `not_parser_replacement=True` | confirmed |
| `not_release_readiness=True` | confirmed |
| `not_full_field_correctness=True` | confirmed |
| `not_raw_pdf_bbox_truth=True` | confirmed |
| `not_source_truth=True` | confirmed |
| `verdict=RESIDUAL_CLOSURE_REEVIDENCE_PARTIAL_NOT_READY` | confirmed |

## Target Seven Verification

| Sample | Fact | Field | 20260616 | 20260617 | Change | Evidence |
|---|---|---|---|---|---|---|
| S1 | F015 | `sales_service_fee_C_current_year` | residual | **closed** | +1 closed | Matched row `当期发生的基金应支付的销售服务费`; column `安信企业价值优选混合C` proves C-class; table context `§7` + fee-accounting label proves expense-fee family |
| S1 | F020 | `manager_holding_range_A` | residual | **closed** | +1 closed | Matched row `本基金基金经理持有 本开放式基金` + `安信企业价值优选混合A`; share-class A derived from 份额级别 column value; table context `§10` + manager-holding label proves family |
| S4 | S4-F015 | `fixed_income_investment_amount` | residual | **closed** | +1 closed | Matched row `固定收益投资`; table context `§8` + portfolio/fair-value/financial-statement label proves portfolio-asset-composition family |
| S5 | S5-F032 | `equity_investment_amount` | residual | residual | unchanged | `semantic_rule_rejected` - no hierarchy proof for equity vs stock disambiguation |
| S6 | S6-F041 | `benchmark` | residual | residual | unchanged | `semantic_rule_rejected` - benchmark semantic context not proven in reference bundle |
| S6 | S6-F049 | `equity_investment_amount` | residual | residual | unchanged | `semantic_rule_rejected` - no aggregate hierarchy proof |
| S6 | S6-F050 | `stock_investment_amount` | residual | residual | unchanged | `semantic_rule_rejected` - no child hierarchy proof under equity parent |

**Net change:** 3 rows newly closed (F015, F020, S4-F015). 4 rows remain residual (S5-F032, S6-F041, S6-F049, S6-F050). This matches the matrix summary: `closed_rows_total` increased from 10 to 13, `residual_rows_total` decreased from 7 to 4.

**Residual reasons are evidence-based:**
- S5-F032/S6-F049/S6-F050: The evidence wrapper documents `row_hierarchy_policy: not asserted by evidence wrapper; rows requiring hierarchy remain residual unless helper can prove them from accepted inputs`. No hierarchy was prefilled in the v1 bundles, and the helper cannot derive hierarchy from flat row labels alone. This is the expected fail-closed behavior.
- S6-F041: The `required_text_semantic_context="benchmark"` rule requires a text span with `semantic_context_label="benchmark"`. The v1 bundle text spans use the raw `context_label` from `ParsedTable`, which does not include a `benchmark` semantic label. This is the expected fail-closed behavior.

## Boundary Verification

| Boundary | Status |
|---|---|
| `source_truth_status=not_proven` on all rows | preserved |
| `candidate_only=true` | preserved |
| `NOT_READY` (verdict token) | preserved |
| No source truth acceptance | confirmed - verdict is `RESIDUAL_CLOSURE_REEVIDENCE_PARTIAL_NOT_READY` |
| No Docling baseline promotion | confirmed |
| No parser replacement | confirmed |
| No full field correctness claim | confirmed |
| No release readiness claim | confirmed |
| No PR readiness claim | confirmed |
| Annual-report access: `FundDocumentRepository.load_annual_report(..., force_refresh=False)` | confirmed in `repository_loads` |
| Network socket guard: `connect/connect_ex blocked during repository load` | confirmed on all 4 samples |
| No direct PDF/cache/source-helper access | confirmed in `reference_bundle_construction` |
| No live/network/provider/LLM/analyze/checklist/golden command | confirmed |

## Evidence-Wrapper Assumptions Challenge

| Assumption | Evidence | Verdict |
|---|---|---|
| Raw legacy v1 bundle, no v2 prefill | `reference_bundle_schema_version: 'repository_reference_bundle.v1(raw legacy; helper enrichment delegated)'` on all 4 samples; `v2_fields_intentionally_not_prefilled` lists 7 fields | confirmed consistent |
| Same-row share-class proof | F020 closed with `matched_row_label_path` containing `安信企业价值优选混合A` (A-class label); `same_row_share_class_proof` documents 份额级别 column inclusion | confirmed consistent |
| Table context scope | Closed rows show table_context derived from section inference reason + ParsedTable headers (e.g., `['§7', 'table text contains fee-accounting label', ...]`); `table_context_proof` documents this scope | confirmed consistent |
| Row-hierarchy residual handling | S6-F049/S6-F050 remain residual with `semantic_rule_rejected`; `row_hierarchy_policy: not asserted by evidence wrapper` | confirmed consistent |
| `force_refresh=False` | All 4 samples show `force_refresh: False` in `repository_loads` | confirmed |
| Socket guard | All 4 samples show `network_socket_guard: 'connect/connect_ex blocked during repository load'` | confirmed |

## Residual Risks

1. Bundle construction code path was not independently audited in this review. The controller judgment accepted the construction protocol; the matched-path evidence for closed rows is consistent with the documented behavior.
2. The 4 remaining residual rows require either hierarchy enrichment (S5-F032, S6-F049, S6-F050) or benchmark semantic labeling (S6-F041) to close. These are design residuals, not evidence bugs.
3. All evidence is from repository-mediated `ParsedAnnualReport` objects with socket guards, not from live provider calls. This is appropriate for a no-live gate but does not prove production readiness.
4. Source truth, baseline disposition, parser replacement, full field correctness, and release readiness remain unproven.

## Final Verdict

**PASS**

The matrix JSON is valid and internally consistent. Row counts (17 total, 13 closed, 4 residual) match the summary. The target seven shows the expected 3 newly closed rows (F015, F020, S4-F015) and 4 preserved residual rows (S5-F032, S6-F041, S6-F049, S6-F050). All guard flags and boundary conditions are preserved. The evidence wrapper's documented assumptions (v1-only enrichment, same-row share-class proof, table context scope, row-hierarchy policy) are consistent with the matrix data. No live/network/provider behavior was claimed. The report accurately summarizes the matrix and the 20260616 baseline comparison.

Blocking findings count: 0

## Self-check

pass - review validated matrix JSON structure and counts, verified all 7 target row dispositions against direct evidence in matched paths, confirmed guard flags and boundary preservation, challenged evidence-wrapper assumptions against matrix data, verified no live/network behavior claims, and confirmed report accuracy against the 20260616 baseline.
