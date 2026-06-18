# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Plan Re-review (AgentDS) — 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Plan Fix`
Role: AgentDS plan re-review worker only
Verdict: `PASS`
Release/readiness: `NOT_READY`

## Reviewed Fix

Fix evidence: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-fix-evidence-20260617.md`
Updated plan: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md`
Prior review: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-review-ds-20260617.md`

## Prior Finding Disposition

| Finding | Severity | Status | Fix Verification |
|---|---|---|---|
| F-DS-P1: `_row_primary_label` 未定义 | Medium | **FIXED** | Plan L182–186: 返回 `row_label_path` 最后一个非空元素；L184: 禁止使用 full path 或 `row_label_path[0]`；L415–431: 精确实现代码（`reversed()` 遍历 + `.strip()` + 首个非空返回） |
| F-DS-P2: context_label/heading_path 优先级未定义 | Medium | **FIXED** | Plan L324: 优先级链 `context_label > heading_path > raw_text`；L325: 投资目标 context_label 阻止 heading_path/raw_text 覆盖；L330: 跨层冲突 → `"unknown"`（context_label 为投资目标时例外→投资目标）；L602: Test 16 覆盖跨层冲突 |
| F-DS-P3: benchmark 前缀检测未精确指定 | Low | **FIXED** | Plan L352–367: delimiter-aware 检测，中文/ASCII 冒号、全角/半角 pipe、whitespace 均作分隔符；L353: leading whitespace 先 strip；L358–367: 精确正例与反例 |
| F-DS-P4: 缺少 heading_path benchmark 正面测试 | Low | **FIXED** | Plan L573–579: Test 12 — `context_label` 为通用标签，`heading_path=("基金概况", "业绩比较基准")`，预期闭合 |
| F-DS-P5: 引用不存在的 `_enrich_share_period_contexts()` | Low | **FIXED** | Plan L466–476: 重写 Step 3 代码示例，不再引用该函数；L478: 明确说明不引入该函数，除非实现 worker 主动选择局部重构 |
| F-DS-P6: `row_index` gaps 未显式确认 | Low | **FIXED** | Plan L276–277: "Integer `row_index` gaps are comparable. A table with row indexes such as `0, 2, 5` may still use nearest-preceding-parent logic"；L271: fail-closed 条件仅包括 non-integer、duplicated、missing，不含 gaps |

## Fix Quality Assessment

### F-DS-P1 Fix Detail

`_row_primary_label` 现在有精确的实现代码（L418–424）：

```python
def _row_primary_label(cell: RepositoryReferenceCell) -> str:
    for label in reversed(cell.row_label_path):
        stripped = label.strip()
        if stripped:
            return stripped
    return ""
```

设计决策和理由明确（L185–186）：最后一个元素是最接近 value cell 的标签。例如 `("资产", "权益投资")` → `"权益投资"`。所有 predicate 均消费此 primary label（L428–430）。

✅ 实现 worker 可直接复制此代码，无歧义。

### F-DS-P2 Fix Detail

优先级链和冲突解决方案完整：

| 场景 | context_label | heading_path | raw_text | 结果 |
|---|---|---|---|---|
| 局部投资目标标签 | `投资目标` | 任意 | 任意 | `investment_objective`（L325） |
| 局部 benchmark 标签，无冲突 | `业绩比较基准` | 不含投资目标 | — | `benchmark`（L326） |
| context 为通用标签 | `基金概况` | `业绩比较基准` | — | `benchmark`（L328） |
| 跨层冲突（ctx=bench, head=obj） | `业绩比较基准` | `投资目标` | — | `benchmark`（L326 先触发） |
| 跨层冲突（ctx=obj, head=bench） | `投资目标` | `业绩比较基准` | — | `investment_objective`（L325 先触发，Test 16） |
| 跨层冲突（ctx 通用, head 冲突） | `基金概况` | 含两者 | — | `unknown`（隐式 fail-closed） |
| 全部通用，raw prefix benchmark | — | — | `业绩比较基准｜...` | `benchmark`（L332） |
| 提及 benchmark 在投资目标句中 | `投资目标` | — | `紧密跟踪业绩比较基准` | `investment_objective`（L335） |

设计合理：`context_label` 作为最局部标签优先，投资目标语境不可被下游 benchmark mention 覆盖。✅

### F-DS-P3 Fix Detail

分隔符处理（L352–367）覆盖了中文/ASCII 冒号、全角/半角 pipe、whitespace。检测逻辑分两步：先 strip leading whitespace，再匹配 label + delimiter 或 end-of-string。正例和反例明确。✅

### F-DS-P4 Fix Detail

Test 12（L573–579）补充了 heading_path 作为 benchmark label 来源的正面测试，覆盖了原缺失的测试路径。✅

### F-DS-P5 Fix Detail

Step 3 代码示例不再引用不存在的函数。L478 明确赋予实现 worker 选择权（保持内联或局部重构），并约束重构不得改变行为。✅

### F-DS-P6 Fix Detail

L276–277 一句澄清消除了 `row_index` gaps 的歧义。✅

## New Tests Summary

Fix 增加了 2 个新测试：

| Test # | 名称 | 覆盖的 finding |
|---|---|---|
| 12 | `test_raw_legacy_text_span_with_benchmark_heading_path_closes_benchmark_when_context_generic` | F-DS-P4 |
| 16 | `test_raw_legacy_context_objective_heading_benchmark_conflict_remains_residual` | F-DS-P2 |

总计：19 个测试（9 hierarchy + 7 benchmark + 3 regression）。✅

## New Finding

### F-DS-R1 (Info) — heading_path 内部同时包含 benchmark 和 investment-objective 标签时的行为未显式覆盖

**Plan reference**: Derivation rules L328–329

**Issue**: L328 说 heading_path 含 benchmark 且不含 investment-objective → benchmark。L329 说含 investment-objective 且不含 benchmark → investment_objective。但两者同时出现时（如 `heading_path=("基金概况", "投资目标", "业绩比较基准")`），两条规则均不触发，走到 raw_text prefix 检测或最终 fallback。

**分析**: 这是极边缘情况。当前设计下会 fallthrough 到 raw_text 或最终返回 `unknown`（fail-closed）。不影响 S6-F041 的正确性，因为 S6-F041 的真实 heading 不会同时包含两个冲突标签。

**建议**: 可在实现时加一条明确规则：heading_path 内部冲突 → `"unknown"`。或在 plan 中注明此为 fail-closed 的隐式行为。

**Severity**: Info — 极边缘情况，不影响 plan 的代码生成能力。当前 fail-closed 行为可接受。

## Boundary Verification

| Requirement | Status |
|---|---|
| `NOT_READY` preserved | ✅ Plan + fix evidence both state `NOT_READY` |
| `source_truth_status=not_proven` | ✅ L29, L53, L594, L652 |
| No source truth acceptance | ✅ Non-goals L40, L654 |
| No baseline promotion | ✅ Non-goals L41, L654 |
| No parser replacement | ✅ Non-goals L42, L655 |
| No full field correctness | ✅ Non-goals L43, L656 |
| No release/PR readiness | ✅ Non-goals L44–45 |
| Pure helper boundary | ✅ L58 |
| v1-only enrichment preserved | ✅ L71–73, Step 4 |
| No v2 overwrite | ✅ Step 4, Test 19 (regression) |
| No FIELD_RULES change | ✅ Step 5 |
| No Service/UI/Host/renderer/quality-gate | ✅ L56 |
| No direct PDF/cache/source-helper | ✅ L54 |
| Affected files scoped correctly | ✅ L80–82 (3 files) |
| No live/network/provider/LLM | ✅ L55, L635 |
| No code/test change in fix | ✅ Fix evidence L18, L40 |
| git diff-check clean | ✅ exit 0, no output |

## Validation

```text
git diff --check -- docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-fix-evidence-20260617.md
```

Result: exit 0, no output.

Fix keywords grep: all 6 finding keywords confirmed present in updated plan (6/6).

## Residual Risks

1. `heading_path` 内部 label 冲突未显式覆盖（F-DS-R1）。当前 fallthrough → fail-closed，可接受。
2. `raw_text` 前缀检测依赖 delimiter-aware normalization，需要实现 worker 正确实现分隔符处理。
3. 所有 plan 质量依赖于实现 worker 按 spec 实现。hierarchy 推导的 label pattern matching 可能在非标准年报格式中遗漏部分有效行。

## Self-Check

pass — re-review 在 AgentDS 范围内完成。6 项 prior findings 全部验证为 FIXED，每项均有 plan 具体行号引用确认。1 项新 Info finding（F-DS-R1）不阻塞实施。Plan 在修复后 code-generation-ready：`_row_primary_label` 有精确实现代码，benchmark 语义推导有完整决策表，call order 和 keying convention 明确。所有 NOT_READY / candidate-only / no-live 边界保持。

Verdict: `PASS`。Blocking findings: 0。
