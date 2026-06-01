# MVP Service ExecutionContract boundary hardening plan controller judgment

Date: 2026-06-01
Gate: `MVP Service ExecutionContract boundary hardening gate`
Controller role: Gateflow controller
Decision: accepted plan checkpoint; do not enter implementation in this checkpoint

## Step Self-check

- Current gate / role: 当前仅完成 plan -> plan review -> fix -> re-review -> accepted plan checkpoint；controller 未实现代码。
- Source of truth: 依据用户启动要求、`AGENTS.md`、上一 accepted checkpoint `906d734 gateflow: accept internalized host runtime governance adapter`、fixed plan 与 review/re-review artifacts。
- Scope boundary: 本 checkpoint 只包含本 gate 的 plan/review/re-review/controller judgment artifacts；历史 untracked residual 保持未处理。
- Stop conditions: 当前 plan gate 无 blocking open question；implementation 前必须继续遵守 fixed plan，且 plan 明确要求 accepted implementation 前解决 design/control sync exit decision。
- Evidence and validation: 本 gate 是 plan-only，因此未运行代码测试；验证信号是独立 plan review finding 已修复并通过 re-review。
- Next action: 后续若继续本 gate，进入 implementation；不得进入下一个 gate、不得 push/PR/merge/mark ready。

## Preflight

- Branch: `codex/local-reconciliation`
- Initial status: `git status --short --untracked-files=all` 仅显示 untracked residual，无 tracked dirty 或 staged files。
- Historical untracked residuals: 未处理、未 stage，包括旧 `mvp-dayu-host-runtime-governance-adapter-implementation-preflight-20260601.md`；该旧 artifact 属于直接依赖 `dayu.host` 路线的 blocked preflight 证据，不作为当前路线依据。

## Plan Artifact

- Plan: `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md`
- Plan status after fix: handoff-ready / code-generation-ready.
- Scope: 收敛 `analyze --use-llm` 的 Service-owned `FundLLMExecutionContract` / typed request 边界；默认 deterministic `analyze/checklist`、score、quality gate semantics、golden/fixture、release/PR 状态和历史 residual 不进入本 gate。

## Review Results

- Boundary review: `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-review-boundary-20260601.md`
  - Verdict: not accepted; blocking findings present.
- Fast review: `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-review-fast-20260601.md`
  - Verdict: requires plan fix.
- Re-review: `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-rereview-20260601.md`
  - Verdict: accepted with no blocking findings.

## Accepted Findings And Fix Judgment

All blocking findings were accepted by controller and fixed in the plan artifact.

1. `ExecutionContract` too wide
   - Accepted because the original plan mixed Service runtime policies with a contract name that could be mistaken for Host-facing schema.
   - Fixed by narrowing `FundLLMExecutionContract` to stable business facts / declarations and moving `ChapterOrchestrationPolicy`, `FinalAssemblyPolicy`, provider budget, safe diagnostic policy and clients into Service-internal `FundLLMExecutionRequest` / `FundLLMRuntimePlan`.

2. Missing default non-LLM negative tests
   - Accepted because opt-in protection is a first-class boundary requirement.
   - Fixed by requiring tests that default `analyze` / `checklist` do not call LLM builder or Host, missing-config `--use-llm` fails before Host/Service execution, and unsupported `checklist --use-llm` fails before Service/Host execution.

3. Design/control sync decision unowned
   - Accepted because this is a heavy boundary-contract gate and truth-source drift cannot be left implicit.
   - Fixed by requiring an implementation-exit decision: either a dedicated docs/control sync slice, or controller judgment that defers sync to a named artifact, owner and next gate before accepted implementation.

## Controller Acceptance

The plan is accepted for implementation handoff. The implementation agent must follow the fixed plan literally:

- Host API remains generic: `operation_name`, `operation`, `timeout_seconds`, `session_id`.
- Host must not receive or inspect fund type, CHAPTER_CONTRACT, preferred_lens, ITEM_RULE, year-report parsing, writer/auditor business judgment, chapter policy or final assembly policy.
- CLI-hosted `--use-llm` may use only the Service-prepared typed execution request and scalar `runtime_plan.host_timeout_seconds` for Host deadline.
- Explicit parameters must remain typed fields; no `extra_payload`, free business dict, `Mapping[str, Any]` bag or `**kwargs` escape hatch.
- No `dayu-agent`, `dayu.host` or `dayu.engine` production dependency may be introduced.
- Default deterministic `analyze/checklist` behavior must remain unchanged.

## Validation Status

- Plan review loop: PASS.
- Code tests: not run; no production code changed in this plan checkpoint.
- Docs/control sync: not yet applicable to plan-only checkpoint. The fixed plan requires implementation acceptance to record one of the explicit statuses: synced in docs/control slice, deferred by controller judgment to named owner/artifact/next gate, or not required because code facts unchanged.

## Accepted Checkpoint Scope

Only the following current-gate artifacts are eligible for staging in this checkpoint:

- `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-review-boundary-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-review-fast-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-rereview-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-controller-judgment-20260601.md`

Do not stage historical residual artifacts.
