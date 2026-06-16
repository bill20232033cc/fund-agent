# Docling Field Correctness Anchor Coverage No-live Implementation Evidence - 2026-06-16

Gate: `Docling Field Correctness Anchor Coverage No-live Implementation Gate`
Role: implementation worker
Release/readiness: `NOT_READY`

## 1. Scope

This gate implements the accepted no-live plan from:

- `docs/reviews/docling-field-correctness-anchor-coverage-no-live-implementation-plan-20260616.md`
- `docs/reviews/docling-field-correctness-anchor-coverage-no-live-implementation-plan-controller-judgment-20260616.md`

Implementation write set:

- `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`
- `tests/fund/documents/test_docling_evidence_anchor_mapping.py`

Evidence write set:

- `reports/docling-field-correctness-anchor-coverage-no-live-implementation/20260616/anchor_coverage_after_matrix.json`
- `docs/reviews/docling-field-correctness-anchor-coverage-no-live-implementation-evidence-20260616.md`

This gate did not run live/network/source acquisition/PDF/FDR/Docling conversion/pdfplumber export/provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands.

## 2. Implementation Summary

Changed candidate section-context mapping only:

1. `_duplicate_sections()` now blocks duplicate annual-report section starts only when deterministic disambiguation is unsafe:
   - same-page top-level duplicate;
   - front-matter ambiguous duplicate;
   - selected start page shared by multiple supported sections.
2. Later same-section duplicate headings can now use the earliest stable body start when the above unsafe cases do not apply.
3. `_section_spans()` now prefers the next supported stable section start over unindexed internal boundary pages.
4. Unindexed boundary pages still close the final stable span when no next supported section start exists.
5. Public candidate mapping result types, public function signatures, `candidate_only=True`, `field_correctness_status="not_proven"` and `source_truth_status="not_proven"` are unchanged.

No public `EvidenceAnchor` schema, source policy, parser replacement policy, Service/Host/UI/renderer/quality gate behavior, or FundDocumentRepository behavior changed.

## 3. Test Coverage

Updated targeted tests in `tests/fund/documents/test_docling_evidence_anchor_mapping.py`:

| Test area | Evidence |
| --- | --- |
| Later duplicate body heading maps stable page span | `test_later_duplicate_body_heading_maps_page_based_propagation` |
| Same-page duplicate remains fail-closed | existing `test_duplicate_same_page_top_level_body_heading_blocks_page_based_propagation` |
| TOC/body ambiguity remains fail-closed | existing `test_unsafe_toc_body_ambiguity_blocks_as_duplicate_section_heading` |
| Non-monotonic section order remains fail-closed | existing `test_inter_section_monotonic_violation_blocks_affected_span` |
| Soft unindexed internal boundary no longer closes stable span | `test_soft_unindexed_internal_boundary_does_not_close_stable_span` |
| Unsupported final boundary still blocks outside page | existing `test_unsupported_section_node_closes_previous_stable_section_span` |
| Multi-page table crossing stable sections remains fail-closed | existing `test_cross_section_multi_page_table_blocks_before_page_number_selection` |
| Candidate-only wrapper invariants remain unchanged | existing `test_document_mapping_emits_candidate_wrappers_for_heading_paragraph_table_and_cell` |

Observed targeted test result:

```text
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
37 passed
```

## 4. After Matrix

Generated:

```text
reports/docling-field-correctness-anchor-coverage-no-live-implementation/20260616/anchor_coverage_after_matrix.json
```

The matrix was generated no-live from accepted local candidate envelopes and current candidate mapping helpers.

Before:

| Metric | Value |
| --- | ---: |
| Accepted Docling reviewed facts | `72` |
| Anchor present for reviewed facts | `44` |
| Missing anchor count | `28` |
| Value exact or normalized matches | `72` |
| S5 positive-control anchors | `17 / 17` |

After:

| Metric | Value |
| --- | ---: |
| Accepted Docling reviewed facts | `72` |
| Anchor present for reviewed facts | `72` |
| Missing anchor count | `0` |
| Prior missing rows recovered | `28 / 28` |
| S5 positive-control anchors | `17 / 17` |

By sample after implementation:

| Sample | Anchor present | Missing |
| --- | ---: | ---: |
| S1 | `21 / 21` | `0` |
| S4 | `17 / 17` | `0` |
| S5 | `17 / 17` | `0` |
| S6 | `17 / 17` | `0` |

## 5. S6-F041 Disposition

S6-F041 is counted for anchor coverage only because the accepted comparative reviewed-facts input maps it to the same candidate cell as S6-F040 and marks it as `exact_match` / `normalized_equal=true`.

Accepted input evidence:

| Fact | Field | Candidate cell | Candidate / reference excerpt |
| --- | --- | --- | --- |
| S6-F040 | `investment_objective` | `docling_table_4` row `0` col `1` | `投资目标 | 紧密跟踪业绩比较基准，追求跟踪偏离度及跟踪误差的最小化。` |
| S6-F041 | `benchmark` | `docling_table_4` row `0` col `1` | `投资目标 | 紧密跟踪业绩比较基准，追求跟踪偏离度及跟踪误差的最小化。` |

This gate does not re-prove that S6-F041 is semantically correct as `benchmark`. It only proves that the current candidate section-context mapping can now return a candidate anchor for the accepted comparative row. The upstream S6-F041 field assignment remains a residual for any future source-truth or full field-correctness gate.

## 6. Locator Reuse

The after matrix records three reviewed-fact locator reuse groups:

| Sample | Locator | Facts | Interpretation |
| --- | --- | --- | --- |
| S5 | `docling_table_11` / `cell:r1:c1:idx2` | S5-F026, S5-F027 | accepted comparative input reuses one candidate cell for multiple reviewed facts |
| S5 | `docling_table_58` / `cell:r18:c2:idx63` | S5-F033, S5-F034 | accepted comparative input reuses one candidate cell for multiple reviewed facts |
| S6 | `docling_table_4` / `cell:r0:c1:idx1` | S6-F040, S6-F041 | accepted comparative input reuses one candidate cell for multiple reviewed facts |

These groups are not introduced by section-context mapping. They reflect accepted comparative input row assignment and do not prove source truth or full field correctness.

## 7. Documentation Decision

`fund_agent/fund/README.md` was not updated.

Reason: the README currently documents candidate harness boundaries and explicitly states that candidate projection does not modify public `EvidenceAnchor` schema or prove source truth/field correctness/readiness. It does not document the internal `_duplicate_sections()` or `_section_spans()` behavior changed in this gate. The current README boundary statement remains accurate.

## 8. Boundary Guardrails

This implementation proves only no-live candidate anchor-coverage improvement for the selected reviewed facts.

It does not prove:

- source truth;
- full field correctness;
- production parser replacement readiness;
- production `EvidenceAnchor` admission;
- Docling baseline or golden promotion;
- release readiness;
- PR readiness.

Negative guards in the after matrix remain:

```text
not_source_truth=true
not_full_field_correctness=true
not_production_parser_replacement=true
not_readiness_proof=true
candidate_field_correctness_status_remains=not_proven
```

## 9. Validation Commands

Commands run:

```bash
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
python -m json.tool reports/docling-field-correctness-anchor-coverage-no-live-implementation/20260616/anchor_coverage_after_matrix.json >/dev/null
jq '.before, .after, .prior_missing_summary, .by_sample, .locator_reuse_groups' reports/docling-field-correctness-anchor-coverage-no-live-implementation/20260616/anchor_coverage_after_matrix.json
git diff --check
```

Observed results:

| Check | Result |
| --- | --- |
| Targeted tests | `37 passed` |
| JSON validation | passed |
| Prior missing rows recovered | `28 / 28` |
| Anchor coverage after | `72 / 72` |
| S5 preserved | `17 / 17` |
| Diff whitespace check | passed |

## 10. Final Verdict

```text
VERDICT: ANCHOR_COVERAGE_72_OF_72_ACHIEVED_NOT_READY
```
