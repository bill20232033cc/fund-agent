# MVP Small Golden Set Bond Top Holding Row Same-Source Failing Test Gate Implementation Evidence - 2026-06-10

## Gate

- Gate: `bond_top_holding_row.v1` same-source failing test gate.
- Classification: `standard`.
- Accepted plan: `docs/reviews/mvp-small-golden-set-bond-top-holding-row-same-source-failing-test-gate-plan-20260610.md`.
- Accepted plan review: `docs/reviews/plan-review-20260610-152453.md`.
- Accepted plan judgment: `docs/reviews/mvp-small-golden-set-bond-top-holding-row-same-source-failing-test-gate-controller-judgment-20260610.md`.

## Implemented Scope

- Added a dedicated strict xfail test for accepted oracle row `006597 / 2024 / top_bond_table_row`.
- The test defines the future additive output surface as `bond_top_holding_row.v1` and asserts:
  - `schema_version = bond_top_holding_row.v1`;
  - `fund_code = 006597`;
  - `report_year = 2024`;
  - first `bond_top_holdings` row fields `code`, `name`, `fair_value_cny`, `net_asset_ratio`;
  - same-source `source_anchor` from `§8` / `前五名债券投资明细`;
  - anchor row locator includes `230214` and `23国开14`.
- Split the prior generic unsupported holdings xfail so `110020 / target_etf_holding` remains separately blocked.
- Updated `tests/README.md` to describe the dedicated bond strict xfail and the remaining target-fund future contract gap.

## Explicit Non-Scope

- No production extractor behavior changed.
- No `StructuredFundDataBundle`, snapshot, score, quality gate, report evidence, chapter facts, renderer, checklist, Service, Host or Agent runtime integration changed.
- No fixture projection, golden/readiness promotion, source/fallback/provider/runtime/config behavior, PDF/FDR/network/live LLM, endpoint probe, release, merge or PR-ready state changed.

## Validation

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Result:

```text
22 passed, 2 xfailed in 0.43s
```

```bash
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Result:

```text
43 passed, 2 xfailed in 0.43s
```

```bash
uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py
```

Result:

```text
All checks passed!
```

```bash
git diff --check -- tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md docs/reviews/mvp-small-golden-set-bond-top-holding-row-same-source-failing-test-gate-plan-20260610.md docs/reviews/mvp-small-golden-set-bond-top-holding-row-same-source-failing-test-gate-controller-judgment-20260610.md docs/reviews/plan-review-20260610-152453.md
```

Result: passed with no output.

## Residuals

- `bond_top_holding_row.v1` remains a strict xfail and has not been implemented as an extractor output surface.
- `target_fund_holding_row.v1` remains blocked as a strict xfail for `110020`.
- Downstream integration for accepted extractor surfaces remains a separate authorization boundary.
