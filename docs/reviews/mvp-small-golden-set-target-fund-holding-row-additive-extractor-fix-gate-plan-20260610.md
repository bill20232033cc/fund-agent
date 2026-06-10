# MVP Small Golden Set Target Fund Holding Row Additive Extractor Fix Gate Plan - 2026-06-10

## Goal

Implement the already accepted `target_fund_holding_row.v1` same-source contract as an additive holdings extractor output surface.

## Direct Evidence

- Current control truth says `target_fund_holding_row.v1` has a dedicated strict xfail for `110020 / 2024 / target_etf_holding`.
- The accepted oracle is `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`.
- The strict xfail asserts row fields `name`, `fair_value_cny`, `net_asset_ratio` and a same-source `§8` / `期末投资目标基金明细` source anchor.
- The accepted oracle does not contain target ETF code, so this gate must not assert or infer code.

## Scope

Allowed files:

- `fund_agent/fund/extractors/holdings_share_change.py`
- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/fund/extractors/test_holdings_share_change.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- gate evidence/review artifacts under `docs/reviews/`
- truth sync docs after implementation acceptance: `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/design.md`

## Non-Goals

- No PDF read, repository access, source helper, fallback, provider, network or live LLM.
- No fixture projection and no golden/readiness promotion.
- No downstream wiring into `StructuredFundDataBundle`, extraction snapshot, score, quality gate, renderer, checklist, Service, Host or Agent runtime.
- No target ETF code extraction, code inference, or lookup from tracking error, benchmark, fund name or external ETF metadata.
- No changes to existing stock `top_holdings`, bond `bond_top_holdings`, industry distribution or share-change semantics.

## Implementation Decisions

- Add a dedicated target-fund holding table detector for `§8` target fund tables using headers/text containing `基金名称`, `公允价值`, and `占基金资产净值比例`.
- Extract rows into a new `target_fund_holdings` list, not into stock `top_holdings` and not into bond `bond_top_holdings`.
- Emit `schema_version = target_fund_holding_row.v1`, `fund_code`, and `report_year` only when a target-fund holding table is detected.
- Each target-fund row must include `name`, `fair_value_cny`, `net_asset_ratio`, and `source_anchor`.
- `source_anchor` must be a serializable dict with `section_id`, `section_title`, `page_number`, `table_id`, and `row_locator`.
- Preserve existing stock holdings, bond holdings, industry fields and their statuses.
- When only a target-fund holding table exists, `holdings_snapshot` must be `direct` instead of `missing`.
- Remove the strict xfail marker only for `test_holdings_extractor_exposes_same_source_target_fund_holding_row`.

## Tests And Validation

Required validation:

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/extractors/test_holdings_share_change.py tests/fund/test_data_extractor.py -q
uv run ruff check fund_agent/fund/extractors/holdings_share_change.py tests/fund/test_small_golden_set_extractor_correctness.py tests/fund/extractors/test_holdings_share_change.py
git diff --check -- fund_agent/fund/extractors/holdings_share_change.py tests/fund/test_small_golden_set_extractor_correctness.py tests/fund/extractors/test_holdings_share_change.py fund_agent/fund/README.md tests/README.md docs/reviews/mvp-small-golden-set-target-fund-holding-row-additive-extractor-fix-gate-*.md
```

Expected:

- Focused row-field test count loses the final xfail: all focused row-field tests pass.
- Small-golden family loses the final xfail: all small-golden family tests pass.
- Holdings extractor unit tests pass and show target-fund-only tables produce a direct `holdings_snapshot`.

## Stop Conditions

- Stop if implementing the target-fund row requires changing source acquisition, fallback, fixture, golden/readiness, or downstream bundle/report behavior.
- Stop if the accepted oracle cannot support row fields without inference.
- Stop if existing equity-like or bond holdings assertions regress.
- Stop if a target ETF code is required by any new assertion.
