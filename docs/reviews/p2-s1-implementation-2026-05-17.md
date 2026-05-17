# P2-S1 Implementation Artifact

> 日期：2026-05-17
> gate：`P2-S1 implementation`
> slice：`P2-S1 实现 R=A+B-C 计算模块`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 在 `fund_agent/fund/analysis/` 内实现模板第 2 章 R=A+B-C 单期收益归因计算。
- 支持纯计算输入 `RabcInput`，以及从 P1 `StructuredFundDataBundle` 适配计算。
- 对公式闭合、P1 字段解析、证据锚点传递和缺失输入路径写单元测试。

### Non-Goals

- 不直接读取 PDF、缓存文件或文档仓库。
- 不实现结构性 vs 阶段性超额判断。
- 不实现言行一致性、投资者获得感、否决项、检查清单或审计规则。
- 不输出买入、卖出、仓位比例建议。

## Changed Files

- `fund_agent/fund/analysis/r_abc.py`
- `fund_agent/fund/analysis/__init__.py`
- `tests/fund/analysis/test_r_abc.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control.md`

## Implemented Items

1. 新增 `RabcInput`
   - 所有比例统一使用小数口径。
   - 字段包括 `nav_growth_rate`、`benchmark_return_rate`、`equity_position`、`management_fee_rate`、`custody_fee_rate`、`turnover_rate`。
2. 新增 `RabcAttribution`
   - 输出 `R`、`B`、`A`、`C`、`turnover_cost`、`net_excess_return`。
   - 支持 `computed / missing` 状态。
   - 保留参与计算字段的 `EvidenceAnchor`。
3. 新增 `calculate_r_abc(...)`
   - 公式按 `docs/design.md` 第 4.1 节：
     - `B = 业绩比较基准收益率 × 股票仓位`
     - `A = R - B`
     - `C = 管理费 + 托管费 + 换手率 × 0.3%`
     - `净超额 = A - C`
4. 新增 `calculate_r_abc_series(...)`
   - 支持 `1y / 3y / 5y` 等多个周期按同一公式批量计算
   - 输出顺序与输入顺序一致
5. 新增 `calculate_r_abc_from_bundle(...)`
   - 只消费 P1 `StructuredFundDataBundle`。
   - 解析 `12.34%`、`1.20%/年`、`80%`、`80` 等常见比例输入。
   - P1 当前尚未稳定抽取股票仓位，因此 `equity_position` 必须显式传入。
   - 关键字段缺失或子值缺失时返回 `missing`，不静默套用假设。

## Boundary Closure

- R=A+B-C 位于 `Capability / fund_agent/fund/analysis`，未越界进入 UI、Service、Runtime 或 Engine。
- 模块不访问文件系统，不调用文档仓库，不读取 PDF helper。
- `calculate_r_abc_from_bundle(...)` 对 P1 字段只做分析层适配，不把 P2 判断写回 P1 extractor。
- 股票仓位缺失时显式返回 `missing`，保持 root cause 同源于输入数据，而不是使用间接默认值。

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_r_abc.py -q
.venv/bin/python -m ruff check fund_agent/fund/analysis tests/fund/analysis
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_parser.py tests/fund/extractors tests/fund/data/test_nav_data.py tests/fund/integration/test_p1_sample_matrix.py tests/fund/analysis/test_r_abc.py -q
```

结果：

```text
6 passed
All checks passed!
38 passed
```

## Residual Risks

### Fixed Later Slice

- `P2-S2` owner：当前只输出数值归因，不判断结构性超额或阶段性超额。
- `P2-S8` owner：当前未接入 L1 审计规则，公式错误检测后续在程序审计 slice 落地。

### Later Phase

- P1 尚未稳定抽取股票仓位，当前通过显式参数输入。若后续 extractor 能稳定输出股票仓位，可在分析层适配中替换为结构化字段。

### User Decision

- 无。

## Completion Status

- `P2-S1` implementation completion signal：`reached`
- 判断依据：
  - R=A+B-C 计算模块已落地
  - 与手工计算一致的单期和多周期单元测试已覆盖
  - 缺失输入不静默假设
  - 文档已同步为当前接口
