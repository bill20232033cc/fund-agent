# MVP Small Golden Set Bond Top Holding Row Additive Extractor Fix Gate Code Review - 2026-06-10

## Scope Reviewed

- `fund_agent/fund/extractors/holdings_share_change.py`
- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-bond-top-holding-row-additive-extractor-fix-gate-implementation-evidence-20260610.md`

## Findings

No blocking findings.

## Review Notes

- The implementation is additive: it adds `bond_top_holdings` and related contract metadata only when a bond top holding table is detected.
- The implementation keeps bond rows separate from stock `top_holdings`, preserving existing equity-like tests.
- The source anchor is row-scoped and same-source, using the table page/table id and a row locator containing the bond code and name.
- The test now converts the accepted strict xfail into a passing assertion, while the target-fund holding xfail remains.
- README updates describe current behavior and explicitly keep downstream integration out of current scope.

## Verification Reviewed

- `uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q` -> `23 passed, 1 xfailed`.
- `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q` -> `44 passed, 1 xfailed`.
- `uv run pytest tests/fund/test_data_extractor.py -q` -> `10 passed`.
- `uv run ruff check fund_agent/fund/extractors/holdings_share_change.py tests/fund/test_small_golden_set_extractor_correctness.py` -> passed.
- `git diff --check -- ...` -> passed.

## Residual Risk

- Current downstream consumers do not project `bond_top_holdings`; this is intentional and should be handled only by a separately authorized integration gate.
