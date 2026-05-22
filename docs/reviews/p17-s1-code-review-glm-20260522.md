# P17-S1 tracking_error extractor ambiguity boundary code review（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

实现完成 P17-S1 计划全部五个切片，旧泛化 `tracking_error_ambiguous` 生产路径已彻底移除，所有 fail-closed 场景改为具体 blocker note；两个早退位置已修复，前序目标/混杂文本不再压制后续有效直接披露；直接披露成功契约完整保留。20 个 focused tests 全部通过，ruff 和 git diff --check 无告警。存在 4 项 LOW 级发现和 2 项 INFO 级观察，均不阻塞合入，但应记录在案。

## Findings

### F1 [LOW] `_classify_tracking_error_nonmatch_context` 对无 tracking_error keyword 的标准差行返回 `tracking_error_standard_deviation_only`

- **文件**：`fund_agent/fund/extractors/performance.py:681-682`
- **现象**：函数先检查 `_STANDARD_DEVIATION_KEYWORDS`（第 681 行），后检查 `_TRACKING_ERROR_KEYWORDS`（第 683 行）。一个不含"跟踪误差"/"跟踪偏离度"、仅含"净值增长率标准差"的普通 §3 行，也会返回 `tracking_error_standard_deviation_only`。
- **影响**：典型指数基金年报中，§3 标准净值表现表含标准差列但无跟踪误差披露时，最终 missing note 为 `tracking_error_standard_deviation_only` 而非通用 `年报未直接披露跟踪误差`。该 note 暗示报告"涉及"跟踪误差但只有标准差，而实际情形可能是报告根本不披露跟踪误差。
- **判断**：行为可接受——这是一个更具体的诊断信号，帮助下游理解为何不提取跟踪误差。标准差列确实是跟踪误差最常见的混淆源，明确标记有诊断价值。但 `_classify_tracking_error_nonmatch_context` 的调用点包括每张不匹配的表格和每行不提及跟踪误差的正文行，可能导致标准差 blocker note 在完全不相关的上下文中被记录。
- **建议**：不改，记录为 residual。若后续出现 note 语义混乱，可在 `_STANDARD_DEVIATION_KEYWORDS` 检查前增加 `_TRACKING_ERROR_KEYWORDS` 前置守卫，使不含跟踪误差关键词的标准差行直接返回 `None`。

### F2 [LOW] "年化"移除后对无其他 actual keyword 的混杂行分类精度略降

- **文件**：`fund_agent/fund/extractors/performance.py:52-57`
- **现象**：`_TRACKING_ERROR_ACTUAL_KEYWORDS` 不含"年化"。一条同时含实际值和目标限制的行如"年化跟踪误差为 0.53%，力争控制在 2% 以内"，若无"实际"/"报告期"/"本报告期"/"过去一年"中的任何一个，将返回 `tracking_error_target_or_limit` 而非 `tracking_error_mixed_actual_and_target`。
- **影响**：note 精度降低——该行实际包含观察值和目标值，但被标记为纯目标。然而 fail-closed 行为不变：该行同样被跳过，不会被误采信。
- **判断**：移除"年化"语义更正确——"年化"是时间维度修饰词，不是"实际观察"信号。"力争将年化跟踪误差控制在 4% 以内"中的"年化"确实不表示实际披露。精度降低仅影响 note 文本，不影响抽取决策。
- **建议**：不改，记录为 residual。

### F3 [LOW] `_classify_tracking_error_nonmatch_context` 缺少 benchmark-only 检查

- **文件**：`fund_agent/fund/extractors/performance.py:667-689`
- **现象**：`_classify_tracking_error_nonmatch_context` 依次检查标准差、tracking_error 关键词、目标/限制、经理叙事，但不检查 benchmark-only 上下文。而 `_classify_tracking_error_line_without_parseable_value`（第 692-713 行）包含 `_is_benchmark_only_tracking_error_context` 检查。
- **影响**：一张含"跟踪误差"+"业绩比较基准"文本但无 tracking error 列头的表格，在 `_classify_tracking_error_nonmatch_context` 中不会返回 `tracking_error_benchmark_only`，而是返回 `None`。benchmark-only 诊断在此路径上丢失。
- **判断**：现实中极少出现——典型净值表现表不含"跟踪误差"关键词（只有标准差列），该场景需要一张非常规的基准+跟踪误差混合文本但无专用列头的表格。fail-closed 行为不受影响（最终 fallback 到通用 missing note）。
- **建议**：不改，记录为 residual。若后续出现 benchmark-only 诊断缺口，可在 `_classify_tracking_error_nonmatch_context` 的 manager narrative 检查后增加 `_is_benchmark_only_tracking_error_context` 检查，与 `_classify_tracking_error_line_without_parseable_value` 对齐。

### F4 [LOW] 测试未覆盖 table-level multi-match 和 §2 fallback

- **文件**：`tests/fund/extractors/test_performance.py`
- **现象**：
  - `test_extract_performance_marks_multiple_tracking_error_matches_with_specific_note`（第 429-448 行）仅测试正文多候选 multi-match。未测试表格多候选（多张表均有 tracking error 列、或一张表多行均有 tracking error 且值不同）。
  - 未测试 §2 兜底正文提取路径（`_extract_tracking_error_from_text` 第 550 行 `for section_id in ("§3", "§2")` 的 §2 分支）。
  - 未测试表格内 mixed-actual-target 上下文的 `_classify_tracking_error_target_context` 调用（第 511 行）。
- **判断**：正文 multi-match 测试已验证 `tracking_error_multi_match` 常量和早退逻辑。§2 fallback 是同一逻辑的二次迭代，风险有限。table-level multi-match 的生产代码路径（第 525-526 行 `if len(matches) > 1`）与 text-level（第 582-583 行）结构一致。未覆盖不构成功能风险，但测试矩阵留有间隙。
- **建议**：不阻塞合入。记录为 residual，后续可补充 table multi-match 和 §2 fallback 的 focused test。

### F5 [INFO] 残留孤立 fixture 文件

- **文件**：`tests/fixtures/fund/extractors/performance/performance_with_tracking_error_ambiguous.txt`
- **现象**：该文件名含 `tracking_error_ambiguous`，但无任何测试引用它。`performance_with_tracking_error.txt`（实际被 `test_extract_performance_outputs_direct_tracking_error_when_disclosed` 使用）内容为干净直接披露 `报告期年化跟踪误差：1.23%`，不含目标/混杂语言。
- **判断**：孤立 fixture 不影响生产或测试行为。历史引用文件保留是可接受的，清理也不违反任何约束。
- **建议**：可选清理。

### F6 [INFO] `_tracking_error_context_is_target_or_ambiguous` 函数名含 "ambiguous" 但语义已收窄

- **文件**：`fund_agent/fund/extractors/performance.py:793-807`
- **现象**：函数名保留 "ambiguous" 字样，但实现只检查 `_TRACKING_ERROR_NEGATIVE_KEYWORDS`（目标/限制/控制关键词）。该函数不再与旧的 `tracking_error_ambiguous` note 关联。
- **判断**：函数名语义略有偏移——检查的是"目标/限制上下文"而非"歧义"。重命名为 `_tracking_error_context_is_target_or_control` 更准确，但属于 cosmetic 改动，不影响行为。
- **建议**：可选 cosmetic rename。

## Required Fixes

无阻塞性 required fix。

全部发现的 fail-closed 行为、直接披露契约、blocker note 优先级均正确实现。4 项 LOW 发现是设计取舍层面的精度问题，不影响安全性或正确性。

## Residual Risks

| Residual | Severity | Owner | Handling |
|---|---|---|---|
| 标准差行在无 TE keyword 时返回 `tracking_error_standard_deviation_only` | LOW | future note precision pass | 若 note 语义混乱，增加 TE keyword 前置守卫 |
| "年化"移除导致混杂行 note 降级为 target-only | LOW | future note precision pass | 不影响 fail-closed 行为 |
| `_classify_tracking_error_nonmatch_context` 缺 benchmark-only 检查 | LOW | future classifier alignment | 对齐两个 classifier 函数的检查项 |
| table-level multi-match / §2 fallback 无 focused test | LOW | next test pass | 补充表格多候选和 §2 兜底路径测试 |
| `tracking_error_incomplete_anchor` fixture | — | future parser malformed-table fixture | 按 plan 记录为 residual，当前 builder 自然生成完整 anchor |
| production `tracking_error` golden rows | — | future evidence-backed golden gate | 001548 及 P16 enhanced-index 候选仍 blocked |
| calculated tracking error / external index data | — | future design phase | Out of scope |
| 孤立 fixture `performance_with_tracking_error_ambiguous.txt` | INFO | optional cleanup | 无测试引用 |

## Validation Reviewed

```
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q
# 20 passed in 0.52s  ← 本地复现确认

.venv/bin/python -m pytest tests/fund/extractors -q
# 60 passed  ← implementation artifact 声明

.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
# 55 passed  ← implementation artifact 声明

.venv/bin/python -m ruff check fund_agent tests
# All checks passed!  ← implementation artifact 声明

git diff --check HEAD
# no output  ← implementation artifact 声明
```

本地复现 `test_performance.py` 20 passed，与 implementation artifact 一致。其余 validation command 信任 implementation artifact 记录。

## Plan Compliance

| Plan Slice | Status | Notes |
|---|---|---|
| Slice 1: explicit blocker semantics | DONE | 10 个 note 常量 + `_TrackingErrorExtractionOutcome` + `_TRACKING_ERROR_BLOCKER_PRECEDENCE` |
| Slice 2: remove broad early-return suppression | DONE | 两个早退位置改为记录 blocker + continue；`test_*_after_earlier_*` 两条测试验证 |
| Slice 3: multi-match explicit | DONE | 正文和表格 multi-match 均返回 `tracking_error_multi_match` |
| Slice 4: preserve success contract | DONE | `source_type="direct_disclosure"` / `calculation_method="disclosed"` / `frequency="annual_report_period"` / provenance_note / anchor 全部保留 |
| Slice 5: focused tests | DONE | 11 条 blocker note 测试 + 2 条早退修复测试 + 3 条直接披露成功契约测试；`incomplete_anchor` 按 plan 记录为 residual |

Design-Boundary Checklist：

- §1.3 non-goals 未违反 ✓
- UI/Service/Capability/Runtime/Engine 边界未突破 ✓
- 年报访问仅通过 ParsedAnnualReport 输入 ✓
- 无外部 Dayu/LLM/Evidence Confirm 依赖 ✓
- 无 production golden rows 变更 ✓
- 无 extra_payload 显式参数隐藏 ✓
- 成功信号可由 deterministic tests 验证 ✓
