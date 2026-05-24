# Release Maintenance 004393 Quality Gate S2 Code Review - MiMo - 2026-05-24

## Scope

- Review target: `release-maintenance 004393 S2 P1 extraction and benchmark correctness implementation`
- Review mode: read-only code review
- Current truth sources:
  - `AGENTS.md`
  - current `docs/design.md`
  - `docs/implementation-control.md` Startup Packet / current gate
- Required plan/evidence artifacts reviewed:
  - `docs/reviews/release-maintenance-004393-quality-gate-plan-20260524.md`
  - `docs/reviews/release-maintenance-004393-quality-gate-plan-fix-20260524.md`
  - `docs/reviews/release-maintenance-004393-quality-gate-evidence-controller-judgment-20260524.md`
  - `docs/reviews/release-maintenance-004393-quality-gate-s2-implementation-20260524.md`
- Diff files reviewed:
  - `fund_agent/fund/extractors/holdings_share_change.py`
  - `fund_agent/fund/extraction_snapshot.py`
  - `fund_agent/fund/extraction_score.py`
  - `tests/fund/extractors/test_holdings_share_change.py`
  - `tests/fund/test_extraction_snapshot.py`
  - `tests/fund/test_extraction_score.py`

## Conclusion

`FAIL`

S2 is directionally aligned with the accepted plan, and the targeted validation commands pass. However, two fail-closed requirements are not fully implemented:

- `holdings_snapshot` score coverage fails open when required machine-readable status is absent or unknown.
- split-table `share_change` merge can combine adjacent A/C header-like and share-data-like tables without proving §10/page-order bounded context.

These are correctness blockers for claiming S2 quality-gate coverage.

## Findings

### [P1] Missing or unknown `top_holdings_status` is treated as covered

- File: `fund_agent/fund/extraction_score.py:1388`
- Code path:
  - `_record_is_covered()` first accepts any `value_present=True` record.
  - For `holdings_snapshot`, it reads `comparable_values["top_holdings_status"]`.
  - It returns covered whenever that optional text is not exactly `"missing"`.

This makes absent or unknown status fail open:

```python
top_holdings_status = _record_comparable_values(record).get(TOP_HOLDINGS_STATUS_SUB_FIELD)
return _optional_scalar_text(top_holdings_status) != TOP_HOLDINGS_STATUS_MISSING
```

The accepted S2 plan says `top_holdings_status` and `top_holdings_source` are required machine-readable contract fields, not optional metadata, and industry-only evidence must not satisfy stock-holdings coverage. With the current predicate, a `holdings_snapshot` record that has `value_present=True` but no comparable status, or an unrecognized status, counts as covered. That lets legacy, malformed, or partially wired industry-only records bypass the intended score/fund_quality/quality-gate semantics.

Minimum fix:

- Treat coverage as true only for an explicit allowlist such as `direct_top_ten` and `direct_all_stock_details`.
- Treat missing, empty, `"missing"`, and unknown status values as not covered.
- Add tests for `value_present=True` with absent `top_holdings_status` and with an unknown status.

### [P1] Split share-change continuation is not bounded to §10/page-order evidence

- File: `fund_agent/fund/extractors/holdings_share_change.py:192`
- File: `fund_agent/fund/extractors/holdings_share_change.py:210`
- File: `fund_agent/fund/extractors/holdings_share_change.py:264`

The accepted S2 plan requires parser-split share-change continuation to fail closed unless the header table and data table are directly adjacent in the same logical §10 disclosure, with page/order evidence and deterministic column mapping.

Current implementation merges any adjacent pair in `report.tables` when:

- the first table text contains A/C labels and lacks `期初` / `期末`;
- the next table text contains `期初` / `期末` / `申购` / `赎回` and lacks A/C labels.

There is no check that the pair is physically or logically bounded to §10, no page/table-index adjacency check, and no guard that the number of inherited class headers exactly matches the data table value columns. `_merge_split_share_table()` then rewrites the data table headers and `_find_share_change_table()` treats it as a normal share-change table.

This can incorrectly merge an unrelated A/C header-like table immediately before a share-change data-like table. If §2 evidence identifies the current class, the extractor may produce direct share-change values instead of failing closed. That violates the plan's direct same-source continuation rule and the explicit stop condition against ambiguous split tables.

Minimum fix:

- Add a bounded continuation predicate before merge, using available page/table-order evidence, for example same page adjacent table index or the accepted next-page continuation pattern.
- Require the inherited class headers to map deterministically to the data table value columns; if counts do not match, fail closed.
- Preserve the inherited-header table ID in the share-change anchor note as planned, so the evidence is auditable.
- Add adversarial tests for unrelated adjacent A/C header-like tables and mismatched header/data column counts.

## Non-Blocking Observations

- The all-stock-details path emits `top_holdings_status=direct_all_stock_details`, `top_holdings_source=all_stock_investment_details`, limits rows to 10, and keeps industry distribution independent.
- Benchmark correctness normalization is field-aware and limited to `benchmark.benchmark_name` / `benchmark.benchmark_text`; non-benchmark Chinese whitespace and ASCII benchmark spacing are covered by tests.
- I did not see Host/Agent package creation, Dayu dependency changes, golden/source CSV edits, turnover policy changes, profile-derived identity orchestration, README/config/runtime changes, or direct PDF/cache/source-helper reads in this S2 diff.
- Root-level untracked `review_report_20260524.md` is unrelated and was not touched.

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
