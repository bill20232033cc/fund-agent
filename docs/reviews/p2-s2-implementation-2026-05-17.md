# P2-S2 Implementation Artifact

> 日期：2026-05-17
> gate：`P2-S2 implementation`
> slice：`P2-S2 实现超额收益性质判断`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 在 `fund_agent/fund/analysis/` 内实现模板第 2 章的“结构性超额 vs 阶段性超额”规则判断。
- 消费 P2-S1 `RabcAttribution` 或显式 `AlphaObservation`。
- 对结构性、部分结构性、阶段性、不适用、样本不足和缺少显式环境输入写单元测试。

### Non-Goals

- 不调用 LLM，不做主观写作判断。
- 不直接读取 PDF、缓存文件或文档仓库。
- 不实现言行一致性、投资者获得感、否决项、检查清单或审计规则。
- 不输出买入、卖出、仓位比例、持有或替换建议。

## Changed Files

- `fund_agent/fund/analysis/alpha_judge.py`
- `fund_agent/fund/analysis/__init__.py`
- `tests/fund/analysis/test_alpha_judge.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control.md`

## Implemented Items

1. 新增 `AlphaObservation`
   - 表示单期 Alpha、净超额、市场环境、来源解释强度和来源说明。
2. 新增 `AlphaJudgmentRule`
   - 默认规则可配置：
     - 最少有效观察期：`3`
     - 结构性正 Alpha 年数：`4`
     - 部分结构性正 Alpha 年数：`3`
     - 结构性判断默认要求牛熊都为正
     - 结构性判断默认要求来源可解释
3. 新增 `judge_alpha_nature(...)`
   - 输出：
     - `structural`
     - `partial_structural`
     - `cyclical`
     - `not_applicable`
     - `insufficient_data`
   - 纯指数基金直接返回 `not_applicable`
   - 样本不足时返回 `insufficient_data`，不强行判断
4. 新增 `observations_from_attributions(...)`
   - 从 P2-S1 `RabcAttribution` 构造判断样本
   - `missing` 或 Alpha 缺失的归因会被跳过
   - 市场环境和来源解释强度必须显式提供，缺失时报错

## Boundary Closure

- 超额收益性质判断位于 `Capability / fund_agent/fund/analysis`，未越界进入 UI、Service、Runtime 或 Engine。
- 模块不访问文件系统，不调用文档仓库，不读取 PDF helper。
- 市场环境与来源解释强度不从收益结果中反推，避免使用间接证据。
- 当前只输出性质判断，不输出基金经理能力结论或投资建议。

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_alpha_judge.py -q
.venv/bin/python -m pytest tests/fund/analysis -q
.venv/bin/python -m ruff check fund_agent/fund/analysis tests/fund/analysis
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_parser.py tests/fund/extractors tests/fund/data/test_nav_data.py tests/fund/integration/test_p1_sample_matrix.py tests/fund/analysis -q
```

结果：

```text
7 passed
13 passed
All checks passed!
45 passed
```

## Residual Risks

### Fixed Later Slice

- `P2-S3` owner：来源解释强度后续可由言行一致性和持仓行为检查提供更强证据。
- `P2-S8` owner：当前未接入程序审计，性质判断与报告文字一致性后续再审计。

### Later Phase

- 市场环境标签当前由调用方显式提供；后续若接入温度计或市场状态模块，应通过稳定接口传入，不在本模块内部抓取或推断。

### User Decision

- 无。

## Completion Status

- `P2-S2` implementation completion signal：`reached`
- 判断依据：
  - 超额收益性质判断模块已落地
  - 核心判断类型均有测试覆盖
  - 市场环境和来源解释强度均要求显式输入
  - 文档已同步为当前接口
