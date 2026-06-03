# MVP typed template contract Slice 7 Service Facade Wiring controller judgment

## Controller Self-Check

- Role: controller; implementation, fix, review and re-review were delegated to workers.
- Gate: `MVP typed template contract Slice 7 Service Facade Wiring Behind Explicit Typed Path implementation gate`.
- Classification: `heavy`.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Source of truth: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, and Slice 7 in `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`.
- Scope boundary: Service-owned typed path wiring in `execution_contract.py`, `fund_analysis_service.py`, `chapter_orchestrator.py`, focused Service/UI tests, and Slice 7 evidence/review artifacts.
- Explicit non-goals preserved: no provider/default/runtime/live probe, no Host business-field exposure, no Agent runtime/tool-loop implementation, no score-loop, no golden/readiness promotion, no template truth replacement, no quality gate semantic change, no deterministic default `analyze/checklist` behavior change, no stdout partial report, no deterministic fallback, no PR/push/external state action.

## Accepted Artifacts

- Implementation evidence: `docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-implementation-evidence-20260603.md`.
- DS code review: `docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-code-review-ds-20260603.md`.
- MiMo code review: `docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-code-review-mimo-20260603.md`.
- Fix evidence: `docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-fix-evidence-20260603.md`.
- DS re-review: `docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-rereview-ds-20260603.md`.
- MiMo re-review: `docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-rereview-mimo-20260603.md`.
- Controller judgment: this file.

## Accepted Implementation

Slice 7 is accepted.

The implementation adds explicit Service-owned typed path selection:

- `TypedTemplatePathMode = "legacy_contract" | "typed_template_contract"`.
- `ChapterOrchestrationPolicy.typed_template_path`.
- `FundLLMRuntimePlan.typed_template_path`.
- `FundLLMExecutionRequest.typed_template_path`.
- Runtime plan validation requires its typed path to match `ChapterOrchestrationPolicy`.
- Execution request validation requires its typed path to match `FundLLMRuntimePlan`.

`build_fund_llm_execution_request()` selects `typed_template_contract` only for the explicit `--use-llm` Service execution request path. Default deterministic `analyze/checklist` remains outside the LLM execution request builder.

`ChapterOrchestrator` remains a Service-owned transition facade. On the explicit typed path it derives same-source `EvidenceAvailability` from `ChapterFactProjection`, passes typed required-output items and evidence availability into writer input, and passes typed chapter contract into auditor input so bounded semantic `audit_focus` is available. Initial and repair writer paths both receive `typed_required_output_items`. Legacy path returns no typed inputs and keeps typed required-output behavior inactive.

Independent body chapter execution remains preserved: one body chapter failure does not skip unrelated body chapters, and `dependency_missing` remains reserved for true writer dependency failures.

## Validation

Controller reran:

```bash
uv run pytest tests/services/test_execution_contract.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py
```

Result: `178 passed in 1.02s`.

```bash
uv run ruff check fund_agent/services tests/services tests/ui
```

Result: `All checks passed!`.

```bash
git diff --check
```

Result: exited `0`.

## Review Disposition

Initial DS and MiMo reviews found one shared blocking finding:

- `typed_required_output_items` was not wired from `TypedChapterContract.required_output_items` into writer input, so Slice 3 `RequiredOutputItem.when_evidence_missing` behavior could not activate through the Service facade.

The fix added `_typed_required_output_items()` and passed typed required-output items to both initial and repair `build_chapter_writer_input()` calls. Tests now prove the Service typed path produces a non-empty typed required-output evidence plan and that Ch3 missing evidence maps to `render_evidence_gap`.

DS re-review result: PASS, no remaining blockers.

MiMo re-review result: PASS, no remaining blockers.

Non-blocking observations accepted as residuals:

- `TypedTemplatePathMode` literal is duplicated between Service modules; this is a future cleanup only.
- Typed contract lookup is per chapter; this is acceptable because each chapter has different required output items.
- Typed path fake-output tests now fail stricter typed contract cases closed; this is expected and does not imply deterministic fallback.

## Controller Decision

Accepted locally. The implementation satisfies the Slice 7 acceptance criteria:

- Explicit typed fields select the typed path; no `extra_payload`, `kwargs`, `payload`, `metadata`, `context`, `dict[str, Any]` or `Mapping[str, Any]` business bags were introduced.
- `fund-analysis analyze` default does not build an LLM execution request, invoke Host, call LLM Service execution, or write incomplete LLM artifacts.
- `fund-analysis checklist` remains deterministic and does not accept typed LLM behavior.
- `fund-analysis analyze --use-llm` remains opt-in and fail-closed.
- Incomplete typed results remain diagnostics/artifacts only under existing safe policies; no stdout partial report is introduced.
- Host remains business-opaque; no Host files or business fields were modified.
- Provider construction, runtime ceilings, timeout defaults and clients remain Service-owned and unchanged.

## Residuals

- Slice 7 keeps `ChapterOrchestrator` as a Service-owned transition facade. Future Agent engine/tool-loop migration must decide how to move write-audit-repair execution and typed contract consumption into Agent while keeping Service use-case ownership.
- Service typed path now wires typed required-output items, evidence availability and audit focus, but Fund-layer writer/auditor semantics remain those accepted by earlier slices.
- Documentation/control sync after accepted implementation remains the next planned Slice 8 gate; this judgment does not update control docs or start Slice 8.

## Next Gate

Do not start the next gate from this judgment. If the controller is explicitly instructed to continue after this accepted checkpoint, the next planned gate is `MVP typed template contract Slice 8 Documentation And Control Sync After Accepted Implementation`.

Provider-runtime branch remains paused before live PASS-only probe. No provider/default/runtime change is authorized by this Slice 7 acceptance.
