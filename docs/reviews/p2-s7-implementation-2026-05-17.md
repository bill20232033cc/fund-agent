# P2-S7 Implementation Artifact

> 日期：2026-05-17
> gate：`P2-S7 implementation`
> slice：`P2-S7 实现检查清单引擎`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 在 `fund_agent/fund/analysis/checklist.py` 内实现 `docs/design.md` 第 4.6 节的 7 问题买入前检查清单。
- 消费 P2 已有分析结果与调用方显式输入，输出红/黄/绿/灰灯和汇总状态。
- 对全绿、红灯阻断、灰灯缺失、黄灯跟踪、资金期限阈值配置、异常否决项输入和 7 问题顺序写单元测试。

### Non-Goals

- 不实现程序审计 R1/R2；审计归属 `P2-S8`。
- 不读取年报、PDF、缓存文件或文档仓库。
- 不接入温度计、用户画像或问答系统。
- 不输出买入、卖出、仓位比例或收益预测。

## Changed Files

- `fund_agent/fund/analysis/checklist.py`
- `fund_agent/fund/analysis/__init__.py`
- `tests/fund/analysis/test_checklist.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control.md`

## Implemented Items

1. 新增 `ChecklistRule`
   - 配置用户资金最短不用期限阈值
   - 配置 §9 持有披露正负关键词
2. 新增 `ChecklistItem`
   - 输出单题 `green / yellow / red / gray`
   - 输出单题 `pass / watch / block / insufficient_data`
   - 保留证据锚点与判断依据
3. 新增 `ChecklistResult`
   - 汇总 7 个问题、红灯/黄灯/灰灯分组、整体状态和下一步最小验证问题
4. 新增 `run_checklist(...)`
   - 第 1 问消费 `RabcAttribution.net_excess_return`
   - 第 2 问消费 §9 `manager_alignment`
   - 第 3 问消费 `InvestorExperienceResult`
   - 第 4 问消费 `ConsistencyCheckResult`
   - 第 5 问消费 `RiskCheckResult`
   - 第 6 问消费显式 `valuation_state`
   - 第 7 问消费显式 `money_horizon` 或 `user_money_horizon_years`

## Boundary Closure

- 检查清单位于 `Capability / fund_agent/fund/analysis`，未越界进入 UI、Service、Runtime 或 Engine。
- 模块不访问文件系统，不调用文档仓库，不读取 PDF helper。
- 估值状态和用户资金期限必须显式提供；缺失时输出灰灯，不默认通过。
- 资金年限按普通 Decimal 年数解析，不复用百分比解析。

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/analysis -q
.venv/bin/python -m ruff check fund_agent/fund/analysis tests/fund/analysis
```

结果：

```text
40 passed
All checks passed!
```

## Residual Risks

### Fixed Later Slice

- `P2-S8` owner：R1/R2 审计尚未验证检查清单信号与规则一致性。

### Later Phase

- 温度计估值状态当前由调用方显式提供，尚未接入 adapter。
- 用户资金期限当前由调用方显式提供，尚未接入用户问答或画像。

### User Decision

- 无。

## Completion Status

- `P2-S7` implementation completion signal：`reached`
- 判断依据：
  - 7 问题完整输出已落地
  - 红黄绿灰汇总规则已落地
  - 缺失显式输入不强判
  - 核心路径、配置阈值和异常输入防御均有测试覆盖
