# Release Maintenance 004393 Quality Gate S2 Re-Review Controller Judgment - 2026-05-24

## Gate

- Current phase: `release maintenance`
- Current gate: `release-maintenance 004393 S2 re-review`
- Work unit: `004393/2024 quality gate block root-cause investigation`
- Slice: `S2 - P1 Extraction And Benchmark Correctness`
- Implementation artifact: `docs/reviews/release-maintenance-004393-quality-gate-s2-implementation-20260524.md`
- Code review judgment: `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-controller-judgment-20260524.md`
- Fix artifact: `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-fix-20260524.md`
- Re-review artifacts:
  - `docs/reviews/release-maintenance-004393-quality-gate-s2-rereview-mimo-20260524.md`
  - `docs/reviews/release-maintenance-004393-quality-gate-s2-rereview-glm-20260524.md`
- Controller conclusion: `accepted locally`

## Re-Review Summary

| Reviewer | Conclusion | Controller disposition |
|---|---|---|
| MiMo | `PASS` | Accept |
| GLM | `PASS` | Accept |

Both targeted re-reviews confirm the S2 fix closes the controller-accepted findings from `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-controller-judgment-20260524.md`.

## Finding Closure

| ID | Required fix | Controller judgment |
|---|---|---|
| `004393-S2-C1` | `holdings_snapshot` coverage must use explicit supported status/source pairs; missing, empty, unknown, or inconsistent status/source must not satisfy coverage. | Closed. Score coverage now accepts only `direct_top_ten/top_ten` and `direct_all_stock_details/all_stock_investment_details`; tests cover absent, empty, unknown, inconsistent, industry-only, and valid pairs. |
| `004393-S2-C2` | Split share-change continuation must be bounded by page/table-order evidence and deterministic class-header-to-value-column mapping. | Closed. Merge requires same-page adjacent table index or next-page first-table continuation, split header/data semantics, and equal inherited class-header count / data value-column count. Tests cover happy path, unbounded adjacent-like tables, intervening tables, and count mismatch. |
| `004393-S2-C3` | Single value column fallback must reject non-current fund-code headers before accepting the column. | Closed. Value-column selection now checks exact current-code matches and non-current six-digit code conflicts before single-column fallback; tests cover single-column non-current fund-code headers. |

## Accepted S2 Behavior

- §8 all-stock investment details may serve as stock-holdings source and populate `top_holdings` with the first 10 rows.
- `holdings_snapshot` now exposes machine-readable `top_holdings_status` and `top_holdings_source`, and score/fund-quality coverage consumes those fields rather than raw `value_present`.
- Industry-only holdings evidence remains visible and traceable but does not count as stock-holdings coverage.
- §10 split share-change tables may be merged only under bounded page/table-order and column-count conditions, then A/C selection requires same-source §2 evidence unless a safe exact-code/single-column path applies.
- Benchmark correctness normalization removes visual whitespace only for `benchmark.benchmark_name` and `benchmark.benchmark_text`, preserving non-benchmark Chinese whitespace and ASCII word spacing.
- S2 did not change Host/Agent packages, Dayu dependencies, golden answers, source CSVs, README/config/runtime files, `quality_gate.py`, `profile.py`, or turnover-rate policy.

## Validation

Controller, implementation worker, and re-reviewers ran the required focused validation:

```bash
uv run pytest tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
uv run ruff check fund_agent/fund/extractors/holdings_share_change.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
git diff --check
```

Observed result:

- `80 passed`
- ruff passed
- `git diff --check` passed

## Residuals

- `ParsedTable` still lacks parser section metadata, so split-table evidence proves bounded page/table-order and table semantics rather than physical parser-section provenance. This is accepted for S2 and remains future parser hardening.
- Broader multi-page continuation beyond the observed same-page adjacent / next-page first-table pattern is out of S2 scope.
- Golden row edits remain blocked pending an explicit row-level approval artifact.
- `turnover_rate` disclosure applicability remains a future policy/schema/gate-denominator candidate and was not changed.

## Next Action

Update `docs/implementation-control.md`, commit S2 accepted-local state, then proceed to the S4 golden approval gate or S5 end-to-end verification depending on whether the controller approves any golden row changes.
