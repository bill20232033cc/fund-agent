# Code Review

## Scope

- Mode: role-scoped implementation review
- Gate: Provider/LLM Chapter 3 Required-output Item 01 Missing-evidence No-live Fix Implementation Gate
- Base: current workspace diff
- Output file: `docs/reviews/provider-llm-chapter3-required-output-item01-missing-evidence-no-live-fix-implementation-review-mimo-20260614.md`
- Included scope: `docs/fund-analysis-template-draft.md`, `tests/agent/test_runner.py`, `tests/fund/template/test_typed_contracts.py`, `tests/README.md`
- Excluded scope: all live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands; control/design doc updates; code changes
- Parallel review coverage: 无

## Findings

未发现实质性问题。

### Verification Summary

The implementation correctly converts missing basic manager info from provider-before `ValueError` / `code_bug` to zero-provider fact-gap `blocked`. Verification chain:

1. **Template change** (`docs/fund-analysis-template-draft.md:667-668`): `ch3.required_output.item_01` changed from `when_evidence_missing=null, missing_evidence_reason=null` to `when_evidence_missing="block", missing_evidence_reason="第 3 章基金经理基本信息缺少已复核证据时不能进入基金经理画像写作。"`. Minimal, single-item, no structural change.

2. **Typed projection** (`fund_agent/fund/template/typed_contracts.py:476-510`): `_project_required_output_entries` reads `when_evidence_missing` via `_read_optional_string` and casts to `MissingEvidenceBehavior | None`. The value `"block"` is in `SUPPORTED_MISSING_EVIDENCE_BEHAVIORS` (line 58-61). Validation at line 787-788 ensures `missing_evidence_reason` is present when `when_evidence_missing` is non-null.

3. **Availability derivation** (`fund_agent/fund/evidence_availability.py:247-251`): `ch3.required_output.item_01` depends on `structured.basic_identity` and `structured.portfolio_managers`. When `portfolio_managers` is missing, the fact status is "missing", which `_status_for_fact` (line 489-508) maps to availability status `"missing"`.

4. **Writer action** (`fund_agent/fund/chapter_writer.py:994-1024`): `_required_output_action` receives `status="missing"` and `behavior="block"`. Since status is in `_MISSING_EVIDENCE_STATUSES` and behavior is `"block"`, it falls through `render_evidence_gap` / `render_minimum_verification_question` / `delete_if_not_applicable` checks and returns `"block"` at line 1024. This is correct — `"block"` is the explicit fail-closed behavior for this item.

5. **Preflight blocking** (`fund_agent/fund/chapter_writer.py:1090-1113`): `_required_output_preflight_issues` generates a blocking `ChapterWriteIssue` with reason `"missing_required_facts"` for any plan item with `action="block"`. The `write_chapter` function returns `_blocked_result` with stop_reason `"missing_required_facts"` (line 762).

6. **Agent runner mapping** (test evidence): Agent runner maps the blocked writer result to `task.status="blocked"`, `task.terminal_state="blocked_fact_gap"`, `task.stop_reason="missing_required_facts"`, `task.failure_category="fact_gap"`. Zero writer/provider requests.

7. **Pre-fix vs post-fix**: Before the fix, `_required_output_action` raised `ValueError("typed required output 缺证但未声明 when_evidence_missing")` because behavior was `None`. The agent runner caught this as `code_bug` / `llm_exception`. After the fix, it returns `"block"` and the task becomes `blocked_fact_gap`. The red test confirmed this: `AssertionError: assert 'failed' == 'blocked'` before fix, all assertions pass after fix.

8. **Existing envelope test preserved**: `test_chapter_3_missing_evidence_availability_envelope_remains_value_error` confirms that when `EvidenceAvailability` is completely absent (not just a single item missing), the path still raises `ValueError`. This is the correct fail-closed behavior for the typed-required-output-must-have-availability invariant.

### Test Coverage

| Test | What it proves |
| --- | --- |
| `test_chapter_3_missing_basic_manager_info_blocks_before_provider` | End-to-end: missing `portfolio_managers` → availability "missing" → action "block" → blocked fact-gap, zero provider calls |
| `test_chapter_3_basic_manager_info_missing_behavior_blocks` | Template guard: typed projection locks `when_evidence_missing="block"` and `missing_evidence_reason` for `ch3.required_output.item_01` |
| `test_chapter_3_missing_evidence_availability_envelope_remains_value_error` | Regression: completely absent `EvidenceAvailability` still raises `ValueError` (separate invariant) |
| `test_chapter_3_missing_typed_availability_blocks_before_provider` | Regression: empty availability requirements → block path for `ch3.required_output.item_03` |

### Validation Commands

All allowed commands pass:

- `git diff --check`: clean
- `uv run pytest ... -q`: 5/5 tests pass (3 runner + 2 typed contracts)
- `uv run ruff check ...`: all checks passed

## Open Questions

无。

## Residual Risk

| Residual | Disposition |
| --- | --- |
| Other typed required-output items with `when_evidence_missing=null` may have analogous risks if evidence availability becomes non-available. | Deferred; not touched by this gate. |
| The `when_evidence_missing="block"` also triggers for `unavailable`, `not_applicable`, and `unreviewed` statuses (all in `_MISSING_EVIDENCE_STATUSES`), not only `missing`. The test only covers `missing`. | Low risk: all four statuses represent insufficient evidence, and "block" is the correct fail-closed behavior for all. The root cause evidence confirmed this status set. |
| Existing service diagnostic tests still cover synthetic pre-writer `ValueError` injection paths. | Not changed; these remain diagnostic regression tests for code-bug mapping. |
| No post-fix live command was run. | Expected; current gate is no-live implementation. |
| Release/readiness remains `NOT_READY`. | Preserved. |

## Reviewer Self-Check

- Review mode, scope, and source evidence: recorded above.
- Findings bound to specific code locations and behavior: yes (template line, typed_contracts projection, evidence_availability derivation, chapter_writer action, agent runner mapping).
- No style/nit/speculation findings.
- Adversarial pass: checked edge cases (null behavior pre-fix, completely absent availability, other missing evidence statuses).
- Output path: `docs/reviews/provider-llm-chapter3-required-output-item01-missing-evidence-no-live-fix-implementation-review-mimo-20260614.md`.

## Verdict

**PASS**

The template fix and tests correctly convert missing basic manager info from provider-before `ValueError` / `code_bug` to zero-provider fact-gap `blocked`. The change is minimal (2 values in 1 template item), fail-closed, well-tested, and preserves all guardrails.
