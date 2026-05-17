# P2-S5 Implementation Artifact

> 日期：2026-05-17
> gate：`P2-S5 implementation`
> slice：`P2-S5 实现否决项检查`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 在 `fund_agent/fund/analysis/` 内实现模板第 6 章的 5 项否决检查。
- 消费 P1 `basic_identity`、`fee_schedule`、P2-S3 `ConsistencyCheckResult`，以及调用方显式传入的经理任期、同类费率中位数和跟踪误差。
- 对安全输入、清盘风险、短任期、风格漂移、费率过高、指数跟踪误差、显式输入缺失写单元测试。

### Non-Goals

- 不实现压力测试；压力测试按总控拆到 P2-S6。
- 不抓取基金经理任职日期、同类费率或跟踪误差。
- 不直接读取 PDF、缓存文件或文档仓库。
- 不输出买入、卖出、仓位比例、持有或替换建议。

## Changed Files

- `fund_agent/fund/analysis/risk_check.py`
- `fund_agent/fund/analysis/__init__.py`
- `tests/fund/analysis/test_risk_check.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control.md`

## Implemented Items

1. 新增 `RiskCheckRule`
   - 清盘风险规模阈值：`5000 万元`
   - 基金经理最短管理本基金时间：`6 个月`
   - 费率过高阈值：同类中位数 `2 倍`
   - 指数基金跟踪误差阈值：`2%`
2. 新增 `RiskCheckItem`
   - 输出单项 `pass / watch / veto / insufficient_data`
   - 保留当前值、阈值、证据锚点和判断依据
3. 新增 `RiskCheckResult`
   - 汇总 5 项检查结果、否决项、跟踪项和下一步最小验证问题
4. 新增 `run_risk_checks(...)`
   - 清盘风险：基金规模 `< 5000 万元`
   - 基金经理任期：管理本基金 `< 6 个月`
   - 严重风格漂移：言行一致性检验红灯
   - 费率远超同类：总费率 `> 同类中位数 × 2`
   - 跟踪误差过大：指数基金跟踪误差 `> 2%`

## Boundary Closure

- 否决项检查位于 `Capability / fund_agent/fund/analysis`，未越界进入 UI、Service、Runtime 或 Engine。
- 模块不访问文件系统，不调用文档仓库，不读取 PDF helper。
- 基金经理任期、同类费率中位数和跟踪误差必须显式传入；缺失时返回 `insufficient_data`。
- 非指数基金不适用跟踪误差否决项，返回 `pass` 并说明原因。

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_risk_check.py -q
.venv/bin/python -m ruff check fund_agent/fund/analysis tests/fund/analysis
```

结果：

```text
5 passed
All checks passed!
```

## Residual Risks

### Fixed Later Slice

- `P2-S6` owner：压力测试尚未接入。
- `P2-S8` owner：R1/R2 审计尚未验证否决项与报告结论一致性。

### Later Phase

- 基金经理任期、同类费率中位数和跟踪误差当前由调用方显式提供；后续可通过稳定 adapter 或 extractor 接入，但不能在本模块内抓取或推断。

### User Decision

- 无。

## Completion Status

- `P2-S5` implementation completion signal：`reached`
- 判断依据：
  - 5 项否决检查已落地
  - 缺失显式输入不强判
  - 核心否决和安全路径均有测试覆盖
