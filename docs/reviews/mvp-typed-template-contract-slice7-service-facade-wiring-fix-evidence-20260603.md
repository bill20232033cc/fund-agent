# MVP typed template contract Slice 7 Service Facade Wiring Fix Evidence

## Gate

- Gate: `MVP typed template contract Slice 7 Service Facade Wiring Behind Explicit Typed Path implementation gate`
- Follow-up: review blocking finding fix
- Role: AgentCodex implementation worker only

## Accepted Findings Fixed

- Blocking finding fixed: Service facade typed path did not pass `TypedChapterContract.required_output_items` into writer, so Slice 3 `RequiredOutputItem.when_evidence_missing` behavior was not activated through the Service facade.

## Changed Files

- `fund_agent/services/chapter_orchestrator.py`
- `tests/services/test_chapter_orchestrator.py`
- `docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-fix-evidence-20260603.md`

No Fund writer/auditor semantics, provider/default/runtime/live probe, Host, Agent runtime/tool-loop, or control documents were modified.

## Behavior Summary

- Added Service orchestrator helper `_typed_required_output_items()` that reads `get_typed_chapter_contract(chapter_id).required_output_items` only when typed path inputs are active.
- Initial `build_chapter_writer_input()` now receives `typed_required_output_items` on `typed_template_contract` path.
- Repair `build_chapter_writer_input()` now receives the same typed required output items, preserving typed behavior across regenerate attempts.
- Legacy path still returns an empty tuple and keeps typed required-output behavior inactive.
- Existing independent body chapter execution remains unchanged: one body chapter failure does not skip unrelated body chapters.

## Tests Added/Updated

- `test_typed_contract_path_preserves_independent_body_execution`
  - Verifies Service typed path derives `EvidenceAvailability`.
  - Verifies writer prompt has typed required output plan and stable typed item ids.
  - Verifies Ch3 missing evidence activates `render_evidence_gap` through the Service facade.
  - Verifies later body chapters still execute after Ch1 timeout.
- `test_typed_contract_path_repair_keeps_typed_required_output_items`
  - Verifies repair attempt writer input retains typed required output items and typed evidence plan.

## Validation

- `uv run pytest tests/services/test_execution_contract.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py`
  - Passed: `178 passed`
- `uv run ruff check fund_agent/services tests/services tests/ui`
  - Passed
- `git diff --check`
  - Passed

## Non-Goals Preserved

- Did not change Fund-layer writer/auditor semantics.
- Did not change provider construction, provider defaults, runtime budgets, live probe, score/golden/readiness/template truth, or quality gate behavior.
- Did not change deterministic `fund-analysis analyze` or `fund-analysis checklist`.
- Did not add Host business fields or modify Host lifecycle behavior.
- Did not implement Agent runtime, tool loop, ToolRegistry, ToolTrace, or dayu runtime.
- Did not commit, push, update control documents, or open a new gate.
