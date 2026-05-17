# P2-S3 Implementation Artifact

> 日期：2026-05-17
> gate：`P2-S3 implementation`
> slice：`P2-S3 实现言行一致性检验`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 在 `fund_agent/fund/analysis/` 内实现模板第 3 章言行一致性 4 维度检查。
- 消费 P1 `manager_strategy_text`、`holdings_snapshot`、`turnover_rate` 和调用方显式提供的实际风格/股票仓位。
- 对 4 维度一致、风格/行业不一致、缺少显式实际证据、高换手冲突、行业分布缺失写单元测试。

### Non-Goals

- 不猜测基金经理动机或性格。
- 不从重仓名称、行业分布或收益结果反推实际持仓风格。
- 不直接读取 PDF、缓存文件或文档仓库。
- 不实现投资者获得感、否决项、检查清单或审计规则。
- 不输出买入、卖出、仓位比例、持有或替换建议。

## Changed Files

- `fund_agent/fund/analysis/_ratios.py`
- `fund_agent/fund/analysis/consistency_check.py`
- `fund_agent/fund/analysis/r_abc.py`
- `fund_agent/fund/analysis/__init__.py`
- `tests/fund/analysis/test_consistency_check.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control.md`

## Implemented Items

1. 新增 `ConsistencyRule`
   - 配置低/高换手阈值和低/高仓位阈值。
2. 新增 `ConsistencyDimensionResult`
   - 输出单维度 `aligned / partial / misaligned / insufficient_data` 与 `green / yellow / red / gray` 信号。
3. 新增 `ConsistencyCheckResult`
   - 输出 4 维度结果和整体状态。
4. 新增 `check_consistency(...)`
   - 投资风格：§4 风格宣称 vs 显式实际持仓风格
   - 行业偏好：§4 行业宣称 vs §8 行业分布
   - 仓位管理：§4 仓位策略 vs 显式实际股票仓位
   - 换手水平：§4 持有周期/换手宣称 vs §8 换手率
5. 新增 `analysis/_ratios.py`
   - 收口 P2 分析模块内重复的百分比解析逻辑
   - `r_abc.py` 和 `consistency_check.py` 均改为复用该 helper

## Boundary Closure

- 言行一致性位于 `Capability / fund_agent/fund/analysis`，未越界进入 UI、Service、Runtime 或 Engine。
- 模块不访问文件系统，不调用文档仓库，不读取 PDF helper。
- 实际持仓风格和股票仓位必须显式传入；缺失时返回 `insufficient_data`，不使用间接证据。
- 行业偏好只在 §4 明确行业宣称和 §8 行业分布都存在时判断。

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_consistency_check.py -q
.venv/bin/python -m pytest tests/fund/analysis -q
.venv/bin/python -m ruff check fund_agent/fund/analysis tests/fund/analysis
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_parser.py tests/fund/extractors tests/fund/data/test_nav_data.py tests/fund/integration/test_p1_sample_matrix.py tests/fund/analysis -q
```

结果：

```text
5 passed
18 passed
All checks passed!
50 passed
```

## Residual Risks

### Fixed Later Slice

- `P2-S8` owner：言行一致性信号与报告文字一致性审计尚未接入。
- 后续 extractor refinement owner：实际持仓风格和股票仓位当前仍需显式输入，尚未由 P1 稳定抽取。

### Later Phase

- 跨期风格稳定性需要多期持仓风格输入；当前 P2-S3 只完成当期 §4 vs §8 的 4 维度一致性检查。

### User Decision

- 无。

## Completion Status

- `P2-S3` implementation completion signal：`reached`
- 判断依据：
  - 4 维度言行一致性模块已落地
  - 缺失实际证据不静默假设
  - 核心信号路径均有测试覆盖
  - 文档已同步为当前接口
