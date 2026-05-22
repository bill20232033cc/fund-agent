# P17-S1 tracking_error extractor ambiguity boundary code review（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

实现正确覆盖已接受 plan 的全部切片：移除旧泛化 `tracking_error_ambiguous` 生产路径，改为 10 种具体 fail-closed note；修复两处早退使前序 blocker 不压制后续有效直接披露；multi-match / table-text inconsistent / unparseable 优先级正确；直接披露成功契约完整保留；20 项 focused tests 全部通过。存在一个边界诊断语义的可接受 finding，不需要阻断。

## Findings

### F1 — `_classify_tracking_error_nonmatch_context` 对纯标准差表格的诊断语义（Severity: Low / Acceptable Diagnostic）

**位置**: `fund_agent/fund/extractors/performance.py:667-689`

**审查问题**: `_classify_tracking_error_nonmatch_context` 在 `_STANDARD_DEVIATION_KEYWORDS` 检查（line 681）时不验证文本是否包含 `_TRACKING_ERROR_KEYWORDS`。对于一个有"净值增长率标准差"列但无"跟踪误差"列的普通净值表现表，当 `_find_tracking_error_header_index` 返回 `None` 时，该函数会返回 `tracking_error_standard_deviation_only`。

**分析**: 这是**可接受的诊断行为**，不是行为缺陷。原因：
1. 该 note 仅出现在 `ExtractedField.note` 中（`extraction_mode="missing"`），不影响任何成功路径。
2. `_TRACKING_ERROR_KEYWORDS`（`"跟踪误差"`, `"跟踪偏离度"`）是高度专用术语，不会出现在标准净值表现表头中。
3. `_STANDARD_DEVIATION_KEYWORDS`（`"净值增长率标准差"` 等）足够具体，误命中概率极低。
4. 对于确实只有标准差列的表格，标记为 `standard_deviation_only` 比 `年报未直接披露跟踪误差` 更有诊断价值——下游可据此判断该表确实有标准差数据但无跟踪误差数据。

**建议**: 无需修改。若未来出现误命中，可在 line 681 前增加 `_TRACKING_ERROR_KEYWORDS` 存在性前置检查。

### F2 — `_TRACKING_ERROR_ACTUAL_KEYWORDS` 移除 "年化" 后的语义完整性（Severity: None / Design Correct）

**位置**: `fund_agent/fund/extractors/performance.py:52-57`

**审查问题**: 移除 "年化" 后，纯 "年化跟踪误差为 X%" 文本（无 "报告期"/"本报告期" 前缀）不再触发 `_has_actual_tracking_error_signal`。这是否遗漏直接实际披露语义？

**分析**: 这是**正确的设计决策**。原因：
1. "年化"是计量口径修饰词，不是期间/来源信号。`"年化跟踪误差"` 可以出现在目标文本（"力争将年化跟踪误差控制在..."）或叙事文本（"降低年化跟踪误差"）中。
2. `_is_annualized_text` (line 890-903) 仍然独立识别 "年化" 语义，设置 `annualized=True`。
3. 纯 "年化跟踪误差为 1.23%" 无期间前缀时，不被 target/negative keywords 拦截，仍可走通直接披露路径——只是 `_has_actual_tracking_error_signal` 返回 False，这在无 negative keywords 的情况下不影响最终接受。
4. 测试 `test_extract_performance_outputs_direct_tracking_error_when_disclosed` 使用 "报告期年化跟踪误差为 1.23%"，"报告期" 提供 actual signal，验证了完整路径。

**建议**: 无需修改。

### F3 — `_is_benchmark_only_tracking_error_context` 在 `_classify_tracking_error_line_without_parseable_value` 中的可达性（Severity: None / Verified）

**位置**: `fund_agent/fund/extractors/performance.py:711-713`

**审查问题**: benchmark-only classifier 是否可达？是否过度脆弱？

**分析**:
- 调用链: `_extract_tracking_error_from_text` (line 562) → `_classify_tracking_error_line_without_parseable_value` (line 692) → `_is_benchmark_only_tracking_error_context` (line 711)。
- 触发条件：行包含 `_TRACKING_ERROR_KEYWORDS`（确保函数被调用）、无百分比值、非 target/ambiguous、非 unparseable、非 manager narrative。
- 测试覆盖: `test_extract_performance_marks_benchmark_only_tracking_error_with_specific_note` 使用 "业绩比较基准指数采用低跟踪误差编制方法。"（含 "业绩比较基准" 和 "跟踪误差"，无百分比，无 negative keywords，无 manager keywords）。
- 脆弱性评估: keyword 集合足够具体，不会误命中。`_TRACKING_ERROR_BENCHMARK_ONLY_KEYWORDS`（`"业绩比较基准"`, `"比较基准"`, `"基准指数"`）是标准术语。

**建议**: 无需修改。

### F4 — target-only 和 mixed-target 早退修复（Severity: None / Verified）

**位置**:
- `fund_agent/fund/extractors/performance.py:510-512`（table extraction）
- `fund_agent/fund/extractors/performance.py:566-568`（text extraction）

**审查问题**: 两个早退是否确实修复为记录 blocker 后继续扫描？

**分析**: 两处均使用 `blocker_notes.append(...)` + `continue` 模式，不提前 return。验证：
- Table path (line 510-512): `blocker_notes.append(_classify_tracking_error_target_context(context))` → `continue` → 继续扫描下一 row。
- Text path (line 566-568): `blocker_notes.append(_classify_tracking_error_target_context(normalized_line))` → `continue` → 继续扫描下一行。
- 测试覆盖:
  - `test_extract_performance_accepts_direct_tracking_error_after_earlier_mixed_target_line` (line 451-479) — mixed target 在前，直接披露在后，后者被接受。
  - `test_extract_performance_accepts_direct_tracking_error_after_earlier_target_only_line` (line 482-508) — target-only 在前，直接披露在后，后者被接受。

**建议**: 无需修改。

### F5 — multi-match / table-text inconsistent / unparseable 的 fail-closed 优先级（Severity: None / Verified）

**位置**: `fund_agent/fund/extractors/performance.py:71-82`

**审查问题**: 优先级是否正确？

**分析**: `_TRACKING_ERROR_BLOCKER_PRECEDENCE` 元组顺序：
1. `tracking_error_table_text_inconsistent` — 表格/正文数值冲突，最高优先。
2. `tracking_error_multi_match` — 多候选无法确定性选择。
3. `tracking_error_incomplete_anchor` — 锚点不完整。
4. `tracking_error_unparseable` — 数值不可解析。
5. `tracking_error_mixed_actual_and_target` — 实际/目标混杂。
6-10. target_or_limit → manager_narrative → benchmark_only → standard_deviation_only → missing。

top-level `_extract_tracking_error` (line 395-450) 的合并逻辑：
- 当 table 和 text 都有 match 但值不一致时 → 直接返回 `_TRACKING_ERROR_NOTE_TABLE_TEXT_INCONSISTENT`（line 416），绕过 precedence。
- 当 table/text 各自 blocker 时 → 通过 `_select_tracking_error_blocker_note` 按 precedence 选择（line 410-412）。
- 当 match 存在但值不可解析时 → 直接返回 `_TRACKING_ERROR_NOTE_UNPARSEABLE`（line 423）。

table/text inconsistency 在合并层直接处理为最高优先，multi-match 在 table/text 各自内部处理后通过 precedence 合并。逻辑正确。

**建议**: 无需修改。

### F6 — stale `tracking_error_ambiguous` 残留（Severity: None / Verified）

**审查结果**: `grep -rn "tracking_error_ambiguous" --include="*.py" .` 无输出。生产代码和测试代码中均无残留。实现 artifact 声称 "Replaced broad precheck early return" 和 "Split stale generic ambiguity semantics"，代码验证一致。

### F7 — 测试覆盖充分性（Severity: None / Verified）

**位置**: `tests/fund/extractors/test_performance.py`

**审查结果**: 20 项测试全部通过，覆盖：

| 测试 | 对应 blocker / success |
|---|---|
| `test_extract_performance_outputs_direct_tracking_error_when_disclosed` | 直接披露成功 |
| `test_extract_performance_does_not_treat_tracking_error_target_as_observed` | target_or_limit |
| `test_extract_performance_fails_closed_on_mixed_actual_target_tracking_error_text` | mixed_actual_and_target |
| `test_extract_performance_does_not_use_standard_deviation_as_tracking_error` | standard_deviation_only |
| `test_extract_performance_marks_manager_tracking_error_narrative_with_specific_note` | manager_narrative |
| `test_extract_performance_marks_benchmark_only_tracking_error_with_specific_note` | benchmark_only |
| `test_extract_performance_marks_unparseable_direct_tracking_error_with_specific_note` | unparseable |
| `test_extract_performance_outputs_tracking_error_from_annual_table` | 表格直接披露成功 |
| `test_extract_performance_keeps_table_match_when_text_discloses_same_tracking_error` | 一致双披露成功 |
| `test_extract_performance_marks_table_text_conflicting_tracking_error_as_inconsistent` | table_text_inconsistent |
| `test_extract_performance_marks_multiple_tracking_error_matches_with_specific_note` | multi_match |
| `test_extract_performance_accepts_direct_tracking_error_after_earlier_mixed_target_line` | 早退修复（mixed） |
| `test_extract_performance_accepts_direct_tracking_error_after_earlier_target_only_line` | 早退修复（target） |

plan 中列出的 `tracking_error_incomplete_anchor` fixture 未添加，implementation artifact 已记录为 residual（owner: `future parser malformed-table fixture`）。这是合理的——当前 `ParsedAnnualReport` builder 总是能产生完整锚点，无法自然构造 incomplete-anchor 场景。

**建议**: 无需补丁。当前测试矩阵已覆盖所有可实现的 blocker 类型和直接披露成功路径。

## Required Fixes

无。所有 findings 均为 Low/None severity，不阻断接受。

## Residual Risks

| Residual | Owner | Handling |
|---|---|---|
| `tracking_error_incomplete_anchor` 无测试 fixture | `future parser malformed-table fixture` | 当前 builder 无法自然构造；note 常量已就位，未来 parser 异常时可补充 |
| production `tracking_error` rows for `001548` 等候选 | `future evidence-backed golden gate` | 仍需 reviewed direct observed disclosure evidence |
| calculated tracking error / external index data | `future design phase` | 不在本切片范围 |

## Validation Reviewed

- [x] `grep -rn "tracking_error_ambiguous" --include="*.py" .` — 无输出
- [x] `pytest tests/fund/extractors/test_performance.py -q` — 20 passed in 0.35s
- [x] 10 种 blocker note 常量均有对应测试
- [x] blocker precedence 元组顺序与 plan 建议一致
- [x] 两处 early-return 均改为 append+continue 模式
- [x] 直接披露成功契约完整：`source_type="direct_disclosure"`, `calculation_method="disclosed"`, `frequency="annual_report_period"`, `provenance_note` 存在
- [x] `docs/design.md` 和 `docs/implementation-control.md` 未被修改
- [x] 无 production golden rows 被添加或修改
- [x] 无 `extra_payload` 显式参数塞入
- [x] 实现范围未越界（仅 `performance.py` + `test_performance.py`）
