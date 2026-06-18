# MVP Small Golden Set Bond Top Holding Row Same-Source Failing Test Gate Code Review - 2026-06-10

## Scope Reviewed

- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-bond-top-holding-row-same-source-failing-test-gate-implementation-evidence-20260610.md`

## Findings

No blocking findings.

## Review Notes

- The new `006597` bond row test is a strict xfail and therefore records the accepted future contract gap without changing current passing extractor semantics.
- The test uses only the accepted retained excerpt oracle and synthesizes the minimal parsed annual report in-memory; it does not read PDF, repository, source helpers, provider, fallback or network.
- The previous generic unsupported holdings xfail was narrowed so `110020` remains separately blocked for `target_fund_holding_row.v1`.
- Existing passing risk-characteristic and equity-like holdings assertions remain intact.

## Verification Reviewed

- `uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q` -> `22 passed, 2 xfailed`.
- `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q` -> `43 passed, 2 xfailed`.
- `uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py` -> passed.
- `git diff --check -- ...` -> passed.

## Residual Risk

- The bond output surface is intentionally not implemented in this gate. A future additive extractor fix gate must decide the production shape and update the strict xfail to a passing same-source correctness assertion.
