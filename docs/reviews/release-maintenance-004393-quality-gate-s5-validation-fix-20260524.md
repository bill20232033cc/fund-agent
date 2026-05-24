# release-maintenance 004393 quality gate S5 validation fix

## Scope

This fix addresses the S5 validation regression in:

```text
uv run pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
```

The failing test was:

```text
tests/fund/test_quality_gate_integration.py::test_run_quality_gate_for_bundle_selected_member_without_golden_is_fq0_info
```

## Root Cause

S2 intentionally made `holdings_snapshot` scoring fail-closed. A holdings record is covered only when it exposes an allowed `top_holdings_status` and `top_holdings_source` pair.

The legacy Service test fixture in `tests/services/test_fund_analysis_service.py::_bundle()` still represented covered holdings with only:

```text
top_holdings
industry_distribution
```

That fixture no longer satisfied the S2 coverage contract, so the quality gate correctly produced a P1 missing-field warning. This was a stale fixture, not a production scoring bug.

## Changed Files

- `tests/services/test_fund_analysis_service.py`
- `docs/reviews/release-maintenance-004393-quality-gate-s5-validation-fix-20260524.md`

## Fix

The `_bundle()` fixture now explicitly marks its holdings snapshot as covered stock holdings:

```text
top_holdings_status=direct_top_ten
top_holdings_source=top_ten
```

No production source, golden answer, config, runtime behavior, README, design document, Host/Agent package, or turnover policy was changed.

## Validation

```text
uv run pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
66 passed

uv run pytest tests/services/test_fund_analysis_service.py tests/fund/test_quality_gate_integration.py -q
31 passed

uv run ruff check tests/services/test_fund_analysis_service.py tests/fund/test_quality_gate_integration.py
All checks passed

git diff --check
passed
```
