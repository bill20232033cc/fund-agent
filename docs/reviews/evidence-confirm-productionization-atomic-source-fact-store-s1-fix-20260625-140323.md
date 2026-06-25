# Atomic Source Fact Store S1 Code Review Fix

## Gate

- Work unit: `Atomic Source Fact Store / Composite Analysis View Split`
- Gate: `S1 fix gate after code review`
- Accepted review artifact: `docs/reviews/code-review-atomic-source-fact-store-s1-subagent-20260625-135803.md`
- Accepted finding: `S1-CR-001`
- Fix artifact: `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s1-fix-20260625-140323.md`
- Verdict: `S1_FIX_IMPLEMENTED_READY_FOR_REREVIEW_NOT_READY`

## Accepted Finding Fixed Status

- `S1-CR-001`: fixed in current slice.
- Fixed behavior:
  - `build_composite_analysis_view()` no longer accepts a caller-supplied composite `value`.
  - View `value` is derived only from dependency atomic facts as `{fact_id: fact.value}`.
  - Absent dependency ids return fail-closed `partial` or `missing` views with explicit `missing dependency fact: <fact_id>` gaps.
  - `required_fact_ids` must be a subset of `dependency_fact_ids`; otherwise construction raises `ValueError`.
  - Empty `dependency_fact_ids` returns `status="missing"` and `value=None`.

## Changed Files

- `fund_agent/fund/source_facts.py`
- `tests/fund/test_source_facts.py`
- `fund_agent/fund/README.md`
- `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s1-fix-20260625-140323.md`

## Contract Decision

S1 helper contract is construction-time derived-only:

- composite analysis views are compatibility views, not extraction truth;
- the helper does not trust external composite payloads;
- the visible view value is assembled from the atomic fact store only;
- missing dependency fact ids are source gaps and therefore become deterministic view gaps/status;
- invalid required dependency configuration is a caller contract error and raises `ValueError`.

This fix does not change S2/S3/S4/S5 scope, default parsed annual child emission, explicit FDD atomic preservation, ChapterFactProvider, Evidence Confirm bridge behavior, live/PDF, product CLI, provider/LLM, PR state, release, or readiness.

## Validation

Passed:

- `uv run pytest tests/fund/test_source_facts.py -q`
  - `17 passed in 0.77s`
- `uv run pytest tests/fund/test_data_extractor.py -q`
  - `57 passed in 0.83s`
- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q`
  - `199 passed in 0.90s`
- `uv run ruff check fund_agent/fund/source_facts.py fund_agent/fund/data_extractor.py fund_agent/fund/processors/contracts.py tests/fund/test_source_facts.py`
  - `All checks passed!`
- `git diff --check`
  - passed with no output

Not run:

- live/PDF commands
- product CLI
- provider/LLM
- network
- repository/parser/source-helper commands
- re-review
- commit/push/PR/merge/tag/release operations

## Residual Risks / Owner

- Covered by re-review: reviewer must confirm S1-CR-001 is fixed and no derived-view second truth remains.
- Covered by later approved slices: default parsed annual child-level atomic emission remains S2A/S2B.
- Covered by later approved slices: explicit `FundDisclosureDocument` source-truth atomic preservation remains S3.
- Covered by later approved slices: `ChapterFactProvider` and Evidence Confirm bridge fields remain S4/S5.
- Assigned to later exact authorization gates: live/PDF re-evidence, product CLI residuals, release/readiness, tag and release.
- Outside current gate: unrelated dirty/untracked workspace residue.

## Stop Condition

Ready for re-review. Not committed. Release/readiness `NOT_READY`.

S1_FIX_IMPLEMENTED_READY_FOR_REREVIEW_NOT_READY
