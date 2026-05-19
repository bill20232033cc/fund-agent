# Code Review - P5-S5 Share Change Hardening - 2026-05-20

## Verdict

PASS after controller fix. No remaining blocking findings.

## Scope Reviewed

- `fund_agent/fund/extractors/holdings_share_change.py`
- `tests/fund/extractors/test_holdings_share_change.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/p5-s5-implementation-20260520.md`

## Findings

### P5-S5-CR1 - A-class fallback ignored other code-specific headers

Severity: blocking

Initial implementation allowed `single_a_class_fallback` when a table had another code-specific header but no current fund-code match. That violated the accepted plan’s “no conflicting code-specific column” condition.

Fix:

- Added `_contains_fund_code(...)`.
- `_select_share_change_value_column(...)` now returns `None` if any value header contains a 6-digit fund code but no exact current-fund match.
- Added regression test `test_extract_holdings_share_change_does_not_fallback_when_other_code_header_exists`.

Status: closed.

## Checks

- `pytest tests/fund/extractors/test_holdings_share_change.py tests/fund/integration/test_p1_sample_matrix.py tests/fund/integration/test_p3_cli_e2e_matrix.py tests/fund/analysis/test_investor_return.py tests/fund/template/test_renderer.py -q`
  - `31 passed`
- `pytest tests/ -q`
  - `195 passed`
- `ruff check .`
  - passed
- `git diff --check`
  - passed

## Controller Notes

- Implementation now fails closed for ambiguous multi-column tables.
- No fund-code suffix or product-name inference is used.
- Exact fund-code table headers remain the strongest same-source signal.
- Single A-class fallback is limited to non-code-specific, non-total ambiguity after total columns are excluded.
- Additional metadata keys are tolerated by investor-return and template tests.

## Next Gate

P5-S5 acceptance / aggregate readiness.
