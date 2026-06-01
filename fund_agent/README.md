# fund_agent 开发手册

`fund_agent` 是基金分析 Agent 的 Python 包。目标架构统一为 Dayu 四层：

```text
UI -> Service -> Host -> Agent
```

当前默认生产主链路仍是确定性 CLI 管线：UI 直接调用 Service，Service 直接调用 `fund_agent/fund` 公开能力。`analyze --use-llm` 已接入本项目内化的最小 Host runner：CLI 解析输入，Service 准备 `FundLLMExecutionRequest` / `FundLLMExecutionContract`、runtime plan 和 provider clients，Host 只托管单次 run lifecycle、deadline/cancel、terminal state、安全诊断和 phase events，然后 Service 执行 LLM report 用例并调用 Fund 领域能力完成第 1-6 章写作/审计与最终总装。

Dayu 是架构参考和能力来源，不是生产 runtime 直接依赖。Host 能力在 `fund_agent/host` 内化实现，不直接依赖 `dayu-agent` / `dayu.host`；未来 Agent 执行内核、tool loop、runner、ToolRegistry 或 ToolTrace 也必须内化 Dayu Engine 能力，不直接依赖 `dayu-agent` / `dayu.engine`。`fund_agent/fund` 是当前 Agent 层基金领域能力包。

## 当前包边界

| 包 | 职责 |
|----|------|
| `fund_agent/ui` | Typer CLI、参数采集、stdout/stderr 输出和退出码 |
| `fund_agent/services` | 用例编排、请求校验、质量策略、调用 Agent 层基金能力、组合返回结果 |
| `fund_agent/host` | 最小 Host runtime governance：进程内 run lifecycle、deadline/cancel、terminal state、安全诊断和 phase events |
| `fund_agent/fund` | Agent 层基金领域能力：文档仓库、抽取、分析、模板、审计、quality gate、数据 adapter |
| `fund_agent/config` | 静态仓库默认路径，以及 Route C `--use-llm` 的 typed LLM env config；当前不提供 durable Host/Agent runtime 配置 |

目标包：

| 包 | 落地条件 |
|----|----------|
| `fund_agent/agent` | 出现通用 Agent 执行内核、tool loop、runner、ToolRegistry、ToolTrace 或 context budget 需求；实现内化 Dayu Engine 能力，不直接依赖外部 Dayu runtime |

## 稳定边界

- UI 只调用 Service，不直接读取年报、PDF、cache，也不直接导入 Agent 内部 helper。
- Service 可编排 `fund_agent/fund` 的公开函数和数据对象，不承载基金领域规则；`analyze` 只在 Service 层解析 product mode / developer override mode、归一化 quality gate 状态、处理 block/not-run 阻断，并在 Agent 层给出安全指数目标后调用自建温度计。
- Service 当前提供 `chapter_orchestrator` 作为 Route C Gate 3 的显式编排入口：只消费调用方提供的 `StructuredFundDataBundle` 或 `ChapterFactProjection`，调用 Fund 层 `ChapterFactProvider`、`chapter_writer` 和 `chapter_auditor`，按第 1-6 章执行 write-audit-repair policy，并输出 accepted chapter conclusions 供 Gate 4 使用。它不生成第 0/7 章正文，不读取仓库/PDF/cache/source helper，也不接入 Agent/dayu。
- Service 当前拥有 `execution_contract.py` 中的 `FundLLMExecutionContract` / `FundLLMExecutionRequest` 边界：稳定业务事实放在 contract，provider runtime、章节策略、总装策略、安全诊断策略、Host timeout 标量和 clients 放在 Service-owned request/runtime plan。CLI `analyze --use-llm` 只请求 Service 构造该 typed request，再把同步 operation 和 `runtime_plan.host_timeout_seconds` 交给 Host。
- Host 当前只接受 UI/CLI 传入的同步 operation closure、`operation_name`、`timeout_seconds` 和可选 `session_id`，生成 `HostRunResult`、`HostRunEvent` 和安全 diagnostics；Host 不导入 Service/Fund，不理解基金代码、年份、章节策略、ExecutionContract 业务字段，也不构造 provider clients。
- Service 当前拥有 Route C Gate 4 provider construction：`fund_agent/services/llm_provider.py` 把 typed `openai_compatible` env config 适配为 `ChapterOrchestratorLLMClients`，使用现有 `httpx` 调用 chat-completions endpoint，不引入 vendor SDK。CLI `analyze --use-llm` 只在 Service request 准备成功后通过 Host 调用 `FundAnalysisService.analyze_with_llm_execution()`；默认 `analyze` 和 `checklist` 保持确定性路径。
- `fund_agent/fund` 拥有基金类型判断、CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、估值状态解析规则、证据锚点、最终判断派生和审计规则。
- Fund writer/auditor 只知道 writer/auditor Protocol、章节 facts、draft 和 audit request；不读取环境变量，不构造 HTTP client，不知道 provider/model/key，也不直接依赖 `httpx` 或 Service provider factory。
- `FundAnalysisRequest.valuation_state=None` 表示允许自动估值；显式 `low/fair/high/unavailable` 都由 Service 短路为用户输入，不调用温度计。自动估值的结构化真源是 `ValuationStateResolution`，同一个对象进入 `FundAnalysisResult`、`TemplateRenderInput` 和 `ProgrammaticAuditInput`。
- 文档读取只通过 `FundDocumentRepository.load_annual_report(...)` 进入生产路径。
- `fund_agent/config/paths.py` 只集中维护仓库默认路径常量；`fund_agent/config/llm.py` 只解析 LLM env config。两者都不代表 workspace override、prompt manifest、scene registry、durable Host/Agent runtime 或工具运行时已经接入。

## 阅读顺序

1. `fund_agent/ui/cli.py`
2. `fund_agent/services/fund_analysis_service.py`
3. `fund_agent/services/chapter_orchestrator.py`
4. `fund_agent/fund/data_extractor.py`
5. `fund_agent/fund/documents/repository.py`
6. `fund_agent/fund/template/renderer.py`
7. `fund_agent/fund/audit/audit_programmatic.py`

更细的 Fund 机制见 `fund_agent/fund/README.md`。
