# MVP Small Golden Set Same-source Manager Failing Test Gate Controller Judgment

## Gate

- Gate: `same-source failing manager test gate for portfolio_manager_tenure_list.v1`
- Classification: `standard`
- Date: 2026-06-10
- Role: controller judgment
- Status: accepted locally, pending checkpoint commit

## Inputs Reviewed

- Implementation evidence: `docs/reviews/mvp-small-golden-set-same-source-manager-failing-test-gate-implementation-evidence-20260610.md`
- DS review: `docs/reviews/mvp-small-golden-set-same-source-manager-failing-test-gate-code-review-ds-20260610.md`
- MiMo review: `docs/reviews/mvp-small-golden-set-same-source-manager-failing-test-gate-code-review-mimo-20260610.md`
- Test file: `tests/fund/test_small_golden_set_extractor_correctness.py`
- Test documentation: `tests/README.md`

## Controller Verdict

Accepted.

The gate satisfies the accepted row-shape contract sequencing: `portfolio_manager_tenure_list.v1` now has same-source failing evidence before any extractor fix. The implementation remains test-only, uses only the accepted retained excerpt oracle, and does not change extractor/source/config/runtime/provider/fallback/live/PDF/FDR/golden/readiness behavior.

## Review Findings Judgment

### DS Review

Verdict: PASS with three non-blocking notes.

1. `table_index=3` in `_manager_table()`.
   - Judgment: accepted as non-blocking residual.
   - Reason: the helper constructs the third table after profile and performance tables for a future manager extractor contract test. It is inert while the strict xfail fails on the missing `portfolio_managers` surface. The future extractor fix gate must reconcile the table locator with the actual parser/extractor implementation.

2. `_build_report_from_oracle_row()` section offset refactor.
   - Judgment: accepted as safe.
   - Reason: the refactor is test-internal, keeps `include_manager=False` as the default, and current validations preserve all existing passing behavior.

3. `row_locator` substring assertion.
   - Judgment: accepted as intentionally loose for the failing-test gate.
   - Reason: the accepted future contract requires a row-level locator that distinguishes managers; this test enforces name-bearing section-level traceability without over-specifying the implementation's locator format before the extractor fix gate.

### MiMo Review

Verdict: PASS with zero blocking findings.

Judgment: accepted.

Reason: MiMo independently confirmed test-only scope, oracle exclusivity, five-row coverage, contract-shape sufficiency, justified removal of manager from the generic unsupported residual set, README wording, and validation reproduction.

## Validation Accepted

| Command | Accepted Result |
|---|---|
| `uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q` | `16 passed, 8 xfailed` |
| `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q` | `37 passed, 8 xfailed` |
| `uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py` | `All checks passed!` |
| `git diff --check -- tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md docs/reviews/mvp-small-golden-set-same-source-manager-failing-test-gate-implementation-evidence-20260610.md` | passed |

## Boundary Confirmation

- No production extractor code changed.
- No source acquisition changed.
- No fixture projection performed.
- No PDF read, network call, FundDocumentRepository live acquisition, fallback invocation, provider probe, or live LLM run performed.
- No provider/default/runtime/budget/config changed.
- No golden/readiness promotion accepted.
- No PR, push, release, merge or mark-ready action performed.

## Accepted Current Fact

`portfolio_manager_tenure_list.v1` is now represented by strict xfail same-source failing tests over all five accepted small-golden rows. This is not a passing correctness result and does not mean the manager roster extractor is implemented.

## Next Entry

Recommended next entry: `portfolio_manager_tenure_list.v1 additive extractor fix gate`, scoped to making the accepted same-source manager failing test pass without changing source/fallback/golden/readiness/provider/runtime boundaries.

Valid alternatives if the controller chooses to defer manager implementation:

- same-source failing risk test gate for `risk_characteristic_text.v1`;
- same-source failing `006597` bond holding test gate for `bond_top_holding_row.v1`;
- same-source failing `110020` target ETF holding test gate for `target_fund_holding_row.v1`;
- separate non-extractor phase.
