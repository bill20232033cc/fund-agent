# MVP typed template contract Slice 5 audit_focus controller judgment

## Controller Self-Check

- Role: controller; implementation and fix were delegated to AgentCodex, code review to AgentDS and AgentMiMo.
- Gate: `MVP typed template contract Slice 5 per-chapter audit_focus bounded semantic audit implementation gate`.
- Classification: `heavy`.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Scope boundary: typed per-chapter `audit_focus` projection into Fund-layer LLM bounded semantic audit request, tests, README sync and review artifacts only.
- Explicit non-goals preserved: no provider/runtime/default/budget/endpoint change, no live provider probe, no Agent runtime/tool-loop implementation, no score-loop, no golden/readiness/promotion change, no template truth replacement, no Service facade wiring, no `extra_payload`, no deterministic fallback and no stdout partial report behavior change.

## Accepted Artifacts

- Implementation evidence: `docs/reviews/mvp-typed-template-contract-slice5-audit-focus-implementation-evidence-20260603.md`.
- DS code review: `docs/reviews/mvp-typed-template-contract-slice5-audit-focus-code-review-ds-20260603.md`.
- MiMo code review: `docs/reviews/mvp-typed-template-contract-slice5-audit-focus-code-review-mimo-20260603.md`.
- Controller judgment: this file.

## Accepted Implementation

Slice 5 is accepted.

The implementation adds an explicit optional `ChapterAuditInput.typed_chapter_contract` field. When supplied, `audit_chapter_llm()` projects `TypedChapterContract.audit_focus` into `ChapterAuditLLMRequest.audit_focus` and into bounded semantic prompt wording. When omitted, the old `DEFAULT_AUDIT_FOCUS` compatibility path remains unchanged.

The accepted behavior is limited to LLM bounded semantic audit input:

- `audit_focus` ids are validated against `SUPPORTED_AUDIT_FOCUS`.
- Chapter mismatch, empty focus or closed-set violation fail closed as `llm:audit_focus_invalid` before the LLM client is called.
- Programmatic audit does not read `typed_chapter_contract` or `audit_focus`; C2, L1, marker, anchor, item-rule, forbidden advice, missing/degrade and severity behavior remain always-on and independent of focus.
- Artifact serialization was not changed; the planned artifact test was correctly skipped because this slice did not add serialized focus fields.

## Validation

Controller reran:

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/services/test_llm_run_artifacts.py
```

Result: `46 passed in 0.52s`.

```bash
uv run pytest tests/fund/template/test_typed_contracts.py
```

Result: `8 passed in 0.40s`.

```bash
uv run ruff check fund_agent/fund fund_agent/services tests/fund tests/services
```

Result: `All checks passed!`.

```bash
git diff --check
```

Result: exited `0`.

## Review Disposition

DS review result: PASS, no blocking findings.

MiMo review result: PASS, no blocking findings.

Non-blocking observations are accepted as residuals, not Slice 5 blockers:

- The `ValueError` conversion in `audit_chapter_llm()` uses a generic safe blocked issue instead of preserving the exact focus validation reason. This is acceptable because the diagnostic is intentionally safe and `_llm_request()` currently raises `ValueError` only for typed focus projection failures.
- `DEFAULT_AUDIT_FOCUS` default-path coverage is partly implicit through the existing prompt protocol test. This is acceptable because the test now directly asserts `request.audit_focus == DEFAULT_AUDIT_FOCUS`.
- The plan-listed artifact serialization test was not added because artifact serialization was not touched. This is accepted and recorded in the implementation evidence.
- Current Service orchestration does not yet pass typed contracts into `ChapterAuditInput`; Service facade wiring remains a later accepted-plan slice.

## Controller Decision

Accepted locally. The implementation satisfies the Slice 5 acceptance criteria:

- per-chapter typed `audit_focus` is projected into the LLM audit request;
- LLM request receives closed-set focus values only;
- invalid focus fails closed before provider/client success path;
- programmatic audit blockers remain independent of focus and severity is unchanged;
- no provider timeout/budget/default/runtime changes are introduced.

## Next Gate

Start `MVP typed template contract Slice 6 Ch0 consumes Ch7 with fail-closed required-body readiness implementation gate`.

Slice 6 must stay within the accepted plan: make final assembly dependency explicit, ensure Ch0 consumes Ch7 rather than independently deriving or strengthening final action, preserve incomplete `--use-llm` fail-closed behavior with empty stdout, and avoid provider/runtime/default/live probe, Agent runtime/tool-loop, score-loop, golden/readiness or deterministic default behavior changes.
