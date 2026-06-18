# MVP Small Golden Set Bond Top Holding Row Additive Extractor Fix Gate Plan - 2026-06-10

## Goal

Implement the already accepted `bond_top_holding_row.v1` same-source contract as an additive holdings extractor output surface.

## Direct Evidence

- Current control truth says `bond_top_holding_row.v1` has a dedicated strict xfail for `006597 / 2024 / top_bond_table_row`.
- The accepted oracle is `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`.
- The strict xfail asserts the row fields `code`, `name`, `fair_value_cny`, `net_asset_ratio` and a same-source `§8` / `前五名债券投资明细` source anchor.

## Scope

Allowed files:

- `fund_agent/fund/extractors/holdings_share_change.py`
- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- gate evidence/review artifacts under `docs/reviews/`
- truth sync docs after implementation acceptance: `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/design.md`

## Non-Goals

- No PDF read, repository access, source helper, fallback, provider, network or live LLM.
- No fixture projection and no golden/readiness promotion.
- No downstream wiring into `StructuredFundDataBundle`, extraction snapshot, score, quality gate, renderer, checklist, Service, Host or Agent runtime.
- No implementation for `target_fund_holding_row.v1`; that is the next gate.

## Implementation Decisions

- Add a dedicated bond table detector for `§8` bond top holding tables using headers/text containing `债券代码`, `债券名称`, `公允价值`, and `占基金资产净值比例`.
- Extract rows into a new `bond_top_holdings` list, not into stock `top_holdings`.
- Emit `schema_version = bond_top_holding_row.v1`, `fund_code`, and `report_year` only when a bond top holding table is detected.
- Each bond row must include `code`, `name`, `fair_value_cny`, `net_asset_ratio`, and `source_anchor`.
- `source_anchor` must be a serializable dict with `section_id`, `section_title`, `page_number`, `table_id`, and `row_locator`.
- Preserve existing stock holdings and industry fields and their statuses.
- When only a bond top holding table exists, `holdings_snapshot` must be `direct` instead of `missing`.

## Tests And Validation

Required validation:

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_data_extractor.py -q
uv run ruff check fund_agent/fund/extractors/holdings_share_change.py tests/fund/test_small_golden_set_extractor_correctness.py
git diff --check -- fund_agent/fund/extractors/holdings_share_change.py tests/fund/test_small_golden_set_extractor_correctness.py fund_agent/fund/README.md tests/README.md docs/reviews/mvp-small-golden-set-bond-top-holding-row-additive-extractor-fix-gate-*.md
```

Expected:

- Focused row-field test count loses one xfail: `23 passed, 1 xfailed`.
- Small-golden family loses one xfail: `44 passed, 1 xfailed`.
- Remaining xfail belongs to `target_fund_holding_row.v1`.

## Stop Conditions

- Stop if the bond test XPASSes before implementation.
- Stop if implementing the bond row requires changing source acquisition, fallback, fixture, golden/readiness, or downstream bundle/report behavior.
- Stop if existing equity-like holdings assertions regress.
