# Aggregate Deepreview: MVP Service ExecutionContract Boundary Hardening

## Scope

- Mode: current changes (aggregate gate review)
- Branch: codex/local-reconciliation
- Base: main
- Output file: docs/reviews/mvp-service-executioncontract-boundary-hardening-aggregate-deepreview-20260601.md
- Included scope: 5 gate commits (dc5fe87 plan, 4691da5 slice 1, 854d4b8 slice 2, 19b08cf slice 3, 72c3a33 slice 4), covering production source + tests in:
  - `fund_agent/services/execution_contract.py` (new)
  - `fund_agent/services/fund_analysis_service.py` (LLM path additions)
  - `fund_agent/services/llm_provider.py` (pre-existing, read for boundary checks)
  - `fund_agent/config/llm.py` (pre-existing, read for boundary checks)
  - `fund_agent/host/__init__.py`, `fund_agent/host/runtime.py` (pre-existing, read for boundary checks)
  - `fund_agent/ui/cli.py` (LLM path integration)
  - `tests/services/test_execution_contract.py` (new)
  - `tests/services/test_fund_analysis_service_llm.py` (LLM path tests)
  - `tests/host/test_runtime_runner.py` (Host boundary assertions)
  - `tests/ui/test_cli.py` (CLI integration tests)
- Excluded scope: docs/reviews/ subdirectory (review artifacts are inputs, not review targets); pre-existing provider/config code before this gate (reviewed for boundary violations only)
- Parallel review coverage: 无 (single reviewer, full trace)

## Pre-existing Review Artifacts Considered

- `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice1-code-review-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice1-code-rereview-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice2-code-review-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice3-code-review-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice4-code-review-20260601.md`
- Slice implementation evidence artifacts and controller judgments

## Focus Check Results

Each of the 10 focus checks is verified below against direct code evidence.

### 1. Service-owned ExecutionContract / FundLLMExecutionRequest boundary coherent across slices

**PASS.** `FundLLMExecutionContract` (`execution_contract.py:305-356`) carries only business facts: `fund_code`, `report_year`, `analysis_input`, `quality_policy`, `schema_version`, `report_mode`, `llm_opt_in_mode`. `FundLLMRuntimePlan` (`execution_contract.py:267-302`) separately carries Service-internal concerns: `chapter_policy`, `assembly_policy`, `provider_runtime_budget`, `quality_fail_closed_policy`, `safe_diagnostic_policy`, `host_timeout_seconds`. `FundLLMExecutionRequest` (`execution_contract.py:359-370`) combines contract + runtime_plan + llm_clients. Test `test_execution_contract_fields_exclude_runtime_and_host_fields` (`test_execution_contract.py:265-304`) explicitly verifies contract fields don't leak runtime-only or Host lifecycle fields. Test `test_execution_request_may_contain_runtime_plan_but_contract_does_not` (`test_execution_contract.py:307-338`) verifies runtime plan fields stay out of the contract. The boundary is clean across all 4 slices.

### 2. Host remains business-agnostic, does not import Service/Fund

**PASS.** `host/runtime.py` explicitly states (line 3-5): "本模块只承载通用运行生命周期、取消、deadline、终态和安全诊断契约。它不理解基金业务，不导入 Service / Fund，也不依赖外部 Dayu runtime。" Test `test_host_package_does_not_import_service_or_fund_layers` (`test_runtime_runner.py:22-38`) greps all Host source for `fund_agent.services` and `fund_agent.fund`. Test `test_host_runner_source_has_no_fund_business_semantics` (`test_runtime_runner.py:41-81`) greps for 17 forbidden business terms including `FundLLMExecutionContract`, `fund_code`, `report_year`, `chapter_policy`, `extra_payload`. The only business-related token Host receives is `host_timeout_seconds` — a bare integer lifetime scalar exposed by the runtime plan, not a business field.

### 3. CLI bridges Service typed request to Host generic lifecycle; default deterministic unchanged

**PASS.** The `analyze` command (`cli.py:74-280`) has two paths: default `analyze()` (unchanged deterministic, line 258) and `--use-llm` (line 244-256). The `--use-llm` path: (a) constructs `FundLLMExecutionRequest` via `build_fund_llm_execution_request` (line 245), (b) passes to `_run_llm_analysis_in_host` which wraps Service call in a Host runner (line 246), (c) Host only sees `operation_name`, `operation` callable, and `timeout_seconds` scalar (line 862-866). The `checklist` command (`cli.py:283-358`) is unchanged. No business parameters cross into Host API.

### 4. --use-llm fail-closed behavior intact

**PASS.** Four fail-closed layers are verified:

a) **Missing config**: `load_llm_provider_config_from_env()` raises `LLMProviderConfigError` on missing `FUND_AGENT_LLM_PROVIDER`/`MODEL`/`BASE_URL`/`API_KEY` (`config/llm.py:79-134`). CLI catches it at line 259-261, exits code=1.

b) **Construction failure**: `build_chapter_llm_clients()` raises `LLMProviderConstructionError` (`llm_provider.py:422-441`). CLI catches at line 262-264, exits code=1. Both failures happen before Host run.

c) **Incomplete result**: CLI operation closure (`cli.py:838-860`) checks `result.final_assembly_result.report_markdown is None` and raises `_LLMIncompleteHostRunError`, causing Host to return FAILED. CLI exit code=1.

d) **Quality gate block/not-run**: `_run_analysis_core()` raises `QualityGateBlockedError`/`QualityGateNotRunBlockedError` before orchestration (`fund_analysis_service.py:816-820`). These propagate through Host and are re-raised by CLI (line 867-868). CLI exits code=2.

e) **Host terminal failure**: CLI checks `host_result.status != HostRunStatus.SUCCEEDED` at line 247, exits code=1. No fallback to deterministic renderer.

Tests confirm: `test_build_fund_llm_execution_request_raises_config_error_before_host_run`, `test_build_fund_llm_execution_request_raises_construction_error_before_host_run`, `test_missing_writer_or_auditor_blocks_without_deterministic_fallback`, `test_analyze_with_llm_propagates_quality_gate_block_before_orchestration` (and `_execution` variants).

### 5. No explicit business parameters through extra_payload bags

**PASS.** Test `test_new_dataclasses_and_public_signatures_exclude_open_business_bags` (`test_execution_contract.py:341-378`) verifies all 11 public objects have no `extra_payload`, `kwargs`, `payload`, `metadata`, `context` fields or `**kwargs` parameters, and no `dict[str, Any]`/`Mapping[str, Any]` open business bag annotations. Test `test_open_business_bag_guard_detects_future_annotation_strings` (`test_execution_contract.py:381-405`) guards against `from __future__ import annotations` string escapes. The only mentions of "extra_payload" in production code are docstring declarations that it is not used (`fund_analysis_service.py:519,573,617`).

### 6. No dayu-agent production runtime dependency

**PASS.** The only occurrences of "dayu" / "Dayu" in production source are docstring/comment declarations of independence:
- `host/runtime.py:4`: "也不依赖外部 Dayu runtime"
- `config/llm.py:4`: "不接入 Service、Host、Agent/dayu"
- `llm_provider.py:6`: "Agent/dayu，也不引入 vendor SDK"

No `import dayu` or `from dayu` in any production file. `pyproject.toml` has no dayu dependency.

### 7. No scope drift

**PASS.** The 8 production Python files changed are within scope boundaries:
- `execution_contract.py`: Service-owned typed contract types
- `fund_analysis_service.py`: LLM execution request construction + `analyze_with_llm_execution` entry point
- `cli.py`: Bridge from CLI to Host runner
- `services/__init__.py`: Re-exports

No changes to: Agent engine/tool-loop, provider runtime implementation, score, quality gate semantics, golden, fixture promotion, release-readiness, PR state.

### 8. Docs describe current implementation, keep future-only items clearly marked

**PASS.** `docs/design.md` clearly distinguishes:
- "当前已实现" (currently implemented) for the Host runtime governance adapter
- "尚无 Agent runner/tool-loop、async Host runner、durable session/resume/memory/reply outbox 或 dayu runtime" (line 6)
- "已接受的未来设计" (accepted future design) section for Route C gates not yet implemented
- "后续 Host scope" / "后续迁移" markers for async/durable/session/resume/outbox/Agent engine

`docs/implementation-control.md` line 9: "async Host runner、durable session/resume/memory/outbox、Agent engine/tool-loop migration 保留为后续 gate"

### 9. Tests cover positive typed path and negative boundary/fail-closed

**PASS.** Coverage summary:
- Positive typed path: `test_valid_contract_from_normalized_fund_analysis_request`, `test_analyze_with_llm_returns_accepted_final_assembly_and_report_markdown`, `test_build_fund_llm_execution_request_prepares_contract_and_runtime_plan`, `test_analyze_with_llm_execution_matches_existing_llm_path`, `test_host_runner_records_llm_service_phase_events`
- Negative boundary: `test_contract_rejects_identity_or_report_year_mismatch`, `test_contract_rejects_invalid_report_mode_or_opt_in_mode`, `test_quality_policy_rejects_deterministic_fallback_allowed`, `test_provider_runtime_budget_rejects_zero_or_negative_timeout_or_attempts`, `test_runtime_plan_rejects_nonpositive_host_timeout`, `test_runtime_plan_rejects_invalid_target_chapter_ids`
- Fail-closed: `test_build_fund_llm_execution_request_raises_config_error_before_host_run`, `test_build_fund_llm_execution_request_raises_construction_error_before_host_run`, `test_missing_writer_or_auditor_blocks_without_deterministic_fallback`, `test_analyze_with_llm_propagates_quality_gate_block_before_orchestration` × 2 (direct + execution), `test_analyze_with_llm_propagates_quality_gate_not_run_before_extraction` × 2
- Deterministic isolation: `test_deterministic_analyze_does_not_call_llm_orchestrator_path`, `test_deterministic_checklist_does_not_call_llm_orchestrator_path`
- Boundary guards: `test_host_package_does_not_import_service_or_fund_layers`, `test_host_runner_source_has_no_fund_business_semantics`, `test_fund_analysis_service_imports_keep_llm_path_above_forbidden_boundaries`

No tests use live provider credentials.

### 10. Residual risks have owners/destinations

**PASS.** `docs/implementation-control.md` Startup Packet (line 9) lists open residuals with owners:
- "provider_runtime_timeout_small_prompt" → next gate
- "async Host runner、durable session/resume/memory/outbox、Agent engine/tool-loop migration" → 后续 gate
- "chapter 0/7 LLM polish/audit、Evidence Confirm、live smoke" → future Route C gates

## Findings

### 1-未修复-中-QualityFailClosedPolicy 构造后未被运行时消费

- **入口/函数**: `build_fund_llm_execution_request()` → `analyze_with_llm_execution()` → `analyze_with_llm()`
- **文件(行号)**: `fund_agent/services/fund_analysis_service.py:950-957`（构造）, `:705-713`（未传递）, `:602-675`（未读取）
- **输入场景**: 任何通过 `build_fund_llm_execution_request()` 或直接构造 `FundLLMExecutionRequest` 发起的 LLM 执行。直接构造时若传入与默认值不同的 `QualityFailClosedPolicy` 字段值（如 `fail_on_partial_orchestration=False`），不会被运行时消费。
- **实际分支**: `analyze_with_llm_execution()` 只从 `execution_request.runtime_plan` 提取 `chapter_policy` 和 `assembly_policy` 传给 `analyze_with_llm()`；`quality_fail_closed_policy` 从未被读取。
- **预期行为**: 若 `QualityFailClosedPolicy` 是运行时策略声明，则 `analyze_with_llm()` 或 `analyze_with_llm_execution()` 应在决策点读取对应字段（如 `fail_on_partial_orchestration`）并据此决定是否将 `blocked`/`incomplete` 状态视为 fail-closed；若它只是声明性文档，则不应以可配置 dataclass 形式暴露且接受任意构造值。
- **实际行为**: 当前 fail-closed 行为由硬编码逻辑强制：`_run_analysis_core` 总是对 block/not-run 抛异常，`orchestrate_chapters` 总是对缺 auditor 返回 blocked，`assemble_final_chapters` 总是对缺章节返回 incomplete，CLI 总是对非 SUCCEEDED 终态 exit(1)。这些行为恰好匹配 `QualityFailClosedPolicy` 的所有 `True` 默认值，但不受策略对象驱动。若未来有人将任何 `fail_on_*` 设为 `False`，代码不会响应。
- **直接证据**: `fund_agent/services/fund_analysis_service.py:705-713` 调用链中完全不出现 `execution_request.runtime_plan.quality_fail_closed_policy`；grep 确认该属性在 `execution_contract.py` 之外只在构造处（`:950-957`）和 `FundLLMRuntimePlan` 字段声明（`:282`）出现。
- **影响**: 中等 — 当前行为正确，但存在两个风险：(a) 策略对象给人以可配置的假象，直接构造 `FundLLMExecutionRequest` 时若修改策略值会被静默忽略；(b) 未来若将决策权交给策略对象而忘记同步硬编码逻辑，可能引入策略与实际行为不一致的回归。
- **建议改法和验证点**: 两个方向择一：(a) 将 `QualityFailClosedPolicy` 从 `FundLLMRuntimePlan` 中移除，fail-closed 语义保留为硬编码（需同步删除 `execution_contract.py` 中的类型引用和测试导入）；(b) 在 `analyze_with_llm()` 中实际读取 `quality_fail_closed_policy` 字段并在决策点使用。验证点：构造不同策略值的 `FundLLMExecutionRequest` 并断言行为随之改变（选择 b）或确认策略已移除（选择 a）。
- **修复风险（低/中/高）**: 低 — 改动范围小，只涉及移除未使用字段或添加读取逻辑。
- **严重程度（低/中/高/严重）**: 中

### 2-未修复-低-QualityGatePolicy Literal 类型在 execution_contract 和 fund_analysis_service 中独立定义

- **入口/函数**: 模块级类型别名
- **文件(行号)**: `fund_agent/services/execution_contract.py:31` 和 `fund_agent/services/fund_analysis_service.py:88`
- **输入场景**: 任一模块需要修改 `QualityGatePolicy` 允许值（如增加 `"strict"` 策略）时。
- **实际分支**: `execution_contract.py` 中 `QualityPolicyDeclaration.quality_gate_policy` 使用本地定义；`fund_analysis_service.py` 中 `FundAnalysisDeveloperOverrides.quality_gate_policy` 和 `ResolvedAnalyzeContract.quality_gate_policy` 使用本地定义。
- **预期行为**: 应只有一个 `QualityGatePolicy` 真源。考虑到 `QualityPolicyDeclaration` 是 Service-owned 业务质量声明且已在 `execution_contract.py` 中定义，该类型应统一从 `execution_contract` 导入。
- **实际行为**: 两个独立定义当前值相同（`Literal["off", "warn", "block"]`），但不存在编译时或静态检查保证它们保持同步。
- **直接证据**: `execution_contract.py:31`: `QualityGatePolicy = Literal["off", "warn", "block"]`；`fund_analysis_service.py:88`: `QualityGatePolicy = Literal["off", "warn", "block"]`。两处均为独立赋值，无 import 关系。
- **影响**: 低 — 当前值一致且不太可能独立变更，但若有人只改一处，类型检查器不会跨模块报告不一致，因为它们是不同的类型别名。
- **建议改法和验证点**: 将 `fund_analysis_service.py` 的 `QualityGatePolicy` 替换为 `from fund_agent.services.execution_contract import QualityGatePolicy`。注意 `execution_contract.py` 当前在 TYPE_CHECKING 下从 `fund_analysis_service` 导入类型，需要确认这不引入运行时循环导入。
- **修复风险（低/中/高）**: 低 — 单行 import 替换。
- **严重程度（低/中/高/严重）**: 低

## Open Questions

1. **repair_timeout_fallback_used 信息丢失**: `LLMProviderConfig.repair_timeout_fallback_used`（`config/llm.py:73`）记录 repair timeout 是否回退到 writer timeout，但 `build_fund_llm_execution_request()` 在构造 `ProviderRuntimeBudget` 时未将此标志传入（`fund_analysis_service.py:941-948`）。Provider 层的 runtime diagnostic 仍可从原始 config 读取该标志（`llm_provider.py:717`），但 runtime plan 自身丢失了此信息。如果后续需要从 runtime plan 审计 timeout 配置完整性，此信息不可得。是否需要由 `ProviderRuntimeBudget` 携带此标志？

2. **execution_contract ↔ fund_analysis_service 的 TYPE_CHECKING 循环**: `execution_contract.py` 在 TYPE_CHECKING 下从 `fund_analysis_service` 导入 `FundAnalysisDeveloperOverrides` 和 `FundAnalysisRequest`（`:17-25`），而 `fund_analysis_service.py` 在运行时从 `execution_contract` 导入（`:71-82`）。当前因 TYPE_CHECKING 保护没有运行时循环导入，但如果将 `QualityGatePolicy` 统一到 `execution_contract`（参见 Finding 2），需要确认 `fund_analysis_service.py` 中的运行时 `QualityGatePolicy` 类型引用不会创建新的循环路径。

## Residual Risk

1. **无真实 provider 端到端集成测试**: 所有 LLM 路径测试使用 fake writer/auditor clients。Provider construction、HTTP 调用、timeout/retry、malformed response 处理仅在 `llm_provider.py` 单元层面可测（通过 `httpx.MockTransport`），但 Service → Provider → Host 的完整链路未在测试中覆盖真实 HTTP。已知 controller 在 real-provider smoke acceptance 中观察到 `provider_runtime_timeout_small_prompt` blocker；该 blocker 与本次 gate 的 boundary hardening 范围不矛盾，但意味着 fail-closed timeout/retry 行为尚未在真实 provider 条件下验证。

2. **CLI asyncio.run() bridge**: CLI 的 `_run_llm_analysis_in_host` (`cli.py:838-860`) 在 Host runner 的同步 operation closure 内使用 `asyncio.run()` 桥接 async Service API。Host runner 设计为同步（`host/runtime.py:402-407` 明确声明 "不管理 asyncio event loop"）。这在当前使用场景下可工作（每个 Host run 只调用一个 Service operation），但如果未来需要 Host 管理多个并发操作或长生命周期 event loop，需要重新设计。这已记录为设计约束（`docs/design.md:55-56`），不是本次 gate 的 regression。

3. **章节级 fail-closed 未区分 per-chapter 策略**: 当前 `QualityFailClosedPolicy.fail_on_partial_orchestration` 是全局布尔值，但 `ChapterOrchestrationPolicy` 的 `fail_fast` 标志（`chapter_orchestrator.py`）控制的是编排器内部行为，这两个概念未在运行时对齐。如果未来需要 per-chapter 差异化 fail-closed（如第 1 章失败时允许继续第 2-6 章），需要在 orchestration policy 和 fail-closed policy 之间建立显式关系。

---

## Verdict

**未发现阻塞性缺陷。** 10 项 focus check 全部 PASS。2 项 finding 均为非阻塞：一项中等（`QualityFailClosedPolicy` 未消费）、一项低（重复类型定义）。3 项 residual risk 均可追溯到已知 design constraint 或已有 owner。当前 aggregate 实现边界清晰、fail-closed 语义完整、Host 业务无关性坚实、测试覆盖正面路径和负面边界。
