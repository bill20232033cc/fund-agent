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
from fund_agent.fund.template import (
    TemplateRenderInput,
    load_template_contract_manifest,
    render_template_report,
    resolve_preferred_lens,
)

repository = FundDocumentRepository()
report = await repository.load_annual_report("110011", 2024)
profile = extract_profile(report)
performance = extract_performance(report)
manager_ownership = extract_manager_ownership(report)
holdings_share_change = extract_holdings_share_change(report)

data_extractor = FundDataExtractor()
bundle = await data_extractor.extract("110011", 2024)
rabc = calculate_r_abc_from_bundle(bundle, equity_position="80%")
manifest = load_template_contract_manifest()
chapter_lens = resolve_preferred_lens(chapter_id=2, fund_type="active_fund")
```

`load_annual_report()` 返回 `ParsedAnnualReport`，包含：

- `key`：基金代码、年份和 `annual_report` 文档类型
- `raw_text`：年报全文文本
- `sections`：章节索引，供后续模板第 2 章 `R=A+B-C` 和第 4 章“投资者获得感”提取复用
- `tables`：年报表格的结构化结果

年报 PDF 获取由 documents 层内部的来源编排器完成，调用方不感知具体下载源。当前生产默认来源仍是 Eastmoney/akshare 包装器；来源优先级、fallback 和 timeout/retry 配置边界只存在于 Fund Capability 内部，不暴露给 Service、UI、Engine 或 CLI。

`extract_profile()` 返回 `ProfileExtractionResult`，当前只覆盖模板第 1 章“这只基金到底是什么产品”的最小数据底座：

- `basic_identity`：基金名称、代码、披露类别、规模、基金经理，以及稳定输出 `classified_fund_type` / `classification_basis`
- `product_profile`：`§2` 中的投资目标、风格定位、投资范围、投资策略
- `benchmark`：`§2` 中的业绩比较基准文本
- `fee_schedule`：`§2` 中的管理费、托管费

真实年报的 `§2` 常把“基金名称 / 投资目标”等首个键值对放在表头中，因此当前 `extract_profile()` 会同时读取键值型表头和数据行，并把表格页码、表 ID 写入 `EvidenceAnchor`。

`extract_performance()` 返回 `PerformanceExtractionResult`，当前覆盖模板第 2 章“R=A+B-C 收益归因”和第 4 章“投资者获得感”的最小数据底座：

- `nav_benchmark_performance`：`§3` 中的 `nav_growth_rate`、`benchmark_return_rate`；当前支持“阶段 / 份额净值增长率 / 业绩比较基准收益率”表格，并优先读取“过去一年”行
- `investor_return`：`§3` 中的投资者收益率三态输出
  - `direct`：直接披露
  - `estimated`：`§3` 明确标注为估算口径披露
  - `missing`：当前未披露，显式保留后续 fallback 入口

`extract_manager_ownership()` 返回 `ManagerOwnershipExtractionResult`，当前覆盖模板第 2 章“C 成本侵蚀”、第 3 章“基金经理画像与言行一致性”和第 6 章“核心风险与否决项”的最小数据底座：

- `manager_strategy_text`：`§4` 中的策略摘要、后市展望原文；当前支持显式冒号行和“报告期内基金投资策略和运作分析”等编号标题后的正文块
- `turnover_rate`：`§8` 中的年度换手率与披露口径
- `manager_alignment`：`§9` 中的基金经理/从业人员持有原始披露，当前支持表格披露且不输出好坏判断
- `holder_structure`：`§9` 中的机构/个人持有人结构；当前支持持有人结构表跨页组表头

`extract_holdings_share_change()` 返回 `HoldingsShareChangeExtractionResult`，当前覆盖模板第 3 章“实际投资行为”和第 4 章“投资者获得感”的最小数据底座：

- `holdings_snapshot`：`§8` 表格中的前十大重仓，以及已披露的行业分布
- `share_change`：`§10` 表格中的期初份额、期末份额、净变动；当前支持申购/赎回拆分表，并在缺少净变动行时用期末减期初计算

`FundDataExtractor.extract()` 返回 `StructuredFundDataBundle`，当前聚合 P1 已接受的 12 项结构化数据，并附带净值数据读取结果。它只做 orchestration，不直接读文件、不直接写缓存。

`run_extraction_snapshot()` 返回 `SnapshotRunResult`，当前覆盖 P4-S1 精选基金池字段级抽取快照：

- 输入显式接收 `fund_code`、`report_year`、`source_csv`、`run_id`、输出目录和 `force_refresh`
- 读取 `docs/code_20260519.csv` 的“基金名称 / 基金代码 / 类别”三列，并校验名称非空、6 位代码、类别非空和重复代码
- 只通过 `FundDataExtractor.extract(...)` 获取结构化数据包，不直接读取 PDF、cache 或底层解析文件
- 将 `StructuredFundDataBundle` 拆成 14 个字段级记录：`basic_identity`、`product_profile`、`benchmark`、`fee_schedule`、`classified_fund_type`、`nav_benchmark_performance`、`investor_return`、`manager_strategy_text`、`turnover_rate`、`manager_alignment`、`holder_structure`、`holdings_snapshot`、`share_change`、`nav_data`
- 每条记录包含 `comparable_values`，只暴露 correctness 可直接比较的白名单子字段；当前覆盖 `basic_identity`、`benchmark`、`nav_benchmark_performance` 和 `classified_fund_type` 的稳定标量子字段
- 输出 `snapshot.jsonl`、`summary.md` 和 `errors.jsonl`；单只基金失败时继续后续基金并记录错误
- snapshot 只记录当前 extractor 的真实输出，不为特定基金覆盖字段值；`004393` 曾被误判为 `index_fund` 的问题已在 P4-S3a 修复为 `active_fund`

`run_extraction_score()` 返回 `ExtractionScoreResult`，当前覆盖 P4-S2 字段级评分和 P4-R10 correctness 最小闭环：

- 只消费 P4-S1 `snapshot.jsonl`，不读取 PDF、cache 或文档仓库
- 按代码同源的 `field_name` 映射 P0/P1/P2 优先级
- 输出字段级 `field_group`、`field_name`、`priority`、`records`、`coverage_rate`、`traceability_rate` 和 `status`
- 同时输出单基金 `fund_scores`，汇总每只基金的 P0/P1 状态与失败字段，避免字段聚合均值掩盖单只基金不可用问题
- 同时输出单基金 `fund_quality`，从 snapshot 同源派生 App 类别匹配、`preferred_lens` 可解析状态、字段缺失率和缺失 P0/P1 字段；同一基金多行 `app_category` 或 `classified_fund_type` 冲突时显式标记，不取第一行静默通过
- 显式提供 `errors_path` 时，同时输出 `failed_funds`，把 `errors.jsonl` 中完全抽取失败的基金带入后续 gate accounting
- 阈值显式配置：pass 为 coverage/traceability 均不低于 90%，watch 为均不低于 70%，其余 fail
- 可选读取 strict `golden-answer.json` 执行 correctness，比对范围只包括 snapshot `comparable_values` 显式暴露的可比 golden 子字段；只有白名单字段/子字段被 snapshot 明确标记缺失时才进入 mismatch，skipped 和 unavailable 不进分母
- 输出 `score.json`、`score.md` 和 `golden_set.json`

`run_golden_prefill()` 返回 `GoldenPrefillResult`，当前用于生成 correctness golden answer 人工复核底稿：

- 读取 `docs/golden-answer-template.md` 中的基金代码和字段行
- 只通过 `FundDataExtractor.extract(...)` 获取结构化数据包，不直接读取 PDF、cache 或底层解析文件
- 自动填入 `expected_value`、`confidence` 和 `source`
- 输出 Markdown 底稿；该输出是 silver label，不能直接作为最终 golden answer

`build_golden_answer_json()` 返回 `GoldenAnswerBuildResult`，当前用于把人工审核后的 Markdown 转成 strict JSON：

- 只消费 Markdown，不读取 PDF、cache 或底层解析文件
- 校验有效行必须包含 `expected_value`、`confidence`、`source`
- `confidence` 只允许 `high / medium / low`
- `source` 必须是可复核来源，不能保留 `manual_required`
- 输出 `fund-agent.golden-answer.v1` JSON，供 correctness 自动比对使用
- `load_golden_answer_json()` 读取同一 strict JSON schema，供 Capability 内部比对复用，不重新解析 Markdown

`run_quality_gate()` 返回 `QualityGateResult`，当前用于 P4-S4 报告质量 gate：

- 只消费 `extraction-score` 产出的 `score.json`
- P0 字段 `fail` 触发 `block`
- 单基金 `fund_scores` 中 P0 `fail` 触发带 `fund_code` 的 `block`
- P1 字段 `fail` 触发 `warn`
- correctness 尚未接入时只记录 `FQ0/info`
- correctness 可用且出现明确 mismatch 时触发 `FQ1/block`
- `fund_quality` 中 App 类别与基金类型明确冲突时触发 `FQ1/block`
- `fund_quality.missing_field_rate` 达到 20% 触发 `FQ4/warn`，达到 35% 触发 `FQ4/block`
- `fund_quality.preferred_lens_status` 使用 `resolved / not_applicable / mismatch` 表达模板契约适用性；`mismatch` 触发 `FQ5/block`，`resolved` 和 `not_applicable` 只进入 `quality_gate.json.rule_results`
- FQ5 只消费 `score.json` 中由 CHAPTER_CONTRACT / ITEM_RULE manifest 派生的适用性事实，不解析最终报告 Markdown，也不证明 renderer 已遵守 preferred_lens 或正确渲染/删除 ITEM_RULE 段落
- `failed_funds` 中的完全抽取失败基金触发 `FQ6/block`
- 旧 `score.json` 缺少 `fund_quality` 时只记录 `FQ0/info`，不作为 fatal schema 错误
- 旧 `score.json` 中 `preferred_lens_status=match` 兼容为 `resolved`
- 输出 `quality_gate.json` 和 `quality_gate.md`，其中 `rule_results` 记录未触发 issue 的 FQ5 解释性结果

`run_quality_gate_for_bundle()` 返回 `BundleQualityGateResult`，当前用于 P5-S1 `analyze` 主链路质量保护：

- 输入为 Service 已经取得的 `StructuredFundDataBundle`，不重新调用 `FundDataExtractor.extract(...)`
- 复用 `build_snapshot_records(...)` 把单基金数据包转换为本次运行的 snapshot 记录
- 写出单基金 `snapshot.jsonl`、`score.json`、`score.md`、`golden_set.json`、`quality_gate.json` 和 `quality_gate.md`
- 基金不在精选池 CSV、CSV 不可用或 schema 非法时返回 `not_run_reason`，不伪造 App 类别
- 默认输出目录由 Service 生成唯一 run id 后落在 `reports/quality-gate-runs/<run-id>`，避免覆盖上一轮自动运行

`select_minimal_golden_set()` 从 `docs/code_20260519.csv` 选择最小 golden set：

- 固定包含 `004393`
- 覆盖黄金类、海外股票类、海外债券/稳健类、国内债券类，以及额外一只国内股票类
- 暂时排除货币基金类，作为当前 8 章模板适配度不足的 edge case 记录

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

- 投资风格：§2 产品风格定位 vs 显式实际持仓风格；缺少 §2 定位时回退到 §4 策略摘要
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
- `P3`：缺少证据与出处、全局证据锚点或章节内最小证据行
- `C2`：确定性 CHAPTER_CONTRACT 契约不一致，包括 required_output_items marker 缺失、must_not_cover 禁止 marker 命中或章节块元数据不一致
- `L1`：R=A+B-C 数值计算不闭合
- `R1`：检查清单信号与规则不一致
- `R2`：最终判断与检查清单信号矛盾

程序审计只消费已渲染 Markdown、`RenderedChapterBlock`、`RabcAttribution`、`ChecklistResult` 和显式最终判断，不读取年报、PDF 或外部数据。`chapter_blocks` 可显式传入；缺省时审计会按 `CHAPTER_CONTRACT` 标题从 `report_markdown` fail-closed 切分。上述输入是当前 MVP 审计 gate 的必需输入；缺少报告、R=A+B-C 结构化结果、检查清单或最终判断时，审计返回失败，不把未执行的规则伪装成通过。

C2 当前只做确定性 marker / 元数据检查，不调用 LLM，不判断语义型章节越界，也不验证证据是否支撑断言；证据精确性与证据匹配仍属于 E1/E2/E3 后续审计。

`render_template_report()` 返回 `TemplateRenderResult`，当前覆盖 `docs/design.md` 第 3.1 节 8 章模板渲染：

- 输入契约是 `TemplateRenderInput`，显式聚合 `StructuredFundDataBundle`、`RabcAttribution`、`AlphaJudgment`、`ConsistencyCheckResult`、`InvestorExperienceResult`、`RiskCheckResult`、`StressTestResult`、`ChecklistResult`、`final_judgment` 和可选 `current_stage`
- 输出 `report_markdown`，固定包含模板第 0-7 章：投资要点概览、产品本质、R=A+B-C、基金经理画像、投资者获得感、当前阶段、核心风险、最终判断；章节标题由 `CHAPTER_CONTRACT` manifest 提供
- 输出 `audit_input`，可直接传给 `run_programmatic_audit()`，其中携带 `report_markdown`、`chapter_blocks`、`rabc_attributions`、`checklist_result` 和 `final_judgment`
- 输出 `evidence_anchors`，并在报告中渲染章节内 `> 📎 证据：年报{年份}§{章节} ...` 与附录 `证据与出处`
- 输出 `chapter_blocks`，每个 `RenderedChapterBlock` 包含 `chapter_id`、`title`、`heading`、`markdown`、`body_markdown` 和对应 `ChapterContract`
- `get_template_chapter_heading(chapter_id)` 按 manifest 返回 `# {chapter_id}. {title}`；`split_rendered_chapter_blocks(report_markdown)` 按当前模板标题切分报告，并在空文本、缺章、重复、乱序、越界、标题不匹配或非模板一级标题时抛出 `ValueError`
- 年报附录锚点按 `年报{年份}§{章节}表{编号}行{行号}` 输出；缺少表格、行定位或章节时显式写 `未定位`，页码作为附加位置元数据保留；非年报来源显式输出来源类型，不伪装成年报
- 章节缺少证据锚点时，正文输出数据不足证据行，附录同步输出对应模板章节的缺证条目
- 缺失字段显式写为“未披露”或“数据不足”，不静默省略

当前模板渲染器是 MVP 模板填充，不调用 LLM，不预测未来收益，不输出交易或配置指令。`final_judgment` 只允许 `worth_holding`、`needs_attention`、`suggest_replace` 三类。

`load_template_contract_manifest()` 返回 `TemplateContractManifest`，当前覆盖 `docs/design.md` 第 3.1 节和 `docs/fund-analysis-template-draft.md` 的第 0-7 章 `CHAPTER_CONTRACT`：

- manifest 位于 Capability 层 `fund_agent/fund/template/contracts.py`，自带章节标题，不依赖 renderer 私有 `_CHAPTER_TITLES`
- 每章包含 `narrative_mode`、`must_answer`、`must_not_cover`、`required_output_items` 和 `preferred_lens`
- `preferred_lens` key 只允许当前标准基金类型 `index_fund`、`active_fund`、`bond_fund`、`enhanced_index`、`qdii_fund`、`fof_fund` 和 `default`
- `resolve_preferred_lens(chapter_id, fund_type)` 优先返回精确基金类型 lens，没有精确命中时返回 `default`；章节缺失、基金类型不支持或缺少 fallback 时抛出 `ValueError`
- `validate_template_contract_manifest()` 对章节数量、id 连续性、重复 id、空字段、unsupported lens key 和无 lens fallback 执行 fail-closed 校验
- 当前 CHAPTER_CONTRACT manifest 是可机器消费的契约清单，不改变 `render_template_report()` 的 Markdown 输出结构；FQ5 只使用它派生模板契约适用性，不声明 renderer compliance

`load_template_item_rule_manifest()` 返回 `TemplateItemRuleManifest`，当前覆盖 `docs/fund-analysis-template-draft.md` 已声明的四条 `ITEM_RULE`：

- manifest 位于 Capability 层 `fund_agent/fund/template/item_rules.py`，与 `contracts.py` 平级，不依赖 renderer、audit、Service、Engine、UI 或 CLI
- 当前内置规则全部为 `conditional`，覆盖第 1 章“指数编制规则与成分股”“基金经理投资哲学”和第 2 章“超额收益分年度拆解”“跟踪误差分析”；没有内置 optional 规则
- `evaluate_template_item_rules(fund_type=..., facets=...)` 只按标准基金类型和调用方显式提供的 facet 做确定性触发，不从报告文本推断 facet；已知 facet 与基金类型冲突时抛出 `ValueError`
- `conditional` 未触发时决策为 `delete_segment`；schema 同时支持 `optional`，其缺失策略为 `render_unavailable`
- `rendered_segment_present(markdown, rule)` 只按唯一小节标记做字面量检查，不把“跟踪指数”等普通正文短语当作 ITEM_RULE 段落命中
- 当前 ITEM_RULE manifest 不接入程序审计、质量门禁、Service/UI/CLI，也不读取年报、PDF 或外部数据

所有关键字段都通过 `EvidenceAnchor` 记录 `document_year`、`section_id`、`row_locator` 和命中原文，供后续证据锚点渲染使用。

温度计数据适配器位于 `fund_agent/fund/data/thermometer.py`：

- `FundThermometerAdapter.load_thermometer(...)` 读取有知有行公开数据页，当前默认页面为 `https://youzhiyouxing.cn/data` 和 `https://youzhiyouxing.cn/data/macro`
- 输出 `ThermometerSnapshot`，包含全市场温度、指数温度行、债券温度、10 年期国债收益率、更新时间、来源、缓存命中和 stale 状态
- 缓存位于 `cache/thermometer/thermometer.json`，24 小时内复用 fresh cache；抓取或解析失败时可回退到 7 天内 stale cache；无缓存时返回 `unavailable=True`
- 当前只提供 Capability data adapter，尚未接入 Service、CLI 或检查清单估值状态

仓库层位于 `fund_agent/fund/documents/`：

- `models.py`：`DocumentKey`、`ParsedAnnualReport`、`ReportSection`、`ParsedTable`
- `repository.py`：对外唯一公开读取入口 `FundDocumentRepository`
- `cache.py`：raw PDF 元信息缓存与 parsed report 物化缓存；parsed report 命中前会检查最小正文长度和关键章节集合，避免历史低质量解析物被当作真实年报复用
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
- 当前只基于 `§1/§2` 的名称、类别、投资目标、投资范围、投资策略做规则识别；业绩比较基准只作为输出和依据说明，不单独触发指数基金分类
- 当前支持从 `§2` 键值表读取名称、简称、类别、基准、投资目标、投资范围和投资策略；基金简称中的 QDII 标识会参与分类，债券基金名称优先于混合股票指数基准，避免产品因基准含沪深 300 被误判为指数基金
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
- `extraction_snapshot.py`：P4-S1 字段级抽取快照能力，消费 `FundDataExtractor` 并写出 JSONL/summary/errors。
- `extraction_score.py`：P4-S2 字段级评分与最小 golden set 选择能力，只消费 snapshot JSONL 和精选基金池 CSV。
- `fund_type.py`：基金类型识别规则，供 extractor 先行消费。
- `analysis/`：分析计算模块。当前包含 `r_abc.py`、`alpha_judge.py`、`consistency_check.py`、`investor_return.py`、`risk_check.py` 与内部比例解析 helper，只消费 P1/P2 结构化数据和显式判断证据，不直接读取年报文件。
- `template/`：模板渲染能力。当前包含 `renderer.py`，只消费 P1/P2 结构化结果并输出 8 章 Markdown、章节块与程序审计输入。
- `template/contracts.py`：模板契约能力，维护第 0-7 章 CHAPTER_CONTRACT 机器契约、章节契约读取和基金类型 lens 解析。
- `template/item_rules.py`：模板 ITEM_RULE manifest，维护当前四条 conditional 规则、确定性触发评估和段落标记检查。
- `pdf/`：底层 PDF helper。当前包含：
  - `downloader.py`：仅供仓库内部使用的 PDF 下载 helper，会写入本地缓存
  - `parser.py`：PDF 全文、表格与章节定位原型
- `audit/`：程序审计规则。当前包含 `audit_programmatic.py`，执行 P1/P2/P3/L1/R1/R2。

## 当前边界

- 当前只支持 `annual_report`。
- 当前稳定 extractor 边界是 `§1/§2/§3/§4/§8/§9/§10`。
- 当前基础画像只覆盖 `basic_identity`、`product_profile`、`benchmark`、`fee_schedule` 四类输出。
- 当前 `§3` 表现只覆盖 `nav_benchmark_performance` 与 `investor_return` 两类输出。
- 当前管理人/持有人 extractor 只覆盖 `manager_strategy_text`、`turnover_rate`、`manager_alignment`、`holder_structure` 四类输出。
- 当前持仓/份额 extractor 只覆盖 `holdings_snapshot` 与 `share_change` 两类输出；`share_change` 对多份额列表只显式选择单值列或表头精确基金代码列，无法可靠选择时返回 `missing`，不再按列顺序或 A 类 fallback 默认取值。
- `data_extractor.py` façade 已接入当前 12 项结构化数据；`structured_data` 当前以 `StructuredFundDataBundle` dataclass 表达，不额外物化 SQLite 表。
- `extraction_snapshot.py` 当前记录字段级抽取状态，并通过 `comparable_values` 暴露 correctness 可比子字段白名单；不为特定基金覆盖字段值。
- `extraction_score.py` 当前计算字段级与单基金 coverage / traceability，对 strict golden answer 中 snapshot 可比字段执行 correctness 比对，并可显式消费 `errors.jsonl` 输出 `failed_funds`；旧 snapshot 仅保留 `classified_fund_type.fund_type` 兼容路径。
- `golden_answer.py` 当前构建、读取和校验人工 golden answer strict JSON，不执行 correctness 比对。
- `quality_gate.py` 当前只消费 `score.json`，按字段级、单基金、`fund_quality`、`failed_funds` 和 correctness 质量信号阻断，不读取基金文档，不执行 LLM 审计。
- 当前 `analysis/r_abc.py` 实现 R=A+B-C 单期与多周期归因。
- 当前 `analysis/alpha_judge.py` 实现结构性/阶段性超额规则判断，不输出持有或替换结论。
- 当前 `analysis/consistency_check.py` 实现言行一致性 4 维度信号，不猜测基金经理动机或实际风格。
- 当前 `analysis/investor_return.py` 实现行为损益和份额变动趋势判断，不分析具体投资者交易行为。
- 当前 `analysis/risk_check.py` 实现 5 项否决条件检查，不把缺失输入强行判为通过或否决。
- 当前 `analysis/risk_check.py` 同时实现压力测试，按基金类型阈值为固定下跌场景分级，不预测风险发生概率。
- 当前 `analysis/checklist.py` 实现 7 问题检查清单，消费分析结果和显式用户输入，不读取外部数据。
- 当前 `audit/audit_programmatic.py` 实现 MVP 程序审计，不调用 LLM 或证据复核。
- 当前 `template/contracts.py` 实现第 0-7 章 CHAPTER_CONTRACT manifest、章节契约读取、基金类型 lens 解析和 fail-closed manifest 校验；不运行时解析 Markdown 注释。
- 当前 `template/item_rules.py` 实现 ITEM_RULE manifest、显式基金类型/facet 评估和唯一段落标记检查；不调用 LLM、不读取基金文档、不接入程序审计或质量门禁。
- 当前 `template/renderer.py` 实现 8 章 Markdown 模板渲染，按 CHAPTER_CONTRACT manifest 生成章节标题，并返回可直接用于程序审计的 `ProgrammaticAuditInput` 与 `RenderedChapterBlock` 章节块。
- `parser.py` 已具备 `§3` 定位修复，但真实样本扩展和更多章节/表格抽取仍在后续 slice 完成。
