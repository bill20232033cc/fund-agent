# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Implementation Code Review - AgentMiMo - 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Implementation Gate`
Role: AgentMiMo code review worker only
Verdict: `PASS_WITH_FINDINGS`
Release/readiness: `NOT_READY`
Blocking findings: 0

## Reviewed Artifacts

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py` (diff: +425 lines)
- `tests/fund/documents/test_docling_source_truth_residual_closure.py` (diff: +578 lines)
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-evidence-20260617.md`

## Accepted Inputs

- Plan: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md`
- Controller judgment: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-controller-judgment-20260617.md`

## Validation

| Check | Result |
|---|---|
| `uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py` | 80 passed in 0.73s |
| `uv run pytest ... -k "hierarchy or benchmark or raw_legacy or neighbor"` | 28 passed, 52 deselected in 0.39s |
| `git diff --check` | pass, exit 0, no output |

## Findings

### F1 - Low - `_is_detail_or_geography_row` does not cover all plan-intended "detail" row labels

**File/line:** `source_truth_residual_closure.py` - `_is_detail_or_geography_row()`

**Evidence:** The plan's "Ambiguity Fail-closed Rules" states: "row label indicates a detail/geography/security classification table" should keep role `unknown`. The `_is_detail_or_geography_row()` checks for: `国家`, `地区`, `美国`, `行业`, `明细`, `前十名`, `券种`, `第二层次`, `第三层次`. However, common portfolio composition detail labels like `其他资产`, `银行存款`, `结算备付金`, `应收利息`, `应收股利`, `其他应收款`, `资产支持证券` are not covered. If such a label appears between `权益投资` and `其中：股票` in a real §8 table, `_is_detail_or_geography_row` returns `False` and `_is_explicit_top_level_asset_row` also returns `False` (since these are not in the top-level list), so the parent scope would NOT reset and the stock child would incorrectly adopt the distant parent.

**Impact:** Low severity. The plan accepted this conservative boundary list as a non-blocking residual (MiMo F2, accepted in controller judgment). The fail-closed behavior is that `其中：股票` would still need `权益投资` as a same-table parent with lower `row_index`, and the `_is_explicit_top_level_asset_row` list provides the primary scope boundary. In practice, `其他资产` and similar labels are unlikely to appear between `权益投资` and `其中：股票` in real §8 portfolio tables. The existing test `test_raw_legacy_detail_or_geography_row_does_not_bridge_equity_parent_to_stock_child` covers the `美国` case.

**Recommendation:** Non-blocking residual for a future gate. If re-evidence reveals false closures from unlabeled detail rows, expand `_is_detail_or_geography_row()` or add a generic "non-portfolio-leaf" heuristic.

### F2 - Info - `_is_equity_parent_label` uses substring matching which may over-match

**File/line:** `source_truth_residual_closure.py` - `_is_equity_parent_label()`

**Evidence:** `_is_equity_parent_label` returns `"权益投资" in _normalize_for_label(label)`. This is a substring check. A hypothetical label like `权益投资占比` or `权益投资明细` would match. However, `_derive_table_row_hierarchy` requires this to be in a §8 `portfolio_asset_composition_table`, and the label must be the `_row_primary_label()` (last non-empty stripped element). Real portfolio tables use `权益投资` as a top-level row label without suffixes.

**Impact:** Info only. The existing test `test_raw_legacy_portfolio_bundle_enriches_equity_aggregate_row` verifies the happy path. No real false-match scenario identified. The substring approach is consistent with how `_is_stock_child_label` and `_is_explicit_top_level_asset_row` work.

### F3 - Info - `context_label` ambiguity test uses compound label string

**File/line:** `tests/fund/documents/test_docling_source_truth_residual_closure.py` - `test_raw_legacy_ambiguous_benchmark_and_objective_labels_remain_residual`

**Evidence:** The test uses `context_label="投资目标/业绩比较基准"`. The `_has_local_benchmark_label` calls `_contains_any` which does substring matching, so `"投资目标/业绩比较基准"` contains both `"投资目标"` and `"业绩比较基准"`, triggering the `context_benchmark and context_objective` → `"unknown"` path. This is correct behavior and the test passes. However, real annual reports would not typically have a single `context_label` containing both strings; the ambiguity would more likely arise from `heading_path` containing one and `context_label` containing the other.

**Impact:** Info only. The test correctly validates the conflict resolution logic. The separate `test_raw_legacy_context_objective_heading_benchmark_conflict_remains_residual` test covers the more realistic `context_label="投资目标"` + `heading_path=("基金概况", "业绩比较基准")` scenario.

### F4 - Info - Test for `heading_path` internal benchmark/objective conflict is missing

**File/line:** `tests/fund/documents/test_docling_source_truth_residual_closure.py`

**Evidence:** The plan's DS re-review accepted this as a residual (F-DS-R1): "`heading_path` internal benchmark/investment-objective conflict is not explicitly covered by a dedicated test. Current accepted behavior is fail-closed to `unknown`." The implementation does handle this correctly in `_derive_text_semantic_context` — when `heading_benchmark and heading_objective`, it returns `"unknown"`. However, no test directly covers a `heading_path` like `("投资目标", "业绩比较基准")` with no conflicting `context_label`.

**Impact:** Info only. The accepted plan residual explicitly permits this gap. The fail-closed behavior is correct by code inspection.

## Boundary Verification

| Boundary | Status | Evidence |
|---|---|---|
| `NOT_READY` preserved | ✅ | Evidence artifact verdict: `IMPLEMENTATION_COMPLETE_NOT_READY` |
| `candidate_only=true` | ✅ | No `FundDocumentRepository`, no source-helper, no PDF/cache access |
| `source_truth_status=not_proven` | ✅ | All new tests assert `source_truth_status == "not_proven"` where checked |
| No source truth acceptance | ✅ | No production source truth logic added |
| No Docling baseline promotion | ✅ | No baseline promotion logic |
| No parser replacement | ✅ | No parser changes |
| No full field correctness claim | ✅ | Evidence artifact states residual risks |
| No live/network/provider/LLM | ✅ | No external calls |
| No `FIELD_RULES` expansion for `普通股` | ✅ | Test asserts `"普通股" not in closure.FIELD_RULES["stock_investment_amount"].required_row_label_any` |
| v2 bundles not overwritten | ✅ | `_enrich_reference_bundle_contexts` preserves v2 guard; test `test_v2_bundle_with_unknown_hierarchy_is_not_repaired_by_v1_enrichment` verifies |
| No Service/UI/Host/renderer/quality-gate changes | ✅ | Only candidate helper files modified |

## Plan Compliance

| Plan Requirement | Status |
|---|---|
| `_enrich_row_hierarchy_contexts()` in v1 path only | ✅ |
| `_derive_table_row_hierarchy()` with §8 + portfolio table guard | ✅ |
| `_row_primary_label()` = last non-empty stripped element | ✅ |
| `_is_stock_child_label()` = `其中` + `股票` (no `普通股`) | ✅ |
| `_is_explicit_top_level_asset_row()` resets parent scope | ✅ |
| `_is_detail_or_geography_row()` resets parent scope | ✅ |
| `_is_comparable_row_index()` rejects bool/non-int | ✅ |
| `_enrich_text_span_semantic_contexts()` for v1 text spans | ✅ |
| `_derive_text_semantic_context()` precedence: context > heading > raw | ✅ |
| `_raw_text_has_local_label()` delimiter-aware prefix | ✅ |
| No `FIELD_RULES` expansion | ✅ |
| All 20 planned tests implemented | ✅ (20 new tests added, total 80) |
| Existing regression tests pass | ✅ (60 existing tests still pass) |

## Final Verdict

**PASS_WITH_FINDINGS**

The implementation strictly follows the accepted plan. All 80 tests pass (60 existing + 20 new). The v2 non-overwrite guard is preserved. Row hierarchy derivation uses only table-local explicit labels without value equality, bounded neighbor, cross-table, or page proximity. `其中：普通股` remains residual. `FIELD_RULES` is not expanded. Benchmark semantic precedence follows `context_label > heading_path > raw_text prefix`. Investment objective local context correctly blocks benchmark. All boundary conditions are preserved.

Four Info/Low findings are non-blocking residuals consistent with the accepted plan's residual declarations. No blocking findings.

## Self-check

pass - reviewed all diff hunks against accepted plan and controller judgment; verified test pass rates; confirmed boundary preservation; confirmed no FIELD_RULES expansion; confirmed v2 guard intact; confirmed no value-equality/neighbor/cross-table contamination in hierarchy derivation.
