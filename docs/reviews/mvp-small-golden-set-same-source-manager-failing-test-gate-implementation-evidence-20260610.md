# MVP Small Golden Set Same-source Manager Failing Test Gate Implementation Evidence

## Gate

- Gate: `same-source failing manager test gate for portfolio_manager_tenure_list.v1`
- Classification: `standard`
- Date: 2026-06-10
- Role: implementation evidence
- Status: implementation evidence ready for independent code review

## Controller Self-check

- Current gate / role: this is a test-only implementation gate after the accepted row-shape contract decision gate.
- Source of truth: `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260610.md`, and `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`.
- Scope boundary: only `tests/fund/test_small_golden_set_extractor_correctness.py`, `tests/README.md`, and this evidence artifact were changed.
- Stop conditions: no extractor/source/config/runtime/provider/fallback/live/PDF/FDR/golden/readiness changes were needed.
- Evidence and validation: strict xfail same-source test proves the current manager extractor lacks the accepted future manager roster contract.
- Next action: independent DS/MiMo code review, controller judgment, then control truth sync and local accepted checkpoint if accepted.

## Agent Routing Note

The controller attempted to route implementation to AgentCodex, but the pane did not cleanly clear twice and retained stale prompt output. To avoid blocking a small test-only gate, the controller directly executed this implementation slice and preserved the deviation here. Independent review is still required before acceptance.

## Changes

### `tests/fund/test_small_golden_set_extractor_correctness.py`

- Added `extract_manager_ownership` import.
- Added `MANAGER_CONTRACT_VERSION = "portfolio_manager_tenure_list.v1"`.
- Narrowed generic unsupported same-source residual coverage from `{"manager", "risk"}` to `{"risk"}` because manager now has a dedicated strict xfail contract test.
- Added `_manager_expected_entries()` to read `fields.manager.expected` from the accepted retained excerpt oracle.
- Added `_manager_table()` to build a minimal `§4.1.2 基金经理简介` parsed table using only oracle-retained entries.
- Extended `_build_report_from_oracle_row()` with `include_manager=False` so existing tests are unchanged unless the manager contract test opts in.
- Added strict xfail test `test_manager_extractor_exposes_same_source_portfolio_manager_tenure_list`.

The strict xfail covers all five accepted same-source rows:

- `004393`: 张明, 基金经理, start `2022-08-08`
- `004194`: 蔡振, 基金经理, start `2021-11-05`; 王平, 基金经理（已离任）, start `2017-03-03`, end `2024-12-31`
- `006597`: 陶然, 基金经理, start `2020-07-07`; 丁士恒, 基金经理, start `2020-05-15`
- `110020`: 余海燕, 基金经理, start `2016-04-16`; 庞亚平, 基金经理, start `2022-12-15`
- `017641`: 张军, 基金经理, start `2023-04-06`

Current expected failure mode: `ManagerOwnershipExtractionResult` has no `portfolio_managers` surface. If a future extractor adds that surface, the same test will enforce `schema_version`, fund code, report year, entry count, manager name, role, start date, disclosed end date, and row-level `§4.1.2` source anchor fields.

### `tests/README.md`

- Updated the small-golden test description to state that `portfolio_manager_tenure_list.v1` is currently represented by strict xfail same-source manager roster contract tests, not by passing correctness.

## Validation

| Command | Result |
|---|---|
| `uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q` | `16 passed, 8 xfailed in 0.89s` |
| `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q` | `37 passed, 8 xfailed in 0.45s` |
| `uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py` | `All checks passed!` |
| `git diff --check -- tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md` | passed |

## Boundary Confirmation

- No production extractor code changed.
- No source acquisition changed.
- No fixture projection performed.
- No PDF read, network call, FundDocumentRepository live acquisition, fallback invocation, provider probe, or live LLM run performed.
- No provider/default/runtime/budget/config changed.
- No golden/readiness promotion accepted.

## Residuals

- `portfolio_manager_tenure_list.v1` is still not implemented; this gate only adds same-source failing evidence.
- `risk_characteristic_text.v1`, `bond_top_holding_row.v1`, and `target_fund_holding_row.v1` still need their own same-source failing test gates before any extractor fix.
