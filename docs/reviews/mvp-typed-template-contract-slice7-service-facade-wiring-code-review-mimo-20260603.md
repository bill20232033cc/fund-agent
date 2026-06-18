# MVP typed template contract Slice 7 Service Facade Wiring Code Review — MiMo

## Reviewer

- Role: AgentMiMo, code review worker only.
- Gate: `MVP typed template contract Slice 7 Service Facade Wiring Behind Explicit Typed Path implementation gate`.
- Classification: `heavy`.
- Sources read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md` (Slice 7 section), `docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-implementation-evidence-20260603.md`, full worktree diff, and touched source/test files.
- Actions intentionally not taken: no source code edit, no commit, no push, no PR.

## Validation Results

| Command | Result |
|---|---|
| `uv run pytest tests/services/test_execution_contract.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py` | **177 passed** |
| `uv run ruff check fund_agent/services tests/services tests/ui` | **All checks passed** |
| `git diff --check` | **Passed (no whitespace errors)** |

## Review Focus Findings

### 1. Explicit typed_template_path field selection — PASS

`typed_template_path` is a closed `Literal["legacy_contract", "typed_template_contract"]` field added to three types:

- `ChapterOrchestrationPolicy.typed_template_path` (chapter_orchestrator.py:350)
- `FundLLMRuntimePlan.typed_template_path` (execution_contract.py:286)
- `FundLLMExecutionRequest.typed_template_path` (execution_contract.py:383)

All three default to `"legacy_contract"`. Validation uses `frozenset` allowlists (`_ALLOWED_TYPED_TEMPLATE_PATH_MODES`). Cross-type consistency is enforced:

- `FundLLMRuntimePlan.__post_init__` validates `chapter_policy.typed_template_path == self.typed_template_path`.
- `FundLLMExecutionRequest.__post_init__` validates `self.typed_template_path == self.runtime_plan.typed_template_path`.

No `extra_payload`, `kwargs`, `payload`, `metadata`, `context`, `dict[str, Any]`, or `Mapping[str, Any]` bags exist on any touched public type or signature. The test `test_no_extra_payload_or_free_business_payload_bag` explicitly guards these forbidden names and `VAR_KEYWORD` parameter kinds.

Test coverage:

- `test_typed_template_flags_are_explicit_fields_if_added` — verifies field presence and value.
- `test_no_extra_payload_or_free_business_payload_bag` — guards against open business bags.
- `test_execution_request_rejects_typed_template_path_mismatch` — verifies cross-type consistency.

### 2. build_fund_llm_execution_request typed path scope — PASS

`build_fund_llm_execution_request()` (fund_analysis_service.py:947-993) hardcodes `typed_template_path="typed_template_contract"` on all three typed objects (`ChapterOrchestrationPolicy`, `FundLLMRuntimePlan`, `FundLLMExecutionRequest`). This function is only called on the explicit `--use-llm` Service execution path.

The default `analyze` path and `checklist` path do not call this function. The test `test_default_analyze_unchanged_with_typed_contract_modules_present` explicitly verifies that default `analyze`:

- Does not call `build_fund_llm_execution_request`.
- Does not invoke `HostRuntimeRunner`.
- Does not call `write_llm_incomplete_run_artifacts`.
- Produces deterministic output.

### 3. ChapterOrchestrator as Service-owned transition facade — PASS WITH FINDING

The `ChapterOrchestrator` correctly consumes typed inputs:

- `_typed_template_inputs()` derives `EvidenceAvailability` from same-source `ChapterFactProjection` (pure, no repository/LLM/Host calls).
- `evidence_availability` is passed to `build_chapter_writer_input()` in both initial and repair paths.
- `typed_chapter_contract` is passed to `ChapterAuditInput` for bounded semantic `audit_focus` projection.
- Independent body chapter execution is preserved: the test `test_typed_contract_path_preserves_independent_body_execution` verifies that Ch1 failure does not skip Ch2/Ch3, and `dependency_missing` is reserved for true writer dependency stop reasons.

**Finding F1 (Blocking): `typed_required_output_items` not wired to writer.**

The orchestrator passes `evidence_availability` to `build_chapter_writer_input()` but does NOT extract and pass `TypedChapterContract.required_output_items` as `typed_required_output_items`. Both the initial writer path (line 1053-1058) and the repair path (line 1243-1253) omit this parameter.

Impact: Slice 3's accepted `RequiredOutputItem.when_evidence_missing` behavior (`render_evidence_gap`, `render_minimum_verification_question`, `delete_if_not_applicable`, `block`) does NOT activate through the Service facade. The writer receives `evidence_availability` but has no typed items to apply the missing/degrade semantics to. The `_required_output_evidence_plan()` function in chapter_writer.py:914-924 checks `typed_items = input_data.typed_required_output_items`; when this is empty, it returns `()` immediately, making `evidence_availability` inert for required-output purposes.

The typed contract's `required_output_items` are available via `get_typed_chapter_contract(chapter_id).required_output_items` — the same API already used by `_typed_chapter_contract()` for auditor input. The fix is:

1. Add a helper `_typed_required_output_items(chapter_id, *, typed_inputs)` that extracts `required_output_items` from the typed contract (parallel to `_typed_chapter_contract`).
2. Pass the result as `typed_required_output_items=` to both `build_chapter_writer_input()` calls.

This is a Service-layer wiring change; it does not require modifying Fund-layer writer/auditor semantics.

### 4. Host business-field opacity — PASS

No Host files were touched in this diff. The existing CLI path continues to pass only generic `operation`, `deadline`, and optional `session` to Host. `ChapterOrchestrationPolicy`, `FundLLMRuntimePlan`, and `FundLLMExecutionRequest` business fields remain in Service; Host receives only `host_timeout_seconds` as a scalar deadline.

### 5. Scope creep check — PASS

No changes to:

- Provider construction defaults, timeout budgets, clients, endpoint selection, or live probe.
- Agent runtime, tool loop, ToolRegistry, ToolTrace, or dayu runtime.
- Score, golden, readiness, template truth, or quality gate semantics.
- Deterministic default `analyze/checklist` behavior.
- `docs/design.md`, `docs/implementation-control.md`, or `AGENTS.md`.
- Host business fields.

**Style note S1 (Non-blocking):** `TypedTemplatePathMode` is defined identically as a `Literal` in both `chapter_orchestrator.py:76` and `execution_contract.py:36`. This is duplication; consider importing from `execution_contract.py` as the canonical source.

### 6. Blocking assessment: typed_required_output_items gap — BLOCKING

**Verdict: Blocking.**

The implementation evidence states: "It does not modify Fund-layer auditor marker semantics or broaden typed required-output marker behavior because Fund files were outside this worker's allowed file list." This is accurate for the Fund-layer semantics themselves, but the **Service-layer wiring** of `typed_required_output_items` to the writer is within the Service facade scope and does not require modifying Fund files.

Slice 7's stated purpose (plan line 325-326): "wire typed contract/availability/audit behavior into the current Service-owned LLM facade without changing default deterministic behavior or entering Agent runtime implementation."

The `TypedChapterContract.required_output_items` field exists (typed_contracts.py:193). The `ChapterWriterInput.typed_required_output_items` field exists and is consumed by `_required_output_evidence_plan()` (chapter_writer.py:914). The `EvidenceAvailability` is already derived and passed. The only missing piece is extracting the items from the contract and passing them through — a Service-layer wiring operation, not a Fund-layer semantics change.

Without this wiring, the typed path through the Service facade produces an `evidence_availability` that no writer code path consumes for required-output purposes. The typed path is partially wired: auditor gets `audit_focus`, but writer does not get `typed_required_output_items`. This is an incomplete implementation of the stated Slice 7 objective.

**Recommended fix (non-blocking to implement, blocking to accept gate):**

Add to `chapter_orchestrator.py`:

```python
def _typed_required_output_items(
    chapter_id: int,
    *,
    typed_inputs: _TypedTemplateInputs | None,
) -> tuple[RequiredOutputItem, ...]:
    if typed_inputs is None:
        return ()
    contract = get_typed_chapter_contract(chapter_id)
    return contract.required_output_items
```

Then pass `typed_required_output_items=_typed_required_output_items(chapter_id, typed_inputs=typed_inputs)` to both `build_chapter_writer_input()` calls (initial at line 1053, repair at line 1243).

## Summary

| # | Finding | Severity | Blocking |
|---|---|---|---|
| F1 | `typed_required_output_items` not wired from `TypedChapterContract` to `build_chapter_writer_input()` — Slice 3 missing/degrade behavior does not activate through Service facade | High | **Yes** |
| S1 | `TypedTemplatePathMode` Literal duplicated in two modules | Low | No |

## Conclusion

The Slice 7 implementation correctly adds explicit `typed_template_path` field selection with cross-type validation, preserves deterministic default `analyze/checklist`, keeps Host business-field opacity, maintains independent body chapter execution, and introduces no scope creep. All 177 tests pass, ruff is clean, and diff has no whitespace errors.

One blocking finding remains: `typed_required_output_items` is not wired from the typed contract to the writer input. This is a Service-layer wiring gap that prevents Slice 3's accepted `RequiredOutputItem.when_evidence_missing` behavior from activating through the facade. The fix is small and scoped to `chapter_orchestrator.py`. The gate should not be accepted until this wiring is complete.

Secret-safety statement: this review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
