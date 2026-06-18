# MVP typed template contract Slice 5 audit_focus code review — MiMo

## Self-check

- Role: code review worker only, not controller and not implementation worker.
- Gate: `MVP typed template contract Slice 5 per-chapter audit_focus bounded semantic audit implementation gate`.
- Classification: heavy.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Files reviewed: `fund_agent/fund/chapter_auditor.py`, `tests/fund/test_chapter_auditor.py`, `fund_agent/fund/README.md`, `tests/README.md`.
- Sources read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md` (Slice 5 section), `docs/reviews/mvp-typed-template-contract-slice5-audit-focus-implementation-evidence-20260603.md`.
- Actions intentionally not taken: no file edit, no commit, no push, no PR, no live provider probe, no gate entry.

## Validation

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/services/test_llm_run_artifacts.py -q
```

Result: `46 passed in 0.49s`.

```bash
uv run pytest tests/fund/template/test_typed_contracts.py -q
```

Result: `8 passed in 0.44s`.

```bash
uv run ruff check fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_auditor.py fund_agent/fund/README.md tests/README.md
```

Result: `All checks passed!`.

```bash
git diff --check
```

Result: no output.

## Findings

### Finding 1 — Non-blocking: Plan test name `test_artifact_serializes_audit_focus_ids_only_if_added` was dropped

**Severity**: non-blocking.
**Location**: `tests/fund/test_chapter_auditor.py`.
**Detail**: The Slice 5 plan listed three test names, including `tests/services/test_llm_run_artifacts.py::test_artifact_serializes_audit_focus_ids_only_if_added`. The implementation dropped this test and correctly documented the reason in the evidence: artifact serialization was not touched by this slice. The implementation added two additional tests (`test_invalid_typed_audit_focus_blocks_without_calling_client` and `test_mismatched_typed_audit_focus_blocks_without_calling_client`) that were not in the plan but are required by the acceptance criteria ("invalid/mismatched focus fail-closed without calling the LLM client"). The net test coverage is stronger than the plan minimum.
**Disposition**: accepted; the evidence artifact explicitly explains the deviation.

### Finding 2 — Non-blocking: `_llm_audit_focus` raises generic `ValueError` instead of a typed exception

**Severity**: non-blocking.
**Location**: `fund_agent/fund/chapter_auditor.py:1453-1479`.
**Detail**: `_llm_audit_focus()` raises bare `ValueError` for three distinct failure modes (chapter mismatch, empty focus, unknown focus ids). The caller `audit_chapter_llm()` catches all `ValueError` identically and converts to `llm:audit_focus_invalid` blocked. This is functionally correct and fail-closed. A typed exception subclass could disambiguate diagnostics in the future, but the current gate scope does not require it and the catch-all conversion is safe.
**Disposition**: accepted as-is; future diagnostic refinement may introduce a typed exception.

## Review Matrix

| Review focus | Verdict | Evidence |
|---|---|---|
| Typed per-chapter `audit_focus` projects from `TypedChapterContract` into `ChapterAuditLLMRequest` only for LLM bounded semantic audit | PASS | `_llm_audit_focus()` reads `input_data.typed_chapter_contract.audit_focus` only; programmatic audit (`audit_chapter_programmatic`) never reads `typed_chapter_contract` or focus ids. |
| Default path preserves `DEFAULT_AUDIT_FOCUS` compatibility | PASS | `_llm_audit_focus()` returns `DEFAULT_AUDIT_FOCUS` when `typed_chapter_contract is None`; existing test `test_llm_audit_prompt_spells_exact_pass_and_issue_line_protocol` now explicitly asserts `request.audit_focus == DEFAULT_AUDIT_FOCUS`. |
| Focus ids validated against closed set; invalid/mismatched focus fail-closed without calling LLM client | PASS | `_llm_audit_focus()` validates chapter match, non-empty focus, and closed-set membership via `SUPPORTED_AUDIT_FOCUS`; `ValueError` is caught in `audit_chapter_llm()` and converted to `status="blocked"` with `issue_id="llm:audit_focus_invalid"` before `llm_client.audit_chapter()` is called. Tests `test_invalid_typed_audit_focus_blocks_without_calling_client` and `test_mismatched_typed_audit_focus_blocks_without_calling_client` assert `client.requests == []`. |
| Programmatic audit independent of focus for C2, L1, markers, anchors, item-rule, forbidden advice, missing/degrade and severity | PASS | `audit_chapter_programmatic()` delegates to `_audit_*` functions that read `input_data.writer_input` and call `_typed_chapter_contract_for()` (internal loader), never reading `input_data.typed_chapter_contract` or `audit_focus`. Test `test_programmatic_blocker_fires_even_when_focus_omits_must_not_cover_boundary` confirms C2 fires when `must_not_cover_boundary` is absent from the typed contract's focus. |
| Tests sufficient, including non-disabling programmatic blocker and no-raise invalid focus behavior | PASS | Four new tests plus one assertion addition to existing test. Coverage exceeds plan minimum. Validation 46 passed, ruff clean. |
| README updates accurate and not overclaiming | PASS | `fund_agent/fund/README.md` updated `audit_focus` description to reflect LLM request projection semantics while preserving "不能关闭 programmatic blockers" guardrail. `tests/README.md` updated test description to mention typed per-chapter `audit_focus`. Neither claims Service wiring, Agent runtime, provider/runtime, score-loop, template truth replacement, or golden/readiness changes. |
| No secret/prompt/raw provider response leakage | PASS | No API key, Authorization header, raw provider response, raw prompt text, provider config values, or omitted model names added. The `_llm_request` system/user prompts are constructed from typed scalar values only. |

## Adversarial Failure Analysis

1. **Can `audit_focus` disable programmatic blockers?** No. `audit_chapter_programmatic()` never reads `typed_chapter_contract` or `audit_focus`. The programmatic audit functions (`_audit_must_not_cover`, `_audit_numerical_closure`, etc.) use `_typed_chapter_contract_for()` which loads from the typed contract loader, not from the input's `typed_chapter_contract` field. Even if a future caller passes a typed contract with a focus subset omitting `must_not_cover_boundary`, the programmatic C2 check still fires.

2. **Can invalid focus leak to the LLM client?** No. `_llm_audit_focus()` raises `ValueError` before `_llm_request()` returns. The caller catches `ValueError` and returns `blocked` without calling `llm_client.audit_chapter()`.

3. **Can chapter mismatch between typed contract and input go undetected?** No. `_llm_audit_focus()` explicitly checks `typed_contract.chapter_id != input_data.writer_input.chapter.chapter_id` and raises `ValueError`.

4. **Does the default path still work when no typed contract is passed?** Yes. `_llm_audit_focus()` returns `DEFAULT_AUDIT_FOCUS` when `typed_contract is None`. The existing LLM prompt protocol test now asserts `request.audit_focus == DEFAULT_AUDIT_FOCUS`.

## Verdict

**PASS** — No blocking findings. Two non-blocking findings accepted with evidence-based justification. Implementation correctly wires typed per-chapter `audit_focus` as bounded semantic audit input, preserves default compatibility, validates against closed set with fail-closed behavior, keeps programmatic audit independent of focus, and maintains safe diagnostics.

## Residual risks

- Current Service orchestration path (`ChapterOrchestrator`) does not yet pass a typed contract into `ChapterAuditInput`; this slice implements the explicit Fund auditor input path and preserves default compatibility. Service wiring is a separate future gate.
- `_llm_audit_focus` uses generic `ValueError`; future diagnostic refinement may introduce a typed exception subclass for finer-grained blocked-issue disambiguation.
