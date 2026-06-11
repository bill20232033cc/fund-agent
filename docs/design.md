# 基金行为教练 Agent —— 设计真源文档

> **版本**: v2.16
> **日期**: 2026-06-11
> **状态**: 已按 `AGENTS.md` 统一为 Dayu 四层边界 `UI -> Service -> Host -> Agent`；当前默认 `fund-analysis analyze/checklist`、确定性 `fund-analysis analyze-annual-period` 与 Route C provider-backed `--use-llm` opt-in 路径的状态边界已显式区分；Dayu 是架构参考与能力来源，不是当前生产 runtime 直接依赖；internalized Host runtime governance adapter 已有 MVP 最小闭环；Slice E first no-live Agent body-chapter mechanics 已是当前代码事实，`fund_agent/agent` 已存在并拥有当前 no-live contracts、ToolTrace、Fund adapters、repair policy、body runner 和 `FinalAssemblyReadiness`；multi-year annual analysis productization implementation 已是当前代码事实：Service 提供 `MultiYearAnnualAnalysisRequest` / `analyze_multi_year_annual()`，UI 提供 `analyze-annual-period`，Fund 提供 `AnnualEvidenceScopeRequest`、`AnnualEvidenceLoader`、`AnnualEvidenceBundle` 和 Chapter 5 cross-year fact projection；full production Agent tool-loop/retry/budget/ToolRegistry/live runtime expansion、durable Host session/resume/memory/reply outbox、provider/default/runtime/budget change、score-loop、golden/readiness、full cross-year narrative writer/reporting、structured-data source identity extension 和 live acceptance 仍是未来 scope；typed template truth-source replacement 已把 `docs/fund-analysis-template-draft.md` 中的 canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 变成当前 untyped 和 typed template contract projection 的 authored Fund template contract truth source；EID single-source annual-report no-live implementation 已是当前代码事实：`selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`，默认 production orchestrator 只构造 EID source，repository/cache 只复用带当前 EID single-source metadata 的缓存；small-golden 五行 `004393`、`004194`、`006597`、`110020`、`017641` / `2024` 均已有 accepted live EID/FDR acquisition proof，证明 EID metadata、PDF integrity 和 parser viability；row-shape contract decision 已接受 `portfolio_manager_tenure_list.v1`、`risk_characteristic_text.v1`、`bond_top_holding_row.v1` 和 `target_fund_holding_row.v1`，四者均已是当前 extractor 输出面且已有 same-source passing correctness；live failure branches、fixture projection、golden/readiness 和 provider/LLM 行为仍未由该 live gate 证明；deterministic single-year renderer/checklist/analyze、provider/runtime defaults、score-loop、golden/readiness 和 public chapter ids `0-7` 未改变。
> **变更摘要**: v2.16 当前修订接受 multi-year annual analysis productization implementation gate。当前 2021-2025 产品路径不再是手工运行 5 次单年报告后人工合并：`fund-analysis analyze-annual-period FUND_CODE --target-year 2025 --start-year 2021` 会先运行 target year 单年 `analyze`，再由 Service 声明 Fund-owned annual evidence scope，Fund 通过 `FundDocumentRepository.load_annual_report()` 加载 optional prior 年报并产出 `AnnualEvidenceBundle`。Target year 仍是必需年报；prior year `not_found` / `unavailable` 记录为可降级 gap，`schema_drift` / `identity_mismatch` / `integrity_error` 记录为 failed-closed 年度。Prior 年份只使用窄 extractor 函数，不调用 full `FundDataExtractor.extract()`，不新增来源、不启用 fallback、不运行 live/provider/LLM。Chapter 5 可消费 eligible cross-year facts；没有 eligible facts 时保留既有 `cross_period_comparison_missing`。当前 CLI 输出 target-year Markdown 加多年 evidence summary，不声明完整跨年叙事报告已实现。v2.15 的 row-shape contract decision、EID single-source live proof 和 Source Provenance v2 事实继续保持当前代码/evidence fact。完整 Agent tool-loop/retry/budget/ToolRegistry/live runtime expansion、async Host runner、durable session/resume/memory/reply outbox、chapter live acceptance、provider runtime budget/default changes、score-loop entry、dayu runtime、live EID failure branch coverage、fixture projection、golden/readiness promotion、full cross-year narrative writer/reporting 和 structured-data source identity extension 仍未实现或未证明，必须进入后续独立 gate。
> **关联文档**: `docs/implementation-control.md`（实施总控）、`fund-agent-mvp-plan.md`（MVP 计划书）、`docs/fund-analysis-template-draft.md`（定性模板 v2）、`docs/audit-alignment.md`（审计机制对照研究）

⚠️ **重要声明**：本文档记录当前代码设计真源；若本文档、实施总控、README 或代码与用户提供的仓库执行规则冲突，必须先修正方案和实现，再回写本文档；不得长期保留“设计未来”口径冒充已实现状态。

---

## 1. 设计目标

### 1.1 北极星

**让普通基金投资者在买入前获得专业级的基金体检报告，避免追涨杀跌的行为亏损。**

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| 确定性 MVP 主链路 | 当前默认 `fund-analysis analyze` 与 `fund-analysis checklist` 不依赖 LLM 写作或 Host/Agent 调度，由结构化抽取、确定性分析、模板渲染、程序审计和 quality gate 组成；`analyze --use-llm` 是显式 opt-in provider-backed Route C 路径 |
| 好资产 + 好价格 + 长期持有 | 有知有行核心理念：分析报告回答"好不好"，检查清单回答"该不该买" |
| 证据可审计 | 每条断言必须关联到年报具体章节，计算必须可追溯 |
| 模板驱动而非自由生成 | MVP 阶段用模板填充，避免 LLM 幻觉；v2 引入 LLM 写作 |
| 分层解耦 | 目标边界统一为 `UI -> Service -> Host -> Agent`。当前确定性 CLI 路径是 UI 直接调用 Service、Service 直接调用 `fund_agent/fund` Agent 层基金能力的过渡实现；未来 Host/Agent 调度接入必须内化 Dayu Host / Engine 的稳定能力，不直接依赖外部 Dayu runtime |
| 基金类型判断优先 | 必须先识别标准基金类型，再应用对应 `preferred_lens` 与 `ITEM_RULE` |
| 工程基线可复现 | Python `>=3.11`；打包、元数据、测试、lint、format 和可选开发依赖以 `pyproject.toml` 为单一入口；吸收 Dayu 工程化、配置、贡献和边界纪律，但不吸收 Dayu 运行时 |

### 1.3 非目标

- 不做全市场横向比较（MVP 在精选基金池内做质量门控）
- 不做实时行为偏差检测（改为买入前检查清单）
- 不把当前有知有行公开页面抓取视为长期温度计真源（当前只读查询是过渡能力；P19 已决策在本项目内开发自建温度计计算与数据契约）
- 不把温度计数值无边界地映射为 `valuation_state`。P19-S3 后只允许在 exact benchmark identity 命中当前支持指数时自动映射；用户显式输入始终优先，缺失、主动/债券/QDII/FOF、派生指数、多个权益指数或无法精确归类基准必须保持 `unavailable` 灰灯，并保留审计证据。
- 不做组合管理（v2 阶段）
- 不输出买卖建议或仓位比例
- 不在当前确定性 `analyze` / `checklist` 主链路中临时拼接 Host、tool loop 或 LLM 写作。若后续进入 Agent 化路径，Host 层必须内化 Dayu Host 的 run lifecycle / deadline / cancel / terminal state / safe diagnostics / event-outbox 能力，Agent 执行内核必须内化 Dayu Engine 的 runner / tool loop / ToolRegistry / ToolTrace / context budget 能力，并先完成四层契约、事件流、失败语义、测试和必要 license/compliance gate。

---

## 2. 系统架构

### 2.1 架构边界

```text
UI → Service → Host → Agent
```

| 层级 | 职责 | 实现 | 边界约束 |
|------|------|------|---------|
| **UI** | 用户交互界面、报告渲染、可视化展示 | 当前为 `fund_agent/ui/cli.py`（Typer） | 只依赖 Service 层接口；不得直接调用 Host 或 Agent 内部模块 |
| **Service** | 业务用例编排、场景定义、prompt/ExecutionContract 组装、用户会话语义、报告生成、质量策略选择 | `fund_agent/services/` | 调用 Host 执行 Agent；当前确定性过渡路径可直接调用 `fund_agent/fund` 公开能力；不得直接读取年报文件/PDF/cache 或具体来源 |
| **Host** | Agent session/run 生命周期、并发、超时、取消、恢复、memory、reply outbox、事件投递、ExecutionDeliveryContext | `fund_agent/host` 当前提供最小进程内 Host runtime runner；尚未提供 durable session/resume/memory/reply outbox | 实现必须内化 Dayu Host 稳定能力；不得直接依赖 `dayu-agent` / `dayu.host` 生产 runtime；不得实现工具或基金分析 |
| **Agent** | Agent 执行、tool loop、runner、ToolRegistry、ToolTrace、context budget、工具调用、基金领域能力、审计规则 | `fund_agent/agent` 当前提供 no-live body-chapter contracts、ToolTrace、Fund adapters、repair policy、body runner 和 `FinalAssemblyReadiness`；`fund_agent/fund/` 是当前基金领域能力包 | Agent 执行内核必须内化 Dayu Engine 稳定能力；不得直接依赖 `dayu-agent` / `dayu.engine` 生产 runtime；当前 Slice E 只覆盖 no-live body-chapter mechanics，full production tool-loop/retry/budget/ToolRegistry/live runtime expansion 仍是未来 scope |
| **Config** | 默认配置与 typed env config | `fund_agent/config/paths.py`、`fund_agent/config/llm.py` | 不读取 prompt manifest、scene registry、workspace runtime 状态或 Host/Agent 配置；LLM env config 只服务显式 `--use-llm` |

> **当前实现裁决**：MVP 默认路径采用纯 Python 确定性管线，不依赖 LLM。当前默认 CLI 走 UI → Service，Service 直接调用 `fund_agent/fund` 的公开能力；这是未接入 Host/Agent 调度的过渡实现。Route C `analyze --use-llm` 是显式 opt-in：CLI 只表达用户 opt-in 并调用 Service hosted LLM 用例；Service 构造 `FundLLMExecutionRequest` / `FundLLMExecutionContract`、provider-backed writer/auditor Protocol clients 和 runtime plan，并把同步 operation closure、`fund_analysis_llm_report` 和 `runtime_plan.host_timeout_seconds` 交给本地 Host runner；Host 只治理生命周期、deadline/cancel、终态、phase events 和安全诊断；Service 通过 bridge 调用当前 Agent body runner，再由 Agent 调用 Fund writer/auditor primitives。任何新增 durable session/resume/memory/reply outbox 能力必须继续进入 Host 并在本项目内实现；任何超出 Slice E no-live body-chapter mechanics 的完整 tool loop、retry/budget、ToolRegistry 或 live runtime expansion 必须继续进入 Agent 并在本项目内实现。

> **Dayu 裁决**：四层架构采用 Dayu 手册口径作为架构参考。Dayu 是能力来源和研究输入，不是生产 runtime 直接依赖；不得把 `dayu-agent` 作为本项目生产依赖，也不得直接 import `dayu.host` / `dayu.engine` 承担生产执行。Host/Agent 接入属于新的架构 gate，必须先定义本项目内化契约、生命周期边界、ToolTrace/事件流、失败语义和测试。如复制或改写上游 Dayu 代码，必须先经过独立 license/compliance gate。

> **已接受并部分实现的 Agent engine / typed audit contract 裁决**：`MVP internalized Agent engine and typed audit contract design gate` 与后续 `MVP internalized Agent engine/tool-loop contract execution design gate` 先前接受为 future architecture；Slice E 已落地第一段 no-live body-chapter mechanics。当前代码事实是：Gate 3 `ChapterOrchestrator` 仍做 Service 输入校验与结果投影，但通过 `fund_agent/services/agent_bridge.py` 调用 `fund_agent/agent` body runner；`fund_agent/agent` 当前拥有 `AgentReportRun`、`ChapterTask`、attempt ledger、safe `ToolTrace`、Fund tool adapters、repair policy 和 `FinalAssemblyReadiness` for body chapters 1-6。Service 保留 use case、ExecutionContract、quality policy、报告策略、provider config parsing / provider construction、runtime ceilings、Host context translation 和 final product fail-closed mapping。Provider writer/auditor clients 由 Service 构造并作为 explicit per-run typed fields 注入 Agent policy/input，再由 Agent adapter 传给 Fund tools；它们不是 ToolRegistry tool、pseudo-tool 或 `extra_payload`。Fund 作为 Agent 层领域包提供 typed writer、programmatic audit、bounded semantic LLM audit adapter、derived `EvidenceAvailability` 和 `RepairSemantics`；`EvidenceAvailability` 是基于 same-source `ChapterFactProjection` 的预计算派生输入，不是 registry tool。当前 Agent runner observes Host cancel/deadline at task scheduling boundaries and after tool-call return through Service bridge translation; mid-tool-call interruption relies on provider client timeout。未来仍未实现的是 full production Agent task graph/tool-loop/retry/budget/ToolRegistry/context budget/live runtime expansion、chapter 0/7 LLM polish、Evidence Confirm、multi-model writer/auditor split 和 durable runtime integration；这些不得被写成当前事实，也不得夹带 Ch3-only calibration 或 provider budget/default changes。

> **当前已实现的 multi-year annual evidence / productization 裁决**：`MVP multi-year annual analysis productization implementation gate` 已接受为当前代码事实。`FundDocumentRepository.load_annual_report()` 仍是唯一年报仓库入口；`FundDataExtractor.extract()` 和 `StructuredFundDataBundle` 仍是 target year 单年 canonical structured data source，不被多年 bundle 替代。Service 通过 `MultiYearAnnualAnalysisRequest` 和 `FundAnalysisService.analyze_multi_year_annual()` 显式声明 target/current/prior 年份、refresh policy 和 quality gate 参数，并翻译为 Fund-owned `AnnualEvidenceScopeRequest`；Service 不直接调用 repository/cache/PDF/source helper，也不通过 `extra_payload` 传递业务参数。Fund 通过 `AnnualEvidenceLoader` 加载 optional prior 年报，构造 additive `AnnualEvidenceBundle`，保留 current-year `StructuredFundDataBundle`，包含 year records、available/gap/fail-closed years、source provenance、safe document identity、anchors、data gaps、requirement availability、cross-year facts、degradation summary 和 fallback summary。MVP scope 限定为 target year plus up to four immediately preceding annual reports, `max_years=5`；target year failure 仍由单年 `analyze()` fail closed；optional prior year `not_found` / `unavailable` 产生 year-level gap；optional prior year `schema_drift` / `identity_mismatch` / `integrity_error` 产生 failed-closed year record 并阻断依赖该年的 cross-year claims。Prior 年份只调用 `extract_profile()`、`extract_manager_ownership()` 和 `extract_holdings_share_change()` 窄字段 extractor，不调用 full `FundDataExtractor.extract()`，不触发多年 NAV/drawdown。`ChapterFactProvider.project_annual_evidence()` 继续输出 `chapter_fact_projection.v1`，公开章节 id 仍是 `0-7`；eligible cross-year facts 只进入第 5 章，source field id 使用 `annual_evidence.cross_year.*`，并在有可用 facts 时替换 `cross_period_comparison_missing`，没有可用 facts 时保留原缺口语义。当前 CLI 入口是 `fund-analysis analyze-annual-period`，stdout 输出 target-year Markdown，stderr 输出质量 gate 与多年 evidence summary；完整跨年叙事 writer/reporting、structured-data source identity extension、live 2021-2025 EID/PDF proof、quarterly/interim/prospectus/fund contract、多年 NAV/drawdown、Ch2 public split、provider budget、score-loop、新 source strategy 和 cache/PDF API exposure 均仍是未来 scope。

> **Dayu 手册映射裁决**：Dayu 的 `UI -> Service -> Host -> Agent` 就是本项目目标分层。Dayu Fins 只类比本项目 Agent 层的 `fund_agent/fund` 领域能力包，不单独成为系统基础设施层；Dayu config 手册只提供“默认配置 + workspace 覆盖 + prompt 资产分层”的配置纪律；Dayu CONTRIBUTING 提供第一性原理、root cause 同源、边界说明、测试与文档同步的贡献纪律。

> **显式参数裁决**：Dayu 手册中的 `extra_payloads` 只能作为未来 provider 扩展参数参考；本项目任何业务参数、基金代码、年份、估值状态、缓存策略、来源选择、scene、tool 或审计开关都必须在 typed request / contract / config 中显式声明，禁止塞进 `extra_payload` 或自由 dict。

> **目录事实裁决**：`fund_agent/config` 的存在不代表 prompt manifest、scene registry 或 Dayu config runtime 已接入；当前已创建 `fund_agent/host` 最小 runtime governance 包；当前已创建 `fund_agent/agent` no-live body-chapter execution package；空目录、本地未跟踪草案或审计输入不能单独作为设计事实。

### 2.2 当前确定性执行链路

```
CLI（Typer app）
  → FundAnalysisService.analyze/checklist(request)
    → FundDataExtractor.extract(fund_code, year)  # P1 结构化抽取
      → FundDocumentRepository.load_annual_report()  # 文档仓库
        → documents layer source orchestration and cache internals
      → extract_profile / extract_performance / ...  # 章节 extractor
      → FundNavDataAdapter.load_nav_data()  # 净值数据；失败时降级为 unavailable，不阻断年报抽取
    → run_quality_gate_for_bundle(bundle)  # 质量门控（可选，在 P2 分析之前）
    → judge_alpha_nature / calculate_r_abc / check_consistency / ...  # P2 分析计算
    → render_template_report(render_input)  # analyze 专用模板渲染
    → run_programmatic_audit(audit_input)  # analyze 专用程序审计
  → stdout 输出报告 Markdown
```

**Service 层服务清单**（7 个）：

| 服务 | 文件 | 职责 |
|------|------|------|
| `FundAnalysisService` | `fund_analysis_service.py` | 主分析用例编排（P1 抽取 → P2 分析 → 模板渲染 → 审计） |
| `ExtractionSnapshotService` | `extraction_snapshot_service.py` | 精选基金池字段级抽取快照 |
| `ExtractionScoreService` | `extraction_score_service.py` | 字段级 coverage / traceability / correctness 评分 |
| `QualityGateService` | `quality_gate_service.py` | 报告质量门控（FQ0-FQ6 规则） |
| `GoldenPrefillService` | `golden_prefill_service.py` | golden answer 预填底稿生成 |
| `GoldenAnswerService` | `golden_answer_service.py` | golden answer Markdown → JSON 转换 |
| `ThermometerService` | `thermometer_service.py` | 有知有行温度计数据查询 |

**Service 层关键类型**：

| 类型 | 说明 |
|------|------|
| `FinalJudgment` | `Literal["worth_holding", "needs_attention", "suggest_replace"]` |
| `FinalJudgmentDecision` | 最终判断选择结果，包含 `selected_judgment`（实际采用）、`derived_judgment`（系统派生）、`source`（来源：derived/developer_override）、冲突原因 |
| `AnalyzeMode` | `Literal["product", "developer_override"]` |
| `FundAnalysisDeveloperOverrides` | 开发覆盖参数（最终判断、股票仓位、实际风格等） |
| `QualityGatePolicy` | `Literal["off", "warn", "block"]` |

`quality_gate_policy=block` 是 `analyze` 默认策略；低质量或 not-run gate 以结构化异常阻断并由 CLI 返回退出码 2。当前 `--use-llm` 有本地 `HostRunResult` 终态摘要；默认确定性路径仍没有 `AgentInput` / scene preparation 主链路。

`command_source` 当前只允许 `analyze / checklist`，用于默认 quality gate run id 和 artifact path 命名。`FundAnalysisService.analyze()` 与 `FundAnalysisService.checklist()` 是该字段的权威归一化边界；调用方传入冲突值时，Service 会按实际方法覆盖为对应来源。显式 `quality_gate_run_id` 仍优先于默认命名。

> **边界裁决**：上图描述当前代码事实。当前已为 `--use-llm` 接入最小 Host run 包裹，并通过 Service bridge 接入 Slice E no-live Agent body runner；这不等同于 full production Agent tool-loop/retry/budget/ToolRegistry/live runtime。不得引入未使用的 Dayu runtime 依赖。

### 2.3 核心契约

| 契约 | 方向 | 说明 |
|------|------|------|
| `FundAnalysisRequest` | UI → Service | 基金代码、年报年份、分析参数、质量 gate 策略和 `command_source`；开发覆盖参数通过 `FundAnalysisDeveloperOverrides` 且只能在 `developer_override` mode 生效 |
| `FundAnalysisResult` | Service → UI | 报告 Markdown、最终判断选择契约、质量 gate 摘要、审计结果 |
| `MultiYearAnnualAnalysisRequest` | UI → Service | 多年年报产品请求，显式声明 `target_year`、`start_year`、`max_years`、刷新策略、分析参数和 quality gate 策略 |
| `MultiYearAnnualAnalysisResult` | Service → UI | target-year 单年分析结果、Fund-owned `AnnualEvidenceBundle`、available/gap/fail-closed 年份摘要 |
| `ValuationState` | Service 类型 | `Literal["low", "fair", "high", "unavailable"]` |
| `MoneyHorizon` | Service 类型 | `Literal["long_enough", "uncertain", "too_short"]` |
| `StructuredFundDataBundle` | Agent 内部 | P1 结构化数据包，聚合结构化年报抽取字段与 `NavDataResult` |
| `FinalJudgmentDecision` | Agent → Service/renderer/audit | 根据检查清单、否决项、压力测试和 quality gate 派生；开发覆盖只改变 `selected`，冲突交给 R2 审计 |
| `TemplateRenderInput` | Service → Agent renderer | P1/P2 结构化结果、`FinalJudgmentDecision`、当前阶段说明 |
| `TemplateRenderResult` | Agent renderer → Service | 8 章 Markdown、程序审计输入、章节块、lens 应用计划 |
| `ProgrammaticAuditInput` / `ProgrammaticAuditResult` | Agent renderer ↔ Agent audit | 程序审计输入与结果，覆盖章节结构、证据、R=A+B-C、检查清单和 selected/derived/source 最终判断一致性 |
| `QualityGateResult` | Agent quality gate → Service/UI | `pass / warn / block`、issue 列表、JSON/Markdown 产物路径 |

**依赖注入模式**：Service 层通过 Protocol 定义依赖（如 `_FundDataExtractor`、`_AnnualReportRepository`），生产使用真实实现，测试注入 fake。

---

## 3. 定性分析模板

### 3.1 模板结构（8 章）

| 章 | 标题 | 核心问题 | 数据来源 |
|----|------|---------|---------|
| 0 | 投资要点概览 | 这是什么基金？好不好？ | 后续章节汇总 |
| 1 | 这只基金到底是什么产品 | 买的是什么？怎么赚钱？ | 年报§1/§2 |
| 2 | R=A+B-C 收益归因 | 钱是怎么赚到的？ | 年报§3 + 净值数据 |
| 3 | 基金经理画像与言行一致性 | 基金经理靠不靠谱？ | 年报§4（说）vs §8（做） |
| 4 | 投资者获得感 | 买了的人赚到钱了吗？ | 年报§3（2026新规）+ §10 |
| 5 | 当前阶段与关键变化 | 为什么偏偏是现在？ | 跨期年报对比 |
| 6 | 核心风险与否决项 | 什么情况下直接放弃？ | 年报§2/§9 + 天天基金 |
| 7 | 是否值得持有——最终判断 | 结论是什么？ | 后续章节汇总 |

### 3.2 CHAPTER_CONTRACT 机制

**代码实现**：`docs/fund-analysis-template-draft.md` canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 是 authored template contract truth source；`fund_agent/fund/template/contracts.py` 解析、投影并验证 untyped `TemplateContractManifest`；`fund_agent/fund/template/typed_contracts.py` 从同一 JSON 投影并验证 typed dataclasses；dev-only 可执行 sidecar 在 `fund_agent/fund/template/chapter_contract_constraints.py`。

每个章节都有 `ChapterContract` dataclass，定义：

- `chapter_id`：章节编号（0-7）
- `title`：章节标题
- `narrative_mode`：叙事模式（封面→动作→验证 / 拆解→判断→成本 / ...）
- `must_answer`：必须回答的问题列表
- `must_not_cover`：禁止覆盖的内容
- `required_output_items`：必须输出的条目
- `preferred_lens`：按基金类型动态适配的分析视角（`Mapping[str, TemplateLensRule]`）

**机器契约清单**：`TemplateContractManifest` 聚合 8 章 `ChapterContract`，其 authored 内容来自 `docs/fund-analysis-template-draft.md` 中唯一 canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` block；`contracts.py` 提供 `load_template_contract_manifest()` 和 `validate_template_contract_manifest()`，负责 strict parse / projection / validation，不再维护平行 Python-authored 章节文本或 lens truth。

**preferred_lens 规则**：`TemplateLensRule` 包含 `fund_type`、`statements`、`facets_any`、`priority` 字段。通过 `resolve_preferred_lens(manifest, fund_type)` 获取当前基金类型的 lens 规则。

**可执行 sidecar**：`ChapterContractConstraintManifest` 包裹既有 `TemplateContractManifest`，默认覆盖第 0-7 章并复制既有 `must_answer` / `must_not_cover`，避免形成平行章节真源。当前 material 实现只覆盖 `active_fund` 第 3 章换手率 / 风格变化证据约束：若缺少已复核事实和可解析证据锚点，报告不得输出风格稳定、风格一致或言行一致正向判断；若仅有兼容 `data_gap`，必须明示证据不足和下一步最小验证问题。增强指数第 2 章和债券第 6 章仅登记为 deferred `config_only` 要求。

**dev-only 写作审计**：`fund_agent/fund/report_writing_audit.py` 只消费调用方显式传入的 `ReportEvidenceBundle`、已解析 records 和 `ChapterDraftSurrogate`，输出 deterministic issue list / summary / failure category / evidence requirement gaps。它不读取基金文档、不调用 `FundDocumentRepository`、不接入 renderer、Service/CLI 默认链路、FQ0-FQ6 quality gate、Host/Agent 或 Dayu runtime。

**当前已实现：active-fund 第 3 章 renderer 最小输出契约**：`fund_agent/fund/template/renderer.py` 当前只在 `active_fund` 第 3 章实现缺证据降级措辞。当 renderer 输入缺少显式已复核换手率或跨期风格变化证据时，不输出风格稳定、风格一致或言行一致正向判断，而是明示 `证据不足`，说明不能据此判断风格稳定 / 风格一致 / 言行一致，并给出复核年报§8换手率及跨期行业配置 / 持仓集中度变化的下一步最小验证问题。该实现不接入 dev-only audit 到 renderer，不改变 Service/CLI、FQ0-FQ6、默认入口、参数、退出码或 Service 控制流，也不扩大到增强指数第 2 章或债券第 6 章。由于当前 renderer 输入没有显式 reviewed turnover/style evidence 状态，当前实现把 active-fund 第 3 章视为 missing-reviewed-evidence 默认路径；任何正向 reviewed-evidence 分支仍属于已接受的未来设计，必须先进入单独 input-contract design gate。

**当前已实现：typed template truth-source replacement**：`MVP typed template truth-source replacement gate` Slices 1-4 已接受为当前代码事实。`docs/fund-analysis-template-draft.md` 中唯一 canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` block 现在是 Fund template contract 的 authored truth source，覆盖当前 untyped `TemplateContractManifest` projection 和 typed `typed_chapter_contract.v1` projection；可见 per-chapter `CHAPTER_CONTRACT_REF` 只是非权威引用，不重复结构化契约。`contracts.py` 从该 JSON 解析、投影并验证当前 untyped manifest；`typed_contracts.py` 从同一 JSON 投影并验证 typed `TypedChapterContract` dataclasses，不再维护 code-authored stable id/text mapping、audit focus、missing behavior、Ch2 internal subcontract truth、Ch0/Ch7 dependency metadata 或 Ch3 evidence predicate。当前 chapter id 范围继续是 `0-7`，不得把 `0+9` / `0+10` 或 Ch2 公开拆章写成当前事实；Ch2 `performance / attribution / cost` 只作为 `chapter_id=2` 内部 typed subcontracts。Ch0 记录 `consumes_chapter_conclusions=(7,)` 且 `independent_action_source=False`，`RequiredOutputItem.when_evidence_missing` 为第 2/3 章 typed writer path 提供 `block / render_evidence_gap / render_minimum_verification_question / delete_if_not_applicable` 缺证行为数据，`audit_focus` 是 closed-set bounded semantic audit input，不能关闭 programmatic blockers、改变阻断等级或修复预算。

**当前已实现：same-source EvidenceAvailability 与 typed audit/writer 消费**：`fund_agent/fund/evidence_availability.py` 提供 additive `evidence_availability.v1`，只从 same-source `ChapterFactProjection`、facts、anchors、missing reasons 和 typed requirement ids 派生 `available / missing / unavailable / not_applicable / unreviewed`，不读取文档仓库、PDF/cache/source helper、Service、Host、provider、retained report、文件系统、环境变量或 dayu，也不替代 `ChapterFactProjection`。Fund writer 可在显式 typed path 中消费 typed required-output items 与 `EvidenceAvailability`，在 LLM client 调用前 fail-closed 执行 `block`，并要求 gap / minimum verification question 使用 approved 缺口或下一步最小验证问题措辞。Fund programmatic auditor 当前覆盖 Ch3 `ch3.must_not_cover.item_04` evidence-conditional 禁区：当实际行为/风格证据 missing、unavailable 或 unreviewed 时，required label 与显式证据缺口句可通过，正向或准正向 `言行一致` / `风格稳定` 判断触发稳定 C2 issue；缺少 `EvidenceAvailability` 时 unsafe 正向/准正向判断仍 fail-closed。LLM auditor 只接收 bounded `audit_focus` 作为语义关注点；programmatic audit 不读取 focus。

**当前已实现：Service explicit typed path wiring**：Service-owned `typed_template_path` 已作为显式字段存在于 `ChapterOrchestrationPolicy`、`FundLLMRuntimePlan` 和 `FundLLMExecutionRequest`；runtime plan 与 request 校验要求 typed path 一致。`build_fund_llm_execution_request()` 只在显式 `fund-analysis analyze --use-llm` provider-backed path 选择 `typed_template_contract`；default deterministic `analyze/checklist` 不构造该 LLM execution request。当前 `ChapterOrchestrator` 仍是 Service-owned transition façade：在 typed path 派生 same-source `EvidenceAvailability`，把 typed required-output items / availability 传给 initial 和 repair writer input，并把 typed chapter contract / `audit_focus` 传给 auditor input；legacy path 不传 typed inputs，保持旧 required-output 行为 inactive。Host 仍 business-opaque，只接收 generic operation/deadline/session 字段。

**仍未实现 / 非目标**：template truth-source replacement 只改变 authored template contract truth 的位置和 parser/projection authority；不改变 current deterministic `analyze/checklist`、renderer Markdown 输出、FQ0-FQ6 quality gate、final judgment、provider budget/default/runtime、score-loop、golden/readiness、snapshot 或 promotion state。Full production Agent tool-loop/retry/budget/ToolRegistry/live runtime expansion、typed audit runtime expansion beyond current no-live body-chapter mechanics、full cross-year narrative writer/reporting、Ch2 public split、`source_strength_by_requirement`、full facet wiring、provider live probe/default change、chapter acceptance calibration 和 score-loop remain separate future gates。

### 3.3 ITEM_RULE 机制

**代码实现**：`fund_agent/fund/template/item_rules.py`

条件型条目——某些内容只在特定条件下出现：

- `mode: optional`：有披露就写，无披露写"未披露"（`missing_behavior: render_unavailable`）
- `mode: conditional`：有披露就写，无披露**必须删除整段**（`missing_behavior: delete_segment`）
- `facets_any`：条件触发（如 `facets_any: [主动权益基金]`）
- `fund_types_any`：由 facets 确定性映射的标准基金类型（如 `("active_fund",)`）
- `segment_markers_any`：用于定位已渲染段落的唯一小节标记

**已实现的 ITEM_RULE**（4 条）：

| rule_id | 章节 | 条目 | 触发条件 |
|---------|------|------|---------|
| `chapter_1_index_constituents` | 1 | 指数编制规则与成分股 | 指数基金（含增强） |
| `chapter_1_manager_philosophy` | 1 | 基金经理投资哲学 | 主动基金 |
| `chapter_2_alpha_yearly_breakdown` | 2 | 超额收益分年度拆解 | 主动基金 + 指数增强 |
| `chapter_2_tracking_error_analysis` | 2 | 跟踪误差分析 | 指数基金 + 指数增强 |

**评估机制**：`evaluate_template_item_rules(fund_type, facets=())` 返回 `TemplateItemRuleDecision` 列表，每条包含 `triggered`、`status`（render/delete）、`reason`。

**ITEM_RULE 审计 API**：

| 函数/类型 | 说明 |
|-----------|------|
| `evaluate_template_item_rule(rule, fund_type, facets=())` | 单条 ITEM_RULE 评估，返回 `TemplateItemRuleDecision` |
| `TemplateItemRuleAuditContext` | 审计上下文：`Literal["identity_missing", "identity_present"]` |
| `rendered_segment_present(markdown, rule)` | 判断渲染后的 Markdown 是否包含某条 ITEM_RULE 的唯一段落标记 |

**评估结果验证**：renderer 在渲染后调用 `_validate_template_item_rule_decisions()`，确保：
- 触发的 conditional 规则（`status="render"`）在最终 Markdown 中有对应段落标记
- 未触发的 conditional 规则（`status="delete"`）在最终 Markdown 中无对应段落标记
- 缺证章节在证据附录中显式标注

### 3.4 preferred_lens 机制

**代码实现**：`fund_agent/fund/fund_type.py` + `fund_agent/fund/template/contracts.py`

按基金类型动态调整分析重点：

| 基金类型 | FundType 标识 | 优先分析视角 |
|---------|-------------|-------------|
| 宽基指数基金 | `index_fund` | 跟踪误差、费率、规模流动性 |
| 行业/主题指数基金 | `index_fund` | 跟踪误差、行业集中度 |
| 策略指数基金 | `index_fund` | 跟踪误差、策略纯度 |
| 指数增强基金 | `enhanced_index` | 超额收益来源、跟踪误差 |
| 主动权益基金 | `active_fund` | 超额收益稳定性、基金经理、言行一致性 |
| 债券基金 | `bond_fund` | 信用风险、久期、最大回撤 |
| QDII 基金 | `qdii_fund` | 汇率风险、境外市场暴露 |
| FOF 基金 | `fof_fund` | 子基金质量、双重收费 |

**preferred_lens 确定性应用**（P8）：

renderer 通过 Agent 层基金能力 `LensApplicationPlan` 消费 `preferred_lens`：

| 组件 | 说明 |
|------|------|
| `LensFocusLabels` | 标准基金类型的确定性关注点标签（`primary_focus`、`watch_variable_label`、`risk_focus_label`） |
| `LensChapterApplication` | 单章 lens 应用事实（`chapter_id`、`lens_key`、`used_default`、`primary_focus` 等） |
| `LensApplicationPlan` | 聚合 8 章 lens 应用事实，供 renderer 消费 |
| `build_lens_application_plan(fund_type, chapter_ids=(0,1,2,3,4,5,6,7))` | 构建 lens 应用计划 |

当前确定性应用范围：第 0 章"当前最值得盯住的变量"和第 1 章"看这类基金最先看什么"使用 normalized 关注点标签填充报告 slot。Quality gate 的 FQ5 证明模板契约适用性，不证明 renderer 已完整执行 lens 语义。

---

## 4. 分析引擎

### 4.1 R=A+B-C 计算器

**代码实现**：`fund_agent/fund/analysis/r_abc.py` + `fund_agent/fund/analysis/_ratios.py`

```
R（总收益）= 基金净值增长率
B（Beta）= 业绩基准收益率 × 股票仓位
A（Alpha）= R - B
C（Cost）= 管理费 + 托管费 + 换手率 × 0.3%
净超额 = A - C
```

**公开接口**：
- `calculate_r_abc(input: RabcInput) -> RabcAttribution`
- `calculate_r_abc_from_bundle(bundle: StructuredFundDataBundle) -> tuple[RabcAttribution, ...]`
- `calculate_r_abc_series(...) -> tuple[RabcAttribution, ...]`

**关键区分**：结构性超额（可持续的能力）vs 阶段性超额（风格顺风/运气）

| 特征 | 结构性超额 | 阶段性超额 |
|------|-----------|-----------|
| 多年度为正 | 4/5 年以上 | 集中在某 1-2 年 |
| 不同市场环境 | 牛熊都为正 | 仅在特定风格顺风时 |
| 来源可解释 | 选股/配置能力 | 无法解释 |

### 4.2 超额收益性质判断

**代码实现**：`fund_agent/fund/analysis/alpha_judge.py`

**公开接口**：`judge_alpha_nature(attributions) -> AlphaJudgment`

基于多年度 R=A+B-C 归因结果，判断超额收益是结构性还是阶段性。输出 `AlphaJudgment` 包含 `rule`（判断规则）、`observations`（逐年观察）。

### 4.3 言行一致性检验

**代码实现**：`fund_agent/fund/analysis/consistency_check.py`

交叉验证年报§4（"说"）和年报§8（"做"）：

| 维度 | §4 宣称 | §8 实际 | 信号 |
|------|--------|--------|------|
| 投资风格 | 风格定位 | 实际持仓风格 | 🟢/🟡/🔴 |
| 行业偏好 | 看好行业 | 重仓行业 | 🟢/🟡/🔴 |
| 仓位管理 | 仓位策略 | 实际仓位 | 🟢/🟡/🔴 |
| 换手水平 | 持有周期 | 换手率 | 🟢/🟡/🔴 |

**公开接口**：`check_consistency(input) -> ConsistencyCheckResult`

### 4.4 投资者获得感分析

**代码实现**：`fund_agent/fund/analysis/investor_return.py`

```
行为损益 = 投资者实际收益 - 基金产品收益
```

- 数据来源：年报§3（2026 新规要求披露加权平均投资者收益率）
- 备用方案：份额变动 × 净值变化估算

**公开接口**：
- `analyze_investor_experience(input) -> InvestorExperienceResult`
- `calculate_behavior_gap(input) -> BehaviorGapResult`
- `judge_fund_flow(input) -> FundFlowResult`

### 4.5 否决项检查

**代码实现**：`fund_agent/fund/analysis/risk_check.py`

| 风险项 | 否决条件 |
|--------|---------|
| 清盘风险 | 规模 < 5000 万 |
| 基金经理离职 | 管理本基金 < 6 个月 |
| 风格严重漂移 | 言行一致性检验 🔴 |
| 费率远超同类 | 总成本 > 同类 2 倍中位数 |
| 跟踪误差过大 | 指数基金 > 2% |

**公开接口**：`run_risk_checks(input) -> RiskCheckResult`

### 4.6 压力测试

**代码实现**：`fund_agent/fund/analysis/risk_check.py`（同上）

模拟 -20%/-40%/-60% 三个场景（借鉴 E大网格策略理念）。按基金类型使用差异化阈值。

**公开接口**：`run_stress_test(input) -> StressTestResult`

### 4.7 买入前检查清单

**代码实现**：`fund_agent/fund/analysis/checklist.py`

7 个问题，红/黄/绿灯判定：

| # | 问题 | 数据来源 |
|---|------|---------|
| 1 | 超额收益能覆盖成本吗？ | R=A+B-C |
| 2 | 基金经理跟我一条心吗？ | 年报§9 |
| 3 | 投资者真的赚到钱了吗？ | 年报§3 |
| 4 | 说的和做的一样吗？ | §4 vs §8 |
| 5 | 这只基金"不死"吗？ | 天天基金 |
| 6 | 当前估值处于什么位置？ | 温度计 |
| 7 | 这笔钱 3-4 年内不会用吗？ | 用户输入 |

**公开接口**：`run_checklist(input) -> ChecklistResult`

### 4.8 最终判断派生（P10）

**代码实现**：`fund_agent/fund/analysis/final_judgment.py`

最终判断由 Agent 层基金 policy 派生，不直接由用户输入或开发覆盖决定：

| 条件 | 派生判断 | 说明 |
|------|---------|------|
| 否决项存在、检查清单红灯、基础 -20% 压力场景越过用户承受能力 | `suggest_replace` | 必须建议替换 |
| 质量 gate block/not-run、黄灯/灰灯/数据不足、watch 项 | `needs_attention` | 需要关注 |
| 检查清单全绿、否决项通过、质量 gate pass/warn、压力测试未越界 | `worth_holding` | 值得持有 |
| 未命中更明确条件 | `needs_attention` | fail-safe 默认 |

**开发覆盖模式**（`developer_override`）：
- 只允许在 `AnalyzeMode.DEVELOPER_OVERRIDE` 下生效
- 覆盖只改变 `selected_judgment`，不改变 `derived_judgment`
- 覆盖与派生不一致时，记录 `conflict_reasons` 供 R2 审计使用

**当前实现核查（2026-05-24）**：
- `FundAnalysisService._run_analysis_core()` 是 `analyze` 与 `checklist` 的唯一共享确定性分析核心；质量 gate、检查清单、压力测试和最终判断同源，禁止 checklist 另写一套判断规则。
- Service 先运行 `run_quality_gate_for_bundle()`，再把结果归一化为 `pass / warn / block / not_run` 传入 `derive_final_judgment()`；`quality_gate_policy=block` 时，`block` 或 `not_run` 会先以结构化异常阻断输出。
- `derive_final_judgment()` 的优先级是 `suggest_replace` 高于 `needs_attention` 高于 `worth_holding`；否决项、检查清单红灯、基础 `minus_20` 压力场景越界会进入 `suggest_replace`；质量 gate `block/not_run`、黄灯/灰灯、watch 项或压力测试接近边界会进入 `needs_attention`；只有检查清单全绿、否决项通过、quality gate `pass/warn` 且压力测试不过界时才进入 `worth_holding`。`quality_gate_status="warn"` 是可继续的数据质量警告，不会单独把 otherwise-green 产品降为 `needs_attention`。
- quality gate 数据质量问题不直接升级为 `suggest_replace`；这是第一性原理约束：数据质量不足说明“不应自信判断”，不是产品本身应替换的证据。

**最终判断优先级表**：

| 优先级 | 触发条件 | 派生判断 | 说明 |
|--------|----------|----------|------|
| 1 | 否决项存在、检查清单红灯、基础 `minus_20` 压力场景越过用户承受能力 | `suggest_replace` | 产品或用户承受能力出现同源否决证据 |
| 2 | quality gate `block/not_run`、风险 watch、检查清单黄/灰、压力测试接近边界或非基础极端场景越界 | `needs_attention` | 证据不足或存在需最小验证的问题 |
| 3 | 检查清单全绿、否决项通过、无风险 watch、quality gate `pass/warn`、压力测试不过界 | `worth_holding` | 当前证据支持持有；`warn` 只提示数据质量警告 |
| fail-safe | 未命中以上明确条件 | `needs_attention` | 禁止在证据不完备时默认乐观 |

**公开接口**：
- `derive_final_judgment(checklist_result, risk_check_result, stress_test_result, quality_gate_status, ...) -> FinalJudgmentDecision`

---

## 5. 审计机制

### 5.1 三层审计架构

```
程序审计（P1/P2/P3/C2/L1/R1/R2 规则，已实现）
  → LLM 审计（证据充分性 + 内容合规性，v2）
    → 证据复核（年报 PDF 搜索验证，v2）
```

### 5.2 审计规则体系

**代码实现**：
- `fund_agent/fund/audit/audit_programmatic.py`—— 程序审计执行器
- `fund_agent/fund/audit/contract_rules.py`—— CHAPTER_CONTRACT C2 审计规则

**规则码口径**：P/C/L/R/E 审计规则码描述报告级三层审计目标，不等同于 quality gate 的 FQ0-FQ6 字段质量规则。当前 MVP 只执行确定性的程序审计规则 `P1/P2/P3/C2/L1/R1/R2`；`E1/E2/E3/C1/L2` 是后续 LLM 审计、Evidence Confirm 或语义复核目标，不进入当前 `ProgrammaticAuditResult.checked_rules`，也不得在文档或测试中把未运行规则描述为已通过。

| 规则码 | 含义 | 阻断级别 | MVP 阶段 | 代码位置 |
|--------|------|----------|---------|---------|
| P1 | 章节结构不匹配 | 阻断 | ✅ 实现 | `audit_programmatic.py` |
| P2 | 内容过短（<10字符） | 阻断 | ✅ 实现 | `audit_programmatic.py` |
| P3 | 缺少"证据与出处"小节 | 阻断 | ✅ 实现 | `audit_programmatic.py` |
| C2 | 章节越界（展开禁止话题） | 阻断 | ✅ 实现 | `contract_rules.py` |
| L1 | R=A+B-C 计算错误 | 阻断 | ✅ 实现 | `audit_programmatic.py` |
| R1 | 检查清单规则错误 | 阻断 | ✅ 实现 | `audit_programmatic.py` |
| R2 | 判定与评分不一致 | 阻断 | ✅ 实现 | `audit_programmatic.py` |
| E1 | 证据锚点不精确 | 可复核 | ⬜ v2 | — |
| E2 | 证据与断言不匹配 | 可复核 | ⬜ v2 | — |
| E3 | 证据完全缺失 | 需重建 | ⬜ v2 | — |
| C1 | 内容违规（幻觉） | 阻断 | ⬜ v2 | — |
| L2 | 百分位计算错误 | 可复核 | ⬜ v2 | — |

**C2 审计实现细节**（`contract_rules.py`）：
- `ContractRequiredItemRule`：required_output_items 的字面 marker 规则（40+ 条）
- `ContractForbiddenContentRule`：must_not_cover 的字面禁止 marker 规则（9 条）
- `load_programmatic_contract_rules()`：加载并校验规则集合
- 规则通过 `validate_programmatic_contract_rules()` 与 CHAPTER_CONTRACT manifest 交叉校验

**公开接口**：`run_programmatic_audit(input: ProgrammaticAuditInput) -> ProgrammaticAuditResult`

### 5.3 修复闭环机制（v2）

借鉴 Dayu-Agent 的修复策略，根据违规严重程度选择修复粒度：

| 修复策略 | 触发条件 | 说明 |
|---------|---------|------|
| **none** | 审计通过 | 无需修复 |
| **patch** | E1/E2/C2 类违规 | 局部修补（删除断言/修正锚点/补充证据） |
| **regenerate** | P1/P2/P3/E3/C1 类违规 | 整章重建 |

> 详细对照分析见 `docs/audit-alignment.md`。

### 5.4 章节级写作审计闭环（已接受的未来设计）

当前 `fund-analysis analyze` 仍是 v0 确定性 8 章模板渲染：一次性消费结构化抽取、P2 分析、检查清单、最终判断和 quality gate 状态，输出 Markdown 后执行程序审计。该路径保持为当前可用主链路，不声明已经具备 LLM 分章写作、章节级修复或 Dayu Host/Agent 调度。

后续报告质量升级接受 Dayu 的方法论启发：原始文档、系统降噪、结构化事实、批量评分、章节审计；但不得直接依赖外部 `dayu-agent` runtime，也不得绕过本项目 `UI -> Service -> Host -> Agent` 边界。目标是把报告生成从“一次性模板填充”升级为“事实评分可观测 → 章节级写作 → 审计 → 修复/重写 → 总装”的闭环：

```text
Evidence Store / Fact Store
  → ReportQualityBaseline（小样本基准评分）
  → Chapter 1-9 写作
    → 章节规则审计
    → 章节 LLM 审计
    → patch / regenerate / accept
  → Chapter 10 最终判断（只消费 Chapter 1-9 accepted 结论）
  → Chapter 0 总结（只消费 Chapter 1-10 accepted 结论）
  → 全文一致性审计
  → 报告输出
```

**设计原则**：

- 报告质量优化必须先可评分、可复盘，再迭代数据源或模板；不得只凭单份报告体感修改模板或大规模改动抽取脚本。
- 首个实现切片应定义小样本基准集和报告质量评分 schema，而不是直接改写当前 renderer；基准集应覆盖主动、指数、增强指数、债券、QDII/FOF 等代表性基金，优先使用已能通过 `FundDocumentRepository` 获取并人工核验身份的年报。
- 报告质量评分至少覆盖：事实覆盖度、抽取正确性、证据可追溯性、章节契约完整性、最终判断一致性、投资建议边界和可读性；评分结果必须能定位到字段、章节、证据或写作规则，不能只输出总分。
- 数据获取脚本迭代和模板打磨都必须由评分结果驱动：若事实覆盖或抽取正确性不足，优先修复数据/抽取；若事实充分但章节结论弱，才进入模板、章节计划或写作审计优化。
- Fact Store / Evidence Store 是章节写作的唯一事实输入：LLM 写作和审计只能读取结构化 facts、derived calculations、EvidenceAnchor 和明确的数据缺口，不得直接读取 PDF、cache、下载 helper 或外部来源适配器。
- 第 1-9 章先独立写作，每章必须声明输入 facts、必须回答项、禁止覆盖项、证据锚点和章节结论。
- 每条关键判断必须绑定 `EvidenceAnchor` 或 derived 计算来源；没有同源证据时只能写“未披露 / 数据不足 / 下一步最小验证问题”。
- 每章都必须经过规则审计和 LLM 审计；规则审计负责结构、锚点、CHAPTER_CONTRACT / ITEM_RULE、数值闭合与边界条件，LLM 审计负责证据是否支撑断言、语义越界、投资建议措辞和读者可理解性。
- 审计失败必须产生 `RepairDecision`：可局部修复的问题走 patch；证据缺失、章节结构错误、关键逻辑不成立或 LLM 审计判定不可修补时整章 regenerate；修复后必须重新审计。
- 第 10 章最终判断必须后置，只能消费第 1-9 章 accepted 结构化结论和 quality gate 状态，不得由 prompt 自由发挥。
- 第 0 章执行摘要必须最后生成，只能总结第 1-10 章 accepted 结论，不得引入新事实、新证据或新判断。
- LLM 写作、审计和修复不得直接读取 PDF、cache 或来源 helper；所有事实输入必须来自 `FundDocumentRepository` 派生的结构化 evidence/fact store。
- 若未来需要 session/run/cancel/resume/outbox、章节任务并发或写作 agent 调度，必须先开独立 Host/Agent gate：Host 内化 Dayu Host 能力，Agent 执行内核内化 Dayu Engine 能力，并声明事件流、ToolTrace、失败语义、重试策略和测试。
- 当前 8 章模板与未来 0-10 章体系的映射尚未裁决；不得在未完成 design gate 前把当前 renderer 改写为 0-10 章，或把该设计候选描述为已实现。

建议的最小状态机：

| 状态 | 输入 | 输出 | 失败处理 |
|------|------|------|----------|
| `ChapterPlan` | CHAPTER_CONTRACT / facts / evidence | 章节写作约束 | 缺少关键 fact 时先返回数据缺口 |
| `ChapterDraft` | ChapterPlan + 写作器 | 草稿 Markdown + 结构化结论 | 进入规则审计 |
| `RuleAudit` | ChapterDraft | 规则问题列表 | patch 或 regenerate |
| `LLMAudit` | ChapterDraft + evidence bundle | 语义/证据/措辞问题列表 | patch 或 regenerate |
| `AcceptedChapter` | 审计通过草稿 | 可供后续章节消费的结论 | 锁定输入和证据 |
| `ReportAssemblyAudit` | accepted chapters | 全文一致性结果 | 回退到具体章节修复 |

后续评分、数据源迭代、写作脚本迭代和报告质量调参会产生大量本地 run 产物，应落在 `reports/scoring-runs/`、`reports/data-source-runs/`、`reports/writing-runs/` 或临时目录；只有人工复核后要作为长期基准的输入才进入 curated fixture。

#### 5.4.1 已接受的未来设计：MVP LLM report generation route

Route C 是已接受的 MVP LLM report generation 路由，用来把 §5.4 的章节级写作审计闭环拆成可实施 gate。已完成 gate 可作为当前代码事实；未完成 gate 仍是未来设计。当前产品默认实现仍是确定性 `fund-analysis analyze/checklist`，当前确定性 renderer、程序审计、FQ0-FQ6 quality gate 和 CLI 默认入口都不因本设计记录而改变。

**当前已实现状态**：

- `fund-analysis analyze` 和 `fund-analysis checklist` 仍由 UI 调用 Service，Service 直接调用 `fund_agent/fund` 公开能力完成结构化抽取、确定性分析、模板渲染、程序审计和 quality gate。
- Route C Gate 1 的 Fund 层 `ChapterFactProvider` / `project_chapter_facts()` typed projection 已实现为 `chapter_fact_projection.v1`：它只消费 `StructuredFundDataBundle` 与现有 CHAPTER_CONTRACT、preferred_lens、ITEM_RULE API，输出模板第 0-7 章的 facts、证据锚点、缺失/不可用/不适用语义、分类依据、lens 和 ITEM_RULE 决策；它不读取文档仓库、PDF、cache、source helper、下载器或 parser，不调用 LLM、Service、Host 或 dayu。
- Route C Gate 2 的 Fund 层 `chapter_writer` / `chapter_auditor` 单章 primitives 已实现：它们只消费 Gate 1 `ChapterFactProjection` / `ChapterFactInput`、显式注入的 LLM Protocol client 和 writer draft；生产代码不读取文档仓库、PDF、cache、source helper、下载器或 parser，不导入真实 provider SDK，不读取 env/config，不调用 Service、Host 或 dayu。
- Route C Gate 3 的 Service 层 `ChapterOrchestrator` / `orchestrate_chapters()` 已实现为 `chapter_orchestrator.v1`：它只消费调用方显式提供的 `StructuredFundDataBundle` 或 `ChapterFactProjection`、显式注入的 writer/auditor LLM Protocol client 和可选 `ChapterFactProvider`，按模板第 1-6 章执行 write-audit-repair policy，输出 accepted chapter conclusions 供后续 Gate 4 使用；它不生成第 0/7 章正文，不构造真实 LLM provider，不读取文档仓库、PDF、cache、source helper、下载器或 parser，不接入 Host、Agent 或 dayu。
- Route C Gate 4 Slice 4A 的 Service 层 `FinalChapterAssembler` / `assemble_final_chapters()` 已实现为 `final_chapter_assembler.v1`：它只消费 Gate 3 accepted chapters/conclusions 和现有 `FinalJudgmentDecision`，确定性生成第 7 章和第 0 章，并以 `0 -> 1-6 -> 7` 顺序总装；它不调用 LLM、不读取结构化 facts/PDF/source helper、不重新应用 preferred_lens/ITEM_RULE，也不改变 final judgment 语义。
- Route C Gate 4 Slice 4B 的 Service 层 `FundAnalysisService.analyze_with_llm()` / `FundLLMAnalysisResult` 已实现：它复用 `_run_analysis_core()`，通过显式注入的 `ChapterOrchestratorLLMClients` 调用 Gate 3，再调用 Slice 4A final assembly；partial/blocked 不回退确定性报告。
- Route C Gate 4 Slice 4C/4D 之后的 CLI `fund-analysis analyze --use-llm` 已实现为显式 opt-in provider-backed 入口：CLI 构造普通 `FundAnalysisRequest` 并调用 Service `FundAnalysisService.analyze_with_llm_hosted()`；Service 读取 typed env config、构造 `FundLLMExecutionContract` / `FundLLMExecutionRequest` / runtime plan 和 `openai_compatible` HTTP chat-completions writer/auditor Protocol clients；Service 经本地 `HostRuntimeRunner` 托管一次 run，并只把 `runtime_plan.host_timeout_seconds` 作为 Host deadline 标量；Host operation 调用 Service `analyze_with_llm_execution()`；默认 `analyze` 不读取 LLM env、不构造 provider，仍走确定性报告路径；`checklist` 不接受该 flag。
- Route C Gate 4 Slice 4D 的 provider contract 是 typed env config + Service-owned `openai_compatible` HTTP chat-completions adapter over existing `httpx`：不新增 vendor SDK，不设置默认 vendor/model/base URL，不通过 `extra_payload` 传参，不把 API key 写入 repr/error；pytest 使用 fake env、`httpx.MockTransport` 和 monkeypatch，不做 live provider smoke。
- `--use-llm` fail-closed 语义已实现：missing/invalid config 和 provider construction failure 在 Service 调用前退出 `1` 且 stdout 为空；provider runtime error、writer/auditor blocked、partial orchestration 或 incomplete final assembly 退出 `1`，不回退 deterministic markdown；quality gate block/not-run 仍按既有语义退出 `2`。
- typed template truth-source replacement 已作为 Fund 层当前事实接受：`docs/fund-analysis-template-draft.md` canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 是 authored template contract truth source；`load_template_contract_manifest()` 从该 JSON 投影 untyped `TemplateContractManifest`；`load_typed_template_contract_manifest()` 从同一 JSON 投影 `typed_chapter_contract.v1` dataclasses；`derive_evidence_availability()` 从 same-source `ChapterFactProjection` 与 typed requirement ids 派生 `evidence_availability.v1`，writer typed required-output path 按 `RequiredOutputItem.when_evidence_missing` 执行缺证 block/degrade/delete，programmatic auditor 覆盖 Ch3 typed evidence-conditional `must_not_cover`，LLM auditor 接收 bounded `audit_focus`，final assembly readiness 通过 Ch0 consuming Ch7 / required body readiness metadata 表达。它们不改变 renderer、quality gate 或 default deterministic path。
- typed template contract Slice 7 已作为 Service 层 transition wiring 接受：`typed_template_path` 是 `FundLLMExecutionRequest` / `FundLLMRuntimePlan` / `ChapterOrchestrationPolicy` 的显式字段；`build_fund_llm_execution_request()` 只在 explicit `--use-llm` path 选择 `typed_template_contract`；`ChapterOrchestrator` 在 typed path 将 typed required-output items、same-source `EvidenceAvailability` 和 typed `audit_focus` 传给 Fund primitives，legacy path 保持 typed inputs inactive。
- incomplete `--use-llm` local artifact retention 已实现：CLI 只在 typed incomplete `FundLLMAnalysisResult` 上触发 Service-owned `write_llm_incomplete_run_artifacts()`；artifact 根目录为 ignored `reports/llm-runs/`，每次 run 写入 `manifest.json`、`summary.json`、per-chapter JSON、writer draft、repair draft、normalized auditor feedback、accepted/failed status、chapter matrix 和 first failed diagnostic。artifact serializer 使用 allowlist-first payload 与 redaction；不保存 API key、Authorization/cookie、完整 provider config、prompt request payload、raw provider response、raw auditor response 或 incomplete final assembled report。artifact 写入失败只输出安全 warning，不改变原 fail-closed exit path。
- `fund-analysis analyze --use-llm` progress/timeout UX 已实现：CLI 支持 `--llm-progress/--no-llm-progress`，默认只在 stderr TTY 时自动输出，forced progress 支持 non-TTY；所有 progress 仅写 stderr 且以 `LLM progress:` 为前缀。Service hosted 用例向 Host 传递 generic safe event sink，CLI reporter 以 duck typing 只格式化 allowlist 字段并捕获自身输出失败；`run_terminal` 在 Service 投影的 `FundLLMHostedRunResult.host_elapsed_ms` 上输出。quality gate block/not-run 保持既有 exit `2`、stdout empty 和错误信息，不伪造 terminal progress；incomplete / Host failed run 仍 fail-closed 且不回退 deterministic。
- 当前 Service ExecutionContract 边界已实现：`FundLLMExecutionContract` 只保存基金身份、报告模式、显式 opt-in、规范化业务输入和质量策略声明；provider runtime budget、章节策略、总装策略、安全诊断策略、Host timeout 和 LLM clients 只在 Service-owned `FundLLMExecutionRequest` / runtime plan 中存在，不进入 Host API。
- 当前 `--use-llm` 有最小 Host run lifecycle、deadline/cancel、terminal state、安全诊断和 writer/auditor/repair/final_assembly phase events；Host 不导入 Service/Fund，不读取基金代码、年份、章节策略或 ExecutionContract 业务字段；Service bridge 调用当前 `fund_agent/agent` no-live body runner，Agent runner 拥有 body-chapter contracts、attempt ledger、safe `ToolTrace`、Fund adapters、repair policy 和 `FinalAssemblyReadiness`。尚无 async Host runner、durable session/resume/memory/reply outbox、full production Agent tool-loop/retry/budget/ToolRegistry/live runtime 或 dayu runtime。
- 当前没有把 quality gate、LLM audit、Evidence Confirm、full production Agent runtime 或 dayu 集成声明为已实现。

**Route C gate 序列**：

| Gate | 已接受的未来 scope | 边界约束 |
|---|---|---|
| Gate 1 | `facet_recognizer` + `ChapterFactProvider` / `FundToolService` contract and implementation | 消费现有 8 章模板、CHAPTER_CONTRACT、preferred_lens、ITEM_RULE 和 facet catalog；基金类型 / facet 识别、fact/evidence 语义属于 Agent/Fund；Service 只负责用例编排和 typed invocation |
| Gate 2 | `chapter_writer` + `chapter_auditor` | 已实现 Fund 层单章 primitives；写作和审计只能消费结构化 facts、derived calculations、显式 data gaps 和 EvidenceAnchor；不得直接读取 PDF、cache、source helper 或下载 helper |
| Gate 3 | `chapter_orchestrator` | 已实现 Service 层 write-audit-repair policy；只通过显式 contract 调用 Agent/Fund 能力；不得把业务参数藏入 `extra_payload` |
| Gate 4 | `final_chapter_assembler`、第 0 章 assembly、Service `analyze_with_llm`、CLI `--use-llm` 和 provider construction 已作为 slices 4A/4B/4C/4D accepted locally | `--use-llm` 是 opt-in provider-backed 路径；missing/invalid config、provider construction/runtime 和 incomplete LLM result fail-closed 且无 deterministic fallback；默认 `analyze/checklist` 保持确定性，除非后续 gate 明确改变 |
| Gate 5A | internalized Host runtime governance adapter（已实现 MVP 最小闭环） | 当前 `--use-llm` 路径为 `CLI -> Service prepares FundLLMExecutionRequest / ExecutionContract -> Host runner -> Service -> Agent body runner -> fund_agent/fund -> provider HTTP call`；本项目 Host 已承接进程内 run lifecycle、global deadline、cancel、terminal run state、安全诊断和 phase events；durable session/resume/memory/reply outbox 与 async Host runner 仍是后续 Host scope |
| Gate 5B | internalized Agent engine / typed audit contract migration（Slice E first no-live body mechanics 已实现；完整 runtime 仍为未来 scope） | 当前 `fund_agent/agent` 拥有 no-live body-chapter contracts、safe `ToolTrace`、Fund adapters、repair policy、body runner 和 `FinalAssemblyReadiness`；full production Agent task graph/tool-loop/retry/budget/ToolRegistry/context budget/live runtime expansion 仍必须内化 Dayu Engine 能力并进入后续 gate；first MVP 保持 provider construction Service-owned；不得夹带 Ch3-only calibration、provider/default/runtime/budget change 或 live acceptance |

Gate 1 中 `ChapterFactProvider` 已是 Fund 层代码事实，但只代表 typed projection façade，不是完整 `FundToolService`。Gate 2 中 `chapter_writer` / `chapter_auditor` 已是 Fund 层代码事实，但只代表单章 writer/auditor primitives：writer 使用精确 `<!-- anchor:<anchor_id> -->` / `<!-- missing:<reason> -->` marker、fail-closed LLM client injection 和 `prompt_only` 合约；auditor 执行程序审计、解析 `SEVERITY|LOCATION|MESSAGE` LLM audit 行协议，并显式把 E2 源文核验 deferred 到 Evidence Confirm gate。Gate 3 中 `chapter_orchestrator` 已是 Service 层代码事实，但只代表第 1-6 章 write-audit-repair façade：`patch` 暂映射为预算内整章 regenerate，`partial` 不是完整报告。Gate 4 Slices 4A/4B/4C/4D 已是代码事实，但只代表 final assembly、Service use case、CLI opt-in、Service-owned provider construction 和 Service-owned ExecutionContract / typed request boundary。incomplete LLM run artifact retention 已是代码事实，但只代表 local ignored diagnostic retention for fail-closed incomplete runs；LLM run progress/timeout UX 已是代码事实，但只代表 safe stderr progress 和 Host generic event sink，不代表 chapter acceptance calibration、provider runtime budget change 或 score-loop entry。Slice E first no-live Agent body-chapter mechanics 已是代码事实：`fund_agent/agent` 承接 body chapters 1-6 的 contracts、attempt ledger、safe `ToolTrace`、Fund adapters、repair policy、body runner 和 `FinalAssemblyReadiness`，并由 Service bridge 调用。chapter 0/7 LLM polish/audit、Evidence Confirm、live smoke、多模型 writer/auditor split、async Host runner、durable Host session/resume/memory/outbox、full production Agent tool-loop/retry/budget/ToolRegistry/live runtime 和 dayu runtime 仍未实现。当前 provider runtime budget / prompt-cost 只能作为 Service runtime plan 和 provider timeout 诊断机制，不是 Host 业务输入；Host 的 run lifecycle、global deadline、cancel、terminal run state 和安全诊断已经由本项目内化最小 runner 提供。Full production internalized Agent runtime expansion 后置到 Agent/tool-loop gate。`facet_recognizer` 与 `FundToolService` 仍是 Route C 的未来候选命名，不是当前代码类型，也不替代当前已实现的 `FundDataExtractor`、`StructuredFundDataBundle` 或既有 Service/Fund contract。

Route C 不删除当前 deterministic rendering，也不降低 release-maintenance/golden residual 的严肃性；它只把 golden / strict correctness / QDII / FOF / `110020` / fixture promotion 从 MVP report generation 主线的启动阻塞改为残余产品质量工作。任何 fixture promotion、golden answer、score、snapshot、quality gate 语义或 final judgment 变更仍必须进入独立 gate。Agent engine / typed audit contract 的 Slice E first no-live body mechanics 已落地为当前事实；完整 production Agent runtime expansion 仍必须进入单独 implementation planning / review / slice gate；不得把未来 runtime 写成当前事实。

#### 5.4.2 报告质量评分维度

未来报告质量 gate 应先作为观测工具引入，不直接替代当前 FQ0-FQ6 quality gate。建议评分维度如下：

| 维度 | 目标 | 失败时优先修复方向 |
|------|------|--------------------|
| 事实覆盖度 | 章节所需 facts 是否足够回答 CHAPTER_CONTRACT / ITEM_RULE | 数据源、解析、字段抽取、数据缺口声明 |
| 抽取正确性 | facts 与年报/招募书/外部结构化来源是否一致 | extractor、表格解析、单位/日期归一化 |
| 证据可追溯性 | 关键数值和判断是否绑定 `EvidenceAnchor` 或 derived 来源 | Evidence Store、锚点生成、审计规则 |
| 章节契约完整性 | 每章是否回答 must_answer，避开 must_not_cover | 模板契约、章节计划、规则审计 |
| 最终判断一致性 | 第 10 章是否只消费第 1-9 章 accepted 结论和 quality gate 状态 | final judgment contract、assembly audit |
| 投资建议边界 | 是否避免直接买卖建议、收益预测、仓位比例和无证据因果 | wording audit、LLM audit、规则码 |
| 可读性与行动性 | 是否让用户知道下一步最小验证问题，而不是堆砌字段 | 章节写作、摘要、问题生成 |

评分产物必须保留输入版本、基金代码、报告年份、章节编号、字段名、证据锚点、失败类别和本地 run 路径。未人工核验的评分结果不得直接写入 golden answer 或长期 fixture。

#### 5.4.3 Fact / Evidence 输入契约

章节写作输入应被建模为可审计的 evidence bundle，而不是散落的 renderer 字符串：

| 输入类别 | 内容 | 约束 |
|----------|------|------|
| `facts` | 基金类型、规模、费率、持仓、业绩、基准、经理、风险等结构化字段 | 必须来自现有 extractor 或后续通过 `FundDocumentRepository` 派生的结构化来源 |
| `derived_calculations` | R=A+B-C、成本估算、温度计状态、压力测试等计算结果 | 必须列出参与计算字段和 EvidenceAnchor |
| `evidence_anchors` | 年报章节、表格、行号、页码、来源种类 | 必须可回溯；缺失时只能输出数据缺口 |
| `data_gaps` | 未披露、不可用、schema drift、identity mismatch、integrity error 等 | 必须按失败类别显式记录，不得被模板静默掩盖 |
| `quality_context` | FQ0-FQ6 结果、程序审计结果、报告质量评分结果 | 只能影响结论置信度和阻断/警示语义，不得替代事实 |

任何 future implementation 若需要把这些输入交给 Host/Agent 调度，必须先通过独立 gate 设计本项目内化 Host/Agent 契约、事件流、ToolTrace、重试、超时、取消和 replay 语义。

#### 5.4.4 Morningstar × 有知有行 × 基金类型 × 章节合同覆盖矩阵

基金分析模板不是普通报告格式，而是面向个人投资者的决策安全合同。设计目标是把专业尽调、行为保护、基金类型差异和 LLM 章节约束收敛到同一个可审计矩阵：

- Morningstar 提供专业尽调覆盖：People、Process、Parent、Price、Performance。当前设计只吸收这些研究维度，不输出 Morningstar medal / star rating，也不冒充晨星评级。
- 有知有行提供个人投资者行为保护：R=A+B-C、基金类型优先、知识 / 情绪 / 意愿、四笔钱适配、温度计 / 估值阶段、下一步最小验证问题。
- Dayu 提供执行机制：CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、章节审计、repair / regenerate；但不直接依赖外部 `dayu-agent` runtime。
- 本项目四层边界保持不变：方法论矩阵属于 Agent 层 `fund_agent/fund` 的基金领域知识；Service 只能选择 scene、质量策略和输入契约；UI 只展示；Host/Agent runtime 仍需独立 gate。

当前 8 章模板的覆盖关系如下：

| 当前章节 | 核心决策问题 | Morningstar 覆盖 | 有知有行覆盖 | CHAPTER_CONTRACT 重点 | 缺失事实降级 |
|----------|--------------|------------------|--------------|-----------------------|--------------|
| 第 0 章 投资要点概览 | 用户是否应继续研究 / 持有 / 关注 / 替换 | 综合输出，不单独评级 | 行为动作、最大风险、下一步最小验证问题 | 只总结已接受章节结论，不引入新事实 | 写明 `数据不足`，动作降级为谨慎观察 |
| 第 1 章 产品本质 | 这到底是什么基金，跟什么比 | Process | 基金类型优先、看这类基金先看什么 | 基金类型、投资目标、策略、基准、特别情况 | 基金类型或基准不明时阻断后续类型 lens |
| 第 2 章 R=A+B-C | 钱从哪里来，费用是否吞噬收益 | Performance、Price | R=A+B-C、温度/估值阶段的成本意识 | R/B/A/C、结构性 vs 阶段性超额、成本拆解 | 缺 R/B/C 输入时输出缺口，不计算伪 alpha |
| 第 3 章 基金经理画像 | 主动能力是否可信、知行是否一致 | People、Process | 知识、情绪、意愿 | §4 说法与 §8 持仓/换手/风格交叉验证 | 无访谈时不得脑补投资哲学；无持有披露时写未披露 |
| 第 4 章 投资者获得感 | 持有人实际体验是否匹配净值表现 | Performance、Price | 投资者回报、资金进出结构、四笔钱适配 | 回撤、波动、持有体验、申赎/规模变化 | 缺持有人结构或申赎数据时只做年报内体验判断 |
| 第 5 章 当前阶段 | 当前处在顺风、逆风、风格切换还是估值约束 | Process、Performance | 温度计、阶段判断、能否拿住 | 估值状态、组合变化、风格阶段、关键变量 | 温度计 unavailable 时显式灰灯，不替代估值判断 |
| 第 6 章 核心风险与否决项 | 什么情况应停止或否决 | Parent、Process、Price | 情绪压力测试、否决项、行为阈值 | 风险红线、压力测试、清盘/风格漂移/费用风险 | 证据不足时列为待验证风险，不升级为否决 |
| 第 7 章 最终判断 | 综合是否值得持有 / 需要关注 / 建议替换 | 五维综合，但不输出晨星评级 | 行为动作、最小验证问题、升级/降级阈值 | 只能消费前文 accepted 结论和 quality context | 任一核心章节未接受时不得给强结论 |

基金类型决定各维度优先级，不能让一套通用模板平均用力：

| 基金类型 | 核心 lens | Morningstar 权重倾向 | 有知有行行为重点 | 章节优先级 |
|----------|-----------|----------------------|------------------|------------|
| `active_fund` | 基金经理认知、流程、言行一致、利益绑定 | People / Process / Parent 高，Price / Performance 用于验证 | 知识、情绪、意愿；能否长期信任并拿住 | 第 3 章 core，第 2/4/6 章 high |
| `index_fund` | 指数规则、跟踪精度、费率、规模流动性 | Process / Price 高，People 低 | 低成本 Beta、温度计纪律、避免追涨 | 第 1/2/5 章 core，第 3 章 low |
| `enhanced_index` | 增强来源、超额稳定性、跟踪约束 | Process / Performance / Price 高 | 不把阶段性增强误认为结构性能力 | 第 2/3/5 章 core |
| `bond_fund` | 久期、信用、杠杆、流动性、回撤 | Process / Parent / Price 高 | 稳健钱适配、极端回撤承受 | 第 4/6 章 core，第 2/5 章 high |
| `qdii_fund` | 市场暴露、汇率、底层资产、费率 | Process / Price / Parent 高 | 汇率和海外市场波动是否适合资金期限 | 第 1/2/5/6 章 high |
| `fof_fund` | 底层基金筛选、资产配置、双重收费 | Process / Parent / Price 高 | 四笔钱匹配、配置纪律、是否值得付双重费用 | 第 1/2/4/6 章 high |

证据来源按强度分层，章节写作和审计必须保留来源强度：

| 证据层级 | 允许用途 | 禁止用途 |
|----------|----------|----------|
| 年报、招募说明书、基金合同、定期报告 | 事实、数值、费率、持仓、基准、经理任职、风险披露 | 不得推断未披露动机 |
| 官方指数公司、交易所、监管披露 | 指数规则、成分、估值、披露制度 | 不得替代基金自身披露 |
| 基金经理访谈、持有人信、公开演讲 | 投资哲学、知识 / 情绪 / 意愿辅助证据 | 不得当作年报事实；不得脑补人格评价 |
| 第三方评级、同类数据、估值工具 | 对比、分位、温度计、外部参照 | 不得输出为本项目自有评级或投资建议 |

当前 8 章到未来 0-10 章的映射仍是未来 gate，不在当前 renderer 中实现。设计边界如下：

| 当前 8 章 | 未来 0-10 候选映射 | 状态 |
|-----------|--------------------|------|
| 第 0 章 | 未来第 0 章，最后生成 | 设计接受，代码未实现 |
| 第 1 章 | 未来第 1-2 章：产品本质 / 策略与基准 | 候选 |
| 第 2 章 | 未来收益归因、成本、质量评分章节 | 候选 |
| 第 3 章 | 未来 People / Process 章节 | 候选 |
| 第 4 章 | 未来投资者获得感 / 行为适配章节 | 候选 |
| 第 5 章 | 未来当前阶段 / 估值温度章节 | 候选 |
| 第 6 章 | 未来风险 / 否决项 / 压力测试章节 | 候选 |
| 第 7 章 | 未来第 10 章，最终判断，倒数第二步生成 | 设计接受，代码未实现 |

后续模板或评分设计必须先引用本矩阵，说明新增字段、章节或审计规则服务哪个方法论维度、哪个基金类型 lens、哪个 CHAPTER_CONTRACT 条款，以及缺失事实时的降级语义。

### 5.5 证据锚点格式

**代码实现**：`fund_agent/fund/extractors/models.py` —— `EvidenceAnchor` dataclass

| 数据类型 | 锚点格式 | source_kind |
|---------|---------|-------------|
| 年报数据 | `年报{年份}§{章节}表{编号}行{行号}` | `annual_report` |
| 外部 API | `外部数据(external_api)` | `external_api` |
| 计算结果 | `计算(derived)` | `derived` |

`EvidenceAnchor` 字段：`source_kind`、`document_year`、`section_id`、`page_number`、`table_id`、`row_locator`、`note`。

---

## 6. 数据源与文档仓库

### 6.1 文档仓库层

**代码实现**：`fund_agent/fund/documents/`

对基金文档的存取统一通过 `FundDocumentRepository`，禁止直接操作文件系统。

| 模块 | 文件 | 职责 |
|------|------|------|
| 仓库入口 | `repository.py` | `FundDocumentRepository` —— 对外唯一文档读取入口 |
| 数据模型 | `models.py` | `ParsedAnnualReport`、`ParsedTable`、`ReportSection`、`DocumentKey` 等 |
| 缓存层 | `cache.py` | `AnnualReportDocumentCache` —— PDF + parsed report 两级缓存，schema 版本控制 |
| 数据源 | `sources.py` | 当前 production default 是 EID single-source policy：`selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`；Eastmoney 仅保留为 deferred future source candidate |
| PDF 适配器 | `adapters/annual_report_pdf.py` | `AnnualReportPdfAdapter` —— PDF 下载 + 解析适配 |

**来源失败分类与 EID single-source 当前策略**（P8-S3 + EID operational hardening）：

当前代码事实：production default annual-report source path 是 EID single-source。`AnnualReportSourceOrchestrator(None)` 只构造 `EidAnnualReportSource`，并拒绝空来源或多来源构造。`EastmoneyAnnualReportSource` 仍保留在源码中，但只作为 deferred future source candidate，不是当前 production fallback。

生产年报 acquisition 通过 EID source path 单源解析 operational annual reports，source policy 固定为 `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`。Eastmoney、基金公司官网/CDN、CNINFO 或其他 first-party disclosure route 只能作为 deferred source candidate / historical evidence route；不得写成当前 production fallback。

在 `single_source_only` 下，EID source outcome 是 terminal source outcome；`not_found` 与 `unavailable` 可以作为 EID source failure 上报，但不授权 fallback：

| 失败类别 | single_source_only 处理 | 说明 |
|---------|-------------------------|------|
| `not_found` | terminal EID source failure；不授权 fallback | 来源正常响应但没有目标基金/年份年报 |
| `unavailable` | terminal EID source failure；不授权 fallback | 网络、超时、服务端或本地依赖临时不可用 |
| `schema_drift` | fail-closed | 官方来源响应结构、字段或附件形态偏离契约 |
| `identity_mismatch` | fail-closed | 返回候选与基金代码、基金 ID、年份或报告类型矛盾 |
| `integrity_error` | fail-closed | PDF Content-Type、文件头、写入内容完整性或 parser viability 失败 |

**当前已接受 live evidence**：small-golden 五行 `004393`、`004194`、`006597`、`110020`、`017641` / `2024` 均已通过受控 live EID evidence gate。该证据只证明 `FundDocumentRepository -> AnnualReportPdfAdapter -> EID single-source` 可对这些行完成 live acquisition、PDF integrity check 和 parser viability check；不证明 live failure branches、extractor correctness、fixture projection、golden/readiness、生产报告生成或 provider/LLM 行为。

**代码实现**：`fund_agent/fund/documents/sources.py`
- `AnnualReportSourceFailure`：记录失败类别、原始异常、上下文
- `AnnualReportSourceFallbackBlockedError`：当非 eligible 失败触发 fallback 时抛出，强制开发者显式处理

**缓存策略**：
- PDF 文件缓存：按 `cache/annual-reports/{fund_code}/{year}.pdf` 路径缓存；当前 repository 只复用带当前 EID single-source metadata 的 PDF cache，legacy、Eastmoney/fallback 或 metadata-less PDF cache 会被忽略而不是删除。
- Parsed report 缓存：JSON 格式，带 `PARSED_REPORT_SCHEMA_VERSION` 版本号；parsed cache 必须绑定 schema version 与 source identity，source mismatch / schema drift 必须 invalidate 或 block reuse。
- 来源元数据：当前 `AnnualReportSourceMetadata` 是年报来源 provenance 容器，支持 `selected_source=eid`、`source_mode=single_source_only`、`fallback_enabled=false`、`fallback_used=false`、EID URL/identifier、`primary_failure_category` 和 `discovery_contract_version` 等当前字段；`identity_mismatch` / `integrity_error` 是来源失败分类与校验结果，不是 `AnnualReportSourceMetadata` 的 status 字段。不得通过隐藏 fallback metadata 伪装 EID source。

**当前已实现：公共来源 provenance 输出契约**：`fund_agent/fund/source_provenance.py` 将 `AnnualReportSourceMetadata` 投影为 additive public provenance 字段；`StructuredFundDataBundle.source_provenance` 使用安全 `not_applicable` 默认值，生产 `FundDataExtractor.extract()` 显式从 `ParsedAnnualReport.metadata.source` 投影。公共 extraction snapshot JSONL 每条记录包含 `source_provenance_schema_version`、`source_strategy`、`selected_source`、`source_mode`、`fallback_enabled`、`resolved_source_name`、`fallback_used`、`primary_failure_category`、`fallback_eligibility`、`source_provenance_status` 和 `source_provenance_reason`，`summary.md` 额外输出独立 `Source Provenance` 表。该实现是当前代码事实，只暴露已审查的公共 provenance，不授权 baseline/golden promotion，不改变 renderer、FQ0-FQ6、默认 analyze/checklist 行为、Host/Agent/dayu。当前 EID single-source implementation 下 `schema_drift`、`identity_mismatch`、`integrity_error` 必须 fail-closed，`not_found` / `unavailable` 只作为 terminal EID source failures，不再产生 production fallback eligibility。2026-06-09 repository review 记录的 Eastmoney integrity-classification risk 是 future source-candidate/fallback gate 的 deferred risk，不是当前实现目标。

### 6.2 结构化抽取层

**代码实现**：`fund_agent/fund/extractors/`

| 模块 | 文件 | 抽取内容 | 年报章节 |
|------|------|---------|---------|
| 基础画像 | `profile.py` | 基金名称、类型、费率、投资目标/范围/策略、风格定位、业绩基准、指数画像 `index_profile` | §1/§2 |
| 表现数据 | `performance.py` | 净值增长率、基准收益率、投资者收益率、直接披露跟踪误差 `tracking_error` | §3/§2 |
| 管理人 | `manager_ownership.py` | 管理人策略原文、换手率、基金经理持有、持有人结构 | §4/§8/§9 |
| 持仓变动 | `holdings_share_change.py` | 前十大重仓、行业分布、份额变动 | §8/§10 |
| 数据模型 | `models.py` | `EvidenceAnchor`、`ExtractedField[T]`、各抽取结果 dataclass | — |

**已接受 row-shape extractor contracts**：

2026-06-10 row-shape contract decision gate 接受以下契约；已实现项只代表当前 extractor 输出面，不代表已接入 `StructuredFundDataBundle`、snapshot、renderer、quality gate、report evidence、chapter facts、checklist 或 Service：

| Residual | Contract | Current status / boundary |
|---|---|---|
| `manager` | `portfolio_manager_tenure_list.v1` | 当前 extractor 输出面：`extract_manager_ownership().portfolio_managers` 从年报 `§4.1.2 基金经理简介` 输出 year-specific portfolio-manager list；每个 entry 至少包含 `name`、normalized `role`、`start_date`、`source_anchor` |
| retained `risk` | `risk_characteristic_text.v1` | 当前 extractor 输出面：`extract_profile().risk_characteristic_text` 只从 `§2` 显式 `风险收益特征` / `基金风险收益特征` 标签输出 exact risk text 与 source anchors；该契约不是 `product_profile.style_positioning` |
| `006597` bond top holding | `bond_top_holding_row.v1` | 当前 extractor 输出面：`extract_holdings_share_change().holdings_snapshot.value.bond_top_holdings` 输出独立 bond holding sub-shape，不复用 stock `top_holdings` 语义；当前 passing same-source test 断言 `code`、`name`、`fair_value_cny`、`net_asset_ratio` 和 source anchor；`rank` 仅在 oracle 提供时可断言 |
| `110020` target ETF holding | `target_fund_holding_row.v1` | 当前 extractor 输出面：`extract_holdings_share_change().holdings_snapshot.value.target_fund_holdings` 输出独立 target-fund holding sub-shape，不复用 stock `top_holdings` 或 bond `bond_top_holdings` 语义；当前 passing same-source test 断言 `name`、`fair_value_cny`、`net_asset_ratio` 和 source anchor；不从 tracking error、benchmark、fund name 或外部 ETF metadata 推断 code |

后续 downstream integration 仍必须单独 gate，不得在一个 implementation slice 中同时向 `StructuredFundDataBundle` 接入多个 additive contracts。该设计不授权 source acquisition、PDF/network/FDR live use、fallback、fixture projection、golden/readiness promotion、provider/runtime/config change 或 PR/release 外部动作。

**P1 数据 façade**：`fund_agent/fund/data_extractor.py`
- `FundDataExtractor`：编排文档仓库 + 净值适配器 + 章节 extractor
- `StructuredFundDataBundle`：聚合 profile、performance、manager、holdings、share change 和 nav 数据；当前包含 `index_profile` 与 `tracking_error` 结构化字段
- `NavDataResult`：净值结果；成功时保留 `source="nav_cache" / "akshare"` 与 `cached`，NAV provider / cache / akshare 失败时由 `FundDataExtractor` 在单次 `load_nav_data()` 调用边界降级为 `unavailable=True`、`records=[]`、`source="nav_unavailable"`，并保留异常类型和消息。年报仓库/PDF/source fallback 的 fail-closed 语义不在该降级 catch 边界内，仍向上抛出。
- `FundNavRepository.load_nav_series()`：当前 Fund data 层 typed NAV repository contract。无参 `FundNavRepository()` 默认通过 CSRC EID 公开 search/detail/classification 页面读取已验证的 006597 家族 A/C/E/F 份额分类累计净值，并输出 `FundNavSeries`，显式包含 `share_class`、`nav_type`、`adjusted_basis`、`dividend_adjustment_status`、`identity_status`、source/cache/query provenance、完整性约束和 `strong_drawdown_evidence_eligible`。旧 `NavDataResult` 仅保留为 `analyze`、`checklist`、snapshot 和既有 P1 façade 兼容结果；路径型 drawdown metric 只能消费 `FundNavRepository.load_nav_series()` 的 typed 边界，不得直接读取 CSRC EID、Akshare、SQLite cache、snapshot JSONL 或旧 raw payload。
- 当前 CSRC EID accumulated path 对已验证 006597=A/2030-1010、006598=C/2030-1020、014217=E/2030-1040、022176=F/2030-1050 分份额输出 `nav_type="accumulated_nav"`、`adjusted_basis="accumulated_nav"`、`dividend_adjustment_status="not_applicable"`、`identity_status="verified"`。`strong_drawdown_evidence_eligible=True` 只表示 source identity 与 accumulated basis 具备路径型指标的 source-level eligibility；`fund_agent/fund/data/nav_metrics.py` 当前只实现最大回撤派生指标，按请求基金代码对应 A 类份额、年报年度 `YYYY-01-01` 至 `YYYY-12-31` inclusive 的 accumulated NAV path 计算，不混合 A/C/E/F，不实现 volatility。
- `FundDataExtractor.extract()` 当前仅对 exact `bond_fund` 通过 `FundNavRepository.load_nav_series(fund_code, share_class="A", start_date=report_year-01-01, end_date=report_year-12-31, minimum_records=30, force_refresh=...)` 加载 typed series，并把最大回撤作为 `bond_risk_evidence.v1.drawdown_stress` 的 `quantitative_derived / derived_metric` 证据。派生锚点使用 `source_kind="derived"`、`section_id="derived:nav"` 和 `metric:max_drawdown:<share_class>:<period_start>:<period_end>` row locator，note 中记录 CSRC EID source、source_id、query params、record count、peak/trough 和 ratio。NAV source 或指标失败时，年报“控制回撤”文本仍只能保持 weak，不提升为 accepted。
- legacy Akshare / 天天基金 `单位净值走势` 仍可通过 constructor-injected raw adapter 进入兼容分支，并只归一化为 `nav_type="unit_nav"`、`adjusted_basis="raw_unit_nav"`、`dividend_adjustment_status="not_adjusted"`、`identity_status="requested_code_only"`，强制 `strong_drawdown_evidence_eligible=False`。该路径没有证明分红调整、累计净值或 total-return basis，也不能作为模板第 6 章强 drawdown evidence。

**抽取模式**（`ExtractionMode`）：
- `direct`：直接从年报文本/表格提取
- `derived`：从多个字段计算得出
- `estimated`：数据缺失时按同类中位数估算
- `missing`：无法获取

### 6.3 外部数据

| 数据 | 来源 | 获取方式 | 代码位置 |
|------|------|---------|---------|
| 基金年报 PDF | Current production default: EID single-source operational annual-report source only (`selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`); small-golden five rows `004393` / `004194` / `006597` / `110020` / `017641` for 2024 have accepted live EID/FDR acquisition proof; Eastmoney、基金公司官网/CDN、CNINFO 仅为 deferred candidate / historical evidence route | httpx 下载；必须经 `FundDocumentRepository` 边界；live failure branches 仍需单独授权 | `documents/sources.py` |
| 基金净值序列 | CSRC EID 分类累计净值；legacy Akshare raw-unit 兼容分支 | httpx + HTML parser；legacy Akshare API | `data/csrc_eid_nav_source.py`, `data/nav_source_contract.py`, `data/nav_data.py`, `data/nav_repository.py` |
| 温度计公开页适配器（过渡/对比） | 有知有行公开页面 | httpx + HTML 解析 | `data/thermometer.py` |
| 自建温度计（当前生产方向） | akshare 指数估值接口；全 A 使用 `stock_a_ttm_lyr()` 的 `middlePETTM` 与 `stock_a_all_pb()` 的 `middlePB` | akshare API；经 Protocol 封装 | `data/thermometer_source.py`, `analysis/thermometer_calculator.py`, `data/thermometer_cache.py`, `data/thermometer_types.py` |
| 精选基金池 | 手动维护 CSV | 文件读取 | `extraction_snapshot.py` |

当前温度计能力通过 `ThermometerService` 与 `fund-analysis thermometer` CLI 暴露。P19 已把沪深 300（`000300`）、中证 500（`000905`）和全 A 市场（`wind_all_a`）的自建温度计作为当前生产方向；CLI 未传 `--index` 时默认查询 `wind_all_a`。有知有行公开页适配器只能作为过渡查询、对比验证或历史兼容输入，不得作为生产真源。

> **温度计独立开发（P19）**：温度计基于有知有行公开方法论独立计算，不依赖有知有行页面抓取作为生产数据真源。核心算法为 A 股市场或指数成分的等权 PE/PB 中位数历史分位数综合。CLI 和报告输出必须标注"基于有知有行公开方法论独立计算，非有知有行官方数据"。详见 §11。

P19-S3 后，`fund-analysis analyze` 允许在严格范围内自动映射买入前检查清单的 `valuation_state`：仅当指数基金或指数增强基金的 exact benchmark identity 命中当前支持指数（`000300` / `000905`）时调用温度计；主动、债券、QDII、FOF、派生指数、多个权益指数和无法精确归类基准保持 `unavailable`，不得调用温度计。用户显式传入 `--valuation-state` 时必须优先于自动结果。

### 6.4 年报章节映射

| 年报章节 | 内容 | 用于 |
|---------|------|------|
| §1/§2 | 基金简介、费率、投资目标/范围/策略 | 第 1 章、第 2 章 |
| §3 | 净值、基准、投资者收益率 | 第 2 章、第 4 章 |
| §4 | 管理人报告（基金经理观点） | 第 3 章（"说"） |
| §8 | 投资组合报告（持仓、换手率） | 第 3 章（"做"） |
| §9 | 持有人结构、自购 | 第 3 章、第 6 章 |
| §10 | 份额变动 | 第 4 章 |

### 6.5 基金类型识别规则

**代码实现**：`fund_agent/fund/fund_type.py`

`FundType = Literal["index_fund", "active_fund", "bond_fund", "enhanced_index", "qdii_fund", "fof_fund"]`

识别基于年报 §1/§2 的稳定披露信息，按优先级执行：

1. **指数关键词**：名称含"指数"/"ETF"/"联接" → `index_fund`
2. **增强标识**：名称含"增强" → `enhanced_index`
3. **QDII 标识**：名称含"QDII"/"境外" → `qdii_fund`
4. **FOF 标识**：名称含"FOF"/"基金中基金" → `fof_fund`
5. **债券类别**：基金类别含"债券"/"中债" → `bond_fund`
6. **主动权益**：基金类别含"混合型"/"股票型" → `active_fund`

**公开接口**：`classify_fund_type(report: ParsedAnnualReport) -> FundTypeClassification`

### 6.6 错误处理与降级策略

| 失败场景 | 影响章节 | 处理策略 | 报告输出 |
|---------|---------|---------|---------|
| PDF 下载失败 | 全部 | single_source_only 下报告 terminal EID source failure；`not_found` / `unavailable` 不授权 fallback，`schema_drift` / `identity_mismatch` / `integrity_error` fail-closed | Service 层捕获并报告 |
| 章节解析失败 | 特定章节 | extractor 返回 `extraction_mode="missing"` | 模板渲染写"未披露" |
| 关键数据缺失 | 第 2 章 | `extraction_mode="estimated"` + note 说明 | "换手率未披露，按同类中位数估算" |
| 2026 新规数据未披露 | 第 4 章 | 份额变动 × 净值变化估算 | "投资者收益率未披露，用份额变动估算" |
| 温度计获取失败 | 检查清单 | 使用过期缓存或返回 unavailable | "⚠️ 温度数据暂时不可用" |
| NAV provider/cache/akshare 失败 | 第 5 章 / P2 `nav_data` | 返回 `NavDataResult(unavailable=True, records=[])` | 年报主链路继续；snapshot 中 `nav_data` 记为 missing / unavailable |

---

## 7. 质量门控体系（P4）

### 7.1 三阶段质量管线

```
P4-S1: extraction_snapshot  —— 精选基金池字段级抽取快照
  → P4-S2: extraction_score  —— coverage / traceability / correctness 评分
    → P4-S3: quality_gate  —— FQ0-FQ6 质量规则门控
```

### 7.2 抽取快照（extraction_snapshot）

**代码实现**：`fund_agent/fund/extraction_snapshot.py`

- 读取精选基金池 CSV（`docs/code_20260519.csv`）
- 对每只基金调用 `FundDataExtractor.extract()`
- 将 `StructuredFundDataBundle` 拆成字段级 `SnapshotRecord`
- 输出 JSONL、错误明细和人工可读 summary

**字段顺序**（当前字段组）：`basic_identity` → `product_profile` → `benchmark` → `index_profile` → `fee_schedule` → `classified_fund_type` → `nav_benchmark_performance` → `investor_return` → `tracking_error` → `manager_strategy_text` → `turnover_rate` → `manager_alignment` → `holder_structure` → `holdings_snapshot` → `share_change` → `nav_data`

### 7.3 抽取评分（extraction_score）

**代码实现**：`fund_agent/fund/extraction_score.py`

对每个字段计算：
- **coverage**：`value_present=True` 的比例（阈值：pass ≥ 90%, watch ≥ 70%）
- **traceability**：`anchor_present=True` 的比例（阈值同上）
- **correctness**：与 golden answer 比对（match/mismatch/unavailable）

**字段优先级**：
| 优先级 | 字段 |
|--------|------|
| P0 | basic_identity, classified_fund_type, benchmark, nav_benchmark_performance, fee_schedule, manager_strategy_text |
| P1 | product_profile, index_profile, tracking_error, turnover_rate, holder_structure, manager_alignment, holdings_snapshot, share_change |
| P2 | investor_return, nav_data |

`index_profile` 和 `tracking_error` 是指数基金 / 指数增强基金的条件 P1 字段。非指数基金不把这两个字段纳入 coverage / traceability / fund quality 分母；未知或冲突基金类型保持保守处理。

### 7.4 质量门控规则（quality_gate）

**代码实现**：`fund_agent/fund/quality_gate.py`

| 规则码 | 含义 | 严重级别 | 说明 |
|--------|------|---------|------|
| FQ0 | 前置条件缺失 | info | score.json 缺少必要数据段，相关规则跳过 |
| FQ1 | 正确性/类别冲突 | block | 抽取值与 golden answer 冲突，或 App 类别与系统类型冲突 |
| FQ2 | 字段覆盖率/可追溯性未达标 | block/warn | P0 字段未达标阻断，P1 字段未达标警告 |
| FQ2F | 基金级评分失败 | block/warn | 单只基金整体 P0/P1 字段存在失败 |
| FQ3 | P0 证据锚点不足 | block | P0 字段 traceability < 90%，证据不可溯源 |
| FQ4 | snapshot 字段缺失率过高 | block/warn | 缺失率 ≥ 20% 警告，≥ 35% 阻断 |
| FQ5 | 模板契约（preferred_lens）不匹配 | block/info | mismatch 阻断，resolved/not_applicable 信息级 |
| FQ6 | 抽取流程完全失败 | block | 基金整个抽取流程异常 |

**质量 gate 集成**：`fund_agent/fund/quality_gate_integration.py`
- `run_quality_gate_for_bundle()`：将 `StructuredFundDataBundle` 转换为 snapshot → score → gate 产物
- 当前基金不在精选池时返回 `not_run_reason`，不伪造 App 类别

**Service 集成裁决**：
- `FundAnalysisService` 在抽取完成后、P2 分析前运行单基金 quality gate；它复用已取得的 `StructuredFundDataBundle`，不重新读取 PDF、cache 或文档仓库。
- `quality_gate_policy=block` 是产品默认：gate `block` 抛出 `QualityGateBlockedError`，gate 未运行抛出 `QualityGateNotRunBlockedError`，CLI 返回退出码 2 并输出结构化 gate 信息。
- `quality_gate_policy=warn` 允许继续输出，但 `derive_final_judgment()` 仍会消费 gate 状态；`quality_gate_policy=off` 显式标记为 `not_run`，仅允许开发覆盖模式使用。
- `fund-analysis checklist` 复用同一 gate 和最终判断路径，只省略 8 章模板渲染与程序审计，不省略质量判断。

**Service policy / gate 状态机**：

| policy | gate 执行结果 | Service 行为 | `derive_final_judgment()` 输入 | 用户可见结果 |
|--------|---------------|--------------|--------------------------------|--------------|
| `block` | `pass` / `warn` | 继续分析 | `pass` / `warn` | 正常输出报告或清单，附 gate 摘要 |
| `block` | `block` | 抛出 `QualityGateBlockedError` | 不进入最终判断 | CLI 退出码 2，输出结构化阻断信息 |
| `block` | 未运行 / 不在精选池 / CSV 不可用 | 抛出 `QualityGateNotRunBlockedError` | 不进入最终判断 | CLI 退出码 2，输出 not-run 原因 |
| `warn` | `pass` / `warn` / `block` | 继续分析 | gate 原始状态 | 输出报告或清单；`block` 只作为数据质量信号进入最终判断 |
| `warn` | 未运行 | 继续分析 | `not_run` | 输出报告或清单，但最终判断最多为 `needs_attention` |
| `off` | 不执行 | 继续分析 | `not_run` | 仅 developer override；最终判断最多为 `needs_attention` |

Golden Answer pipeline 由预填底稿、人工复核、strict JSON 构建和 correctness 比对组成。当前 quality gate 只消费可复核基准与结构化产物；基准覆盖不足时，应扩大 golden coverage 或降级为显式 residual risk，不能把少量 golden answer 误当全域正确性证明。`tracking_error` 生产 golden rows 只有在 reviewed direct observed disclosure evidence 被接受后才能添加。

当前 correctness oracle 的身份键为 `fund_code + report_year + field_name + sub_field`。strict golden answer JSON 在基金级和记录级都保留 `report_year`；旧版 JSON 若缺少 `report_year`，仅按当前已复核 2024 corpus 兼容加载为 `2024`。同基金不同年份的 golden 记录可以并存，当前快照缺少同年 golden 时归类为 `year_not_covered` 并在 quality gate 中保留为 `FQ0/info`，不得拿其他年份 golden 做 mismatch 比对；同年同字段明确 mismatch 仍归类为 correctness mismatch 并触发 `FQ1/block`。

### 7.5 ITEM_RULE 合规审计（P12）

**代码实现**：`fund_agent/fund/template/item_rules.py`

| 函数/类型 | 说明 |
|-----------|------|
| `TemplateItemRuleAuditContext` | 审计上下文：章节 ID、ITEM_RULE 定义、渲染后内容、证据锚点 |
| `evaluate_template_item_rule()` | 评估单条 ITEM_RULE 合规性 |
| `rendered_segment_present()` | 后渲染校验：检查渲染后内容是否包含 ITEM_RULE 要求的片段 |

**审计时机**：模板渲染完成后，对每章执行 ITEM_RULE 校验，确保 must_answer 问题被回答、must_not_cover 内容未出现。

### 7.6 Golden Answer 机制

**代码实现**：
- `fund_agent/fund/golden_prefill.py`—— 预填底稿生成
- `fund_agent/fund/golden_answer.py`—— Markdown → JSON 转换与校验

流程：`GoldenPrefillService`（自动预填）→ 人工复核 → `GoldenAnswerService`（转 JSON）→ `extraction_score`（correctness 比对）

strict golden answer 的可比身份键同样使用 `fund_code + report_year + field_name + sub_field`。构建阶段允许同一基金代码跨年份并存，但同一身份键重复会 fail-fast；读取阶段只为旧版缺少年份的当前 2024 corpus 提供兼容默认值，不表示跨年份可复用。

---

## 8. 模板渲染

### 8.1 渲染器

**代码实现**：`fund_agent/fund/template/renderer.py`

`render_template_report(input: TemplateRenderInput) -> TemplateRenderResult`

渲染流程：
1. 校验最终判断（只允许 worth_holding / needs_attention / suggest_replace）
2. 收集证据锚点
3. 按章节 0-7 依次渲染（`_render_chapter_0` ~ `_render_chapter_7`）
4. 渲染证据附录（`## 证据与出处`）
5. 校验直接交易建议与明确配置指令，允许年报披露语境中的非指令性交易动词
6. 切分章节块（`split_rendered_chapter_blocks`）
7. 构建程序审计输入

### 8.2 最终判断推导（P10）

**代码实现**：`fund_agent/fund/analysis/final_judgment.py`

`derive_final_judgment(...)` 从检查清单结果、风险检查结果、压力测试结果、质量门控状态，推导出最终判断：

| 判断值 | 含义 | 触发条件 |
|--------|------|----------|
| `worth_holding` | 值得持有 | 无否决项，检查清单通过，质量门控通过 |
| `needs_attention` | 需要关注 | quality gate `block/not_run`、数据质量不足、检查清单黄/灰、风险 watch 或压力测试接近边界，但未达替换标准 |
| `suggest_replace` | 建议替换 | 存在否决项，或检查清单红灯，或基础 `minus_20` 压力场景越过用户承受能力 |

该推导口径与第 4.8 节一致：quality gate `block/not_run` 表示数据质量不足，只派生 `needs_attention`；它不是基金产品本身应替换的同源证据，不能单独触发 `suggest_replace`。`suggest_replace` 只来自否决项、检查清单红灯、基础 `minus_20` 压力场景越过用户承受能力等产品或用户风险证据。

**开发者覆盖模式**：
- 允许开发者显式传入 `final_judgment_override` 覆盖推导结果
- 覆盖时记录 `FinalJudgmentSource.DEVELOPER_OVERRIDE` 和冲突信息
- 用于 R2 审计：检测开发者覆盖与程序推导的不一致

### 8.3 章节块切分

**代码实现**：`fund_agent/fund/template/chapter_blocks.py`

`split_rendered_chapter_blocks(report_markdown) -> tuple[RenderedChapterBlock, ...]`

按 `# {chapter_id}. {title}` 一级标题切分，校验章节完整性（0-7 必须全部存在、无重复、无乱序）。

---

## 9. 项目结构

以下结构用于说明当前主要模块边界，不作为逐文件 inventory；新增 helper、review artifact 和运行产物以代码与
`docs/implementation-control.md` 为准。

### 9.0 CLI 命令清单

| 命令 | 功能 | 当前状态 |
|------|------|----------|
| `fund-analysis analyze` | 主分析入口 | 已实现；默认运行 quality gate，低质量以结构化错误阻断 |
| `fund-analysis checklist` | 独立检查清单入口 | 已实现；复用 `FundAnalysisService` 的分析核心，输出 7 问清单、估值来源、最终判断和下一步最小验证问题 |
| `fund-analysis thermometer` | 温度计查询 | 当前已实现项目内自建温度计；默认输出全 A `wind_all_a`，支持 `000300` / `000905` 与批量 JSON 输出；公开页适配器只作过渡/对比输入 |
| `fund-analysis extraction-snapshot` | 精选基金池字段级抽取快照 | 已实现 |
| `fund-analysis extraction-score` | 字段级 coverage / traceability / correctness 评分 | 已实现 |
| `fund-analysis golden-prefill` | Golden answer 预填底稿 | 已实现 |
| `fund-analysis golden-build` | Golden answer Markdown 到 strict JSON 构建 | 已实现 |
| `fund-analysis quality-gate` | 对 score JSON 运行质量门控 | 已实现 |

```text
fund-agent/
├── fund_agent/
│   ├── __init__.py
│   ├── ui/                              # UI 层
│   │   ├── __init__.py
│   │   └── cli.py                       # Typer CLI 入口
│   ├── services/                        # Service 层（7 个服务）
│   │   ├── __init__.py                  # 公共导出（Request/Result/Service 类型）
│   │   ├── fund_analysis_service.py     # 主分析用例编排
│   │   ├── llm_provider.py              # Route C provider factory（openai_compatible over httpx）
│   │   ├── extraction_snapshot_service.py
│   │   ├── extraction_score_service.py
│   │   ├── quality_gate_service.py
│   │   ├── golden_prefill_service.py
│   │   ├── golden_answer_service.py
│   │   └── thermometer_service.py
│   ├── host/                            # Host 层目标包；内化 Dayu Host 能力
│   ├── agent/                           # Agent 执行层目标包；内化 Dayu Engine 能力
│   ├── fund/                            # Agent 层基金领域能力包
│   │   ├── __init__.py
│   │   ├── fund_type.py                 # 基金类型识别（FundType + classify_fund_type）
│   │   ├── data_extractor.py            # P1 结构化数据 façade（FundDataExtractor）
│   │   ├── extraction_snapshot.py       # P4-S1 抽取快照
│   │   ├── extraction_score.py          # P4-S2 抽取评分
│   │   ├── golden_answer.py             # golden answer Markdown → JSON
│   │   ├── golden_prefill.py            # golden answer 预填底稿
│   │   ├── quality_gate.py              # P4-S3 质量门控规则
│   │   ├── quality_gate_integration.py  # 单基金 quality gate 集成
│   │   ├── documents/                   # 文档仓库层
│   │   │   ├── __init__.py              # 导出 FundDocumentRepository
│   │   │   ├── repository.py            # 仓库入口（Protocol + 默认实现）
│   │   │   ├── models.py                # ParsedAnnualReport / ParsedTable / DocumentKey
│   │   │   ├── cache.py                 # PDF + parsed report 两级缓存
│   │   │   ├── sources.py               # 当前 production default 为 EID single-source；Eastmoney 为 deferred candidate
│   │   │   └── adapters/
│   │   │       ├── __init__.py
│   │   │       └── annual_report_pdf.py # PDF 下载 + 解析适配器
│   │   ├── extractors/                  # 结构化抽取层
│   │   │   ├── __init__.py              # 导出 ExtractedField / EvidenceAnchor
│   │   │   ├── models.py                # EvidenceAnchor / ExtractedField[T] / 各 Result
│   │   │   ├── profile.py               # §1/§2 基础画像抽取
│   │   │   ├── performance.py           # §3 表现数据抽取
│   │   │   ├── manager_ownership.py     # §4/§8/§9 管理人抽取
│   │   │   └── holdings_share_change.py # §8/§10 持仓变动抽取
│   │   ├── analysis/                    # 分析引擎
│   │   │   ├── __init__.py              # 公共导出
│   │   │   ├── r_abc.py                 # R=A+B-C 收益归因
│   │   │   ├── alpha_judge.py           # 超额收益性质判断
│   │   │   ├── consistency_check.py     # 言行一致性检验
│   │   │   ├── investor_return.py       # 投资者获得感分析
│   │   │   ├── risk_check.py            # 否决项检查 + 压力测试
│   │   │   ├── checklist.py             # 7 问题检查清单
│   │   │   ├── final_judgment.py        # P10 最终判断推导（worth_holding/needs_attention/suggest_replace）
│   │   │   ├── thermometer_calculator.py # P19 温度计纯计算器
│   │   │   └── _ratios.py               # 内部比率计算工具
│   │   ├── audit/                       # 审计机制
│   │   │   ├── __init__.py              # 导出 run_programmatic_audit
│   │   │   ├── audit_programmatic.py    # 程序审计执行器（P1/P2/P3/L1/R1/R2）
│   │   │   └── contract_rules.py        # CHAPTER_CONTRACT C2 审计规则
│   │   ├── template/                    # 模板系统
│   │   │   ├── __init__.py              # 公共导出（lazy load renderer）
│   │   │   ├── contracts.py             # CHAPTER_CONTRACT 机器契约
│   │   │   ├── item_rules.py            # ITEM_RULE 机器契约
│   │   │   ├── lens_application.py      # P8 preferred_lens 应用计划
│   │   │   ├── renderer.py              # 8 章模板渲染器
│   │   │   └── chapter_blocks.py        # 章节块切分工具
│   │   ├── pdf/                         # PDF 基础设施
│   │   │   ├── __init__.py
│   │   │   ├── downloader.py            # PDF 下载
│   │   │   └── parser.py                # PDF 文本/表格解析（含章节目录定位）
│   │   ├── data/                        # 外部数据获取
│   │   │   ├── __init__.py
│   │   │   ├── nav_data.py              # 净值数据（天天基金/akshare）
│   │   │   ├── thermometer.py           # 当前温度计（有知有行公开页面过渡适配器）
│   │   │   ├── thermometer_source.py    # P19 自建温度计数据源
│   │   │   ├── thermometer_cache.py     # P19 自建温度计历史缓存
│   │   │   └── thermometer_types.py     # P19 自建温度计结构化类型
│   └── config/
│       ├── __init__.py
│       ├── llm.py                       # Route C typed LLM env config
│       └── paths.py                     # P10 路径常量（DEFAULT_SELECTED_FUNDS_CSV 等）
├── scripts/
│   └── selected_funds_smoke.py          # 精选基金池冒烟测试
├── tests/                               # 测试
│   ├── fund/
│   │   ├── analysis/                    # 分析引擎测试（6 个文件）
│   │   ├── audit/                       # 审计测试
│   │   ├── documents/                   # 文档仓库测试
│   │   ├── extractors/                  # 抽取器测试（4 个文件）
│   │   ├── template/                    # 模板测试（3 个文件）
│   │   ├── pdf/                         # PDF 测试
│   │   ├── data/                        # 数据获取测试
│   │   ├── integration/                 # 集成测试
│   │   ├── test_extraction_snapshot.py
│   │   ├── test_extraction_score.py
│   │   ├── test_golden_answer.py
│   │   ├── test_golden_prefill.py
│   │   └── test_quality_gate.py
│   ├── services/                        # Service 层测试（5 个文件）
│   ├── ui/                              # UI 测试
│   ├── scripts/                         # 脚本测试
│   └── fixtures/                        # 测试固件
│       └── fund/
│           ├── extractors/              # 抽取器测试固件
│           └── pdf_sections/            # PDF 章节测试固件
├── reports/                             # 运行产物
│   └── golden-answers/                  # golden answer 产物
├── docs/                                # 设计文档
│   ├── design.md                        # 本文档（设计真源）
│   ├── implementation-control.md        # 实施总控
│   ├── implementation-control-p4.md     # P4 质量体系实施控制
│   ├── audit-alignment.md               # 审计机制对照研究
│   ├── fund-analysis-template-draft.md  # 定性模板 v2
│   ├── golden-answer-template.md        # golden answer 模板
│   ├── golden-answer-instructions.md    # golden answer 操作说明
│   └── reviews/                         # phaseflow / code review / controller judgment artifacts
├── pyproject.toml
├── uv.lock
├── AGENTS.md
├── CLAUDE.md
└── README.md
```

Host / Agent 通用执行包是目标边界。当前已创建 `fund_agent/host` 最小进程内 run governance 包，用于 `--use-llm` 的 run lifecycle、deadline/cancel、terminal state、安全诊断和 phase events；当前已创建 `fund_agent/agent` no-live body-chapter execution package，用于模板第 1-6 章的 contracts、attempt ledger、safe `ToolTrace`、Fund adapters、repair policy、body runner 和 `FinalAssemblyReadiness`。当前仍没有 durable Host session/resume/memory/reply outbox、full production Agent tool-loop/retry/budget/ToolRegistry/context budget/live runtime 或 dayu runtime。后续若要落地这些能力，必须进入独立 gate，先完成 plan review、契约、生命周期、失败语义、事件/trace schema、测试和文档边界裁决。

### 9.1 工程基线与 Dayu 吸收范围

本项目吸收 `dayu-agent` `pyproject.toml` 中适合基金 Agent 的工程要求：

| 领域 | 当前要求 |
|------|----------|
| Python | `requires-python >=3.11`，支持 Python 3.11/3.12 生态窗口 |
| 打包 | 使用 PEP 621 项目元数据；构建后端为 setuptools；只打包 `fund_agent*`，排除 `tests*`、`docs*`、`reports*`、`scripts*`、`workspace*`、`cache*` |
| 包内资源 | 当前 `fund_agent` 包内没有非 Python 资源需要分发；未来如新增默认 prompt、配置、模板、fixture、asset 或 render 资源，必须在 `[tool.setuptools.package-data]` 显式声明，不能依赖隐式包含 |
| 依赖声明 | 生产依赖必须显式列入 `dependencies`；用于当前生产代码的 pandas 必须声明为 `pandas>=2.1.4,<4.0.0`；不允许把显式能力藏在额外 payload 或隐式环境中 |
| 可选依赖 | `test` 放测试工具链；`dev` 汇总测试、lint、format、类型检查工具；浏览器/Web/微信/外部 Dayu runtime 不作为默认或可选生产目标；Host/Agent gate 默认走本项目内化实现，不声明外部 Dayu runtime |
| 工具配置 | pytest、ruff、black 的入口在 `pyproject.toml`；测试与 README 可补充使用说明，但不另立冲突真源 |
| 覆盖率策略 | CI 自动阻断 gate 当前为 `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`；单文件 ≥80% 是新增或大幅修改模块的评审目标，低于目标必须在 review 或 residual risk 中解释，不直接等同于 CI fail |
| 脚本入口 | 当前唯一用户入口为 `fund-analysis = fund_agent.ui.cli:app` |
| License | 项目元数据使用 `license = "MIT"`；发布卫生测试要求仓库根目录存在 MIT `LICENSE` 文件。当前工作区如只保留 `LICENSE.md` 或删除 `LICENSE`，必须作为 repo hygiene 阻塞处理，而不是修改测试去迁就 |

| Dayu-Agent 模块 | pyproject.toml | 代码导入 | 说明 |
|---|---|---|---|
| `dayu.host` | ❌ 当前不声明 | ❌ 当前确定性主链路未使用 | Host 能力研究输入；不得作为生产 runtime 直接依赖 |
| `dayu.engine` | ❌ 当前不声明 | ❌ 当前确定性主链路未使用 | Agent 能力研究输入；不得作为生产 runtime 直接依赖 |
| Prompting/Config | — | ❌ 未使用 | 如需接入 prompt、scene、ExecutionContract 或 workspace override，必须先进入 Service/Host/Config 边界设计 |
| 审计机制架构 | — | 🔧 借鉴 | audit→confirm→repair 三阶段架构参考，代码独立实现 |
| `dayu.fins` 分层 | — | 📐 参考 | Processor/Repository/Pipeline 分层思想只能作为 Agent 层基金领域能力参考，不单独成为系统层 |

---

## 10. 设计决策记录

| 决策 | 选择 | 备选方案 | 理由 |
|------|------|---------|------|
| 架构模式 | 四层边界 `UI -> Service -> Host -> Agent` | 六层 UI/Application/Runtime/Service/Engine/Capability 或继续承认三层为目标架构 | 用户已明确采用 Dayu 四层；`AGENTS.md` 已同步为唯一规则真源；当前确定性实现只是未接入 Host/Agent 的过渡路径 |
| Dayu Host/Agent 能力 | Host/Agent 在本项目内化 Dayu 稳定能力 | 直接依赖 `dayu-agent` 生产 runtime，或未经 license/compliance gate 复制/改写上游代码 | 复用 Dayu 手册和已有实现边界，同时避免上游停止维护、依赖面扩张或接口漂移损害本项目 |
| CLI 框架 | Typer | Click / argparse | 类型注解友好，与 FastAPI 生态一致 |
| 输出格式 | 8 章定性模板 | 一页纸报告 | 信息更完整，覆盖全链路 |
| 超额收益判断 | 区分结构性 vs 阶段性 | 仅计算 A=R-B | 第一性原理：可持续能力 vs 运气 |
| 检查清单位置 | 嵌入报告第 7 章 + 独立 checklist 模块 | 仅嵌入报告 | checklist 独立模块可复用，报告内通过 checklist_result 渲染 |
| PDF 解析 | pdfplumber | PyPDF2 | 表格提取能力更强 |
| 文档存取 | 统一仓库（FundDocumentRepository） | 直接文件操作 | 隔离 PDF/缓存细节，支持 Protocol 注入测试 |
| 数据缓存 | PDF 文件缓存 + parsed report JSON 缓存 | 仅文件缓存 | 避免重复解析，schema 版本控制支持缓存失效 |
| 年报来源 | 当前 production default 为 EID single-source：`selected_source=eid`、`source_mode=single_source_only`、`fallback_enabled=false`；默认 orchestrator 只构造 EID source，repository/cache 只复用当前 EID policy metadata | Eastmoney、基金公司官网/CDN、CNINFO 或其他非 EID route 仅作为 deferred source candidate / historical evidence route | 单源 operational hardening 降低来源身份漂移；`not_found` / `unavailable` 是 terminal EID source failures；schema drift、identity mismatch、integrity error 必须 fail-closed |
| 审计策略 | MVP 程序审计（P1/P2/P3/C2/L1/R1/R2） | 三层全实现 | 降低复杂度，v2 引入 LLM 审计 |
| 质量门控 | FQ0-FQ6 规则 + golden answer correctness | 无质量门控 | 确保精选基金池抽取质量可量化追踪 |
| 温度计 | 当前生产方向为项目内自建温度计；CLI 默认全 A `wind_all_a`，并支持 `000300` / `000905` | 永久依赖有知有行页面抓取 | 公开页抓取不是长期稳定真源；自建能力必须在项目边界内定义数据源、公式、缓存、失败语义和审计证据 |
| 依赖注入 | Protocol + 构造函数默认值 | 框架级 DI | 轻量级，不引入额外依赖，测试友好 |
| ITEM_RULE | 代码内硬编码 manifest | 外部 YAML 配置 | 规则数量少（4 条），代码内定义可获类型检查 |
| 模板渲染 | 纯 Python 函数 | Jinja2 / LLM | MVP 确定性管线，避免模板引擎或 LLM 幻觉 |
| Dayu-Agent 依赖 | 不作为生产 runtime 直接依赖；上游代码只作为研究输入 | 一次性复制 Dayu 全量运行时依赖或入口；直接声明 `dayu-agent` 生产依赖 | 避免扩大依赖面，并保持能力在本项目边界内化 |
| Dayu 工程要求吸收 | 吸收 Python 3.11、setuptools、项目元数据、依赖分组、pytest/ruff/black 配置和包资源声明纪律 | 复制 Dayu Web/browser/wechat 入口 | 工程可复现性值得吸收；入口能力必须由本项目需求驱动 |
| 最终判断推导 | P10 程序化推导 + 开发者覆盖模式 | 纯人工判断 | 结构化输入 → 确定性输出，覆盖模式记录审计线索 |
| 来源失败分类 | EID single-source 五类失败处理：`not_found` / `unavailable` terminal；`schema_drift` / `identity_mismatch` / `integrity_error` fail-closed | 统一 fallback 策略或隐藏 fallback eligibility | 区分"EID 不可用/未找到"与"契约违背"，并避免非 EID fallback 静默掩盖来源错误 |
| ITEM_RULE 审计 | P12 后渲染校验（`rendered_segment_present`） | 仅前置校验 | 确保渲染后内容符合 ITEM_RULE 约束 |
| 跟踪误差披露 | P13/P14/P15 分阶段推进 | 可选且不可观测 | 指数基金核心指标；P13 建立结构化直接披露路径，P14 将其纳入指数/增强指数条件质量分母，P15 先获取 reviewed direct evidence，再决定是否进入 production golden |
| 温度计数据来源 | P19 使用 akshare 指数估值接口；全 A 使用 `stock_a_ttm_lyr()` + `stock_a_all_pb()` | 有知有行页面抓取作为长期真源 | 独立可控，不依赖第三方页面结构变化；当前公开页查询仅作为过渡/对比验证输入 |
| 温度计计算方法 | 基于有知有行公开方法论复现 | 自创估值算法 | 与项目投资方法论一致，结果方向可解释；不声称官方精确复刻 |
| 温度计加权方式 | 等权中位数 | 市值加权 | 对齐有知有行公开说明，反映全市场公司层面的估值分布 |
| 温度计到 `valuation_state` | P19-S3 已完成受控自动映射；仅 exact benchmark identity 命中支持指数时生效 | S1/S2 完成后静默接入 `analyze` 或所有基金泛化映射 | 自动影响报告判断属于分析输入变更；当前仅接受 `000300` / `000905` 精确指数映射，其他场景保持 `unavailable` |

## 11. 温度计设计

### 11.1 设计决策

| 决策 | 选择 | 备选方案 | 理由 |
|------|------|---------|------|
| 数据来源 | akshare + 中证指数官方或 akshare 指数估值接口 | 有知有行页面抓取 | 独立可控，不依赖第三方页面结构 |
| 计算方法 | 有知有行公开方法论复现 | 自创算法 | 与项目投资理念一致，便于解释 |
| 加权方式 | 等权中位数 | 市值加权 | 与有知有行公开说明一致 |
| 考察周期 | 两轮完整牛熊周期的动态窗口；P19-S1 必须先验证可取得历史长度 | 固定 10 年且不验证数据覆盖 | 兼顾方法论一致性和数据可得性 |
| 综合方式 | PE 分位 + PB 分位各 50% | PE 单指标 | 同时覆盖盈利和净资产估值 |
| 精确度目标 | 方向一致，数值合理偏差 | 精确复现 | 有知有行未公开精确算法，不能伪造精确一致性 |

### 11.2 核心算法

```text
输入：A 股市场或目标指数成分的当日 PE、PB + 历史 PE/PB 序列

1. PE 等权中位数 = median(样本内有效 PE)
2. PB 等权中位数 = median(样本内有效 PB)
3. PE 分位数 = percentile_rank(当日 PE 中位数, 历史 PE 中位数序列)
4. PB 分位数 = percentile_rank(当日 PB 中位数, 历史 PB 中位数序列)
5. 综合温度 = (PE 分位数 + PB 分位数) / 2
6. 估值状态候选 = low(≤30) / fair(30~70) / high(≥70)
```

历史 P19-S1/S2 只产出温度计读数和估值状态候选，不自动写入 `fund-analysis analyze`；P19-S3 已完成受控自动映射，当前适用范围见 §11.7。

### 11.3 温度区间定义

| 温度区间 | 范围 | 估值状态候选 | `ValuationState` | 投资含义 |
|----------|------|--------------|------------------|----------|
| 低估 | 0° ~ 30° | 低估 | `low` | 适合纳入买入前检查 |
| 中估 | 30° ~ 70° | 中估 | `fair` | 需要结合基金质量和资金期限 |
| 高估 | 70° ~ 100° | 高估 | `high` | 买入前应重点审查风险 |

温度计不得输出"买入""卖出"或仓位比例，只能作为检查清单估值输入。

### 11.4 支持指数与 Phase

| 优先级 | 指数 | 代码 | Phase |
|--------|------|------|-------|
| P0 | 沪深 300 | `000300` | P19-S1 |
| P0 | 中证 500 | `000905` | P19-S2 |
| P0 | 万得全 A / 全 A 市场 | `wind_all_a` | P19-S5 已实现；CLI 默认 |
| P1 | 创业板指 | `399006` | P19-S4 |
| P1 | 科创 50 | `000688` | P19-S4 |
| P1 | 中证红利 | `000922` | P19-S4 |
| P1 | 中证消费 | `000932` | P19-S4 |
| P1 | 中证医药 | `000933` | P19-S4 |

P19 初始 data-source review 曾因缺少可验证全 A PE 历史而阻断全 A 实现；P19-S5 后续 source feasibility 已验证 `akshare.stock_a_ttm_lyr()` 的 `middlePETTM` 与 `akshare.stock_a_all_pb()` 的 `middlePB` 存在 4828 个共同日期，并被接受为全 A PE/PB source contract。当前 `fund-analysis thermometer` 未传 `--index` 时默认查询 `wind_all_a`；`fund-analysis analyze` 的自动估值仍只限 P19-S3 接受的 exact `000300` / `000905` benchmark identity，不因全 A CLI 默认而泛化到主动、债券、QDII、FOF 或 ambiguous benchmark。

### 11.5 模块边界

| 层级 | 模块 | 职责 | 边界约束 |
|------|------|------|---------|
| UI | `fund_agent/ui/cli.py` | `fund-analysis thermometer` 命令入口 | 只调用 Service，不直接调用 akshare 或 Agent 内部计算器 |
| Service | `ThermometerService` | 编排请求、缓存策略、数据源选择和输出模型 | 可调用 Agent 层公开能力；不直接访问 akshare、官方接口或文件缓存细节 |
| Agent | `ThermometerCalculator` | PE/PB 分位数计算、温度综合、估值状态候选映射 | 纯计算，无 IO |
| Agent | `ThermometerDataSource` | 从 akshare/中证指数获取 PE/PB 数据 | 只返回结构化数据，不缓存，不参与 UI/Service 输出格式 |
| Agent | `ThermometerCache` | 历史数据缓存、增量更新 | 只负责存储，不计算，不决定估值状态 |

现有 `ThermometerService` 应作为 Service 编排入口复用并演进；现有 `FundThermometerAdapter` 只能作为过渡公开页适配器或对比验证输入，P19 生产真源不得依赖它。

### 11.6 核心类型

| 类型 | 说明 |
|------|------|
| `ThermometerReading` | 单次温度读数：指数代码、指数名称、PE/PB 分位、综合温度、估值状态候选、数据日期、回溯窗口 |
| `ThermometerBatchResult` | 批量温度结果：多个读数、计算时间、数据来源 |
| `PePbHistory` | PE/PB 历史序列：日期、PE、PB、样本数量、有效样本数量 |
| `ValuationState` | `Literal["low", "fair", "high", "unavailable"]`；当前仅在 P19-S3 接受的 exact benchmark identity 范围自动写入 `analyze` |

### 11.7 与 `analyze` 的集成

P19-S3 已允许 `fund-analysis analyze` 在受控范围内自动集成温度计：

- 指数基金和指数增强基金：仅当 exact benchmark identity 映射到 `000300` 或 `000905` 时使用指数温度；
- 主动基金：当前不使用业绩基准温度，保持 `unavailable`；如未来要支持，必须先定义基准映射和不确定性策略；
- QDII、债券、FOF 或无可用指数映射：返回 `unavailable`，检查清单第 6 题标记为灰灯；
- 用户显式传入 `--valuation-state` 时必须优先于自动温度计结果；
- 自动映射必须在审计输入中保留温度值、数据日期、来源、指数代码、回溯窗口和 unavailable 原因。

### 11.8 免责标注

CLI 和报告输出中必须包含等价说明：

```text
本温度计基于有知有行公开方法论独立计算，非有知有行官方数据。
计算方法：等权 PE/PB 中位数历史分位数综合。
与有知有行官方温度计可能存在合理偏差，仅供买入前检查参考。
```

### 11.9 非目标

- 不依赖有知有行页面抓取作为生产温度计真源；
- 不追求与有知有行温度计数值精确一致；
- 不提供短期择时信号；
- 不支持非 A 股市场温度计算，QDII 默认 `unavailable`；
- 不预测未来市场走势；
- 不输出买卖建议或仓位比例。

## 12. Plan Review 设计边界检查

每个后续 plan review 必须显式检查：

- 是否违反 §1.3 非目标；
- 是否保持 `UI -> Service -> Host -> Agent` 四层边界；
- 生产年报访问是否仍只通过 `FundDocumentRepository` / `FundDataExtractor`；
- 是否在当前确定性主链路中误拼接 Host/tool loop、LLM 写作、Evidence Confirm、计算型 tracking error、外部指数适配器或隐藏在 `extra_payload` 的显式参数；如计划进入 Host/Agent 路径，是否明确内化 Dayu Host/Engine 能力并通过独立 gate 设计；
- 是否遵守 `pyproject.toml` 工程基线：Python `>=3.11`、setuptools 打包、显式生产依赖、`test`/`dev` 可选依赖、pytest/ruff/black 配置入口、包内非 Python 资源必须经 `[tool.setuptools.package-data]` 声明；
- 是否说明测试覆盖率策略：当前 CI 全局 `--cov-fail-under=50` 是否仍足以守住本 gate，新增或大幅修改模块是否朝单文件 ≥80% 目标补测，任何低于目标的模块是否有 review/residual owner；
- 是否保持 License/repo hygiene：`pyproject.toml` license 与根目录 MIT `LICENSE` 文件一致，不能通过放宽测试掩盖仓库发布卫生问题；
- 是否仍以 Dayu 四层 `UI -> Service -> Host -> Agent` 为规则真源，不重新引入六层或三层口径；
- success signal 是否可验证，且不会激励在缺少直接证据时错误接受数据。
