# Docling Dedicated Extractor Section-context Remediation Controller Judgment - 2026-06-17

Gate: `Docling Dedicated Extractor Section-context Remediation Gate`
Role: controller
Accepted plan commit: `29f4fab`
Status: `IMPLEMENTATION_AND_REEVIDENCE_ACCEPTED_NOT_READY`
Verdict: `ACCEPT_SECTION_CONTEXT_REMEDIATION_ROUTE_TO_ROW_COLUMN_LABEL_DERIVATION_PLANNING_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs

- Plan: `docs/reviews/docling-dedicated-extractor-section-context-remediation-plan-20260617.md`
- Plan review: `docs/reviews/plan-review-20260617-180205.md`
- Implementation evidence: `docs/reviews/docling-dedicated-extractor-section-context-remediation-implementation-evidence-20260617.md`
- Code review: `docs/reviews/code-review-20260617-180704.md`
- Code re-review: `docs/reviews/docling-dedicated-extractor-section-context-remediation-code-rereview-20260617.md`
- Re-evidence: `docs/reviews/docling-dedicated-extractor-section-context-remediation-reevidence-20260617.md`
- Matrix: `reports/docling-dedicated-extractor-section-context-remediation-reevidence/20260617/template_field_coverage_after_section_context.json`

## Decision

Accept the section-context remediation implementation and re-evidence.

The accepted diagnostic primary cause has been materially remediated:

- direct candidate field slots improved from `0 / 92` to `48 / 92`;
- candidate anchors improved from `0` to `52`;
- the same four runnable current-schema Docling envelopes were used.

## Accepted Facts

- The implementation reuses accepted candidate EvidenceAnchor mapping section resolution.
- The implementation does not modify `representation_projection.py`.
- The implementation does not modify `FundDataExtractor`.
- The implementation does not expose production `EvidenceAnchor`.
- Duplicate section context remains fail-closed.
- Explicit `§N` section IDs remain fast-path compatible.
- Section-context results are cached within one extraction call.
- All outputs remain candidate-only and `source_truth_status="not_proven"`.
- Release/readiness remains `NOT_READY`.

## Review Disposition

| Review Finding | Controller disposition |
|---|---|
| `001` section context resolution recomputed inside matcher scans | Accepted and fixed |

No blocking code-review finding remains.

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

## Boundary

This judgment does not authorize:

- field correctness claims;
- source-truth acceptance;
- parser replacement;
- Docling baseline promotion;
- production integration;
- `FundDataExtractor` consumption;
- release/readiness/PR claims.

## Residual Owner

Next gate:

`Docling Dedicated Extractor Row-column Label Derivation Planning Gate`

Purpose:

- derive candidate row/column label paths;
- improve performance table, holdings table, and other table-semantic fields;
- preserve fail-closed and candidate-only boundaries;
- re-evidence on the same four accepted current-schema Docling envelopes.

VERDICT: `ACCEPT_SECTION_CONTEXT_REMEDIATION_ROUTE_TO_ROW_COLUMN_LABEL_DERIVATION_PLANNING_NOT_READY`
