# Docling Dedicated Extractor Section-context Remediation Code Re-review - 2026-06-17

Gate: `Docling Dedicated Extractor Section-context Remediation Implementation Gate`
Role: code re-review
Base review: `docs/reviews/code-review-20260617-180704.md`
Status: `CODE_REREVIEW_PASS_NOT_READY`
Verdict: `CODE_REREVIEW_PASS_NOT_READY`

## Reviewed Fix

Finding `001` accepted fix:

- Added `_SectionContextCache`.
- Created the cache once in `extract_docling_template_fields()`.
- Passed the cache through field matcher calls.
- `_effective_section_id()` now stores resolved section IDs or `None` per block identity.

## Validation

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
```

Result:

```text
50 passed in 0.68s
```

```text
uv run ruff check fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py
```

Result:

```text
All checks passed!
```

Re-evidence result after fix:

```text
{"anchor_count": 52, "blocked_slot_count": 0, "direct_coverage_ratio": 0.5217391304347826, "direct_slot_count": 48, "missing_ratio": 0.4782608695652174, "missing_slot_count": 44, "sample_count": 4, "target_field_slot_count": 92}
```

## Finding Disposition

| Finding | Status | Evidence |
|---|---|---|
| 001 section context resolution recomputed inside matcher scans | 已修复 | cache added; tests pass; re-evidence result stable; runtime reduced from roughly 29s to roughly 8s |

## Residual Risk

- The cache is scoped to one extraction call and keyed by block identity; it is not persisted and does not alter output schema.
- Candidate direct hits still require later field correctness comparison.

VERDICT: `CODE_REREVIEW_PASS_NOT_READY`
