# P1-S7 基线对账裁决

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S7 持仓快照与份额变动
> 分支：`chore/reconcile-baseline`
> 当前 gate：`P1-S7 implementation + review`
> 上一 accepted slice commit：`18566f9` (`gateflow: accept P1 P1-S6`)

## 1. 当前入口

- `docs/implementation-control.md` 当前 gate 已推进到 `P1-S7 implementation + review`。
- `docs/reviews/p1-plan-2026-05-17.md` 要求本 slice 落地：
  - `holdings_snapshot`
  - `share_change`
- 本 slice 只做 `§8/§10` 原始数据抽取，不做行业人工映射、不做资金流向判断、不做投资结论。

## 2. 当前基线事实

- 已有稳定输入：
  - `ParsedAnnualReport`
  - `ParsedAnnualReport.get_section_text(section_id)`
  - `ParsedAnnualReport.tables`
  - `ParsedTable.page_number`
  - `ParsedTable.table_index`
  - `EvidenceAnchor`
  - `ExtractedField`
- 已完成 extractor：
  - `extract_profile(report)` 覆盖 `§1/§2`
  - `extract_performance(report)` 覆盖 `§3`
  - `extract_manager_ownership(report)` 覆盖 `§4/§8/§9`
- 当前尚未存在：
  - `fund_agent/fund/extractors/holdings_share_change.py`
  - `HoldingsShareChangeExtractionResult`
  - `tests/fund/extractors/test_holdings_share_change.py`
  - `tests/fixtures/fund/extractors/holdings_share_change/**`

## 3. 范围裁决

### Allowed files/modules

- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/holdings_share_change.py`
- `fund_agent/fund/extractors/__init__.py`
- `tests/fund/extractors/test_holdings_share_change.py`
- `tests/fixtures/fund/extractors/holdings_share_change/**`

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
- 其他 extractor
- P2 分析、判断、审计逻辑

## 4. 输出契约裁决

- `holdings_snapshot`
  - 来源：`§8`
  - 最低输出：前十大重仓股；行业分布有披露则输出，否则显式 `missing`
  - 表格命中必须使用表格型 anchor：至少 `page_number`、`table_id`、`row_locator`
- `share_change`
  - 来源：`§10`
  - 最低输出：期初份额、期末份额、净变动
  - 命中时必须带表格型 anchor

## 5. Root Cause 裁决

`P1-S7` 当前要关闭的是 `§8/§10` 表格型数据仍无 capability extractor 的缺口：

1. 当前 `ParsedAnnualReport.tables` 已可承载表格，但 extractor 层尚未消费它。
2. 前十大重仓和份额变动是 P2 言行一致性、Beta 计算和投资者获得感 fallback 的输入。
3. 表格证据锚点必须先在 P1 锁定，否则后续数值判断无法满足可溯源约束。

## 6. 当前结论

- baseline reconciliation 结论：`pass`
- `P1-S7` 可以进入 implementation
- 若行业分布只能靠人工解释或外部映射得到，本 slice 必须退化为 `missing`，不能硬编码行业映射。
