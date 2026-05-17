# P1-S6 基线对账裁决

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S6 管理人文本、换手率、利益一致性与持有人结构
> 分支：`chore/reconcile-baseline`
> 当前 gate：`P1-S6 implementation + review`
> 上一 accepted slice commit：`8102944` (`gateflow: accept P1 P1-S5`)

## 1. 当前入口

- `docs/implementation-control.md` 当前 gate 已推进到 `P1-S6 implementation + review`。
- `docs/reviews/p1-plan-2026-05-17.md` 要求本 slice 落地：
  - `manager_strategy_text`
  - `turnover_rate`
  - `manager_alignment`
  - `holder_structure`
- 本 slice 只做 `§4/§8/§9` 直接披露字段的结构化抽取，不做言行一致性、利益一致性好坏判断或 P2 分析。

## 2. 当前基线事实

- 已有稳定输入：
  - `ParsedAnnualReport`
  - `ParsedAnnualReport.get_section_text(section_id)`
  - `EvidenceAnchor`
  - `ExtractedField`
- 已完成的 extractor：
  - `extract_profile(report)` 覆盖 `§1/§2`
  - `extract_performance(report)` 覆盖 `§3`
- 当前尚未存在：
  - `fund_agent/fund/extractors/manager_ownership.py`
  - `ManagerOwnershipExtractionResult`
  - `tests/fund/extractors/test_manager_ownership.py`
  - `tests/fixtures/fund/extractors/manager_ownership/**`

## 3. 范围裁决

### Allowed files/modules

- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/manager_ownership.py`
- `fund_agent/fund/extractors/__init__.py`
- `tests/fund/extractors/test_manager_ownership.py`
- `tests/fixtures/fund/extractors/manager_ownership/**`

### 文档同步文件

实现通过后按仓库规则同步：

- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control.md`

### 禁止触碰

- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/documents/**`
- `fund_agent/fund/pdf/**`
- `fund_agent/fund/data/nav_data.py`
- `§10` 份额变动 extractor
- P2 分析、判断、审计逻辑

## 4. 输出契约裁决

- `manager_strategy_text`
  - 来源：`§4`
  - 最低输出：策略摘要原文、风格定位原文、后市展望原文
  - 缺失时返回 `missing`
- `turnover_rate`
  - 来源：`§8`
  - 最低输出：年度换手率与披露口径
  - 命中时必须带 anchor
  - 当前不做同类中位数估算；未披露时返回 `missing`
- `manager_alignment`
  - 来源：`§9`
  - 最低输出：基金经理/从业人员持有本基金的原始披露
  - 只输出原始数据，不输出红黄绿判断
- `holder_structure`
  - 来源：`§9`
  - 最低输出：机构投资者、个人投资者持有比例或份额
  - 缺失时返回 `missing`

## 5. Root Cause 裁决

`P1-S6` 当前要关闭的是 `§4/§8/§9` 仍无 capability extractor 的缺口：

1. `StructuredFundDataBundle` 计划中的 4 个数据项尚无结果模型承载。
2. 当前 capability 层没有 `§4/§8/§9` 规则化抽取入口。
3. 换手率、持有人结构和持有披露均会被后续 P2 成本、言行一致性、风险检查复用，必须先以带 anchor 的原始数据形式冻结。

## 6. 当前结论

- baseline reconciliation 结论：`pass`
- `P1-S6` 可以进入 implementation
- 本轮不接受主观 NLP 总结、跨章节估算或投资判断。
