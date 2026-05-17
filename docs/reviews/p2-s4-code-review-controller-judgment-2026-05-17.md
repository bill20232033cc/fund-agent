# P2-S4 Code Review Controller Judgment

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P2 / P2-S4 投资者获得感分析
> Implementation artifact：`docs/reviews/p2-s4-implementation-2026-05-17.md`

## 1. 裁决前提

- 当前实现新增：
  - `BehaviorGapResult`
  - `FundFlowResult`
  - `InvestorExperienceResult`
  - `analyze_investor_experience(...)`
  - `calculate_behavior_gap(...)`
  - `judge_fund_flow(...)`
- controller 本地边界检查确认：
  - analysis 模块不直接读取 PDF 或文件系统
  - 行为损益只用 P1 产品收益和投资者收益字段
  - 投资者收益率缺失时不静默估算
- controller 本地验证：

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_investor_return.py -q
.venv/bin/python -m pytest tests/fund/analysis -q
.venv/bin/python -m ruff check fund_agent/fund/analysis tests/fund/analysis
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_parser.py tests/fund/extractors tests/fund/data/test_nav_data.py tests/fund/integration/test_p1_sample_matrix.py tests/fund/analysis -q
```

结果：

```text
6 passed
24 passed
All checks passed!
56 passed
```

## 2. Accepted Findings

### A1-已防护-中-投资者收益率缺失时可能被静默估算

- **来源**：controller 自查
- **裁决**：`accepted`
- **原因**：
  - P1 已把 `investor_return` 明确分成 `direct / estimated / missing`
  - P2-S4 若在缺失时静默估算，会让行为损益失去可溯源证据
- **修复**：
  - `calculate_behavior_gap(...)` 缺少投资者收益率时返回 `missing`
  - 单元测试覆盖投资者收益缺失路径

### A2-已防护-中-资金流向不能分析具体投资者交易行为

- **来源**：controller 自查
- **裁决**：`accepted`
- **原因**：
  - §10 只提供份额级别变动，不能定位具体投资者行为
- **修复**：
  - `judge_fund_flow(...)` 只输出份额净变动方向和保守信号
  - artifact 明确不分析具体投资者交易行为

## 3. Deferred Findings

### D1-未修复-中-高点/低点追涨抄底无法精细定位

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`later monthly flow adapter`
- **原因**：
  - 当前只有报告期份额净变动和期间产品收益
  - 精确识别高点/低点资金行为需要月度份额和净值序列

### D2-未修复-中-投资者收益率缺失 fallback 尚未实现

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`later investor_return fallback refinement`
- **原因**：
  - P1 已显式标记 missing 和 pending fallback
  - 本 slice 只消费现有结构化字段，不新建估算规则

## 4. 当前 Gate 结论

- `P2-S4 code review` 结论：`pass`
- 当前没有 blocker
- `P2-S4` 可推进到 accepted local commit
