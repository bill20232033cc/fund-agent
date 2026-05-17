# P2-S6 Implementation Artifact

> 日期：2026-05-17
> gate：`P2-S6 implementation`
> slice：`P2-S6 实现压力测试`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 在 `fund_agent/fund/analysis/risk_check.py` 内实现模板第 6 章“核心风险与否决项”的压力测试。
- 固定模拟 `-20% / -40% / -60%` 三个场景，满足 `docs/design.md` 第 4.5 节。
- 按基金类型应用 `docs/fund-analysis-template-draft.md` 第 6 章 `preferred_lens` 压力阈值。
- 输出账户余额、浮亏金额、压力等级、承受能力状态和下一步最小验证问题。

### Non-Goals

- 不预测下跌发生概率。
- 不读取年报、PDF、缓存文件或文档仓库。
- 不抓取用户画像、资金用途或风险偏好。
- 不输出买入、卖出、仓位比例、持有或替换建议。
- 不实现 P2-S7 检查清单消费压力测试输出。

## Changed Files

- `fund_agent/fund/analysis/risk_check.py`
- `fund_agent/fund/analysis/__init__.py`
- `tests/fund/analysis/test_risk_check.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control.md`

## Implemented Items

1. 新增 `StressTestRule`
   - 固定压力场景：`minus_20 / minus_40 / minus_60`
   - 基金类型阈值按模板第 6 章配置
2. 新增 `StressScenarioResult`
   - 输出场景跌幅、投入金额、账户余额、浮亏金额、压力等级、承受能力状态、阈值说明和判断依据
3. 新增 `StressTestResult`
   - 汇总基金类型、投入金额、最大可承受亏损比例、场景列表、最差场景和下一步最小验证问题
4. 新增 `run_stress_test(...)`
   - `investment_amount` 必须显式提供且大于 0
   - `max_tolerable_loss_rate` 缺失时返回 `not_provided`，不猜测承受能力
   - 自定义阈值通过 `StressTestRule` 注入，避免调用处硬编码

## Boundary Closure

- 压力测试位于 `Capability / fund_agent/fund/analysis`，未越界进入 UI、Service、Runtime 或 Engine。
- 模块不访问文件系统，不调用文档仓库，不读取 PDF helper。
- 投入金额和最大可承受亏损比例由调用方显式提供。
- 基金类型必须由上游先识别，再传入 `run_stress_test(...)`。

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_risk_check.py -q
.venv/bin/python -m ruff check fund_agent/fund/analysis tests/fund/analysis
```

结果：

```text
10 passed
All checks passed!
```

## Residual Risks

### Fixed Later Slice

- `P2-S7` owner：检查清单尚未消费压力测试输出。
- `P2-S8` owner：压力测试和报告文字一致性审计尚未接入。

### Later Phase

- 投入金额和最大可承受亏损比例当前由调用方显式提供；后续可由用户画像或买入前问答接入，但不能在本模块内猜测。

### User Decision

- 无。

## Completion Status

- `P2-S6` implementation completion signal：`reached`
- 判断依据：
  - 固定压力场景已落地
  - 基金类型阈值已配置化
  - 缺失用户承受能力不强判
  - 核心路径和非法输入均有测试覆盖
