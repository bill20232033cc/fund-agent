# MVP internalized Agent engine and typed audit contract design review

## Review Context

- Gate: `MVP internalized Agent engine and typed audit contract design gate`
- Role: Gateflow-governed review agent / planreview posture; not controller.
- Reviewed target: `docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-20260602.md`
- Output artifact: `docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-review-20260602.md`
- Conclusion: `pass-with-risks`

## Scope And Source Of Truth

Required read set used:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/fund-analysis-template-draft.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1-controller-judgment-after-provider-restore-20260602.md`
- `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json`
- Current code facts in `fund_agent/services/chapter_orchestrator.py`, `fund_agent/fund/chapter_auditor.py`, `fund_agent/fund/chapter_writer.py`, `fund_agent/host/README.md`, `fund_agent/fund/README.md`

Review constraints honored: no code changes, no plan fixes, no gateflow/controller action, no commit/push/PR action. This artifact is the only file written.

## Assumptions Tested

- The design artifact is proposed design only, not current implementation fact.
- The design should be concrete enough to let a later planning agent write an implementation plan without inventing layer ownership, schemas, state transitions, or provider-client movement.
- Current controller judgment after provider restore supersedes stale control-doc text that still mentions missing provider config.
- Ch2/Ch6 timeout diagnosis must stay same-source and not be converted into audit relaxation evidence.
- Ch3 `must_not_cover` diagnosis must stay narrow and must not become implicit authorization for broad auditor relaxation.
- Dayu Engine internalization may use Dayu as reference only; no production dependency or copied runtime code is authorized.

## Findings

### 01-未修复-[中]-Agent runner 与 provider client ownership 没有收敛，后续实现可能重新设计跨层边界

- **位置**: `Proposed architecture boundary`, `Bounded LLM semantic audit design`, `Dayu Engine capabilities to internalize`, `Suggested implementation-planning slices`
- **问题类型**: 架构边界 / 契约缺失 / 不可直接实施
- **当前写法**: 设计把 Service 定义为保留 use case、ExecutionContract、quality/fail-closed/report assembly policy；Agent 拥有 runner、tool-loop、retry/repair、context budget 和 `ToolTrace`；Fund 拥有 bounded semantic audit tool adapter。它同时说 provider timeout 数字和 endpoint calibration 不在本 gate，LLM semantic audit tool 要有 timeout/max attempts/output/redaction policy 记录到 `ToolTrace`。
- **反例/失败场景**: implementation planning agent 需要把当前 `ChapterOrchestratorLLMClients(writer/auditor)`、Service-owned provider construction、Agent-owned tool loop、Fund-owned `ChapterAuditLLMClient` Protocol 串起来时，仍必须自行决定 provider clients 是否继续由 Service 构造并注入、是否迁到 Agent ToolRegistry、是否由 Fund adapter 包装 provider、timeout/retry budget 究竟从 Service runtime plan 传入 Agent 还是由 Agent 自己定义。任一选择都会改变跨层依赖方向或 public contract。
- **为什么有问题**: `AGENTS.md` 要求 Service 负责 prompt/ExecutionContract 组装和质量策略，Host 负责 lifecycle，Agent 负责 tool loop，Fund 负责审计规则；当前 `fund_agent/host/README.md` 明确当前 Service 管 provider clients/chapter policy/final assembly，Host 不检查 provider runtime budget；`fund_agent/services/chapter_orchestrator.py` 当前仍在 Service 层保存 `ChapterOrchestratorLLMClients`、`ChapterOrchestrationPolicy` 和 timeout/runtime diagnostics。目标设计已经正确指出这应迁到 Agent，但缺少过渡 contract：Service 声明哪些 ceilings，Agent 记录哪些 counters，provider client construction 是否保留在 Service。
- **直接证据**:
  - `AGENTS.md`：Service 管 use case/prompt/ExecutionContract/quality policy；Host 管 lifecycle；Agent 管 runner/tool-loop/ToolTrace/context budget；Fund 管 CHAPTER_CONTRACT/audit rules。
  - `docs/design.md`：当前 `--use-llm` 路径是 `CLI -> Service prepares FundLLMExecutionRequest / ExecutionContract -> Host runner -> Service -> fund_agent/fund -> provider HTTP call`，Agent runner/tool-loop 未实现。
  - `fund_agent/host/README.md`：Service 当前管 provider clients、chapter policy、final assembly；Host 禁止检查 provider runtime budget。
  - `fund_agent/services/chapter_orchestrator.py`：Service 当前定义 `ChapterOrchestratorLLMClients`、`ChapterOrchestrationPolicy`、provider runtime categories、timeout budget kinds 和 runtime diagnostics。
- **影响**: 后续 implementation plan 可能把 provider/runtime policy 错放到 Agent 或 Fund，也可能继续把 tool loop 留在 Service；两种结果都会让 review 无法判断边界迁移是否正确，增加返工风险。
- **建议改法和验证点**:
  - 在设计或 controller judgment 中补一个 MVP boundary handoff table：`Service declares ceilings/request/policy`、`Agent executes tool loop and records ToolTrace`、`Fund exposes writer/auditor/domain audit tools`、`provider client construction remains Service-owned until a separate provider-factory migration gate unless explicitly changed`。
  - 明确 Agent runner 输入/输出最小形状：输入接收 Service-declared runtime ceilings 和 injected tool clients；输出返回 accepted chapter state、typed issues、ToolTrace、安全 failure summary。
  - 后续 implementation plan 的第一 slice 只定义 contract/schema 和 fake-client boundary test，不迁移 provider construction。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 中

### 02-未修复-[中]-Typed audit contract 仍是概念清单，缺少可验收的 MVP schema、状态机和现有类型映射

- **位置**: `Typed audit contract design`, `Programmatic-first audit list`, `Acceptance criteria`
- **问题类型**: 契约缺失 / 不可直接实施 / 测试缺口
- **当前写法**: 设计列出 `AuditSubject`、`AuditRuleId`、`AuditLayer`、`AuditIssue`、`AuditDecision`、`RepairPlan`、`ToolTrace` 和若干 invariants，但没有定义字段必填性、enum 闭集、schema version、从当前 `ChapterAuditIssue` / `ChapterAuditResult` / `ChapterRunResult` / failure category 到新 contract 的迁移映射，也没有说明哪些 programmatic-first 项属于 MVP。
- **反例/失败场景**: implementation agent 可以各自发明 `AuditDecision.accepted/rejected/repairable/blocked` 与当前 `ChapterAuditStatus pass/fail/blocked`、`ChapterRepairAction none/regenerate/needs_more_facts/stop`、`ChapterRunStopReason` 的对应关系；也可能一次性实现 programmatic-first list 中的 Ch2 arithmetic、Ch3 missing-fact downgrade、Ch6 pressure thresholds、final judgment consistency，导致 schema、runtime 和 domain rules 同时变更。
- **为什么有问题**: 现有 code facts 已经有多个相邻但不等价的类型系统：`chapter_auditor.py` 的 `ChapterAuditIssue` 只有 `layer/rule_code/severity/message/location/fact_ids/anchor_ids/item_rule_ids/repair_hint`，`ChapterLLMAuditResult` 仍保存 `raw_response`；`chapter_orchestrator.py` 有 `ChapterRunStatus`、`ChapterRunStopReason`、`ChapterRepairAction`、`ChapterFailureCategory`、`ChapterFailureSubcategory` 和 runtime diagnostic serializers。新 typed contract 如果不先规定兼容映射，后续实现会在 Service、Agent、Fund 三处形成平行 schema。
- **直接证据**:
  - `fund_agent/fund/chapter_auditor.py` 当前 `ChapterAuditIssue` 与 `ChapterAuditResult` schema 是 `chapter_audit.v1`，LLM audit layer 只有 `programmatic / llm`，不是设计中的 `semantic_llm / evidence_confirm`。
  - `fund_agent/services/chapter_orchestrator.py` 当前有 chapter run status/stop reason/failure subcategory，并从 issue message 映射 repair corrections。
  - `fund_agent/fund/README.md` 明确 E2 Evidence Confirm 后续 gate 处理，当前 primitives 不实现 orchestrator/repair loop/final assembly/Host/Agent runtime。
  - `docs/fund-analysis-template-draft.md` 第 2/3/6 章合同覆盖 R=A+B-C、言行一致、压力测试等多个 domain rule；全部纳入同一个 MVP contract 会显著扩大实现面。
- **影响**: 后续 plan 不够 code-generation-ready；review 只能看到“typed”口号，无法验收 schema compatibility、fail-closed 语义、raw response redaction、repair budget exhaustion 是否真的被 issue/attempt id 绑定。
- **建议改法和验证点**:
  - 把 MVP schema 缩成一组明确 dataclass/TypedDict 草案：`schema_version`、closed enum domains、required/optional fields、redaction-safe serialization policy、current-type mapping table。
  - 把 MVP programmatic-first scope 限为 current acceptance loop 必需项：required output markers、must_not_cover issue identity、missing-fact downgrade marker、L1 issue identity、timeout as runtime tool failure；Evidence Confirm 和 final judgment consistency 留后续 owner。
  - 要求后续 plan 包含 fake-client tests：programmatic blocker cannot be overridden by semantic pass；timeout serializes as runtime failure without content issue；repair exhausted cites issue ids and attempt ids。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 中

### 03-未修复-[低]-Next gate 建议把 Ch3-only calibration 放入 Agent engine planning slices，容易突破 controller 已收窄的 Ch3 gate

- **位置**: `Ch2 / Ch6 timeout vs Ch3 must_not_cover`, `Next gate`, `Suggested implementation-planning slices`
- **问题类型**: 范围漂移 / sequencing 风险
- **当前写法**: 设计正确诊断 Ch2/Ch6 是 provider runtime blocker，Ch3 是 deterministic contract expression / repair-loop boundary problem；但建议 implementation-planning slices 中包含 `Slice D: Ch3-only deterministic contract / wording calibration, if separately accepted by the Ch3 planning gate`。
- **反例/失败场景**: controller 或后续 planning agent 可能把 Agent engine/tool-loop migration 与 Ch3 writer/repair/contract calibration 合并成一个 implementation work unit，进而同时迁移 runner、定义 ToolTrace、改 Ch3 contract/auditor granularity。这样会让 Ch3 root-cause same-source evidence 与 Agent-engine boundary refactor 互相污染。
- **为什么有问题**: Provider-restore controller judgment 明确授权的是“Ch3-only must_not_cover calibration plan”，并列出 non-goals：no Ch2/Ch6、no provider timeout tuning、no auditor relaxation、no implementation before plan/review accepted。当前设计 artifact 也说 Ch3 safest fix 需要下一 Ch3-only planning gate 决定，不授权 auditor relaxation。把 Ch3 calibration 作为 Agent engine planning slice，即使加了条件，也会降低这个隔离边界的可执行性。
- **直接证据**:
  - Controller judgment after provider restore：Ch2/Ch6 deferred；Ch3 only authorized for a narrow planning gate；implementation remains blocked until Ch3-only plan and independent review are accepted。
  - Retained `summary.json`：Ch2 first failed is `llm_timeout`; Ch3 failed with `repair_budget_exhausted` / `prompt_contract` / `code_bug_other`; Ch6 terminal stop reason is `llm_timeout` after mixed first attempt.
  - `chapter_auditor.py` current `_audit_must_not_cover()` literal phrase extraction can collide with required output item wording, which is a narrow Ch3 evidence thread rather than proof that Agent runner migration is required.
- **影响**: Scope creep; future implementation plan may attempt to fix Ch3 while changing runtime ownership, making regressions hard to attribute and violating the current controller's narrow authorization.
- **建议改法和验证点**:
  - Keep Agent engine / typed audit contract planning and Ch3-only calibration as two separate controller gates.
  - In this design gate, keep Ch3 as motivating evidence and contract requirement only; do not list it as an implementation slice under Agent engine.
  - Require any Ch3 implementation plan to cite retained Ch3 writer/repair/auditor artifacts and prove no provider budget, Ch2, Ch6, or auditor relaxation changes.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Positive Findings / Defensible Decisions

- Architecture direction is broadly aligned with `UI -> Service -> Host -> Agent`: Service should stop owning write-audit-repair mechanics; Agent should own runner/tool-loop/ToolTrace; Fund should own domain facts and programmatic audit semantics.
- The design correctly treats Ch2 and Ch6 as timeout/runtime evidence, not proof of prompt-contract or audit relaxation needs. The retained run shows Ch2 auditor timeout on small prompt and Ch6 terminal timeout after repair.
- The design correctly treats Ch3 as a separate deterministic contract/repair-loop problem and explicitly avoids auditor relaxation in this artifact.
- Programmatic-first over semantic audit is defensible: CHAPTER_CONTRACT markers, `must_not_cover`, ITEM_RULE, R=A+B-C arithmetic, fund-type lens, and missing-fact downgrade are deterministic contract or domain-rule questions, not open-ended LLM judgment.
- Dayu scope is safely stated as internalized capability reference only; no direct `dayu-agent` / `dayu.engine` production dependency or code copying is authorized.

## Open Questions For Controller

- Should provider client construction remain Service-owned for the first Agent runner MVP, with Agent only receiving injected writer/auditor tool clients and Service-declared ceilings?
- Is the next gate meant to be design acceptance only, or should controller require a design-fix artifact before implementation planning?
- Should Ch3-only calibration proceed before Agent engine planning, or remain parallel but explicitly separate?

## Residual Risks And Suggested Tracking

- `docs/implementation-control.md` contains stale front-matter about provider config missing while later artifacts and this handoff use provider-restored evidence. Suggested owner: controller truth-source sync gate, not this review agent.
- Current LLM audit result stores `raw_response`; future `ToolTrace` and retained artifacts must be allowlist-first to avoid prompt/raw-provider leakage. Suggested owner: first Agent schema implementation slice.
- Evidence Confirm remains deferred; do not let `semantic_llm` audit be described as source-evidence confirmation. Suggested owner: later Evidence Confirm gate.
- Programmatic-first list is intentionally broad; future implementation planning should split domain rule expansion by chapter/rule instead of implementing all listed categories at once. Suggested owner: Agent engine planning controller.

## Final Plan Review Conclusion

`pass-with-risks`

The proposed design is directionally sound and safe enough for controller consideration as a design artifact. It should not be handed directly to implementation planning until the provider-client ownership boundary, MVP typed audit schema/mapping, and Ch3 gate separation are explicitly tightened.

## Reviewer Self-Check

- Reviewed target, scope, source of truth and assumptions tested: pass.
- Findings are evidence-based, adversarial and actionable rather than style/nit feedback: pass.
- Open questions and residual risks are separated from findings: pass.
- Conclusion uses only allowed value `pass-with-risks`: pass.
- Output path is under `docs/reviews/` and only this review artifact was written: pass.
- No code, plan source, README, control doc, commit, push or PR changes made: pass.

Self-check: pass
