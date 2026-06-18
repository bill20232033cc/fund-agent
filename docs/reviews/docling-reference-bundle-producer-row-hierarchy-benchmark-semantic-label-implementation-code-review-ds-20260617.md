# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Implementation Code Review (AgentDS) — 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Implementation Gate`
Role: AgentDS code review worker only
Verdict: `PASS`
Release/readiness: `NOT_READY`

## Reviewed Artifacts

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py` (diff: +456 lines)
- `tests/fund/documents/test_docling_source_truth_residual_closure.py` (diff: +638 lines)
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-evidence-20260617.md`

## Accepted Inputs

- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-controller-judgment-20260617.md`

## Validation

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py
→ 80 passed in 0.60s (60 previous + 20 new)

uv run pytest ... -k "hierarchy or benchmark or raw_legacy or neighbor"
→ 28 passed, 52 deselected in 0.78s

git diff --check → exit 0, no output
```

---

## Findings

### F-DS-I1 (Info) — `_is_stock_child_label` 接受 `"其中：股票投资"` 等含 `股票` 子串的标签

**File/line**: `source_truth_residual_closure.py`, `_is_stock_child_label` (≈L2128 in new code)

**Issue**: `_is_stock_child_label` 使用 `"股票" in normalized` 做子串匹配。Plan 的显式正例为 `"其中：股票"` 和 `"其中:股票"`。子串匹配额外接受 `"其中：股票投资"`（如某些基金的持仓表使用 `"其中：股票投资"` 而非 `"其中：股票"`）。

**Why it matters**: 这略宽于 plan 的显式正例范围，但 `"其中：普通股"` 仍被正确拒绝（`"普通股"` 不含 `"股票"` 子串）。`"其中：股票投资"` 在语义上是更具体的股票子行变体，接受它不违反 plan 的 fail-closed 原则。但如果有报表使用 `"其中：股票回购"` 等非投资性标签，也可能被误接受。

**Suggested fix**: 当前行为可接受。如未来发现误匹配，可将匹配收紧为精确子串 `"其中：股票"` 或 `"其中：股票投资"` 白名单。

**Severity**: Info — 无已知误匹配场景，fail-closed 边界完好。

### F-DS-I2 (Info) — `context_label` benchmark + `heading_path` objective 跨层冲突未单独测试

**Implementation**: `_derive_text_semantic_context` 在 `context_label="业绩比较基准"` 且 `heading_path` 含投资目标标签时返回 `"unknown"`（L≈2203 cross-layer conflict）。

**Verification**: 运行时确认：`ctx=benchmark, head=objective → unknown`。反例（ctx=objective, head=benchmark → investment_objective）有 Test 16 覆盖。正例（ctx=benchmark → benchmark）有 Test 10 覆盖。

**Severity**: Info — 实现 fail-closed，无 false positive 风险。缺失测试不影响正确性。

### F-DS-I3 (Info) — `context_label` benchmark + `raw_text` prefix objective 跨层冲突未单独测试

**Implementation**: `_derive_text_semantic_context` 在 `context_label="业绩比较基准"` 且 `raw_text` 以 `"投资目标"` 开头时返回 `"unknown"`。

**Verification**: 运行时确认：`ctx=benchmark, raw_prefix=objective → unknown`。

**Severity**: Info — 同 F-DS-I2，实现 fail-closed。

### F-DS-I4 (Info) — `_is_equity_parent_label` 子串匹配接受 `"权益投资合计"` 等变体

**Implementation**: `_is_equity_parent_label` 使用 `"权益投资" in _normalize_for_label(label)`。

**Why it matters**: 极少数报表可能使用 `"权益投资合计"` 作为汇总行（非 aggregate parent）。当前行为会将其视为 parent。但在标准年报中，`"权益投资"` 就是组合表的 aggregate parent label，汇总行通常位于 child rows 之后，child scan 的顺序逻辑会自然地正确处理。

**Severity**: Info — 无已知误匹配。

---

## Implementation Conformance to Plan

### v2 Non-overwrite Guard

`_enrich_reference_bundle_contexts` v1-only guard 未变（L1919–1920）。v2 bundle 原样返回。Test `test_v2_bundle_with_unknown_hierarchy_is_not_repaired_by_v1_enrichment` 确认 v2 未被修复。✅

### Row Hierarchy Derivation

| Plan Requirement | Implementation | Evidence |
|---|---|---|
| Table-local explicit labels only | `_derive_table_row_hierarchy` 仅使用同表 `(fund_code, document_year, source, section_id, table_id)` 分组内的 `row_label_path` | L1964–1967 grouping key |
| No value equality proof | 从不检查 cell value | trace confirms |
| No bounded neighbor labels | `bounded_neighbor_row_labels` 不在 `_derive_table_row_hierarchy` 中使用 | Test verifies |
| No cross-table context | grouping 按 table_id 隔离 | L1964–1967 |
| `_row_primary_label` = last non-empty strip | `reversed(cell.row_label_path)` + `.strip()` + 首个非空返回 | L2078–2085 |
| `row_index` gaps comparable | `_is_comparable_row_index` 仅检查 `isinstance(int) and not bool`，不检查连续性 | L2142–2143 |
| `row_index` missing/non-int/duplicate fail-closed | `_is_comparable_row_index`, duplicate cell identity check, conflicting row label check all return `{}` | L2000–2014 |
| `其中：普通股` remains residual | `_is_stock_child_label` 要求 `"其中"` + `"股票"`，`"普通股"` 不含 `"股票"` → False | Test confirms |
| No `FIELD_RULES` expansion | `FIELD_RULES["stock_investment_amount"]` 未改动 | Evidence doc + runtime check |
| Aggregate only when child exists | `proven_parent_labels` = 有 children 的 parent label set | L2051 |
| Top-level asset row resets scope | `_is_explicit_top_level_asset_row` → `current_parent = None` | L2037–2039, Test verifies |
| Detail/geography row breaks scope | `_is_detail_or_geography_row` → `current_parent = None` | L2034–2036, Test verifies |
| Child appears before parent → unknown | `parent_index < row_index` guard | L2024 |

### Benchmark Semantic Derivation

| Plan Requirement | Implementation | Evidence |
|---|---|---|
| `section_id != "§2"` → unknown | First check in `_derive_text_semantic_context` | L2190 |
| `context_label > heading_path > raw_text` | Evaluation order: context → heading → raw | L2195–2211 |
| Investment objective context blocks benchmark | `context_objective` returns immediately, no heading/raw override | L2203 |
| `context_label` benchmark + heading objective → unknown | `heading_objective` check inside `context_benchmark` branch → `"unknown"` | Runtime verified |
| Delimiter-aware prefix (:, ：, \|, ｜, space) | `_raw_text_has_local_label` suffix check | L2235–2237 |
| Full-width space stripped | `str.lstrip()` handles U+3000 (Unicode whitespace) | Runtime verified |

### Tests Coverage vs Plan Requirements

| Plan Test | Implemented | Status |
|---|---|---|
| 1. Equity aggregate closes | `test_raw_legacy_portfolio_bundle_enriches_equity_aggregate_row` | ✅ |
| 2. Stock child closes | `test_raw_legacy_portfolio_bundle_enriches_stock_child_under_equity_parent` (parametrized: `其中：股票`, `其中:股票`) | ✅ |
| 3. Identical values close distinct rows | `test_raw_legacy_identical_equity_and_stock_values_close_distinct_rows_when_hierarchy_proven` | ✅ |
| 4. No parent → residual | `test_raw_legacy_stock_child_without_equity_parent_remains_residual` | ✅ |
| 5. No `其中` marker → residual | `test_raw_legacy_stock_label_without_child_marker_remains_residual` (parametrized: `股票`, `普通股`) | ✅ |
| 6. No child → residual | `test_raw_legacy_equity_without_explicit_child_remains_residual` | ✅ |
| 7. Neighbor labels → residual | `test_raw_legacy_neighbor_labels_still_do_not_prove_hierarchy_after_enrichment` | ✅ |
| 8. Detail row → residual | `test_raw_legacy_detail_or_geography_row_does_not_bridge_equity_parent_to_stock_child` | ✅ |
| 9. Top-level resets scope | `test_raw_legacy_top_level_asset_row_resets_parent_scope` | ✅ |
| 10. Benchmark via context_label | `test_raw_legacy_text_span_with_benchmark_context_label_closes_benchmark` | ✅ |
| 11. Benchmark via raw prefix | `test_raw_legacy_text_span_with_benchmark_row_prefix_closes_benchmark` | ✅ |
| 12. Benchmark via heading_path | `test_raw_legacy_text_span_with_benchmark_heading_path_closes_benchmark_when_context_generic` | ✅ |
| 13. Investment objective → residual | `test_raw_legacy_investment_objective_text_mentions_benchmark_but_remains_residual` | ✅ |
| 14. Ambiguous labels → residual | `test_raw_legacy_ambiguous_benchmark_and_objective_labels_remain_residual` | ✅ |
| 15. Non-§2 → residual | `test_raw_legacy_benchmark_label_outside_section_two_remains_residual` | ✅ |
| 16. Cross-layer conflict → residual | `test_raw_legacy_context_objective_heading_benchmark_conflict_remains_residual` | ✅ |
| 17. F015/F020/S4-F015 regression | All existing tests pass | ✅ |
| 18. Invalid literal regression | `test_invalid_literals_become_unknown_and_fail_target_predicates` passes | ✅ |
| 19. v2 non-overwrite | `test_v2_bundle_with_unknown_hierarchy_is_not_repaired_by_v1_enrichment` | ✅ |
| `其中：普通股` remains residual | `test_raw_legacy_stock_child_plain_common_share_label_remains_residual_under_current_rules` | ✅ (额外) |

All 19 plan-required tests + 1 extra guard test implemented. ✅

### Additional Runtime Edge Case Verification

| Scenario | Expected | Result |
|---|---|---|
| `context_label="业绩比较基准"` + `heading_path=("投资目标",)` | `unknown` (cross-layer conflict) | ✅ |
| `context_label=""` + `heading_path=("业绩比较基准", "投资目标")` | `unknown` (heading double-label) | ✅ |
| `context_label=""` + `raw_text="业绩比较基准：..."` | `benchmark` (raw prefix) | ✅ |
| `context_label="业绩比较基准"` + `raw_text="投资目标：..."` | `unknown` (cross-layer) | ✅ |
| `raw_text` with full-width space `　业绩比较基准` + delimiter | `True` (prefix detected) | ✅ |
| `raw_text` mid-sentence mention `紧密跟踪业绩比较基准` | `False` | ✅ |

---

## Boundary Verification

| Requirement | Status | Evidence |
|---|---|---|
| `NOT_READY` preserved | ✅ | Evidence verdict: `IMPLEMENTATION_COMPLETE_NOT_READY` |
| `source_truth_status=not_proven` | ✅ | All new test assertions verify `not_proven` |
| `candidate_only=true` | ✅ | Existing + new tests preserve |
| No source truth acceptance | ✅ | Evidence confirms |
| No baseline promotion | ✅ | Evidence confirms |
| No parser replacement | ✅ | Evidence confirms |
| No full field correctness | ✅ | Evidence confirms |
| No release/PR readiness | ✅ | Evidence confirms |
| Pure helper boundary | ✅ | `test_pure_helper_boundary_does_not_read_or_call_repository` passes |
| No live/network/provider/LLM | ✅ | Evidence confirms |
| No direct PDF/cache/source-helper | ✅ | Evidence confirms |
| No `FundDocumentRepository` in helper | ✅ | Existing boundary test passes |
| v2 non-overwrite | ✅ | Test + guard unchanged |
| No `FIELD_RULES` expansion for `普通股` | ✅ | Runtime check in test |
| No Service/UI/Host/renderer change | ✅ | Only candidate internals modified |
| No evidence-wrapper v2 prefill | ✅ | Enrichment is helper-side only |
| All 60 existing tests still pass | ✅ | Zero regression |
| git diff-check clean | ✅ | exit 0, no output |

## Residual Risks

1. `_is_stock_child_label` 子串匹配接受 `"其中：股票投资"` 等变体。当前安全，未来可能需要收紧白名单。
2. Cross-layer benchmark/objective 冲突的两个方向（F-DS-I2, F-DS-I3）仅一个方向有显式测试。实现均 fail-closed → `"unknown"`。
3. 真实年报 hierarchy 可能与 label pattern 不完全匹配（如非标准命名 `"权益投资合计"`, `"减：股票投资"` 等），需要 re-evidence gate 验证。

## Self-Check

pass — review 在 AgentDS 范围内完成。80/80 测试通过，零回归。实现严格遵循 accepted plan：table-local explicit labels 专用、value equality/bounded neighbor 未使用、v2 non-overwrite 守卫完整、benchmark 优先级链正确、`其中：普通股` 保持 residual 且 FIELD_RULES 未扩展。4 项 Info findings 均为非阻塞性的覆盖率/匹配范围建议。无 blocking findings。

Verdict: `PASS`。Blocking findings: 0。
