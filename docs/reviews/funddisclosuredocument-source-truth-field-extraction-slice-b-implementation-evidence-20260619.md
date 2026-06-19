# FundDisclosureDocument Source-truth Field Extraction Slice B Implementation Evidence 20260619

## Scope

- Work unit: `FundDisclosureDocument Source-truth Field Extraction`
- Gate: `Implementation Gate - Slice B`
- Accepted Slice A commit: `2fd8bba`
- Fixed plan: `docs/reviews/funddisclosuredocument-source-truth-field-extraction-plan-20260619.md`
- Slice B scope: proof-positive `FundDisclosureDocument` content intermediate may emit `product_essence.v1` direct source-truth extraction only.

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`

No changes were made to `tests/fund/test_data_extractor.py`, design docs, control docs, README files, Service/UI/Host/renderer/quality-gate code, public `EvidenceSourceKind`, or processor contracts.

## Implementation Summary

- Added Slice B `product_essence.v1` source-truth extraction behind both gates:
  - base FDD admission must be non-blocked;
  - `FundDisclosureSourceTruthAdmissionProof` must be present and valid.
- Kept proof-missing, invalid proof, candidate-boundary, unsafe provenance, failure-class, unsupported/non-active, and default parsed annual paths fail-closed.
- Implemented exact Slice B value shape with only these top-level keys when available:
  - `basic_identity`
  - `product_profile`
  - `benchmark`
  - `risk_characteristic_text`
- Table/cell extraction follows the fixed plan label map, stable table/cell locator requirement, `row_label_path` before `column_header_path`, sorted iteration by `(row_index, column_index)`, no sibling lookup, duplicate ambiguity omission, and dispatch-matching `fund_code`.
- Paragraph fallback is limited to descriptive fields only and does not populate `basic_identity.*`.
- Every emitted path contributes an `EvidenceAnchor(source_kind="annual_report")`; candidate evidence is not copied into public value or anchors.
- The promoted `product_essence.v1` field family has `candidate_evidence == ()`; the other five field families remain public `missing`.

## Test Coverage

Added/updated processor tests:

- `test_product_essence_source_truth_extracts_exact_value_shape`
- `test_product_essence_source_truth_requires_proof_even_when_candidate_boundary_none`
- `test_product_essence_source_truth_ambiguous_duplicate_omits_conflicting_path`
- `test_product_essence_source_truth_paragraph_fallback_for_descriptive_fields`
- `test_product_essence_source_truth_missing_keeps_family_missing`
- `test_product_essence_source_truth_partial_when_required_groups_missing`
- Updated Slice A proof-positive regression to expect no candidate evidence on the source-truth direct path.

Existing default parsed route and explicit FDD fail-closed regressions remain covered by `tests/fund/test_data_extractor.py`.

## Validation

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
```

Result: `140 passed in 0.50s`.

```bash
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
```

Result: `All checks passed!`.

```bash
git diff --check
```

Result: passed with no output.

## Residual Risks

- Slice B does not prove real-report field correctness beyond no-live fixtures.
- Slice B does not implement source-truth extraction for `return_attribution.v1`, `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, or `core_risk.v1`.
- Slice B does not promote candidate evidence, replace parsers, alter public source kinds, change readiness/release status, or authorize Service/UI/Host/renderer/quality-gate consumption.
