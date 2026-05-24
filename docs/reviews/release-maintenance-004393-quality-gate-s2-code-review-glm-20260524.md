# Release Maintenance 004393 Quality Gate S2 Code Review GLM - 2026-05-24

## Gate

- Role: Gateflow S2 code review agent
- Scope: `release-maintenance 004393 S2 P1 extraction and benchmark correctness implementation`
- Review mode: read-only source/test/diff review, plus allowed validation commands
- Conclusion: `FAIL`

## Sources Read

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md` Startup Packet/current gate
- `docs/reviews/release-maintenance-004393-quality-gate-plan-20260524.md`
- `docs/reviews/release-maintenance-004393-quality-gate-plan-fix-20260524.md`
- `docs/reviews/release-maintenance-004393-quality-gate-evidence-controller-judgment-20260524.md`
- `docs/reviews/release-maintenance-004393-quality-gate-s2-implementation-20260524.md`
- Diff and current files for:
  - `fund_agent/fund/extractors/holdings_share_change.py`
  - `fund_agent/fund/extraction_snapshot.py`
  - `fund_agent/fund/extraction_score.py`
  - `tests/fund/extractors/test_holdings_share_change.py`
  - `tests/fund/test_extraction_snapshot.py`
  - `tests/fund/test_extraction_score.py`

## Findings

### [P1] `holdings_snapshot` score coverage fails open when required status is absent

- File: `fund_agent/fund/extraction_score.py:1388`
- Direct evidence: `_record_is_covered()` reads `top_holdings_status` from `comparable_values`, then treats every value except literal `"missing"` as covered:

```python
top_holdings_status = _record_comparable_values(record).get(TOP_HOLDINGS_STATUS_SUB_FIELD)
return _optional_scalar_text(top_holdings_status) != TOP_HOLDINGS_STATUS_MISSING
```

This means a `holdings_snapshot` record with `value_present=True` and missing/empty `top_holdings_status` is counted as covered, because `None != "missing"`.

That contradicts the accepted S2 contract: `top_holdings_status` and `top_holdings_source` are required machine-readable fields, and industry-only evidence must not satisfy stock-holdings coverage. The current tests prove `top_holdings_status="missing"` fails coverage, but they do not prove absent/unknown status fails closed. A malformed, legacy, or partially propagated `holdings_snapshot` row can therefore pass score/fund_quality coverage even though the required stock-holdings source/status contract is absent.

Minimum fix:

- Make holdings coverage explicit allow-list based:
  - covered only when `top_holdings_status in {"direct_top_ten", "direct_all_stock_details"}` and source is consistent;
  - missing/empty/unknown status should be not covered or a hard validation error.
- Add score tests for `holdings_snapshot` with `value_present=True` and absent/empty/unknown `top_holdings_status`, proving it does not satisfy P1 coverage.

### [P1] `share_change` accepts a single value column before rejecting non-current fund-code headers

- File: `fund_agent/fund/extractors/holdings_share_change.py:578`
- File: `fund_agent/fund/extractors/holdings_share_change.py:583`
- File: `fund_agent/fund/extractors/holdings_share_change.py:604`

`_select_share_change_value_column()` returns `single_value_column` immediately when there is exactly one value column:

```python
value_columns = [...]
if len(value_columns) == 1:
    ...
    reason=_REASON_SINGLE_VALUE_COLUMN
```

The rejection for headers containing a fund code appears later:

```python
if any(_contains_fund_code(header) for _, header in value_columns):
    return None
```

So a one-value-column table whose header is explicitly for another fund code, for example `110010 A类份额` while current fund is `110011`, will be accepted as the current fund's `share_change`. This violates the accepted plan requirement that tables containing other fund-code headers fail closed unless the exact current fund code matches. Existing tests only cover the multi-column "other code header + A class" case; they miss the single-column other-code case.

Minimum fix:

- Evaluate exact current fund-code match and non-current fund-code conflict before the single-value fallback.
- If a single value column contains any six-digit fund code that is not the current fund code, return missing.
- Add a regression test for a single-column share-change table with a non-current fund-code header.

## Non-Blocking Observations

- The implementation did not create `fund_agent/host` or `fund_agent/agent`, did not add Dayu Host/Agent dependencies, and did not touch golden/source/config/runtime/README in the reviewed diff.
- Benchmark correctness normalization is field-aware in the reviewed path: intra-Chinese visual whitespace removal is gated to `benchmark.benchmark_name` / `benchmark.benchmark_text`, and tests cover non-benchmark Chinese whitespace plus ASCII benchmark spacing.
- `turnover_rate` policy was not changed in the reviewed diff.

## Validation

```bash
uv run pytest tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
```

Result: `76 passed`.

```bash
uv run ruff check fund_agent/fund/extractors/holdings_share_change.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
```

Result: passed.

```bash
git diff --check
```

Result: passed.

## Conclusion

`FAIL`. The implementation passes local validation but still has two correctness blockers in fail-closed behavior. Both can cause false positive quality coverage or false direct extraction under plausible snapshot/table shapes and should be fixed before S2 acceptance.
