# MVP Service ExecutionContract boundary hardening plan

Date: 2026-06-01
Gate: `MVP Service ExecutionContract boundary hardening gate`
Gate type: heavy boundary-contract planning gate
Role: Gateflow-governed planning worker, not controller
Baseline: accepted previous checkpoint `906d734 gateflow: accept internalized host runtime governance adapter`
Artifact status: handoff-ready / code-generation-ready plan

## Worker Self-check

- Current gate / role: 当前只做 planning worker，输出本 plan artifact；不启动 `$gateflow` / `/gateflow`，不实现代码，不 commit / push / PR。
- Source of truth: 已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、`docs/current-startup-packet.md`、上一 gate controller judgment、Host runtime、CLI、Service、chapter orchestrator 和相关 tests。
- Scope boundary: 本 plan 只规划 Service ExecutionContract / typed request 边界硬化；默认 deterministic `analyze/checklist`、score、quality gate、golden、fixture、release / PR 状态和历史 residual 不进入本 gate。
- Stop conditions: 当前无 blocking open question；implementation 期间若需要 Host 理解基金业务、引入 dayu runtime、迁移 Agent/tool-loop 或把参数塞入 `extra_payload`，必须停止交回 controller。
- Evidence and validation: 完成信号是代码生成 worker 可按 slices 直接实现，且验证命令与预期断言明确。

## Goal / Motivation

本 gate 目标是把当前 `fund-analysis analyze --use-llm` 路径中散落在 CLI helper、Service 方法参数和 Host closure 里的执行语义，收敛成 Service-owned 显式 `ExecutionContract` / typed request。

当前已接受路径是：

```text
CLI -> Host runner -> Service -> fund_agent/fund -> provider HTTP call
```

本 gate 不改变这条路径的用户行为，而是硬化边界：

- UI/CLI 只表达用户输入和显式 `--use-llm` opt-in，不再组装 provider clients、chapter policy 或 provider/runtime budget。
- Service 解释基金业务、报告语义、prompt/chapter orchestration intent、final assembly policy、provider clients construction 和 fail-closed 策略；其中稳定业务事实进入 `FundLLMExecutionContract`，Service runtime-only 策略和能力进入 `FundLLMExecutionRequest` / `FundLLMRuntimePlan`。
- Host 只接收通用 operation、deadline、session/run 安全字段和 safe diagnostics；Host closure 只读取 Service request/runtime plan 上的 scalar `host_timeout_seconds` 来调用 `HostRuntimeRunner.run_sync(timeout_seconds=...)`，不得读取、不解释、不分支处理基金领域字段。
- 所有显式参数都在 dataclass / typed request / typed policy 中声明，禁止 `extra_payload`、`**kwargs` 或自由 dict 透传业务参数。

## Non-goals / Scope

本 gate 明确不做：

- 不迁移 Agent runner、tool-loop、ToolRegistry、ToolTrace、context budget 或 Agent execution kernel。
- 不引入 `dayu-agent`、`dayu.host`、`dayu.engine` 或任何外部 Dayu production runtime 依赖。
- 不改变默认 deterministic `fund-analysis analyze` 或 `fund-analysis checklist` 行为。
- 不改变 score、FQ0-FQ6 quality gate 语义、golden fixture、golden answer、snapshot、baseline/golden promotion、release-readiness 或 PR 外部状态。
- 不修 provider endpoint `provider_runtime_timeout_small_prompt`，不扩大 provider fallback，不做 live provider smoke acceptance。
- 不改变基金类型判断、CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、年报解析、writer/auditor 审计业务规则。
- 不处理历史 residual、untracked workspace artifact 或 PR #21 状态。

## Direct Evidence

1. `docs/current-startup-packet.md` 和 `docs/implementation-control.md` 均记录当前 `--use-llm` 路径为 `CLI -> Host runner -> Service -> fund_agent/fund -> provider HTTP call`，默认 deterministic `analyze/checklist` 仍绕过 Host。
2. 上一 gate controller judgment 接受本地 Host runtime governance：Host 只拥有 process-local run lifecycle、global deadline、cancel token、terminal state、safe diagnostics 和 phase events；不导入 Service/Fund，不构造 provider clients，不理解基金业务。
3. [fund_agent/ui/cli.py](/Users/maomao/fund-agent/fund_agent/ui/cli.py:231) 当前 CLI 构造 `FundAnalysisRequest`，随后在 `--use-llm` 分支调用 `_build_llm_clients_or_fail()` 和 `_run_llm_analysis_in_host()`。
4. [fund_agent/ui/cli.py](/Users/maomao/fund-agent/fund_agent/ui/cli.py:797) 当前 `_build_llm_clients_or_fail()` 在 CLI 里加载 env config、构造 `ChapterOrchestratorLLMClients`、构造 `ChapterOrchestrationPolicy`，并从 provider config 推导 Host timeout。
5. [fund_agent/ui/cli.py](/Users/maomao/fund-agent/fund_agent/ui/cli.py:852) 当前 `_run_llm_analysis_in_host()` 在 CLI closure 中捕获 `request`、`llm_clients`、`chapter_policy` 和 `timeout_seconds`，再调用 `FundAnalysisService.analyze_with_llm()`。
6. [fund_agent/services/fund_analysis_service.py](/Users/maomao/fund-agent/fund_agent/services/fund_analysis_service.py:172) 当前 `FundAnalysisRequest` 是 Service 请求，显式包含 fund code、report year、投资金额、估值、force refresh、mode、developer overrides 和 command source。
7. [fund_agent/services/fund_analysis_service.py](/Users/maomao/fund-agent/fund_agent/services/fund_analysis_service.py:587) 当前 `analyze_with_llm()` 接收 `request`、`llm_clients`、`chapter_policy`、`assembly_policy` 和可选 `host_context`；它复用 deterministic core，再调用 Gate 3 chapter orchestrator 和 Gate 4 final assembler。
8. [fund_agent/host/runtime.py](/Users/maomao/fund-agent/fund_agent/host/runtime.py:409) 当前 `HostRuntimeRunner.run_sync()` 只接收 `operation_name`、`operation`、`timeout_seconds` 和 `session_id`；docstring 明确 operation name 只用于安全诊断，不承载业务语义。
9. [tests/ui/test_cli.py](/Users/maomao/fund-agent/tests/ui/test_cli.py:1518) 当前 CLI tests 断言 configured `--use-llm` 会把 typed `ChapterOrchestrationPolicy` 和 Host context 传给 fake Service。
10. `rg extra_payload` 结果显示本仓库已有多处 contract tests 防止 `extra_payload`；本 gate 必须延续该纪律并给 Service ExecutionContract 增加同类测试。

## Affected Files / Modules

Implementation allowed files:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/execution_contract.py`（新增 Service-owned contract module；若 implementation worker 判断更适合放在现有 Service module，必须保持 public exports 和 tests 等价）
- `fund_agent/services/__init__.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/services/test_execution_contract.py`（新增）
- `tests/ui/test_cli.py`
- `tests/host/test_runtime_runner.py`（只允许新增/调整 Host 不理解业务语义的边界断言；不得改变 Host runtime 行为）
- `fund_agent/README.md`
- `fund_agent/host/README.md`
- `tests/README.md`

Read-only / forbidden for this gate:

- `fund_agent/fund/**`，除非只为 imports/type references 必需且 controller 另行授权。
- `fund_agent/agent/**`，不得创建或迁移 Agent runner/tool-loop。
- `pyproject.toml` dependency section，禁止加入 dayu 或 provider SDK。
- `docs/fund-analysis-template-draft.md`
- score / quality gate / golden / fixture / snapshot / release-readiness / PR 状态文件。
- `AGENTS.md`。
- `docs/design.md`、`docs/implementation-control.md`，除非 controller 在本 gate accepted implementation 前追加独立 docs/control sync slice，或在 controller judgment 中明确 deferred owner / artifact / next gate。

## Contract / Schema / State-machine / Public-interface Changes

### New Service-owned ExecutionContract

新增 Service-owned typed contract，推荐名称：

```python
FundLLMExecutionContract
```

Required fields:

- `schema_version: Literal["fund_llm_execution_contract.v1"]`
- `fund_code: str`
- `report_year: int`
- `report_mode: Literal["llm_report"]`
- `llm_opt_in_mode: Literal["explicit_cli_flag"]`
- `analysis_input: FundLLMAnalysisInput`（或等价 normalized analysis request reference；必须是 normalized business input，不得是 provider/runtime capability）
- `quality_policy: QualityPolicyDeclaration`（只表达业务质量策略声明，例如 resolved quality gate policy name 和 deterministic fallback 禁止声明）

Validation requirements:

- `fund_code == analysis_input.fund_code`
- `report_year == analysis_input.report_year`
- `analysis_input.command_source` is normalized to `"analyze"` for LLM report generation.
- `report_mode` only accepts `"llm_report"` in this gate.
- `llm_opt_in_mode` only accepts `"explicit_cli_flag"` in this gate.
- `quality_policy.deterministic_fallback_allowed` must be `False`.
- Contract dataclass fields must not include `extra_payload`, `kwargs`, `dict[str, Any]` business parameter bags, prompt text, draft text, raw provider response, raw audit response, API key or Authorization header.
- Contract dataclass fields must not include `ChapterOrchestrationPolicy`, `FinalAssemblyPolicy`, `ProviderRuntimeBudget`, `SafeDiagnosticPolicy`, `ChapterOrchestratorLLMClients`, Host lifecycle fields, safe diagnostic display toggles or provider/runtime clients.

`FundLLMAnalysisInput` must be an explicit normalized business input. It may mirror the current `FundAnalysisRequest` fields required by the LLM report use case, but it must not carry provider clients, Host runtime objects, prompt bodies, raw model responses or open payload bags.

`QualityPolicyDeclaration` must be a narrow business declaration. Runtime fail-closed mechanics such as partial orchestration handling and final assembly completion checks belong to the Service runtime plan below.

### New Service-internal request, runtime plan and policy types

Add typed Service policy objects:

```python
ProviderRuntimeBudget
QualityFailClosedPolicy
SafeDiagnosticPolicy
FundLLMRuntimePlan
FundLLMExecutionRequest
```

These types are Service-internal request/runtime planning objects. They are not Host-facing contract schema and must not be described as Host contract.

`ProviderRuntimeBudget` must explicitly include:

- `writer_timeout_seconds`
- `auditor_timeout_seconds`
- `repair_timeout_seconds`
- `timeout_max_attempts`
- `timeout_backoff_seconds`
- `max_output_chars`
- `prompt_payload_mode`

`QualityFailClosedPolicy` must explicitly include:

- `quality_gate_policy`
- `fail_on_quality_gate_block`
- `fail_on_quality_gate_not_run`
- `fail_on_partial_orchestration`
- `fail_on_incomplete_final_assembly`
- `deterministic_fallback_allowed`

`SafeDiagnosticPolicy` must explicitly include:

- `schema_version`
- `host_summary_enabled`
- `chapter_matrix_enabled`
- `runtime_scalar_diagnostics_enabled`
- `forbid_prompt`
- `forbid_draft`
- `forbid_raw_provider_response`
- `forbid_raw_audit_response`
- `forbid_secrets`

`FundLLMRuntimePlan` must contain:

- `chapter_policy: ChapterOrchestrationPolicy`
- `assembly_policy: FinalAssemblyPolicy`
- `provider_runtime_budget: ProviderRuntimeBudget`
- `quality_fail_closed_policy: QualityFailClosedPolicy`
- `safe_diagnostic_policy: SafeDiagnosticPolicy`
- `host_timeout_seconds: int`

`host_timeout_seconds` is the only runtime scalar the CLI Host closure may read from the Service-prepared request/runtime plan.

`FundLLMExecutionRequest` must contain:

- `contract: FundLLMExecutionContract`
- `runtime_plan: FundLLMRuntimePlan`
- `llm_clients: ChapterOrchestratorLLMClients`

The runtime plan and clients live in the request rather than the contract because they are runtime policies/capabilities, not stable business facts. `ChapterOrchestrationPolicy`, `FinalAssemblyPolicy`, `ProviderRuntimeBudget`, `SafeDiagnosticPolicy` and `llm_clients` must not be added to `FundLLMExecutionContract`.

### Service public API

Add Service-owned preparation and execution helpers:

```python
def build_fund_llm_execution_request(
    request: FundAnalysisRequest,
    *,
    opt_in_mode: Literal["explicit_cli_flag"] = "explicit_cli_flag",
) -> FundLLMExecutionRequest
```

This helper must:

- load typed LLM provider config via `fund_agent.config.llm`;
- construct provider clients via existing Service-owned `build_chapter_llm_clients()`;
- construct `ChapterOrchestrationPolicy(prompt_payload_mode="compact", max_output_chars=config.max_output_chars)`;
- derive `ProviderRuntimeBudget` and `host_timeout_seconds` from provider config using the existing formula unless tests prove a safer equivalent;
- construct `QualityPolicyDeclaration` from the request’s resolved quality policy;
- construct Service-internal `QualityFailClosedPolicy` from the request’s resolved quality policy;
- construct `SafeDiagnosticPolicy`;
- return one typed `FundLLMExecutionRequest`.

Add a Service execution method:

```python
async def analyze_with_llm_execution(
    self,
    execution_request: FundLLMExecutionRequest,
    *,
    host_context: HostRunContext | None = None,
) -> FundLLMAnalysisResult
```

This method must be the CLI-hosted path. It delegates to current `analyze_with_llm()` or shares a private implementation, but CLI must no longer pass `llm_clients` and `chapter_policy` as separate ad hoc parameters.

Existing `analyze_with_llm()` may remain for lower-level tests and backwards-compatible internal use, but the hardened boundary test must assert CLI uses the typed execution request path.

### Host public API / state machine

No Host state-machine behavior change is allowed in this gate.

Host `run_sync()` remains generic:

- `operation_name`
- `operation`
- `timeout_seconds`
- `session_id`

Host may receive `timeout_seconds=execution_request.runtime_plan.host_timeout_seconds`, but it must not inspect:

- `fund_code`
- `report_year`
- `report_mode`
- `llm_opt_in_mode`
- `analysis_input`
- `chapter_policy`
- `assembly_policy`
- quality/fail-closed business policy
- Fund domain rules

State transitions remain:

```text
created -> running -> succeeded | failed | cancelled | deadline_exceeded
```

No durable session/resume/memory/outbox semantics are introduced.

## Field Placement Decisions

### Must be explicit in `ExecutionContract`

- Fund identity: `fund_code`, `report_year`
- Report mode: `report_mode="llm_report"`
- LLM opt-in mode: `llm_opt_in_mode="explicit_cli_flag"`
- Normalized analysis business input or request reference: `analysis_input`
- Necessary quality policy declaration: resolved quality gate policy name and `deterministic_fallback_allowed=False`

### Must stay in Service

- Fund analysis use case selection and request normalization.
- Prompt/chapter orchestration intent for template chapters 1-6.
- Final assembly policy for template chapters 0/7 and complete report.
- Provider clients construction ownership.
- Mapping typed provider config to `ChapterOrchestratorLLMClients`.
- Mapping provider config to runtime budget and scalar Host timeout.
- Fail-closed interpretation of Service result, incomplete final assembly and quality gate exceptions before CLI rendering.
- Service-internal `FundLLMRuntimePlan`, including `ChapterOrchestrationPolicy`, `FinalAssemblyPolicy`, `ProviderRuntimeBudget`, `QualityFailClosedPolicy`, `SafeDiagnosticPolicy` and `host_timeout_seconds`.

### Must be forbidden from Host

- 基金类型判断。
- CHAPTER_CONTRACT / preferred_lens / ITEM_RULE 解析或应用。
- 年报解析、PDF/cache/source helper 调用、`FundDocumentRepository` 访问。
- writer/auditor 业务判断、programmatic audit 业务规则、final judgment 业务语义。
- provider client construction, prompt construction, prompt payload mode decisions.
- `FundLLMExecutionContract` business fields beyond receiving an opaque operation closure prepared by Service/CLI.
- score / golden / fixture promotion decisions.

## How To Prohibit `extra_payload`

Implementation must enforce this at three levels:

1. Type shape:
   - New contract/request/policy dataclasses use `frozen=True`, `slots=True`, explicit fields only.
   - No `extra_payload`, `metadata`, `context`, `payload`, `options`, `dict[str, Any]`, `Mapping[str, Any]`, `**kwargs` or open-ended business bags in public contract constructors.
   - Safe diagnostics remain scalar allowlisted and go through Host `build_safe_diagnostics()`.

2. Runtime validation:
   - `FundLLMExecutionContract.__post_init__()` validates identity and fixed enum values.
   - `SafeDiagnosticPolicy` defaults to forbidding prompt/draft/raw response/secret fields.
   - `ProviderRuntimeBudget` validates positive provider timeouts, `timeout_max_attempts >= 1`, and `prompt_payload_mode in {"compact", "full"}`.
   - `FundLLMRuntimePlan` validates positive scalar `host_timeout_seconds` and template chapter policy bounds.

3. Tests/static guard:
   - Add a Service contract test that inspects dataclass fields and public callable signatures to assert no field/parameter named `extra_payload`, no `**kwargs`, and no free `dict[str, Any]` / `Mapping[str, Any]` on new execution contract APIs.
   - Update existing CLI boundary test so `fund_agent/ui/cli.py` contains no `extra_payload`, no provider SDK, no `httpx`, no direct Fund imports, and no `build_chapter_llm_clients` call.

## Implementation Slices

### Slice 1: Service ExecutionContract Types

Objective: introduce explicit Service-owned contract/schema/policy types with validation and tests, without changing CLI behavior yet.

Allowed files:

- `fund_agent/services/execution_contract.py`
- `fund_agent/services/__init__.py`
- `tests/services/test_execution_contract.py`

Exact changes:

- Create the dataclasses listed above.
- Export them from `fund_agent.services`.
- Implement deterministic `host_timeout_seconds` derivation as a pure helper, moving the formula currently in CLI:

```text
host_timeout_seconds = max(1, (writer_timeout + auditor_timeout + repair_timeout) * timeout_max_attempts * chapter_count)
```

Use integer seconds and validate positive values.

- Do not load env or construct clients in this slice.
- Do not import Host runtime except optional type references if unavoidable; contract itself should not depend on Host internals.
- Keep `FundLLMExecutionContract` limited to business facts / declarations. Do not place `ChapterOrchestrationPolicy`, `FinalAssemblyPolicy`, `ProviderRuntimeBudget`, `SafeDiagnosticPolicy`, `llm_clients`, Host context, Host run id, timeout lifecycle state or diagnostic display toggles on the contract.

Tests:

- Construct a valid contract from normalized `FundLLMAnalysisInput` derived from `FundAnalysisRequest(fund_code="110011", report_year=2024, command_source="analyze")`.
- Assert invalid fund identity mismatch raises `ValueError`.
- Assert invalid report mode / opt-in mode raises `ValueError`.
- Assert deterministic fallback allowed raises `ValueError`.
- Assert budget validation rejects zero/negative timeout or attempts.
- Assert runtime plan validation rejects zero/negative `host_timeout_seconds`.
- Assert `FundLLMExecutionContract` dataclass fields do not include `chapter_policy`, `assembly_policy`, `provider_runtime_budget`, `safe_diagnostic_policy`, `llm_clients`, `host_context`, `host_timeout_seconds`, `session_id`, `run_id` or any Host lifecycle fields.
- Assert `FundLLMExecutionRequest` may contain runtime-only fields via `runtime_plan`, but this object is documented and tested as Service-internal and not passed into Host `run_sync()`.
- Assert dataclass fields and public function signatures do not contain `extra_payload`, `kwargs`, `dict[str, Any]` or `Mapping[str, Any]` open business bags.

Completion signal:

- `uv run pytest tests/services/test_execution_contract.py -q` passes.

Stop condition:

- Stop if implementing these types requires Host to import Service, Fund or config provider modules.

### Slice 2: Service-owned Provider Preparation

Objective: move LLM provider config/client/policy/budget preparation out of CLI and into Service-owned typed request creation.

Allowed files:

- `fund_agent/services/execution_contract.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/__init__.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/services/test_execution_contract.py`

Exact changes:

- Add `build_fund_llm_execution_request(request, opt_in_mode="explicit_cli_flag")`.
- The helper loads `LLMProviderConfig` via `load_llm_provider_config_from_env()` and builds clients via existing `build_chapter_llm_clients(config)`.
- The helper constructs:
  - normalized `FundLLMAnalysisInput`
  - `QualityPolicyDeclaration`
  - `ChapterOrchestrationPolicy(max_output_chars=config.max_output_chars, prompt_payload_mode="compact")`
  - `FinalAssemblyPolicy()` unless a future explicit parameter is added by controller
  - `ProviderRuntimeBudget` from typed provider config
  - `QualityFailClosedPolicy` from the request / developer override quality gate policy
  - `SafeDiagnosticPolicy`
  - `FundLLMRuntimePlan` with scalar `host_timeout_seconds`
  - `FundLLMExecutionContract`
  - `FundLLMExecutionRequest`
- Add `FundAnalysisService.analyze_with_llm_execution(execution_request, host_context=None)`.
- `analyze_with_llm_execution()` must call existing `analyze_with_llm()` with Service-internal runtime fields unpacked from `execution_request.runtime_plan` and clients from `execution_request.llm_clients`; it must not re-load env or reconstruct provider clients.
- Preserve existing quality gate exception propagation.
- Preserve incomplete final assembly semantics: no deterministic fallback.

Tests:

- Service helper with monkeypatched config/client builder returns `FundLLMExecutionRequest` whose contract has correct fund code, report year, report mode, opt-in mode, normalized analysis input and quality declaration.
- The same helper returns `runtime_plan` with positive `host_timeout_seconds`, `ChapterOrchestrationPolicy(prompt_payload_mode="compact")`, expected max output chars, expected provider runtime budget and no deterministic fallback.
- Contract shape test asserts runtime-only fields remain absent from `FundLLMExecutionContract` and present only on `FundLLMExecutionRequest.runtime_plan` / `llm_clients`.
- Missing config raises `LLMProviderConfigError` before Host run.
- Provider construction error raises `LLMProviderConstructionError` before Host run.
- `analyze_with_llm_execution()` produces the same accepted report as current `analyze_with_llm()` using fake writer/auditor.
- `analyze_with_llm_execution()` propagates `QualityGateBlockedError` and `QualityGateNotRunBlockedError`.
- `analyze_with_llm()` may keep existing tests, but add at least one assertion that the hardened path goes through `FundLLMExecutionRequest`.

Completion signal:

- `uv run pytest tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py -q` passes.

Stop condition:

- Stop if provider construction would move into Host or UI, or if the implementation needs live provider credentials.

### Slice 3: CLI -> Host Uses Typed Execution Request

Objective: change `fund-analysis analyze --use-llm` so CLI asks Service to prepare one typed execution request, then gives Host only generic lifecycle inputs.

Allowed files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- `tests/services/test_fund_analysis_service_llm.py` only if fake service signatures need alignment

Exact changes:

- Replace `_build_llm_clients_or_fail()` with a thin wrapper or direct call to `build_fund_llm_execution_request(request, opt_in_mode="explicit_cli_flag")`.
- Remove CLI imports of:
  - `load_llm_provider_config_from_env`
  - `build_chapter_llm_clients`
  - `ChapterOrchestratorLLMClients`
  - direct use of `ChapterOrchestrationPolicy` except for tests/helpers that no longer need it
- Change `_run_llm_analysis_in_host()` signature to accept only:

```python
execution_request: FundLLMExecutionRequest
```

and derive:

```python
timeout_seconds = execution_request.runtime_plan.host_timeout_seconds
```

- The Host operation closure calls:

```python
service.analyze_with_llm_execution(execution_request, host_context=host_context)
```

- Keep `_LLMIncompleteHostRunError`, incomplete result attachment and quality gate exception re-raise semantics unchanged.
- Keep Host `operation_name="fund_analysis_llm_report"`; do not encode fund code/year into operation name.
- Keep default deterministic branch exactly as:

```python
asyncio.run(FundAnalysisService().analyze(request))
```

Tests:

- Update fake Service to expose `analyze_with_llm_execution(execution_request, host_context=None)` and record `last_execution_request`.
- Configured `--use-llm` test asserts:
  - deterministic `analyze()` not called;
  - `analyze_with_llm_execution()` called;
  - `execution_request.contract.fund_code == "110011"`;
  - `execution_request.contract.report_year == 2024`;
  - `execution_request.contract.llm_opt_in_mode == "explicit_cli_flag"`;
  - `execution_request.runtime_plan.host_timeout_seconds` is positive;
  - Host context exists and timeout matches `execution_request.runtime_plan.host_timeout_seconds`;
  - Host fake records only `operation_name`, `operation`, `timeout_seconds`, `session_id` and never receives fund code/year/chapter policy/contract business fields as API arguments.
- Default `analyze` negative boundary test monkeypatches the CLI-visible Service builder / `build_fund_llm_execution_request` target and `HostRuntimeRunner.run_sync` to raising fakes, runs `fund-analysis analyze 110011`, and asserts exit `0`, deterministic `FundAnalysisService.analyze()` called, builder/Host not called, and `analyze_with_llm_execution()` not called.
- `checklist` negative boundary test applies the same raising fakes and asserts `fund-analysis checklist 110011` exits `0` without LLM builder / Host / LLM Service execution.
- `checklist --use-llm` negative boundary test asserts the CLI still rejects unsupported `--use-llm` for checklist, exits through Typer parsing/usage failure, and does not call deterministic Service, LLM builder, Host or LLM Service execution.
- Missing config / construction error tests still exit `1`, stdout empty, Host not run, deterministic `analyze()` not called and `analyze_with_llm_execution()` not called.
- Missing-config `--use-llm` must prove failure happens during Service request preparation before Host execution and before Service report execution.
- Incomplete result tests still include `LLM Host run 未完成`, first failed summary, safe matrix and no deterministic fallback.
- Boundary test asserts CLI source contains no provider SDK, no `httpx`, no `extra_payload`, no direct `fund_agent.fund` import, and no `build_chapter_llm_clients`.

Completion signal:

- `uv run pytest tests/ui/test_cli.py tests/services/test_fund_analysis_service_llm.py -q` passes.

Stop condition:

- Stop if the CLI needs to inspect chapter policy, provider timeout internals or Fund domain semantics after this slice.

### Slice 4: Host Boundary Regression And Docs Sync

Objective: prove Host remains business-agnostic and sync developer docs/tests docs for the new boundary.

Allowed files:

- `tests/host/test_runtime_runner.py`
- `tests/ui/test_cli.py`
- `fund_agent/README.md`
- `fund_agent/host/README.md`
- `tests/README.md`

Exact changes:

- Add/adjust tests to assert `fund_agent/host` source has no imports from `fund_agent.services` or `fund_agent.fund`.
- Assert Host diagnostics reject forbidden prompt/draft/raw response/secret keys through existing `build_safe_diagnostics()` behavior if not already covered.
- Update `fund_agent/README.md` to state current `--use-llm` boundary:

```text
CLI parses input -> Service prepares FundLLMExecutionRequest / ExecutionContract and provider clients -> Host runner governs lifecycle/deadline/cancel/safe events -> Service executes LLM report use case -> Fund domain capabilities write/audit chapters.
```

- Update `fund_agent/host/README.md` to clarify Host receives only generic operation/deadline/session diagnostics and must not inspect Service ExecutionContract business fields.
- Update `tests/README.md` to mention `tests/services/test_execution_contract.py` and the CLI typed execution request tests.
- Do not update user-facing root `README.md` unless CLI command or user-visible behavior changes; this plan expects no root README change.
- Record design/control truth-source sync status in the implementation artifact and closeout evidence. If controller has not authorized direct `docs/design.md` / `docs/implementation-control.md` edits in this slice, the artifact must say `design/control sync: deferred by controller decision required before accepted implementation`.

Tests:

- `uv run pytest tests/host/test_runtime_runner.py tests/ui/test_cli.py -q`
- `uv run ruff check .`

Completion signal:

- Docs describe current code facts only and do not claim Agent/tool-loop migration.

Stop condition:

- Stop if docs need to describe future Agent/Dayu runtime as implemented.

## Validation Matrix

Required targeted validation:

```bash
uv run pytest tests/services/test_execution_contract.py -q
uv run pytest tests/services/test_fund_analysis_service_llm.py -q
uv run pytest tests/ui/test_cli.py -q
uv run pytest tests/host/test_runtime_runner.py -q
```

Required combined validation:

```bash
uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

Required smoke validation:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --dev-override --quality-gate-policy off
uv run fund-analysis checklist 006597 --report-year 2024
```

Expected assertions:

- deterministic `analyze` exits `0` and outputs report markdown;
- deterministic `checklist` exits `0`;
- default `analyze` with raising fake Service builder and raising fake Host runner still exits `0`, calls deterministic `FundAnalysisService.analyze()`, and does not call builder / Host / `analyze_with_llm_execution()`;
- default `checklist` with the same raising fakes still exits `0` and does not call LLM builder / Host / LLM Service execution;
- `checklist --use-llm` remains unsupported if CLI has no checklist LLM mode; it is rejected before Service/Host execution and does not call deterministic Service, LLM builder or Host;
- missing-config `--use-llm` still exits `1`, stdout empty, no deterministic fallback, Host not run and Service report execution not called;
- configured fake/monkeypatched `--use-llm` goes through typed `FundLLMExecutionRequest`;
- Host fake sees only `operation_name`, `operation`, `timeout_seconds`, `session_id`; `timeout_seconds` equals scalar `execution_request.runtime_plan.host_timeout_seconds`;
- `FundLLMExecutionContract` fields do not include chapter orchestration policy, final assembly policy, provider clients, provider runtime budget, safe diagnostic display policy or Host lifecycle fields;
- incomplete LLM result exits `1`, stdout empty, includes safe Host run summary and safe chapter matrix;
- no provider SDK, no `dayu-agent`, no `dayu.host`, no `dayu.engine`, no direct Host import of Service/Fund;
- no `extra_payload` on new contract/request APIs.

Failure paths to test:

- missing LLM provider config;
- provider construction error;
- default `analyze` without `--use-llm` must not prepare LLM execution request or enter Host;
- default `checklist` without `--use-llm` must not prepare LLM execution request or enter Host;
- unsupported `checklist --use-llm` must fail before any Service/Host execution;
- quality gate blocked;
- quality gate not run;
- partial orchestration / incomplete final assembly;
- Host operation exception;
- invalid contract identity;
- invalid runtime budget;
- accidental `extra_payload` / `**kwargs` on contract APIs.

## Docs Decision

Docs updates are required only for developer-facing docs touched by boundary semantics:

- Update `fund_agent/README.md` because the Service/Host boundary and provider construction ownership are changing.
- Update `fund_agent/host/README.md` because Host must be explicitly documented as business-agnostic relative to the new ExecutionContract.
- Update `tests/README.md` because a new Service contract test module and updated CLI boundary tests are added.
- Do not update root `README.md` unless implementation changes user commands, env names, output, exit codes or user workflow.
- Implementation worker may leave `docs/design.md` and `docs/implementation-control.md` untouched inside the code/doc slices above, but this gate has a required exit decision before accepted implementation:
  - Option A: controller appends a dedicated docs/control sync slice that updates `docs/design.md` current implemented state and `docs/implementation-control.md` Startup Packet / Current Truth Guardrails / next entry point to the accepted Service builder typed request path.
  - Option B: controller judgment explicitly defers truth-source sync to a named artifact, owner and next gate before accepting implementation.
- If code facts change to `CLI -> Service builds FundLLMExecutionRequest / FundLLMRuntimePlan -> Host runner uses scalar timeout -> Service executes LLM report`, the recommended sync is Option A. The docs/control update must not describe Agent/tool-loop migration, old `dayu.host` runtime, or any direct production dependency on Dayu as implemented.
- Validation, review artifacts and closeout must record `design/control sync status` as one of: `synced in docs/control slice`, `deferred by controller judgment to <artifact/owner/next gate>`, or `not required because code facts unchanged`.

## Review Gates

Plan review should check:

- Contract is handoff-ready and does not leave field ownership to implementation guesswork.
- Host remains generic and business-agnostic.
- Provider construction moved to Service, not Host.
- CLI no longer constructs provider clients/chapter policy/runtime budget.
- No `extra_payload` or `**kwargs` escape hatch.
- Slices are small enough for implementation/review loops.
- Tests cover both successful typed path and fail-closed paths.

Code review should check:

- `fund_agent/host` has no Service/Fund imports.
- New contract validation is deterministic and explicit.
- `FundLLMExecutionContract` contains only business facts / quality declaration and excludes chapter policy, final assembly policy, provider clients, provider runtime budget, safe diagnostic display policy and Host lifecycle fields.
- `FundLLMExecutionRequest` is used by CLI-hosted path.
- Host API remains `operation_name` / `operation` / `timeout_seconds` / `session_id`, with timeout sourced from scalar `execution_request.runtime_plan.host_timeout_seconds`.
- Existing `analyze()` and `checklist()` deterministic behavior is unchanged.
- Default `analyze` and `checklist` tests prove no LLM builder / Host call without explicit supported opt-in.
- Unsupported `checklist --use-llm` still fails before Service/Host if checklist LLM mode remains unsupported.
- Quality gate exceptions still propagate to CLI exit `2`.
- Missing provider config/construction still fails before Host execution.
- Incomplete LLM output still fails closed and does not print partial report.
- Safe diagnostics do not include prompt, draft, raw provider response, raw audit response, API key, Authorization header, model name or arbitrary provider body.
- Design/control sync status is recorded in implementation/review/closeout, with controller Option A or Option B resolved before accepted implementation.

Aggregate/deep review should check:

- No dependency changes adding dayu or provider SDK.
- No score/golden/quality gate/fixture/release-readiness drift.
- Docs describe current implementation only.

## Stop Conditions

Implementation worker must stop and return to controller if any condition occurs:

- Any design requires Host to inspect fund code, report year, report mode, chapter policy, Fund type, CHAPTER_CONTRACT, preferred_lens, ITEM_RULE or writer/auditor business semantics.
- Any design requires `extra_payload`, free dict payloads, `**kwargs` or untyped business parameter bags.
- Any design requires direct `dayu-agent`, `dayu.host` or `dayu.engine` production dependency.
- Any design requires Agent/tool-loop migration.
- Any design changes deterministic `analyze/checklist` behavior or exit codes.
- Any design touches score, quality gate semantics, golden fixtures, fixture promotion, release-readiness or PR external state.
- Validation shows missing-config `--use-llm` no longer fails before Host/service execution, or incomplete LLM result prints a partial report.
- Validation shows default `analyze` / `checklist` touches LLM request preparation or Host without explicit supported `--use-llm`.
- Accepted implementation is about to proceed without a recorded design/control sync status or controller defer decision.
- Worktree ownership becomes unclear due to unrelated dirty/untracked files in target files.

## Risks / Open Questions

Blocking questions: none.

Non-blocking risks:

- Existing `analyze_with_llm()` is already a public-ish Service method. Keeping it while adding `analyze_with_llm_execution()` creates two Service entry points. Working assumption: acceptable for this gate if CLI uses only the hardened typed path and tests cover both; a future cleanup gate may deprecate the lower-level method.
- `FundLLMExecutionContract` includes both normalized fund identity and explicit normalized `analysis_input`; this is deliberate to make the contract self-describing while preventing runtime policy leakage into the contract. Validation must fail on drift.
- Provider runtime budget continues to be derived from current provider timeout fields. This gate records and types the current semantics; it does not tune provider endpoint behavior.
- Docs/control truth-source sync is an exit decision, not an unowned residual. Before accepted implementation, controller must either append the docs/control sync slice or defer to a named artifact / owner / next gate in controller judgment.

## Completion Report Format

Implementation worker final report must use this format:

```text
Self-check: pass | blocked - <reason>
Gate: MVP Service ExecutionContract boundary hardening gate
Implemented slices: <slice ids>
Changed files:
- <path>
Validation:
- <command>: PASS | FAIL (<short reason>)
Docs:
- <updated docs or "not required">
Boundary assertions:
- Host business-agnostic: pass | blocked
- No extra_payload: pass | blocked
- Deterministic analyze/checklist unchanged: pass | blocked
Residual risks:
- <risk and owner/destination, or "none">
Blocking questions:
- <question, or "none">
```
