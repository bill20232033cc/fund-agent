# 基金行为教练 Agent —— 实施总控文档

> **版本**: v2.3
> **日期**: 2026-05-30
> **规则真源**: `AGENTS.md`
> **设计真源**: `docs/design.md`
> **控制真源**: `docs/implementation-control.md`
> **短启动入口**: `docs/current-startup-packet.md`
> **当前状态**: MVP real-provider stabilization and score-loop phase 已完成本地闭环；PR #21 保持 draft/open 且未由本 phase 修改外部状态。Gate A writer/auditor contract hardening 已本地接受；provider runtime timeout hardening 已本地接受；prompt-contract calibration 已本地接受；writer prompt contract diagnostic narrowing 已本地接受为诊断 gate；writer marker syntax repair 已本地接受；programmatic audit L1 calibration 已本地接受；provider runtime timeout follow-up 已作为诊断/code hardening 本地接受；independent body chapter execution 已本地接受；real provider independent body matrix rerun 诊断完成；provider runtime budget and prompt-cost root-cause calibration 已本地接受为诊断/runtime-cost hardening。Gate B real provider smoke acceptance 仍 blocked：真实 provider `006597 / 2024 --use-llm` 现在能观察章节 1-6 独立矩阵，`generated_chapter_ids=[1,2,3,4,5,6]`、`skipped_chapter_ids=[]`，但未生成完整 0-7 报告；compact mode 已把 chapter 2/6 writer prompt 从 approx `26086` / `29078` tokens 降到 approx `1590` / `2110` tokens；当前唯一主 blocker 为 `provider_runtime_timeout_small_prompt`。Gate C chapter generation score-loop design accepted as design-only。当前 `--use-llm` 实现已由本地 Host runner 托管为 `CLI -> Host runner -> Service -> fund_agent/fund -> provider HTTP call`；Host runner 提供进程内 run lifecycle、global deadline、cancel token、terminal run state、安全诊断和 phase events。下一入口调整为 `MVP Service ExecutionContract boundary hardening gate`；internalized Agent engine/tool-loop migration 保留为后续 Agent/tool-loop gate。Dayu 是架构参考与能力来源，不是生产 runtime 直接依赖；不得把 `dayu-agent` / `dayu.host` / `dayu.engine` 作为生产 runtime 直接依赖。

---

## Startup Packet

本文件只保留当前控制面。详细恢复入口见 `docs/current-startup-packet.md`；历史 release-maintenance 长账本只作为证据链，不再作为当前 phase 或 next entry。

### Current Truth Guardrails

- `AGENTS.md` 是最高优先级执行规则真源；若与本文档或 `docs/design.md` 冲突，先调整方案/实现，再回写文档。
- 当前 phase 是 `MVP real-provider stabilization and score-loop phase`；当前 gate 是 `MVP internalized Host runtime governance adapter implementation gate`，分类为 `heavy`，状态为 accepted locally：full validation 和 code review/re-review 已通过，accepted checkpoint 已创建。Provider runtime budget and prompt-cost root-cause calibration 已本地接受为诊断/runtime-cost hardening；当前唯一 provider blocker 仍是 `provider_runtime_timeout_small_prompt`。
- 当前默认实现仍以确定性 `fund-analysis analyze/checklist` 为生产主链路：结构化抽取、确定性分析、模板渲染、程序审计和 FQ0-FQ6 quality gate。
- Gate 1 已新增 Fund 层 typed projection：`project_chapter_facts()` / `ChapterFactProvider.project()` 将内存中的 `StructuredFundDataBundle` 投影为 `chapter_fact_projection.v1`。
- Gate 1 typed projection 只消费现有 bundle、CHAPTER_CONTRACT、preferred_lens 和 ITEM_RULE truth APIs；不读取仓库、PDF/cache/source helper、parser、LLM、Service、Host 或 dayu。
- facet 断言保持 fail-closed：无结构化精确证据时 `facets=()`；兼容标签只进入 `non_asserted_facets`，不得驱动 ITEM_RULE。
- Gate 2 已新增 Fund 层单章 writer/auditor primitives：`chapter_writer.py` 和 `chapter_auditor.py`。
- Gate 2 writer/auditor 只消费 Gate 1 chapter facts、writer draft 和显式注入的 LLM Protocol client；生产代码不读取仓库、PDF/cache/source helper、parser、真实 provider SDK、env/config、Service、Host 或 dayu。
- Gate 2 冻结了 anchor/missing marker、LLM audit 行协议、`prompt_only`、`llm_unavailable`、must_not_cover、L1 数值闭合、`non_asserted_facets`、第 5 章跨期缺口、E2 deferred 和 `repair_hint` 聚合等 fail-closed 合约。
- Gate 3 已新增 Service 层 `ChapterOrchestrator` / `orchestrate_chapters()`，作为 `chapter_orchestrator.v1` write-audit-repair façade：只消费显式 `StructuredFundDataBundle` 或 `ChapterFactProjection`、显式 writer/auditor LLM Protocol client 和可选 `ChapterFactProvider`，只生成模板第 1-6 章 accepted conclusions。
- Gate 3 不生成第 0/7 章，不构造生产 LLM provider，不读取仓库、PDF/cache/source helper、parser，不接入 Host/Agent/dayu。
- Gate 4 Slice 4A 已新增 Service 层 `FinalChapterAssembler` / `assemble_final_chapters()`，作为 `final_chapter_assembler.v1` deterministic final assembly：用现有 `FinalJudgmentDecision` 生成第 7 章，再用 accepted conclusions 与 Gate 4-local typed chapter 7 summary 生成第 0 章，最终渲染顺序为 `0 -> 1-6 -> 7`。
- Gate 4 Slice 4B 已新增 Service 层 `FundAnalysisService.analyze_with_llm()` / `FundLLMAnalysisResult`：复用 `_run_analysis_core()`，通过显式注入的 `ChapterOrchestratorLLMClients` 调用 Gate 3，始终调用 Slice 4A final assembly，partial/blocked 不回退确定性报告。
- Gate 4 Slice 4C/4D 已为 `fund-analysis analyze` 增加显式 `--use-llm` opt-in provider-backed 路径；配置完整时读取 typed env config，构造 Service-owned `openai_compatible` HTTP chat-completions writer/auditor clients，并调用 Service `analyze_with_llm()`。`checklist` 不支持 `--use-llm`。
- Gate 4 Slice 4D provider contract 是 typed env config + openai-compatible HTTP chat-completions over existing `httpx`；无 vendor SDK、无默认 vendor/model/base URL、无 provider fallback、无 live pytest smoke。Provider runtime timeout hardening 已在后续 gate 增加 timeout-only bounded retry/backoff。
- Missing/invalid config/construction fail-closed；provider runtime error、blocked/partial orchestration 或 incomplete final assembly fail-closed；无 deterministic fallback。pytest 使用 fake env、`httpx.MockTransport` 和 monkeypatch，不需要真实 key。
- Gate A 已强化真实 provider writer/auditor 合约：writer 固定结构段落和 exact `required_output` marker，parser 精确分类 `missing_required_structure` / `missing_required_output_marker` / `unknown_anchor` / `response_too_long` / `response_incomplete`，auditor line protocol parse failure 保持 blocked，regenerate 带 typed `ChapterRepairContext`，provider runtime 分类到 `llm_timeout` / `llm_rate_limited` / `llm_malformed_response` / `llm_network_error`。
- Provider runtime timeout hardening 已本地接受：`FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` 默认 `2`、范围 `1..3`；`FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS` 默认 `1.0`、范围 `0..30`；只有 timeout 会有界重试，rate limit / malformed / network / non-2xx 不重试；Service 层补齐 provider-safe diagnostics 的章节身份；CLI incomplete result 输出安全 first failed chapter summary。
- Prompt-contract calibration 已本地接受：writer prompt contract 更短且前置，auditor line protocol 继续严格 fail-closed，repair/regenerate 保持 bounded，`ChapterFailureCategory` 新增 `llm_timeout` / `audit_rule_too_strict`，`ChapterRunResult.failure_category` 驱动 CLI `first_failed_category`。
- Writer prompt contract diagnostic narrowing 已本地接受：新增安全 `failure_subcategory`、`ChapterPromptContractDiagnostic` typed counters、CLI `first_failed_subcategory` 和 `serialize_chapter_prompt_contract_diagnostics()`；不存 prompt、draft、raw provider response、raw audit response、API key 或 Authorization header。
- Writer marker syntax repair 已本地接受：missing marker guidance 改为 explicit contract block，parser / allowed missing reasons 仍严格；真实 provider 已越过上一 gate 的 chapter 1 `writer:invalid_missing_marker` blocker。
- Programmatic audit L1 calibration 已本地接受：新增安全 `l1_numerical_closure` taxonomy 和 L1 repair guidance，未放松 `_audit_numerical_closure()` 或 anchor proximity；candidate facet / forbidden phrase precedence 保持高于 L1。
- Provider runtime timeout follow-up 已本地接受：新增 `serialize_chapter_runtime_diagnostics()`、provider-bound prompt/runtime cost 标量和 CLI safe runtime summary；serializer/CLI 不输出 `message`、`model_name`、prompt、draft、raw provider response、raw audit response、API key 或 Authorization header。
- 最新真实 provider smoke / diagnostic：`006597 / 2024 --use-llm` CLI exit `1` / stdout empty / no deterministic fallback / `orchestration_status=partial` / `final_assembly_status=incomplete`。Same-source Service diagnostic with `prompt_payload_mode=compact` has `generated_chapter_ids=[1,2,3,4,5,6]`, `skipped_chapter_ids=[]`, `accepted_chapter_ids=[]`, `report_markdown_present=false`。Failed rows are provider runtime writer timeouts below the large prompt threshold: chapter 1 approx `2109` tokens, chapter 2 `1590`, chapter 3 `2575`, chapter 4 `1274`, chapter 5 `2518`, chapter 6 `2110`, all under bounded `60s x2` writer budget。Chapter 2/6 former large prompt cost reduced from approx `26086` / `29078` to `1590` / `2110`。No provider config/auth, large prompt cost, prompt contract, audit parse, fact gap or code bug evidence.
- Gate C score-loop design 已接受为 design-only：未来必须区分 `extraction_score`、`chapter_fact_score`、`chapter_generation_score`，并把 provider runtime timeout 作为 `not_scored` / `blocked_provider_runtime`，不得接入现有 golden / fixtures / score / quality gate / readiness。
- 当前 `--use-llm` 路径为 `CLI -> Host runner -> Service -> fund_agent/fund -> provider HTTP call`；默认确定性 `analyze/checklist` 仍为 UI -> Service -> fund_agent/fund 过渡路径；尚未接入 Agent 调度。
- 当前 runtime budget / prompt-cost 继续作为 provider timeout 归因和安全诊断；Host run state 现在提供 MVP 进程内生命周期边界，但不解决 provider endpoint small-prompt timeout。
- `internalized Host runtime governance adapter gate` 已完成 MVP 进程内最小闭环：global deadline、cancel token、terminal run state、safe diagnostics、run lifecycle 和 phase events。
- internalized Agent engine/tool-loop migration 是后续 Agent/tool-loop gate，不是当前 small-prompt provider timeout blocker 的最小解。
- Route C 是已接受的 MVP LLM report generation route；Gate 1-3 与 Gate 4 Slices 4A/4B/4C/4D 已作为当前代码事实 accepted locally。不得把 Agent runner/tool loop、durable Host session/resume/memory/reply outbox 或 dayu runtime 写成已实现事实。
- 目标架构保持 UI -> Service -> Host -> Agent。未来 Host 必须内化 Dayu Host 能力且不得直接依赖 `dayu-agent` / `dayu.host`；未来 Agent engine/tool loop/runner/ToolRegistry/ToolTrace 必须内化 Dayu Engine 能力且不得直接依赖 `dayu-agent` / `dayu.engine`。
- Service 可以组装业务用例、prompt/ExecutionContract 语义、报告生成策略和未来 write-audit-repair loop；Fund 作为 Agent 层基金领域能力包，拥有基金类型识别、CHAPTER_CONTRACT / preferred_lens / ITEM_RULE、事实抽取、审计规则和证据锚点语义。
- 所有业务参数必须在 typed request / contract / config 中显式声明；禁止通过 `extra_payload` 传递显式参数。
- 生产年报访问必须通过 `FundDocumentRepository`；Service、UI、Host、renderer、quality gate 不得直接调用具体来源、PDF cache 或下载 helper。
- 年报来源 fallback 继续按 `not_found` / `unavailable` eligible，`schema_drift` / `identity_mismatch` / `integrity_error` fail-closed。
- 本 gate 不改变 runtime、schema、score、snapshot、quality gate、golden fixture、golden answer、manifest、promotion state 或模板；本 gate 只为新裁决同步 `AGENTS.md` / design / control / startup 真源。

| Field | State |
|---|---|
| Branch baseline | `codex/local-reconciliation` |
| Current phase | `MVP real-provider stabilization and score-loop phase` |
| Current gate | `MVP internalized Host runtime governance adapter implementation gate` |
| Current gate classification | `heavy` |
| Current gate status | accepted locally; full validation and code review/re-review passed; Gate B still blocked by `provider_runtime_timeout_small_prompt`; Gate C design accepted |
| Next entry point | `MVP Service ExecutionContract boundary hardening gate` |
| Next gate classification | `standard/heavy`; Service/Host boundary contract hardening affects public execution contract and explicit parameter discipline |
| Design truth | `docs/design.md` |
| Control truth | `docs/implementation-control.md` |
| Short startup entry | `docs/current-startup-packet.md` |
| Accepted plan commit | `beb6891` |
| Accepted provider factory commit | `26203d3` |
| Accepted CLI provider wiring commit | `ab0590a` |
| Accepted docs/control sync commit | `4d0c19f` |
| Accepted aggregate review commit | `7a3dab9` |
| Accepted closeout entrypoint commit | `b0e68e0` |

## Current Gate

### Gate Objective

The local Gate 4 closeout is accepted and the user previously authorized the draft PR gate, but this phase made no external PR changes. PR #21 remains draft/open. Provider auth/config verification passed for the current MiMo-compatible configuration. Gate A hardened the writer/auditor contract, provider runtime timeout hardening is accepted locally, L1 calibration is accepted locally, provider runtime timeout follow-up is accepted as diagnostic/code hardening, and prompt-cost/root-cause calibration is accepted locally. Gate B real `006597 / 2024 --use-llm` smoke still fails closed: compact-mode service diagnostic proves chapters 1-6 all fail writer `llm_timeout` under bounded `60s x2`, while all writer prompts are below approx `3000` tokens. Final assembly is incomplete, stdout stays empty, and there is no deterministic fallback. Gate C score-loop design is accepted as design-only. PR #21 must not be marked ready, merged or released from this gate.

### Current Accepted Artifacts

| Purpose | Artifact |
|---|---|
| Source-of-truth plan | `docs/reviews/mvp-truth-pivot-context-compaction-plan-20260530.md` |
| Independent plan reviews | `docs/reviews/mvp-truth-pivot-context-compaction-plan-review-mimo-20260530.md`; `docs/reviews/mvp-truth-pivot-context-compaction-plan-review-glm-20260530.md` |
| Implementation evidence | `docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md` |
| Gate 1 plan | `docs/reviews/mvp-gate1-chapter-fact-provider-plan-20260530.md` |
| Gate 1 plan reviews | `docs/reviews/mvp-gate1-chapter-fact-provider-plan-review-mimo-20260530.md`; `docs/reviews/mvp-gate1-chapter-fact-provider-plan-review-glm-20260530.md` |
| Gate 1 implementation evidence | `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-evidence-20260530.md` |
| Gate 1 implementation reviews | `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-review-glm-20260530.md` |
| Gate 1 controller judgment | `docs/reviews/mvp-gate1-chapter-fact-provider-controller-judgment-20260530.md` |
| Gate 2 plan | `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-20260530.md` |
| Gate 2 plan decision | `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-decision-20260530.md` |
| Gate 2 implementation evidence | `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-evidence-20260530.md` |
| Gate 2 implementation reviews | `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-review-ds-20260530.md` |
| Gate 2 implementation re-reviews | `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-rereview-mimo-20260530.md`; `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-rereview-ds-20260530.md` |
| Gate 2 controller judgment | `docs/reviews/mvp-gate2-chapter-writer-auditor-controller-judgment-20260530.md` |
| Gate 3 plan | `docs/reviews/mvp-gate3-chapter-orchestrator-plan-20260530.md` |
| Gate 3 plan decision | `docs/reviews/mvp-gate3-chapter-orchestrator-plan-decision-20260530.md` |
| Gate 3 implementation evidence | `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-evidence-20260530.md` |
| Gate 3 implementation reviews | `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-review-ds-20260530.md` |
| Gate 3 review fix evidence | `docs/reviews/mvp-gate3-chapter-orchestrator-review-fix-evidence-20260530.md` |
| Gate 3 review fix re-reviews | `docs/reviews/mvp-gate3-chapter-orchestrator-review-fix-rereview-mimo-20260530.md`; `docs/reviews/mvp-gate3-chapter-orchestrator-review-fix-rereview-ds-20260530.md` |
| Gate 3 controller judgment | `docs/reviews/mvp-gate3-chapter-orchestrator-controller-judgment-20260530.md` |
| Gate 4 plan | `docs/reviews/mvp-gate4-final-assembler-cli-plan-20260530.md` |
| Gate 4 plan decision | `docs/reviews/mvp-gate4-final-assembler-cli-plan-decision-20260530.md` |
| Gate 4 Slice 4A implementation evidence | `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-evidence-20260530.md` |
| Gate 4 Slice 4A implementation reviews | `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-review-ds-20260530.md` |
| Gate 4 Slice 4A review fix evidence | `docs/reviews/mvp-gate4-final-assembler-slice4a-review-fix-evidence-20260530.md` |
| Gate 4 Slice 4A review fix re-reviews | `docs/reviews/mvp-gate4-final-assembler-slice4a-review-fix-rereview-mimo-20260530.md`; `docs/reviews/mvp-gate4-final-assembler-slice4a-review-fix-rereview-ds-20260530.md` |
| Gate 4 Slice 4A controller judgment | `docs/reviews/mvp-gate4-final-assembler-slice4a-controller-judgment-20260530.md` |
| Gate 4 Slice 4B implementation evidence | `docs/reviews/mvp-gate4-llm-service-implementation-evidence-20260530.md` |
| Gate 4 Slice 4B implementation reviews | `docs/reviews/mvp-gate4-llm-service-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-llm-service-implementation-review-glm-20260530.md` |
| Gate 4 Slice 4B controller judgment | `docs/reviews/mvp-gate4-llm-service-controller-judgment-20260530.md` |
| Gate 4 Slice 4C implementation evidence | `docs/reviews/mvp-gate4-cli-use-llm-implementation-evidence-20260530.md` |
| Gate 4 Slice 4C implementation reviews | `docs/reviews/mvp-gate4-cli-use-llm-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-cli-use-llm-implementation-review-glm-20260530.md` |
| Gate 4 Slice 4C controller judgment | `docs/reviews/mvp-gate4-cli-use-llm-controller-judgment-20260530.md` |
| Gate 4 Slice 4D provider plan | `docs/reviews/mvp-gate4-provider-construction-plan-20260530.md` |
| Gate 4 Slice 4D provider plan reviews | `docs/reviews/mvp-gate4-provider-construction-plan-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-provider-construction-plan-review-glm-20260530.md` |
| Gate 4 Slice 4D provider plan decision | `docs/reviews/mvp-gate4-provider-construction-plan-decision-20260530.md` |
| Gate 4 Slice 4D1 provider factory implementation evidence | `docs/reviews/mvp-gate4-provider-construction-4d1-implementation-evidence-20260530.md` |
| Gate 4 Slice 4D1 provider factory reviews | `docs/reviews/mvp-gate4-provider-construction-4d1-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-provider-construction-4d1-implementation-review-glm-20260530.md` |
| Gate 4 Slice 4D1 provider factory controller judgment | `docs/reviews/mvp-gate4-provider-construction-4d1-controller-judgment-20260530.md` |
| Gate 4 Slice 4D2 CLI provider wiring implementation evidence | `docs/reviews/mvp-gate4-provider-construction-4d2-implementation-evidence-20260530.md` |
| Gate 4 Slice 4D2 CLI provider wiring reviews | `docs/reviews/mvp-gate4-provider-construction-4d2-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-provider-construction-4d2-implementation-review-glm-20260530.md` |
| Gate 4 Slice 4D2 CLI provider wiring controller judgment | `docs/reviews/mvp-gate4-provider-construction-4d2-controller-judgment-20260530.md` |
| Gate 4 Slice 4D3 docs/control sync controller judgment | `docs/reviews/mvp-gate4-provider-construction-4d3-controller-judgment-20260530.md` |
| Gate 4 Slice 4D aggregate reviews | `docs/reviews/mvp-gate4-provider-construction-aggregate-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-provider-construction-aggregate-review-glm-20260530.md` |
| Gate 4 Slice 4D aggregate controller judgment | `docs/reviews/mvp-gate4-provider-construction-aggregate-controller-judgment-20260530.md` |
| Gate 4 closeout readiness reconciliation | `docs/reviews/mvp-gate4-closeout-readiness-reconciliation-20260530.md` |
| MVP local acceptance / real provider smoke plan | `docs/reviews/mvp-local-acceptance-real-provider-smoke-plan-20260530.md` |
| MVP local acceptance / real provider smoke evidence | `docs/reviews/mvp-local-acceptance-real-provider-smoke-evidence-20260530.md` |
| MVP local acceptance / real provider smoke review | `docs/reviews/mvp-local-acceptance-real-provider-smoke-review-zeno-20260530.md` |
| MVP local acceptance / real provider smoke controller judgment | `docs/reviews/mvp-local-acceptance-real-provider-smoke-controller-judgment-20260530.md` |
| MVP local acceptance / real provider smoke rerun evidence | `docs/reviews/mvp-local-acceptance-real-provider-smoke-rerun-evidence-20260530.md` |
| MVP local acceptance / real provider smoke rerun review | `docs/reviews/mvp-local-acceptance-real-provider-smoke-rerun-review-lovelace-20260530.md` |
| MVP local acceptance / real provider smoke rerun controller judgment | `docs/reviews/mvp-local-acceptance-real-provider-smoke-rerun-controller-judgment-20260530.md` |
| MVP real provider audit-block diagnostic | `docs/reviews/mvp-real-provider-audit-block-diagnostic-20260530.md` |
| MVP real provider audit-block diagnostic controller judgment | `docs/reviews/mvp-real-provider-audit-block-diagnostic-controller-judgment-20260530.md` |
| MVP provider auth/config verification | `docs/reviews/mvp-provider-auth-config-verification-20260531.md` |
| MVP provider auth/config verification controller judgment | `docs/reviews/mvp-provider-auth-config-verification-controller-judgment-20260531.md` |
| MVP writer/auditor contract hardening plan | `docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-20260531.md` |
| MVP writer/auditor contract hardening implementation evidence | `docs/reviews/mvp-llm-writer-auditor-contract-hardening-implementation-evidence-20260531.md` |
| MVP writer/auditor contract hardening reviews | `docs/reviews/mvp-llm-writer-auditor-contract-hardening-code-review-mimo-20260531.md`; `docs/reviews/mvp-llm-writer-auditor-contract-hardening-code-review-glm-20260531.md` |
| MVP writer/auditor contract hardening re-reviews | `docs/reviews/mvp-llm-writer-auditor-contract-hardening-code-rereview-mimo-20260531.md`; `docs/reviews/mvp-llm-writer-auditor-contract-hardening-code-rereview-glm-20260531.md` |
| MVP writer/auditor contract hardening controller judgment | `docs/reviews/mvp-llm-writer-auditor-contract-hardening-controller-judgment-20260531.md` |
| MVP real provider smoke acceptance controller judgment | `docs/reviews/mvp-real-provider-smoke-acceptance-controller-judgment-20260531.md` |
| MVP real provider independent body matrix evidence | `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-evidence-20260531.md` |
| MVP real provider independent body matrix reviews | `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-review-mimo-20260531.md`; `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-review-glm-20260531.md` |
| MVP real provider independent body matrix controller judgment | `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-controller-judgment-20260531.md` |
| MVP chapter generation score-loop design | `docs/reviews/mvp-chapter-generation-score-loop-design-20260531.md` |
| MVP chapter generation score-loop design reviews | `docs/reviews/mvp-chapter-generation-score-loop-design-review-mimo-20260531.md`; `docs/reviews/mvp-chapter-generation-score-loop-design-review-glm-20260531.md` |
| MVP chapter generation score-loop design controller judgment | `docs/reviews/mvp-chapter-generation-score-loop-design-controller-judgment-20260531.md` |
| MVP real-provider stabilization and score-loop phase judgment | `docs/reviews/mvp-real-provider-stabilization-score-loop-phase-controller-judgment-20260531.md` |
| MVP provider runtime timeout hardening plan | `docs/reviews/mvp-provider-runtime-timeout-hardening-plan-20260531.md` |
| MVP provider runtime timeout hardening implementation evidence | `docs/reviews/mvp-provider-runtime-timeout-hardening-implementation-evidence-20260531.md` |
| MVP provider runtime timeout hardening reviews | `docs/reviews/mvp-provider-runtime-timeout-hardening-code-review-glm-20260531.md`; `docs/reviews/mvp-provider-runtime-timeout-hardening-code-rereview-mimo-20260531.md` |
| MVP provider runtime timeout hardening controller judgment | `docs/reviews/mvp-provider-runtime-timeout-hardening-controller-judgment-20260531.md` |
| MVP prompt-contract calibration plan | `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-20260531.md` |
| MVP prompt-contract calibration implementation evidence | `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-implementation-evidence-20260531.md` |
| MVP prompt-contract calibration reviews | `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-code-review-mimo-20260531.md`; `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-code-review-glm-20260531.md` |
| MVP prompt-contract calibration controller judgment | `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-controller-judgment-20260531.md` |
| MVP provider runtime budget and prompt-cost root-cause calibration plan | `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-20260531.md` |
| MVP provider runtime budget and prompt-cost root-cause calibration plan reviews | `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-review-mimo-20260531.md`; `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-review-ds-20260531.md` |
| MVP provider runtime budget and prompt-cost root-cause calibration implementation evidence | `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-implementation-evidence-20260531.md` |
| MVP provider runtime budget and prompt-cost root-cause calibration code reviews | `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-code-review-mimo-20260531.md`; `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-code-review-ds-20260531.md` |
| MVP provider runtime budget and prompt-cost root-cause calibration validation evidence | `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-validation-evidence-20260531.md` |
| MVP provider runtime budget and prompt-cost root-cause calibration deep review | `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-deepreview-20260531.md` |
| MVP provider runtime budget and prompt-cost root-cause calibration controller judgment | `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-controller-judgment-20260531.md` |
| MVP internalized Host runtime governance adapter implementation evidence | `docs/reviews/mvp-internalized-host-runtime-governance-adapter-implementation-evidence-20260601.md` |
| MVP internalized Host runtime governance adapter code review / re-review | `docs/reviews/mvp-internalized-host-runtime-governance-adapter-code-review-20260601.md`; `docs/reviews/mvp-internalized-host-runtime-governance-adapter-code-rereview-20260601.md` |
| MVP internalized Host runtime governance adapter controller judgment | `docs/reviews/mvp-internalized-host-runtime-governance-adapter-controller-judgment-20260601.md` |
| Prior release-maintenance roadmap summary | `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md` |
| Prior overnight closeout summary | `docs/reviews/overnight-release-maintenance-closeout-20260529.md` |
| Historical control snapshots | `docs/archive/implementation-control-history-20260525.md`; `docs/archive/implementation-control-release-maintenance-ledger-20260527.md` |

The Current Accepted Artifacts table is intentionally short. Older release-maintenance artifacts remain available through the historical index and review artifacts, but are not active gate truth for this MVP phase.

### Current Decision Summary

- Route C is the accepted MVP LLM report generation route; Gates 1-3 and Gate 4 Slices 4A/4B/4C/4D are accepted local code facts; Gate 5A internalized Host runtime governance adapter is a user-facing MVP readiness prerequisite; Gate 5B internalized Agent engine/tool-loop migration remains future design.
- Current deterministic `fund-analysis analyze/checklist` remains the default production report/checklist mainline; `fund-analysis analyze --use-llm` is the explicit provider-backed opt-in path.
- Local PR #21 acceptance is no longer blocked by the old HTTP `401` provider_config issue for the current MiMo configuration. Provider timeout hardening, prompt-contract calibration, diagnostic narrowing, marker syntax repair, L1 calibration, provider runtime timeout follow-up and independent body execution are accepted locally. The current blocker is still real provider smoke acceptance: latest independent-body real provider rerun fails closed before complete chapters 0-7 with primary blocker `provider_runtime_timeout`; final assembly is incomplete, stdout empty and no deterministic fallback.
- Gate 1 `ChapterFactProvider` typed projection is implemented and accepted locally as Fund-layer code fact.
- Gate 2 `chapter_writer` / `chapter_auditor` single-chapter primitives are implemented and accepted locally as Fund-layer code facts.
- Gate 3 `chapter_orchestrator` is implemented and accepted locally as Service-layer write-audit-repair façade for chapters 1-6.
- Gate 4 Slice 4A `final_chapter_assembler` is implemented and accepted locally as Service-layer deterministic final assembly for chapters 0 and 7 plus accepted body chapters.
- Gate 4 Slice 4B `FundAnalysisService.analyze_with_llm()` is implemented and accepted locally as Service-layer LLM analyze use case over deterministic core, Gate 3 and Slice 4A.
- Gate 4 Slice 4C/4D `fund-analysis analyze --use-llm` is implemented and accepted locally as explicit provider-backed CLI opt-in: complete typed env config constructs Service-owned `openai_compatible` writer/auditor clients and calls `analyze_with_llm()`; missing config, construction failure and incomplete LLM result fail closed without deterministic fallback.
- `facet_recognizer` and full `FundToolService` remain future candidates; Gate 1 did not implement them.
- Gate 4 Slice 4D1 provider factory was accepted in commit `26203d3`; Gate 4 Slice 4D2 CLI provider wiring was accepted in commit `ab0590a`; 4D3 docs/control sync was accepted in commit `4d0c19f`; 4D aggregate review was accepted in commit `7a3dab9`.
- Golden / strict correctness / QDII / FOF / `110020` / fixture promotion blockers are residual product-quality work, not blockers for starting MVP report generation Gate 1.
- Local Host runtime governance is implemented for `--use-llm`; Agent/dayu runtime is not implemented. Internalized Agent engine/tool-loop remains deferred.

## Route C Future Route

| Gate | Future scope | Boundary |
|---|---|---|
| MVP Gate 1 | `ChapterFactProvider` typed projection accepted locally; `facet_recognizer` / full `FundToolService` remain future candidates | Agent/Fund owns fund-type/facet/fact/evidence semantics; no Service/Host/dayu runtime introduced |
| MVP Gate 2 | `chapter_writer` + `chapter_auditor` accepted locally as Fund-layer single-chapter primitives | LLM writing/audit consumes structured facts, derived calculations, explicit data gaps and evidence anchors only; no Service/Host/dayu/CLI integration introduced |
| MVP Gate 3 | `chapter_orchestrator` accepted locally | Service owns write-audit-repair policy for chapters 1-6; calls Agent/Fund capabilities through explicit contracts |
| MVP Gate 4 | Slices 4A `final_chapter_assembler`, 4B Service `analyze_with_llm`, 4C CLI `--use-llm` and 4D provider construction accepted locally | `--use-llm` is explicit opt-in; deterministic `analyze/checklist` remains default unless a later gate changes it |
| MVP Gate 5A | internalized Host runtime governance adapter | MVP process-local implementation accepted by this gate; covers global deadline, cancel token, terminal run state, safe diagnostics, run lifecycle and phase events; durable session/resume/memory/reply outbox remains future Host scope |
| MVP Gate 5B | internalized Agent engine/tool-loop migration | Future Agent engine/tool loop internalizes Dayu Engine capabilities; not required to classify or resolve the current small-prompt provider timeout |

## Open Residuals

| Residual | Current disposition | Owner / next gate |
|---|---|---|
| Golden / strict correctness / fixture promotion | Residual only for MVP report generation; no promotion allowed without a separate accepted future gate | Future strict golden / fixture promotion gate |
| `004393` / `004194` / `006597` promotion readiness | `004393`, `004194`, `006597` are not promotion-prep-ready; `fixture_state=absent`; `promotion_allowed=false` | Future promotion-prep readiness owner |
| QDII / FOF / `110020` / `017641` coverage | Deferred from minimum v1 and not ready for full v1; not blockers for MVP Route C Gate 1 | Future QDII / FOF / index evidence policy gates |
| Release-maintenance long ledger | Preserved by archive and review links only; not active startup surface | Historical Evidence Index |
| internalized Host runtime governance adapter | MVP process-local implementation complete for `--use-llm`; no external Dayu dependency added | Future durable Host scope only if session/resume/memory/outbox is required |
| internalized Agent engine/tool-loop migration | Deferred; not the minimal fix for current provider timeout blocker | Future Agent/tool-loop migration gate |
| Deterministic renderer default | Remains current default production behavior; provider-backed LLM report path is explicit `--use-llm` opt-in only | Current behavior |
| Provider reliability / polish | Timeout-only retry/backoff accepted locally; live provider smoke acceptance, multi-model writer/auditor split, provider fallback, chapter 0/7 LLM polish and Evidence Confirm are not implemented | Future provider reliability / LLM polish gates |
| PR #21 real provider smoke | Provider auth now passes for current MiMo config; timeout hardening, prompt-contract calibration, diagnostic narrowing, marker syntax repair, L1 calibration, runtime-cost diagnostic, independent body execution and prompt-cost/root-cause calibration accepted; latest compact-mode rerun proves chapters 1-6 independent (`generated=[1..6]`, `skipped=[]`) and ch2/ch6 prompt cost reduced below large-prompt threshold, but still fails closed before complete 0-7 report with primary blocker `provider_runtime_timeout_small_prompt` | Provider endpoint calibration remains a later diagnostic gate; Host now records fail-closed run state but does not resolve endpoint runtime |
| Programmatic audit C2 | Supplemental service diagnostic after a timeout-free run accepts chapters 1-2, then fails chapter 3 `programmatic_audit` with issue prefix `programmatic:C2` and subcategory `code_bug_other`; no complete 0-7 report | Future `MVP programmatic audit C2 calibration gate` after timeout is no longer first blocker |
| Score-loop implementation | Gate C design accepted only; not implemented and not connected to readiness/golden/quality gate | Future score-loop implementation gate after Gate B timeout is handled |
| Untracked unrelated workspace files | Not part of accepted evidence unless a later controller gate explicitly accepts them | Controller scope audit |

## Recent Active Gate Ledger

| Gate | Status | Summary | Next action |
|---|---|---|---|
| `MVP internalized Host runtime governance adapter implementation gate` | accepted locally | Adds `fund_agent/host` process-local Host runtime runner, safe run events, deadline/cancel, terminal state and `--use-llm` CLI integration without `dayu-agent`; full validation and code review/re-review passed; live provider smoke in current shell was blocked by absent provider env and does not change prior `provider_runtime_timeout_small_prompt` residual | Next entry remains `MVP Service ExecutionContract boundary hardening gate`; do not enter it until explicitly continuing that gate |
| `MVP provider runtime budget and prompt-cost root-cause calibration gate` | accepted locally as diagnostic/runtime-cost hardening; smoke still blocked | Compact writer payload and safe prompt-cost/runtime diagnostics accepted; ruff/full pytest/deterministic smoke/missing-config fail-closed PASS; real provider compact-mode CLI exit `1`, stdout empty, no fallback; Service diagnostic generated `[1..6]`, `skipped=[]`, `accepted=[]`; ch2/ch6 reduced from approx `26086`/`29078` tokens to `1590`/`2110`; all chapters writer timeout below `3000` tokens | Start `MVP Service ExecutionContract boundary hardening gate`; do not revisit provider config/auth or large-prompt slimming |
| `MVP real provider smoke acceptance rerun with independent body chapter matrix` | diagnostic complete; smoke blocked | Real provider CLI exit `1`, stdout empty, no deterministic fallback; service diagnostic generated full body matrix with `generated=[1..6]`, `skipped=[]`, `accepted=[4]`; final assembly incomplete; MiMo/GLM evidence reviews PASS; unique blocker `provider_runtime_timeout`, with chapter 2/6 writer prompts approx `26086`/`29078` tokens | Start `MVP provider runtime budget and prompt-cost calibration gate`; do not revisit provider config/auth |
| `MVP independent body chapter execution gate` | accepted locally | Removed body chapter fail-fast semantics: chapters 1-6 now each run independent write/audit/repair attempts from the same projection; `dependency_missing` is reserved for true writer dependency; CLI incomplete output includes safe all-chapter matrix; final assembly remains fail-closed; ruff, targeted/full pytest, deterministic smoke, missing-config fail-closed and artifact secret scan pass | Rerun real provider smoke to observe independent body matrix before selecting the next calibration gate |
| `MVP provider runtime timeout follow-up gate` | accepted diagnostic/code hardening; smoke still blocked | Added safe provider-bound prompt/runtime cost diagnostics, runtime serializer and CLI runtime summary; reviews PASS; earlier default provider budget proved chapter 1 auditor timeout, and later independent-body rerun localized current blocker to provider runtime timeout across writer/auditor rows | Historical evidence; current next entry is provider runtime budget and prompt-cost calibration |
| `MVP real-provider stabilization and score-loop phase` | blocked with accepted local work | Gate A writer/auditor contract hardening accepted; provider runtime timeout hardening accepted; prompt-contract calibration accepted; writer diagnostic narrowing, marker syntax repair, L1 calibration, provider runtime timeout follow-up, independent body execution and prompt-cost/root-cause calibration accepted; Gate B real provider smoke still blocked by `provider_runtime_timeout_small_prompt`; Gate C score-loop design accepted as design-only | Start `MVP provider endpoint small-prompt runtime budget calibration gate`; do not mark PR ready |
| `MVP programmatic audit L1 calibration gate` | accepted locally; superseded by timeout follow-up evidence | Added safe `l1_numerical_closure` taxonomy and L1 repair guidance without relaxing L1; local validation and two code reviews PASS; then provider runtime timeout follow-up showed default-budget chapter 1 auditor timeout and bounded-budget chapter 1 `audit_rule_too_strict` | Historical evidence for current gate; next active entry is chapter 1 auditor calibration |
| `MVP writer prompt contract diagnostic narrowing gate` | accepted locally as diagnostic; smoke still blocked | Added safe failure subcategory and prompt-contract diagnostic matrix; controller real provider service diagnostic localizes latest primary blocker to chapter 1 `invalid_marker` / `writer:invalid_missing_marker`; CLI rerun observed `candidate_facet_assertion`; no prompt/draft/provider response stored | Start `MVP writer marker syntax repair gate`; keep candidate facet as monitored secondary boundary |
| `MVP writer marker syntax repair gate` | accepted locally; smoke still blocked | Missing-marker prompt guidance changed to explicit contract block without parser relaxation; reviews PASS; real provider progressed to chapter 1 accepted and chapter 2 `programmatic:L1` audit failure | Start `MVP programmatic audit L1 calibration gate`; do not revisit provider config/auth |
| `MVP real provider smoke prompt-contract calibration gate` | accepted locally; smoke still blocked | Writer prompt shortened, auditor protocol stricter, repair bounded, failure taxonomy/CLI category improved; code reviews PASS; real provider reaches chapter 1 accepted in service rerun but chapter 2 blocks `prompt_contract` | Narrow writer contract failure subcategory without storing prompt/draft/provider response |
| `MVP provider runtime timeout hardening gate` | accepted locally; smoke still blocked | Timeout-only bounded retry, safe diagnostics and CLI first-failed summary implemented; MiMo/GLM review PASS; real provider still exits `1` without complete 0-7 report | Use evidence for prompt-contract calibration rerun; do not revisit auth/config unless env load fails |
| `MVP chapter generation score loop design gate` | accepted design-only | Design distinguishes extraction/fact/generation scores, routes provider timeout as not-scored, defines schema/taxonomy/task rules/thresholds/lifecycle/manual override; MiMo/GLM reviews PASS | Future implementation only after Gate B runtime blocker is handled |
| `MVP real provider smoke acceptance gate` | blocked by writer prompt contract | `006597 / 2024 --use-llm` exits `1` with empty stdout and no fallback; latest controller CLI first failed chapter `1` / `prompt_contract`; service diagnostic: chapter 1 accepted, chapter 2 `prompt_contract` | Start writer prompt contract diagnostic narrowing; preserve safety boundaries |
| `MVP LLM writer/auditor contract hardening gate` | accepted locally | Writer/auditor contract hardened; ruff, targeted pytest, full coverage, missing-config smoke pass; real provider diagnostic now classifies chapter 2 timeout precisely | Evidence feeds Gate B timeout follow-up |
| `MVP provider auth/config verification gate` | complete, blocked by writer/auditor contract | MiMo-compatible config loads and minimal chat-completions succeeds; real `--use-llm` smoke still exits `1`; chapter 1 writer produces draft but misses required structure/output markers, asserts candidate facets, LLM audit parse fails, and regenerate times out | Start `MVP LLM writer/auditor contract hardening gate` with plan/review before code changes |
| `MVP real provider audit-block diagnostic gate` | diagnostic complete, blocked by `provider_config` | Same-source Service diagnostic found chapter 1 `llm_exception` from provider HTTP `401`; no draft/audit attempt existed; chapters 2-6 were fail-fast dependency skips; no code fix accepted | Verify provider key/base URL/model permission in a secret-safe shell, then rerun real provider smoke |
| `MVP local acceptance / real provider smoke rerun with configured provider` | blocked by `audit_block` | Ruff and full pytest passed; deterministic default passed; missing-config `--use-llm` failed closed; real provider `--use-llm` loaded config but exited `1` with `orchestration_status=blocked`, no generated 0-7 report and no deterministic fallback | Start `MVP real provider audit-block diagnostic gate`; keep PR #21 draft/open |
| `MVP local acceptance / real provider smoke gate` | blocked by environment | Ruff and full pytest passed; deterministic `fund-analysis analyze 006597 --report-year 2024` passed with chapters `0-7`; missing-config `--use-llm` failed closed with exit `1` and no deterministic fallback; real provider smoke did not run because typed provider env is missing | Rerun single-fund real provider smoke after provider config is supplied; keep PR #21 draft/open |
| `MVP Gate 4 closeout / ready-to-open-draft-PR readiness reconciliation` | accepted locally | Local closeout accepted after ruff, `git diff --check`, CLI `--use-llm` fail-closed smoke and full pytest `1106 passed`, coverage `91.76%`; no runtime changes beyond accepted Gate 4 work | Await explicit user authorization for draft PR gate |
| `MVP Gate 4 Slice 4D aggregate review` | accepted locally | MiMo and GLM aggregate reviews passed with no blocking findings; controller judgment accepted provider construction as a local checkpoint in commit `7a3dab9` | Start `MVP Gate 4 closeout / ready-to-open-draft-PR readiness reconciliation gate` |
| `MVP Gate 4 Slice 4D3: docs, design/control sync, and full regression` | accepted locally | Synced README, design and control docs after 4D1/4D2; fixed `only` vs `default` control-doc blocker; full regression `1106 passed`, coverage `91.76%`; accepted commit `4d0c19f` | Completed by accepted aggregate review commit `7a3dab9` |
| `MVP Gate 4 Slice 4D2: CLI --use-llm provider construction wiring` | accepted locally | CLI `analyze --use-llm` now reads typed LLM env config, constructs Service-owned provider clients, calls `analyze_with_llm()`, keeps default `analyze` deterministic, and fail-closes missing config/construction/incomplete LLM result without deterministic fallback; accepted commit `ab0590a` | Start `MVP Gate 4 Slice 4D3: docs, design/control sync, and full regression gate` |
| `MVP Gate 4 Slice 4D1: typed LLM config and provider factory` | accepted locally | Added typed env config and Service-owned `openai_compatible` HTTP chat-completions provider factory over existing `httpx`; tests use fake env and `httpx.MockTransport`; accepted commit `26203d3` | Start `MVP Gate 4 Slice 4D2: CLI --use-llm provider construction wiring gate` |
| `MVP Gate 4 Slice 4D: production LLM provider construction plan` | plan accepted locally | Plan accepts `openai_compatible` HTTP chat-completions over existing `httpx`, typed env config, Service-owned provider factory, no provider SDK, no live pytest network, no deterministic fallback and controller amendments for audit prompt passthrough, API key handling and CLI temporary error removal | Start `MVP Gate 4 Slice 4D1: typed LLM config and provider factory implementation gate` |
| `MVP Gate 4 Slice 4C: CLI --use-llm opt-in fail-closed` | accepted locally | CLI `analyze --use-llm` added as explicit opt-in but fail-closes before Service LLM call because provider construction is absent; `checklist` rejects the flag; 46 CLI tests, Service regressions, full validation and two PASS reviews; no provider, Service internals, Fund, final judgment, quality, golden, score, snapshot, dayu changes | Start `MVP Gate 4 Slice 4D: production LLM provider construction plan gate` |
| `MVP Gate 4 Slice 4B: Service analyze_with_llm` | accepted locally | Service-layer `FundAnalysisService.analyze_with_llm()` implemented with explicit `llm_clients`, deterministic core reuse, Gate 3 orchestration, Slice 4A final assembly, 7 targeted tests, full validation and two PASS reviews; no CLI, provider construction, source access, final judgment semantic change, dayu, golden or quality changes | Start `MVP Gate 4 Slice 4C: CLI --use-llm opt-in fail-closed integration gate` |
| `MVP Gate 4 Slice 4A: final_chapter_assembler` | accepted locally | Service-layer deterministic final assembler implemented with typed contract, chapter 7 from existing final judgment, chapter 0 from accepted conclusions, 14 targeted tests, full validation, two PASS reviews and two PASS fix re-reviews; no Service LLM analyze use case, CLI, provider construction, source access, final judgment semantic change, dayu, golden or quality changes | Start `MVP Gate 4 Slice 4B: Service analyze_with_llm implementation gate` |
| `MVP Gate 3: chapter_orchestrator` | accepted locally | Service-layer chapter orchestrator implemented with explicit bundle/projection input, injected writer/auditor clients, fail-closed repair policy, 30 targeted tests, full validation, two PASS reviews and two PASS fix re-reviews; no chapter 0/7 assembly, CLI, provider construction, source access, dayu, golden or quality changes | Start `MVP Gate 4: final_chapter_assembler + chapter 0 + CLI --use-llm plan gate` |
| `MVP Gate 2: chapter_writer + chapter_auditor` | accepted locally | Fund-layer writer/auditor primitives implemented with 38 targeted tests, full validation, two PASS re-reviews and controller judgment; no orchestrator/repair loop/CLI/dayu/promotion/source access changes | Start `MVP Gate 3: chapter_orchestrator plan gate` |
| `MVP Gate 1: ChapterFactProvider typed projection` | accepted locally | Fund-layer `chapter_fact_projection.v1` implemented with tests, docs, two PASS reviews and controller judgment; no writer/auditor/orchestrator/CLI/dayu/promotion changes | Start `MVP Gate 2: chapter_writer + chapter_auditor plan gate` |
| `MVP truth pivot and context compaction gate` | accepted locally | Control truth pivots to MVP report generation; Route C future route recorded; deterministic current implementation preserved; docs-only validation recorded | Historical current-phase evidence only |
| `release-maintenance consolidation + overnight closeout` | accepted locally as historical evidence | All `promotion_allowed=false`; `004393` / `004194` / `006597` not promotion-prep-ready with `fixture_state=absent`; QDII / FOF / `110020` deferred; Host/Agent/dayu deferred; no score/quality/FQ0-FQ6/golden fixture/golden-answer/manifest/runtime promotion changes | Use Historical Evidence Index only; do not treat as current phase |

## Historical Evidence Index

Detailed historical control state is preserved outside the active startup surface:

- `docs/archive/implementation-control-history-20260525.md`
- `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`
- `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`
- `docs/reviews/overnight-release-maintenance-closeout-20260529.md`

Use these files only to reconstruct evidence. They must not override this Startup Packet, the Current Gate table, or `docs/design.md` current implementation sections.

## Design / Control Alignment Rules

1. `AGENTS.md` remains the highest-priority execution rule source.
2. `docs/design.md` remains the design truth for current architecture, boundaries, current product behavior, accepted future Route C, Dayu discipline, `FundDocumentRepository` source boundary, report-quality design and thermometer design.
3. `docs/implementation-control.md` remains the control truth for current phase, current gate, accepted artifacts, residual owners and next entry point.
4. `docs/current-startup-packet.md` is the short resume entry for later phaseflow work; it must mirror this control surface, not replace it.
5. Historical archive/review entries are evidence only. If archive content contradicts Startup Packet or `docs/design.md`, treat archive content as superseded unless a later controller judgment says otherwise.
6. Future updates should prefer a new `docs/reviews/` artifact plus a short control-doc reference over appending long logs.

## Resume Checklist

1. Read `AGENTS.md`.
2. Read `docs/current-startup-packet.md`.
3. Read `docs/design.md` current implementation and Route C future design sections.
4. Confirm current phase, current gate and next entry in this file.
5. Confirm role: controller or specialist.
6. Confirm allowed files and non-goals before edits.
7. Classify the next gate per `AGENTS.md`; default heavier when uncertain.
8. Preserve deterministic MVP boundaries and do not introduce runtime, golden, promotion, Host/Agent/dayu or template changes outside an explicit accepted gate.
