# Docling Field Correctness Anchor Coverage Root-cause Plan - 2026-06-16

Status: `PLAN_NOT_READY`
Gate: `Docling Field Correctness Anchor Coverage Root-cause Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## Worker Self-check

- Current gate / role: planning gate for the anchor coverage blocker produced by `Docling Field Correctness Comparative Evidence Gate`; not implementation, not evidence execution, not controller judgment.
- Source of truth: `AGENTS.md`, comparative evidence controller judgment `docs/reviews/docling-field-correctness-comparative-evidence-controller-judgment-20260616.md`, evidence artifact `docs/reviews/docling-field-correctness-comparative-evidence-20260616.md`, and machine-readable matrices under `reports/docling-field-correctness-comparative/20260616/`.
- Scope boundary: write this single plan artifact only; no source/test/control/design/README edits; no live/source/PDF/FDR/Docling conversion/pdfplumber export/provider/LLM/readiness/release/PR action.
- Stop conditions: any route that treats Docling values as source truth, promotes baseline candidacy, changes production `EvidenceAnchor`, or bypasses candidate internals must stop.
- Validation: `git diff --check`.

## 1. Goal

Define a no-live evidence gate that explains why accepted reviewed Docling facts can match source references while missing candidate EvidenceAnchor mappings.

The root-cause evidence must classify each missing-anchor reviewed fact into one of these repair surfaces:

| Repair surface | Meaning |
| --- | --- |
| `section_context_mapping_rule` | Candidate cell exists and locator is stable, but section resolution blocks the table/cell. |
| `table_cell_locator_normalization` | Candidate cell exists but table id, row index, column index, source ref or parent-table resolution is not deterministic enough for mapping. |
| `reference_to_anchor_join_logic` | Mapping exists under a semantically same locator but the comparative matrix join key is too narrow or route-specific. |
| `reference_artifact_scope` | Reviewed-fact row does not describe a candidate cell locator that can be mapped by current candidate internals. |
| `reduced_scope_controller_decision` | The missing fact is correct as selected-fact evidence but is outside the current Gate D anchor-coverage threshold and must be excluded only by explicit controller decision. |

This plan does not choose a fix. It prepares a root-cause evidence artifact that can support a later implementation plan or a reduced-scope controller disposition.

## 2. Accepted Input Facts

| Fact | Accepted status |
| --- | --- |
| Selected Docling reviewed fact values match accepted same-source references in `72 / 72` cases. | accepted by comparative evidence judgment |
| Candidate EvidenceAnchor mapping is present for `44 / 72` accepted Docling reviewed facts. | accepted blocker |
| Missing candidate anchor mappings total `28 / 72`. | accepted blocker |
| Missing anchor by sample: S1 `3`, S4 `11`, S6 `14`; S5 `0`. | accepted blocker distribution |
| Missing anchor by family: `expense_costs=6`, `fund_identity_profile=10`, `performance_indicators=6`, `product_contract_profile=6`. | accepted blocker distribution |
| S2/S3 lack accepted reviewed reference facts. | separate reference-establishment residual; not the immediate anchor root-cause target |
| Release/readiness remains `NOT_READY`. | preserved |

## 3. Non-goals

- No production source edit.
- No tests edit.
- No design/control/README edit.
- No production `EvidenceAnchor` schema change or public `EvidenceSourceKind` expansion.
- No `FundDocumentRepository`, parser, source policy, Service, Host, UI, renderer or quality gate behavior change.
- No live/network/source acquisition/PDF/FDR/Docling conversion/pdfplumber export.
- No provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge/stage/commit.
- No performance/cache/cost evidence. That gate remains blocked until the anchor-coverage root cause is dispositioned.

## 4. Root-cause Evidence Scope

The evidence worker must analyze exactly the `28` rows from:

```text
reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json
```

where:

```text
anchor_mapping_status == "missing"
```

The evidence may also include the `44` anchor-present rows only as controls for the same sample/family/table patterns.

Required sample focus:

| Sample | Missing anchors | Primary evidence role |
| --- | ---: | --- |
| S1 `004393 / 2025` | 3 | S1 current-envelope section/table-family control |
| S4 `006597 / 2024` | 11 | expansion sample with large identity/product/performance gap |
| S6 `110020 / 2024` | 14 | expansion sample with low mapping yield and large identity/product/performance/expense gap |

S5 must be retained as a positive control because it has `17 / 17` anchor presence under the same `S4_S5_S6_lightweight` schema family.

## 5. Evidence Procedure

The next evidence gate must build a root-cause matrix with one row per missing-anchor reviewed fact.

For each row, collect:

| Field | Required meaning |
| --- | --- |
| `sample_id`, `fund_code`, `document_year`, `fact_id`, `family`, `field_name` | copied from comparative matrix |
| `candidate_table_id`, `candidate_row_index`, `candidate_column_index` | copied from comparative matrix |
| `candidate_cell_exists` | whether the accepted candidate envelope contains that table/cell coordinate |
| `candidate_cell_text` and `candidate_cell_normalized_text` | candidate values for local diagnosis only; not source truth |
| `parent_table_exists` | whether table lookup by `candidate_table_id` succeeds |
| `parent_table_section_id`, `parent_table_page_numbers`, `parent_table_heading_path` | context needed to classify section resolution blockers |
| `mapping_result_status` | `mapped`, `blocked`, or `not_found` when calling current candidate mapping helper on the exact cell |
| `mapping_blocked_reason_code` | current fail-closed reason, if blocked |
| `mapping_blocked_message` | current fail-closed message, if blocked |
| `same_table_present_control_count` | number of anchor-present reviewed facts in the same sample/table, if any |
| `repair_surface` | one of the closed repair surfaces in Section 1 |
| `recommended_next_action` | `implementation_plan`, `more_evidence`, or `controller_reduced_scope_decision` |

The evidence must use current candidate internals, especially:

- `project_candidate_representation()`
- `map_candidate_document_anchor_candidates()`
- `map_candidate_locator_to_anchor_candidate()`

It must not parse candidate JSON with ad hoc production semantics when an existing candidate API exists. Small read-only helper code in an evidence script is allowed only to locate the candidate table/cell row needed to call the existing candidate mapping API.

## 6. Allowed Reads

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-field-correctness-comparative-evidence-controller-judgment-20260616.md`
- `docs/reviews/docling-field-correctness-comparative-evidence-20260616.md`
- `reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json`
- `reports/docling-field-correctness-comparative/20260616/reference_coverage_matrix.json`
- `reports/representation-json/004393_2025_docling_current_envelope.json`
- `reports/docling-runtime-containment/20260616/outputs/006597_2024_docling_full.json`
- `reports/docling-runtime-containment/20260616/outputs/017641_2024_docling_full.json`
- `reports/docling-runtime-containment/20260616/outputs/110020_2024_docling_full.json`
- `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`
- `fund_agent/fund/documents/candidates/representation_projection.py`
- `fund_agent/fund/documents/candidates/representation_models.py`
- `tests/fund/documents/test_docling_evidence_anchor_mapping.py`

## 7. Allowed Commands

```bash
sed -n '<range>p' <allowed-file>
rg '<pattern>' <allowed-file...>
jq '<filter>' reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json
jq '<filter>' reports/docling-field-correctness-comparative/20260616/reference_coverage_matrix.json
python -m json.tool reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json >/dev/null
python -m json.tool reports/docling-field-correctness-comparative/20260616/reference_coverage_matrix.json >/dev/null
uv run python <approved local evidence script or inline read-only diagnostic>
git diff --check
```

The `uv run python` diagnostic is allowed only if it:

- reads the allowed local JSON artifacts;
- imports only candidate internals listed in Section 5 plus Python standard library;
- writes only the approved report JSON under Section 8 and the evidence artifact under Section 8;
- does not read PDFs, run Docling/pdfplumber export, call `FundDocumentRepository`, perform network/source acquisition, or mutate source/tests/docs outside the approved evidence outputs.

## 8. Write Set

Write only:

- `reports/docling-field-correctness-anchor-coverage-root-cause/20260616/anchor_coverage_root_cause_matrix.json`
- `docs/reviews/docling-field-correctness-anchor-coverage-root-cause-evidence-20260616.md`

Do not write controller judgment, review artifacts, control docs, design docs, README, source, tests, cache, parser outputs, release artifacts or PR artifacts in the evidence gate.

## 9. Evidence Artifact Requirements

The evidence artifact must include:

1. Scope and non-goal boundary.
2. Exact input artifact list and hashes if cheaply available from the existing artifacts.
3. Missing-anchor row count reconciliation: total `28`; S1 `3`, S4 `11`, S6 `14`; S5 `0`.
4. Root-cause classification table by sample, family, blocked reason and repair surface.
5. Representative examples for each repair surface, with candidate table/cell locator details.
6. Explicit statement that selected fact value matches remain accepted but do not prove source truth or full field correctness.
7. Recommendation for the next gate:
   - no-live implementation planning, if a single dominant repair surface is proven;
   - more evidence, if classification is ambiguous;
   - reduced-scope controller disposition, only if missing facts are outside the current anchor threshold by accepted design.
8. Final verdict token from Section 10.

## 10. Verdict Tokens

The evidence gate must choose exactly one:

```text
VERDICT: ROOT_CAUSE_CLASSIFIED_READY_FOR_NO_LIVE_IMPLEMENTATION_PLANNING_NOT_READY
VERDICT: ROOT_CAUSE_CLASSIFIED_READY_FOR_REDUCED_SCOPE_CONTROLLER_DECISION_NOT_READY
VERDICT: ROOT_CAUSE_PARTIAL_NEEDS_ADDITIONAL_EVIDENCE_NOT_READY
VERDICT: ROOT_CAUSE_EVIDENCE_BLOCKED_NOT_READY
```

## 11. Pass / Block Criteria

Pass as classified root cause only if:

- all `28 / 28` missing-anchor rows are represented in the root-cause matrix;
- each row has a closed `repair_surface`;
- every row either has a candidate cell found or is explicitly classified as `reference_artifact_scope`;
- every `mapping_blocked_reason_code` is preserved when current mapping helper returns blocked;
- no row is scored as source truth or production readiness proof;
- no production/public boundary is changed.

Block if:

- the evidence worker cannot reproduce the `28` missing rows from the comparative matrix;
- candidate-cell lookup requires direct PDF/FDR/Docling/pdfplumber execution;
- root cause depends on changing production `EvidenceAnchor` schema before candidate mapping can be analyzed;
- any route agreement or Docling value is treated as source truth;
- any command or write falls outside Sections 7 and 8.

## 12. Review Requirements

After the evidence artifact is written, route to two independent review workers.

Reviewers must verify:

- row reconciliation: exactly `28` missing-anchor rows;
- each row has a closed repair surface;
- no source-truth/full-field-correctness/baseline/readiness overclaim;
- the next-gate recommendation follows from the root-cause distribution;
- JSON and artifact agree.

Review verdict tokens:

```text
REVIEW_PASS_NOT_READY
REVIEW_BLOCKED_NEEDS_FIX_NOT_READY
```

## 13. Final Verdict

```text
VERDICT: PLAN_READY_FOR_ROOT_CAUSE_EVIDENCE_GATE_NOT_READY
```
