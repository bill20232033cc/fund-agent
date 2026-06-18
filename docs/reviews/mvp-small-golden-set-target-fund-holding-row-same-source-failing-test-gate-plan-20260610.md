# MVP Small Golden Set Target Fund Holding Row Same-Source Failing Test Gate Plan - 2026-06-10

## Goal

Replace the remaining generic unsupported-holdings xfail with a dedicated strict xfail for `110020 / 2024 / target_etf_holding`.

## Direct Evidence

- Current control truth lists the next entry as same-source failing `110020` target ETF holding test gate for `target_fund_holding_row.v1`.
- Accepted oracle: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`.
- Oracle row:
  - fund code: `110020`;
  - anchor: `PDF p64 §8.2 期末投资目标基金明细`;
  - expected target ETF holding fields: `name`, `fair_value_cny`, `net_asset_ratio`.

## Scope

Allowed files:

- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- gate evidence/review artifacts under `docs/reviews/`
- truth sync docs after implementation acceptance: `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/design.md`

## Non-Goals

- No production extractor behavior change.
- No `target_fund_holding_row.v1` implementation.
- No PDF read, repository access, source helper, fallback, provider, network or live LLM.
- No fixture projection and no golden/readiness promotion.
- No downstream bundle/snapshot/report/quality integration.

## Implementation Decisions

- Add `TARGET_FUND_HOLDING_CONTRACT_VERSION = "target_fund_holding_row.v1"`.
- Replace the generic `TARGET_FUND_UNSUPPORTED_HOLDINGS_ROWS` parameterized xfail with a named strict xfail test.
- Build an in-memory minimal `§8.2 期末投资目标基金明细` table from the accepted oracle.
- Assert future output surface:
  - `schema_version`;
  - `fund_code = 110020`;
  - `report_year = 2024`;
  - non-empty `target_fund_holdings`;
  - first row `name`, `fair_value_cny`, `net_asset_ratio`, and source anchor.
- Do not assert any target ETF code because the accepted oracle does not contain one.

## Tests And Validation

Required validation:

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py
git diff --check -- tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md docs/reviews/mvp-small-golden-set-target-fund-holding-row-same-source-failing-test-gate-*.md docs/reviews/plan-review-20260610-164350.md
```

Expected:

- Focused row-field tests stay `23 passed, 1 xfailed`.
- Small-golden family stays `44 passed, 1 xfailed`.
- The single xfail is the named `target_fund_holding_row.v1` same-source failing test.

## Stop Conditions

- Stop if the target-fund test XPASSes unexpectedly.
- Stop if writing the test requires production extractor changes.
- Stop if existing bond/equity-like holdings assertions regress.
