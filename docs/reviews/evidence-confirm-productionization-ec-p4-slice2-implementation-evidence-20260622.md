# Evidence Confirm Productionization EC-P4 Slice 2 Implementation Evidence

## Gate / Slice

- Work unit: Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration
- Gate: implementation
- Slice: Slice 2 - Service Deterministic Opt-In Propagation
- Classification: heavy
- Release/readiness: NOT_READY

## Changed Files

- `fund_agent/services/fund_analysis_service.py`
- `tests/services/test_fund_analysis_service.py`
- `docs/reviews/evidence-confirm-productionization-ec-p4-slice2-implementation-evidence-20260622.md`

## Exact Behavior Implemented

- Added `evidence_confirm_policy` to `FundAnalysisDeveloperOverrides` and `ResolvedAnalyzeContract`.
- Added `evidence_confirm_summary` to `_AnalysisCoreResult`, `FundAnalysisResult`, and `FundChecklistResult`.
- Added `EvidenceConfirmBlockedError` carrying only safe `EvidenceConfirmProductionSummary`.
- Added async Evidence Confirm runner dependency injection on `FundAnalysisService`.
- `analyze()` developer override `evidence_confirm_policy="warn"|"block"` now:
  - projects chapter facts from the already extracted `StructuredFundDataBundle`;
  - calls the injected repository-bounded runner with `EvidenceConfirmRepositoryRunRequest`;
  - converts runner results through `summary_from_repository_result()`;
  - converts runner exceptions to safe fail summaries with `runner_exception:<class_name>`;
  - forwards the summary to `run_quality_gate_for_bundle()`.
- Policy `off` does not call the runner and returns `evidence_confirm_summary=None`.
- `checklist()` effective Evidence Confirm policy remains `off` in this slice, so checklist does not call the runner.
- Blocking semantics:
  - `quality_gate_policy=off` + EC policy `block` + EC fail raises `EvidenceConfirmBlockedError`.
  - `quality_gate_policy=warn` + EC policy `block` + EC fail raises `EvidenceConfirmBlockedError`.
  - `quality_gate_policy=block` + EC policy `block` + EC fail raises `QualityGateBlockedError` when the quality gate runs and merged ECQ issues block.
  - EC policy `warn` never blocks by itself.
  - Existing FQ quality-gate block remains `QualityGateBlockedError`.

## Tests / Validation

Command:

```text
uv run pytest tests/services/test_fund_analysis_service.py -q
```

Output:

```text
......................................                                   [100%]
38 passed in 1.25s
```

Command:

```text
uv run pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
```

Output:

```text
........................................................                 [100%]
56 passed in 0.49s
```

Command:

```text
uv run ruff check fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service.py
```

Output:

```text
All checks passed!
```

## Boundary Proof

Command:

```text
rg -n "FundDocumentRepository|pdf_cache|cache_helper|source_adapter|Docling|docling|pdfplumber" fund_agent/services/fund_analysis_service.py
```

Output:

```text
<no matches; rg exited 1>
```

Service only imports Fund-layer public Evidence Confirm runner/request/result/summary helpers and `project_chapter_facts()`. It does not import or instantiate repository/source/PDF/cache/parser/provider/LLM internals and does not inspect raw references or excerpts.

## Residual Risks

- CLI/UI Evidence Confirm option and summary output: covered by later approved Slice 3.
- Renderer non-rendering guard: covered by later approved Slice 4.
- Semantic companion propagation: covered by later approved Slice 5.
- Checklist Evidence Confirm CLI support: covered by later approved Slice 6 or separate explicit checklist gate; this slice keeps checklist off/no runner.
- Default-on/product-mode Evidence Confirm and release/readiness transition: assigned to future reviewed gates; NOT_READY preserved.

## Verdict

EC_P4_SLICE2_IMPLEMENTATION_READY_FOR_CODE_REVIEW_NOT_READY
