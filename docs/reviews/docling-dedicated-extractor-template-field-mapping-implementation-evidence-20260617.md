# Docling Dedicated Extractor Template-field Mapping Implementation Evidence - 2026-06-17

Gate: `Docling Dedicated Extractor Template-field Mapping No-live Implementation Gate`
Role: implementation worker
Accepted plan commit: `d48aa9f`
Status: `IMPLEMENTATION_COMPLETE_NOT_READY`
Verdict: `IMPLEMENTATION_READY_FOR_CODE_REVIEW_NOT_READY`
Release/readiness: `NOT_READY`

## Changed Files

- `fund_agent/fund/documents/candidates/template_field_extraction.py`
- `tests/fund/documents/test_docling_template_field_extraction.py`

## Implementation Summary

Implemented a no-live Docling dedicated template-field candidate extractor.

Accepted implementation facts:

- Adds `DOCLING_TEMPLATE_FIELD_SCHEMA_VERSION = "docling_template_field_candidates.v1"`.
- Adds exact `DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS`.
- Adds candidate-only output dataclasses:
  - `CandidateTemplateFieldAnchor`
  - `CandidateTemplateField`
  - `DoclingTemplateFieldExtractionResult`
- Adds public function `extract_docling_template_fields(document, target_field_paths=...)`.
- Consumes `CandidateRepresentationDocument` directly.
- Does not consume `CandidateEvidenceAnchorMappingResult`.
- Does not create or return production `EvidenceAnchor`.
- Rejects non-Docling candidate source kinds.
- Rejects candidate documents whose proof/status fields cross `not_proven` / `not_authorized` boundaries.
- Rejects candidate template anchors whose note does not start with `candidate_only:`.
- Emits exactly one field per requested target field path.
- Emits explicit `extraction_mode="missing"` for unmatched or deferred paths.

Implemented deterministic candidate matching for:

- `basic_identity.fund_name`
- `basic_identity.fund_code`
- `basic_identity.management_company`
- `basic_identity.custodian`
- `product_profile.investment_objective`
- `product_profile.investment_scope`
- `benchmark.benchmark_text`
- `risk_characteristic_text.risk_characteristic_text`
- `fee_schedule.management_fee`
- `fee_schedule.custody_fee`
- `nav_benchmark_performance.nav_growth_rate`
- `nav_benchmark_performance.benchmark_return_rate`
- `tracking_error.value_text`
- `portfolio_managers`
- `turnover_rate`
- `manager_alignment.manager_holding_range`
- `holdings_snapshot.top_holdings`
- `holdings_snapshot.bond_top_holdings`
- `holdings_snapshot.target_fund_holdings`

Deferred fields are still emitted as explicit missing:

- `manager_strategy_text`
- `holder_structure`
- `share_change`
- `bond_risk_evidence`

## Validation

Command:

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py -q
```

Result:

```text
10 passed
```

Command:

```text
uv run ruff check fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py
```

Result:

```text
All checks passed!
```

Command:

```text
git diff --check -- fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py docs/reviews/docling-dedicated-extractor-template-field-mapping-implementation-evidence-20260617.md
```

Result: pass.

Controller rerun after code-review follow-up:

```text
git diff --check -- fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py docs/reviews/docling-dedicated-extractor-template-field-mapping-implementation-evidence-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-code-review-ds-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-code-review-mimo-20260617.md
```

Result: pass.

Final controller validation:

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py -q
```

Result: `10 passed in 0.72s`.

```text
uv run ruff check fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py
```

Result: `All checks passed!`.

```text
git diff --check -- fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py docs/reviews/docling-dedicated-extractor-template-field-mapping-implementation-evidence-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-code-review-ds-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-code-review-mimo-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-code-rereview-ds-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-code-rereview-mimo-20260617.md
```

Result: pass.

## Code-review Follow-up

After DS/MiMo code review, the implementation added non-blocking hardening:

- `CandidateTemplateFieldAnchor.__post_init__` now requires `note.startswith("candidate_only:")`.
- Tests now cover empty, duplicate, and unsupported `target_field_paths`.
- Tests now cover text-label fallback when no table is present.
- Tests now cover candidate anchor note prefix rejection.

## Boundary Confirmation

This implementation does not:

- modify `FundDataExtractor`;
- integrate with production report generation;
- change Service/UI/Host/renderer/quality-gate behavior;
- run live/network/provider/LLM/analyze/checklist/golden/readiness/release/PR commands;
- directly access PDF/cache/source-helper;
- run fresh Docling conversion or repository reload;
- accept source truth;
- promote Docling baseline;
- replace production parser;
- prove full field correctness;
- claim golden/readiness/release/PR readiness.

The following remain binding:

- candidate-only output;
- `source_truth_status="not_proven"`;
- release/readiness remains `NOT_READY`.

## Residual Risks

- The extractor is not consumed by `FundDataExtractor` or report generation yet.
- Tests use synthetic `CandidateRepresentationDocument` objects, not real annual-report source truth.
- Numeric normalization, unit conversion, multi-year semantics, QDII/FOF specifics, and full CHAPTER_CONTRACT coverage are not proven.
- Production projection to `ExtractedField` / `EvidenceAnchor` remains a later gate.

VERDICT: `IMPLEMENTATION_READY_FOR_CODE_REVIEW_NOT_READY`
