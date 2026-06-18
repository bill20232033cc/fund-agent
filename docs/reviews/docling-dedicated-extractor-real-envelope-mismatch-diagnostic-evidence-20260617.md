# Docling Dedicated Extractor Real-envelope Mismatch Diagnostic Evidence - 2026-06-17

Gate: `Docling Dedicated Extractor Real-envelope Mismatch Diagnostic Evidence Gate`
Role: evidence worker
Accepted plan commit: `dbd77fd`
Status: `DIAGNOSTIC_COMPLETE_NOT_READY`
Verdict: `REAL_ENVELOPE_MISMATCH_PRIMARY_SECTION_BLOCK_UNLINKED_NOT_READY`
Release/readiness: `NOT_READY`

## Evidence Artifacts

- Matrix: `reports/docling-dedicated-extractor-real-envelope-mismatch-diagnostic/20260617/real_envelope_shape_matrix.json`
- Plan: `docs/reviews/docling-dedicated-extractor-real-envelope-mismatch-diagnostic-plan-20260617.md`
- Prior negative evidence: `docs/reviews/docling-dedicated-extractor-candidate-field-no-live-evidence-20260617.md`

## Scope

This diagnostic inspected the four runnable current-schema Docling candidate envelopes that produced zero candidate-field hits in the previous gate.

It did not:

- modify extractor rules;
- modify representation projection;
- run fresh Docling conversion;
- access PDF/cache/source helpers directly;
- compare field values with source truth;
- claim field correctness, source truth, baseline promotion, parser replacement, production integration, release readiness, or PR readiness.

## Aggregate Result

| Metric | Value |
|---|---:|
| Sample count | 4 |
| Field slots classified | 92 |
| `section_candidates_exist_but_blocks_unlinked` | 74 |
| `deferred_by_plan` | 16 |
| `section_id_absent_or_not_projected` | 2 |

## Per-sample Shape Facts

| Sample | Fund | Year | Sections | Text blocks | Tables | Cells | Table section IDs | Text section IDs | Table family | Row label paths | Column header paths |
|---|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| S1 | 004393 | 2025 | 25 | 670 | 95 | 3493 | all `None` | all `None` | all `unknown` | 0 | 0 |
| S4 | 006597 | 2024 | 229 | 737 | 96 | 2759 | all `None` | all `None` | all `unknown` | 0 | 0 |
| S5 | 017641 | 2024 | 208 | 856 | 121 | 7060 | all `None` | all `None` | all `unknown` | 0 | 0 |
| S6 | 110020 | 2024 | 222 | 840 | 124 | 5940 | all `None` | all `None` | all `unknown` | 0 | 0 |

## Label Presence

The diagnostic found many target labels in candidate text or table cells, including examples such as:

- `业绩比较基准`
- `基金名称`
- `基金托管人`
- `基金管理人`
- `托管费`
- `管理费`
- `投资目标`
- `股票名称`
- `公允价值`
- `占基金资产净值比例`
- `姓名`
- `任职日期`

Therefore the zero candidate-field coverage should not be interpreted as source absence.

## Root-cause Classification

Primary cause:

- `section_candidates_exist_but_blocks_unlinked`

Evidence:

- Section headings are present and can often be heuristically associated with expected report chapters.
- Extractor requires concrete section IDs such as `§2`, `§3`, `§4`, `§7`, `§8`, `§10`.
- Projected `CandidateTextBlock.section_id` is `None` for all sampled text blocks.
- Projected `CandidateTableBlock.section_id` is `None` for all sampled tables.
- As a result, `_section_allowed(block.section_id, ...)` and `_section_allowed(table.section_id, ...)` reject all real envelope content before label matching can succeed.

Contributing cause:

- `row_column_paths_absent`

Evidence:

- Across all four samples, `row_label_path` non-empty count is `0`.
- Across all four samples, `column_header_path` non-empty count is `0`.
- Performance, manager, and holdings matchers depend on row/column labels or header-derived cells.

Contributing cause:

- `table_family_unknown`

Evidence:

- Across all four samples, every projected table has `table_family="unknown"`.
- The current extractor does not directly require table family, but later field-specific remediation and stabilization will need it to avoid false positives.

Deferred cause:

- `deferred_by_plan`

Evidence:

- `manager_strategy_text`, `holder_structure`, `share_change`, and `bond_risk_evidence` were intentionally deferred in the accepted extractor implementation.
- Four deferred fields across four samples account for 16 of 92 classified field slots.

Residual cause:

- `section_id_absent_or_not_projected`

Evidence:

- Two S1 fee fields are classified this way because the diagnostic did not find an accepted section candidate matching the extractor's fee-section expectation.
- This remains a residual and should not drive the first remediation slice.

## Interpretation

The previous 0/92 coverage result is now explained enough to choose a remediation direction:

1. First remediation should propagate normalized section context from candidate section headings to text blocks and tables.
2. Second remediation should derive row/column label paths from table cells.
3. Field-specific matcher changes should come after section linkage and label derivation, not before.

This remains candidate-only evidence. It does not prove field correctness.

## Validation

Command:

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py tests/fund/documents/test_candidate_representation_projection.py -q
```

Result:

```text
15 passed in 0.38s
```

No-live matrix generation command:

```text
uv run python -c '<load four accepted current-schema Docling envelopes; project_candidate_representation(payload); classify section/table/text/label-path shapes; write real_envelope_shape_matrix.json>'
```

Result:

```text
{"failure_classification_counts": {"deferred_by_plan": 16, "section_candidates_exist_but_blocks_unlinked": 74, "section_id_absent_or_not_projected": 2}, "field_slot_count": 92, "sample_count": 4}
```

## Residual Risks

Assigned to next remediation planning gate:

- Specify how normalized section IDs should be derived and attached without accepting source truth.
- Decide whether section context belongs in `representation_projection.py`, upstream representation export, or a new candidate-only enrichment layer.
- Define deterministic fail-closed behavior for ambiguous section spans.

Assigned to later row/column label derivation gate:

- Populate row and column label paths for candidate tables.
- Validate manager/performance/holdings fields after section linkage is fixed.

Assigned to later field contract stabilization:

- Stabilize missing/block reason taxonomy and multi-row candidate values.

Assigned to later comparative correctness:

- Compare candidate fields against production truth or independent source truth.

## Next Gate Recommendation

Recommended next gate:

`Docling Dedicated Extractor Section-context Remediation Planning Gate`

Purpose:

- plan the minimal candidate-only change that links text blocks and tables to normalized report sections;
- preserve fail-closed behavior when section span or heading hierarchy is ambiguous;
- produce enough coverage uplift to justify row/column label derivation.

VERDICT: `REAL_ENVELOPE_MISMATCH_PRIMARY_SECTION_BLOCK_UNLINKED_NOT_READY`
