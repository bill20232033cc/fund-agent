# MVP Service ExecutionContract boundary hardening plan review - boundary lens

Reviewed target: `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md`
Review gate: `MVP Service ExecutionContract boundary hardening gate`
Reviewer role: Gateflow-governed independent plan review agent, not controller
Review scope: Service / Host / Agent boundary, `ExecutionContract` vs `FundLLMExecutionRequest` ownership, CLI `--use-llm` opt-in regression matrix, `extra_payload` / open payload guard, docs/control sync decision.

## Findings

### 001-未修复-[高]-ExecutionContract 被规划成过宽的 Service runtime policy 容器
- **Blocking**: yes
- **位置**: plan `Contract / Schema / State-machine / Public-interface Changes` lines 95-168; `Field Placement Decisions` lines 239-256; `Slice 2` lines 343-354
- **问题类型**: 架构边界 / 过度耦合 / 契约缺失
- **当前写法**: plan 要求 `FundLLMExecutionContract` 直接包含 `analysis_request`、`chapter_policy`、`assembly_policy`、`provider_runtime_budget`、`quality_fail_closed_policy` 和 `safe_diagnostic_policy`，并把 provider timeout、Host timeout、安全诊断开关、partial / final assembly fail-closed policy 都列为 “Must be explicit in ExecutionContract”。
- **反例/失败场景**: implementation agent 会按 plan 把章节编排策略、最终总装策略、provider 运行预算和 CLI/Host 安全诊断显示策略都固化为 `ExecutionContract` 字段。下一步 Host/Agent 迁移时，这个名字会自然被当成 Host-facing 或 Agent-facing 公共输入，导致 Host-facing contract 名义上携带 Service 内部 policy，或者让后续代码为了读取 timeout / diagnostics 而开始依赖整份基金业务 contract。
- **为什么有问题**: `AGENTS.md` 明确 Service 负责 prompt / ExecutionContract 组装和质量策略选择，但 Host 只负责生命周期、并发、超时、取消、事件投递等通用运行治理，不负责 prompt 业务语义或报告判断。当前 plan 虽然写了 Host 不 inspect contract，但又把 Host timeout、safe diagnostic policy、chapter / assembly policy 放进名为 `ExecutionContract` 的对象，概念上把 Service 内部运行计划提升为 contract schema，削弱了本 gate 要硬化的边界。`FundLLMExecutionRequest` 已被 plan 定义为 runtime capabilities 容器，但除了 clients 之外没有承接这些 runtime policies。
- **直接证据**:
  - `AGENTS.md` lines 103-113: Service 负责业务用例 / prompt / ExecutionContract / 质量策略，Host 负责生命周期治理且不负责 prompt 业务语义、报告判断。
  - plan lines 95-107: `FundLLMExecutionContract` required fields 包含 `chapter_policy`、`assembly_policy`、`provider_runtime_budget`、`quality_fail_closed_policy`、`safe_diagnostic_policy`。
  - plan lines 163-168: `FundLLMExecutionRequest` 只额外包含 `llm_clients`，理由是 clients 是 runtime capabilities，不是 schema facts。
  - plan lines 218-227: Host 不得 inspect `chapter_policy`、`assembly_policy` 和 quality/fail-closed business policy。
- **影响**: implementation 可能生成技术上能跑但 contract 语义错误的 API；review 很难判断哪些字段是稳定业务事实、哪些只是 Service 内部运行计划；后续 Host/Agent gate 会在错误命名和字段归属上返工，或形成 “Host 不读但 Host-facing object 带业务 policy” 的长期耦合。
- **建议改法和验证点**:
  - 将 `FundLLMExecutionContract` 缩窄为业务事实 / 策略声明：例如 `schema_version`、normalized `fund_code`、`report_year`、`report_mode`、`llm_opt_in_mode`、必要的 normalized `FundAnalysisRequest` 或更窄的 `FundLLMAnalysisInput`，以及明确属于业务语义的 quality gate policy name。
  - 将 `ChapterOrchestrationPolicy`、`FinalAssemblyPolicy`、`ProviderRuntimeBudget`、`SafeDiagnosticPolicy` 和 `llm_clients` 放入 `FundLLMExecutionRequest` 或单独 `FundLLMRuntimePlan` / `FundLLMRuntimeCapabilities`，并在 plan 中声明这些对象是 Service-internal，不是 Host contract。
  - Host closure 只读取 `execution_request.runtime_budget.host_timeout_seconds` 或同等 Service-returned scalar，不读取 `ExecutionContract` 的业务字段。
  - 新增测试断言：`FundLLMExecutionContract` dataclass 不包含 `ChapterOrchestrationPolicy`、`FinalAssemblyPolicy`、provider client、safe diagnostic display policy 或 raw Host lifecycle fields；`FundLLMExecutionRequest` 可以包含 runtime-only fields，但 Host API 仍只接收 `operation_name`、`operation`、`timeout_seconds`、`session_id`。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 高

### 002-未修复-[高]-测试矩阵没有强制证明未显式 `--use-llm` 时不会调用新 Service builder 或 Host
- **Blocking**: yes
- **位置**: plan `Slice 3` lines 411-432; `Validation Matrix` lines 500-515; `Failure paths to test` lines 517-527
- **问题类型**: 测试缺口 / 架构边界
- **当前写法**: plan 要求保持默认 deterministic branch，且 smoke 跑 `fund-analysis analyze` / `checklist`；configured `--use-llm` 测试断言 typed request 路径，missing-config 测试断言 Service execution 不调用。但没有要求 monkeypatch 新的 `build_fund_llm_execution_request()`、provider config loader 或 `HostRuntimeRunner.run_sync()` 在默认 `analyze` / `checklist` 路径中 forbidden。
- **反例/失败场景**: implementation 把 `build_fund_llm_execution_request(request)` 放在 `if use_llm` 之前，用于预计算 typed request 或 timeout。默认 `fund-analysis analyze` 在有 LLM env 的开发机上可能静默读取 provider config / 构造 clients / 触发 Host 依赖；在无 env 的环境里可能提前 fail；而当前 plan 的 smoke 只证明某个 happy-path 命令退出 0，不会定位到 “默认路径不应触碰 LLM builder / Host” 的边界违例。
- **为什么有问题**: 当前设计真源明确默认 `analyze/checklist` 不读取 LLM env、不构造 provider，仍走确定性报告路径；control doc 也记录默认确定性路径仍为 `UI -> Service -> fund_agent/fund`，`--use-llm` 才由 Host runner 托管。此 gate 的核心是显式 opt-in 边界，测试必须把 “没有 opt-in 就不触碰 LLM preparation / Host” 当成一等断言。
- **直接证据**:
  - `docs/design.md` lines 497-500: `--use-llm` 是显式 opt-in；默认 `analyze` 不读取 LLM env、不构造 provider，仍走确定性报告路径。
  - `docs/implementation-control.md` lines 44-48: 当前 `--use-llm` 路径经 Host runner，默认确定性 `analyze/checklist` 仍为 UI -> Service -> Fund 过渡路径。
  - plan lines 421-432: configured `--use-llm` 与 missing-config / incomplete tests 有断言，但没有默认分支对新 builder / Host 的 forbidden 断言。
  - 当前 `tests/ui/test_cli.py` lines 1902-1932 已用 forbidden config/client monkeypatch 保护默认 product request；迁移后这些 monkeypatch target 会从 CLI 移走，plan 没有要求等价更新为 forbidden execution-request builder / Host runner。
- **影响**: implementation 可能无意中破坏 `--use-llm` opt-in，导致默认 CLI 开始依赖 LLM 环境、读取 provider config、构造 clients 或进入 Host runner。该回归用户可见且与 Non-goal 直接冲突，但现有计划的验证矩阵可能漏报。
- **建议改法和验证点**:
  - 在 Slice 3 tests 增加默认 `analyze` 断言：monkeypatch CLI 引用的 `build_fund_llm_execution_request` 或等价 Service builder 为 raising fake，monkeypatch `HostRuntimeRunner.run_sync` 为 raising fake，运行 `fund-analysis analyze 110011`，断言 exit 0、`FundAnalysisService.analyze()` called、builder/Host 未调用、`analyze_with_llm_execution()` 未调用。
  - 在 `checklist` tests 增加同类断言：`fund-analysis checklist 110011` 不调用 LLM builder / Host；`checklist --use-llm` 继续被 Typer 拒绝且不调用 Service。
  - missing-config `--use-llm` 测试应同时断言 Host 未运行、`analyze()` 未调用、`analyze_with_llm_execution()` 未调用，并区分 “builder fail before Host” 与 “Service execution fail inside Host”。
  - Validation Matrix 明确列出 `--use-llm` absent 的 negative assertions，而不是只列 deterministic smoke。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 高

### 003-未修复-[中]-设计真源和控制真源同步被留成未分类后续事项
- **Blocking**: yes
- **位置**: plan `Affected Files / Modules` lines 76-83; `Slice 4` lines 454-466; `Docs Decision` lines 529-537; `Risks / Open Questions` lines 585-590
- **问题类型**: 文档/控制面缺口 / residual owner 不清
- **当前写法**: plan 禁止 implementation worker 更新 `docs/design.md` / `docs/implementation-control.md`，只要求更新 `fund_agent/README.md`、`fund_agent/host/README.md`、`tests/README.md`。同时把 “Docs/control truth may need a later controller sync” 作为 non-blocking risk，但没有指定本 gate 退出前必须由 controller 形成同步裁决、同步 slice 或 residual owner。
- **反例/失败场景**: implementation 接受后，代码已经变成 “CLI 调用 Service builder 准备 `FundLLMExecutionRequest`，再由 Host 托管 Service execution”，但 `docs/design.md` 仍写当前事实为 “CLI 读取 typed env config，经 Host runner 托管，Service 构造 clients 并调用 `analyze_with_llm()`”；`docs/implementation-control.md` 仍把下一入口和当前事实停留在旧 gate。后续 agent 按真源恢复时，会把旧 route 当成当前事实，重新要求 CLI 读取 env 或调用旧 Service API。
- **为什么有问题**: 用户明确要求 review 检查 docs/control docs 的同步决策；AGENTS 要求 `docs/design.md` 是设计真源、`docs/implementation-control.md` 是实施总控入口，后续设计/重构/评审必须对照边界。当前 plan 的 “除非 controller 后续授权” 没有把同步变成 gate 完成条件，也没有给 residual risk owner/destination，无法防止 heavy boundary-contract gate 以 stale truth source 收尾。
- **直接证据**:
  - `AGENTS.md` lines 123-129: 后续设计、重构、评审必须显式对照边界；README、规则、实现不一致时不能长期并存；以代码为准。
  - `docs/design.md` lines 497-501: 当前事实仍描述 CLI 读取 provider env/config、经 Host runner 调用 Service `analyze_with_llm()`。
  - `docs/implementation-control.md` lines 44-51: 当前 startup guardrails 仍描述旧 `--use-llm` route，并要求所有业务参数在 typed request / contract / config 中显式声明。
  - plan lines 531-537: docs decision 只要求 package README/tests README，不更新 design/control。
  - plan lines 587-590: docs/control sync 被列为可能需要的 later controller sync，但无 owner/destination。
- **影响**: gate 接受后控制面可能与代码事实不一致；后续 controller 或 specialist 从 startup packet / design doc 恢复时会走旧边界，造成重复返工或错误评审标准。对 heavy boundary-contract gate，这属于验收链路缺口，而不是普通文档补充。
- **建议改法和验证点**:
  - plan 增加明确 Docs/control exit decision：implementation worker 仍可不改 `docs/design.md` / `docs/implementation-control.md`，但 controller 在 accepted implementation 前必须二选一：追加独立 docs/control sync slice，或写 controller judgment 把同步 deferred 到具体 artifact / owner / next gate。
  - 若本 gate 完成代码边界改变，至少更新 `docs/design.md` 当前已实现状态中 Route C Gate 4/5A 的 `--use-llm` 当前事实，以及 `docs/implementation-control.md` Startup Packet / Current Truth Guardrails 的 next entry/current gate。
  - 验证点：review/closeout artifact 明确列出 design/control sync status，且不把 Agent/tool-loop 或 old dayu.host route 写成已实现。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

## Assumptions Tested

- `ExecutionContract` 应表达 Service-owned 业务事实 / 策略声明，而不是把所有 Service runtime objects 都提升为 Host-facing 或 long-lived contract schema。
- `FundLLMExecutionRequest` 应承接 Service 内部 runtime capabilities，包括 clients 和可变运行计划；Host API 仍只接收通用 lifecycle inputs。
- `--use-llm` opt-in 的负向边界与成功 typed path 同等重要：默认 `analyze/checklist` 不应读取 LLM env、不构造 provider、不进入 Host。
- 禁止 `extra_payload` 的保护必须覆盖新 contract/request API，同时避免引入新的 `dict[str, Any]` / `Mapping[str, Any]` / `**kwargs` business bag。
- Heavy boundary-contract gate 完成时，设计真源和控制真源需要明确同步状态或 residual owner。

## Open Questions

None requiring user input. The blocking findings are plan-specification issues and can be resolved by tightening the plan before implementation.

## Residual Risks

- Keeping `analyze_with_llm()` alongside `analyze_with_llm_execution()` remains acceptable only if the plan explicitly marks the former as lower-level Service test hook / internal compatibility path and ensures CLI cannot call it.
- Existing Host tests already cover safe diagnostic key/value rejection; after the plan is fixed, code review should still verify new Service diagnostic policy does not duplicate or weaken Host's scalar allowlist.

## Plan Review Verdict

Plan review verdict: not accepted; blocking findings present.
