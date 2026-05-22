# P17-S1 Aggregate Deepreview — GLM（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

P17-S1 完整满足 plan 的全部 success signals：旧泛化 `tracking_error_ambiguous` 生产路径彻底移除；10 种具体 fail-closed note 替换泛化歧义语义；两个早退位置修复为记录 blocker + continue；multi-match / table-text inconsistency / unparseable 优先级正确；§2 fallback 路径可达；直接披露成功契约完整保留。design v2.1 非目标边界未被突破。MiMo / GLM / controller 三方 findings 裁决一致，residual owner 清楚。存在 4 项 LOW 级 note-precision findings 和 2 项 INFO 观察，均不阻塞。

## Scope

- **Commit range**: `8cba095..HEAD`（3 commits）
- **Changed files**: `performance.py` +314/-89 行、`test_performance.py` +300/-56 行、`tests/README.md` +2/-1 行、`docs/implementation-control.md` +15 行、4 个 review artifacts
- **Baseline**: `8cba095 docs: accept p17 s1 tracking error plan`

## Plan Success Signals Audit

| Success Signal | Status | Evidence |
|---|---|---|
| 去除 stale `tracking_error_ambiguous` | DONE | `grep -rn "tracking_error_ambiguous" --include="*.py" .` 零输出；10 个新 note 常量替代（`performance.py:61-70`） |
| 具体 fail-closed note | DONE | 10 个 `Final` 常量（`_TRACKING_ERROR_NOTE_*`），每个对应至少一个测试 |
| target/mixed 不早退 | DONE | 表格路径 `performance.py:510-512`：`blocker_notes.append(...)` + `continue`；正文路径 `performance.py:566-568`：同模式；测试 `test_*_after_earlier_mixed_target_line` / `test_*_after_earlier_target_only_line` 验证后续直接披露被接受 |
| multi-match 显式 | DONE | `performance.py:525-526`（table）、`performance.py:582-583`（text）返回 `tracking_error_multi_match`；表格和正文均有测试覆盖 |
| table/text inconsistency | DONE | `performance.py:416` 在 `_select_consistent_tracking_error_match` 返回 `None` 时返回 `_TRACKING_ERROR_NOTE_TABLE_TEXT_INCONSISTENT`；优先级最高 |
| §2 fallback | DONE | `performance.py:550` `for section_id in ("§3", "§2")`；`test_extract_performance_falls_back_to_section_two_tracking_error_when_section_three_missing` 验证 anchor.section_id == "§2" |
| 直接披露契约保持 | DONE | `source_type="direct_disclosure"`、`calculation_method="disclosed"`、`frequency="annual_report_period"`、`provenance_note` 存在、`EvidenceAnchor(row_locator="tracking_error")` |

## Design-Boundary Checklist（docs/design.md §11）

| Check | Result |
|---|---|
| §1.3 non-goals 未违反（无全市场对比、实时检测、自算温度计、投资管理、交易建议、Dayu 依赖） | PASS |
| UI / Service / Capability / Runtime / Engine 边界保留 | PASS |
| 年报访问仅通过 `ParsedAnnualReport` 输入，无直接 PDF/cache/source 访问 | PASS |
| 无 Dayu runtime、LLM writing、Evidence Confirm、calculated TE、外部 index adapter | PASS |
| 无 production golden rows 变更 | PASS |
| 无 `extra_payload` 隐藏显式参数 | PASS |
| 成功信号由 deterministic tests 验证 | PASS |
| 实现范围未超出 Fund Capability extractor + focused tests | PASS |

## Reviewer Findings Reconciliation

| Reviewer | Finding | Severity | Controller Decision | Aggregate Assessment |
|---|---|---|---|---|
| MiMo F1 | 旧 `tracking_error_ambiguous` 残留可能 | — | 要求实现全部替换 | **已验证清除**：grep 零输出 |
| MiMo F2 | manager narrative classifier 欠规范 | LOW | 保持稳定信号或记 residual | **可接受**：5 个 `_TRACKING_ERROR_MANAGER_NARRATIVE_KEYWORDS` 是确定性名词，测试覆盖 |
| MiMo F3 / GLM F3 | benchmark-only 不可达 | LOW | 仅在 TE keyword 上下文中添加 | **已验证可达**：`_classify_tracking_error_line_without_parseable_value` line 711 调用 `_is_benchmark_only_tracking_error_context`，测试 `test_*_benchmark_only` 通过 |
| MiMo F4 | incomplete-anchor fixture 不可构造 | — | 记录 residual | **Residual 确认**：owner `future parser malformed-table fixture` |
| MiMo F5 / GLM F1 | blocker 积累/优先级 | LOW | 按固定 precedence 选择 | **已验证**：`_TRACKING_ERROR_BLOCKER_PRECEDENCE` 元组 + `_select_tracking_error_blocker_note` 函数正确实现 |
| MiMo F6/F7 | 旧测试缺 note 断言 | — | 更新或补 focused tests | **已覆盖**：22 个测试全部断言具体 note |
| GLM F2 | target-only continue 静默 | LOW | 记录 blocker note 后 continue | **已修复**：line 566-568 |
| GLM F4/F5 | `_has_actual_tracking_error_signal` 签名 | — | 不扩大 keyword 策略 | **保持**：4 个 actual keyword 无变更 |
| MiMo/GLM 共识 | table-level multi-match / §2 fallback 缺测试 | LOW | 补 focused test | **已补充**：`test_extract_performance_marks_table_level_multiple_tracking_error_matches` + `test_extract_performance_falls_back_to_section_two_tracking_error_when_section_three_missing` |
| MiMo/GLM 共识 | 孤立 fixture `performance_with_tracking_error_ambiguous.txt` | INFO | 可选清理 | **Deferred**：不影响行为 |

## Findings

### AF1 [LOW] `_classify_tracking_error_nonmatch_context` 在无 TE keyword 的标准差行返回 `tracking_error_standard_deviation_only`

- **文件**: `performance.py:681-682`
- **现象**: 函数先检查 `_STANDARD_DEVIATION_KEYWORDS`（line 681），不验证行是否包含 `_TRACKING_ERROR_KEYWORDS`。典型指数基金 §3 标准净值表现表（有标准差列无 TE 列）的 missing note 为 `tracking_error_standard_deviation_only` 而非通用 `年报未直接披露跟踪误差`。
- **影响**: note 语义暗示"涉及跟踪误差但只有标准差"，而实际情形可能是报告根本不涉及跟踪误差。fail-closed 行为不受影响。
- **判断**: 可接受——标准差是跟踪误差最常见混淆源，具体诊断信号有下游价值。但不排除未来出现 note 语义混乱时需加 TE keyword 前置守卫。
- **建议**: 不改，记录为 residual。

### AF2 [LOW] "年化"移除后混杂行 note 精度略降

- **文件**: `performance.py:52-57`
- **现象**: `_TRACKING_ERROR_ACTUAL_KEYWORDS` 不含"年化"。行如"年化跟踪误差为 0.53%，力争控制在 2% 以内"若无其他 actual keyword，标记为 `tracking_error_target_or_limit` 而非 `tracking_error_mixed_actual_and_target`。
- **影响**: note 精度降低，但 fail-closed 行为不变——两种情况行同样被跳过。
- **判断**: 正确——"年化"是计量口径修饰词，不是"实际观察"信号。"力争将年化跟踪误差控制在 4% 以内"中"年化"不表示实际披露。
- **建议**: 不改，记录为 residual。

### AF3 [LOW] `_classify_tracking_error_nonmatch_context` 缺 benchmark-only 检查

- **文件**: `performance.py:667-689`
- **现象**: 该函数检查标准差、TE keyword、目标/限制、经理叙事，但不检查 benchmark-only 上下文。对应的 `_classify_tracking_error_line_without_parseable_value`（line 692-713）包含该检查。
- **影响**: 含 TE keyword + benchmark keyword 但无 TE 列头的表格，在 nonmatch 路径不返回 `tracking_error_benchmark_only`。fail-closed 行为不变（fallback 到通用 missing note）。
- **判断**: 生产风险低。典型净值表不含 TE keyword。
- **建议**: 不改，记录为 residual。未来可在 manager narrative 检查后增加 `_is_benchmark_only_tracking_error_context` 调用。

### AF4 [LOW] table-level mixed-actual-target 和 §2 fallback 内 mixed 上下文无专门测试

- **文件**: `tests/fund/extractors/test_performance.py`
- **现象**: `test_extract_performance_marks_table_level_multiple_tracking_error_matches` 测试表格多候选，但未测试表格内 `_classify_tracking_error_target_context` 路径（`performance.py:510-512`）。§2 fallback 测试仅覆盖直接披露成功路径，未覆盖 §2 内 mixed/target blocker。
- **影响**: 代码路径结构一致（与正文路径对称），风险有限。测试矩阵留有间隙但不影响功能正确性。
- **建议**: 不阻塞。记录为 residual，后续可补充。

### AF5 [INFO] 孤立 fixture 和函数名 cosmetic 偏移

- **文件**: `tests/fixtures/fund/extractors/performance/performance_with_tracking_error_ambiguous.txt`、`performance.py:793`
- **现象**: fixture 文件含旧 `tracking_error_ambiguous` 命名但无测试引用；`_tracking_error_context_is_target_or_ambiguous` 函数名保留"ambiguous"但语义已收窄为 target/control。
- **影响**: 不影响生产或测试行为。
- **建议**: 可选清理。

## Residual Risks

| Residual | Severity | Owner | Handling |
|---|---|---|---|
| 标准差行无 TE keyword 时返回 `tracking_error_standard_deviation_only` | LOW | future note precision pass | 若 note 语义混乱，增加 TE keyword 前置守卫 |
| "年化"移除导致混杂行 note 降级 | LOW | future note precision pass | 不影响 fail-closed 行为 |
| `_classify_tracking_error_nonmatch_context` 缺 benchmark-only 检查 | LOW | future classifier alignment | 对齐两个 classifier 的检查项 |
| table-level mixed-target / §2 fallback mixed 无专门测试 | LOW | next test pass | 补充 focused test |
| `tracking_error_incomplete_anchor` fixture | — | future parser malformed-table fixture | 当前 builder 自然生成完整 anchor |
| production `tracking_error` golden rows | — | future evidence-backed golden gate | 001548 和 P16 enhanced-index 候选仍 blocked |
| calculated tracking error / external index data | — | future design phase | Out of scope |
| 孤立 fixture / cosmetic rename | INFO | optional cleanup | 无行为影响 |

## Validation

本地独立复现：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q
# 22 passed in 0.36s ✓

.venv/bin/python -m pytest tests/fund/extractors -q
# 62 passed in 0.36s ✓

.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
# 55 passed in 0.39s ✓

.venv/bin/python -m ruff check fund_agent tests
# All checks passed! ✓

git diff --check HEAD
# no output ✓

grep -rn "tracking_error_ambiguous" --include="*.py" .
# no output ✓
```

全部验证通过，与 implementation artifact 和 controller judgment 记录一致。

## Control-Document Consistency

- `docs/implementation-control.md:9` 记录当前 gate 为 `P17-S1 aggregate deepreview` — 与本次 review 一致
- `docs/implementation-control.md:18-20` 记录 next entry point — 正确
- `docs/implementation-control.md:159` Active Gate Ledger 记录 P17-S1 implementation accepted at commit `d069862` — 与 `git log` 一致
- `tests/README.md:15` 描述 `test_performance.py` 覆盖跟踪误差直接披露、目标/限制、mixed actual/target、manager narrative、benchmark-only、standard-deviation-only、unparseable、table/text inconsistency、多候选、表格多候选、§2 fallback 和早期 blocker 后继续扫描 — 与 22 个测试实际覆盖一致

## Controller Follow-up Needed

无需 blocking follow-up。可选后续：

1. 若 aggregate controller judgment 接受本 review，更新 `docs/implementation-control.md` gate 状态和 next entry point。
2. 可选 cosmetic cleanup：删除孤立 fixture `performance_with_tracking_error_ambiguous.txt`；将 `_tracking_error_context_is_target_or_ambiguous` 重命名为 `_tracking_error_context_is_target_or_control`。
3. 未来 test pass 可补充 table-level mixed-target 和 §2 fallback mixed 场景的 focused test。
