# FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Slice 1 Implementation Evidence

## Gate And Slice

- Work unit: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction`
- Gate: `Implementation Gate`
- Slice id: `Slice 1: Admission/reuse guard`
- Role: `implementation worker only`
- Verdict: `IMPLEMENTATION_READY_FOR_REVIEW_NOT_READY`

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice1-implementation-evidence-20260620.md`

## Behavior Summary

- `_field_families_for_intermediate()` now declares `return_attribution_source_truth: FundFieldFamilyResult | None`.
- When existing source-truth admission has already passed and content intermediate exists, it calls `_extract_return_attribution_source_truth(content_intermediate, source_provenance, context)`.
- Slice 1 direct extractor is a fail-closed skeleton: `return_attribution.v1` remains public `status="missing"`, `extraction_mode="missing"`, `value={}`, `anchors=()`, with local `field_family_missing` gap.
- Proof-positive direct route suppresses `return_attribution.v1` candidate evidence by returning `candidate_evidence=()`.
- Proof-missing or proof-invalid paths still use existing candidate evidence selection and `_with_source_truth_admission_gap()`.
- Base admission failures from `failure_class`, missing/unsafe `source_provenance`, or `candidate_boundary` remain blocked through existing admission behavior.
- `_validate_source_truth_admission()` was not changed.

## Validation

| Command | Result |
|---|---|
| `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py` | PASS: `125 passed in 0.95s` |
| `uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py` | PASS: `All checks passed!` |
| `git diff --check -- fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice1-implementation-evidence-20260620.md` | PASS: no output |

## Focused Test Coverage

- `test_return_attribution_source_truth_route_suppresses_candidate_evidence`
  - proof-positive `return_attribution.v1` route enters direct skeleton, suppresses candidate evidence, and remains public missing until a later value extraction slice.
- `test_return_attribution_source_truth_requires_proof_even_when_candidate_boundary_none`
  - proof missing with `candidate_boundary=None` keeps public missing, candidate evidence, `candidate_only_not_source_truth`, and `source_truth_admission_missing`.
- `test_return_attribution_source_truth_rejects_base_admission_invalid_paths`
  - invalid `source_provenance` and `failure_class` paths do not produce field-family direct output.
- `test_return_attribution_source_truth_candidate_boundary_remains_blocked`
  - candidate-boundary path remains blocked and candidate-only; it is not promoted to source truth even when a proof object is present.
- Existing S6-C candidate-only tests remain in the same file and passed.

## Explicit Non-claims

- `NOT_READY` is preserved.
- No parser replacement.
- No value extraction for `return_attribution.v1` in this slice.
- No public source-truth claim for candidate locator evidence.
- No direct extraction for `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, or `core_risk.v1`.
- No schema expansion for `EvidenceSourceKind`, `EvidenceAnchor`, `FundFieldFamilyResult`, `FundProcessorResult`, `FundDisclosureDocumentContentIntermediate`, or `FundDisclosureSourceTruthAdmissionProof`.
- No Service/UI/Host/renderer/quality-gate/repository/source-policy changes.
- No live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference/provider/LLM commands were run.

## Residual Risks And Next Slice Destination

- `return_attribution.v1` public value extraction remains intentionally unimplemented in Slice 1.
  - Classification: covered by later approved slice.
  - Destination: Slice 2 `Value extraction`.
- Public anchors, ambiguity handling, and field-local partial gaps for real direct values remain unimplemented.
  - Classification: covered by later approved slice.
  - Destination: Slice 3 `Anchor/gap behavior`.
- Facade projection/docs sync for a completed direct value remains deferred.
  - Classification: covered by later approved slice.
  - Destination: Slice 4 `Facade/test/docs sync`.

## Completion Status

Slice 1 implementation is ready for review while preserving `NOT_READY`.

Verdict token: `IMPLEMENTATION_READY_FOR_REVIEW_NOT_READY`
