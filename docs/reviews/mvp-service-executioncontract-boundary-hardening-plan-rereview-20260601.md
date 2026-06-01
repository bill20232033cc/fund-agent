# MVP Service ExecutionContract boundary hardening plan re-review

## Findings

No blocking findings remain.

Plan re-review verdict: accepted with no blocking findings

## Reviewed Target And Scope

- Reviewed fixed plan: `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md`
- Original review artifacts:
  - `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-review-boundary-20260601.md`
  - `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-review-fast-20260601.md`
- Reviewer role: Gateflow-governed plan re-review specialist, not controller.
- Scope: re-review only; no production code implementation, no commit, no push, no PR.
- Source rules read: `AGENTS.md`.

## Accepted Finding Status

### boundary-001 / fast-001: ExecutionContract too wide

Status: fixed.

Evidence:

- Fixed plan narrows `FundLLMExecutionContract` required fields to stable business facts and declarations: `schema_version`, `fund_code`, `report_year`, `report_mode`, `llm_opt_in_mode`, `analysis_input`, and `quality_policy` (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:96`).
- Fixed plan explicitly forbids `ChapterOrchestrationPolicy`, `FinalAssemblyPolicy`, `ProviderRuntimeBudget`, `SafeDiagnosticPolicy`, `ChapterOrchestratorLLMClients`, Host lifecycle fields, safe diagnostic display toggles, and provider/runtime clients from the contract (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:114`).
- Runtime-only fields are moved to Service-internal `FundLLMRuntimePlan` and `FundLLMExecutionRequest`, including `chapter_policy`, `assembly_policy`, provider runtime budget, quality fail-closed policy, safe diagnostic policy, scalar `host_timeout_seconds`, and `llm_clients` (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:121`, `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:166`, `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:177`).
- Fixed plan states these runtime objects are Service-internal and are not Host-facing contract schema (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:133`).
- Slice 1 tests require dataclass field assertions proving `FundLLMExecutionContract` excludes runtime-only and Host lifecycle fields (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:330`, `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:340`).

### boundary-002: Default non-LLM negative tests missing

Status: fixed.

Evidence:

- Slice 3 now requires default `analyze` negative boundary tests that monkeypatch the CLI-visible Service builder and `HostRuntimeRunner.run_sync` to raising fakes, then assert deterministic `analyze()` is called while builder, Host, and `analyze_with_llm_execution()` are not called (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:459`).
- Slice 3 now requires equivalent `checklist` negative boundary tests proving no LLM builder, Host, or LLM Service execution occurs without supported opt-in (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:460`).
- Slice 3 now requires unsupported `checklist --use-llm` to fail through Typer parsing/usage before deterministic Service, LLM builder, Host, or LLM Service execution (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:461`).
- Missing-config / construction-error tests now must prove exit `1`, stdout empty, no Host run, no deterministic fallback, no deterministic `analyze()`, and no `analyze_with_llm_execution()` (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:462`).
- Validation matrix and failure paths repeat these negative assertions as required gate evidence (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:545`, `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:560`).

### boundary-003: docs/design and control sync left unowned

Status: fixed.

Evidence:

- Fixed plan keeps `docs/design.md` and `docs/implementation-control.md` outside ordinary implementation slices unless controller authorizes a dedicated docs/control sync slice or records an explicit deferred owner/artifact/next gate (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:84`).
- Docs Decision now requires a gate exit decision before accepted implementation: Option A is a dedicated docs/control sync slice; Option B is controller judgment deferring truth-source sync to a named artifact, owner, and next gate (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:579`).
- The plan recommends Option A if code facts change to `CLI -> Service builds FundLLMExecutionRequest / FundLLMRuntimePlan -> Host runner uses scalar timeout -> Service executes LLM report`, and forbids describing Agent/tool-loop migration or old Dayu runtime as implemented (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:582`).
- Validation, review artifacts, and closeout must record `design/control sync status` as one of three explicit statuses (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:583`).
- Stop conditions now block accepted implementation if design/control sync status or controller defer decision is missing (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:631`).

## User Requirements / Non-goals Check

- Original user plan goal is still preserved: the fixed plan hardens the Service ExecutionContract boundary for explicit `analyze --use-llm` without changing default deterministic `analyze/checklist` behavior.
- Host remains generic: fixed plan says Host `run_sync()` only receives `operation_name`, `operation`, `timeout_seconds`, and `session_id`; the timeout is sourced from scalar `execution_request.runtime_plan.host_timeout_seconds` (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:227`, `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:234`).
- Forbidden scope remains excluded: no Agent/tool-loop migration, no Dayu production dependency, no score / quality gate semantic drift, no golden/fixture/release/PR state changes, and no `extra_payload` / `**kwargs` escape hatch (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:36`, `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:285`, `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:619`).

## Open Questions

None requiring controller or user input for plan handoff.

## Residual Risks

- Keeping both `analyze_with_llm()` and `analyze_with_llm_execution()` remains a non-blocking future cleanup risk, already recorded with an acceptable working assumption in the fixed plan (`docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md:640`).
- Code review should still verify implementation follows the fixed field placement literally, especially that CLI cannot call the lower-level `analyze_with_llm()` path and Host never receives business fields as API arguments.

## Reviewer Self-check

- Current gate / role: re-review specialist only; no controller actions taken.
- Source of truth: read `AGENTS.md`, fixed plan, and both original review artifacts.
- Scope boundary: wrote only this re-review artifact; no production code, commit, push, PR, or implementation.
- Evidence and validation: re-review conclusion is based on fixed plan line evidence against all accepted blocking findings.

