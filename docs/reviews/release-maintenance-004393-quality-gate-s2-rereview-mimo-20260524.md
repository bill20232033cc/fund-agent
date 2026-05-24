# Release Maintenance 004393 Quality Gate S2 Targeted Re-review - 2026-05-24

## Gate

- Work unit: `004393/2024 quality gate block root-cause investigation`
- Slice: `S2 - P1 Extraction And Benchmark Correctness`
- Role: targeted re-review agent
- Scope: only verify whether controller accepted findings in `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-controller-judgment-20260524.md` are closed
- Conclusion: `PASS`

## Read Scope

- `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-controller-judgment-20260524.md`
- `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-fix-20260524.md`
- `fund_agent/fund/extractors/holdings_share_change.py`
- `fund_agent/fund/extraction_score.py`
- `tests/fund/extractors/test_holdings_share_change.py`
- `tests/fund/test_extraction_score.py`

## Finding Closure Review

### `004393-S2-C1`

Status: closed.

`fund_agent/fund/extraction_score.py:1375` now routes coverage through `_record_is_covered()`. For `holdings_snapshot`, it reads `top_holdings_status` and `top_holdings_source` from `comparable_values` and only accepts the explicit allowlist in `TOP_HOLDINGS_COVERED_STATUS_SOURCE_PAIRS`. Missing `value_present`, missing comparable values, empty strings, unknown values, and inconsistent status/source pairs all fail closed. The regression coverage in `tests/fund/test_extraction_score.py:261` and `tests/fund/test_extraction_score.py:314` exercises industry-only, absent, empty, unknown, inconsistent, and valid allowlist pairs.

### `004393-S2-C2`

Status: closed.

`fund_agent/fund/extractors/holdings_share_change.py:219` now gates split-table merging through `_can_merge_split_share_tables()`. The merge requires bounded page/table-order evidence via `_is_bounded_split_table_continuation()` at `fund_agent/fund/extractors/holdings_share_change.py:241`, split header/data semantics, and deterministic equality between inherited A/C class header count and data value column count. The regression coverage at `tests/fund/extractors/test_holdings_share_change.py:619`, `tests/fund/extractors/test_holdings_share_change.py:684`, and `tests/fund/extractors/test_holdings_share_change.py:715` covers the accepted happy path, unbounded adjacent-like tables, and mismatched header/data value counts.

### `004393-S2-C3`

Status: closed.

`fund_agent/fund/extractors/holdings_share_change.py:667` checks exact current fund-code matches first, rejects any remaining non-current six-digit fund-code header at `fund_agent/fund/extractors/holdings_share_change.py:681`, and only then permits the single-value-column fallback at `fund_agent/fund/extractors/holdings_share_change.py:683`. The regression test at `tests/fund/extractors/test_holdings_share_change.py:859` verifies a single-column `110010 A类份额` header is rejected for current fund `110011`.

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

## Residual Risk

- No blocking residual risk for the three accepted findings.
- The fix still relies on available `ParsedTable` page/table-order metadata rather than parser section metadata, matching the accepted S2 fix scope and recorded residual.
