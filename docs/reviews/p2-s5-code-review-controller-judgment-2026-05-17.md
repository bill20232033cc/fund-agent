# P2-S5 Code Review Controller Judgment

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P2 / P2-S5 否决项检查
> Implementation artifact：`docs/reviews/p2-s5-implementation-2026-05-17.md`

## 1. 裁决前提

- 当前实现新增：
  - `RiskCheckRule`
  - `RiskCheckItem`
  - `RiskCheckResult`
  - `run_risk_checks(...)`
- controller 本地边界检查确认：
  - analysis 模块不直接读取 PDF 或文件系统
  - 基金经理任期、同类费率和跟踪误差均要求显式输入
  - 缺失输入返回 `insufficient_data`，不强判为安全
- controller 本地验证：

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_risk_check.py -q
.venv/bin/python -m ruff check fund_agent/fund/analysis tests/fund/analysis
```

结果：

```text
5 passed
All checks passed!
```

## 2. Accepted Findings

### A1-已防护-中-缺失经理任期/同类费率/跟踪误差时可能被误判为安全

- **来源**：controller 自查
- **裁决**：`accepted`
- **原因**：
  - 这些输入当前不在 P1 稳定结构化字段内
  - 若缺失时直接 pass，会掩盖关键风险
- **修复**：
  - 对应检查项返回 `insufficient_data`
  - 汇总状态进入 `watch`
  - 单元测试覆盖显式输入缺失路径

### A2-已防护-低-非指数基金跟踪误差不适用

- **来源**：controller 自查
- **裁决**：`accepted`
- **原因**：
  - 跟踪误差否决项只适用于指数基金/指数增强
- **修复**：
  - 非指数基金返回 `pass`，并在 reason 说明不适用

## 3. Deferred Findings

### D1-未修复-中-压力测试尚未接入

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P2-S6`
- **原因**：
  - 总控文档将否决项检查和压力测试拆为 P2-S5 / P2-S6

### D2-未修复-中-外部风险输入尚未有稳定 adapter

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`later external metrics adapter`
- **原因**：
  - 经理任期、同类费率中位数、跟踪误差目前由调用方显式提供
  - 后续接入外部数据源时应通过稳定 adapter，不在 `risk_check.py` 内抓取

## 4. 当前 Gate 结论

- `P2-S5 code review` 结论：`pass`
- 当前没有 blocker
- `P2-S5` 可推进到 accepted local commit
