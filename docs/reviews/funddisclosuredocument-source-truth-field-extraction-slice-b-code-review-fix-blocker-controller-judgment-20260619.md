# FundDisclosureDocument Source-truth Field Extraction Slice B Fix Blocker Controller Judgment 20260619

## Scope

- Work unit: `FundDisclosureDocument Source-truth Field Extraction`
- Gate: `code review fix - Slice B`
- Prior controller judgment: `docs/reviews/funddisclosuredocument-source-truth-field-extraction-slice-b-code-review-controller-judgment-20260619.md`
- DS code review: `docs/reviews/code-review-20260619-232403.md`
- MiMo code review: `docs/reviews/code-review-20260619-232617.md`
- Worker blocker: AgentCodex reported that two accepted fail-closed tests expose a mismatch between admission-layer behavior and reviewer/controller expectation.

## Controller Judgment

`REVISE_TEST_EXPECTATION_NO_PRODUCTION_CHANGE_READY_FOR_NARROW_TEST_FIX_NOT_READY`

The blocker is accepted as a controller-scope clarification, not as a production-code defect.

Direct code evidence:

- `FundDisclosureDocumentProcessor.extract()` calls `admit_disclosure_intermediate()` before `_validate_source_truth_admission()`.
- `admit_disclosure_intermediate()` rejects `source_provenance is None` with top-level gap `source_provenance_unsafe` and `contract_status="blocked"`.
- `admit_disclosure_intermediate()` rejects non-null `failure_class` using `FAILURE_CLASS_ADMISSION_MAP`; `not_found` / `unavailable` are unsupported, while `schema_drift` / `identity_mismatch` / `integrity_error` are blocked candidate-boundary failures.
- Because these inputs are not admitted, the processor must not force them into field-family `source_truth_admission_invalid`.

Therefore the prior test-only fix action was too specific for two branches. It should not require `source_provenance=None` or non-null `failure_class` to appear as `product_essence.v1` field-family gaps.

## Revised Fix Scope

The fix remains test-only unless an allowed test proves an unrelated current implementation failure.

Required tests:

- `source_provenance=None` with otherwise valid proof must assert the existing top-level `source_provenance_unsafe` blocked result and no public field families / anchors.
- `failure_class` with otherwise valid proof must assert the existing admission-layer gap/status from `FAILURE_CLASS_ADMISSION_MAP`, not `source_truth_admission_invalid`.
- column-header-only cell matching.
- generic cell text filter.
- unstable table/cell skip.
- duplicate identical normalized values dedupe.
- paragraph heading-path fallback.

Still accepted:

- Source-truth proof missing/invalid after base admission continues to use `source_truth_admission_missing` / `source_truth_admission_invalid` at field-family level.
- DS low-risk whitespace normalization finding remains deferred to a future real-report normalization gate.

## Allowed Files

- `tests/fund/processors/test_fund_disclosure_processor.py`
- `docs/reviews/funddisclosuredocument-source-truth-field-extraction-slice-b-code-review-fix-evidence-20260619.md`

This controller clarification artifact is controller-owned and does not authorize production code changes.

## Required Validation

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
git diff --check
```

## Next Gate

- Next entry point: `FundDisclosureDocument Source-truth Field Extraction Code Review Fix Gate - Slice B`
- Worker: `AgentCodex`
- Stop condition: implementation tests + evidence artifact complete, or a non-test production behavior conflict is proven by a failing allowed test.
