# Code Review - P5-S3 Snapshot Sub-Field Exposure - 2026-05-20

## Verdict

PASS. No blocking findings.

## Scope Reviewed

- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/extraction_score.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/p5-s3-implementation-20260520.md`

## Findings

No blocking correctness, stability, boundary, or test findings.

## Checks

- `pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q`
  - `43 passed`
- `pytest tests/ -q`
  - `187 passed`
- `ruff check .`
  - passed
- `git diff --check`
  - passed

## Controller Notes

- `comparable_values` is produced in Capability snapshot code and consumed by Capability score code; no Service/UI layer takes on fund-domain comparison logic.
- Correctness expansion is explicit and conservative: only whitelisted field/sub-field pairs can enter the denominator.
- Old snapshots remain conservative: absence of `comparable_values` does not create new synthetic mismatches except the existing top-level `classified_fund_type` compatibility path.
- `benchmark_name` alias is field-local from `benchmark_text`, matching the reviewed plan.
- Deferred fields such as `product_profile` and `fee_schedule` remain unavailable rather than inferred from nested or unstable structures.

## Residual Risk

RR-16 is only partially closed. P5-S3 expands the denominator from classification-only to stable P0 sub-fields, but real-run denominator size still depends on extractor output coverage and the current strict golden answer contents. Remaining coverage expansion, if needed, should be a later planned slice rather than inferred here.

## Next Gate

P5-S3 acceptance / aggregate readiness.
