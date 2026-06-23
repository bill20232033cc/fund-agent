# RR-09 A1-C Projection / Anchor Locator / Reference Materializer No-live Implementation Evidence

Verdict: `RR_09_A1C_NO_LIVE_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY`

## 1. Scope

This evidence covers the accepted A1-C no-live implementation gate.

Implemented scope:

- `fund_agent/fund/evidence_confirm_sources.py`
- `fund_agent/fund/evidence_confirm.py`
- `tests/fund/test_evidence_confirm_sources.py`
- `tests/fund/test_evidence_confirm.py`
- `fund_agent/fund/README.md`
- `tests/README.md`

Out of scope:

- No live/PDF R1-R4 re-evidence.
- No B1 `017641 / 2024` runtime product CLI re-evidence.
- No provider, LLM, checklist support, report-body rendering, quality-gate threshold change, tag, release or readiness promotion.

## 2. Implementation Summary

- Semantic `row_locator` with compatible `page-{page_number}-table-{table_index}` now materializes a table-level annual-report excerpt instead of producing zero references.
- Semantic `row_locator` without `table_id` now materializes a bounded section-level annual-report excerpt when section preflight is valid.
- Both degradation paths produce informational materializer issues:
  - `semantic_row_locator_degraded_to_table_excerpt`
  - `semantic_row_locator_degraded_to_section_excerpt`
- Existing blocking behavior remains for unsupported `table_id`, missing/duplicate table, page mismatch, row-N out-of-range, missing section, fund/year mismatch and source-truth admission failure.
- V2 `anchor_precision` now compares proof references with the original chapter anchor map. If an anchor declared `row_locator` but the reference has no `row_locator`, V2 emits E1 reviewable warning instead of silently treating the coarse reference as row-precise.

## 3. Boundary Evidence

- The implementation did not add imports of repository, PDF/cache/source helpers, Service, Host, provider, renderer, quality gate or CLI code to `evidence_confirm.py`.
- `evidence_confirm_sources.py` still only obtains production annual reports through the existing repository-bounded runner and its `load_annual_report()` path.
- The materializer fallback uses only already-loaded `ParsedAnnualReport.tables`, `ParsedAnnualReport.get_section_text()` and the existing projection anchors.

## 4. Validation

```bash
uv run pytest tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm.py -q --tb=short
```

Result: `89 passed in 1.28s`

```bash
uv run pytest tests/services/test_fund_analysis_service.py tests/services/test_quality_gate_service.py -q --tb=short
```

Result: `48 passed in 0.91s`

```bash
uv run ruff check fund_agent/fund/evidence_confirm_sources.py fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm.py
```

Result: `All checks passed!`

```bash
git diff --check
```

Result: passed.

## 5. Acceptance Notes

- No-live tests now prove semantic row locators no longer produce zero references when a safe table/section excerpt is available.
- Tests prove source-support and missing-evidence pass after materialization, while anchor precision remains warn for downgraded row locators.
- Repository runner tests prove strict `status` can remain `fail` while `pathway_status` is `pass` for all-E1 precision-warning shape.
- README updates record current materializer behavior and no-live test scope.

## 6. Residuals

- R1-R4 remain release-blocking until a separate explicit live/PDF re-evidence gate proves the fix on repository-loaded annual reports.
- B1 `017641 / 2024` runtime product CLI re-evidence remains separate and requires explicit live/PDF authorization.
- Checklist support, report-body rendering, provider-backed semantic production default, tag/release and release/readiness promotion remain separate gates.
- Release/readiness remains `NOT_READY`.
