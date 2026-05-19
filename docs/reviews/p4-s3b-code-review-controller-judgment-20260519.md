# P4-S3b Code Review Controller Judgment

> 日期：2026-05-19
> Gate：`P4-S3b review judgment`
> 审查对象：`004393` 高影响 extractor 缺口修复
> 裁决：PASS；P4-S3b 可接受，下一步进入 P4-S4 报告质量审计与阻断。

## 总体裁决

P4-S3b 的目标是基于 P4-S2/P4-S3a snapshot 与 score，优先修复 `004393` 中有直接、语义清晰年报证据的高影响 extractor 缺口，不在同一 slice 中重写所有 extractor。

本次实现满足验收条件：

- 修复 5 个高影响字段：`nav_benchmark_performance`、`manager_strategy_text`、`manager_alignment`、`holder_structure`、`share_change`。
- 每个字段都有基于 `004393` 真实章节/表格形态构造的最小复现测试。
- 修复后真实 `004393` snapshot/score 证明对应字段 coverage / traceability 从 0.0% 提升到 100.0%。
- 没有绕过统一文档仓库接口；解析规则仍在 Capability 层 extractor 内。
- `fee_schedule` 未修复是正确边界：真实 `§6` 披露的是当期支付费用金额，不是费率，不能污染 `fee_schedule` 语义。

## Review Findings 裁决

| 来源 | Finding | Severity | Controller 裁决 | 处理 |
|---|---|---:|---|---|
| MiMo | `performance.py` 表头子串匹配可能误中“标准差”列 | Medium | accepted and fixed | 已改为必含/排除关键词匹配，并新增列序反转回归测试 |
| MiMo/GLM | `_infer_adjacent_personal_ratio` 硬编码 `+2` 偏移且缺少比例格式校验 | Medium | accepted and fixed | 已改为候选相邻列 + 比例值校验，并新增相邻比例/非比例回归测试 |
| MiMo/GLM | `share_change` 多份额列取首个有效值，无份额级别选择策略 | Low | deferred | 需要引入份额级别选择策略；当前 004393 A 份额不触发，保留为后续 residual risk |

## Targeted Re-Review

accepted findings 修复后已派发 MiMo / GLM 做 targeted re-review，不重开 P4 全量 review：

- MiMo：`docs/reviews/p4-s3b-rereview-mimo-20260519-1300.md`，结论 PASS。
- GLM：`docs/reviews/p4-s3b-rereview-glm-20260519.md`，结论 PASS。

两份 re-review 均确认：

- `performance.py` 表头匹配排除“标准差”列的修复已闭合。
- `manager_ownership.py` 跨页持有人结构 fallback 的候选列探测与比例值校验已闭合。
- `share_change` 多份额列选择策略作为 residual risk deferred 合理。
- `fee_schedule` 不以费用金额冒充费率合理。

## Controller 自验

已运行：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py -q
# 20 passed

.venv/bin/ruff check fund_agent/fund/extractors/performance.py fund_agent/fund/extractors/manager_ownership.py fund_agent/fund/extractors/holdings_share_change.py tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py
# All checks passed

git diff --check
# passed

.venv/bin/python -m pytest tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py -q
# 24 passed
```

真实 snapshot/score 复核：

```bash
.venv/bin/fund-analysis extraction-snapshot --run-id p4-s3b-004393-controller-final --fund-code 004393 --report-year 2024
.venv/bin/fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/p4-s3b-004393-controller-final/snapshot.jsonl --output-dir reports/extraction-snapshots/p4-s3b-004393-controller-final-score
```

结果：

- `errors.jsonl` 为 0 bytes。
- `summary.md` 显示 `nav_benchmark_performance`、`manager_strategy_text`、`manager_alignment`、`holder_structure`、`share_change` 均为 `100.0%` coverage / traceability。
- `score.md` 显示 `pass=9`、`fail=5`、`p0_status=fail`。
- `p0_status=fail` 的原因仍是 `fee_schedule` 缺失；这是本 slice 有意保留的语义边界，不应以费用金额冒充费率。

## 残余风险

- `share_change` 多份额列仍未根据基金代码选择 A/C 份额列；后续需要明确份额级别选择策略。
- `turnover_rate`、`holdings_snapshot`、`investor_return` 仍未在本 slice 修复。
- `score.md` 的 correctness 仍为 `not_implemented`；coverage / traceability 只能证明“抽到了且有锚点”，不能替代 golden answer 正确性校验。
- 跨页表格识别仍依赖 `ParsedTable` 顺序和相邻页表格形态；更复杂 PDF 布局需要后续在文档解析层或 extractor 层继续增强。

## 下一步

P4-S3b accepted。下一 gate 为 `P4-S4 implementation`：把 P4-S1/S2/S3 形成的 snapshot/score 能力接入报告质量 gate，至少让低质量输入被标记或阻断，避免“形式合格、内容不可用”的报告进入可用状态。
