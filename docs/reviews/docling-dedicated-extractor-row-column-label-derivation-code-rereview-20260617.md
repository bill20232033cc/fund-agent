# Docling Dedicated Extractor Row-column Label Derivation Code Re-review - 2026-06-17

Gate: `Docling Dedicated Extractor Row-column Label Derivation Code Re-review`
Prior review: `docs/reviews/code-review-20260617-221818.md`
Status: `CODE_REVIEW_FINDINGS_FIXED_NOT_READY`
Release/readiness: `NOT_READY`

## Finding Disposition

| Finding | Disposition | Evidence |
|---|---|---|
| `001` column_header flag can turn non-header row 0 into a derived header | 已修复 | `_is_header_like_row` no longer treats `cell.column_header` as independent header evidence. Added regression coverage for structural `column_header=True` rows without semantic header labels. |

## Validation

Command:

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
```

Result:

```text
56 passed in 0.41s
```

Command:

```text
uv run ruff check fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py
```

Result:

```text
All checks passed!
```

## Residual Risks

- Real-envelope coverage uplift is not proven by synthetic tests and must be measured in the re-evidence gate.
- Candidate-only outputs still do not prove field correctness or source truth.

VERDICT: `CODE_REVIEW_FIXED_ROW_COLUMN_LABEL_DERIVATION_NOT_READY`
