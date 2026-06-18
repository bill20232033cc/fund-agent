# MVP typed template contract Slice 7 Service Facade Wiring Implementation Evidence

## Gate

- Gate: `MVP typed template contract Slice 7 Service Facade Wiring Behind Explicit Typed Path implementation gate`
- Role: AgentCodex implementation worker only
- Baseline checkpoint: Slice 6 `1ec22e0`
- Scope classification: heavy

## Touched Files

- `fund_agent/services/execution_contract.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/chapter_orchestrator.py`
- `tests/services/test_execution_contract.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/ui/test_cli.py`
- `docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-implementation-evidence-20260603.md`

No files outside the allowed implementation/test/evidence scope were modified.

## Behavior Summary

- Added explicit `typed_template_path` typed fields to Service-owned LLM execution request/runtime plan and chapter orchestration policy.
- `typed_template_path` is a closed enum: `legacy_contract` / `typed_template_contract`.
- `FundLLMRuntimePlan` now validates that its typed path matches `ChapterOrchestrationPolicy.typed_template_path`.
- `FundLLMExecutionRequest` now validates that its typed path matches the runtime plan.
- `build_fund_llm_execution_request()` selects `typed_template_contract` only for the explicit `--use-llm` execution request path.
- `ChapterOrchestrator` remains a Service-owned transition facade. When explicitly on typed path, it derives same-source `EvidenceAvailability` from `ChapterFactProjection` and passes:
  - `EvidenceAvailability` into writer/auditor input,
  - typed per-chapter contract into auditor input for bounded semantic `audit_focus`.
- Independent body chapter execution is preserved: a failed body chapter does not skip unrelated body chapters, and `dependency_missing` remains reserved for true writer dependency stop reasons.

## Validation Result

- `uv run pytest tests/services/test_execution_contract.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py`
  - Passed: `177 passed`
- `uv run ruff check fund_agent/services tests/services tests/ui`
  - Passed
- `git diff --check`
  - Passed

## Acceptance Criteria Mapping

- Explicit typed fields: satisfied by `typed_template_path` on `FundLLMExecutionRequest`, `FundLLMRuntimePlan`, and `ChapterOrchestrationPolicy`.
- No free business bag: tests guard against `extra_payload`, `kwargs`, `payload`, `metadata`, `context`, and `dict[str, Any]` / `Mapping[str, Any]` bags on the touched public Service types/signatures.
- Service-owned transition facade: `ChapterOrchestrator` consumes typed inputs while remaining in `fund_agent/services`; no Host/Agent runtime migration was introduced.
- Default deterministic `analyze`: regression test confirms default CLI analyze does not build LLM execution request, invoke Host, call LLM Service path, or write LLM incomplete artifacts.
- `checklist`: existing CLI test continues to reject `--use-llm`; deterministic checklist behavior unchanged.
- `--use-llm` opt-in fail-closed: existing incomplete-result and Host fail-closed CLI tests continue to pass.
- Host business-field opacity: no Host files were touched; Host still receives only generic operation/deadline/session runtime inputs from the existing CLI path.

## Non-Goals Preserved

- Did not change deterministic `fund-analysis analyze`.
- Did not change deterministic `fund-analysis checklist`.
- Did not change provider construction defaults, timeout budgets, clients, live probe behavior, endpoint selection, runtime ceilings, score/golden/readiness/template truth, or quality gate semantics.
- Did not add or modify Host business fields.
- Did not implement Agent runtime, tool loop, ToolRegistry, ToolTrace, dayu runtime, or provider live smoke.
- Did not update control documents or open a new gate.

## Residual Risks

- Service Slice 7 wires typed availability and audit focus through the allowed Service facade. It does not modify Fund-layer auditor marker semantics or broaden typed required-output marker behavior because Fund files were outside this worker's allowed file list.
- Ch3 can still fail closed under typed availability when same-source evidence is insufficient; this is expected typed programmatic behavior, not deterministic fallback.
