# Same-source Manager Failing Test Gate Code Review — MiMo

## Gate

- Gate: `same-source failing manager test gate for portfolio_manager_tenure_list.v1`
- Classification: `standard`
- Date: 2026-06-10
- Role: independent code review (MiMo)
- Reviewer scope: `tests/fund/test_small_golden_set_extractor_correctness.py`, `tests/README.md`, `docs/reviews/mvp-small-golden-set-same-source-manager-failing-test-gate-implementation-evidence-20260610.md`

## Verdict

**PASS** — zero blocking findings.

## Validation Reproduction

| Command | Expected | Actual |
|---|---|---|
| `uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q` | 16 passed, 8 xfailed | 16 passed, 8 xfailed ✓ |
| `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q` | 37 passed, 8 xfailed | 37 passed, 8 xfailed ✓ |
| `uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py` | All checks passed | All checks passed ✓ |
| `git diff --check -- tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md` | no output | no output ✓ |

## Scope Verification

### 1. Test-only, no behavior changes

Confirmed. The diff touches only:
- `tests/fund/test_small_golden_set_extractor_correctness.py` — adds imports, constants, helper functions, one new test, and refactors `_build_report_from_oracle_row` to support conditional `include_manager` parameter.
- `tests/README.md` — one-line wording update.

No `fund_agent/**` source, config, runtime, provider, fixture, golden, readiness, or design/control files were modified.

### 2. No extractor/source/config/runtime/provider/fallback/live/PDF/FDR/golden/readiness behavior changed

Confirmed. The new test imports `extract_manager_ownership` (existing production surface) but only calls it within a `strict xfail` test that is expected to fail. No production code was touched. No PDF read, network call, `FundDocumentRepository`, fallback, provider probe, fixture projection, or golden/readiness promotion occurs.

### 3. Strict xfail manager test uses only accepted retained excerpt oracle and covers all five rows

Confirmed. The test `test_manager_extractor_exposes_same_source_portfolio_manager_tenure_list` is parametrized over `sorted(EXPECTED_ACCEPTED_FUND_CODES)` = `{"004393", "004194", "006597", "110020", "017641"}`, covering all five accepted rows. It reads expected entries from `_manager_expected_entries(row)` which sources from `_expected(row, "manager")` — the `fields.manager.expected` array in the accepted retained excerpt oracle at `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`. No other oracle source is used.

### 4. Contract shape sufficiency for future fix

Confirmed. The test at lines 755-794 asserts:
- `schema_version` == `"portfolio_manager_tenure_list.v1"` (line 780)
- `fund_code` == fund code (line 781)
- `report_year` == 2024 (line 782)
- `portfolio_managers` is a non-empty list with correct entry count (line 783-784)
- Each entry: `name`, `role`, `start_date` exact match (lines 786-788)
- `end_date` asserted when present in oracle — specifically covers 004194 Wang Ping `end_date="2024-12-31"` (lines 789-790)
- Source anchor: `section_id == "§4"`, `"4.1.2" in section_title`, manager name in `row_locator` (lines 791-793)
- `portfolio_managers.anchors` is truthy (line 794)

This covers all required and optional fields from the accepted `portfolio_manager_tenure_list.v1` contract as specified in `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260610.md` §Contract 1.

### 5. `SAME_SOURCE_UNSUPPORTED_FIELDS` narrowing is justified

Confirmed. The change from `{"manager", "risk"}` to `{"risk"}` at line 77 is correct because `manager` now has its own dedicated strict xfail test (`test_manager_extractor_exposes_same_source_portfolio_manager_tenure_list`) that covers the full contract shape. Keeping `manager` in `SAME_SOURCE_UNSUPPORTED_FIELDS` would create duplicate xfail coverage and would not match the accepted row-shape contract decision gate sequencing (manager → risk → bond → target ETF).

### 6. README wording does not claim manager passing correctness

Confirmed. The updated README line 29 states: "`portfolio_manager_tenure_list.v1` 当前仅有 strict xfail same-source manager roster contract test，不是 passing correctness". This explicitly disclaims passing status.

### 7. Refactoring of `_build_report_from_oracle_row`

The refactoring (lines 465-563) replaces hardcoded section offset computation with a dynamic `section_starts` / `section_ends` dictionary approach and moves section construction into a conditional block. This is a clean refactor that:
- Makes section offset computation consistent and data-driven
- Enables the `include_manager=False` default to produce identical output for existing tests (verified by 16 passed + 8 xfailed unchanged)
- Avoids code duplication when adding future conditional sections

The `include_manager` parameter defaults to `False`, so all existing tests that call `_build_report_from_oracle_row(row)` or `_build_report_from_oracle_row(row, include_holdings=True)` produce the same parsed report as before.

## Findings

### Severity: None (informational only)

No blocking or non-blocking findings.

## Residual Risk

- `portfolio_manager_tenure_list.v1` is still not implemented; this gate only adds same-source failing evidence. The test will xfail until a future extractor fix adds `portfolio_managers` surface to `extract_manager_ownership()`.
- `risk_characteristic_text.v1`, `bond_top_holding_row.v1`, and `target_fund_holding_row.v1` still need their own same-source failing test gates.
- The `_build_report_from_oracle_row` refactoring changes internal section offset computation from hardcoded to dynamic; while functionally equivalent for current callers (verified by unchanged test results), future reviewers adding new conditional sections should follow the same `section_starts` dictionary pattern.
