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
from fund_agent.fund.data_extractor import FundDataExtractor
from fund_agent.fund.analysis import (
    analyze_investor_experience,
    calculate_r_abc_from_bundle,
    check_consistency,
    judge_alpha_nature,
    run_checklist,
    run_risk_checks,
    run_stress_test,
)
from fund_agent.fund.audit import ProgrammaticAuditInput, run_programmatic_audit

repository = FundDocumentRepository()
report = await repository.load_annual_report("110011", 2024)
profile = extract_profile(report)
performance = extract_performance(report)
manager_ownership = extract_manager_ownership(report)
holdings_share_change = extract_holdings_share_change(report)

data_extractor = FundDataExtractor()
bundle = await data_extractor.extract("110011", 2024)
rabc = calculate_r_abc_from_bundle(bundle, equity_position="80%")
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

`FundDataExtractor.extract()` 返回 `StructuredFundDataBundle`，当前聚合 P1 已接受的 12 项结构化数据，并附带净值数据读取结果。它只做 orchestration，不直接读文件、不直接写缓存。

`calculate_r_abc_from_bundle()` 返回 `RabcAttribution`，当前覆盖模板第 2 章“R=A+B-C 收益归因”的单期计算：

- `R`：基金净值增长率，来自 `nav_benchmark_performance.nav_growth_rate`
- `B`：业绩比较基准收益率 × 显式传入的股票仓位
- `A`：`R - B`
- `C`：管理费 + 托管费 + 换手率 × `0.3%`
- `net_excess_return`：`A - C`

P1 当前尚未稳定抽取股票仓位，因此调用方必须显式传入 `equity_position`；缺少股票仓位或关键子字段时，函数返回 `missing` 状态，不静默套用假设。

`calculate_r_abc_series()` 支持对 `1y / 3y / 5y` 等多个周期按同一公式批量计算，输出顺序与输入顺序一致。

`judge_alpha_nature()` 返回 `AlphaJudgment`，当前覆盖模板第 2 章“超额收益性质判断”：

- `structural`：多年度为正、牛熊环境都为正，且存在明确来源解释
- `partial_structural`：正 Alpha 较多或部分跨环境成立，但证据不完整
- `cyclical`：正 Alpha 集中在少数时期，更接近阶段性风格顺风
- `not_applicable`：纯指数基金不做结构性/阶段性超额判断
- `insufficient_data`：有效观察期不足，不强行判断

市场环境和来源解释强度必须由调用方显式提供；当前模块不从收益结果中反推市场环境，也不猜测基金经理能力来源。

`check_consistency()` 返回 `ConsistencyCheckResult`，当前覆盖模板第 3 章“言行一致性检验”的 4 个维度：

- 投资风格：§4 风格宣称 vs 显式实际持仓风格
- 行业偏好：§4 行业宣称 vs §8 行业分布
- 仓位管理：§4 仓位策略 vs 显式实际股票仓位
- 换手水平：§4 持有周期/换手宣称 vs §8 换手率

P1 当前尚未稳定抽取实际持仓风格和股票仓位，因此这两个实际值必须由调用方显式传入；缺失时对应维度返回 `insufficient_data`。

`analyze_investor_experience()` 返回 `InvestorExperienceResult`，当前覆盖模板第 4 章“投资者获得感”：

- `behavior_gap`：行为损益，公式为投资者实际收益率减基金产品收益率
- `fund_flow`：基于 `§10` 份额净变动和产品收益方向判断追涨、抄底、流出或正常
- `status`：`positive / neutral / negative / insufficient_data`

投资者收益率缺失时返回 `missing`，不静默估算；份额变动子字段缺失时资金流向返回 `missing`。

`run_risk_checks()` 返回 `RiskCheckResult`，当前覆盖模板第 6 章“核心风险与否决项”的 5 项检查：

- 清盘风险：基金规模 `< 5000 万元`
- 基金经理任期：管理本基金 `< 6 个月`
- 严重风格漂移：言行一致性检验红灯
- 费率远超同类：总费率 `> 同类中位数 × 2`
- 跟踪误差过大：指数基金跟踪误差 `> 2%`

基金经理任期、同类总费率中位数和跟踪误差必须由调用方显式提供；缺失时对应项返回 `insufficient_data`。

`run_stress_test()` 返回 `StressTestResult`，当前覆盖模板第 6 章“压力测试”：

- 固定模拟 `-20% / -40% / -60%` 三个场景
- 按基金类型应用 `preferred_lens` 阈值：
  - 指数基金：`-30% / -50% / -70%`
  - 主动基金：`-25% / -45% / -65%`
  - 债券基金：`-5% / -10% / -20%`
  - 指数增强：`-25% / -45% / -60%`
  - QDII：`-35% / -55% / -75%`
  - FOF：`-20% / -40% / -55%`
- 输出每个场景的账户余额、浮亏金额、压力等级和承受能力状态

投入金额和最大可承受亏损比例必须由调用方显式提供；缺少最大可承受亏损比例时只输出浮亏，不猜测用户能否承受。

`run_checklist()` 返回 `ChecklistResult`，当前覆盖 `docs/design.md` 第 4.6 节“买入前检查清单”的 7 个问题：

- 超额收益能覆盖成本吗：消费 `RabcAttribution.net_excess_return`
- 基金经理跟我一条心吗：消费 §9 `manager_alignment` 原始持有披露
- 投资者真的赚到钱了吗：消费 `InvestorExperienceResult`
- 说的和做的一样吗：消费 `ConsistencyCheckResult`
- 这只基金不死吗：消费 `RiskCheckResult`
- 当前估值处于什么位置：消费调用方显式传入的 `valuation_state`
- 这笔钱 3-4 年内不会用吗：消费调用方显式传入的 `money_horizon` 或资金不用年限

检查清单只输出 `green / yellow / red / gray` 和 `pass / watch / block / insufficient_data`，不输出买入、卖出、仓位比例或收益预测。估值和资金期限缺失时输出灰灯，不猜测。

`run_programmatic_audit()` 返回 `ProgrammaticAuditResult`，当前覆盖 `docs/design.md` 第 5.2 节 MVP 程序审计规则：

- `P1`：报告章节结构不匹配
- `P2`：章节内容过短
- `P3`：缺少证据与出处或证据锚点
- `L1`：R=A+B-C 数值计算不闭合
- `R1`：检查清单信号与规则不一致
- `R2`：最终判断与检查清单信号矛盾

程序审计只消费已渲染 Markdown、`RabcAttribution`、`ChecklistResult` 和显式最终判断，不读取年报、PDF 或外部数据。上述输入是当前 MVP 审计 gate 的必需输入；缺少报告、R=A+B-C 结构化结果、检查清单或最终判断时，审计返回失败，不把未执行的规则伪装成通过。

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
- `data/`：外部数据适配器。当前包含 `FundNavDataAdapter` 与自身 `nav_cache`。
- `extractors/`：章节级结构化提取能力。当前已落地基础画像、`§3` 表现、管理人/持有人、持仓/份额 extractor。
- `data_extractor.py`：P1 façade，聚合文档仓库、净值适配器和章节 extractor。
- `fund_type.py`：基金类型识别规则，供 extractor 先行消费。
- `analysis/`：分析计算模块。当前包含 `r_abc.py`、`alpha_judge.py`、`consistency_check.py`、`investor_return.py`、`risk_check.py` 与内部比例解析 helper，只消费 P1/P2 结构化数据和显式判断证据，不直接读取年报文件。
- `pdf/`：底层 PDF helper。当前包含：
  - `downloader.py`：仅供仓库内部使用的 PDF 下载 helper，会写入本地缓存
  - `parser.py`：PDF 全文、表格与章节定位原型
- `audit/`：程序审计规则。当前包含 `audit_programmatic.py`，执行 P1/P2/P3/L1/R1/R2。
- `template/`：后续模板能力的扩展位置

## 当前边界

- 当前只支持 `annual_report`。
- 当前稳定 extractor 边界是 `§1/§2/§3/§4/§8/§9/§10`。
- 当前基础画像只覆盖 `basic_identity`、`product_profile`、`benchmark`、`fee_schedule` 四类输出。
- 当前 `§3` 表现只覆盖 `nav_benchmark_performance` 与 `investor_return` 两类输出。
- 当前管理人/持有人 extractor 只覆盖 `manager_strategy_text`、`turnover_rate`、`manager_alignment`、`holder_structure` 四类输出。
- 当前持仓/份额 extractor 只覆盖 `holdings_snapshot` 与 `share_change` 两类输出。
- `data_extractor.py` façade 已接入当前 12 项结构化数据；`structured_data` 当前以 `StructuredFundDataBundle` dataclass 表达，不额外物化 SQLite 表。
- 当前 `analysis/r_abc.py` 实现 R=A+B-C 单期与多周期归因。
- 当前 `analysis/alpha_judge.py` 实现结构性/阶段性超额规则判断，不输出持有或替换结论。
- 当前 `analysis/consistency_check.py` 实现言行一致性 4 维度信号，不猜测基金经理动机或实际风格。
- 当前 `analysis/investor_return.py` 实现行为损益和份额变动趋势判断，不分析具体投资者交易行为。
- 当前 `analysis/risk_check.py` 实现 5 项否决条件检查，不把缺失输入强行判为通过或否决。
- 当前 `analysis/risk_check.py` 同时实现压力测试，按基金类型阈值为固定下跌场景分级，不预测风险发生概率。
- 当前 `analysis/checklist.py` 实现 7 问题检查清单，消费分析结果和显式用户输入，不读取外部数据。
- 当前 `audit/audit_programmatic.py` 实现 MVP 程序审计，不调用 LLM 或证据复核。
- `parser.py` 已具备 `§3` 定位修复，但真实样本扩展和更多章节/表格抽取仍在后续 slice 完成。
