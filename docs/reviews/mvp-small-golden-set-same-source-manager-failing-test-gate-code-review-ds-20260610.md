# MVP Small Golden Set Same-source Manager Failing Test Gate — Code Review (DS)

## Gate

- Gate: `same-source failing manager test gate for portfolio_manager_tenure_list.v1`
- Classification: `standard`
- Date: 2026-06-10
- Role: DS independent code reviewer
- Review target: `tests/fund/test_small_golden_set_extractor_correctness.py`, `tests/README.md`, and implementation evidence at `docs/reviews/mvp-small-golden-set-same-source-manager-failing-test-gate-implementation-evidence-20260610.md`

## Verdict: PASS

Zero blocking findings. The gate is test-only, scoped correctly, and all validation evidence reproduces cleanly.

## Source of Truth Cross-check

- `AGENTS.md` — hard constraints obeyed: no production code modified, no `FundDocumentRepository` bypass, no fallback involved, no `extra_payload` introduced, all parameters explicit.
- `docs/current-startup-packet.md` — next entry point for same-source failing manager test gate respected. No extractor/config/runtime/provider/live/PDF/FDR/golden/readiness behavior changed.
- `docs/implementation-control.md` — row-shape contract decision gate closeout states four accepted future contracts; this gate correctly implements only the first (manager) failing test, leaving the other three for later gates.
- `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260610.md` — Contract 1 (`portfolio_manager_tenure_list.v1`) required fields, optional fields, normalization rules, source anchor requirements, and expected oracle mapping are all faithfully reflected in the new test.
- `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json` — the oracle is the sole data source for all assertions. No synthetic fixture, PDF, network, or external source is consulted.

## Findings

### Non-blocking

1. **`tests/fund/test_small_golden_set_extractor_correctness.py:356` — `_manager_table` hardcodes `table_index=3`**

   This is a forward-looking assumption about the future extractor's table indexing. Since the test is strict xfail and cannot pass with the current extractor (which lacks `portfolio_managers`), the value is inert for now. The future extractor fix gate will need to reconcile this index against the actual implementation. Not a correctness issue at this gate.

2. **`tests/fund/test_small_golden_set_extractor_correctness.py:446–563` — `_build_report_from_oracle_row` refactored section offset computation**

   The function was refactored from hardcoded local-variable-based offsets (`section_two_start`, `section_three_start`, `section_eight_start`) to a generalized dictionary-based approach that also handles conditional `§4`. All 16 existing passing tests continue to pass, confirming no regression. The refactoring is test-internal only and improves maintainability. Worth noting because it touches a shared helper; the validation evidence confirms the change is safe.

3. **`tests/fund/test_small_golden_set_extractor_correctness.py:793` — `row_locator` uses substring match**

   The assertion `expected_entry["name"] in actual_entry["source_anchor"]["row_locator"]` is a substring inclusion check, not an exact match. For a strict xfail contract test, this is appropriately loose — it verifies the row can be traced to the correct manager without over-specifying the locator format. When the extractor fix gate opens, the locator format should be tightened in the implementation contract, not in this test.

### No findings on these items

- **Extractor/source/config/runtime behavior**: confirmed unchanged. Only `tests/fund/test_small_golden_set_extractor_correctness.py` and `tests/README.md` were modified.
- **Oracle exclusivity**: the new test reads only `fields.manager.expected` and `fields.manager.anchor` from the retained excerpt oracle. No PDF, network, FDR, fallback, or provider access.
- **All five rows covered**: `@pytest.mark.parametrize("fund_code", sorted(EXPECTED_ACCEPTED_FUND_CODES))` covers `004393`, `004194`, `006597`, `110020`, `017641`.
- **Shape coverage**:
  - `schema_version` → `portfolio_manager_tenure_list.v1` ✓
  - `fund_code` → exact match ✓
  - `report_year` → `2024` ✓
  - manager entry count → `len(actual_entries) == len(expected_entries)` with `strict=True` zip ✓
  - `name`, `role`, `start_date` per entry ✓
  - `end_date` when present → `if "end_date" in expected_entry` covers `004194` 王平 `end_date=2024-12-31` ✓
  - source anchor `section_id == "§4"` and `"4.1.2" in section_title` and `name in row_locator` ✓
  - top-level `portfolio_managers.anchors` truthy ✓
- **`SAME_SOURCE_UNSUPPORTED_FIELDS` change**: narrowing from `{"manager", "risk"}` to `{"risk"}` is justified. Manager is now covered by a dedicated strict xfail contract test (`test_manager_extractor_exposes_same_source_portfolio_manager_tenure_list`), so it should not also appear in the generic unsupported gap test. Risk remains in the set pending its own dedicated test gate.
- **README wording**: line 29 correctly states `portfolio_manager_tenure_list.v1` 当前仅有 strict xfail same-source manager roster contract test，不是 passing correctness`. No claim of passing correctness.
- **`include_manager=False` default**: existing tests are unchanged. Only the new manager test opts in with `include_manager=True`.

## Validation Evidence Reproduction

All four validation commands reproduced cleanly:

| Command | Observed Result | Expected |
|---|---|---|
| `uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q` | `16 passed, 8 xfailed in 0.82s` | Match |
| `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q` | `37 passed, 8 xfailed in 0.52s` | Match |
| `uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py` | `All checks passed!` | Match |
| `git diff --check -- tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md` | no output | Match |

xfail breakdown (8 total):
- 5 × `test_manager_extractor_exposes_same_source_portfolio_manager_tenure_list` — one per fund code, strict xfail because `ManagerOwnershipExtractionResult` has no `portfolio_managers` surface
- 1 × `test_same_source_fields_without_current_row_consumer_are_blocked_gaps[risk]` — risk contract not yet tested
- 2 × `test_same_source_holdings_rows_outside_equity_like_subset_remain_blocked` — `006597` bond, `110020` target ETF

## Residual Risk

- `table_index=3` in `_manager_table()`: when the extractor fix gate opens, the actual table index consumed by the future manager extractor must be reconciled. This is a forward-looking assumption in test-only code; it does not affect current correctness.
- The `row_locator` format is verified only by substring inclusion of the manager name. When the extractor fix is implemented, the locator contract should define a stable format (e.g., table row index, paragraph offset, or name-anchored line number).
- The other three accepted future contracts (`risk_characteristic_text.v1`, `bond_top_holding_row.v1`, `target_fund_holding_row.v1`) remain without dedicated failing tests. Their absence from this gate is intentional per the sequencing plan.

## Boundary Confirmation

- Zero production code changed.
- Zero source acquisition, PDF read, network call, FDR live acquisition, or fallback invocation.
- Zero fixture projection or golden/readiness promotion.
- Zero provider/default/runtime/budget/config change.
- Test file changes are additive and backward-compatible: `include_manager=False` default preserves all existing test behavior.
