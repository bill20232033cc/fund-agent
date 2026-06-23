# Fund Agent 能力包

`fund_agent/fund` 是 Agent 层基金领域能力包，负责承载基金领域知识、年报解析规则和模板取证输入，不负责 UI、Service 或 Host 生命周期治理。未来通用 Agent 执行内核落地时必须在本项目内内化 Dayu Engine 稳定能力，不直接依赖外部 `dayu.engine` runtime；`fund_agent/fund` 当前仍保持确定性 Python 能力包形态。

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
from fund_agent.fund.chapter_facts import ChapterFactProvider, project_chapter_facts
from fund_agent.fund.evidence_confirm import (
    EvidenceConfirmReference,
    confirm_projection_evidence,
    confirm_projection_evidence_v2,
)
from fund_agent.fund.evidence_confirm_diagnostics import summarize_evidence_confirm_diagnostics
from fund_agent.fund.evidence_confirm_sources import (
    EvidenceConfirmReferenceBuildRequest,
    build_annual_report_evidence_confirm_references,
)
from fund_agent.fund.evidence_confirm_runner import (
    EvidenceConfirmRepositoryRunRequest,
    run_repository_bounded_evidence_confirm,
)
from fund_agent.fund.evidence_confirm_production import EvidenceConfirmProductionSummary
from fund_agent.fund.evidence_availability import derive_evidence_availability
from fund_agent.fund.chapter_writer import build_chapter_writer_input, write_chapter
from fund_agent.fund.chapter_auditor import ChapterAuditInput, audit_chapter
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
    load_typed_template_contract_manifest,
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
chapter_projection = project_chapter_facts(bundle)
chapter_projection_via_provider = ChapterFactProvider().project(bundle)
evidence_availability = derive_evidence_availability(chapter_projection)
evidence_confirm_result = confirm_projection_evidence(
    chapter_projection,
    (
        EvidenceConfirmReference(
            anchor_id="example-anchor",
            reference_kind="annual_report_excerpt",
            source_kind="annual_report",
            document_year=2024,
            section_id="§3",
            page_number=12,
            table_id=None,
            row_locator="row:1",
            excerpt_text="年报摘录文本",
        ),
    ),
)
evidence_confirm_result_v2 = confirm_projection_evidence_v2(
    chapter_projection,
    (
        EvidenceConfirmReference(
            anchor_id="example-anchor",
            reference_kind="annual_report_excerpt",
            source_kind="annual_report",
            document_year=2024,
            section_id="§3",
            page_number=12,
            table_id=None,
            row_locator="row:1",
            excerpt_text="年报摘录文本",
        ),
    ),
)
evidence_confirm_diagnostic = summarize_evidence_confirm_diagnostics(evidence_confirm_result_v2)
reference_build_result = build_annual_report_evidence_confirm_references(
    EvidenceConfirmReferenceBuildRequest(
        fund_code="110011",
        report_year=2024,
        projection=chapter_projection,
        parsed_report=report,
        source_truth_status="not_proven",
    )
)
repository_run_result = await run_repository_bounded_evidence_confirm(
    EvidenceConfirmRepositoryRunRequest(fund_code="110011", report_year=2024)
)
writer_input = build_chapter_writer_input(chapter_projection, chapter_id=1, mode="prompt_only")
write_result = write_chapter(writer_input, llm_client=None)
if write_result.draft is not None:
    audit_result = audit_chapter(
        ChapterAuditInput(writer_input=writer_input, draft=write_result.draft),
        llm_client=None,
    )
rabc = calculate_r_abc_from_bundle(bundle, equity_position="80%")
manifest = load_template_contract_manifest()
typed_manifest = load_typed_template_contract_manifest()
chapter_lens = resolve_preferred_lens(chapter_id=2, fund_type="active_fund")
```

`load_annual_report()` 返回 `ParsedAnnualReport`，包含：

- `key`：基金代码、年份和 `annual_report` 文档类型
- `raw_text`：年报全文文本
- `sections`：章节索引，供后续模板第 2 章 `R=A+B-C` 和第 4 章“投资者获得感”提取复用
- `tables`：年报表格的结构化结果
- `metadata`：年报来源与缓存来源信息；`metadata.source` 标识当前 EID single-source policy、可用公告/PDF ID 和 fail-closed 分类，`metadata.cache` 标识 parsed report 或 PDF cache 命中来源

年报 PDF 获取由 documents 层内部的来源编排器完成，调用方不感知具体下载源。当前生产默认策略是 EID/证监会资本市场统一信息披露平台 single-source：`selected_source=eid`、`source_mode=single_source_only`、`fallback_enabled=false`。默认来源编排器只构造 EID source，并拒绝多来源构造；Eastmoney、基金公司官网/CDN、CNINFO 只保留为 future candidate / 历史 evidence route，不是当前生产 fallback。EID 请求级 timeout/retry、PDF 文件头校验、原子写入和来源元数据持久化只存在于 Fund 内部，不暴露给 Service、UI、Host、Agent 执行内核或 CLI。来源失败按 `not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error` 显式分类；`not_found` 与 `unavailable` 是 terminal EID source failure，不触发 fallback；EID schema drift、身份矛盾和 PDF 完整性错误会 fail-closed，并在阻断异常中保留来源、类别和原始错误。缓存读取时，documents 层只复用带当前 EID single-source metadata 的 parsed/PDF cache；历史、人工污染、metadata-less 或 Eastmoney/fallback-origin cache 会被忽略而不是删除。正常写入和模型反序列化仍保持来源闭集校验。

`fund_agent/fund/documents/candidates/` 当前承载 Docling / pdfplumber / EID HTML render 候选年报表示的内部 evidence harness。`representation_export.py` 定义 candidate-only manifest、输出 envelope、路径/hash 校验、默认 no-clobber 写入策略、blocked-result 和显式 opt-in 内置 handler 入口；`representation_handlers.py` 提供候选内部 route handlers：Docling handler 仅在调用时 lazy import 并保持本地 artifact / socket-block 约束，pdfplumber handler 只用于候选表示导出，EID HTML render 在未有独立 accepted artifact 前保持 blocked；`representation_models.py` 和 `representation_projection.py` 只把已生成的候选 JSON 投影为 Fund documents 内部 route-neutral dataclass 与 candidate anchor note，不修改公共 `EvidenceAnchor` schema。它们不改变 `FundDocumentRepository` 行为，不写 `cache/pdf`，不从 `fund_agent.fund.documents` 公共入口导出，也不证明 source truth、字段正确性、taxonomy compatibility、parser replacement 或 readiness。显式 staged PDF path 仅能作为已接受 gate evidence 链中的 Fund documents candidate-harness 输入，不能成为 Service、UI、Host、renderer、quality gate 或生产 repository 的文档访问模式。

Docling 架构重定位后，candidate harness 只保留为转换中间态和研究证据入口；它不是结构化基金事实提取层。当前 `fund_agent/fund/processors/` 已落地 no-live Processor/Extractor 契约、`FundProcessorRegistry` 和按基金类型拆分的 `ParsedAnnualReport` processor：`active_fund`、`index_fund`、`enhanced_index`、`bond_fund`、`qdii_fund` 与 `fof_fund` 均支持 `<fund_type> + annual_report + parsed_annual_report.v1`，消费已加载的 `ParsedAnnualReport`，包装现有窄 extractor，输出模板第 1-6 章字段族、公共 `EvidenceAnchor`、source provenance 和 fail-closed 缺口。默认生产 facade 中，`FundDataExtractor.extract()` 对已分类基金类型通过 `FundProcessorRegistry` 投影 `StructuredFundDataBundle`（product_essence / return_attribution / manager_profile / investor_experience / core_risk fallback）；只有 `classified_fund_type` 缺失或非法时保留 direct legacy residual path。S3 新增的 `FundDisclosureDocumentIntermediate` 协议和 `fund_disclosure_dispatch.py` admission helper 只定义受控文档表示进入 Processor 边界前的 fail-closed 判定。S4/S5 的 `FundDisclosureDocument` route 已按六类 `FundType` 拆分 processor：active 保留 `FundDisclosureDocumentProcessor`（processor_id=`active_fund_disclosure.fund_disclosure_document.v1`），index/enhanced_index/bond/QDII/FOF 分别由对应分类型 FDD processor 处理；facade 仍先通过 `FundDocumentRepository` 加载并校验 `ParsedAnnualReport`，再用 parsed report 分类结果构造 `<fund_type> + annual_report + fund_disclosure_document.v1` dispatch key，`FundDisclosureDocumentIntermediate` 不决定基金类型。`disclosure_intermediate=None` 的默认生产路径仍不解析 `fund_disclosure_document.v1`。S6-A 起，processor contract 增加 `FundDisclosureDocumentContentIntermediate` 与 `FundCandidateEvidenceRecord`：candidate-only locator evidence 可作为内部证据记录挂在 `FundFieldFamilyResult.candidate_evidence`，但不进入 `value`，不替代公共 `EvidenceAnchor`，也不满足 `partial` / `accepted`。S6-B 起，`FundDisclosureDocumentProcessor` 为 `product_essence.v1` 选择 section/paragraph/table/cell 层面的 candidate locator evidence；S6-C 起，`FundDisclosureDocumentProcessor` 为 `return_attribution.v1` 选择净值/基准表现、费率、跟踪误差相关的 candidate locator evidence；S6-D 起，`FundDisclosureDocumentProcessor` 为 `manager_profile.v1` 选择基金经理名册、策略/展望、换手率、经理/从业人员持有与持仓快照相关 candidate locator evidence；S6-E 起，`FundDisclosureDocumentProcessor` 为 `investor_experience.v1` 选择投资者实际收益、基金份额持有人结构、基金份额变动、实际申购赎回流量和收益分配相关 candidate locator evidence；S6-F 起，`FundDisclosureDocumentProcessor` 为 `core_risk.v1` 选择风险收益特征、清盘/规模、跟踪误差/偏离、换手/风格漂移和持仓集中相关 candidate locator evidence；S6-G 起，`FundDisclosureDocumentProcessor` 为 `current_stage.v1` 选择当前阶段、基金经理变更、份额/规模变化和持仓/策略变化相关 candidate locator evidence。proof-missing / proof-invalid / candidate-boundary 路径中的 candidate evidence 仍保持 `status="missing"`、`value={}`、`anchors=()`，并以 `candidate_only_not_source_truth` gap 标明不能消费为事实；proof-positive direct route 会清空对应已实现字段族的 `candidate_evidence`。`FundDisclosureDocument` candidate schema 当前只存在于 `fund_agent/fund/documents/candidates/` 内部：记录 EID HTML render candidate 身份、navigation、section、paragraph、table、cell locator、candidate boundary 和 source-failure mapping，并固定 `intermediate_kind="fund_disclosure_document.v1"`。该 schema 不导出到 `fund_agent.fund.documents` 公共入口，不扩展 `EvidenceSourceKind` / `EvidenceAnchor`，不改变 repository/source 行为；processor reachability、S6-A contract、S6-B product essence selector、S6-C return attribution selector、S6-D manager profile selector、S6-E investor experience selector、S6-F core risk selector、S6-G current stage selector，以及 source-truth direct extraction 的单字段族推进都不证明 real-report correctness、字段正确性、parser replacement、golden/readiness 或 release。不能从候选 JSON 直接外推出 CHAPTER_CONTRACT、renderer、quality gate 或 LLM prompt 输入。

Source-truth direct extraction 在该 Processor/Extractor 边界内增加了 `FundDisclosureSourceTruthAdmissionProof` 正向准入证明。`candidate_boundary is None` 是必要条件但不充分；只有 proof-positive、`source_provenance` 有效且 `failure_class` 为空的 `FundDisclosureDocument` content input 可以产出 FDD source-truth public field value。缺少或无效 proof 不产出公共字段值或 anchors；`source_provenance=None` 与非空 `failure_class` 仍是 base admission-layer failure。当前 `product_essence.v1`、`return_attribution.v1`、`manager_profile.v1`、`investor_experience.v1`、`current_stage.v1` 与 `core_risk.v1` 有 FDD source-truth direct extraction，且 direct result 的 `candidate_evidence` 为空；`return_attribution.v1` 的显式 FDD facade route 可把 proof-positive 费率与净值/基准表现投影到 `StructuredFundDataBundle`；`manager_profile.v1` 的显式 FDD facade route 可把 proof-positive `portfolio_managers`、`turnover_rate`、`manager_alignment`、`manager_strategy_text` 和 `holdings_snapshot` 投影到 `StructuredFundDataBundle`。其中 `manager_strategy_text` 只从 `heading_path` 命中策略/展望标题的稳定 paragraph 生成，当前覆盖“投资策略和运作分析”“投资策略和业绩表现说明”“管理人对境外市场走势的简要展望”等普通和 QDII/海外报告标题变体；正文关键词不能自授权生成字段。`investor_experience.v1` 的显式 FDD facade route 可把 proof-positive `investor_return`、`holder_structure` 和 `share_change` 投影到 `StructuredFundDataBundle`。`current_stage.v1` 仅复用既有 public fact shape `basic_identity`、`share_change`、`holdings_snapshot` 与 `portfolio_managers`，不新增 bundle-level `current_stage` 字段，不投影 `StructuredFundDataBundle` 字段，不输出当前阶段语义摘要、市场/估值判断或最终持有/替换判断。`core_risk.v1` 通过 `_CORE_RISK_REQUIRED_TOP_LEVEL` 实现全部五个 required source-truth subvalue：`risk_characteristic_text` 保持既有 `risk_characteristic_text.v1` shape，`liquidation_or_scale_risk`、`tracking_error_or_deviation_risk`、`turnover_or_style_drift_risk` 与 `concentration_risk` 各自通过 direct paragraph/cell 披露抽取为 `core_risk_role_disclosure.v1` subvalue（五键：`schema_version`、`fund_code`、`report_year`、`role`、`risk_disclosure_text`），不内嵌 `source_anchors`。缺失单个 role 时发射 `field_family_partial` gap 并返回 `partial` 状态；冲突披露 emit `ambiguous_table_or_locator`。不再使用 `deferred_role`。显式 FDD facade route 不新增 `StructuredFundDataBundle.core_risk`；只在 product essence 缺少 `risk_characteristic_text` 时复用既有 fallback 投影到 `StructuredFundDataBundle.risk_characteristic_text`。`subscription_redemption` 和 `income_distribution` 仍只作为 `investor_experience.v1` candidate locator roles，不是 public source-truth subvalues。Candidate evidence 继续保持 candidate_only / not_proven / NOT_READY，不扩展 `EvidenceSourceKind` / `EvidenceAnchor`，不改变 repository/source 行为，不授权 Service/UI/Host/renderer/quality-gate consumption、parser replacement、golden/readiness 或 release。

`extract_profile()` 返回 `ProfileExtractionResult`，当前只覆盖模板第 1 章“这只基金到底是什么产品”的最小数据底座：

- `basic_identity`：基金名称、代码、披露类别、规模、基金经理，以及稳定输出 `classified_fund_type` / `classification_basis`
- `product_profile`：`§2` 中的投资目标、风格定位、投资范围、投资策略
- `risk_characteristic_text`：`§2` 中显式披露的风险收益特征，输出 `risk_characteristic_text.v1`，不以 `product_profile.style_positioning` 作为替代
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
- `portfolio_managers`：`§4` 中的基金经理任期列表；当前只在 `§4` 存在编号“基金经理简介”标题且表格具备姓名、职务、任职日期表头时输出 `portfolio_manager_tenure_list.v1`
- `turnover_rate`：`§8` 中的年度换手率与披露口径
- `manager_alignment`：`§9` 中的基金经理/从业人员持有原始披露，当前支持表格披露且不输出好坏判断
- `holder_structure`：`§9` 中的机构/个人持有人结构；当前支持持有人结构表跨页组表头
- 多子字段 extractor 在至少命中一项时保持 `direct` 并保留已抽取原文；策略文本、利益一致性、持有人结构若存在部分子字段缺失，会在 `note` 中标记“部分子字段缺失，仅抽取到部分信息”。换手率以数值为核心字段：数值存在时保持 direct，口径缺失不单独标 partial；仅口径存在时返回 `missing`

`extract_holdings_share_change()` 返回 `HoldingsShareChangeExtractionResult`，当前覆盖模板第 3 章“实际投资行为”和第 4 章“投资者获得感”的最小数据底座：

- `holdings_snapshot`：`§8` 表格中的前十大重仓、`bond_top_holding_row.v1` 前五名债券投资明细、`target_fund_holding_row.v1` 期末投资目标基金明细，以及已披露的行业分布；债券持仓输出为独立 `bond_top_holdings` 子形态，目标基金持仓输出为独立 `target_fund_holdings` 子形态，二者都不复用股票 `top_holdings`
- `share_change`：`§10` 表格中的期初份额、期末份额、净变动；当前支持申购/赎回拆分表，并在缺少净变动行时用期末减期初计算

`FundDataExtractor.extract()` 返回 `StructuredFundDataBundle`。默认 `ParsedAnnualReport` 路径通过 `FundProcessorRegistry` 按 `classified_fund_type` 分派：`active_fund` 走 `ActiveFundAnnualProcessor`，`index_fund`、`enhanced_index`、`bond_fund`、`qdii_fund` 与 `fof_fund` 走对应分类型 processor，并投影 bundle 字段（product_essence / return_attribution / manager_profile / investor_experience / core_risk fallback）；未分类仍保留 direct legacy residual path。S5 起，`extract(..., disclosure_intermediate=...)` 仅提供显式 opt-in 的内部/test facade route：它仍先通过 `FundDocumentRepository` 加载并校验 `ParsedAnnualReport`，从 parsed report 分类基金类型，按 `active_fund`、`index_fund`、`enhanced_index`、`bond_fund`、`qdii_fund` 或 `fof_fund` 进入对应 `fund_disclosure_document.v1` processor，并把 `source_provenance` / `candidate_boundary` 作为 processor input 显式传递；`disclosure_intermediate=None` 的默认生产路径不解析 `fund_disclosure_document.v1`。

当前 `FundDisclosureDocument` candidate schema 与 proof-missing locator evidence 仍是 candidate-only / `not_proven` / `NOT_READY`；S6-A 只新增内部 candidate evidence contract，S6-B/S6-C/S6-D/S6-E/S6-F/S6-G 只分别为 `product_essence.v1`、`return_attribution.v1`、`manager_profile.v1`、`investor_experience.v1`、`core_risk.v1` 与 `current_stage.v1` 生成 candidate locator evidence，不把 candidate evidence 投影进 `StructuredFundDataBundle`，不声明 parser replacement、full correctness、golden/readiness 或 release。Source-truth direct extraction 的当前例外是 proof-positive `product_essence.v1`、`return_attribution.v1`、`manager_profile.v1`、`investor_experience.v1`、`current_stage.v1` 与 `core_risk.v1`；`investor_experience.v1` 只覆盖既有 public/bundle key `investor_return`、`holder_structure` 与 `share_change`，`current_stage.v1` 只覆盖既有 public fact shape `basic_identity`、`share_change`、`holdings_snapshot` 与 `portfolio_managers` 且不投影 bundle，`core_risk.v1` 覆盖全部五个 required source-truth subvalue（`risk_characteristic_text` + 四个 `core_risk_role_disclosure.v1` role key）且不新增 `StructuredFundDataBundle.core_risk`。`subscription_redemption` 与 `income_distribution` 仍不进入 public value。

`portfolio_managers`、`risk_characteristic_text` 等 active fund 已覆盖字段来自 processor 输出而非窄 extractor 透传；`bond_top_holdings` 和 `target_fund_holdings` 仍只作为 `holdings_snapshot.value` 的子形态存在，不是 top-level bundle 字段。`index_profile` 只承载指数画像上下文，`tracking_error` 只承载年报直接披露或后续已接受计算路径形成的跟踪误差；开发覆盖不写入结构化数据包。它只做 orchestration，不直接读文件、不直接写缓存。年报仓库和 PDF 来源失败仍按来源策略向上抛出；仅 NAV provider / cache / akshare 等外部净值数据失败会降级为 `NavDataResult(unavailable=True, records=[])`，让年报字段抽取和 `analyze` / `checklist` 主路径继续运行。

当前 FDD source-truth direct extraction 覆盖 proof-positive `product_essence.v1`、`return_attribution.v1`、`manager_profile.v1`、`investor_experience.v1`、`current_stage.v1` 与 `core_risk.v1`。`candidate_boundary is None` 不等于 source-truth proof；缺少或无效 `FundDisclosureSourceTruthAdmissionProof` 时，`FundDataExtractor.extract(..., disclosure_intermediate=...)` 不会从 FDD input 产出公共字段值或 anchors。`investor_experience.v1` 只发出 `investor_return`、`holder_structure` 与 `share_change`；`current_stage.v1` 只发出 `basic_identity`、`share_change`、`holdings_snapshot` 与 `portfolio_managers`，没有 bundle-level `current_stage` 字段或语义阶段判断；`core_risk.v1` 发出全部五个 required subvalue（`risk_characteristic_text` + 四个 `core_risk_role_disclosure.v1` role key），不再使用 `deferred_role`。`subscription_redemption` 与 `income_distribution` 仍是 candidate-only roles；candidate evidence 仍是 candidate_only / not_proven / NOT_READY，不能被 Service/UI/Host/renderer/quality gate 或 LLM prompt 直接消费为事实。

`project_chapter_facts()` 和 concrete `ChapterFactProvider.project()` 当前把已存在的 `StructuredFundDataBundle` 投影为 `chapter_fact_projection.v1`：

- 只消费内存中的结构化数据包，以及现有 CHAPTER_CONTRACT、preferred_lens 和 ITEM_RULE API
- 输出模板第 0-7 章的 `ChapterFactProjection`、章节 facts、证据锚点、缺失/不可用/不适用语义、分类依据、lens 与 ITEM_RULE 决策
- `classified_fund_type` 缺失或非法时投影为 `unknown`，并跳过 preferred_lens 与 ITEM_RULE 的有效基金类型路径
- facet 行为保持确定性：没有 exact structured evidence 时 `facets=()`，候选 catalog 标签只进入 `non_asserted_facets`，不会传给 ITEM_RULE
- `portfolio_managers` 投影到第 1 章和第 3 章，source field id 为 `structured.portfolio_managers`
- `risk_characteristic_text` 投影到第 1 章和第 6 章，source field id 为 `structured.risk_characteristic_text`
- `holdings_snapshot` 继续作为第 3/5/6 章持仓子形态的唯一来源字段
- `bond_risk_evidence` 的组级 anchors 保留在 value 内部，不展开为普通章节 `ChapterEvidenceAnchor`
- 该能力不读取文档仓库、PDF、cache、source helper、下载器或 parser，不调用 LLM、Service、Host 或 dayu；它不是 writer、auditor、orchestrator 或 `FundToolService`

`AnnualEvidenceScopeRequest`、`AnnualEvidenceLoader` 和 `AnnualEvidenceBundle` 位于 `fund_agent/fund/annual_evidence.py`，当前为 `analyze-annual-period` 提供多年年报证据作用域和年度摘要：

- MVP 作用域要求 `required_years=(target_year,)`，prior 年份只能作为连续 optional 年份，最多 5 年
- 当前年份直接复用 Service 已取得的 `StructuredFundDataBundle`；prior 年份只能通过 `FundDocumentRepository.load_annual_report(...)` 加载
- prior 年份只调用 `extract_profile()`、`extract_manager_ownership()` 和 `extract_holdings_share_change()` 的窄字段抽取，不调用完整 `FundDataExtractor.extract()`
- `not_found` / `unavailable` prior 年份记录为 `gap`；`schema_drift` / `identity_mismatch` / `integrity_error` prior 年份记录为 `failed_closed`
- 可用年度会派生 `fee_schedule_trend`、`turnover_rate_trend`、`share_change_trend`、`holdings_snapshot_trend` 和 `manager_continuity` 等低风险跨年事实，并保留年度 anchor 和 source provenance
- 该能力不新增来源、不启用 fallback、不调用 LLM/provider/Host/dayu，不执行 golden/readiness/score-loop，也不删除或改写缓存

`ChapterFactProvider.project_annual_evidence()` 当前在已有单年 `ChapterFactProjection` 基础上投影 `AnnualEvidenceBundle`：

- 公开章节 id 仍严格为 `0-7`
- 跨年事实只进入模板第 5 章“当前阶段与关键变化”
- 当可用跨年事实存在时，替换单年投影中的 `cross_period_comparison_missing` 缺口；没有可用跨年事实时保持原有单年缺口语义
- 该投影只消费内存中的 `AnnualEvidenceBundle`，不读取文档仓库、PDF、cache、source helper、Service、Host、provider 或 dayu

`fund_agent/fund/template/annual_period_renderer.py` 当前为 `analyze-annual-period` 生成正式多年年报 Markdown 报告：

- 输入只包含 `AnnualEvidenceBundle`、当前年份 8 章报告 Markdown 和显式 quality gate 状态
- 输出包含年度覆盖与来源、跨年关键变化、对当前判断的影响、缺口与降级，并通过稳定 marker 保留当前年份 8 章报告
- `MultiYearAnnualAnalysisResult.report_markdown` 仍保持当前年份报告语义；正式多年报告位于显式 `annual_period_report.report_markdown`
- 缺少 quality gate 状态时输出 `quality_gate_status=not_available`，不声明通过、readiness 或 release 状态
- renderer 不读取文档仓库、PDF、cache、source helper、下载器、provider、LLM、Service、Host、文件系统文档语料或 dayu

`docs/fund-analysis-template-draft.md` canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 当前是 Fund template contract 的 authored truth source。模板层从同一 JSON 生成 untyped 与 typed 两种投影：

- `fund_agent/fund/template/contracts.py` 解析、投影并验证 untyped `TemplateContractManifest`，继续提供 `load_template_contract_manifest()`、`validate_template_contract_manifest()`、`get_chapter_contract()` 和 `resolve_preferred_lens()`
- `fund_agent/fund/template/typed_contracts.py` 从同一 JSON 投影并验证 typed `TypedChapterContract` dataclasses，继续提供 `load_typed_template_contract_manifest()` 和 `get_typed_chapter_contract()`
- 模板文档中的 visible per-chapter `CHAPTER_CONTRACT_REF` 只是非权威引用；结构化 `must_answer`、`must_not_cover`、`required_output_items`、`preferred_lens`、typed ids、Ch2 internal subcontracts、Ch0/Ch7 metadata、Ch3 predicate、missing behavior 和 `audit_focus` 均以 canonical JSON 为准
- typed schema 版本为 `typed_chapter_contract.v1`，公开章节 id 仍严格为 `0-7`
- 第 2 章的 `performance / attribution / cost` 只作为 `chapter_id=2` 内部 `ChapterInternalSubcontract`，不会成为公开章节或 chapter matrix row
- 第 0 章声明 `consumes_chapter_conclusions=(7,)`，且 `independent_action_source=False`，不独立派生动作判断
- `audit_focus` 是 bounded semantic audit 的闭集语义提示；显式传入 typed contract 时只投影到 LLM audit request 和 prompt 语义强调，不能关闭 programmatic blockers、改变阻断等级或修复预算
- `RequiredOutputItem.when_evidence_missing` 当前为第 2/3 章 typed writer path 提供缺证行为数据：第 2 章 R=A+B-C required outputs 缺少同源证据时 `block`，第 3 章策略/实际行为/言行一致性/风格稳定性缺少已复核证据时只允许输出证据缺口，利益一致性缺证时只允许输出下一步最小验证问题
- loader 使用 strict parser/projection validation 校验当前 `must_answer / must_not_cover / required_output_items` 文本和 stable ids；template JSON 漂移、未知 requirement id 或 stale `source_manifest` 会 fail-closed，而不是 fuzzy、substring、embedding 或 LLM 匹配

`fund_agent/fund/evidence_availability.py` 当前提供 additive same-source `EvidenceAvailability`：

- `derive_evidence_availability()` 只消费已经存在的 `ChapterFactProjection`、章节 facts、evidence anchor ids、missing reasons 和 typed contract requirement ids
- 输出 `evidence_availability.v1`，逐 requirement 区分 `available / missing / unavailable / not_applicable / unreviewed`
- 第 2 章的 availability 使用 typed Ch2 `performance / attribution / cost` 内部子契约 requirement id，但所有记录仍归属公开 `chapter_id=2`，不会形成 Ch2 公开拆章
- 第 1 章当前覆盖 `portfolio_managers` 和 `risk_characteristic_text` 的字段级 availability
- 第 3 章当前覆盖基金经理基本信息、portfolio managers、manager strategy text、turnover、holdings snapshot、cross-period style evidence、manager alignment 和 actual behavior 聚合 requirement；当前单年 `ChapterFactProjection` 不加载 prior-year 文档，跨期风格证据保持 `unreviewed` 缺口
- 第 6 章当前覆盖 `risk_characteristic_text` 的字段级 availability
- malformed 或未知 typed requirement id 会 fail-closed；该能力不读取文档仓库、PDF/cache/source helper、Service、Host、provider、retained report、文件系统、环境变量或 dayu，也不替代 `ChapterFactProjection`

`fund_agent/fund/evidence_confirm.py` 当前提供 no-live phase 1 `evidence_confirm.v1` 证据复核与锚点可审计性评分：

- `confirm_chapter_evidence()` / `confirm_projection_evidence()` 只消费调用方显式传入的 `ChapterFactInput` / `ChapterFactProjection` 和 `EvidenceConfirmReference`
- phase 1 proof predicate 是闭集：`candidate_only=False`、`source_truth_status="proven"`，`reference_kind` 与 `source_kind` 必须匹配 `annual_report_excerpt/annual_report`、`reviewed_note/reviewed_note` 或 `derived_calculation/derived`，且 reference 必须与当前 `ChapterEvidenceAnchor` 的来源类型、年份和显式 locator 不矛盾
- E1 检查 anchor 定位精度，E2 检查 fact material token 是否出现在同一个 anchor 的 proven excerpt 中，E3 检查可用 required fact 是否缺 anchor 或缺 proven reference
- `auditability_score` 当前为确定性四档：通过 100、E1 reviewable 70、E2 不匹配 40、E3 缺失 0；derived、not_applicable 或当前 phase 1 不支持的非 annual-report / derived anchor fact 不计分
- 该能力不读取文档仓库、PDF/cache/source helper、Service、Host、provider、retained report、文件系统、环境变量或 dayu，不接入 `ProgrammaticAuditResult`、FQ0-FQ6 quality gate、renderer、CLI 或 readiness 判定

`fund_agent/fund/evidence_confirm.py` 同时提供 no-live `evidence_confirm.v2` 五维评分与硬门控：

- `confirm_chapter_evidence_v2()` / `confirm_projection_evidence_v2()` 消费与 V1 相同的 `ChapterFactInput` / `ChapterFactProjection` 和 `EvidenceConfirmReference`，返回 `EvidenceConfirmResultV2`
- 五个确定性评分维度：`anchor_precision`、`source_support`、`missing_evidence`、`proof_boundary`、`value_match`，每个维度有独立的 `pass/warn/fail/not_applicable` 状态
- 硬门控语义：fact 级和聚合级 `EvidenceConfirmHardGate` 的 `fail/warn/pass/not_applicable`；阻断性失败（如 E3 缺失、proof_boundary 失败）产生 `fail`
- 分数语义：阻断性失败产生分数上限（score cap），防止稀释；通过 fact 使用无上限均值聚合
- V2 与 V1 共存：V1 公共函数 `confirm_chapter_evidence()` / `confirm_projection_evidence()` 不变，返回类型、分数和状态语义保持原样
- 该能力不读取文档仓库、PDF/cache/source helper、Service、Host、provider、retained report、文件系统、环境变量或 dayu，不接入 `ProgrammaticAuditResult`、FQ0-FQ6 quality gate、renderer、CLI 或 readiness 判定；调用方自行提供 reference

`fund_agent/fund/evidence_confirm_diagnostics.py` 当前提供 no-live `evidence_confirm_fact_diagnostic.v1` 安全诊断聚合：

- `summarize_evidence_confirm_diagnostics()` 只消费已经得到的 `EvidenceConfirmResultV2`，按 fail/warn 维度、`source_field_id` 和章节号聚合诊断桶
- 输出只包含基金代码、年份、fact/status/issue 计数、维度名、字段 ID、章节号、issue ids、下一 gate 建议和保守 root-cause 分类，不包含原文 excerpt、PDF/cache 路径、source helper 细节或 provider payload
- 当前 root-cause 分类只用于 RR-09 A0/A1 诊断准备：`missing_evidence`、`source_support`、`proof_boundary` 归为 `projection_attachment_defect`，`anchor_precision` warn 归为 `true_anchor_precision_gap`，`value_match` 保持 `undetermined`
- 该能力不读取文档仓库、PDF/cache/source helper、Service、Host、provider、renderer、quality gate、文件系统、环境变量或 dayu；不改变 V2 strict truth、ECQ 投影、quality gate 语义、report-body rendering、runtime product evidence、readiness 或 release 状态

`fund_agent/fund/evidence_confirm_semantic.py` 当前提供 no-live `evidence_confirm_semantic.v1` 语义蕴含 companion contract：

- `confirm_semantic_entailment()` 只消费调用方显式传入的 `EvidenceConfirmResultV2`、`EvidenceConfirmReference`、`EvidenceSemanticClaim` 和注入的 `EvidenceEntailmentClient`
- `EvidenceSemanticClaim` 是显式自然语言 claim 输入，包含 `claim_id`、`fact_id`、`source_field_id`、`claim_text` 和 `anchor_ids`；当前不从 `ChapterFactEntry.value`、renderer output 或报告正文推断 claim
- per-claim `status` 使用 `entailed / contradicted / insufficient / not_applicable` 表示语义支持；aggregate `overall_status` 使用 `pass / warn / fail / not_applicable` 表示 gate 状态
- deterministic V2 是前置硬门控：`source_support`、`missing_evidence`、`proof_boundary` 不通过或 `value_match` 失败时不调用 semantic client；semantic output 不能覆盖缺证、candidate-only、not_proven、定位不匹配或数值不匹配
- `anchor_precision` warning 下可以运行 semantic client，但 entailed 结果仍保持 aggregate `warn`
- malformed client result、client status/reason 不兼容和 client exception 都 fail-closed；异常详情不写入结果
- 该能力不构造真实 provider/LLM client，不读取文档仓库、PDF/cache/source helper、Service、Host、renderer、quality gate、文件系统、环境变量或 dayu；Service-owned provider adapter、default-on analyze warn 策略、CLI safe summary 和 quality-gate ECQ 投影已经由后续 gate 接入，provider-backed semantic default-on production use、renderer/report-body 集成和 release/readiness 仍需后续 gate

`fund_agent/fund/evidence_confirm_sources.py` 当前提供 no-live `ParsedAnnualReport` 年报引用 materializer 和底层 repository-bounded runner 实现：

- `build_annual_report_evidence_confirm_references()` 只消费调用方已经传入的 `ChapterFactProjection` 与 `ParsedAnnualReport`
- 只 materialize `source_kind="annual_report"` 的 anchor，输出既有 `annual_report_excerpt / annual_report` reference/source kind，不扩展 `EvidenceSourceKind` 或公共 `EvidenceAnchor`
- 表格定位只接受 `page-{page_number}-table-{table_index}` 并精确匹配 `ParsedTable.page_number/table_index`；行定位只接受零基 `row-N`
- 无 table/row locator 时只用 `ParsedAnnualReport.get_section_text(section_id)` 构造 bounded section excerpt，不按 page_number 切 `raw_text`
- `source_truth_status` 默认 `not_proven`；只有请求为 `proven` 且当前 EID single-source metadata admission 满足时才输出 proven reference
- import 与 materializer 不实例化 `FundDocumentRepository`，不读取 PDF/cache/source helper，不触发网络、provider、Service、Host、renderer、quality gate 或 readiness 判定
- `run_repository_bounded_evidence_confirm()` 是 EC-P2 repository-bounded runner：只通过注入或默认 repository 的 async `load_annual_report(fund_code, report_year, force_refresh=...)` 取得 `ParsedAnnualReport`，可在 repository load 成功后用受控 `projection_factory` 构造 live smoke projection，再复用 materializer 与 V2 Evidence Confirm；来源异常按 `not_found / unavailable / schema_drift / identity_mismatch / integrity_error / ambiguous_repository_failure` fail-closed 分类；`status` 保持 strict V2 聚合语义，`pathway_status` 只表示 repository/source/PDF 通路是否打通
- `scripts/evidence_confirm_ec_p2_live_sample.py` 只允许 `004393/2025`，构造 `projection_kind="ec_p2_live_section_smoke"` 的 section-smoke projection，输出安全标量 JSON；section-only smoke 的 E1 `anchor_precision` warning 可作为 `pathway_status="pass"` 的 warning reason，但不改变 strict `status` / `evidence_confirm_overall_status`；它只证明 repository -> parsed report -> reference materializer -> V2 通路，不证明字段正确性、source truth family、semantic entailment、golden、readiness 或 release

`fund_agent/fund/evidence_confirm_runner.py` 当前是 Service 可导入的 Fund 层 typed facade：

- 只导出 `EvidenceConfirmRepositoryRunRequest`、`EvidenceConfirmRepositoryRunResult` 和 `run_repository_bounded_evidence_confirm()`
- Service 通过该 facade 调用 repository-bounded Evidence Confirm runner，不直接导入底层 materializer/source 模块名
- 该 facade 不改变底层实现、不读取 Service/UI/Host/renderer/quality gate 输入，也不放宽 source/PDF 访问边界

`fund_agent/fund/evidence_confirm_production.py` 当前提供 `EvidenceConfirmProductionSummary`，用于 Service/UI/quality gate 的生产集成摘要：

- 摘要字段只包含 `policy`、`status`、`pathway_status`、`deterministic_status`、`semantic_status`、fact 计数、issue id、可审计性分数和稳定 reason code，不包含原文 excerpt、PDF/cache 路径、parser JSON、source adapter 对象或 provider payload
- 默认 product `analyze` 会以 `warn` 策略通过 Service 调用 repository-bounded runner 并创建 summary；`analyze-annual-period` 通过 current-year `analyze()` 委托路径继承该 summary；`checklist` 仍固定 Evidence Confirm `off`；developer override `off|warn|block` 仅用于 `analyze --dev-override`
- semantic companion 可通过调用方已经产生的 no-live injected result 进入 summary；Service-owned provider adapter 已有 release/readiness 证据，但默认 product path 仍不构造 provider-backed semantic client、不读取 env、HTTP 或 LLM 配置

`fund_agent/fund/quality_gate_integration.py` 当前可把显式传入的 Evidence Confirm summary 投影到 `ECQ` issue family：

| 规则码 | 含义 | 当前语义 |
|--------|------|----------|
| ECQ0 | Evidence Confirm not-run | 显式 not-run summary 的 `info` issue |
| ECQ1 | repository/source/reference 通路失败 | policy `block` 时阻断，否则警告 |
| ECQ2 | deterministic V2 hard-gate fail | policy `block` 时阻断，否则警告 |
| ECQ3 | deterministic V2 warn | 警告 |
| ECQ4 | injected semantic companion fail/warn | 仅当 summary 已携带 no-live semantic result 时投影；不代表 provider-backed semantic quality |

ECQ 投影只消费 compact summary，不读取文档仓库、PDF/cache、source helper、parser artifact、renderer、provider 或 LLM。`score.json` 仍保持 FQ0-FQ6 评分输出；ECQ 只进入合并后的 `quality_gate.json` / `quality_gate.md`。缺省未请求 Evidence Confirm 时保持既有 quality gate 行为。

template truth-source replacement、typed projection 和 `EvidenceAvailability` 的当前非目标是：不改变 deterministic `analyze/checklist`、renderer、FQ0-FQ6 quality gate、final judgment、provider/runtime defaults、score/golden/readiness，不实现 Ch2 公开拆章、多年证据 runtime、Agent runner/tool-loop、Host 业务理解或 dayu runtime。

`fund_agent/fund/chapter_writer.py` 和 `fund_agent/fund/chapter_auditor.py` 当前提供 Gate 2 单章 writer / auditor primitives：

- `build_chapter_writer_input()` 从 `ChapterFactProjection` 中选择单个 `ChapterFactInput`，不读取任何文档或外部来源
- `build_chapter_prompt()` 只消费 CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、facts、missing reasons 和 evidence anchors
- writer 支持 `prompt_payload_mode="compact"`，当前由显式 `--use-llm` Service 路径使用；compact 只压缩大 `value` 的表达，保留 `fact_id`、`source_field_id`、`status`、`missing_reason`、`evidence_anchor_ids`、anchor id 和 source location metadata，并明确禁止 LLM 引用或推断被省略的 raw detail
- writer prompt-cost diagnostic 只记录 component 字符数、fact/anchor 成本行和 prompt char/token 标量，不保存完整 prompt、fact 原文、anchor note、draft、provider request 或 provider response
- `write_chapter()` 通过调用方显式注入的 `ChapterLLMClient` 生成单章草稿；`mode="prompt_only"` 只返回 prompt 和 blocked result，不伪造草稿
- `audit_chapter_llm()` 在未提供 typed contract 时继续使用旧 `DEFAULT_AUDIT_FOCUS` 兼容路径；提供 typed contract 时只把闭集 `audit_focus` id 传入 LLM request，程序审计不读取 focus
- writer 要求第 1-6 章输出固定顶层段落 `### 结论要点`、`### 详细情况`、`### 证据与出处`；每个 `required_output_items` 必须先输出 exact marker `<!-- required_output:<item> -->`
- writer 可显式接收 typed `RequiredOutputItem` 与 `EvidenceAvailability` 作为 additive path；该路径使用 stable item id marker `<!-- required_output:<typed item id> -->`，按 `render_evidence_gap / render_minimum_verification_question / delete_if_not_applicable / block` 裁定缺证 required output。`block` 在调用 LLM client 前 fail-closed，`delete_if_not_applicable` 必须有 typed reason，gap/verification 输出必须包含 approved 缺口或最小验证问题措辞。未传 typed 输入时保持当前生产默认 marker 和写作行为
- writer 只接受精确 marker：`<!-- required_output:<item> -->`、`<!-- anchor:<anchor_id> -->` 和 `<!-- missing:<reason> -->`；未知 anchor、缺固定段落、缺 required output marker、超出 `max_output_chars`、`finish_reason=length/max_tokens/content_filter` 都会 fail-closed 到稳定 stop reason，不截断或部分接受
- writer prompt 明确禁止根据 `fact_id`、`source_field_id`、`source_field_name` 或 fact value 合成 anchor id；`bond_risk_evidence` 内部/组级 anchors 不属于 `ChapterEvidenceAnchor`，除非未来 conversion helper 显式转换，否则不得写入 `<!-- anchor:... -->`
- writer prompt 对模板第 2 章 R=A+B-C 数字闭环有专门约束：R/A/B/C/A-C、Alpha/Beta/Cost 或具体百分比闭合断言必须在同句或上下 2 行内带 allowed anchor marker；来源标签、年报章节名或出处列表不能替代局部 anchor；缺同源事实或无法确认 anchor 支撑精确数值时，只能输出数据不足或下一步最小验证问题，不写具体百分比
- `ChapterRepairContext` 是当前 regenerate 的显式 typed 输入，携带上一轮 issue ids、脱敏 messages 和 required corrections；禁止通过 extra payload 传递这些参数
- `audit_chapter_programmatic()` 执行确定性章节审计，覆盖结构、占位符、锚点、ITEM_RULE 删除段落、禁用交易建议、`non_asserted_facets` 误断言、第 5 章跨期缺口措辞，以及第 3 章 `ch3.must_not_cover.item_04` 的 typed evidence-conditional 禁区：当 `EvidenceAvailability` 显示实际行为/风格证据 missing、unavailable 或 unreviewed 时，required label 与显式证据缺口句可通过，正向或准正向 `言行一致` / `风格稳定` 判断触发稳定 clause id C2；如果调用方没有传入 `EvidenceAvailability`，unsafe 正向/准正向判断仍 fail-closed，不会因 typed clause 接管旧 phrase path 而 silent pass
- `audit_chapter_programmatic()` 对 required output 只以 exact marker 作为通过条件；typed writer path 使用 stable item id marker，legacy path 使用原文 item marker，正文裸 item 文案不能替代 marker；候选 facet 的“候选/未断言信息”说明允许通过，但任一断言式写法仍阻断
- `audit_chapter_programmatic()` 的 ITEM_RULE 删除段落检查只匹配对应 optional/conditional 段落的标题或专属 marker，不把 required_output 内的合法稳定性/结构性缺口讨论当成删除段落；`must_not_cover` 字面短语抽取忽略 `除非` 后的例外语义，例如第 6 章可在风险/验证语境中讨论压力测试，但仍阻断真正的 forbidden phrase
- `audit_chapter_llm()` 只通过调用方显式注入的 `ChapterAuditLLMClient` 审计；唯一 pass 行为必须是单行 `PASS|chapter|no issues`，问题行只能是 `BLOCKING|LOCATION|MESSAGE`、`REVIEWABLE|LOCATION|MESSAGE` 或 `INFO|LOCATION|MESSAGE`，且每行恰好三段、不得带解释性前缀、Markdown、JSON、标题、总结句或额外 `|`；解析失败或缺少 client 都 fail-closed
- LLM auditor 只做 bounded semantic audit：`<!-- missing:<reason> -->` 是 approved evidence-gap marker；草稿已用 allowed missing marker 和谨慎缺口措辞说明数据缺失时，不得仅因缺少事实、缺少 anchor 或缺少外部来源而阻断，但将缺失数据写成确定性结论、遗漏必要缺口语义、引用未知 anchor 或与 allowed facts 矛盾仍应阻断
- E2 证据与断言源文匹配复核不在 Gate 2 实现范围；当前由 no-live phase 1 Evidence Confirm helper 对调用方显式传入的同 anchor proven excerpt 做保守复核，不代表 full live source/PDF Evidence Confirm
- 这些 primitives 不实现 Service 用例、provider construction、CLI `--use-llm`、Host lifecycle、Agent runner/tool-loop 或 dayu runtime；当前显式 `--use-llm` typed path 由 Service 选择并把 typed inputs 传入这些 Fund primitives

`FundNavRepository.load_nav_series()` 是 data 层当前 typed NAV series contract，返回 `FundNavSeries`，显式承载份额类别、NAV 类型、调整基础、分红调整状态、identity 状态、source/cache/query provenance、完整性约束和强回撤证据资格。无参 `FundNavRepository()` 当前默认使用 CSRC EID accumulated NAV adapter：通过公开 search/detail/classification 页面验证 006597=A/2030-1010、006598=C/2030-1020、014217=E/2030-1040、022176=F/2030-1050，并按份额分别输出 `nav_type="accumulated_nav"`、`adjusted_basis="accumulated_nav"`、`dividend_adjustment_status="not_applicable"`、`identity_status="verified"`。旧 `FundNavDataAdapter.load_nav_data()` 继续作为 legacy/snapshot/analyze 兼容入口，返回 `NavDataResult` 并保持 `source="nav_cache" / "akshare"` 与 `cached` 语义；constructor-injected Akshare raw-unit adapter 兼容分支仍标记 `unit_nav/raw_unit_nav/requested_code_only` 且 `strong_drawdown_evidence_eligible=False`。

`fund_agent/fund/data/nav_metrics.py` 当前只实现 NAV 派生最大回撤。`calculate_max_drawdown_from_nav_series()` 只接受 `accumulated_nav / accumulated_nav / verified / strong_drawdown_evidence_eligible=True` 的 `FundNavSeries`，按显式 `period_start` / `period_end` inclusive 二次过滤 records，独立检查期内 `minimum_records`，遇到重复日期、非正 NAV、raw-unit、identity 未验证或样本不足都会通过 `NavDataContractError` fail-closed。`FundDataExtractor.extract()` 仅在 exact `bond_fund` 路径调用 typed repository，当前显式使用请求基金代码的 A 类份额和年报年度自然年窗口；A/C/E/F 不混合，volatility 不在当前实现范围。

`bond_risk_evidence.v1` 当前支持 `drawdown_stress` 使用 NAV 派生最大回撤作为 `quantitative_derived / derived_metric` accepted 证据。派生锚点使用 `source_kind="derived"`、`section_id="derived:nav"` 和 `metric:max_drawdown:<share_class>:<period_start>:<period_end>` row locator，note 中记录 source、source_id、source_url、query params、retrieved_at、record count、NAV type/basis、peak/trough 和 ratio。年报“控制回撤”文本只作为 weak control intent；当 NAV source 或指标失败时，不会被提升为定量证据，score / quality gate 仍按结构化未满足组自然发出缺口。

`project_report_evidence_bundle()` 位于 `fund_agent/fund/report_evidence.py`，当前把已经创建的 `StructuredFundDataBundle` 投影为 typed `ReportEvidenceBundle`：

- 只消费内存中的结构化数据包和显式 `ReportEvidenceProjectionContext`，不调用文档仓库、PDF/cache/source helper、renderer 或 FQ0-FQ6
- 输出冻结 slotted dataclass 记录，包括来源文档边界、报告事实、证据锚点、数据缺口、preferred_lens 可序列化投影、评分 issue 链接和派生 `review_status`
- `classified_fund_type` 只读取 `basic_identity.value["classified_fund_type"]`，不从名称、基准或类别推断；`nav_data` 当前不投影为报告事实
- `accepted_baseline` 只作为未来生命周期域存在，当前 slice 不会派生，也会拒绝调用方强制设置
- `DerivedCalculation` 当前只定义记录形状，`derived_calculations` 默认为空；R=A+B-C、压力测试等计算来源仍由后续 calculation-source gate 处理

`validate_report_quality_bundle()` 和 `validate_report_quality_jsonl()` 位于 `fund_agent/fund/report_quality_validation.py`，当前用于校验报告质量评分输入内容：

- 只消费 `ReportEvidenceBundle`、JSON-like Mapping 或 JSONL record，不读取文档仓库、PDF/cache/source helper、renderer、Service 或 FQ0-FQ6 输出
- 复用 `report_evidence.py` 的 Literal domain、schema version 和 typed dataclass 字段名，不创建平行评分输入 schema
- 输出冻结 slotted dataclass 结果，包括字段缺失、enum domain、invalid combinations、id refs、`N/A`、`chapter_summary`、fallback consistency、`scoring_ready` 前置条件和链接完整性 issue
- JSONL 当前支持 `record_type="bundle"` 与 `record_type="score_issue"`；多 bundle artifact 中，独立 `score_issue` 归属到最近的前置 bundle，bundle 前的裸 `score_issue` 会 fail-closed，并保留稳定行号 / 字段 pointer，供后续 scoring-run artifact 复盘
- validator 只做内容可消费性判断，不替代 `run_quality_gate()` 的 FQ0-FQ6，也不生成 durable baseline 或 curated fixture

`run_extraction_snapshot()` 返回 `SnapshotRunResult`，当前覆盖 P4-S1 精选基金池字段级抽取快照：

- 输入显式接收 `fund_code`、`report_year`、`source_csv`、`run_id`、输出目录和 `force_refresh`
- 读取 `docs/code_20260519.csv` 的“基金名称 / 基金代码 / 类别”三列，并校验名称非空、6 位代码、类别非空和重复代码
- 只通过 `FundDataExtractor.extract(...)` 获取结构化数据包，不直接读取 PDF、cache 或底层解析文件
- 将 `StructuredFundDataBundle` 拆成字段级记录：`basic_identity`、`product_profile`、`benchmark`、`index_profile`、`fee_schedule`、`classified_fund_type`、`nav_benchmark_performance`、`investor_return`、`tracking_error`、`manager_strategy_text`、`portfolio_managers`、`turnover_rate`、`manager_alignment`、`holder_structure`、`holdings_snapshot`、`risk_characteristic_text`、`bond_risk_evidence`、`share_change`、`nav_data`
- 每条记录包含 `comparable_values`，只暴露 correctness 可直接比较的白名单子字段；当前覆盖 `basic_identity`、`benchmark`、`index_profile`、`nav_benchmark_performance`、`tracking_error`、`classified_fund_type`、`portfolio_managers` 和 `risk_characteristic_text` 的稳定标量子字段
- 每条记录包含 additive 公共来源 provenance 字段：`source_provenance_schema_version`、`source_strategy`、`selected_source`、`source_mode`、`fallback_enabled`、`resolved_source_name`、`fallback_used`、`primary_failure_category`、`fallback_eligibility`、`source_provenance_status` 和 `source_provenance_reason`；这些字段只来自 `StructuredFundDataBundle.source_provenance` 投影，不改变来源编排或 fallback 资格判定。当前 v2 公共投影以 `selected_source` / `source_mode` / `fallback_enabled` 表达 EID single-source policy；`source_strategy` 只作为兼容 alias，不是来源获取策略或 fallback 授权。当前 fallback 成功路径会把主来源 `not_found` / `unavailable` 分类持久化为 `AnnualReportSourceMetadata.primary_failure_category`，旧元数据缺失 current policy 字段时继续输出 `legacy_or_unknown` / `unknown_public_metadata_absent`
- `index_profile` 和 `tracking_error` 对 `index_fund` / `enhanced_index` 作为条件 P1 字段进入 FQ2 coverage、traceability 和单基金缺失分母；非指数基金从这些指数质量字段分母中排除，未知基金类型继续保守计分
- 输出 `snapshot.jsonl`、`summary.md` 和 `errors.jsonl`；`summary.md` 额外包含独立 `Source Provenance` 表，完全失败且没有 snapshot 记录的基金在 v1 表中省略并保留说明；单只基金失败时继续后续基金并记录错误
- snapshot 只记录当前 extractor 的真实输出，不为特定基金覆盖字段值；`004393` 曾被误判为 `index_fund` 的问题已在 P4-S3a 修复为 `active_fund`

`ExtractorOutputRepository` 当前用于把完整 `StructuredFundDataBundle` 保存为 bundle-level 结构化 JSON：

- schema version 固定为 `fund-agent.extractor_output.v1`
- 默认根目录为 `reports/extractor-outputs`
- 路径固定为 `<root>/<fund_code>/annual_report/<year>/structured_fund_data.json`
- 当前只支持 `report_type="annual_report"`；其它报告类型 fail-closed
- JSON 顶层保留 `fund_code`、`report_type`、`report_year`、`created_at` 和 `bundle`
- `bundle` 保留当前 `StructuredFundDataBundle` 的全部字段；每个 `ExtractedField` 保留 `value`、`anchors`、`extraction_mode` 和 `note`
- `load(...)` 会校验路径请求身份与 JSON 顶层身份一致；不一致时 fail-closed
- 序列化只接受 JSON primitive、dataclass、string-key mapping 和 sequence；未知对象不做 `str()` fallback，而是 `TypeError` fail-closed
- 该仓库不读取文档仓库、PDF/cache、parser 原始产物或 source helper，不替代 `extraction_snapshot`、strict golden answer、quality gate、source truth、readiness 或 release proof

`run_extraction_score()` 返回 `ExtractionScoreResult`，当前覆盖 P4-S2 字段级评分和 P4-R10 correctness 最小闭环：

- 只消费 P4-S1 `snapshot.jsonl`，不读取 PDF、cache 或文档仓库
- 按代码同源的 `field_name` 映射 P0/P1/P2 优先级
- 输出字段级 `field_group`、`field_name`、`priority`、`records`、`coverage_rate`、`traceability_rate` 和 `status`
- 同时输出单基金 `fund_scores`，汇总每只基金的 P0/P1 状态与失败字段，避免字段聚合均值掩盖单只基金不可用问题
- 同时输出单基金 `fund_quality`，从 snapshot 同源派生 App 类别匹配、`preferred_lens` 可解析状态、字段缺失率和缺失 P0/P1 字段；同一基金多行 `app_category` 或 `classified_fund_type` 冲突时显式标记，不取第一行静默通过
- 对 exact `bond_fund`，权益持仓形态的 `holdings_snapshot` 不进入股票持仓 coverage / traceability / `fund_quality.missing_field_rate` 分母；该排除必须同时输出 `field_applicability_decisions` 和 `score_applicability_issues` 中的 `bond_risk_evidence.v1` / `bond_risk_evidence_missing` 替代风险证据缺口。未知或冲突基金类型保持 fail-closed，不排除该字段
- 显式提供 `errors_path` 时，同时输出 `failed_funds`，把 `errors.jsonl` 中完全抽取失败的基金带入后续 gate accounting
- 阈值显式配置：pass 为 coverage/traceability 均不低于 90%，watch 为均不低于 70%，其余 fail
- 可选读取 strict `golden-answer.json` 执行 correctness，比对 identity 为 `fund_code + report_year + field_name + sub_field`；比对范围只包括 snapshot `comparable_values` 显式暴露的可比 golden 子字段；只有白名单字段/子字段被同年 snapshot 明确标记缺失时才进入 mismatch，skipped 和 unavailable 不进分母
- `CorrectnessSummary.status` 保持 `available / unavailable` 粗粒度状态，`coverage_scope` 额外区分 `not_configured / fund_not_covered / year_not_covered / no_comparable_fields / partially_covered / covered`，并输出 `covered_fund_codes`、`missing_fund_codes`、`coverage_reason` 和 `coverage_required=false`
- 输出 `score.json`、`score.md` 和 `golden_set.json`

`run_golden_prefill()` 返回 `GoldenPrefillResult`，当前用于生成 correctness golden answer 人工复核底稿：

- 读取 `docs/golden-answer-template.md` 中的基金代码和字段行
- 只通过 `FundDataExtractor.extract(...)` 获取结构化数据包，不直接读取 PDF、cache 或底层解析文件
- 自动填入 `expected_value`、`confidence` 和 `source`；字段值可以是 dict 或 dataclass
- 输出 Markdown 底稿；该输出是 silver label，不能直接作为最终 golden answer

`build_golden_answer_json()` 返回 `GoldenAnswerBuildResult`，当前用于把人工审核后的 Markdown 转成 strict JSON：

- 只消费 Markdown，不读取 PDF、cache 或底层解析文件
- 支持在每个基金标题下用 fenced `golden-answer-metadata` 代码块声明基金级 `report_year`；历史 Markdown 缺少 metadata 时仅按已复核 legacy 2024 corpus 兼容解析为 `2024`
- 校验有效行必须包含 `expected_value`、`confidence`、`source`
- `confidence` 只允许 `high / medium / low`
- `source` 必须是可复核来源，不能保留 `manual_required`
- `source` 文本只作为人工证据描述，不参与机器身份键推断
- 构建阶段允许同一基金代码跨年份并存；同一 `fund_code + report_year` 基金区块或同一 `fund_code + report_year + field_name + sub_field` 记录重复时 fail-fast
- 输出 `fund-agent.golden-answer.v1` JSON，包含基金级和记录级 `report_year`，供 correctness 自动比对使用
- `load_golden_answer_json()` 读取同一 strict JSON schema，供 Fund 内部比对复用，不重新解析 Markdown；legacy JSON 缺少 `report_year` 时按当前已复核 2024 golden corpus 加载为 `2024`

`run_quality_gate()` 返回 `QualityGateResult`，当前用于 P4-S4 报告质量 gate：

- 只消费 `extraction-score` 产出的 `score.json`
- P0 字段 `fail` 触发 `block`
- 单基金 `fund_scores` 中 P0 `fail` 触发带 `fund_code` 的 `block`
- P1 字段 `fail` 触发 `warn`
- correctness 尚未接入、当前基金缺 strict golden 覆盖、当前基金有 golden 但当前 `report_year` 未覆盖，或当前基金有 golden 记录但无可比字段时只记录 `FQ0/info`，metadata 包含 `reason`、`coverage_scope`、`fund_code` 和记录计数
- correctness 可用且出现明确 mismatch 时触发 `FQ1/block`
- `fund_quality` 中 App 类别与基金类型明确冲突时触发 `FQ1/block`
- `fund_quality.missing_field_rate` 达到 20% 触发 `FQ4/warn`，达到 35% 触发 `FQ4/block`
- `fund_quality.preferred_lens_status` 使用 `resolved / not_applicable / mismatch` 表达模板契约适用性；`mismatch` 触发 `FQ5/block`，`resolved` 和 `not_applicable` 只进入 `quality_gate.json.rule_results`
- FQ5 只消费 `score.json` 中由 CHAPTER_CONTRACT / ITEM_RULE manifest 派生的适用性事实，不解析最终报告 Markdown，也不证明 renderer 已遵守 preferred_lens 或 ITEM_RULE 段落；renderer/audit 的 ITEM_RULE 合规由程序审计 C2 在报告渲染后验证
- `failed_funds` 中的完全抽取失败基金触发 `FQ6/block`
- `score_applicability_issues` 中的 `bond_risk_evidence_missing` 投影为 `FQ2F/warn`，用于防止债券基金因排除权益持仓分母而误通过；旧 `score.json` 缺少该字段时按空列表兼容
- 旧 `score.json` 缺少 `fund_quality` 时只记录 `FQ0/info`，不作为 fatal schema 错误
- 旧 `score.json` 中 `preferred_lens_status=match` 兼容为 `resolved`
- 输出 `quality_gate.json` 和 `quality_gate.md`，其中 `rule_results` 记录未触发 issue 的 FQ5 解释性结果

`run_quality_gate_for_bundle()` 返回 `BundleQualityGateResult`，当前用于 P5-S1 `analyze` 主链路质量保护：

- 输入为 Service 已经取得的 `StructuredFundDataBundle`，不重新调用 `FundDataExtractor.extract(...)`
- 复用 `build_snapshot_records(...)` 把单基金数据包转换为本次运行的 snapshot 记录
- 写出单基金 `snapshot.jsonl`、`score.json`、`score.md`、`golden_set.json`、`quality_gate.json` 和 `quality_gate.md`
- 基金不在精选池 CSV、CSV 不可用或 schema 非法时返回 `not_run_reason`，不伪造 App 类别；Service 在 `quality_gate_policy=block` 下会把该状态转成结构化阻断异常，CLI 以退出码 2 输出 `quality_gate_status: not_run`
- 基金在精选池 CSV 中但 strict golden answer 尚未覆盖时 gate 仍已运行，结果保留 `FQ0/info`，不返回 `not_run_reason`
- 默认输出目录由 Service 生成唯一 run id 后落在 `reports/quality-gate-runs/<run-id>`，避免覆盖上一轮自动运行

`check_quality_gate_fund_membership()` 是 Service 抽取前短路使用的轻量公开契约：

- 只读取并校验精选池 CSV，确认当前基金是否存在
- 不读取年报、不生成 snapshot、不执行 score 或 gate
- 返回 `None` 表示可运行；返回 not-run reason 表示 block 策略下应阻断昂贵抽取

`run_golden_readiness_preflight()` 返回 `GoldenReadinessPreflightResult`，当前用于 baseline/golden v1 promotion 前的只读 readiness 聚合：

- 只消费显式传入的 `source_csv`、snapshot JSONL、score JSON、quality gate JSON、strict `golden-answer.json`、fixture promotion state manifest 和 accepted coverage disposition manifest
- 没有 tracked coverage disposition manifest 时使用代码内 static current accepted disposition manifest，并在输出 JSON 原样写入 `schema_version`、`accepted_as_of`、`source_artifacts`、`entries` 和 lifecycle semantics
- strict golden answer v1 做 fund/year coverage 检查；同一基金已有 golden 但当前 `report_year` 未覆盖时输出 `strict_golden_year_not_covered` blocker；`strict_golden_partial_coverage` 仍保留为未来 schema/gate，不在当前 preflight 触发
- fixture promotion state manifest 缺省时输出 `fixture_promotion_absent` blocker，而不是 IO failure；year-aware manifest 使用 `(fund_code, report_year)` 作为 promotion proof 身份，legacy fund-code-only manifest 只作为诊断输入并输出 `fixture_promotion_legacy_fund_only` blocker，不会被当成特定年份 promotion proof；eligible fallback 只解除 source provenance blocker，不证明 ready
- 006597 当前 bond `bond_risk_evidence_missing` 以 `blocker_resolved` / `original_blocker_code=bond_risk_evidence_missing` 输出为 resolved item，不列为 blocker
- 输出 `golden_readiness_preflight.json` 与 `.md`，只表达 readiness/blocker/owner/next gate，不修改 score policy、quality gate severity、golden answer、golden fixture 或 promotion state

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

基金经理任期和同类总费率中位数必须由调用方显式提供；跟踪误差通过 `resolve_tracking_error_for_risk()` 从 `StructuredFundDataBundle.tracking_error` 解析，结构化 Fund 数据优先。开发覆盖只在 developer override mode 且结构化跟踪误差缺失时作为本地风险检查 fallback，不作为产品证据；缺失时对应项返回 `insufficient_data`。

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
- 当前估值处于什么位置：消费 `ValuationStateResolution`；调用方显式传入的 `valuation_state` 只作为手动 override 和旧兼容投影
- 这笔钱 3-4 年内不会用吗：消费调用方显式传入的 `money_horizon` 或资金不用年限

检查清单只输出 `green / yellow / red / gray` 和 `pass / watch / block / insufficient_data`，不输出买入、卖出、仓位比例或收益预测。估值和资金期限缺失时输出灰灯，不猜测。

`run_programmatic_audit()` 返回 `ProgrammaticAuditResult`，当前覆盖 `docs/design.md` 第 5.2 节 MVP 程序审计规则。这里的 P/C/L/R 规则码只用于报告渲染后的程序审计，不等同于 quality gate 的 FQ0-FQ6 字段质量规则，也不声明后续 LLM 审计和 Evidence Confirm 已实现：

- `P1`：报告章节结构不匹配
- `P2`：章节内容过短
- `P3`：缺少证据与出处、全局证据锚点或章节内最小证据行
- `C2`：确定性 CHAPTER_CONTRACT 契约不一致，包括 required_output_items marker 缺失、must_answer 独立程序 marker 缺失、must_not_cover 禁止 marker 命中或章节块元数据不一致
- `L1`：R=A+B-C 数值计算不闭合
- `R1`：检查清单信号与规则不一致
- `R2`：最终 selected 判断、系统派生判断、判断来源与检查清单信号矛盾

程序审计只消费已渲染 Markdown、`RenderedChapterBlock`、`RabcAttribution`、`ChecklistResult`、selected 最终判断、derived 最终判断、判断来源、renderer 产生的 `item_rule_decisions` 和 `item_rule_audit_context`，不读取年报、PDF 或外部数据。`chapter_blocks` 可显式传入；缺省时审计会按 `CHAPTER_CONTRACT` 标题从 `report_markdown` fail-closed 切分。上述输入是当前 MVP 审计 gate 的必需输入；缺少报告、R=A+B-C 结构化结果、检查清单、selected/derived 判断或判断来源时，审计返回失败，不把未执行的规则伪装成通过。developer override 与系统派生判断不一致时由 R2 阻断。

R1 对检查清单第 6 问使用 `ProgrammaticAuditInput.valuation_state_resolution` 作为估值来源真源，不从 `ChecklistItem.reason` 反推来源。自动温度计估值必须携带 `external_api` 锚点、指数代码、指数名称、温度、PE/PB 分位、数据日期、回溯窗口、数据来源、缓存状态和报告内免责声明；显式用户输入只要求 `user_input` derived 锚点。

C2 当前只做确定性 marker / 元数据检查，不调用 LLM，不判断语义型章节越界，也不验证证据是否支撑断言；证据精确性与证据匹配属于 E1/E2/E3 审计面。当前 Fund 层已有 no-live phase 1 Evidence Confirm helper，但它不进入 `ProgrammaticAuditResult.checked_rules`。`load_contract_audit_coverage_manifest()` 维护每条 `must_answer` 的显式覆盖路由：当前 44 条通过既有 `required_output_items` marker 承载，1 条为第 5 章 narrative guidance；非程序化 coverage 只用于可审计路由，不表示 C2 已证明语义质量。ITEM_RULE C2 只检查 renderer 传入的决策是否与对应 `RenderedChapterBlock.body_markdown` 中的唯一小节标记一致：`identity_present` 且决策缺失会失败，`identity_missing` 空决策只跳过 ITEM_RULE 缺决策问题。

完整三层审计目标仍包含 E1/E2/E3、C1 和 L2，但这些规则属于后续 LLM 审计 / Evidence Confirm / 语义复核层。当前 MVP 不把 E1/E2/E3 放入 `ProgrammaticAuditResult.checked_rules`；已实现的 Evidence Confirm phase 1 只提供显式 reference 输入下的 no-live 可审计性评分，不把 full source/PDF 语义复核伪装成程序审计通过。

`render_template_report()` 返回 `TemplateRenderResult`，当前覆盖 `docs/design.md` 第 3.1 节 8 章模板渲染：

- 输入契约是 `TemplateRenderInput`，显式聚合 `StructuredFundDataBundle`、`RabcAttribution`、`AlphaJudgment`、`ConsistencyCheckResult`、`InvestorExperienceResult`、`RiskCheckResult`、`StressTestResult`、`ChecklistResult`、`FinalJudgmentDecision` 和可选 `current_stage`
- `TemplateRenderInput.valuation_state_resolution` 是估值状态结构化真源；若自建温度计被调用，模板第 7 章会输出免责声明，附录会渲染非年报 `external_api` 锚点
- 输出 `report_markdown`，固定包含模板第 0-7 章：投资要点概览、产品本质、R=A+B-C、基金经理画像、投资者获得感、当前阶段、核心风险、最终判断；章节标题由 `CHAPTER_CONTRACT` manifest 提供
- 主动基金第 3 章当前没有显式 reviewed turnover/style evidence 输入时，renderer 走缺证据降级路径：保留 `言行一致性判断` / `风格稳定性判断` required markers，明示 `证据不足` 和 `不能据此判断风格稳定、风格一致或言行一致`，并输出复核年报§8换手率及跨期行业配置 / 持仓集中度变化的下一步最小验证问题
- 输出 `audit_input`，可直接传给 `run_programmatic_audit()`，其中携带 `report_markdown`、`chapter_blocks`、`rabc_attributions`、`checklist_result`、`valuation_state_resolution`、selected 判断、derived 判断、判断来源、`item_rule_decisions` 和 `item_rule_audit_context`
- 输出 `evidence_anchors`，并在报告中渲染章节内 `> 📎 证据：年报{年份}§{章节} ...` 与附录 `证据与出处`
- 输出 `chapter_blocks`，每个 `RenderedChapterBlock` 包含 `chapter_id`、`title`、`heading`、`markdown`、`body_markdown` 和对应 `ChapterContract`
- 输出 `item_rule_decisions` 和 `item_rule_audit_context`；身份缺失时为空决策和 `identity_missing`，身份存在但 `classified_fund_type` 缺失或非法时 fail closed，身份有效时按 `facets=()` 评估当前四条 ITEM_RULE
- `get_template_chapter_heading(chapter_id)` 按 manifest 返回 `# {chapter_id}. {title}`；`split_rendered_chapter_blocks(report_markdown)` 按当前模板标题切分报告，并在空文本、缺章、重复、乱序、越界、标题不匹配或非模板一级标题时抛出 `ValueError`
- 第 0 章“当前最大的风险”优先使用首个 `risk_check_result.veto_items`，其次使用首个 `watch_items`，再其次使用压力测试中首个 `near_limit` / `beyond_tolerance` 场景；没有动作项时输出基于 `overall_status` 的通过/无否决说明。“什么变化会升级、降级或终止当前动作”消费风险、检查清单、压力测试和最终判断原因，按风险项 `pass`、检查清单 `green/pass`、压力测试 `within_tolerance` 的目标状态生成升级阈值；全绿通过时仍输出后续监控阈值
- 年报附录锚点按 `年报{年份}§{章节}表{编号}行{行号}` 输出；缺少表格、行定位或章节时显式写 `未定位`，页码作为附加位置元数据保留；非年报来源显式输出来源类型，不伪装成年报
- 章节缺少证据锚点时，正文输出数据不足证据行，附录同步输出对应模板章节的缺证条目
- 缺失字段显式写为“未披露”或“数据不足”，不静默省略

当前模板渲染器是 MVP 模板填充，不调用 LLM，不预测未来收益，不输出交易或配置指令。`FinalJudgment` 只允许 `worth_holding`、`needs_attention`、`suggest_replace` 三类，单一定义点为 `fund_agent/fund/analysis/final_judgment.py`。最终判断由 `derive_final_judgment()` 根据检查清单、否决项、压力测试和 Service 归一化后的 quality gate 状态派生；开发覆盖只改变 selected 判断，并保留 derived/source 供 R2 审计。

`load_template_contract_manifest()` 返回 `TemplateContractManifest`，当前从 `docs/fund-analysis-template-draft.md` canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 投影 `docs/design.md` 第 3.1 节和模板第 0-7 章 `CHAPTER_CONTRACT`：

- authored manifest 位于模板文档 canonical JSON；Fund 模板层 `fund_agent/fund/template/contracts.py` 只负责 strict parse / projection / validation，自带章节标题，不依赖 renderer 私有 `_CHAPTER_TITLES`
- 每章包含 `narrative_mode`、`must_answer`、`must_not_cover`、`required_output_items` 和 `preferred_lens`
- 第 3 章主动基金契约要求：风格稳定、风格一致或言行一致判断必须基于已复核的换手率或风格变化证据；证据缺失、不可用或未复核时，契约禁止推断主动基金风格稳定、风格一致或言行一致
- 第 5 章“当前阶段与关键变化”只承载当前阶段、上一期或历史对比下的关键变化、变化是否影响原始投资假设和下一步最小验证问题；不得给最终判断或展开风险清单
- 第 6 章“核心风险与否决项”承载结构性/阶段性风险、否决项、压力测试和最可能改变最终判断的信息缺口；不得复述阶段事实，除非明确转译为风险、压力测试或否决项
- `preferred_lens` key 只允许当前标准基金类型 `index_fund`、`active_fund`、`bond_fund`、`enhanced_index`、`qdii_fund`、`fof_fund` 和 `default`
- `resolve_preferred_lens(chapter_id, fund_type)` 优先返回精确基金类型 lens，没有精确命中时返回 `default`；章节缺失、基金类型不支持或缺少 fallback 时抛出 `ValueError`
- `validate_template_contract_manifest()` 对章节数量、id 连续性、重复 id、空字段、unsupported lens key 和无 lens fallback 执行 fail-closed 校验
- 当前 CHAPTER_CONTRACT manifest 是从模板文档 JSON 投影出的可机器消费契约清单，不改变 `render_template_report()` 的 Markdown 输出结构；FQ5 只使用它派生模板契约适用性，不声明 renderer compliance
- `fund_agent/fund/audit/contract_rules.py` 中的 `ContractAuditCoverageManifest` 逐条映射 `must_answer` 到 `covered_by_required_item`、`programmatic_marker`、`structured_data_availability`、`llm_semantic_audit`、`evidence_confirm` 或 `narrative_guidance`；当前内置规则没有 `programmatic_marker`，因此既有报告 C2 行为保持不变
- `build_lens_application_plan(fund_type)` 返回 `LensApplicationPlan`，把每章 `preferred_lens` 解析为 normalized `primary_focus`、`watch_variable_label` 和 `risk_focus_label`；renderer 当前只在第 0 章“当前最值得盯住的变量”和第 1 章“看这类基金最先看什么”两个既有 slot 消费这些标签，不把 raw `lens:` statements 渲染进最终报告

`load_template_item_rule_manifest()` 返回 `TemplateItemRuleManifest`，当前覆盖 `docs/fund-analysis-template-draft.md` 已声明的四条 `ITEM_RULE`：

- manifest 位于 Fund 模板层 `fund_agent/fund/template/item_rules.py`，与 `contracts.py` 平级；它不读取年报、PDF 或外部数据，renderer 和程序审计只消费其确定性规则与段落标记
- 当前内置规则全部为 `conditional`，覆盖第 1 章“指数编制规则与成分股”“基金经理投资哲学”和第 2 章“超额收益分年度拆解”“跟踪误差分析”；没有内置 optional 规则
- `evaluate_template_item_rules(fund_type=..., facets=...)` 只按标准基金类型和调用方显式提供的 facet 做确定性触发，不从报告文本推断 facet；已知 facet 覆盖指数、主动、增强指数、债券、QDII 和 FOF 细分标签，与基金类型冲突时抛出 `ValueError`
- `conditional` 未触发时决策为 `delete_segment`；schema 同时支持 `optional`，其缺失策略为 `render_unavailable`
- `rendered_segment_present(markdown, rule)` 只按唯一小节标记做字面量检查，不把“跟踪指数”等普通正文短语当作 ITEM_RULE 段落命中
- renderer 当前按 `classified_fund_type` 和 `facets=()` 生成 `item_rule_decisions`：触发规则输出固定 heading + 固定 bullet 的确定性段落，未触发 `conditional` 删除整段
- ITEM_RULE 段落内的 `证据边界` bullet 会在同一行渲染全部去重后的相关锚点，保留章节级 `> 📎 证据` 一章一条契约；这些锚点只表达 provenance，不证明跟踪误差、指数编制方法或成分股已经具备实质数据
- 程序审计 C2 当前消费 renderer 传入的 `item_rule_decisions` 和 `item_rule_audit_context`，只在对应章节块正文中验证应渲染段落存在、应删除段落不存在；不重新从报告 prose 推断 facet
- ITEM_RULE 当前不接入质量门禁、Service/UI/CLI 产品选项，也不改变 FQ5 语义

所有关键字段都通过 `EvidenceAnchor` 记录 `document_year`、`section_id`、`row_locator` 和命中原文，供后续证据锚点渲染使用。

温度计数据适配器位于 `fund_agent/fund/data/thermometer.py`：

- `FundThermometerAdapter.load_thermometer(...)` 读取有知有行公开数据页，当前默认页面为 `https://youzhiyouxing.cn/data` 和 `https://youzhiyouxing.cn/data/macro`
- 输出 `ThermometerSnapshot`，包含全市场温度、指数温度行、债券温度、10 年期国债收益率、更新时间、来源、缓存命中和 stale 状态
- 缓存位于 `cache/thermometer/thermometer.json`，24 小时内复用 fresh cache；抓取或解析失败时可回退到 7 天内 stale cache；无缓存时返回 `unavailable=True`
- 当前公开页快照已接入 `ThermometerService` 和 `fund-analysis thermometer`，但只作为过渡查询能力，不作为 P19 自建温度计生产真源

自建温度计 P19-S1/S2/P19-S5 位于 `fund_agent/fund/data/thermometer_types.py`、`fund_agent/fund/data/thermometer_source.py`、`fund_agent/fund/data/thermometer_cache.py` 和 `fund_agent/fund/analysis/thermometer_calculator.py`：

- 当前覆盖宽基指数和全 A 市场：`fund-analysis thermometer` 默认查询全 A 市场 `wind_all_a`，`fund-analysis thermometer --index wind_all_a` 可显式查询全 A，`fund-analysis thermometer --index wind_all_a,000300,000905` 可批量查询全 A、沪深300和中证500
- 数据源通过 akshare 乐咕乐股指数 PE/PB 接口获取沪深300/中证500 `滚动市盈率中位数` 和 `市净率中位数`，并通过全 A PE/PB 历史接口获取 `wind_all_a` 共同日期数据
- 指数和全 A 的 PE/PB 抓取按 PE 后 PB 顺序执行，避免并发进入 akshare/Legulegu native 依赖；全 A 同源响应内同日期多条正数记录按输入顺序保留最后一条，不跨来源插补或推断
- 计算器使用 PE/PB 历史分位数各 50% 生成温度和 `low/fair/high` 候选状态
- 缓存使用版本化 JSON，按市场/指数隔离命名空间：全 A 使用 `cache/thermometer/market/wind_all_a_history.json`，宽基指数使用 `cache/thermometer/index/<index_code>_history.json`
- 数据源失败时返回 `unavailable` 数据态或复用可用缓存，不 fallback 到有知有行公开页面
- `fund-analysis analyze` 缺省估值输入时，只对 `index_fund` / `enhanced_index` 且业绩基准 exact identity 映射到沪深300 `000300` 或中证500 `000905` 的基金调用自建温度计；主动、债券、QDII、FOF、缺失/歧义/派生/未支持指数均返回 `unavailable` 灰灯且不调用温度计
- 显式 `valuation_state=low/fair/high/unavailable` 优先于自动估值；其中显式 `unavailable` 是手动灰灯 opt-out
- `fund_agent/fund/analysis/valuation_state.py` 定义 `ValuationStateResolution`、指数映射规则和 resolution 构造函数，是检查清单、renderer、审计共享的估值结构化真源
- `fund_agent/fund/data/__init__.py` 是自建温度计对 Service 暴露的公共入口，导出读数类型、代码分类 helper 和默认数据源/缓存工厂；Service 不直接 import `thermometer_source.py` 或 `thermometer_cache.py` 的具体实现模块

仓库层位于 `fund_agent/fund/documents/`：

- `models.py`：`DocumentKey`、`ParsedAnnualReport`、`ReportSection`、`ParsedTable`、`AnnualReportReferenceMetadataResult`
- `repository.py`：对外唯一公开读取入口 `FundDocumentRepository`；`load_annual_report()` 返回解析年报，`get_annual_report_reference_metadata()` 只返回不含正文和路径的来源身份元数据
- `cache.py`：raw PDF 元信息缓存、parsed report 物化缓存与 bodyless reference metadata 查询；parsed report 命中前会检查最小正文长度和关键章节集合，避免历史低质量解析物被当作真实年报复用；parsed report JSON 使用同目录临时文件加原子替换写入，替换失败会清理临时 payload 且不写入 SQLite 行；损坏的来源元数据只降级为空元数据，不阻断 PDF 路径缓存读取；同一缓存实例内 parsed report 读写串行执行，避免同进程并发读写同一 SQLite/JSON 物化状态
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
- 当前支持从 `§2` 键值表读取名称、简称、类别、基准、投资目标、投资范围和投资策略；基金简称、类别、投资目标、投资范围和投资策略中的 QDII/FOF 标识会参与分类，但业绩比较基准不会单独触发 QDII/FOF/指数分类
- 债券基金名称优先于混合股票指数基准，避免产品因基准含沪深 300 被误判为指数基金；增强指数只由“指数增强/增强指数/增强型指数”等身份级表述触发，不因泛化“增强收益”误判
- QDII/FOF 是当前顶层分类标签；当 QDII/FOF 产品同时具备指数或增强指数身份时，`classified_fund_type` 仍保持 `qdii_fund`/`fof_fund`，并在 `classification_basis` 中保留并发指数/增强证据，不引入复合类型
- 分类结果通过 `FundTypeClassification(classified_fund_type, classification_basis)` 输出
- 当前实现明确遵守“基金类型判断优先于通用分析”，即先分类，再构造 `basic_identity`

当前边界要求：

- 业务调用方只通过 `FundDocumentRepository.load_annual_report(...)` 读取年报；只需要确认同源引用元数据时使用 `FundDocumentRepository.get_annual_report_reference_metadata(...)`，该接口不返回 PDF 路径、正文、章节、表格或来源 URL。
- 业务调用方若需要基础画像，只消费 `extract_profile(report)` 的结构化结果，不直接复用正则规则。
- `fund_agent/fund/pdf/*` 只作为仓库内部 helper / adapter，允许返回本地 `Path`，但这不是上层公共契约。
- `ParsedAnnualReport` 是后续各章节 extractor 的统一输入；当前稳定 extractor 已扩展到 `§1/§2/§3/§4/§8/§9/§10`。
- `extract_profile()` 当前不应用 `preferred_lens`，也不输出任何投资结论。
- `extract_performance()` 当前不跨章节做复杂 fallback，不引入 `§10`、净值序列或任何 P2 分析公式。
- `extract_manager_ownership()` 当前只抽原始披露，不输出言行一致性、利益一致性或成本判断。
- `extract_holdings_share_change()` 当前只抽表格原始披露，不输出持仓集中度、资金流向或投资者收益 fallback。

## 内部分层

- `documents/`：公共契约与仓库实现。上层应通过这里读取基金文档。
- `data/`：外部数据适配器、typed repository 与 NAV 派生指标。当前包含 CSRC EID accumulated NAV source adapter、NAV source Protocol/DTO、`FundNavDataAdapter` legacy raw-unit/cache adapter、`FundNavRepository` typed NAV series contract 和最大回撤 metric helper；`load_nav_data()` 保留 legacy 兼容，`load_nav_series()` 是路径型 NAV 指标的 typed 边界。
- `extractors/`：章节级结构化提取能力。当前已落地基础画像、`§3` 表现、管理人/持有人、持仓/份额 extractor。
- `data_extractor.py`：P1 façade，聚合文档仓库、净值适配器和章节 extractor。
- `report_evidence.py`：报告证据包 typed model / projection，只消费 `StructuredFundDataBundle` 与显式投影上下文，产出事实、锚点、缺口、preferred_lens 和派生 review status。
- `annual_evidence.py`：多年年报证据作用域、prior 年份加载、年度缺口分类、跨年事实派生和 `AnnualEvidenceBundle` typed model；只通过 `FundDocumentRepository` 加载 prior 年报。
- `template/annual_period_renderer.py`：多年年报期间报告 renderer，只消费内存中的 `AnnualEvidenceBundle` 和显式当前年份报告，输出正式 annual-period Markdown。
- `_value_utils.py`：Fund 内部结构化值 helper，把 dict/dataclass 抽取值规范化为子字段映射。
- `extraction_snapshot.py`：P4-S1 字段级抽取快照能力，消费 `FundDataExtractor` 并写出 JSONL/summary/errors。
- `extraction_score.py`：P4-S2 字段级评分与最小 golden set 选择能力，只消费 snapshot JSONL 和精选基金池 CSV。
- `fund_type.py`：基金类型识别规则，供 extractor 先行消费。
- `analysis/`：分析计算模块。当前包含 `r_abc.py`、`alpha_judge.py`、`consistency_check.py`、`investor_return.py`、`risk_check.py` 与内部比例解析 helper，只消费 P1/P2 结构化数据和显式判断证据，不直接读取年报文件。
- `template/`：模板渲染能力。当前包含 `renderer.py`，只消费 P1/P2 结构化结果并输出 8 章 Markdown、章节块与程序审计输入。
- `template/contracts.py`：模板契约能力，从模板文档 canonical JSON 投影第 0-7 章 CHAPTER_CONTRACT 机器契约、章节契约读取和基金类型 lens 解析。
- `template/chapter_contract_constraints.py`：CHAPTER_CONTRACT 可执行写作约束 sidecar，包裹既有章节契约并为 dev-only 写作审计提供 required evidence / N/A / failure behavior 配置。
- `template/item_rules.py`：模板 ITEM_RULE manifest，维护当前四条 conditional 规则、确定性触发评估和段落标记检查。
- `report_writing_audit.py`：dev-only 报告写作审计，只消费调用方显式传入的 `ReportEvidenceBundle`、已解析 records 和章节草稿代理，不读取基金文档、不接入 renderer、Service/CLI 或 FQ0-FQ6 质量门。
- `pdf/`：底层 PDF helper。当前包含：
  - `downloader.py`：仅供仓库内部使用的 PDF 下载 helper，会写入本地缓存
  - `parser.py`：PDF 全文、表格与章节定位原型
- EID 年报来源对同一基金代码/年份的 PDF 下载使用实例级锁；同 key 并发请求会复用首个请求落地的 PDF 缓存。该保护不等同于跨进程锁或完整仓库事务。
- `evidence_confirm.py`：no-live Evidence Confirm（V1 phase 1 + V2 五维评分与硬门控），只消费显式 `EvidenceConfirmReference`，执行 E1/E2/E3 的保守同 anchor excerpt 复核与五维确定性评分，不接 `ProgrammaticAuditResult` 或 quality gate。
- `evidence_confirm_diagnostics.py`：no-live Evidence Confirm V2 安全诊断聚合，只消费 `EvidenceConfirmResultV2`，输出维度/字段/章节级安全诊断桶和保守 root-cause 分类，不读取 source/PDF 或改变 quality gate。
- `evidence_confirm_semantic.py`：no-live Evidence Confirm 语义蕴含 companion contract，只消费 V2 结果、显式 references、显式 semantic claims 和注入的 `EvidenceEntailmentClient`；semantic output 不能覆盖 deterministic V2 failures，不构造 provider/live/Service/renderer/quality-gate 路径。
- `evidence_confirm_runner.py`：Service 可导入的 Evidence Confirm typed facade，只暴露 repository-bounded runner request/result/entrypoint；底层 materializer/source 实现仍留在 Fund 内部。
- `evidence_confirm_production.py`：Evidence Confirm 生产集成安全摘要，把 repository-bounded result 和可选 no-live injected semantic result 压缩为 `EvidenceConfirmProductionSummary`；不携带原文 excerpt、路径或 provider payload。
- `audit/`：程序审计规则。当前包含 `audit_programmatic.py` 和 `contract_rules.py`，执行 P1/P2/P3/C2/L1/R1/R2；C1/L2 属于后续 LLM 审计或语义复核层，E1/E2/E3 的 report-level/full source 接入仍需后续 gate。

## 当前边界

- 当前只支持 `annual_report`。
- 当前稳定 extractor 边界是 `§1/§2/§3/§4/§8/§9/§10`。
- 当前基础画像只覆盖 `basic_identity`、`product_profile`、`risk_characteristic_text`、`benchmark`、`fee_schedule` 五类输出。
- 当前 `§3` 表现只覆盖 `nav_benchmark_performance` 与 `investor_return` 两类输出。
- 当前管理人/持有人 extractor 覆盖 `manager_strategy_text`、`portfolio_managers`、`turnover_rate`、`manager_alignment`、`holder_structure` 五类输出；`portfolio_managers` 已接入 `StructuredFundDataBundle`、snapshot、report evidence、chapter facts 和 EvidenceAvailability，但不改变 renderer 或 quality gate。
- 当前持仓/份额 extractor 只覆盖 `holdings_snapshot` 与 `share_change` 两类输出；`holdings_snapshot` 当前支持股票 `top_holdings`、债券 `bond_top_holdings`、目标基金 `target_fund_holdings` 和行业分布，债券持仓与目标基金持仓只作为 `holdings_snapshot` 子形态接入下游，不新增 top-level bundle 字段；`share_change` 对多份额列表只显式选择单值列或表头精确基金代码列，无法可靠选择时返回 `missing`，不再按列顺序或 A 类 fallback 默认取值。
- `data_extractor.py` façade 已接入当前结构化数据；`structured_data` 当前以 `StructuredFundDataBundle` dataclass 表达，不额外物化 SQLite 表。
- `extractor_output_repository.py` 当前把 `StructuredFundDataBundle` 显式保存为 `fund-agent.extractor_output.v1` JSON，按 `fund_code / annual_report / report_year` 组织；它是 bundle-level 输出仓库，不是字段级 scoring snapshot，也不触发 extractor 默认写盘。
- `report_evidence.py` 当前只投影已有 `StructuredFundDataBundle`，包括 `portfolio_managers` 与 `risk_characteristic_text`；不新增抽取路径、不调用文档仓库、不把 `nav_data` 作为事实，也不改变 renderer / FQ0-FQ6 行为。
- `data/nav_repository.py` 当前默认把 CSRC EID 006597 家族 A/C/E/F 分类 `累计净值` 归一化为 accumulated NAV typed series，按份额 fail-closed 验证身份、分页、日期和数值；legacy raw-unit adapter 只能通过 constructor injection 进入兼容分支，并显式标记为非 strong drawdown evidence。`data/nav_metrics.py` 当前基于该 typed series 计算最大回撤；不提供 dividend-adjusted、total-return 或 volatility 指标。
- `extraction_snapshot.py` 当前记录字段级抽取状态，并通过 `comparable_values` 暴露 correctness 可比子字段白名单；不为特定基金覆盖字段值。
- `extraction_score.py` 当前计算字段级与单基金 coverage / traceability，对 strict golden answer 中 snapshot 可比字段执行 correctness 比对，并可显式消费 `errors.jsonl` 输出 `failed_funds`；旧 snapshot 仅保留 `classified_fund_type.fund_type` 兼容路径。
- `golden_answer.py` 当前构建、读取和校验人工 golden answer strict JSON，不执行 correctness 比对。
- `quality_gate.py` 当前只消费 `score.json`，按字段级、单基金、`fund_quality`、`failed_funds` 和 correctness 质量信号阻断，不读取基金文档，不执行 LLM 审计。
- `quality_gate_integration.py` 当前可在已有单基金 quality gate 结果上合并 ECQ issue；合并只消费可选 `EvidenceConfirmProductionSummary`，不读取基金文档。
- 当前 `analysis/r_abc.py` 实现 R=A+B-C 单期与多周期归因。
- 当前 `analysis/alpha_judge.py` 实现结构性/阶段性超额规则判断，不输出持有或替换结论。
- 当前 `analysis/consistency_check.py` 实现言行一致性 4 维度信号，不猜测基金经理动机或实际风格。
- 当前 `analysis/investor_return.py` 实现行为损益和份额变动趋势判断，不分析具体投资者交易行为。
- 当前 `analysis/risk_check.py` 实现 5 项否决条件检查，不把缺失输入强行判为通过或否决。
- 当前 `analysis/risk_check.py` 同时实现压力测试，按基金类型阈值为固定下跌场景分级，不预测风险发生概率。
- 当前 `analysis/checklist.py` 实现 7 问题检查清单，消费分析结果和显式用户输入，不读取外部数据。
- 当前 `audit/audit_programmatic.py` 实现 MVP 程序审计，不调用 LLM 或证据复核。
- 当前 `template/contracts.py` 从模板文档 canonical JSON 投影第 0-7 章 CHAPTER_CONTRACT manifest、章节契约读取和基金类型 lens，并执行 fail-closed manifest 校验。
- 当前 `template/chapter_contract_constraints.py` 实现第 0-7 章默认 wrapper 和首个 material overlay：主动基金第 3 章换手率 / 风格变化证据约束。增强指数第 2 章和债券第 6 章只登记为 deferred `config_only` 要求，不执行材料级审计。
- 当前 `template/item_rules.py` 实现 ITEM_RULE manifest、显式基金类型/facet 评估、审计上下文类型和唯一段落标记检查；不调用 LLM、不读取基金文档、不接入质量门禁。
- 当前 `template/renderer.py` 实现 8 章 Markdown 模板渲染，按 CHAPTER_CONTRACT manifest 生成章节标题，按 ITEM_RULE 决策渲染/删除固定段落，并返回可直接用于程序审计的 `ProgrammaticAuditInput` 与 `RenderedChapterBlock` 章节块；主动基金第 3 章在缺少显式 reviewed turnover/style evidence 输入时输出证据不足降级措辞，不输出风格稳定、风格一致或言行一致正向结论。
- 当前 `report_writing_audit.py` 实现主动基金第 3 章写作审计：缺少已复核换手率 / 风格变化事实和可解析证据锚点时，禁止稳定性、风格一致或言行一致正向判断；若仅有兼容 `data_gap`，草稿必须明示证据不足和下一步最小验证问题。
- `parser.py` 已具备 `§3` 定位修复，但真实样本扩展和更多章节/表格抽取仍在后续 slice 完成。
