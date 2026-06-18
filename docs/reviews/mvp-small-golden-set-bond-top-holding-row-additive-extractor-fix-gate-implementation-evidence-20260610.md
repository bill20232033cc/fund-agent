# MVP Small Golden Set Bond Top Holding Row Additive Extractor Fix Gate Implementation Evidence - 2026-06-10

## Gate

- Gate: `bond_top_holding_row.v1` additive extractor fix gate.
- Classification: `heavy` because it adds a public Fund extractor output field.
- Accepted plan checkpoint: `9cb1fb3`.
- Plan artifact: `docs/reviews/mvp-small-golden-set-bond-top-holding-row-additive-extractor-fix-gate-plan-20260610.md`.
- Plan review: `docs/reviews/plan-review-20260610-154924.md`.
- Controller judgment: `docs/reviews/mvp-small-golden-set-bond-top-holding-row-additive-extractor-fix-gate-controller-judgment-20260610.md`.

## Implemented Scope

- `fund_agent/fund/extractors/holdings_share_change.py` now detects `§8` bond top holding tables by explicit bond table headers.
- `holdings_snapshot.value` now additively exposes:
  - `schema_version = bond_top_holding_row.v1`;
  - `fund_code`;
  - `report_year`;
  - `bond_top_holdings`.
- Each `bond_top_holdings` row contains `code`, `name`, `fair_value_cny`, `net_asset_ratio`, and a serializable `source_anchor`.
- The existing stock `top_holdings` semantics are preserved and are not reused for bond rows.
- The dedicated `006597` strict xfail is now a passing same-source correctness assertion.
- `fund_agent/fund/README.md` and `tests/README.md` were updated for current behavior.

## Explicit Non-Scope

- No PDF read, repository access, source helper, fallback, provider, network or live LLM.
- No fixture projection and no golden/readiness promotion.
- No downstream wiring into `StructuredFundDataBundle`, extraction snapshot, score, quality gate, renderer, checklist, Service, Host or Agent runtime.
- No `target_fund_holding_row.v1` implementation.

## Validation

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Result:

```text
23 passed, 1 xfailed in 0.73s
```

```bash
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Result:

```text
44 passed, 1 xfailed in 0.46s
```

```bash
uv run pytest tests/fund/test_data_extractor.py -q
```

Result:

```text
10 passed in 0.38s
```

```bash
uv run ruff check fund_agent/fund/extractors/holdings_share_change.py tests/fund/test_small_golden_set_extractor_correctness.py
```

Result:

```text
All checks passed!
```

```bash
git diff --check -- fund_agent/fund/extractors/holdings_share_change.py tests/fund/test_small_golden_set_extractor_correctness.py fund_agent/fund/README.md tests/README.md docs/reviews/mvp-small-golden-set-bond-top-holding-row-additive-extractor-fix-gate-plan-20260610.md docs/reviews/plan-review-20260610-154924.md docs/reviews/mvp-small-golden-set-bond-top-holding-row-additive-extractor-fix-gate-controller-judgment-20260610.md
```

Result: passed with no output.

## Residuals

- `bond_top_holding_row.v1` is an extractor output surface only.
- Downstream bundle/snapshot/report/quality integration remains separate.
- The remaining strict xfail belongs to `target_fund_holding_row.v1`.
