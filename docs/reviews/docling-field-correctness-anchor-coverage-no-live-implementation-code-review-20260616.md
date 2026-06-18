# Docling Field Correctness Anchor Coverage No-live Implementation Code Review - 2026-06-16

Gate: `Docling Field Correctness Anchor Coverage No-live Implementation Code Review Gate`
Role: code reviewer
Release/readiness: `NOT_READY`

## 1. Review Inputs

Reviewed implementation and evidence:

- `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`
- `tests/fund/documents/test_docling_evidence_anchor_mapping.py`
- `docs/reviews/docling-field-correctness-anchor-coverage-no-live-implementation-evidence-20260616.md`
- `reports/docling-field-correctness-anchor-coverage-no-live-implementation/20260616/anchor_coverage_after_matrix.json`

Accepted planning and controller inputs:

- `docs/reviews/docling-field-correctness-anchor-coverage-no-live-implementation-plan-20260616.md`
- `docs/reviews/docling-field-correctness-anchor-coverage-no-live-implementation-plan-controller-judgment-20260616.md`

## 2. Findings

No blocking findings.

## 3. Scope Review

The implementation stayed within the accepted write set:

- candidate section-context mapping helper only;
- targeted mapping tests only;
- implementation evidence artifact;
- no-live after-matrix JSON.

No public `EvidenceAnchor` schema, `EvidenceSourceKind`, FundDocumentRepository, source policy, Service, Host, UI, renderer, quality gate, provider/LLM, golden, release, PR, push, or merge behavior was changed.

## 4. Behavior Review

The implementation addresses the accepted root-cause surface:

| Root-cause family | Review result |
| --- | --- |
| `duplicate_section_heading` | Later same-section body headings no longer automatically block stable page-span mapping; same-page duplicate and front-matter ambiguity remain fail-closed. |
| `missing_section_context` | Soft unindexed internal boundaries no longer truncate a stable supported section before the next supported section start; final unsupported boundary behavior remains covered. |

The changed rules remain deterministic and do not introduce field-specific manual exceptions.

## 5. Test And Evidence Review

Reviewed targeted test coverage:

| Required area | Covered by |
| --- | --- |
| later duplicate heading maps stable table cell | `test_later_duplicate_body_heading_maps_page_based_propagation` |
| same-page duplicate remains blocked | `test_duplicate_same_page_top_level_body_heading_blocks_page_based_propagation` |
| TOC/body ambiguity remains blocked | `test_unsafe_toc_body_ambiguity_blocks_as_duplicate_section_heading` |
| non-monotonic section order remains blocked | `test_inter_section_monotonic_violation_blocks_affected_span` |
| soft unindexed internal boundary does not close stable span | `test_soft_unindexed_internal_boundary_does_not_close_stable_span` |
| unsupported final boundary still blocks outside page | `test_unsupported_section_node_closes_previous_stable_section_span` |
| cross-section multi-page table remains blocked | `test_cross_section_multi_page_table_blocks_before_page_number_selection` |
| candidate wrapper invariants remain unchanged | `test_document_mapping_emits_candidate_wrappers_for_heading_paragraph_table_and_cell` |

Reviewed after-matrix requirements:

| Requirement | Review result |
| --- | --- |
| input artifact paths and SHA-256 values | present |
| before metrics | `44 / 72` anchor present, `28` missing |
| after metrics | `72 / 72` anchor present, `0` missing |
| prior missing row disposition | `28 / 28` mapped, `0` residual |
| S5 positive control | `17 / 17` preserved |
| negative guards | `not_source_truth=true`, `not_full_field_correctness=true`, `not_production_parser_replacement=true`, `not_readiness_proof=true` |

## 6. S6-F041 Review

S6-F041 is counted only because the accepted comparative input maps `benchmark` to the shared S6-F040/S6-F041 candidate cell and marks it as exact/normalized match.

This review does not accept S6-F041 as source truth or full benchmark semantic correctness. The implementation evidence correctly records the upstream field-assignment residual for a future source-truth or full field-correctness gate.

## 7. Validation Observed

Commands observed during review:

```bash
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
python -m json.tool reports/docling-field-correctness-anchor-coverage-no-live-implementation/20260616/anchor_coverage_after_matrix.json >/dev/null
git diff --check
jq '.input_artifacts, (.prior_missing_rows | length), (.rows | length), (.residual_rows | length), .not_source_truth, .not_full_field_correctness, .not_production_parser_replacement, .not_readiness_proof' reports/docling-field-correctness-anchor-coverage-no-live-implementation/20260616/anchor_coverage_after_matrix.json
```

Observed results:

| Check | Result |
| --- | --- |
| Targeted tests | `37 passed` |
| JSON validation | passed |
| Diff whitespace check | passed |
| Prior missing row count | `28` |
| Reviewed row count | `72` |
| Residual row count | `0` |
| Negative guards | all true |

## 8. Residuals

Residuals preserved:

- candidate field correctness remains `not_proven`;
- source truth remains `not_proven`;
- Docling candidate remains non-production and non-readiness evidence;
- S6-F041 semantic benchmark correctness remains upstream residual;
- release/readiness remains `NOT_READY`.

## 9. Verdict

```text
VERDICT: REVIEW_PASS_NOT_READY
```
