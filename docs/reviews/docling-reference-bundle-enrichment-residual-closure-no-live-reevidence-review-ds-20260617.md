# Docling Reference Bundle Enrichment Residual Closure No-live Re-evidence Review (AgentDS) — 2026-06-17

Gate: `Docling Reference Bundle Enrichment Residual Closure No-live Re-evidence Gate`
Role: AgentDS evidence review worker only
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

## Validation Commands

```text
python -m json.tool reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json
git diff --check -- reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-20260617.md
```

Result: JSON valid, git diff-check clean (exit 0, no output).

## Findings

### F-DS-E1 (Info) — Evidence wrapper 的 `target_seven_summary` 中 residual 行的 `matched_*_path` 全部为空数组

**Matrix evidence**: rows S5-F032, S6-F041, S6-F049, S6-F050 的 `matched_row_label_path`、`matched_column_header_path`、`matched_table_context` 均为 `[]`，同时 `source_layer_status` 为 `"same_source_reference_loaded"`。

**分析**: 这是 helper `_close_row` 的正确行为——当 `_evaluate_semantics` 返回非 satisfied 状态时，`_result()` 以 `match=None` 调用，导致 matched paths 为空。`same_source_reference_loaded` 表示 candidate 文本在 source 中被找到，但没有 match 能满足该字段的 fund 层语义规则。

**影响**: 对 closed 行，matched paths 携带了足够的证明上下文（如 F015 的 column_header 含 C 类和本期，F020 的 row_label 含 A 份额）。对 residual 行，空 matched paths 意味着无法从 matrix 直接判断 WHY 语义规则被拒绝——需要回溯到原始 bundle 数据才能诊断。这不影响正确性，但降低了 matrix 对 residual 原因的可解释性。建议在 residual 行中保留最佳（被拒绝的）match 的路径信息，用于诊断。

**Severity**: Info — 不影响矩阵正确性，纯属诊断完备性建议。当前 residual 原因（`"same-source value is present but fund semantic context is not proven"`）在所有 4 行中一致且准确。

### F-DS-E2 (Info) — `previous_20260616` summary 中 `s5_f023_closed_with_same_source_proof` 命名可能引起混淆

**Evidence document**: `previous_20260616.s5_f023_closed_with_same_source_proof: true`

**分析**: S5-F023（investment_objective）的 `current_disposition` 是 `"source_body_mismatch"`。此 disposition 来自 source_truth_matrix（20260616），表示 source_truth 步骤未找到同源文本。但 20260616 的 residual closure 步骤找到了文本并闭合了该行。新 re-evidence 也闭合了该行。命名 `s5_f023_closed_with_same_source_proof` 容易与 source_truth 的 "same source" 概念混淆——这里实际是 closure 步骤的 "same-source reference" 命中，与 source_body_mismatch 的输入 disposition 不矛盾。

**Severity**: Info — 不构成不一致，但命名建议更精确（如 `s5_f023_closed_with_reference_match`）。

---

## Matrix Validation (12 Programmatic Checks)

| # | Check | Result |
|---|---|---|
| 1 | 17 rows total, summary consistent | PASS |
| 2 | 13 closed + 4 residual = 17, disposition tally matches | PASS |
| 3 | All 17 rows: `source_truth_status="not_proven"`, `candidate_only=true`, guard flags true | PASS |
| 4 | Target seven: F015/F020/S4-F015 closed; S5-F032/S6-F041/S6-F049/S6-F050 residual | PASS |
| 5 | By-sample counts: S1=3, S4=3, S5=4, S6=7; summary by_sample matches | PASS |
| 6 | All source_layer_status = `same_source_reference_loaded` | PASS |
| 7 | All processed_layer_status = `locator_context_available` | PASS |
| 8 | S5-F023 (investment_objective) closed with semantic_rule_satisfied | PASS |
| 9 | S6-F041 (benchmark) residual with semantic_rule_rejected | PASS |
| 10 | S6-F049/S6-F050 share identical value `149698325.51`, both residual | PASS |
| 11 | Top-level guard flags: all 7 true | PASS |
| 12 | Fund layer: 13 satisfied + 4 rejected = 17 | PASS |

## Target Seven Verification

| Fact ID | Field | Disposition | Fund Layer | Evidence Quality |
|---|---|---|---|---|
| **F015** | `sales_service_fee_C_current_year` | ✅ `disambiguated_source_body_match` | `semantic_rule_satisfied` | column_header 含 C 类 + 本期 → C share + current_period; section §7 + fee context → expense_fee_table; matched_row 含销售服务费 |
| **F020** | `manager_holding_range_A` | ✅ `disambiguated_source_body_match` | `semantic_rule_satisfied` | row_label 含 A 份额（same-row share-class proof）；section §10 + manager-holding context → manager_holding_table；matched_row 含基金经理持有 |
| **S4-F015** | `fixed_income_investment_amount` | ✅ `disambiguated_source_body_match` | `semantic_rule_satisfied` | matched_row 含固定收益投资；section §8 + portfolio context → portfolio_asset_composition_table |
| **S5-F032** | `equity_investment_amount` | ❌ `semantic_assignment_residual` | `semantic_rule_rejected` | 值在 source 中存在，但 hierarchy 未被 evidence wrapper 断言 → rejected_row_hierarchy_roles 中 `unknown`/`child` 拒绝 |
| **S6-F041** | `benchmark` | ❌ `semantic_assignment_residual` | `semantic_rule_rejected` | candidate 文本含"紧密跟踪业绩比较基准"——属于投资目标语境，非 benchmark 语义标签 → required_text_semantic_context="benchmark" 拒绝 |
| **S6-F049** | `equity_investment_amount` | ❌ `semantic_assignment_residual` | `semantic_rule_rejected` | 与 S6-F050 同值 `149698325.51`；hierarchy 未证明 aggregate vs child 区分 |
| **S6-F050** | `stock_investment_amount` | ❌ `semantic_assignment_residual` | `semantic_rule_rejected` | 与 S6-F049 同值；hierarchy 未证明 child-under-equity 关系 |

### F015 Closure Detail Cross-check

- `matched_column_header_path`: `["本期 2025年1月1日至2025年12月31日", "当期发生的基金应支付的销售服务费", "安信企业价值优选混 合C"]`
  - 含 `C` → share_class 派生为 C ✓
  - 含 `本期` → period 派生为 current_period ✓
- `matched_table_context`: `["§7", "table text contains fee-accounting label", ...]`
  - §7 + fee label → `_classify_table_family` 返回 expense_fee_table ✓
- `matched_row_label_path`: `["当期发生的基金应支付的销售服务费", "安信基金"]`
  - 含 "销售服务费" → `required_row_label_any` 命中 ✓
  - "安信基金" 是 same-row 上下文（不干扰匹配）✓

### F020 Closure Detail Cross-check

- `matched_row_label_path`: `["本基金基金经理持有 本开放式基金", "安信企业价值优选混合A"]`
  - 含"本基金基金经理持有" → 命中 manager holding row ✓
  - 含"A" → share_class 从 row_label 派生为 A ✓
- `matched_table_context`: 含 `"§10"`, `"manager-holding label"`, `"份额级别"`
  - §10 + manager-holding → manager_holding_table ✓

### S4-F015 Closure Detail Cross-check

- `matched_row_label_path`: `["固定收益投资"]` ✓
- `matched_table_context`: `["§8", "table text contains portfolio/fair-value/financial-statement label", "序号", "项目", "金额", ...]`
  - §8 + portfolio label → `_classify_table_family` 返回 portfolio_asset_composition_table ✓
  - Not fair_value_hierarchy_table → 不被 rejected_table_families 拒绝 ✓

### Residual Rows Cross-check

- **S5-F032**: S5 是 QDII 指数基金（017641 摩根标普500），equity 金额 `1818456375.25` 在 source 中存在。但 bundle 不含 hierarchy 信息，equity rule 的 `rejected_row_hierarchy_roles=("child", "unknown")` 拒绝所有 unknown-role 匹配 → correct residual ✓
- **S6-F041**: candidate `"紧密跟踪业绩比较基准,追求跟踪偏离度及跟踪误差的最小化."` 在 source 中存在（source_layer_status=same_source_reference_loaded），但 matched context 不含 benchmark 语义标签。benchmark rule 的 `required_text_semantic_context="benchmark"` 加上 `rejected_row_label_any=("投资目标",)` → 投资目标语境被拒绝。bundle 的 8 个 text_spans 中可能不含 benchmark 标签 → correct residual ✓
- **S6-F049 / S6-F050**: 同值 `149698325.51`，在同一 table（`docling_table_91`）的不同行（r1 vs r2）。evidence wrapper 未断言 hierarchy，v1 bundle 不含 `row_parent_label_path`/`row_hierarchy_role` → 两条规则均 fail-closed ✓

---

## Evidence Wrapper Assumptions Challenge

### 1. Raw Legacy v1 Bundle, No v2 Prefill

**Claim**: `reference_bundle_construction.bundle_schema = "raw legacy repository_reference_bundle.v1; helper performs in-memory enrichment"`

**Verified**: 
- 所有 4 个 repository load 的 `reference_bundle_schema_version` 均为 `"repository_reference_bundle.v1(raw legacy; helper enrichment delegated)"` ✓
- `v2_fields_intentionally_not_prefilled` 列出 7 个字段：table_family, share_class_context, period_context, row_parent_label_path, row_hierarchy_path, row_hierarchy_role, semantic_context_label ✓
- 这些字段由 helper 的 `_enrich_reference_bundle_contexts` 在 v1 路径上自动派生 ✓
- Controller judgment 明确接受 v1-only enrichment guard ✓

**结论**: 符合 accepted implementation 的行为约定。v1 bundle 经 coercion → enrichment → closure 链条正确处理。

### 2. Same-Row Share-Class Proof

**Claim**: `"when ParsedTable has a '份额级别' column, its same-row value is included in row_label_path for sibling value cells"`

**Verified**:
- F020: matched_row_label_path 含 `"安信企业价值优选混合A"`。该值来自同一 ParsedTable 行的"份额级别"列 → share_class 从 row_label 派生为 A ✓
- F015: matched_column_header_path 含 `"安信企业价值优选混 合C"`。share_class 从 column_header 派生为 C ✓
- 两种来源（column_header vs row_label）均在 `allowed_share_class_context_sources` 范围内 ✓

**潜在风险**: row_label_path 中混入非行标签信息（份额级别列值）可能在未来影响其他 row_label 匹配。当前无负面影响——所有 target rule 的 `required_row_label_any` 和 `rejected_row_label_any` 均能正确区分。

### 3. Table Context Scope

**Claim**: `"derived deterministically from ParsedTable section inference reason and headers only; table row labels remain row-local context"`

**Verified**: 
- 所有行的 `matched_table_context` 包含 section inference reason（如 `"table text contains fee-accounting label"`）和 ParsedTable headers ✓
- 不包含来自其他行的 row labels → 防止跨行 context 污染 ✓
- section inference reason 参与 `_classify_table_family` 的 signal 构建 → 支持 table_family 分类 ✓

### 4. Row Hierarchy Residual Handling

**Claim**: `"not asserted by evidence wrapper; rows requiring hierarchy remain residual unless helper can prove them from accepted inputs"`

**Verified**:
- S6-F049/S6-F050: 同值不同行，hierarchy 未证明 → residual ✓
- S5-F032: equity amount，hierarchy 未证明 → residual ✓
- F015/F020/S4-F015: 不依赖 hierarchy → enrichment 后闭合 ✓

**一致性**: 闭合的 3 行均不依赖 `row_hierarchy_role`/`row_parent_label_path`。Residual 的 4 行中有 3 行直接依赖 hierarchy（S5-F032, S6-F049, S6-F050），1 行依赖 text_semantic_context（S6-F041）。证据 wrapper 的 hierarchy policy 与结果一致。

---

## Boundary Verification

| Requirement | Status | Evidence |
|---|---|---|
| `source_truth_status = "not_proven"` | ✅ | Top-level + all 17 rows |
| `candidate_only = true` | ✅ | Top-level + all 17 rows |
| `not_source_truth = true` | ✅ | Guard flag |
| `not_baseline_promotion = true` | ✅ | Guard flag |
| `not_parser_replacement = true` | ✅ | Guard flag |
| `not_full_field_correctness = true` | ✅ | Guard flag |
| `not_release_readiness = true` | ✅ | Guard flag |
| `not_raw_pdf_bbox_truth = true` | ✅ | Guard flag |
| `NOT_READY` preserved | ✅ | Verdict token + evidence doc |
| No live/network/provider/LLM | ✅ | `force_refresh=false`, socket guard recorded ×4 |
| Annual-report access repository-mediated | ✅ | `FundDocumentRepository.load_annual_report(..., force_refresh=False)` |
| S1 parsed_cache_hit | ✅ | True |
| S4 parsed_cache_hit | ✅ | True |
| S5 pdf_cache_hit (not parsed) | ✅ | parsed_cache_hit=false, pdf_cache_hit=true (repository-mediated) |
| S6 parsed_cache_hit | ✅ | True |
| No raw PDF/cache/source-helper bypass | ✅ | Stated + consistent with repository metadata |
| JSON valid | ✅ | `python -m json.tool` exit 0 |
| git diff-check clean | ✅ | exit 0, no output |
| 13 closed + 4 residual = 17 | ✅ | Programmatic check passed |
| Previous 20260616: 10→13 improvement | ✅ | +3 from target seven (F015, F020, S4-F015) |

## Residual Risks

1. **Matched paths empty for residual rows**: 如 F-DS-E1 所述，residual 行的 matched paths 为全空，无法从 matrix 直接理解语义拒绝的具体原因。需回溯原始 bundle 数据做诊断。
2. **Same-row share-class proof 机制**: row_label_path 中包含份额级别列值。当前正确工作，但如果未来规则依赖精确的 row_label 结构（如仅接受单一 label），可能产生意外交互。
3. **S5 使用 pdf_cache_hit=true**: 区别于其他 sample 的 parsed_cache_hit。pdf_cache_hit 表示需从 PDF 重新解析。该路径仍在 `FundDocumentRepository` 内，符合 repository-mediated 约束，但需注意 S5 的 table_count=114 和 cell_count=6739 明显大于其他 sample。
4. **Hierarchy 仍未证明**: S5-F032、S6-F049、S6-F050 因 hierarchy 缺失保持 residual。未来需在 evidence wrapper 或上游 bundle 构造中明确 hierarchy 证明机制才能闭合这些行。
5. **S6-F041 benchmark residual**: benchmark 规则要求语义标签。当前 8 个 text_spans 中可能已有 benchmark 标签但未被 evidence wrapper 正确赋给对应 text_span。需在 evidence wrapper 层确认 text_span 的 semantic_context_label 派生逻辑。
6. **No real document source truth**: 所有结果仍是 candidate-only helper 输出。`source_truth_status=not_proven` 在所有行中一致。

## Self-Check

pass — evidence review 在 AgentDS 范围内完成。12 项程序化检查全部通过，target seven 逐行验证，evidence wrapper 的 4 项假设逐一交叉验证。无 blocking finding。2 项 Info finding 均为诊断完备性或命名建议。矩阵与 evidence 文档一致，与 accepted controller judgment 和 accepted implementation 行为边界一致。

Final verdict: `PASS`。Blocking findings: 0。
