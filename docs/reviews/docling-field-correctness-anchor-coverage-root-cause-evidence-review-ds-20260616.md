# Docling Field Correctness Anchor Coverage Root-cause Evidence Review (DS) - 2026-06-16

Gate: `Docling Field Correctness Anchor Coverage Root-cause Evidence Review Gate`
Role: AgentDS review worker
Release/readiness: `NOT_READY`

## Scope Reviewed

- Evidence artifact: `docs/reviews/docling-field-correctness-anchor-coverage-root-cause-evidence-20260616.md`
- Root-cause matrix JSON: `reports/docling-field-correctness-anchor-coverage-root-cause/20260616/anchor_coverage_root_cause_matrix.json`
- Plan artifact (for boundary compliance): `docs/reviews/docling-field-correctness-anchor-coverage-root-cause-plan-20260616.md`
- Input comparative matrices (for row reconciliation): `field_comparison_matrix.json`, `reference_coverage_matrix.json`
- Candidate internals (for API boundary): `evidence_anchor_mapping.py`, `representation_projection.py`, `representation_models.py`

This review did not run live/network/PDF/FDR/Docling conversion/pdfplumber export/provider/LLM commands. No source, test, control, or design edits were made.

## Validation Commands And Results

### 1. Row Count Reconciliation

```bash
jq '.rows | length' anchor_coverage_root_cause_matrix.json  # → 28
jq '[.rows[] | select(.sample_id == "S1")] | length' ...     # → 3
jq '[.rows[] | select(.sample_id == "S4")] | length' ...     # → 11
jq '[.rows[] | select(.sample_id == "S6")] | length' ...     # → 14
```

**Result: PASS.** Exactly 28 rows, matching plan expectations S1=3, S4=11, S6=14. No S5 rows (positive control, correct).

### 2. Row Field Completeness

```bash
jq '[.rows[] | select(.parent_table_exists != true)] | length'     # → 0
jq '[.rows[] | select(.candidate_cell_exists != true)] | length'   # → 0
jq '[.rows[] | select(.mapping_result_status != "blocked")] | length'  # → 0
jq '[.rows[] | select(.repair_surface == null)] | length'          # → 0
jq '[.rows[] | select(.recommended_next_action == null)] | length' # → 0
```

**Result: PASS.** All 28 rows have `parent_table_exists=true`, `candidate_cell_exists=true`, `mapping_result_status=blocked`, and a closed `repair_surface` with `recommended_next_action`.

### 3. Root-cause Classification

```bash
jq '[.rows[] | select(.repair_surface != "section_context_mapping_rule")] | length'  # → 0
jq '[.rows[] | select(.mapping_blocked_reason_code == "duplicate_section_heading")] | length'  # → 16
jq '[.rows[] | select(.mapping_blocked_reason_code == "missing_section_context")] | length'    # → 12
```

**Result: PASS.** All 28 rows classify to `section_context_mapping_rule`. Blocked reasons: `duplicate_section_heading`=16, `missing_section_context`=12. Sum = 28.

No row classified to `table_cell_locator_normalization`, `reference_to_anchor_join_logic`, `reference_artifact_scope`, or `reduced_scope_controller_decision`.

### 4. Evidence Artifact ↔ JSON Agreement

| Claim (evidence artifact) | JSON source | Match |
| --- | --- | --- |
| Total missing-anchor rows: 28 | `reconciliation.missing_anchor_rows_total` = 28 | PASS |
| S1=3, S4=11, S6=14 | `reconciliation.by_sample` | PASS |
| expense_costs=6, fund_identity_profile=10, performance_indicators=6, product_contract_profile=6 | `reconciliation.by_family` | PASS |
| candidate_cell_exists: 28/28 | `reconciliation.candidate_cell_exists_count` = 28 | PASS |
| parent_table_exists: 28/28 | `reconciliation.parent_table_exists_count` = 28 | PASS |
| mapped when called directly: 0 | `reconciliation.mapped_when_called_directly_count` = 0 | PASS |
| duplicate_section_heading: 16 | `root_cause_summary.by_mapping_blocked_reason.duplicate_section_heading` = 16 | PASS |
| missing_section_context: 12 | `root_cause_summary.by_mapping_blocked_reason.missing_section_context` = 12 | PASS |
| repair surface: section_context_mapping_rule 28 | `root_cause_summary.by_repair_surface.section_context_mapping_rule` = 28 | PASS |
| Next gate recommendation | `root_cause_summary.recommended_next_gate` | PASS |
| Verdict token | `verdict` | PASS |
| Sample/family/reason cross-tab (8 rows in evidence Section 4) | Cross-tab via `group_by` on sample+family+reason | PASS |

**Result: PASS.** Evidence artifact and JSON agree on all counts, distributions, blocked reasons, repair surface, next-gate recommendation, and verdict.

### 5. Representative Examples Verification

| Evidence claim | JSON row | Match |
| --- | --- | --- |
| S4-F001: table `docling_table_2`, row 0, col 1, page 5, blocked `duplicate_section_heading` | S4-F001 row | PASS |
| S4-F009: table `docling_table_14`, row 3, col 2, page 10, blocked `missing_section_context` | S4-F009 row | PASS |
| S6-F046: table `docling_table_19`, row 21, col 2, page 25, blocked `missing_section_context` | S6-F046 row | PASS |
| F013: table `#/tables/48`, row 1, col 1, page 37, blocked `missing_section_context` | F013 row | PASS |

**Result: PASS.** All four representative examples match their corresponding JSON rows exactly.

### 6. JSON Structural Validity

```bash
python3 -m json.tool anchor_coverage_root_cause_matrix.json >/dev/null  # → VALID
```

**Result: PASS.** JSON is structurally valid.

### 7. Overclaim Check

Top-level flags:
```bash
jq '{not_source_truth, not_full_field_correctness, not_production_parser_replacement,
     not_readiness_proof, candidate_field_correctness_status_remains, verdict}'  # all true/not_proven
```

Per-row flags:
```bash
jq '[.rows[] | select(.not_source_truth != true or .not_readiness_proof != true)] | length'  # → 0
```

**Result: PASS.** No overclaim detected. Top-level and per-row `not_source_truth`, `not_readiness_proof` are uniformly set. `candidate_field_correctness_status_remains` = `not_proven`. Verdict ends with `NOT_READY`. Evidence artifact Section 6 explicitly disclaims source truth, full field correctness, production parser replacement, EvidenceAnchor admission, baseline promotion, readiness, release, PR, push, and merge state.

### 8. Plan Boundary Compliance

| Plan requirement | Status |
| --- | --- |
| Writes only evidence artifact + root-cause matrix JSON | PASS |
| No production source/test/control/design/README edits | PASS |
| No live/network/PDF/Docling/pdfplumber/provider/LLM | PASS |
| Uses candidate internals (project_candidate_representation, map_candidate_document_anchor_candidates, map_candidate_locator_to_anchor_candidate) | PASS (per evidence Section 1) |
| No production EvidenceAnchor schema change | PASS |
| No readiness/release claim | PASS |
| All 28/28 missing-anchor rows represented | PASS |
| Each row has closed repair_surface | PASS |
| mapping_blocked_reason_code preserved | PASS |
| No row scored as source truth or production readiness proof | PASS |

**Result: PASS.** Evidence artifact complies with all plan boundaries.

## Findings

| # | Severity | Finding | Evidence | Required Action |
| --- | --- | --- | --- | --- |
| F1 | INFO | S6-F040 `investment_objective` and S6-F041 `benchmark` share identical `cell_locator_hash` (`f0dabd5f...`), both mapping to `docling_table_4` row 0 col 1. Two distinct reference fields resolve to the same candidate cell. | jq on `cell_locator_hash` groups: one collision pair found | None for root-cause gate. This is a comparative input artifact characteristic, not introduced by the root-cause evidence. Controller should be aware that the reference-side mapping assigned `benchmark` to the same cell as `investment_objective` for S6. |
| F2 | INFO | `docs/current-startup-packet.md` still lists `Docling Field Correctness Comparative Evidence Gate` as the current active gate (line 23), while this review is for the root-cause evidence gate. | Read of startup packet Section 2 | Control doc staleness — does not block this review. Controller should update the startup packet when accepting this gate's artifacts. |
| F3 | INFO | `positive_control_summary` in JSON shows high blocked counts across all samples (S1: 2209, S4: 3001, S5: 2278, S6: 6598), confirming section-context blocking is a systemic issue far beyond the 28 reviewed-fact rows. | JSON `positive_control_summary` | Not a blocker. This confirms the root-cause classification (section_context_mapping_rule) is consistent with the broader candidate mapping behavior. The next implementation planning gate should consider whether section-context fixes for the 28 rows will also improve the broader blocked population. |

## Verdict

```text
REVIEW_PASS_NOT_READY
```

All six review criteria are satisfied:

1. **Row reconciliation**: Exactly 28 missing-anchor rows, matching S1=3, S4=11, S6=14. Confirmed by independent jq counts.
2. **Row field completeness**: All 28 rows have `parent_table_exists=true`, `candidate_cell_exists=true`, `mapping_result_status=blocked`, and a closed `repair_surface`. Zero violations.
3. **Classification**: All 28 rows classify to `section_context_mapping_rule`, with blocked reasons `duplicate_section_heading`=16 and `missing_section_context`=12. No rows fall into other repair surfaces.
4. **Artifact/JSON agreement**: Evidence artifact and JSON agree on all counts, sample/family distributions, blocked reasons, repair surface, next-gate recommendation, and verdict token. Representative examples verified.
5. **No overclaim**: Top-level and per-row `not_source_truth`/`not_readiness_proof` flags are uniformly set. Evidence artifact explicitly disclaims all prohibited claims. `candidate_field_correctness_status_remains` = `not_proven`. Verdict ends with `NOT_READY`.
6. **No blocking issues**: No finding requires fixing the evidence artifact or JSON before controller judgment. F1 and F2 are informational only and do not affect root-cause classification correctness.

## Residual Risks

1. **S6-F040/F041 cell_locator_hash collision**: `investment_objective` and `benchmark` for S6 map to the same candidate cell (`docling_table_4` row 0 col 1). This is upstream of the root-cause evidence (in the comparative matrix) and does not affect the root-cause classification. If the comparative matrix's reference-side mapping is incorrect for `benchmark`, fixing it would change this from a missing-anchor row to a reference-artifact-scope row. The next implementation planning gate should verify that the reference-side `benchmark` field assignment is correct before investing in section-context fixes for this row.

2. **Control doc staleness**: The startup packet's current active gate field is stale. This does not affect evidence correctness but should be addressed in the controller judgment's control sync step.

3. **Systemic blocking scope**: The `positive_control_summary` shows 2209-6598 blocked candidate cells per sample from section-context issues alone. The 28 missing-anchor reviewed facts are a tiny subset of a much larger blocked population. The next implementation planning gate should decide whether fixing section-context rules for the 28 reviewed facts is the right scope or whether broader section-context calibration is needed.
