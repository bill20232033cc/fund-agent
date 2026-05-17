# P1-S5 Implementation Artifact

> 日期：2026-05-17
> gate：`P1-S5 implementation`
> slice：`P1-S5 §3 表现提取与投资者收益 fallback`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 落地 `nav_benchmark_performance` 与 `investor_return` 的最小 extractor 边界。
- 让投资者收益率输出明确区分 `direct / estimated / missing` 三态。
- 为 `§3` 的净值增长率、业绩基准收益率、投资者收益率输出 `EvidenceAnchor`。

### Non-Goals

- 不修改 `data_extractor.py`。
- 不触碰 `documents/**`、`pdf/**`、`nav_data.py` 或上层目录。
- 不进入 `§4/§8/§9/§10` 抽取。
- 不实现依赖 P2 分析公式的复杂 fallback，不做任何投资结论。

## Changed Files

- `fund_agent/fund/extractors/__init__.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/performance.py`
- `tests/fund/extractors/test_performance.py`
- `tests/fixtures/fund/extractors/performance/performance_with_investor_return.txt`
- `tests/fixtures/fund/extractors/performance/performance_with_estimated_investor_return.txt`
- `tests/fixtures/fund/extractors/performance/performance_without_investor_return.txt`
- `tests/fixtures/fund/extractors/performance/performance_with_partial_nav_only.txt`

## Implemented Items

1. 扩展 `fund_agent/fund/extractors/models.py`
   - 新增 `PerformanceExtractionResult`
   - 稳定承载：
     - `nav_benchmark_performance`
     - `investor_return`
2. 新增 `fund_agent/fund/extractors/performance.py`
   - 仅基于 `§3` 做表现抽取
   - `extract_performance(report)` 当前输出：
     - `nav_benchmark_performance`
       - `nav_growth_rate`
       - `benchmark_return_rate`
     - `investor_return`
       - 直接披露时：`extraction_mode="direct"`
       - `§3` 估算口径披露时：`extraction_mode="estimated"`
       - 未披露时：`extraction_mode="missing"`
   - 所有直接命中或估算口径命中都通过 `EvidenceAnchor` 携带：
     - `document_year`
     - `section_id`
     - `row_locator`
     - 原始命中行
3. 扩展 `fund_agent/fund/extractors/__init__.py`
   - 导出：
     - `PerformanceExtractionResult`
     - `extract_performance`
4. 新增最小 `§3` fixture 与测试
  - `performance_with_investor_return.txt`
    - 覆盖直接披露路径
  - `performance_with_estimated_investor_return.txt`
    - 覆盖估算披露路径
  - `performance_without_investor_return.txt`
    - 覆盖未披露 `missing` 路径
  - `performance_with_partial_nav_only.txt`
    - 覆盖 `nav_benchmark_performance` 部分命中路径
  - `tests/fund/extractors/test_performance.py` 覆盖：
    - 净值增长率 / 基准收益率提取与 anchor
    - anchor 完整性 contract
    - 直接披露 `direct`
    - 估算披露 `estimated`
    - 未披露 `missing`
    - `nav_benchmark_performance` 部分命中时显式保留 `missing`

## §3 State Closure

- 已建立 `investor_return` 的最小三态输出：
  - `direct`
  - `estimated`
  - `missing`
- 已显式关闭“未披露时静默空字符串”的风险：
  - 当前未披露路径固定返回：
    - `extraction_mode="missing"`
    - `disclosure_status="missing"`
    - `fallback_status="pending_later_slice"`
- 当前 `estimated` 只覆盖“`§3` 中明确以估算口径披露”的情况；
  - 尚未接入依赖 `§10` 或跨章节数据的后续 fallback
- 当前 `nav_benchmark_performance` 只在净值增长率与基准收益率都命中时才返回 `direct`；
  - 若只命中一项，当前显式保留 `missing` 并附带部分命中说明

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q
```

结果：

```text
5 passed in 0.69s
```

## Residual Risks

### Fixed Later Slice

- 当前 `estimated` 只识别 `§3` 中已显式出现“估算”口径的披露，不包含后续需要依赖 `§10` 或净值序列的 fallback 计算。
- 当前 `§3` 整体缺失路径仍未通过 fixture 锁定，需在后续样本矩阵或集成测试中补强。

### Later Phase

- 当前只抽 `§3` 当前需要的表现字段，未进入 `§4/§8/§9/§10`。
- 当前 extractor 结果尚未通过 `data_extractor.py` façade 对外装配，符合当前 slice 边界。

### User Decision

- 无。

## Completion Status

- `P1-S5` completion signal：`reached`
- 判断依据：
  - 已建立 `§3` 表现 extractor 最小边界
  - `nav_benchmark_performance` 已稳定输出净值增长率与业绩基准收益率
  - `investor_return` 已稳定区分 `direct / estimated / missing`
  - 所有直接命中与估算披露命中均带 `EvidenceAnchor`
