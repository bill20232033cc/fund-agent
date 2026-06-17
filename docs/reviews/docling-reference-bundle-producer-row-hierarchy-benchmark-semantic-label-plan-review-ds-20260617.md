# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Plan Review (AgentDS) — 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Planning Gate`
Role: AgentDS plan review worker only
Verdict: `PASS_WITH_FINDINGS`
Release/readiness: `NOT_READY`

## Reviewed Artifact

- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md`

## Accepted Inputs Cross-checked

- `docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-controller-judgment-20260617.md`
- `docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-review-ds-20260617.md`
- `docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-review-mimo-20260617.md`
- `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json`
- `source_truth_residual_closure.py` (current helper)
- `test_docling_source_truth_residual_closure.py` (current tests)

## Code Facts Verification

Plan claims checked against current `source_truth_residual_closure.py`:

| Plan Claim | Status | Evidence |
|---|---|---|
| `RepositoryReferenceCell` has hierarchy fields | ✅ | `row_parent_label_path` (L270), `row_hierarchy_path` (L270), `row_hierarchy_role` (L272) |
| `RepositoryReferenceTextSpan` has `semantic_context_label` | ✅ | L358 |
| `_enrich_reference_bundle_contexts` enriches v1 bundles | ✅ | L1919–1920 v1 guard, L1921 classify, L1923–1933 share/period |
| `_match_satisfies_rule` consumes `span.semantic_context_label` | ✅ | L974–980 |
| `equity_investment_amount` rejects `("child", "unknown")` | ✅ | L651 |
| `stock_investment_amount` requires parent `权益投资` + `role="child"` | ✅ | L666–667 |
| `benchmark` requires `required_text_semantic_context="benchmark"` | ✅ | L713 |
| `_row_primary_label`, `_is_equity_parent`, `_is_stock_child`, `_is_explicit_top_level_asset_row` do NOT exist | ✅ | grep returns no matches |
| `_enrich_row_hierarchy_contexts`, `_enrich_text_span_semantic_contexts` do NOT exist | ✅ | grep returns no matches |

---

## Findings

### F-DS-P1 (Medium) — `_row_primary_label(cell)` 函数行为未定义

**Plan reference**: Step 1 function signatures (line 374), "Parent proof" section (line 208–212), "Child proof" section (line 225–229)

**Issue**: 该函数是 hierarchy 推导的核心——决定一行是 parent（含 `权益投资`）、child（含 `其中：股票`）还是 top-level asset row。Plan 列出了函数签名但未定义其行为：

- 返回 `row_label_path[-1]`（最后一个/最具体的标签）？
- 返回 `row_label_path[0]`（第一个/最通用的标签）？
- 返回拼接后的全路径字符串？
- 检查 `row_label_path` 的所有元素？

**失败模式**: 对于 `row_label_path = ("资产", "权益投资")`：
- 返回 `"资产"` → parent 检查 `"权益投资" in "资产"` → False → 不会被识别为 parent
- 返回 `"权益投资"` → True → 被识别为 parent
- 返回 `"资产权益投资"` (join) → True → 被识别为 parent（但可能误匹配其他情况）

不同实现会产生不同的 hierarchy 结果，直接导致 S5-F032/S6-F049/S6-F050 的闭合/非闭合差异。

**建议**: 明确定义 `_row_primary_label`：要么返回 `row_label_path[-1]`（最接近 cell value 的标签），并说明选择理由；要么定义 `_contains_any` 风格的检查逻辑（检查所有元素）。

**Severity**: Medium — 属于实现前必须澄清的设计决策，否则不同实现可能产生冲突结果。

### F-DS-P2 (Medium) — `context_label` 与 `heading_path` 之间的优先级未定义

**Plan reference**: "Derivation rules" 第 2–3 条 (line 313–314)，"Local label detection" (line 334–341)

**Issue**: Plan 规定了 `context_label` > `raw_text` 的优先级（"Treat `context_label` as stronger than `raw_text`"），但未规定 `context_label` 与 `heading_path` 之间的优先级。

场景：`context_label="投资目标"` 且 `heading_path` 包含 `"业绩比较基准"`。

按当前规则：
- Rule 2：explicit investment-objective label 在 context_label 中 → 返回 `investment_objective`
- Rule 3：explicit benchmark label 在 heading_path 中 → 返回 `benchmark`

两种解读均合理，取决于实现顺序。Plan 应明确规定：
- `context_label` 优先于 `heading_path`（因为 context_label 是更局部的标签）
- 或：任意层出现投资目标标签就拒绝 benchmark
- 或：跨层冲突 → `"unknown"`（fail-closed）

**失败模式**: 在 `context_label="投资目标"`、`heading_path` 含 `"业绩比较基准"` 的 span 上，如果实现选择 rule 3 覆盖 rule 2，该 span 会被错误标记为 `"benchmark"`，导致 S6-F041 在投资目标语境下被误闭合。

**建议**: 明确规定检测优先级顺序：先检查 `context_label`，再检查 `heading_path`，最后检查 `raw_text` prefix。或统一规定：任意层检测到投资目标标签即拒绝 benchmark 分类。

**Severity**: Medium — 涉及 false-positive 风险（投资目标语境被误标为 benchmark）。

### F-DS-P3 (Low) — Benchmark 前缀/分隔符检测模式未精确指定

**Plan reference**: "Local label detection" (line 334–341)

**Issue**: Plan 描述了三种 label 模式（`业绩比较基准 | ...`、`业绩比较基准：...`、`业绩比较基准 ...`），但未指定：
- 检测在 normalization 之前还是之后
- 中英文冒号（`：` vs `:`）的处理
- tab、多空格、全角空格的处理
- pipe 分隔符（`|`）的变体

`_normalize_for_label()` 会去除所有 whitespace，导致 `"业绩比较基准  沪深300"` 归一化为 `"业绩比较基准沪深300"`，startswith 检查仍有效。但 `"业绩比较基准: 沪深300"` 中的 `:` 是否被归一化取决于 normalization 逻辑。

**建议**: 明确规定：先对 `raw_text` 做 `_normalize_for_label()`，再检查是否以 benchmark/investment_objective 标签开头。或定义独立的 delimiter-aware prefix 检测函数。

**Severity**: Low — 实现 worker 可合理推断，但明确规范可避免边缘情况争议。

### F-DS-P4 (Low) — 缺少 `heading_path` 作为 benchmark label 来源的正面测试

**Plan reference**: Required tests 10–14 (line 514–538)

**Issue**: Plan 的 derivation rules（line 314）明确规定 benchmark label 可从 `context_label` **或** `heading_path` 中检测。但必须测试仅覆盖了：
- Test 10: `context_label="业绩比较基准"` → 闭合 ✓
- Test 11: raw text 前缀 → 闭合 ✓
- Test 12–14: 均为负面测试

缺少测试：`context_label` 不包含 benchmark 标签，但 `heading_path` 包含 `"业绩比较基准"` → 应闭合。

**建议**: 添加一个测试：text span 的 `context_label` 为空或为通用标签，`heading_path` 含 `"业绩比较基准"`，验证 benchmark 正确闭合。

**Severity**: Low — derivation rules 已覆盖此路径，只是测试未显式覆盖。

### F-DS-P5 (Low) — Step 3 代码示例中引用了不存在的 `_enrich_share_period_contexts()`

**Plan reference**: Step 3 code block (line 428)

**Issue**:

```python
context_enriched = _enrich_share_period_contexts(hierarchy_enriched)
```

该函数在当前 codebase 中不存在。Plan 虽然补充说明 "If implementation does not introduce `_enrich_share_period_contexts()`, keep the existing loop"，但代码示例中的函数名会误导实现 worker。当前 `_enrich_reference_bundle_contexts` 内联了 share/period 派生逻辑（L1923–1933），无需抽取为独立函数。

**建议**: 从代码示例中移除 `_enrich_share_period_contexts`，或显式标注为可选重构。建议示例改为：

```python
classified = _classify_bundle_tables(bundle)
hierarchy_enriched = _enrich_row_hierarchy_contexts(classified)
# existing share/period derivation loop on hierarchy_enriched.cells
span_enriched = _enrich_text_span_semantic_contexts(share_period_enriched)
return span_enriched
```

**Severity**: Low — 有 fallback 说明，但代码示例可能引起混淆。

### F-DS-P6 (Low) — `row_index` 非连续值未显式确认可比较

**Plan reference**: Ambiguity fail-closed rules, "row order is non-integer, duplicated, or not comparable" (line 263)

**Issue**: "Nearest preceding parent" 逻辑依赖 `row_index` 比较。整数索引即使有 gaps（如 0, 2, 5），仍然可比较大小。但 Plan 的 fail-closed 条件 "not comparable" 未区分 "有 gaps 但可比较" 和 "非整数不可比较"。实现 worker 可能将 gaps 视为异常。

**建议**: 明确说明：整数 `row_index` 值无论是否连续均可比较；只有非整数或缺失时才 fall back 到 `unknown`。

**Severity**: Low — 整数比较天然支持 gaps，但明确文档可减少实现歧义。

---

## Adversarial Review: False-Positive Risk Analysis

### Can value equality alone prove hierarchy?

Plan 明确禁止（line 143–144: "value equality alone" → not allowed）。Hierarchy 推导仅基于 explicit label markers (`权益投资`, `其中：股票`)，不检查 cell value。✅

### Can bounded_neighbor_row_labels become positive proof?

Plan 明确禁止（line 262: "the relation can only be inferred from... bounded_neighbor_row_labels" → keep unknown）。Test 7 验证。✅

### Can a row without `其中` marker become child?

Plan 要求 child marker 必须包含 `其中` + (`股票` | `普通股`)（line 189–191）。单独的 `股票` 或 `普通股` 不被接受。Test 5 验证。✅

### Can `equity_investment_amount` close on a child row?

Rule `rejected_row_hierarchy_roles=("child", "unknown")` 拒绝 child 角色。Enrichment 只为 child rows 设置 role="child"，为 parent rows 设置 role="aggregate"。Child row 上的 equity_investment_amount 会被拒绝。✅

### Can `stock_investment_amount` close on an aggregate or standalone row?

Rule `required_row_hierarchy_role="child"` 要求 child 角色。Enrichment 只为明确的 stock child rows 设置 role="child"。Aggregate/standalone/unknown 行会被拒绝。✅

### Can benchmark close on investment-objective text?

Plan 规定 "If the value text merely mentions 业绩比较基准 inside an investment-objective sentence, return investment_objective or unknown"（line 319）。Derivation rules 中 rule 2 在 rule 3 之前，investment-objective label 先于 benchmark label 检测。✅

### Can benchmark close outside §2?

Plan 规定 `section_id != "§2"` → unknown（line 313）。Rule 也要求 `expected_section_id="§2"`（line 349）。双重防护。Test 14 验证。✅

### Can top-level asset rows between parent and child cause false child assignment?

Plan 规定 `_is_explicit_top_level_asset_row` 会关闭 parent scope（line 250–251, 235–252）。Test 9 验证。✅

---

## Test Coverage Gap Analysis

| Scenario | Positive Test | Negative Test |
|---|---|---|
| Equity aggregate row closure | Test 1 | Test 6 (no child → residual) |
| Stock child row closure | Test 2 | Test 4 (no parent), Test 5 (no `其中`) |
| Identical values both close | Test 3 | — |
| Neighbor labels don't prove | — | Test 7 |
| Detail table rejection | — | Test 8 |
| Top-level asset resets scope | — | Test 9 |
| Benchmark via context_label | Test 10 | — |
| Benchmark via raw_text prefix | Test 11 | — |
| Investment-objective mentions benchmark | — | Test 12 |
| Ambiguous labels | — | Test 13 |
| Non-§2 benchmark | — | Test 14 |
| Benchmark via heading_path | **MISSING** | — |
| Regression: F015/F020/S4-F015 | Test 15 | — |
| Regression: invalid literals | Test 16 | — |
| v2 non-overwrite | Test 17 | — |

唯一缺失：heading_path 作为 benchmark label 来源的正面测试（见 F-DS-P4）。

---

## Boundary Check

| Requirement | Status |
|---|---|
| `NOT_READY` preserved | ✅ Plan verdict: `HANDOFF_READY_NOT_READY` |
| `source_truth_status=not_proven` | ✅ Stated explicitly (line 29, 53, 594) |
| `candidate_only=true` | ✅ Stated (line 52) |
| No source truth acceptance | ✅ Non-goals (line 38–47) |
| No baseline promotion | ✅ Non-goals (line 41) |
| No parser replacement | ✅ Non-goals (line 42) |
| No full field correctness | ✅ Non-goals (line 43) |
| No release/PR readiness | ✅ Non-goals (line 44–45) |
| Pure helper boundary | ✅ Line 58: no file reads, no repository calls |
| No live/network/provider/LLM | ✅ Line 55, line 574 |
| v1-only enrichment guard preserved | ✅ Line 71–73, Step 4 |
| No v2 overwrite | ✅ Step 4, Test 17 |
| No FIELD_RULES change unless justified | ✅ Step 5, lines 446–453 |
| No Service/UI/Host/renderer/quality-gate | ✅ Line 56 |
| No direct PDF/cache/source-helper | ✅ Line 54 |
| Affected files scoped correctly | ✅ 3 files (helper, tests, evidence) |
| No README/control-doc change | ✅ Line 84 |

---

## Validation

```text
git diff --check -- docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md
```

Result: exit 0, no output.

---

## Residual Risks

1. **`_row_primary_label` ambiguity** (F-DS-P1): 如果实现选择与 plan 意图不同的标签解析方式，hierarchy 推导结果可能偏离预期。
2. **`context_label` vs `heading_path` 优先级** (F-DS-P2): 如果不明确规定，可能导致 S6-F041 在投资目标语境下被误闭合。
3. **Benchmark 前缀检测实现** (F-DS-P3): normalization 管线可能影响边缘情况的匹配。
4. **Real document hierarchy complexity**: Plan 基于 label pattern matching，如果实际年报中存在非标准行标签结构（如 `权益投资合计`、`其中:股票投资`），可能需要调整 pattern。
5. **S6-F041 可能仍保持 residual**: 如果 repository reference projection 未提供独立的 benchmark 标签 span，这是可接受的（plan 明确声明不要求 4/4 闭合，line 562）。
6. **Partial evidence**: 即使 4 行全部闭合，仍然只是 candidate-only helper 证据。Source truth 接受率、baseline promotion 需要独立 gate。

## Self-Check

pass — plan review 在 AgentDS 范围内完成。6 项 Code Facts 验证通过，6 项 findings（2 Medium + 4 Low）均有具体行号引用和反例。False-positive 风险分析覆盖 6 种可能的误闭合路径。测试缺口分析识别出 1 项缺失测试。Plan 整体结构良好，非 goal 边界清晰，call order 和 keying convention 具体可操作。

Verdict: `PASS_WITH_FINDINGS`。Blocking findings: 0。2 Medium findings 建议在 controller judgment 接受前澄清。
