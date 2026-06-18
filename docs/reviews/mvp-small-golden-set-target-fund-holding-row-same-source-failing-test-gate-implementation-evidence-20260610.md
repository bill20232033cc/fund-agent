# MVP Small Golden Set Target Fund Holding Row Same-Source Failing Test Gate Implementation Evidence - 2026-06-10

## Gate

- Gate: `target_fund_holding_row.v1` same-source failing test gate.
- Classification: `standard`.
- Accepted plan checkpoint: `478dd56`.
- Plan artifact: `docs/reviews/mvp-small-golden-set-target-fund-holding-row-same-source-failing-test-gate-plan-20260610.md`.
- Plan review: `docs/reviews/plan-review-20260610-164350.md`.
- Controller judgment: `docs/reviews/mvp-small-golden-set-target-fund-holding-row-same-source-failing-test-gate-controller-judgment-20260610.md`.

## Implemented Scope

- Replaced the remaining generic target-fund xfail with a dedicated strict xfail for `110020 / 2024 / target_etf_holding`.
- Added a test-local minimal `§8.2 期末投资目标基金明细` table built only from the accepted retained excerpt oracle.
- The dedicated strict xfail defines the future `target_fund_holding_row.v1` output surface:
  - `schema_version`;
  - `fund_code = 110020`;
  - `report_year = 2024`;
  - non-empty `target_fund_holdings`;
  - first row `name`, `fair_value_cny`, `net_asset_ratio`, and `source_anchor`.
- The test explicitly does not require `code` because the accepted oracle does not contain a target ETF code.

## Explicit Non-Scope

- No production extractor behavior changed.
- No `target_fund_holding_row.v1` implementation.
- No PDF read, repository access, source helper, fallback, provider, network or live LLM.
- No fixture projection and no golden/readiness promotion.
- No downstream bundle/snapshot/report/quality integration.

## Validation

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Result:

```text
23 passed, 1 xfailed in 0.67s
```

```bash
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Result:

```text
44 passed, 1 xfailed in 0.42s
```

```bash
uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py
```

Result:

```text
All checks passed!
```

```bash
git diff --check -- tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md docs/reviews/mvp-small-golden-set-target-fund-holding-row-same-source-failing-test-gate-plan-20260610.md docs/reviews/plan-review-20260610-164350.md docs/reviews/mvp-small-golden-set-target-fund-holding-row-same-source-failing-test-gate-controller-judgment-20260610.md
```

Result: passed with no output.

## Residuals

- `target_fund_holding_row.v1` remains a strict xfail and has not been implemented as an extractor output surface.
- A future additive extractor fix gate must convert this strict xfail into a passing same-source correctness assertion.
