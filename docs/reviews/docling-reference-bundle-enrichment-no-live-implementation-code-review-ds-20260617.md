# Docling Reference Bundle Enrichment No-live Implementation Code Review (AgentDS) — 2026-06-17

Gate: `Docling Reference Bundle Enrichment No-live Implementation Gate`
Role: AgentDS code review worker only
Verdict: `PASS`
Release/readiness: `NOT_READY`

## Reviewed Artifacts

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- `docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-evidence-20260617.md`

## Accepted Plan / Judgment

- `docs/reviews/docling-reference-bundle-field-spec-plan-20260617.md`
- `docs/reviews/docling-reference-bundle-field-spec-plan-controller-judgment-20260617.md`

## Validation Commands Executed

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py -v
git diff --check -- fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py
```

Result: `56 passed in 0.77s`, whitespace clean with no output.

---

## Findings

### F-DS-1 (Low) — `_enrich_reference_bundle_contexts` 未接入 `close_source_truth_residuals` 主流程

**File/line**: `source_truth_residual_closure.py:714–750` (`close_source_truth_residuals`), `source_truth_residual_closure.py:1894–1923` (`_enrich_reference_bundle_contexts`)

**Issue**: 模块定义了完整的 enrichment pipeline（`_classify_bundle_tables` → `_enrich_reference_bundle_contexts`），但 `close_source_truth_residuals` 在 `_coerce_reference_bundles` 之后不调用 enrichment。所有测试通过显式传入预富化 fixture 来验证行为，但上游调用方如果直接传入原始 bundle dict，cell 的 `table_family`、`share_class_context`、`period_context` 等全部保持 `"unknown"` 默认值，无法闭合任何使用 enriched predicate 的目标行。

**Why it matters**: 按 plan 的 Slice 2 设计，table-family classification 是 "an explicit bundle/table-level enrichment step"，应在 coercion 之后、closure 之前执行。当前实现函数存在且正确，但没有一个统一的入口点执行 enrichment → closure 链路。这不会导致错误闭合（fail-closed 是正确的），但会导致调用方遗漏 enrichment 时所有目标行静默 residual，可能被误判为"数据不支持闭合"而非"未执行 enrichment"。

**Suggested fix**: 在 `close_source_truth_residuals` 中对每个 bundle 调用 `_enrich_reference_bundle_contexts`，确保 enrichment 作为 closure 的隐式预处理步骤；或在模块 docstring 中明确声明 enrichment 是调用方的前置责任。两种方案均可，当前测试结构兼容两者。

**Severity justification**: 不影响正确性（fail-closed），当前测试通过且没有生产调用方。属于契约清晰度问题而非 bug。

### F-DS-2 (Low) — `_cell_has_required_text_semantic_context` 仅处理 benchmark 情况

**File/line**: `source_truth_residual_closure.py:1606–1632`

**Issue**: 该函数对 `required_context == "benchmark"` 实现了完整逻辑（拒绝投资目标上下文、要求业绩比较基准标签），但对其他所有 `TextSemanticContext` 值（`"investment_objective"`, `"fund_profile"`, `"other"`）直接返回 `False`。当前只有 benchmark 规则设置了 `required_text_semantic_context`，所以不存在功能缺失。

**Failure mode**: 如果未来某条规则对 `investment_objective` 设置 `required_text_semantic_context="investment_objective"`，该函数会静默返回 `False`，导致该规则永远无法通过 cell match 闭合（只能通过 text_span match）。

**Suggested fix**: 当前可以接受，但建议在函数 docstring 中注明当前仅实现 benchmark 分支，并在 `return False` 前加注释 `# 其他 TextSemanticContext 暂未实现 cell 级别检查`。

**Severity justification**: 无当前影响，仅影响未来扩展。属于代码可维护性提醒。

### F-DS-3 (Low) — `_period_context_from_text` 复合标签的匹配顺序可能导致误判

**File/line**: `source_truth_residual_closure.py:1819–1845`

**Issue**: 函数按 `period_end → prior_period → current_period` 顺序检查。对于复合标签如 `"上年度可比期间末"`（normalized 后包含 `"上年度可比期间"` 也包含 `"末"`），会匹配到 `"期末"`（因为 `"期末" in "上年度可比期间末"` → True），返回 `period_end` 而非预期的 `prior_period`。中国年报中 `"上年度可比期间期末"` 是常见的列标题表述，其语义是 prior_period 的 period_end snapshot。当前按 `period_end` 返回可能会与 pure current_period 的 `"报告期末"` 混同。

**Failure mode**: 某一列标题为 `"上年度可比期间期末"`，派生为 `period_end`。F015 规则要求 `period_context == "current_period"` 且 `rejected_period_contexts=("prior_period", "unknown")`。该列不会被 F015 接受（因为要求的是 current_period），但标签语义中隐含了 prior 信息。当前 `period_end` 分类不会导致错误闭合，但如果未来某规则用 `required_period_context="prior_period"` 匹配该列，将无法命中。

**Suggested fix**: 将 `period_end` 检查中的 `"期末"` 改为更精确的匹配（如要求在 `"报告期末"` / `"期末余额"` / `"期末公允价值"` 的上下文中出现，而非独立的 `"期末"` 子串）。或在匹配 `"期末"` 之前先检查是否属于 prior_period 的 period-end（如 `"上年度可比期间末"` 或 `"上期末"`）。当前影响有限，可作为后续 gate 的改进项。

**Severity justification**: 边界情况，当前规则不会被此问题导致误闭合。

### F-DS-4 (Info) — `_enrich_reference_bundle_contexts` 缺少直接集成测试

**File/line**: `tests/fund/documents/test_docling_source_truth_residual_closure.py`

**Issue**: `_classify_table_family`、`_derive_share_class_context`、`_derive_period_context` 都有独立的单元测试，但组合函数 `_enrich_reference_bundle_contexts`（先 classify 再 derive share/period）没有直接测试。当前通过间接路径验证（预富化 fixture 在 target rule 测试中工作正常），但 enrichment pipeline 的端到端行为（如分类结果广播到同一 table 的所有 cell、派生字段不覆盖已有值等）未被显式断言。

**Suggested fix**: 添加一个测试：构造一个含有多个 cell 的 bundle（部分 cell 属于同一 table），调用 `_enrich_reference_bundle_contexts`，验证 table_family 广播、share/period 派生、enrichment_status 不变。

**Severity justification**: 信息性，不影响正确性。现有间接覆盖充分。

### F-DS-5 (Info) — `test_identical_portfolio_values_remain_residual_without_proven_hierarchy` 测试命名不够精确

**File/line**: `tests/fund/documents/test_docling_source_truth_residual_closure.py:662–703`

**Issue**: 测试名暗示 "without_proven_hierarchy" 是保持 residual 的原因，但测试中 cell 的 `table_family` 也是默认 `"unknown"`，而被测规则的 `rejected_table_families` 包含 `"unknown"`。实际 rejection 由 table_family 和 hierarchy 双重触发。如果目的是仅测试 hierarchy 不足时的行为，应显式设置 `table_family="portfolio_asset_composition_table"` 并保持 hierarchy 为 unknown。

**Suggested fix**: 拆分或重命名测试，使其更精确地反映双重 rejection 路径。单独测试 table_family 不足和 hierarchy 不足的独立路径已分别存在（`test_new_table_family_rejection_overrides_legacy_raw_context_match` 和 `test_equity_amount_closes_only_aggregate_row_not_stock_child_or_detail`），当前测试可以作为"全未富化时的综合 residual 行为"保留，但名称应与实现一致。

**Severity justification**: 信息性，断言正确，不影响测试有效性。

---

## Cross-Check Matrix

| Plan Requirement | Status | Evidence |
|---|---|---|
| Literal aliases all match plan spec | ✅ | Lines 57–100, all 8 aliases verified |
| RepositoryReferenceCell 12 new fields | ✅ | Lines 263–275, types & defaults match |
| RepositoryReferenceTextSpan 2 new fields | ✅ | Lines 352–354 |
| RepositoryReferenceBundle 3 new fields | ✅ | Lines 412–414 |
| ResidualClosureRule 10 new fields | ✅ | Lines 201–210 |
| to_dict emits all new fields | ✅ | Lines 290–319, 369–383, 429–441 |
| _coerce_cell does NOT infer table_family | ✅ | Line 1234–1238, coerces literal only |
| _coerce_bundle does NOT infer enrichment_status from cells | ✅ | Lines 1177–1181, coerces literal only |
| Table-family classification deterministic | ✅ | `_classify_table_family` uses priority-ordered signals |
| Conflict resolution: fair-value overrides portfolio | ✅ | Lines 2057–2058, `_resolve_table_family_conflict` |
| Row hierarchy: standalone default behavior | ✅ | Lines 1210–1211, only when role proven |
| Share/period derivation uses header_band | ✅ | Lines 1701–1737, 1760–1795 |
| New table-family fields take precedence over legacy | ✅ | Lines 1017–1028, `has_new_table_family_predicate` guard |
| Legacy raw context cannot override new-field rejection | ✅ | Test `test_new_table_family_rejection_overrides_legacy_raw_context_match` |
| S6-F041 fail-closed unless benchmark-labeled | ✅ | Test `test_benchmark_guard_keeps_investment_objective_context_residual` and `test_benchmark_closes_only_with_benchmark_semantic_label` |
| S6-F049/S6-F050 fail-closed unless hierarchy distinguishes | ✅ | Tests `test_equity_amount_closes_only_aggregate_row_not_stock_child_or_detail`, `test_stock_amount_closes_only_child_stock_row_under_equity_parent`, `test_identical_portfolio_values_remain_residual_without_proven_hierarchy` |
| bounded_neighbor_row_labels not used for positive proof | ✅ | Test `test_neighbor_row_labels_do_not_prove_positive_hierarchy` |
| No live/network/source acquisition | ✅ | `test_pure_helper_boundary_does_not_read_or_call_repository`, no such imports |
| No direct PDF/cache/source-helper/repository calls | ✅ | Same test, `builtins.open` blocked |
| No Service/UI/Host/renderer/quality-gate changes | ✅ | Only candidate internals touched |
| candidate_only preserved | ✅ | `test_output_guard_flags_are_preserved`, `test_candidate_boundary_guard_rejects_truth_claims` |
| NOT_READY preserved | ✅ | Guard flags: not_baseline_promotion, not_parser_replacement, not_release_readiness |
| ResidualClosureRule remains Python-only | ✅ | No JSON serialization/coercion for rules |
| Legacy payloads deserialize with unknown defaults | ✅ | `test_legacy_reference_bundle_payload_deserializes_with_unknown_defaults` |
| Invalid literals → unknown, fail target predicates | ✅ | `test_invalid_literals_become_unknown_and_fail_target_predicates` |

## Rule-by-Rule Predicate Verification

### F015 (`sales_service_fee_C_current_year`)
- `allowed_table_families=("expense_fee_table",)` ✅
- `rejected_table_families=("unknown", "other")` ✅
- `share_class_context="C"` ✅
- `required_period_context="current_period"` ✅
- `rejected_period_contexts=("prior_period", "unknown")` ✅
- `allow_semantic_equivalent_duplicate=True` ✅
- `allowed_share_class_context_sources` covers all 4 sources ✅
- Parametrized test covers: C/current/expense ✅, A/current/expense ❌, C/prior/expense ❌, C/unknown/expense ❌, C/current/unknown ❌

### F020 (`manager_holding_range_A`)
- `allowed_table_families=("manager_holding_table",)` ✅
- `rejected_table_families=("unknown", "other")` ✅
- `share_class_context="A"` ✅
- Parametrized test covers: A/manager-holding/correct-row ✅, C/manager-holding ❌, A/unknown ❌, A/manager-holding/employee-row ❌

### S4-F015 (`fixed_income_investment_amount`)
- `allowed_table_families=("portfolio_asset_composition_table",)` ✅
- `rejected_table_families` includes fair_value_hierarchy, financial_statement, holding_detail, unknown, other ✅
- New field rejection overrides legacy raw context ✅

### S5-F032 / S6-F049 (`equity_investment_amount`)
- `rejected_row_hierarchy_roles=("child", "unknown")` ✅
- `rejected_table_families` includes holding_detail ✅
- `rejected_row_label_any` includes stock-child labels ✅
- Aggregate row ✅ closes, stock child ❌, detail ❌

### S6-F050 (`stock_investment_amount`)
- `required_parent_row_label_any=("权益投资",)` ✅
- `required_row_hierarchy_role="child"` ✅
- `rejected_row_label_any` blocks non-stock-child ✅
- Child under equity ✅ closes, aggregate ❌

### S6-F041 (`benchmark`)
- `required_text_semantic_context="benchmark"` ✅
- `rejected_row_label_any=("投资目标",)` ✅ (redundant defense)
- Text span with benchmark label ✅ closes, investment_objective ❌
- Cell with 投资目标 context ❌ (double-rejected)

---

## Open Questions

None. All plan requirements are addressed.

## Residual Risks

1. **Enrichment pipeline 未自动化**: `_enrich_reference_bundle_contexts` 不会被 `close_source_truth_residuals` 自动调用。如果未来的 evidence gate 直接传入原始 bundle dict 而不经 enrichment 预处理，所有 target row 将静默保持 residual。风险owner：implementation owner，在下一 evidence gate 中确认 enrichment 调用链。

2. **`_period_context_from_text` 复合标签边界**: 如 F-DS-3 所述，`"上年度可比期间期末"` 等标签的匹配存在理论歧义。当前不会导致误闭合，但如果未来规则需要精确区分 prior_period_end vs current_period_end，需要改进匹配逻辑。

3. **`_cell_has_required_text_semantic_context` 仅实现 benchmark**: 如 F-DS-2 所述，未来扩展需要补充实现。

4. **No real document evidence**: 如 evidence 文档所述，所有测试使用内存 fixture，未证明任何 source truth row 可被接受。这属于后续 evidence gate 的范围，不在本 gate scope 内。

## Validation Checks

- [x] 56/56 tests pass
- [x] `git diff --check` clean
- [x] All 8 literal aliases match plan spec
- [x] All 27 new dataclass fields match plan spec (types, defaults, serialization)
- [x] `_coerce_cell` does not infer `table_family`
- [x] `_coerce_bundle` does not infer `enrichment_status` from cells
- [x] Table-family classification deterministic and priority-ordered
- [x] Share/period derivation uses header_band in priority order
- [x] New table-family fields take precedence over legacy `required_table_family_any`
- [x] S6-F041 fail-closed for investment-objective context
- [x] S6-F049/S6-F050 fail-closed without proven hierarchy
- [x] `bounded_neighbor_row_labels` never used for positive proof
- [x] Pure-helper boundary: no `open()`, no `FundDocumentRepository`, no source helper imports
- [x] Guard flags preserved: `not_baseline_promotion`, `not_parser_replacement`, `not_release_readiness`, `not_full_field_correctness`, `not_raw_pdf_bbox_truth`, `candidate_only`
- [x] `NOT_READY` preserved
- [x] No live/network/source acquisition/provider/LLM/analyze/checklist/golden/readiness/release behavior
- [x] No Service/UI/Host/renderer/quality-gate changes

## Self-Check

pass — review stayed within AgentDS code review scope. No files were edited, staged, committed, or pushed. All findings are evidence-based with specific file/line references, counterexamples, and severity justification. The implementation conforms to the accepted field-spec plan and controller judgment, preserves candidate-only fail-closed boundaries, and has no blocking findings.
