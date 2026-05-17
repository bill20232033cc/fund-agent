# P1-S6 Implementation Artifact

> 日期：2026-05-17
> gate：`P1-S6 implementation`
> slice：`P1-S6 管理人文本、换手率、利益一致性与持有人结构`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 落地 `manager_strategy_text`、`turnover_rate`、`manager_alignment`、`holder_structure` 的最小 extractor 边界。
- 仅基于 `§4/§8/§9` 的直接披露文本做规则化抽取。
- 为换手率、基金经理/从业人员持有、持有人结构等命中字段输出 `EvidenceAnchor`。

### Non-Goals

- 不修改 `data_extractor.py`。
- 不触碰 `documents/**`、`pdf/**`、`nav_data.py`。
- 不进入 `§10` 份额变动或持仓快照抽取。
- 不做言行一致性、利益一致性红黄绿、成本估算或投资判断。

## Changed Files

- `fund_agent/fund/extractors/__init__.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/manager_ownership.py`
- `tests/fund/extractors/test_manager_ownership.py`
- `tests/fixtures/fund/extractors/manager_ownership/manager_ownership_complete.txt`
- `tests/fixtures/fund/extractors/manager_ownership/manager_ownership_missing.txt`
- `tests/fixtures/fund/extractors/manager_ownership/manager_ownership_partial.txt`
- `tests/fixtures/fund/extractors/manager_ownership/manager_ownership_turnover_basis_only.txt`

## Implemented Items

1. 扩展 `fund_agent/fund/extractors/models.py`
   - 新增 `ManagerOwnershipExtractionResult`
   - 稳定承载：
     - `manager_strategy_text`
     - `turnover_rate`
     - `manager_alignment`
     - `holder_structure`
2. 新增 `fund_agent/fund/extractors/manager_ownership.py`
   - `extract_manager_ownership(report)` 当前输出：
     - `manager_strategy_text`
       - `strategy_summary`
       - `style_positioning`
       - `market_outlook`
     - `turnover_rate`
       - `turnover_rate`
       - `turnover_basis`
     - `manager_alignment`
       - `manager_holding`
       - `employee_holding`
       - `judgment=None`
     - `holder_structure`
       - `institutional_holder`
       - `individual_holder`
   - 所有命中字段均通过 `EvidenceAnchor` 携带：
     - `document_year`
     - `section_id`
     - `row_locator`
     - 原始命中行
3. 扩展 `fund_agent/fund/extractors/__init__.py`
   - 导出：
     - `ManagerOwnershipExtractionResult`
     - `extract_manager_ownership`
4. 新增最小 `§4/§8/§9` fixture 与测试
   - `manager_ownership_complete.txt`
     - 覆盖四类字段完整直接披露路径
   - `manager_ownership_missing.txt`
     - 覆盖四类字段未披露 `missing` 路径
   - `manager_ownership_partial.txt`
     - 覆盖部分披露路径
   - `manager_ownership_turnover_basis_only.txt`
     - 覆盖只有换手率口径、缺少换手率数值的路径
   - `tests/fund/extractors/test_manager_ownership.py` 覆盖：
     - `§4` 策略文本提取与 anchor
     - `§8` 换手率提取与 anchor
     - `§9` 基金经理/从业人员持有原始披露
     - `§9` 机构/个人持有人结构
     - 未披露时显式 `missing`
     - 部分披露时保留原始值，不输出主观判断
     - 换手率数值缺失时不能标记为 `direct`

## Boundary Closure

- `manager_alignment.value["judgment"]` 固定为 `None`，表示 P1 只保留原始披露，不做利益一致性判断。
- 当前 `turnover_rate` 未披露时返回 `missing`，不做同类中位数估算。
- 当前 `turnover_rate` 只有在换手率数值命中时才返回 `direct`；仅命中换手率口径时仍返回 `missing`。
- 当前实现不读取 `§10`，不依赖跨章节计算，也不消费 P2 公式。

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_manager_ownership.py -q
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py -q
```

结果：

```text
4 passed
13 passed
```

## Residual Risks

### Fixed Later Slice

- 当前 fixture 为最小文本夹具，真实年报中 `§4/§8/§9` 的表格和字段命名差异仍需在 `P1-S8` 样本矩阵中继续验证。
- 当前未实现换手率缺失时按同类中位数估算；该估算需要同类口径和样本数据，不能在本 slice 用间接证据填充。

### Later Phase

- 当前不做言行一致性、利益一致性或成本侵蚀判断，这些由 P2 分析模块负责。

### User Decision

- 无。

## Completion Status

- `P1-S6` implementation completion signal：`reached`
- 判断依据：
  - 已建立 `§4/§8/§9` extractor 最小边界
  - 四类输出字段均可区分 `direct / missing`
  - 换手率与持有人信息命中路径均带 `EvidenceAnchor`
  - 未引入任何 P2 判断逻辑
