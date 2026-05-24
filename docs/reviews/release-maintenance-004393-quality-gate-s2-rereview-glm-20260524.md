# Release Maintenance 004393 Quality Gate S2 Rereview GLM - 2026-05-24

## Gate

- Role: S2 targeted re-review agent
- Scope: read-only re-review of S2 code review fix
- Controller judgment: `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-controller-judgment-20260524.md`
- Fix artifact: `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-fix-20260524.md`
- Conclusion: `PASS`

## Reviewed Inputs

- `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-controller-judgment-20260524.md`
- `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-fix-20260524.md`
- `fund_agent/fund/extractors/holdings_share_change.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/extraction_score.py`
- `tests/fund/extractors/test_holdings_share_change.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`

## Finding Closure Review

### `004393-S2-C1`

Status: closed.

`fund_agent/fund/extraction_score.py` now routes coverage through `_record_is_covered()` for field score, fund score, fund quality missing counts, and missing-field priority derivation. For `holdings_snapshot`, `_record_is_covered()` requires `value_present=True` and an explicit `(top_holdings_status, top_holdings_source)` pair in the allowlist:

- `direct_top_ten` / `top_ten`
- `direct_all_stock_details` / `all_stock_investment_details`

Absent `comparable_values`, empty status/source, unknown status/source, or inconsistent pairs therefore fail closed instead of being counted as covered. `fund_agent/fund/extraction_snapshot.py` also propagates `top_holdings_status` and `top_holdings_source` into comparable values, so the score path consumes the fields produced by the extractor instead of relying on `value_present` alone.

Tests cover industry-only visible-but-missing behavior, absent status/source, empty status/source, unknown status/source, inconsistent status/source, and both accepted allowlist pairs.

### `004393-S2-C2`

Status: closed.

`fund_agent/fund/extractors/holdings_share_change.py` now merges split share-change tables only when all required checks pass:

- same-page adjacent table index, or next-page first-table continuation;
- candidate header table contains A/C labels and no complete period data;
- candidate data table contains share-change period/flow semantics and no A/C labels;
- inherited A/C header count exactly equals the data value-column count.

This closes the earlier fail-open route where any adjacent A/C-like header table could be merged into any following share-data-like table. Regression tests cover unbounded table position, unrelated intervening table, and mismatched header/data column counts.

### `004393-S2-C3`

Status: closed.

`_select_share_change_value_column()` now checks exact current fund-code header matches first, returns ambiguous when multiple current-code matches exist, rejects any remaining value column containing a six-digit non-current fund code, and only then allows the single-value-column fallback. A single value column such as `110010 A类份额` therefore returns missing instead of being accepted for fund `004393`.

The added regression test covers a single-column non-current fund-code header.

## Residual Risks

- `ParsedTable` still has no parser section metadata. The S2 fix therefore proves bounded page/table-order and table semantics, not physical membership in parser section `§10`. This is already recorded in the fix artifact and is not a blocker for the accepted S2 contract.
- The continuation rule is intentionally conservative and covers same-page adjacent tables plus next-page first-table continuation. Broader multi-page continuation remains outside this S2 slice.

## Validation

```bash
uv run pytest tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
```

Result: `80 passed`.

```bash
uv run ruff check fund_agent/fund/extractors/holdings_share_change.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
```

Result: passed.

```bash
git diff --check
```

Result: passed.

## Decision

`PASS`. I found no remaining P1/P2 blocker for `004393-S2-C1`, `004393-S2-C2`, or `004393-S2-C3`.
