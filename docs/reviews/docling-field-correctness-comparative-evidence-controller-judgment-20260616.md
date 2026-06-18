# Docling Field Correctness Comparative Evidence Controller Judgment - 2026-06-16

Gate: `Docling Field Correctness Comparative Evidence Gate`
Controller role: AgentController
Release/readiness: `NOT_READY`

## Scope

This judgment closes review of the no-live comparative correctness evidence for accepted local Docling candidate mappings.

This judgment does not authorize production parser replacement, production `EvidenceAnchor` admission, source acquisition, source policy change, Service/Host/UI/renderer/quality gate change, provider/LLM route change, Docling baseline promotion, readiness, release, PR, push or merge.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-field-correctness-comparative-evidence-20260616.md` | evidence artifact |
| `reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json` | machine-readable field comparison matrix |
| `reports/docling-field-correctness-comparative/20260616/reference_coverage_matrix.json` | machine-readable reference coverage matrix |
| `docs/reviews/docling-field-correctness-comparative-evidence-review-ds-20260616.md` | DS review |
| `docs/reviews/docling-field-correctness-comparative-evidence-review-mimo-20260616.md` | MiMo review |

## Accepted Facts

- D2 scoring is limited to `docling_pdf_candidate` rows with accepted reviewed reference facts.
- The 4 S1 `pdfplumber_pdf_candidate` comparator rows are D1 route-disagreement context only and are not scored as Docling D2 correctness.
- Selected Docling reviewed fact values match accepted same-source references in `72 / 72` cases.
- Candidate EvidenceAnchor mapping is present for only `44 / 72` accepted Docling reviewed facts.
- Missing candidate anchor mappings total `28 / 72`; main sample gaps are S4 `11 / 17` missing and S6 `14 / 17` missing.
- Locator collision count for mapped cells by `(table, row, column)` is `0`.
- S2 and S3 remain unscored because current gate inputs do not contain accepted same-report reviewed/golden reference facts.
- Candidate mappings preserve `field_correctness_status="not_proven"` and `source_truth_status="not_proven"`.
- Evidence and reviews preserve `NOT_READY` and do not claim source truth, full field correctness, production parser replacement, baseline promotion, readiness, release or PR.

## Review Finding Disposition

| Reviewer | Verdict | Controller disposition |
| --- | --- | --- |
| AgentDS | `REVIEW_PASS_NOT_READY` | ACCEPTED |
| AgentMiMo | `REVIEW_PASS_NOT_READY` | ACCEPTED |

No reviewer reported a blocking issue requiring evidence artifact or JSON repair before controller judgment.

DS noted two non-blocking residuals:

- `reference_coverage_matrix.json` lacks a separate `not_production_parser_replacement` field, while the primary comparison matrix contains it. This is accepted as non-blocking because the evidence artifact and primary matrix deny production parser replacement and no overclaim depends on the coverage matrix alone.
- D1 route-disagreement rows record fact identity and reason, not full pdfplumber-side values. This is accepted as non-blocking for the current gate because D1 rows are not used as truth or D2 score input.

## Controller Decision

The comparative evidence is accepted as a narrow selected-fact value-correctness signal and as a fail-closed blocker signal for Gate D.

The evidence confirms that reviewed Docling values are exact or normalized matches for the currently accepted selected facts. It also confirms that current candidate EvidenceAnchor mapping coverage is insufficient for Gate D pass criteria, because comparable accepted fields require anchor presence and only `44 / 72` accepted Docling reviewed facts have candidate anchors.

Therefore this gate is not accepted as a Docling baseline-candidate pass. It is accepted as blocked comparative evidence.

## Residuals

| Residual | Status | Next owner |
| --- | --- | --- |
| EvidenceAnchor presence is `44 / 72` for accepted Docling reviewed facts. | blocking for Gate D pass threshold | Fund documents candidate mapping owner |
| S4 anchor coverage is `6 / 17`; S6 anchor coverage is `3 / 17`. | sample-specific mapping gap | Fund documents candidate mapping owner |
| S2/S3 lack accepted reviewed reference facts. | blocks full sample-matrix field-correctness verdict | reference establishment owner |
| S5/S6 profile-specific high-priority family coverage remains partial. | limits evidence to selected facts | reference establishment owner |
| EID HTML render route is accepted only for S1. | no tri-route comparative claim for S4/S5/S6 | EID HTML availability owner |
| Source truth, full field correctness, production parser replacement and baseline disposition remain unproven. | explicit non-proof | future baseline disposition owner |
| Release/readiness remains `NOT_READY`. | preserved | future readiness gate |

## Next Gate Recommendation

Do not proceed to `Docling Performance / Cache / Cost Evidence Gate` from this evidence state. Performance evidence cannot resolve the current Gate D blocker.

Proceed instead to a planning/root-cause gate for the anchor coverage gap:

```text
Docling Field Correctness Anchor Coverage Root-cause Planning Gate
```

The next gate should explain why accepted reviewed facts for S4/S6 and selected families lack candidate anchors despite value matches, and should decide whether the fix belongs in section-context mapping, table/cell locator normalization, reference-to-anchor join logic, or reduced-scope controller disposition.

## Final Verdict

```text
VERDICT: ACCEPT_SELECTED_FIELD_VALUE_MATCH_ANCHOR_COVERAGE_BLOCKED_NOT_READY
```
