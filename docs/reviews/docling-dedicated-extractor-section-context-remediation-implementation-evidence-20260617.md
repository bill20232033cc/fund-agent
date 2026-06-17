# Docling Dedicated Extractor Section-context Remediation Implementation Evidence - 2026-06-17

Gate: `Docling Dedicated Extractor Section-context Remediation Implementation Gate`
Role: implementation worker
Accepted plan commit: `29f4fab`
Status: `IMPLEMENTATION_COMPLETE_NOT_READY`
Verdict: `SECTION_CONTEXT_REMEDIATION_IMPLEMENTED_NOT_READY`
Release/readiness: `NOT_READY`

## Changed Files

- `fund_agent/fund/documents/candidates/template_field_extraction.py`
- `tests/fund/documents/test_docling_template_field_extraction.py`

## Implementation Summary

Implemented candidate-only effective section context resolution for the Docling dedicated template-field extractor.

Accepted implementation facts:

- Reuses `map_candidate_locator_to_anchor_candidate()` from candidate EvidenceAnchor mapping.
- Does not implement a second section parser in the template extractor.
- Keeps section resolution private to candidate template extraction.
- Resolves effective sections for tables and text blocks whose raw `section_id` is `None`.
- Keeps fail-closed behavior when candidate mapping cannot return exactly one mapped section.
- Keeps explicit `§N` section IDs as the direct fast path.
- Adds extraction-scope section context cache keyed by block identity.
- Uses schema family convention only as a candidate-internal helper:
  - `S1_full` for sample `S1`;
  - `S4_S5_S6_lightweight` otherwise.
- Emits direct anchors with the effective section ID when a field is matched through resolved section context.

The implementation does not:

- modify `representation_projection.py`;
- modify `FundDataExtractor`;
- modify production `EvidenceAnchor`;
- derive row/column label paths;
- classify `table_family`;
- access PDF/cache/source helpers directly;
- run fresh Docling conversion;
- claim source truth, field correctness, baseline promotion, parser replacement, release readiness, or PR readiness.

## Tests

New tests:

- `test_docling_template_field_extractor_uses_page_section_context_for_unlinked_table`
- `test_docling_template_field_extractor_uses_page_section_context_for_unlinked_text`
- `test_docling_template_field_extractor_keeps_duplicate_section_context_missing`

Validation command:

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
```

Result:

```text
50 passed
```

Validation command:

```text
uv run ruff check fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py
```

Result:

```text
All checks passed!
```

## Code Review Follow-up

Code review artifact: `docs/reviews/code-review-20260617-180704.md`

Accepted finding:

- `001`: section context resolution was recomputed inside every matcher scan.

Fix:

- Added extraction-scope `_SectionContextCache`.
- Passed the cache through field matchers.
- `_effective_section_id()` now resolves each block at most once per extraction call.

Post-fix validation:

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

## Re-evidence

Matrix:

`reports/docling-dedicated-extractor-section-context-remediation-reevidence/20260617/template_field_coverage_after_section_context.json`

Aggregate result:

```text
{"anchor_count": 52, "blocked_slot_count": 0, "direct_coverage_ratio": 0.5217391304347826, "direct_slot_count": 48, "missing_ratio": 0.4782608695652174, "missing_slot_count": 44, "sample_count": 4, "target_field_slot_count": 92}
```

Compared with prior accepted evidence:

- direct slots: `0 -> 48`;
- missing slots: `92 -> 44`;
- anchor count: `0 -> 52`;
- direct coverage ratio: `0.0 -> 0.5217391304347826`.

The rerun after cache fix preserved the same coverage result and reduced the local re-evidence command from roughly 29 seconds to roughly 8 seconds.

## Residual Risks

Assigned to next row/column label derivation gate:

- `nav_benchmark_performance.nav_growth_rate`
- `nav_benchmark_performance.benchmark_return_rate`
- `tracking_error.value_text`
- remaining holdings paths not covered across all samples

Assigned to later table-family stabilization gate:

- false-positive controls for table-specific matching.

Assigned to later comparative correctness gate:

- all direct candidate hits still need field correctness comparison.

Assigned to later integration gate:

- production projection, quality-gate semantics, and `FundDataExtractor` consumption.

VERDICT: `SECTION_CONTEXT_REMEDIATION_IMPLEMENTED_NOT_READY`
