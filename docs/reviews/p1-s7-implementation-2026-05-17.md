# P1-S7 Implementation Artifact

> 日期：2026-05-17
> gate：`P1-S7 implementation`
> slice：`P1-S7 持仓快照与份额变动`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 落地 `holdings_snapshot` 与 `share_change` 的最小 extractor 边界。
- 基于 `ParsedAnnualReport.tables` 做表格型数据抽取。
- 为前十大重仓、行业分布和份额变动输出表格型 `EvidenceAnchor`。

### Non-Goals

- 不修改 `data_extractor.py`。
- 不触碰 `documents/**`、`pdf/**`、`nav_data.py`。
- 不做人工作业行业映射。
- 不做资金流向判断、投资者收益 fallback 计算或 P2 分析。

## Changed Files

- `fund_agent/fund/extractors/__init__.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/holdings_share_change.py`
- `tests/fund/extractors/test_holdings_share_change.py`

## Implemented Items

1. 扩展 `fund_agent/fund/extractors/models.py`
   - 新增 `HoldingsShareChangeExtractionResult`
   - 稳定承载：
     - `holdings_snapshot`
     - `share_change`
2. 新增 `fund_agent/fund/extractors/holdings_share_change.py`
   - `extract_holdings_share_change(report)` 当前输出：
     - `holdings_snapshot`
       - `top_holdings`
       - `industry_distribution`
       - `industry_distribution_status`
     - `share_change`
       - `beginning_share`
       - `ending_share`
       - `net_change`
   - 表格型 anchor 当前包含：
     - `document_year`
     - `section_id`
     - `page_number`
     - `table_id`
     - `row_locator`
     - 表头说明
3. 扩展 `fund_agent/fund/extractors/__init__.py`
   - 导出：
     - `HoldingsShareChangeExtractionResult`
     - `extract_holdings_share_change`
4. 新增表格型测试
   - `tests/fund/extractors/test_holdings_share_change.py` 覆盖：
     - 前十大重仓表与表格型 anchor
     - 行业分布表与表格型 anchor
     - 份额变动表与表格型 anchor
     - 行业分布未披露时显式 `missing`
     - 缺少可识别表格时显式 `missing`

## Boundary Closure

- 当前行业分布仅在年报表格已经披露时输出；未披露时不做人工映射，返回 `industry_distribution_status="missing"`。
- 当前份额变动只抽取期初、期末、净变动原始数据，不计算投资者收益 fallback。
- 当前不从 `§8` 持仓数据推导基金类型、风格或风险判断。

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_holdings_share_change.py -q
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py -q
```

结果：

```text
3 passed
16 passed
```

## Residual Risks

### Fixed Later Slice

- 当前表格识别使用关键词匹配，真实年报表头差异仍需在 `P1-S8` 样本矩阵中继续验证。
- 当前前十大重仓和行业分布原样输出表头到值的映射，尚未归一化为统一字段名；该 schema 应在 façade 集成前统一裁决。

### Later Phase

- 当前不做持仓集中度、行业集中度、资金流向或投资者收益 fallback 判断，这些由 P2 或后续集成模块负责。

### User Decision

- 无。

## Completion Status

- `P1-S7` implementation completion signal：`reached`
- 判断依据：
  - 已建立 `§8/§10` 表格 extractor 最小边界
  - 前十大重仓和份额变动可结构化输出
  - 行业分布缺失可显式标记 `missing`
  - 表格命中路径均带页码、表 ID 和行定位
