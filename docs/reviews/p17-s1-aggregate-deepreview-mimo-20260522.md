# P17-S1 Aggregate DeepReview（2026-05-22）

## Verdict

`PASS`

P17-S1 实现完整满足已接受 plan 的全部 success signals，未越过 design v2.1 非目标边界，reviewer findings 均被 controller 合理裁决，residual owner 清楚，tests/README 与代码事实一致，不存在 blocking correctness/stability/maintainability finding。所有验证命令通过。

## Reviewed Artifacts

| Artifact | Role |
|---|---|
| `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-plan-20260522.md` | Accepted plan baseline |
| `docs/reviews/p17-s1-plan-review-controller-judgment-20260522.md` | Plan review controller judgment |
| `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-implementation-20260522.md` | Implementation artifact |
| `docs/reviews/p17-s1-code-review-mimo-20260522.md` | MiMo code review |
| `docs/reviews/p17-s1-code-review-glm-20260522.md` | GLM code review |
| `docs/reviews/p17-s1-code-review-controller-judgment-20260522.md` | Code review controller judgment |
| `docs/implementation-control.md` | Control truth |
| `docs/design.md` v2.1 | Design truth |
| `fund_agent/fund/extractors/performance.py` | Production implementation |
| `tests/fund/extractors/test_performance.py` | Focused tests |
| `tests/README.md` | Test documentation |

## Scope Verification

Commits `8cba095..HEAD`（2 commits: `d069862`, `40e8175`）touch exactly 8 files:

- `fund_agent/fund/extractors/performance.py` — production extractor
- `tests/fund/extractors/test_performance.py` — focused tests
- `tests/README.md` — test documentation
- `docs/implementation-control.md` — control bookkeeping
- 5 review artifacts under `docs/reviews/`

No out-of-scope files touched: no production golden, no CSV/RR-13, no design.md, no Service/UI/Runtime/Engine/source/PDF/cache helper.

## 1. Plan Success Signal Verification

| Success Signal | Status | Evidence |
|---|---|---|
| 去除 stale `tracking_error_ambiguous` | ✅ | `grep -rn "tracking_error_ambiguous" --include="*.py" .` 无输出；旧 `_has_ambiguous_tracking_error_text` 调用已移除；旧测试 `test_extract_performance_fails_closed_on_ambiguous_tracking_error_text` 重写为 `test_extract_performance_fails_closed_on_mixed_actual_target_tracking_error_text` |
| 具体 fail-closed note（10 种） | ✅ | `_TRACKING_ERROR_NOTE_*` 常量 10 个全部定义（`performance.py:61-70`），`_TRACKING_ERROR_BLOCKER_PRECEDENCE` 元组包含全部 10 种（`performance.py:71-82`），每种均有至少一个 focused test |
| target/mixed 不早退 | ✅ | table path `performance.py:510-512` 使用 `blocker_notes.append(...)` + `continue`；text path `performance.py:566-568` 使用相同模式；两条早退修复测试验证后续直接披露被接受 |
| 多候选显式 blocker | ✅ | table `performance.py:525-526` 和 text `performance.py:582-583` 均返回 `_TRACKING_ERROR_NOTE_MULTI_MATCH`；table-level multi-match test 和 text multi-match test 覆盖 |
| table/text inconsistency | ✅ | `performance.py:416` 直接返回 `_TRACKING_ERROR_NOTE_TABLE_TEXT_INCONSISTENT`；`test_extract_performance_marks_table_text_conflicting_tracking_error_as_inconsistent` 覆盖 |
| §2 fallback | ✅ | text extraction `performance.py:550` 迭代 `("§3", "§2")`；`test_extract_performance_falls_back_to_section_two_tracking_error_when_section_three_missing` 覆盖 |
| 直接披露契约保持 | ✅ | 成功路径 `performance.py:425-450` 保留 `source_type="direct_disclosure"`、`calculation_method="disclosed"`、`frequency="annual_report_period"`、`provenance_note`、`row_locator="tracking_error"`；`test_extract_performance_outputs_direct_tracking_error_when_disclosed` 验证全部字段 |

## 2. Design v2.1 Non-Goal Boundary Check

| Non-Goal | Status | Evidence |
|---|---|---|
| 无 calculated tracking error | ✅ | 无计算逻辑引入；仅做直接披露抽取 |
| 无外部 index series | ✅ | 无外部数据源适配器 |
| 无 Dayu/LLM/Evidence Confirm | ✅ | 无 Dayu runtime、LLM 调用或 Evidence Confirm 依赖 |
| 无 production golden rows | ✅ | `reports/golden-answers/` 未修改 |
| 无 Service/UI/Runtime/Engine/source/PDF/cache 改动 | ✅ | 仅 `performance.py` + `test_performance.py` |
| 年报访问通过 FundDocumentRepository | ✅ | extractor 接收 `ParsedAnnualReport` 输入，不直接访问 PDF/cache |
| 无 extra_payload 显式参数隐藏 | ✅ | 无 `extra_payload` 引入 |
| §11 design-boundary checklist 通过 | ✅ | plan review controller judgment 已确认 |

## 3. Reviewer Finding 裁决审查

| Finding | Source | Controller Decision | Residual Owner | 合理性 |
|---|---|---|---|---|
| 标准差行无 TE keyword 时返回 `standard_deviation_only` | MiMo F1 / GLM F1 | Accepted as residual | future note precision pass | ✅ 合理：仅 missing-path 诊断，不影响成功路径；标准差是 TE 最常见混淆源 |
| "年化"移除导致混杂行 note 降级 | MiMo F2 / GLM F2 | Accepted as residual | future note precision pass | ✅ 合理："年化"是计量口径修饰词非实际信号；fail-closed 行为不变 |
| `_classify_tracking_error_nonmatch_context` 缺 benchmark-only 检查 | MiMo F3 / GLM F3 | Accepted as residual | future classifier alignment | ✅ 合理：benchmark-only text path 已覆盖；table-context 对齐可后续补充 |
| table-level multi-match / §2 fallback 缺测试 | GLM F4 | Accepted and fixed | 已关闭 | ✅ 合理：controller 要求并验证了 focused tests |
| 孤立 fixture `performance_with_tracking_error_ambiguous.txt` | GLM F5 | Deferred optional cleanup | optional | ✅ 合理：不影响行为 |
| `_tracking_error_context_is_target_or_ambiguous` 函数名含 "ambiguous" | GLM F6 | Deferred optional cleanup | optional | ✅ 合理：cosmetic rename，不影响行为 |
| `tracking_error_incomplete_anchor` 无测试 fixture | MiMo F4 | Accepted as residual | future parser malformed-table fixture | ✅ 合理：当前 builder 无法自然构造 incomplete-anchor |

## 4. tests/README 与代码一致性

`tests/README.md` 第 15 行描述 test_performance.py 覆盖范围：

> 跟踪误差直接披露、目标/限制、mixed actual/target、manager narrative、benchmark-only、standard-deviation-only、unparseable、table/text inconsistency、多候选、表格多候选、`§2` fallback 和早期 blocker 后继续扫描

实际测试文件包含 22 个测试（含非 tracking-error 的 nav/benchmark/investor tests），tracking-error 相关测试 16 个：

| 测试名 | README 覆盖 |
|---|---|
| `test_extract_performance_outputs_direct_tracking_error_when_disclosed` | 直接披露 ✅ |
| `test_extract_performance_does_not_treat_tracking_error_target_as_observed` | 目标/限制 ✅ |
| `test_extract_performance_fails_closed_on_mixed_actual_target_tracking_error_text` | mixed actual/target ✅ |
| `test_extract_performance_does_not_use_standard_deviation_as_tracking_error` | standard-deviation-only ✅ |
| `test_extract_performance_marks_manager_tracking_error_narrative_with_specific_note` | manager narrative ✅ |
| `test_extract_performance_marks_benchmark_only_tracking_error_with_specific_note` | benchmark-only ✅ |
| `test_extract_performance_marks_unparseable_direct_tracking_error_with_specific_note` | unparseable ✅ |
| `test_extract_performance_outputs_tracking_error_from_annual_table` | 直接披露（表格） ✅ |
| `test_extract_performance_marks_table_level_multiple_tracking_error_matches` | 表格多候选 ✅ |
| `test_extract_performance_keeps_table_match_when_text_discloses_same_tracking_error` | 一致双披露 ✅ |
| `test_extract_performance_marks_table_text_conflicting_tracking_error_as_inconsistent` | table/text inconsistency ✅ |
| `test_extract_performance_marks_multiple_tracking_error_matches_with_specific_note` | 多候选 ✅ |
| `test_extract_performance_accepts_direct_tracking_error_after_earlier_mixed_target_line` | 早期 blocker 后继续扫描 ✅ |
| `test_extract_performance_falls_back_to_section_two_tracking_error_when_section_three_missing` | §2 fallback ✅ |
| `test_extract_performance_accepts_direct_tracking_error_after_earlier_target_only_line` | 早期 blocker 后继续扫描 ✅ |

README 描述与实际测试一致。`implementation-control.md` 当前 gate 为 `P17-S1 aggregate deepreview`，与本次 review 定位吻合。

## 5. Blocking Correctness/Stability/Maintainability 审查

### 5.1 误采信路径分析

逐一检查可能导致错误接受 tracking_error 的路径：

| 潜在误采信场景 | 防护机制 | 评估 |
|---|---|---|
| 目标文本被采信 | `_tracking_error_context_is_target_or_ambiguous` 检查 `_TRACKING_ERROR_NEGATIVE_KEYWORDS`；test 验证 | ✅ fail-closed |
| 标准差被采信 | `_find_tracking_error_header_index` 排除含 "标准差" 的表头；text path 要求 `_line_mentions_tracking_error` | ✅ fail-closed |
| 经理叙事被采信 | `_is_manager_tracking_error_narrative` 检查管理关键词 | ✅ fail-closed |
| benchmark-only 文本被采信 | `_is_benchmark_only_tracking_error_context` 检查基准关键词且无实际信号 | ✅ fail-closed |
| 混杂 actual/target 被采信 | `_classify_tracking_error_target_context` 检查 actual signal 后返回 mixed note | ✅ fail-closed |
| 多候选被采信 | `len(matches) > 1` 返回 multi_match | ✅ fail-closed |
| table/text 不一致被采信 | `_select_consistent_tracking_error_match` 值不等返回 None → inconsistent note | ✅ fail-closed |
| 不可解析值被采信 | `_parse_percent_ratio` 返回 None → unparseable note | ✅ fail-closed |

### 5.2 `_classify_tracking_error_nonmatch_context` 标准差前置检查

`performance.py:681` 在检查 `_TRACKING_ERROR_KEYWORDS` 之前检查 `_STANDARD_DEVIATION_KEYWORDS`。对于含"净值增长率标准差"但不含"跟踪误差"的普通表格，会返回 `tracking_error_standard_deviation_only` 而非 `None`。

评估：这是更具体的诊断信号。标准差列是跟踪误差最常见的混淆源，明确标记有助于下游判断。该 note 仅出现在 `extraction_mode="missing"` 路径，不影响任何成功路径。**不阻断**。

### 5.3 "_年化" 移除影响

`_TRACKING_ERROR_ACTUAL_KEYWORDS` 不含 "年化"。纯 "年化跟踪误差为 0.53%" 无 "报告期"/"本报告期" 前缀时，`_has_actual_tracking_error_signal` 返回 False。

评估："年化"是时间维度修饰词，不是"实际观察"信号。"力争将年化跟踪误差控制在 4% 以内"中的"年化"确实不表示实际披露。纯 "年化跟踪误差为 X%" 在无 negative keywords 时仍可走通直接披露路径（因 `_tracking_error_context_is_target_or_ambiguous` 返回 False）。**不阻断**。

## Findings

无 blocking finding。

现有 findings 均为 Low/None severity，已在 code review controller judgment 中记录为 residual，aggregate review 不新增额外 finding。

## Residual Risks

| Residual | Owner | Handling |
|---|---|---|
| 标准差行无 TE keyword 时返回 `standard_deviation_only` | future note precision pass | 仅在 real data 显示误导性诊断时增加 TE keyword 前置守卫 |
| "年化"移除导致混杂行 note 降级 | future note precision pass | 不影响 fail-closed 行为 |
| `_classify_tracking_error_nonmatch_context` 缺 benchmark-only 检查 | future classifier alignment | 对齐两个 classifier 函数的检查项 |
| `tracking_error_incomplete_anchor` fixture | future parser malformed-table fixture | 当前 builder 自然生成完整 anchor |
| production `tracking_error` golden rows for `001548` 及 P16 enhanced-index 候选 | future evidence-backed golden gate | 仍需 reviewed direct observed disclosure evidence |
| calculated tracking error / external index data | future design phase | out of scope |
| 孤立 fixture `performance_with_tracking_error_ambiguous.txt` | optional cleanup | 无测试引用 |
| `_tracking_error_context_is_target_or_ambiguous` 函数名 cosmetic rename | optional cleanup | 不影响行为 |

## Validation

独立运行验证命令，结果与 implementation/code review artifact 一致：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q
# 22 passed in 0.38s ✅

.venv/bin/python -m pytest tests/fund/extractors -q
# 62 passed in 0.37s ✅

.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
# 55 passed in 0.40s ✅

.venv/bin/python -m ruff check fund_agent tests
# All checks passed! ✅

git diff --check HEAD
# no output ✅
```

附加验证：

- `grep -rn "tracking_error_ambiguous" --include="*.py" .` — 无输出 ✅
- `grep -rn "tracking_error_ambiguous" --include="*.txt" tests/fixtures/` — 无输出 ✅
- blocker precedence 元组顺序与 plan 建议一致 ✅
- 两处 early-return 均改为 append+continue 模式 ✅
- 10 种 blocker note 常量均有对应测试 ✅
- 直接披露成功契约完整保留 ✅

## Controller Follow-up Needed

无需 controller follow-up。P17-S1 aggregate deepreview 通过，可进入下一步 gate（record aggregate review in implementation-control.md，then proceed to next phase selection or closeout）。
