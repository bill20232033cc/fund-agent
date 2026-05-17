# P1-S7 Code Review Controller Judgment

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S7 持仓快照与份额变动
> Implementation artifact：`docs/reviews/p1-s7-implementation-2026-05-17.md`

## 1. 裁决前提

- 当前实现严格限定在 `§8/§10` 表格型原始数据抽取：
  - `holdings_snapshot` 消费 `ParsedAnnualReport.tables` 中的前十大重仓与行业分布表
  - `share_change` 消费 `ParsedAnnualReport.tables` 中的份额变动表
- 当前实现未触碰：
  - `fund_agent/fund/data_extractor.py`
  - `fund_agent/fund/documents/**`
  - `fund_agent/fund/pdf/**`
  - `fund_agent/fund/data/nav_data.py`
  - 其他 extractor
  - P2 分析、判断、审计逻辑
- controller 本地验证：

```bash
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_parser.py tests/fund/extractors/test_profile.py tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py -q
```

结果：`29 passed`

## 2. Accepted Findings

### A1-已修复-中-份额变动表识别对“净变动”文本过窄

- **来源**：controller 本地 review / 初次测试失败
- **裁决**：`accepted`
- **原因**：
  - 份额变动表可能使用“本期申购赎回净额”表达净变动
  - 原识别条件要求同时包含“期初 / 期末 / 净变动”，会漏掉合理披露口径
- **修复**：
  - 当前识别逻辑改为：
    - 必须包含“期初”
    - 必须包含“期末”
    - 同时包含“净变动”或“本期申购赎回净额”之一
- **测试**：
  - `tests/fund/extractors/test_holdings_share_change.py` 的份额变动 fixture 使用“本期申购赎回净额”，当前已通过

## 3. Deferred Findings

### D1-未修复-中-真实年报表头差异尚未覆盖

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P1-S8 / real sample matrix`
- **原因**：
  - 当前测试使用最小 `ParsedTable` fixture 锁定契约与 anchor
  - 真实年报可能使用不同表头或多级表头，应在 P1 验收矩阵中继续扩展

### D2-未修复-低-前十大重仓与行业分布字段名尚未统一

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P1-S8 / façade schema finalization`
- **原因**：
  - 当前按原表头输出，利于证据溯源
  - 对外 bundle 的稳定字段名应在 `data_extractor.py` façade 集成时统一裁决

## 4. 当前 Gate 结论

- `P1-S7 code review` 结论：`pass`
- 当前没有 blocker
- `P1-S7` 可推进到 accepted local commit，并把下一 entry point 切到 `P1-S8 implementation + review`
