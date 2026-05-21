# P13 Tracking Error Direct Disclosure Implementation（2026-05-22）

## Scope

Implemented the accepted direct-disclosure scope from `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md` and controller judgment.

Included:

- typed `IndexProfileValue` and `TrackingErrorValue` fields on `StructuredFundDataBundle`
- direct annual-report tracking-error extraction from `ParsedAnnualReport`
- index/enhanced/non-index/QDII applicability behavior
- `ResolvedTrackingErrorForRisk` authority path with structured data priority and developer override fallback only in developer mode
- renderer replacement of tracking-error placeholder only from `structured_data.tracking_error`
- deterministic audit guards against tracking-error and benchmark-anchor misuse
- snapshot observability for `index_profile` and `tracking_error` without comparable/golden denominator promotion

Excluded as required:

- calculated index series tracking error
- external index adapter
- methodology extraction
- constituents extraction
- E1/E2/E3, Evidence Confirm, LLM, Dayu runtime
- Service/UI direct source access
- RR-13 changes
- repo-audit changes

## Changed Files

- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/profile.py`
- `fund_agent/fund/extractors/performance.py`
- `fund_agent/fund/extractors/__init__.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/analysis/risk_check.py`
- `fund_agent/fund/analysis/__init__.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/fund/template/renderer.py`
- `fund_agent/fund/audit/audit_programmatic.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- focused tests and fixtures under `tests/fund/...`

`docs/repo-audit-20260521.md` remains untouched and out of scope.

## Validation

- `pytest tests/fund/extractors/test_performance.py tests/fund/extractors/test_profile.py`：31 passed
- `pytest tests/fund/analysis/test_risk_check.py`：14 passed
- `pytest tests/fund/template/test_renderer.py`：38 passed
- `pytest tests/fund/audit/test_audit_programmatic.py`：36 passed
- `pytest tests/fund/test_extraction_snapshot.py tests/fund/test_quality_gate.py`：23 passed
- Adjacent regression: `pytest tests/fund/integration/test_p1_sample_matrix.py tests/fund/analysis/test_r_abc.py tests/fund/test_golden_prefill.py tests/services/test_fund_analysis_service.py`：18 passed
- `ruff check fund_agent tests`：passed
- `git diff --check HEAD`：passed

## Code Review Fix Notes

Fixed accepted low findings from `docs/reviews/p13-tracking-error-code-review-mimo-20260522.md` and `docs/reviews/p13-tracking-error-code-review-glm-20260522.md`:

- Replaced the renderer `assert` in `_render_tracking_error_segment()` with an explicit defensive missing-data branch.
- Expanded `_benchmark_components()` splitting to cover all declared separators, including `和` and `×`, with a composite benchmark regression test.
- Changed `_extract_tracking_error()` so table+text matches with equal parsed values keep the table match, while unequal values remain `tracking_error_ambiguous`; added same-value and conflicting-value tests.

## Residuals

- Tracking-error calculation from fund/index time series remains unimplemented by scope.
- Methodology and constituents remain benchmark-only insufficient unless future source contracts are accepted.
- QDII tracking-error applicability remains not applicable until a QDII subtype design exists.
- Snapshot fields are observable only; `index_profile` and `tracking_error` are not promoted to `comparable_values`, FQ2, or golden correctness denominator.
