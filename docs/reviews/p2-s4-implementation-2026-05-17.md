# P2-S4 Implementation Artifact

> 日期：2026-05-17
> gate：`P2-S4 implementation`
> slice：`P2-S4 实现投资者获得感分析`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 在 `fund_agent/fund/analysis/` 内实现模板第 4 章投资者获得感分析。
- 消费 P1 `nav_benchmark_performance`、`investor_return`、`share_change`。
- 计算行为损益：投资者实际收益率减基金产品收益率。
- 基于 §10 份额净变动和产品收益方向判断资金流向。
- 对行为损益、投资者收益缺失、追涨、抄底、获得感负向和份额字段缺失写单元测试。

### Non-Goals

- 不分析具体投资者交易行为。
- 不做未来投资者行为预测。
- 不在分析层静默估算投资者实际收益率。
- 不直接读取 PDF、缓存文件或文档仓库。
- 不实现否决项、压力测试、检查清单或审计规则。

## Changed Files

- `fund_agent/fund/analysis/investor_return.py`
- `fund_agent/fund/analysis/__init__.py`
- `tests/fund/analysis/test_investor_return.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control.md`

## Implemented Items

1. 新增 `BehaviorGapResult`
   - 输出产品收益、投资者实际收益、行为损益和证据锚点。
   - 缺少产品收益或投资者收益时返回 `missing`。
2. 新增 `FundFlowResult`
   - 输出期初份额、期末份额、净变动、净变动比例和资金流向信号。
   - 信号包括 `chasing_performance / bottom_fishing / outflow / normal / missing`。
3. 新增 `InvestorExperienceResult`
   - 汇总获得感状态、行为损益和资金流向。
   - 状态包括 `positive / neutral / negative / insufficient_data`。
4. 新增 `analyze_investor_experience(...)`
   - 串联行为损益和资金流向判断。
5. 新增 `calculate_behavior_gap(...)` 与 `judge_fund_flow(...)`
   - 支持单独测试和后续报告渲染复用。

## Boundary Closure

- 投资者获得感位于 `Capability / fund_agent/fund/analysis`，未越界进入 UI、Service、Runtime 或 Engine。
- 模块不访问文件系统，不调用文档仓库，不读取 PDF helper。
- 投资者收益率缺失时返回 `missing`，不在分析层静默估算。
- 资金流向只基于 §10 份额净变动和产品收益方向做保守判断，不分析具体投资者交易行为。

## Validation

执行命令：

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

## Residual Risks

### Fixed Later Slice

- `P2-S8` owner：行为损益和报告文字一致性审计尚未接入。
- 后续 fallback owner：投资者收益率缺失时的估算仍依赖后续明确 fallback 规则，本 slice 不静默估算。

### Later Phase

- 追涨/抄底判断当前只使用报告期净值收益方向和份额净变动方向；若后续接入月度份额/净值序列，可细化到高点/低点资金行为。

### User Decision

- 无。

## Completion Status

- `P2-S4` implementation completion signal：`reached`
- 判断依据：
  - 行为损益模块已落地
  - 份额变动资金流向判断已落地
  - 缺失投资者收益率不静默估算
  - 核心路径均有测试覆盖
