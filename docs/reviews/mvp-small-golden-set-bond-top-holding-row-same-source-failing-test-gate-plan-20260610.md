# bond_top_holding_row.v1 same-source failing test gate plan

## 1. Gate Metadata

- Gate: `same-source failing 006597 bond holding test gate for bond_top_holding_row.v1`
- Classification: `standard`
- Controller baseline: branch `feat/mvp-llm-incomplete-run-artifacts`; current accepted control sync `6aa2dea`
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, accepted retained excerpt oracle `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`

## 2. Goal

Replace the generic unsupported-holdings xfail for `006597` with a named, strict, same-source failing test for `bond_top_holding_row.v1`.

The test must prove a precise current gap: the retained oracle and a same-source minimal `§8.6` bond holdings table contain the first bond holding row, but the current holdings extractor has no dedicated bond top holding output surface.

## 3. Non-goals

- Do not modify production extractor code.
- Do not add `bond_top_holdings` or `bond_top_holding_row.v1` to the production holdings extractor.
- Do not reuse stock `top_holdings` as the bond holding acceptance surface.
- Do not route this through `bond_risk_evidence`.
- Do not touch `target_fund_holding_row.v1` beyond preserving its current blocked strict xfail.
- Do not integrate anything into `StructuredFundDataBundle`, snapshot, score, quality gate, report evidence, chapter facts, renderer, checklist, Service, Host or Agent runtime.
- Do not read PDFs, call `FundDocumentRepository`, use cache/source helpers, invoke fallback, access network, run provider/live LLM, project fixtures, promote golden/readiness state, or change source/provider/runtime/config behavior.

## 4. Direct Evidence

- `docs/current-startup-packet.md` and `docs/implementation-control.md` list same-source failing `006597` bond holding test gate for `bond_top_holding_row.v1` as a valid next entry.
- `docs/design.md` says `bond_top_holding_row.v1` remains unimplemented and must be tested before any extractor fix.
- The accepted row-shape contract decision states that `006597` `top_bond_table_row` maps to additive `holdings_snapshot.value["bond_top_holdings"]`, not stock `top_holdings`, and must not assert `rank` because the retained oracle has no rank value.
- The accepted oracle contains:
  - `code`: `230214`
  - `name`: `23国开14`
  - `fair_value_cny`: `1,133,300,622.22`
  - `net_asset_ratio`: `9.00%`
  - anchor: `PDF p61 §8.6 前五名债券投资明细`
- Current `tests/fund/test_small_golden_set_extractor_correctness.py` still has generic `UNSUPPORTED_HOLDINGS_ROWS = {"006597": "top_bond_table_row", "110020": "target_etf_holding"}` and one parameterized strict xfail for both row shapes.

## 5. Affected Files

Allowed implementation files:

- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-bond-top-holding-row-same-source-failing-test-gate-*.md`

Allowed truth sync files after accepted implementation:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md`

No production `fund_agent/` file is in scope.

## 6. Contract Decisions For This Test Gate

The future output expected by the test is:

```python
holdings_snapshot.value == {
    "schema_version": "bond_top_holding_row.v1",
    "fund_code": "006597",
    "report_year": 2024,
    "bond_top_holdings": [
        {
            "code": "230214",
            "name": "23国开14",
            "fair_value_cny": "1,133,300,622.22",
            "net_asset_ratio": "9.00%",
            "source_anchor": {
                "section_id": "§8",
                "section_title": <contains "8.6" or "前五名债券投资明细">,
                "page_number": 61,
                "table_id": <table id or equivalent>,
                "row_locator": <contains "230214" and "23国开14">,
            },
        }
    ],
}
```

Test constraints:

- Must not assert `rank`.
- Must not require `quantity` or `bond_type`.
- Must assert `holdings_snapshot.extraction_mode == "direct"` and non-empty anchors.
- Must construct a minimal parsed report with an explicit `§8.6 前五名债券投资明细` table derived only from the accepted oracle.
- Must fail today because current `extract_holdings_share_change(report).holdings_snapshot` has no dedicated bond top holding surface.

## 7. Implementation Slices

### Slice 1: Split bond xfail from generic unsupported holdings xfail

- Add `BOND_TOP_HOLDING_CONTRACT_VERSION = "bond_top_holding_row.v1"`.
- Add `TARGET_FUND_UNSUPPORTED_HOLDINGS_ROWS = {"110020": "target_etf_holding"}` or equivalent naming.
- Add `_bond_top_holding_expected_row(row)` helper for `006597`.
- Add `_bond_top_holding_table(row)` helper that creates a minimal `ParsedTable` with explicit headers for `§8.6` bond investment details.
- Add `include_bond_holdings` to the test report builder or build the bond report in the test with the helper.
- Add `test_holdings_extractor_exposes_same_source_bond_top_holding_row` marked `xfail(strict=True)`.
- Preserve the target ETF unsupported holdings strict xfail.

Expected focused result: `43 passed, 2 xfailed` for small-golden family; the two xfails are bond and target.

### Slice 2: Documentation alignment

- Update `tests/README.md` so remaining strict xfails are described as dedicated `bond_top_holding_row.v1` and `target_fund_holding_row.v1` gaps.

## 8. Validation Matrix

Required commands:

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py
git diff --check -- tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md docs/reviews/mvp-small-golden-set-bond-top-holding-row-same-source-failing-test-gate-*.md docs/reviews/plan-review-20260610-152453.md
```

Expected outcomes:

- Focused row-field correctness remains with two strict xfails.
- Small-golden family remains `43 passed, 2 xfailed`.
- Ruff passes.
- Diff check passes.

## 9. Review Gates

Plan review must challenge:

- whether the proposed test accidentally reuses stock `top_holdings`;
- whether it routes through bond risk evidence rather than a holdings row shape;
- whether it asserts rank or fields absent from the retained oracle;
- whether it depends on PDF/FDR/source/network access.

Code review must confirm:

- no production code changed;
- 006597 has a dedicated contract-named strict xfail;
- 110020 target ETF remains blocked;
- the test consumes only the retained oracle and minimal same-source table;
- xfail count remains two.

## 10. Stop Conditions

Stop before implementation if:

- plan review finds the future surface is underspecified or conflicts with accepted row-shape decision;
- passing the test would require production extractor changes in this gate;
- a validation command would need PDF/FDR/network/source/fallback/provider/live LLM.

Stop after implementation if:

- xfail count changes from two;
- the bond test XPASSes;
- target ETF xfail is removed or weakened;
- any validation command fails without accepted controller disposition.

## 11. Completion Report Format

Implementation evidence must report:

- files changed;
- exact test name added;
- validation commands and results;
- confirmation that no production extractor, downstream integration, source/runtime/golden/readiness behavior changed;
- remaining next entries.
