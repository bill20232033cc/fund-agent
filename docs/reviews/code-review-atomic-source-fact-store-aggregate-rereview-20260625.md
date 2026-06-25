# Atomic Source Fact Store Aggregate Deepreview Re-review

## Scope

- Gate: Atomic Source Fact Store / Composite Analysis View Split Aggregate Deepreview Re-review.
- Branch: `evidence-confirm-productionization`.
- Accepted finding under re-review: `F-01` from `docs/reviews/code-review-atomic-source-fact-store-aggregate-20260625.md`.
- Fix artifact reviewed: `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-aggregate-fix-20260625.md`.
- Code/tests reviewed: `fund_agent/fund/evidence_confirm.py`, `tests/fund/test_evidence_confirm_atomic.py`.
- Excluded by instruction: live/PDF/repository/source-helper/parser/provider/LLM/product CLI commands, PR/remote state, staging, commit, push, merge, tag, release, readiness mutation.

## Finding Status

`F-01`: 已修复

## Re-review Evidence

1. Dual bridge identity now fails closed.
   - `fund_agent/fund/evidence_confirm.py:1884-1887` returns `_UNRESOLVED_FACT_MATERIAL` when `source_fact_ids` is non-empty and `derived_view_id is not None`.
   - `fund_agent/fund/evidence_confirm.py:570` passes the resolved material value into V2 value_match, and `fund_agent/fund/evidence_confirm.py:1106-1118` turns unresolved material into an E3 blocking `value_match` failure with message `bridge fact 无法解析 material value。`.
   - `tests/fund/test_evidence_confirm_atomic.py:98-133` mutates a valid atomic fact into dual identity, verifies V2 fact status `fail`, value_match `fail`, diagnostics zero material tokens, and a blocking issue containing `bridge fact 无法解析 material value`.

2. Duplicate `derived_view_id` target now fails closed.
   - `fund_agent/fund/evidence_confirm.py:1993-1998` collects all matching derived views and only returns a view when cardinality is exactly one.
   - For derived facts, `fund_agent/fund/evidence_confirm.py:515-519` calls `_derived_dependency_provenance_issues()`, and `fund_agent/fund/evidence_confirm.py:1943-1948` emits an E3 blocking issue when the derived view cannot be uniquely resolved.
   - `tests/fund/test_evidence_confirm_atomic.py:136-162` appends a duplicate `derived_views` entry with the same `view_id`, verifies V2 fact status `fail`, missing_evidence `fail`, and a blocking issue containing `derived_view_id 未在 projection.derived_views 中解析`.

3. Valid single atomic bridge and legacy no-bridge behavior are preserved.
   - `fund_agent/fund/evidence_confirm.py:1888-1894` still resolves exactly one `source_fact_id` to the atomic source fact value.
   - `fund_agent/fund/evidence_confirm.py:1900` still returns `fact.value` when no projection bridge is present on the fact.
   - `tests/fund/test_evidence_confirm_atomic.py:165-192` verifies a valid single atomic bridge still passes `value_match`.
   - Existing legacy tests remained in place: `tests/fund/test_evidence_confirm_atomic.py:259-287` verifies no-bridge composite value behavior, and `tests/fund/test_evidence_confirm_atomic.py:290-319` verifies no-atomic-facts summary behavior.

4. No unrelated ECQ/quality-gate/report-body/checklist/provider/CLI/live/PDF behavior was changed.
   - The scoped diff under review contains only `fund_agent/fund/evidence_confirm.py` and `tests/fund/test_evidence_confirm_atomic.py`.
   - The code change is limited to Evidence Confirm bridge material resolution and derived-view lookup cardinality. No Service/UI/Host/renderer, quality-gate, report body, checklist, provider, CLI, live, PDF, repository, source-helper, parser, or LLM path was modified or executed.
   - V2 behavior changed only for the targeted malformed bridge cases required by `F-01`; related V2 regression suites passed.

## Validation

- `git branch --show-current` -> `evidence-confirm-productionization`.
- `git status --short` showed existing unrelated dirty/untracked residue before re-review; left untouched.
- `uv run pytest tests/fund/test_evidence_confirm_atomic.py -q` -> `9 passed in 0.75s`.
- `uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm_value_diagnostics.py -q` -> `108 passed in 1.28s`.
- `uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm_atomic.py` -> `All checks passed!`.
- `git diff --check -- fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm_atomic.py docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-aggregate-fix-20260625.md` -> passed.

## Residual Risk

- No live/PDF/repository/source-helper/parser/provider/LLM/product CLI validation was run by instruction.
- This re-review does not prove release/readiness, PR readiness, production adoption, or provider/CLI behavior.
- Existing unrelated workspace residue was observed and not reviewed.

## Verdict

ATOMIC_SOURCE_FACT_STORE_AGGREGATE_REREVIEW_PASS_READY_FOR_ACCEPTED_DEEPREVIEW_COMMIT_NOT_READY
