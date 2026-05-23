# P9-S2 Implementation Artifact

- **Date**: 2026-05-21
- **Gate**: P9-S2 implementation
- **Plan**: `docs/reviews/p9-s2-quality-gate-golden-coverage-plan-20260521.md`
- **Controller judgment**: `docs/reviews/p9-s2-plan-review-controller-judgment-20260521.md`
- **Status**: completed; not committed
- **Implementation substitute**: Claude Code (cannot serve as P9-S2 code reviewer)

## Scope

Implemented quality gate / golden coverage calibration without changing product-mode safety defaults.

Product mode still uses:

- `quality_gate_policy="block"`
- `docs/code_20260519.csv` as the default selected-pool membership source
- default strict golden answer path resolution where only absent default path becomes not configured
- `warn/off` only behind `--dev-override`

## Changed Files

- `fund_agent/fund/extraction_score.py`
  - Extended `CorrectnessSummary` while preserving `status=available/unavailable`.
  - Added `coverage_scope`, `coverage_reason`, `covered_fund_codes`, `missing_fund_codes`, and `coverage_required=false`.
  - Distinguished `not_configured`, `fund_not_covered`, `no_comparable_fields`, `partially_covered`, and `covered`.
  - Kept explicit missing comparable value and normalized conflicts on the existing mismatch path.

- `fund_agent/fund/quality_gate.py`
  - Converted correctness coverage gaps into `FQ0/info` issues with machine-readable metadata.
  - Preserved correctness mismatches as `FQ1/block`.
  - Kept malformed score correctness schemas fail-closed through `ValueError`.

- `fund_agent/ui/cli.py`
  - Added concise `quality_gate_info: ...` stderr output for fund-scoped correctness coverage `FQ0/info`.
  - Did not change exit status semantics.

- `tests/fund/test_extraction_score.py`
  - Added coverage scope tests for no golden path, malformed existing golden file, explicit missing golden file, fund not covered, no comparable fields, partial coverage, and score JSON fields.

- `tests/fund/test_quality_gate.py`
  - Added FQ0/info metadata tests for `not_configured`, `fund_not_covered`, and `no_comparable_fields`.
  - Kept FQ1/block mismatch coverage.

- `tests/fund/test_quality_gate_integration.py`
  - Added selected-pool member without golden coverage test proving gate runs and does not return `not_run`.

- `tests/ui/test_cli.py`
  - Added CLI coverage info stderr test.

- `tests/services/test_extraction_score_service.py`
  - Fixed `fake_run_extraction_score` to include the 5 new `CorrectnessSummary` fields (`coverage_scope`, `coverage_reason`, `covered_fund_codes`, `missing_fund_codes`, `coverage_required`) required by the P9-S2 dataclass extension.

- `fund_agent/fund/quality_gate.py`
  - Added fail-closed validation in `_evaluate_correctness` for `status=unavailable`: unknown `coverage_scope` or `coverage_reason` values now raise `ValueError` instead of silently passing through.

- `tests/fund/test_quality_gate.py`
  - Added `test_run_quality_gate_rejects_unknown_unavailable_coverage_scope` and `test_run_quality_gate_rejects_unknown_unavailable_coverage_reason` to verify malformed unavailable correctness schemas fail closed.

- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
  - Documented the current distinction between gate execution, selected-pool membership, and strict golden correctness coverage.

## Validation

- Targeted tests (P9-S2 scope + affected service test):
  - `.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py tests/services/test_extraction_score_service.py tests/ui/test_cli.py -q`
  - `78 passed`

- Full suite:
  - `.venv/bin/python -m pytest -q`
  - `377 passed`

- `.venv/bin/ruff check .`
  - passed

- `.venv/bin/ruff format` on 7 changed files
  - applied

- `git diff --check`
  - passed

## Residual Risks

- Strict golden coverage is still limited to the current human-labeled records; P9-S2 only makes that coverage gap explicit and non-blocking as `FQ0/info`.
- Multi-fund aggregate score output now exposes covered and missing fund codes, but CLI info output is intentionally limited to fund-scoped analyze paths.
- P9-S2 does not implement a configurable `correctness_required` policy; `coverage_required=false` is diagnostic only.
