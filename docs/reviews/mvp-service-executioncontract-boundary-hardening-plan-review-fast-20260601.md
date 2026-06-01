## Findings

### 001-未修复-高-blocking-`ExecutionContract` 混入 Service-only 章节与总装策略，边界语义自相矛盾
- **Severity**: 高
- **Blocking / non-blocking**: blocking
- **Evidence**:
  - Plan 在 `New Service-owned ExecutionContract` 中把 `chapter_policy: ChapterOrchestrationPolicy` 和 `assembly_policy: FinalAssemblyPolicy` 列为 `FundLLMExecutionContract` required fields（`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:95-107`）。
  - 同一 plan 又在 `Field Placement Decisions` 中声明 `Prompt/chapter orchestration intent for template chapters 1-6` 和 `Final assembly policy for template chapters 0/7 and complete report` 必须留在 Service（`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:248-256`）。
  - Plan 还声明 Host 不能 inspect `chapter_policy` / `assembly_policy`（`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:218-226`），但 Slice 3 要 CLI 取得 `FundLLMExecutionRequest` 并把 `execution_request.contract.provider_runtime_budget.host_timeout_seconds` 用作 Host timeout（`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:375-408`）。这让同一个 `contract` 同时承担 Host-facing deadline carrier 与 Service-internal orchestration policy carrier。
  - 当前代码事实中 Host `run_sync()` 只接受 `operation_name`、`operation`、`timeout_seconds`、`session_id`，且 docstring 明确 `operation_name` 只用于安全诊断、不承载业务语义（`fund_agent/host/runtime.py:409-423`）。当前 Service `analyze_with_llm()` 的 `chapter_policy` / `assembly_policy` 是 Service 方法参数，用于构造章节编排输入和最终总装输入（`fund_agent/services/fund_analysis_service.py:587-645`）。AGENTS 要求 Host 不负责 prompt 业务语义或报告判断，Service 负责 prompt / ExecutionContract 组装和质量策略选择（`AGENTS.md:103-113`）。
- **Why this blocks handoff**: Implementation agent 按当前 plan 直接实现时，无法判断 `ExecutionContract` 是 Host-facing contract、Service internal request，还是 CLI 持有的 prepared execution object。该混合会把 Service-only policy 固化进一个被 CLI/Host path 携带和测试的 contract，后续很容易诱导 Host/CLI 断言或分支处理章节/总装语义，正好违背本 gate 的边界硬化目标。
- **Recommendation**:
  - Plan fix 必须先拆清三个对象的边界：
    - Host-facing 只允许通用 lifecycle/deadline/session/safe diagnostic 字段，或只从 prepared request 暴露 `host_timeout_seconds` 标量；Host 不接收、命名或测试基金章节/总装 policy。
    - Service internal orchestration/final assembly policy 留在 Service helper 或 Service-owned prepared request 内部，不放入名为 `ExecutionContract` 的 Host-facing schema。
    - Runtime capabilities（`ChapterOrchestratorLLMClients`）继续不进入 schema contract。
  - 若保留 `FundLLMExecutionContract` 名称，plan 必须明确它是 Service-internal contract，且 CLI/Host 只能把整个 prepared request 作为 opaque operation capture 使用；tests 不应把 `chapter_policy` / `assembly_policy` 作为 Host boundary contract 字段。
  - 更新 Slice 1-3 的 required fields、tests 和 boundary assertions，确保 `chapter_policy` / `assembly_policy` 不再出现在 Host-facing contract field list 中，或改名为明确的 Service-internal prepared execution structure。

## Reviewed Target And Scope

- Review target: `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md`
- Review role: Gateflow-governed plan review specialist, not controller.
- Scope: plan only; no production code implementation, no commit, no push, no PR.
- Required source facts read: `AGENTS.md`; plan artifact; `fund_agent/ui/cli.py` `_build_llm_clients_or_fail()` / `_run_llm_analysis_in_host()`; `fund_agent/services/fund_analysis_service.py` `FundAnalysisRequest` / `analyze_with_llm()`; `fund_agent/host/runtime.py` `HostRuntimeRunner.run_sync()`.

## Coverage Notes

- User-required plan coverage is mostly present: goal/non-goals, affected files, slices, tests, docs decision, validation matrix and stop conditions are explicit.
- `extra_payload` prohibition is implementable and testable as planned: type-shape restrictions, runtime validation and static/signature tests are specified.
- Dayu runtime dependency, Agent/tool-loop migration, deterministic analyze/checklist behavior, score/golden/fixture/release/PR external state are explicitly out of scope with matching stop conditions.
- Allowed files and docs are clear. The plan correctly avoids root README unless user-visible CLI behavior changes and confines Host changes to boundary regression tests/docs.

## Open Questions

- None beyond the blocking contract-boundary fix above.

## Residual Risks

- After fixing finding 001, code review should still verify that tests assert Host remains business-agnostic by dependency/import boundary and by absence of Host branching on fund, chapter, quality or assembly semantics.

## Verdict

requires plan fix
