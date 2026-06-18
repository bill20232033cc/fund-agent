# MVP Small Golden Set Portfolio Manager Tenure List Additive Extractor Fix Gate Implementation Evidence

## Gate

- Gate: `portfolio_manager_tenure_list.v1 additive extractor fix gate`
- Classification: `standard`
- Date: 2026-06-10
- Role: implementation evidence
- Status: ready for code review

## Accepted Plan

- Plan: `docs/reviews/mvp-small-golden-set-portfolio-manager-tenure-list-additive-extractor-fix-gate-plan-20260610.md`
- Plan review: `docs/reviews/plan-review-20260610-131917.md`
- Plan re-review: `docs/reviews/plan-review-20260610-132022.md`
- Controller judgment: `docs/reviews/mvp-small-golden-set-portfolio-manager-tenure-list-additive-extractor-fix-gate-plan-controller-judgment-20260610.md`
- Accepted plan checkpoint: `025d375`

## Changed Files

- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/manager_ownership.py`
- `tests/fund/extractors/test_manager_ownership.py`
- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- `fund_agent/fund/README.md`

## Implementation Summary

- Added `portfolio_managers` to `ManagerOwnershipExtractionResult`.
- Added `portfolio_manager_tenure_list.v1` extraction to `extract_manager_ownership()`.
- The emitted value contains `schema_version`, `fund_code`, `report_year` and ordered `portfolio_managers` rows.
- Each manager row contains `name`, `role`, `start_date`, optional non-empty `end_date`, and a row-level `source_anchor`.
- Added a current-model fail-closed guard: direct extraction requires a numbered `§4` heading containing both `基金经理` and `简介`.
- Manager roster tables are identified by header semantics, not fixed `table_index`.
- Removed the strict xfail marker from the accepted same-source manager roster test without relaxing assertions.
- Updated `tests/README.md` to describe `portfolio_manager_tenure_list.v1` as passing row-field correctness coverage.
- Updated `fund_agent/fund/README.md` to describe the current extractor output surface without claiming downstream bundle, snapshot, renderer or quality gate integration.

## Boundary Confirmation

- No PDF read.
- No repository/source/cache/fallback/network/live EID/FDR action.
- No provider, live LLM, runtime budget or config change.
- No small-golden fixture mutation or projection.
- No golden/readiness promotion.
- No source orchestration, parser model, score-loop, quality gate, renderer, chapter facts, evidence availability, report evidence, checklist or Service integration.
- No adjacent `risk_characteristic_text.v1`, `bond_top_holding_row.v1` or `target_fund_holding_row.v1` work.

## Validation

| Command | Result |
|---|---|
| `uv run pytest tests/fund/extractors/test_manager_ownership.py -q` | `10 passed` |
| `uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q` | `21 passed, 3 xfailed` |
| `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q` | `42 passed, 3 xfailed` |
| `uv run ruff check fund_agent/fund/extractors/models.py fund_agent/fund/extractors/manager_ownership.py tests/fund/extractors/test_manager_ownership.py tests/fund/test_small_golden_set_extractor_correctness.py` | `All checks passed!` |
| `git diff --check -- fund_agent/fund/extractors/models.py fund_agent/fund/extractors/manager_ownership.py tests/fund/extractors/test_manager_ownership.py tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md fund_agent/fund/README.md` | passed |

## Remaining Xfails

The remaining three xfails in `tests/fund/test_small_golden_set_extractor_correctness.py` belong to other not-yet-implemented future contracts:

- `risk_characteristic_text.v1`
- `bond_top_holding_row.v1`
- `target_fund_holding_row.v1`

## Residual Risk

`ParsedTable` still has no parser-level section ownership metadata. This gate mitigates that by requiring a numbered `§4` manager-roster heading before direct extraction. Parser-level table section ownership remains future work and was not implemented in this gate.
