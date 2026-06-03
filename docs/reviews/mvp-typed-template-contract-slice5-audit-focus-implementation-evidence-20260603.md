# MVP typed template contract Slice 5 audit_focus implementation evidence

## Self-check

- Role: implementation worker only, not controller.
- Gate: `MVP typed template contract Slice 5 per-chapter audit_focus bounded semantic audit implementation gate`.
- Classification: heavy.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Scope: typed per-chapter `audit_focus` is projected from `TypedChapterContract` into `ChapterAuditLLMRequest` and bounded semantic audit prompt wording only.
- Non-goals respected: no provider/runtime/default/budget change, no live provider probe, no Agent runtime/tool-loop implementation, no score-loop, no golden/readiness change, no template truth replacement.

## Files changed

- `fund_agent/fund/chapter_auditor.py`
- `tests/fund/test_chapter_auditor.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/mvp-typed-template-contract-slice5-audit-focus-implementation-evidence-20260603.md`

## Behavior summary

- Added `ChapterAuditInput.typed_chapter_contract` as an explicit optional typed input.
- When `typed_chapter_contract` is supplied, LLM audit request focus is projected from `TypedChapterContract.audit_focus`.
- Typed focus ids are validated against the closed set `SUPPORTED_AUDIT_FOCUS`.
- When typed input is not supplied, the existing `DEFAULT_AUDIT_FOCUS` LLM request compatibility path remains unchanged.
- LLM prompt wording states focus ids are bounded semantic emphasis only and may only group repair wording semantically.
- Invalid typed focus projection, including chapter mismatch, empty focus or closed-set violation, is converted to a typed LLM audit blocked result before the LLM client is called.
- Programmatic audit does not read `typed_chapter_contract` or focus ids; C2, L1, marker, anchor, item-rule, forbidden advice, missing/degrade and severity behavior remain independent of focus.
- Safe artifact serialization was not changed; no raw prompt, raw provider response, draft body beyond existing allowed artifact behavior, API key, Authorization header, provider config values, or omitted model names were added.

## Tests added or updated

- Added `tests/fund/test_chapter_auditor.py::test_per_chapter_audit_focus_is_passed_to_llm_request`.
- Added `tests/fund/test_chapter_auditor.py::test_programmatic_blocker_fires_even_when_focus_omits_must_not_cover_boundary`.
- Added `tests/fund/test_chapter_auditor.py::test_invalid_typed_audit_focus_blocks_without_calling_client`.
- Added `tests/fund/test_chapter_auditor.py::test_mismatched_typed_audit_focus_blocks_without_calling_client`.
- Extended existing LLM prompt protocol test to assert current default path still uses `DEFAULT_AUDIT_FOCUS`.
- Did not add `tests/services/test_llm_run_artifacts.py::test_artifact_serializes_audit_focus_ids_only_if_added` because artifact serialization was not touched.

## Validation

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/services/test_llm_run_artifacts.py
```

Result: passed, `46 passed in 0.65s`.

```bash
uv run pytest tests/fund/template/test_typed_contracts.py
```

Result: passed, `8 passed in 0.51s`.

```bash
uv run ruff check fund_agent/fund fund_agent/services tests/fund tests/services
```

Result: passed, `All checks passed!`.

```bash
git diff --check
```

Result: passed, no output.

## Explicit non-changes

- Provider/runtime/default/live probe behavior was not changed.
- Provider timeout, retry, max output, model, endpoint, budget and config behavior were not changed.
- Agent runtime, Agent tool-loop, Host behavior and dayu runtime integration were not implemented or changed.
- Score-loop, golden, readiness, promotion and quality gate semantics were not changed.
- Template truth replacement was not performed; `docs/fund-analysis-template-draft.md` and typed manifest truth semantics were not changed.
- Programmatic audit blocking severity and rule selection were not changed.

## Residual risks

- Current Service orchestration path does not yet pass a typed contract into `ChapterAuditInput`; this slice implements the explicit Fund auditor input path and preserves default compatibility. Wiring broader orchestration would touch Service outside the allowed file/module scope for this worker gate.
