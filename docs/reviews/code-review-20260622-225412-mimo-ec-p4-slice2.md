# Code Review: EC-P4 Slice 2 — Service Deterministic Opt-In Propagation

## Gate / Slice

- Work unit: Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration
- Gate: code review
- Slice: Slice 2 - Service Deterministic Opt-In Propagation
- Classification: heavy
- Release/readiness: NOT_READY
- Timestamp: 2026-06-22 22:54 Asia/Shanghai

## Reviewed Target

- `fund_agent/services/fund_analysis_service.py` (uncommitted diff, +226/-3)
- `tests/services/test_fund_analysis_service.py` (uncommitted diff, +419/-3)

## Verdict

**PASS_WITH_FINDINGS**

Implementation correctly follows the accepted plan. All required scenarios are covered by tests. No blocking findings. Two non-blocking findings for future improvement.

## Summary

The diff wires Evidence Confirm into `FundAnalysisService._run_analysis_core()` through developer override opt-in, matching the accepted plan exactly:

1. **Policy resolution**: `_effective_evidence_confirm_policy()` correctly forces checklist to `"off"` and passes through analyze policy. Product mode rejects developer overrides through existing guard. `_resolve_analyze_contract()` defaults EC policy to `"off"` in both product and developer_override paths.

2. **Runner injection**: `FundAnalysisService.__init__` accepts optional `EvidenceConfirmRunner` callable; defaults to `run_repository_bounded_evidence_confirm`. Async call constructs `EvidenceConfirmRepositoryRunRequest` with `project_chapter_facts()` projection, `fund_code`, `report_year`, `force_refresh`. No direct `FundDocumentRepository` / PDF / source / parser / provider access.

3. **Error handling**: Runner exceptions are caught by `except Exception` and converted to fail-closed summary via `_runner_exception_evidence_confirm_summary()`. `EvidenceConfirmBlockedError` vs `QualityGateBlockedError` precedence matches plan: `QualityGateBlockedError` is canonical when quality gate runs and blocks; `EvidenceConfirmBlockedError` is EC-only when quality gate is off/not-runnable or `quality_gate_policy=warn` + EC policy `block`.

4. **Quality gate integration**: `_run_quality_gate_if_enabled()` forwards `evidence_confirm_summary` to `run_quality_gate_for_bundle()` (confirmed Slice 1 parameter exists). Checklist remains off/no runner.

5. **Boundary**: Static import check confirms no forbidden terms (`FundDocumentRepository`, `pdf_cache`, `cache_helper`, `source_adapter`, `Docling`, `docling`, `pdfplumber`) in service file.

6. **Tests**: 38 tests pass. All 8 required plan scenarios are covered:
   - Default analyze policy off → no runner call, summary is None
   - Default checklist policy off → no runner call, summary is None
   - Developer override warn → runner called, returns summary, no block
   - Developer override block + gate off → `EvidenceConfirmBlockedError`
   - Quality gate warn + EC block + EC fail → `EvidenceConfirmBlockedError`
   - Quality gate block + EC fail → `QualityGateBlockedError` with ECQ2/block
   - Product mode with EC developer override → existing rejection
   - Boundary static imports → no forbidden terms

## Findings

### F-01 [low] Runner exception conversion path has no direct test coverage

- **File/line**: `fund_agent/services/fund_analysis_service.py:1327-1333`
- **Issue**: `_runner_exception_evidence_confirm_summary()` is only tested indirectly (no test injects an Exception into `_FakeEvidenceConfirmRunner` and verifies the resulting summary fields). The try/except in `_run_evidence_confirm_if_enabled` catches `Exception` and delegates to this helper, but no test verifies:
  - the `not_run_reason` format is `runner_exception:<class_name>`
  - the summary `status` is `"fail"` with `pathway_status="fail"`
  - the `deterministic_status` is `"not_run"` (not `"fail"`)
  - the `blocking_issue_ids` contains the correct issue id
- **Why it matters**: The runner exception path is a fail-closed safety net. If the helper were to produce incorrect fields (e.g. wrong reason format, missing blocking issue id), the downstream blocking behavior would be silently incorrect.
- **Required fix**: Add one test that injects `RuntimeError("test")` into the fake runner, calls `analyze` with `evidence_confirm_policy="block"`, and asserts the `EvidenceConfirmBlockedError.evidence_confirm_summary` fields match the expected fail-closed shape.
- **Suggested owner**: Service test owner

### F-02 [info] EvidenceConfirmRunner type alias lacks docstring

- **File/line**: `fund_agent/services/fund_analysis_service.py:200-203`
- **Issue**: The `EvidenceConfirmRunner` type alias is a module-level public symbol but has no docstring. AGENTS.md requires all functions/classes to have Chinese docstrings.
- **Why it matters**: Minor style consistency. The alias is used in `FundAnalysisService.__init__` signature and is importable by tests.
- **Required fix**: Add a one-line Chinese docstring or comment explaining the type alias.
- **Suggested owner**: Service owner

## Residual Risks / Uncovered Areas

| Risk | Status |
|---|---|
| CLI/UI Evidence Confirm summary output | Covered by later Slice 3 |
| Renderer non-rendering guard | Covered by later Slice 4 |
| Semantic companion propagation | Covered by later Slice 5 |
| Checklist EC CLI support | Deferred; slice keeps checklist off/no runner |
| Default-on/product-mode EC and release readiness | Future gate; NOT_READY preserved |
| Runner exception helper correctness | See F-01 |

## Required Follow-Up

- F-01: one additional test for runner exception conversion path (non-blocking for merge, but recommended before next slice builds on this path).
- F-02: optional docstring addition.
