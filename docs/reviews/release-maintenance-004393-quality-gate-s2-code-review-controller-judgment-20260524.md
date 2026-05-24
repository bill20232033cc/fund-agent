# Release Maintenance 004393 Quality Gate S2 Code Review Controller Judgment - 2026-05-24

## Gate

- Current phase: `release maintenance`
- Current gate: `release-maintenance 004393 S2 code review`
- Work unit: `004393/2024 quality gate block root-cause investigation`
- Slice: `S2 - P1 Extraction And Benchmark Correctness`
- Implementation artifact: `docs/reviews/release-maintenance-004393-quality-gate-s2-implementation-20260524.md`
- Code reviews:
  - `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-mimo-20260524.md`
  - `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-glm-20260524.md`
- Controller conclusion: `fix required`

## Review Summary

| Reviewer | Conclusion | Controller disposition |
|---|---|---|
| MiMo | `FAIL` | Accept both fail-closed findings |
| GLM | `FAIL` | Accept both fail-closed findings |

Both reviewers agree the S2 direction is aligned with the accepted plan and that targeted validation currently passes. The remaining blockers are static fail-closed gaps not covered by the happy-path tests.

## Accepted Findings

| ID | Source | Finding | Controller decision | Required fix |
|---|---|---|---|---|
| `004393-S2-C1` | MiMo P1, GLM P1 | `holdings_snapshot` score coverage treats missing, empty, or unknown `top_holdings_status` as covered because only literal `missing` is rejected. | Accepted. The accepted S2 contract says `top_holdings_status` / `top_holdings_source` are required machine-readable fields. Coverage must fail closed unless status/source are explicit supported stock-holdings coverage. | Change coverage to an explicit allowlist, e.g. `direct_top_ten/top_ten` and `direct_all_stock_details/all_stock_investment_details`. Missing, empty, malformed, or unknown status/source must not satisfy coverage. Add tests for absent, empty, unknown, and inconsistent status/source. |
| `004393-S2-C2` | MiMo P1 | Split share-change continuation can merge any adjacent A/C header-like table with any following share-data-like table, without enough bounded §10/page-order context or deterministic header-count guard. | Accepted. The accepted plan requires adjacent continuation to be direct and fail closed when ambiguous. | Add bounded continuation checks using available page/table-order evidence, and require inherited class headers to map deterministically to data value columns. Add adversarial tests for unrelated adjacent header-like tables and mismatched header/data column counts. |
| `004393-S2-C3` | GLM P1 | `_select_share_change_value_column()` accepts a single value column before checking whether that header contains a non-current fund code. | Accepted. A single value column that explicitly names another fund code is not a safe current-fund value column. | Check exact current-code match and any other fund-code conflict before single-value fallback. Add a regression test for a single-column non-current fund-code header. |

## Accepted Non-Blocking Parts

- All-stock details may serve as `top_holdings` source when status/source are explicit and stock-holdings rows are present.
- Benchmark correctness normalization is field-aware and limited to `benchmark.benchmark_name` / `benchmark.benchmark_text`.
- S2 did not edit Host/Agent packages, Dayu dependencies, golden answers, source CSVs, README/config/runtime, or turnover-rate policy.

## Required Fix Scope

The fix agent may edit only:

- `fund_agent/fund/extractors/holdings_share_change.py`
- `fund_agent/fund/extraction_score.py`
- `tests/fund/extractors/test_holdings_share_change.py`
- `tests/fund/test_extraction_score.py`
- `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-fix-20260524.md`

It may edit `fund_agent/fund/extraction_snapshot.py` and `tests/fund/test_extraction_snapshot.py` only if needed to keep status/source propagation mechanically aligned, but no schema expansion is expected.

The fix must not edit `docs/implementation-control.md`, `docs/design.md`, `AGENTS.md`, README, golden answers, source CSVs, config, runtime output, `quality_gate.py`, `fund_agent/host`, `fund_agent/agent`, `profile.py`, or turnover applicability behavior.

## Required Validation

```bash
uv run pytest tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
uv run ruff check fund_agent/fund/extractors/holdings_share_change.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
git diff --check
```

## Next Action

Dispatch an S2 fix worker. After the fix, run targeted re-review from two independent reviewers before accepting S2.
