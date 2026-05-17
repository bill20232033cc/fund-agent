# Fund Capability

`fund_agent/fund` 是基金分析 Capability 层，负责承载基金领域知识、年报解析规则和模板取证输入，不负责 UI、Service、Runtime 或 Engine。

## 当前实现

当前已经落地的稳定公共契约包含：

```python
from fund_agent.fund.documents import FundDocumentRepository
from fund_agent.fund.extractors import (
    extract_holdings_share_change,
    extract_manager_ownership,
    extract_performance,
    extract_profile,
)

repository = FundDocumentRepository()
report = await repository.load_annual_report("110011", 2024)
profile = extract_profile(report)
performance = extract_performance(report)
manager_ownership = extract_manager_ownership(report)
holdings_share_change = extract_holdings_share_change(report)
```

`load_annual_report()` 返回 `ParsedAnnualReport`，包含：

- `key`：基金代码、年份和 `annual_report` 文档类型
- `raw_text`：年报全文文本
- `sections`：章节索引，供后续模板第 2 章 `R=A+B-C` 和第 4 章“投资者获得感”提取复用
- `tables`：年报表格的结构化结果

`extract_profile()` 返回 `ProfileExtractionResult`，当前只覆盖模板第 1 章“这只基金到底是什么产品”的最小数据底座：

- `basic_identity`：基金名称、代码、披露类别、规模、基金经理，以及稳定输出 `classified_fund_type` / `classification_basis`
- `product_profile`：`§2` 中的投资目标、投资范围、投资策略
- `benchmark`：`§2` 中的业绩比较基准文本
- `fee_schedule`：`§2` 中的管理费、托管费

`extract_performance()` 返回 `PerformanceExtractionResult`，当前覆盖模板第 2 章“R=A+B-C 收益归因”和第 4 章“投资者获得感”的最小数据底座：

- `nav_benchmark_performance`：`§3` 中的 `nav_growth_rate`、`benchmark_return_rate`
- `investor_return`：`§3` 中的投资者收益率三态输出
  - `direct`：直接披露
  - `estimated`：`§3` 明确标注为估算口径披露
  - `missing`：当前未披露，显式保留后续 fallback 入口

`extract_manager_ownership()` 返回 `ManagerOwnershipExtractionResult`，当前覆盖模板第 2 章“C 成本侵蚀”、第 3 章“基金经理画像与言行一致性”和第 6 章“核心风险与否决项”的最小数据底座：

- `manager_strategy_text`：`§4` 中的策略摘要、风格定位、后市展望原文
- `turnover_rate`：`§8` 中的年度换手率与披露口径
- `manager_alignment`：`§9` 中的基金经理/从业人员持有原始披露，当前不输出好坏判断
- `holder_structure`：`§9` 中的机构/个人持有人结构

`extract_holdings_share_change()` 返回 `HoldingsShareChangeExtractionResult`，当前覆盖模板第 3 章“实际投资行为”和第 4 章“投资者获得感”的最小数据底座：

- `holdings_snapshot`：`§8` 表格中的前十大重仓，以及已披露的行业分布
- `share_change`：`§10` 表格中的期初份额、期末份额、净变动

所有关键字段都通过 `EvidenceAnchor` 记录 `document_year`、`section_id`、`row_locator` 和命中原文，供后续证据锚点渲染使用。

仓库层位于 `fund_agent/fund/documents/`：

- `models.py`：`DocumentKey`、`ParsedAnnualReport`、`ReportSection`、`ParsedTable`
- `repository.py`：对外唯一公开读取入口 `FundDocumentRepository`
- `adapters/annual_report_pdf.py`：把底层 PDF helper 适配为统一仓库返回值

基础画像 extractor 位于 `fund_agent/fund/extractors/`：

- `models.py`：`EvidenceAnchor`、`ExtractedField`、`ProfileExtractionResult`、`PerformanceExtractionResult`、`ManagerOwnershipExtractionResult`、`HoldingsShareChangeExtractionResult`
- `profile.py`：`§1/§2` 的基础画像抽取
- `performance.py`：`§3` 的净值表现与投资者收益率抽取
- `manager_ownership.py`：`§4/§8/§9` 的管理人文本、换手率、持有披露与持有人结构抽取
- `holdings_share_change.py`：`§8/§10` 的持仓快照与份额变动表格抽取
- `__init__.py`：当前公开导出 `extract_profile`、`extract_performance`、`extract_manager_ownership`、`extract_holdings_share_change`

基金类型识别位于 `fund_agent/fund/fund_type.py`：

- 当前标准标签：`index_fund`、`active_fund`、`bond_fund`、`enhanced_index`、`qdii_fund`、`fof_fund`
- 当前只基于 `§1/§2` 的名称、类别、基准、投资范围做规则识别
- 分类结果通过 `FundTypeClassification(classified_fund_type, classification_basis)` 输出
- 当前实现明确遵守“基金类型判断优先于通用分析”，即先分类，再构造 `basic_identity`

当前边界要求：

- 业务调用方只通过 `FundDocumentRepository.load_annual_report(...)` 读取年报。
- 业务调用方若需要基础画像，只消费 `extract_profile(report)` 的结构化结果，不直接复用正则规则。
- `fund_agent/fund/pdf/*` 只作为仓库内部 helper / adapter，允许返回本地 `Path`，但这不是上层公共契约。
- `ParsedAnnualReport` 是后续各章节 extractor 的统一输入；当前稳定 extractor 已扩展到 `§1/§2/§3/§4/§8/§9/§10`。
- `extract_profile()` 当前不应用 `preferred_lens`，也不输出任何投资结论。
- `extract_performance()` 当前不跨章节做复杂 fallback，不引入 `§10`、净值序列或任何 P2 分析公式。
- `extract_manager_ownership()` 当前只抽原始披露，不输出言行一致性、利益一致性或成本判断。
- `extract_holdings_share_change()` 当前只抽表格原始披露，不输出持仓集中度、资金流向或投资者收益 fallback。

## 内部分层

- `documents/`：公共契约与仓库实现。上层应通过这里读取基金文档。
- `extractors/`：章节级结构化提取能力。当前已落地基础画像、`§3` 表现、管理人/持有人、持仓/份额 extractor。
- `fund_type.py`：基金类型识别规则，供 extractor 先行消费。
- `pdf/`：底层 PDF helper。当前包含：
  - `downloader.py`：仅供仓库内部使用的 PDF 下载 helper，会写入本地缓存
  - `parser.py`：PDF 全文、表格与章节定位原型
- `analysis/`、`audit/`、`data/`、`template/`：后续分析、审计、数据和模板能力的扩展位置

## 当前边界

- 当前只支持 `annual_report`。
- 当前稳定 extractor 边界是 `§1/§2/§3/§4/§8/§9/§10`。
- 当前基础画像只覆盖 `basic_identity`、`product_profile`、`benchmark`、`fee_schedule` 四类输出。
- 当前 `§3` 表现只覆盖 `nav_benchmark_performance` 与 `investor_return` 两类输出。
- 当前管理人/持有人 extractor 只覆盖 `manager_strategy_text`、`turnover_rate`、`manager_alignment`、`holder_structure` 四类输出。
- 当前持仓/份额 extractor 只覆盖 `holdings_snapshot` 与 `share_change` 两类输出。
- `data_extractor.py` façade 仍未接入；当前不提前冻结 `structured_data` 缓存。
- `parser.py` 已具备 `§3` 定位修复，但真实样本扩展和更多章节/表格抽取仍在后续 slice 完成。
