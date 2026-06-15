# Candidate Representation Schema No-live Implementation Evidence

## Scope

Gate: `Candidate Representation Schema No-live Implementation Gate`

This evidence covers a Fund documents internal candidate-only schema and projection layer for already-generated candidate representation JSON.

Implemented files:

- `fund_agent/fund/documents/candidates/representation_models.py`
- `fund_agent/fund/documents/candidates/representation_projection.py`
- `tests/fund/documents/test_candidate_representation_models.py`
- `tests/fund/documents/test_candidate_representation_projection.py`
- `fund_agent/fund/README.md`

## Accepted Plan Basis

Accepted plan:

- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-no-live-implementation-plan-20260615.md`

Accepted controller judgment:

- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-no-live-implementation-plan-controller-judgment-20260615.md`

## Implementation Summary

The implementation adds candidate-internal dataclasses for:

- closed source kinds:
  - `docling_pdf_candidate`
  - `pdfplumber_pdf_candidate`
  - `eid_xbrl_html_render_candidate`
- candidate identity and non-proof status
- route-specific source locators
- section, text block, table, and cell models
- route failure and projection issue records
- candidate-only anchor notes that do not modify public `EvidenceAnchor`

The projection layer converts accepted candidate representation envelopes into those dataclasses while preserving route-specific locator differences:

- Docling PDF candidates preserve page number, source refs, bbox, table ids, row/column offsets, row/column header flags, hashes, and cell locators when present.
- pdfplumber PDF candidates synthesize cell locators from `headers` + `rows` without inventing bbox.
- Row/column zero offsets are preserved as valid locator coordinates instead of being treated as missing values.
- EID HTML render blocked candidates preserve route failure taxonomy without creating table or field facts.

## Boundary Evidence

The implementation does not:

- change `FundDocumentRepository`
- change annual-report source policy
- change production parser behavior
- add Service/UI/Host/renderer/quality gate access to candidate internals
- modify public `EvidenceAnchor` schema
- consume Docling/pdfplumber/EID HTML from production runtime
- claim field correctness
- claim source truth
- claim taxonomy compatibility
- claim parser replacement
- change release/readiness status

Candidate status guards are enforced by model constructors and projection validation:

- `candidate_status = not_proven`
- `field_correctness_status = not_proven`
- `source_truth_status = not_proven`
- `taxonomy_compatibility_status = not_proven`
- `production_parser_replacement_status = not_authorized`

Projection also requires the standard blocked-claim guards, including:

- `not_raw_xml_download_proof`
- `not_field_correctness_proof`
- `not_taxonomy_compatibility_proof`
- `not_source_truth`
- `not_readiness_proof`
- `no_repository_behavior_change`
- `no_parser_replacement`

## Validation

Command:

```bash
uv run pytest tests/fund/documents/test_candidate_representation_models.py tests/fund/documents/test_candidate_representation_projection.py tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Result:

```text
11 passed in 0.47s
```

Command:

```bash
uv run ruff check fund_agent/fund/documents/candidates/representation_models.py fund_agent/fund/documents/candidates/representation_projection.py tests/fund/documents/test_candidate_representation_models.py tests/fund/documents/test_candidate_representation_projection.py
```

Result:

```text
All checks passed!
```

Command:

```bash
git diff --check
```

Result:

```text
PASS
```

Additional compatibility command:

```bash
uv run pytest tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_models.py tests/fund/documents/test_candidate_representation_projection.py tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Result:

```text
35 passed in 2.51s
```

## Review-driven Fixes Before Rereview

| Finding | Source | Fix |
| --- | --- | --- |
| Zero-valued row/column offsets were at risk of being treated as missing values. | MiMo implementation review | Projection now uses first-present semantics that preserves `0`; tests assert Docling and pdfplumber zero offsets survive projection. |
| Docling row/column header flags were not represented in candidate cells. | DS implementation review | `CandidateTableCell` now stores `row_header` and `column_header`; projection maps them and tests assert preservation. |

## Residuals

| Residual | Status | Owner |
| --- | --- | --- |
| Locator stability is structurally represented but not empirically accepted across full sample JSON. | Deferred to next evidence gate. | Controller |
| Candidate anchor note remains internal and is not public `EvidenceAnchor`. | Accepted boundary. | Controller |
| EID HTML render route remains blocked for samples without accepted render artifact payload. | Accepted residual. | Controller |
| Structural representation is not field correctness, source truth, taxonomy proof, parser replacement, or readiness. | Accepted residual. | Controller |

## Verdict Candidate

`IMPLEMENTATION_READY_FOR_REVIEW_NOT_READY`

Recommended next gate after review/controller acceptance:

`Candidate Representation Locator Stability Evidence Gate`
