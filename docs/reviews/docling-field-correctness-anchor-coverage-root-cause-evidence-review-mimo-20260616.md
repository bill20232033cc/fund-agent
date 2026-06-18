# Docling Field Correctness Anchor Coverage Root-cause Evidence Review (MiMo) - 2026-06-16

Gate: `Docling Field Correctness Anchor Coverage Root-cause Evidence Review Gate`
Role: AgentMiMo independent review worker
Verdict: `REVIEW_PASS_NOT_READY`

## Scope Reviewed

- Evidence artifact: `docs/reviews/docling-field-correctness-anchor-coverage-root-cause-evidence-20260616.md`
- Root-cause JSON: `reports/docling-field-correctness-anchor-coverage-root-cause/20260616/anchor_coverage_root_cause_matrix.json`
- Cross-checked against: `reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json`

Did not read: `docs/reviews/docling-field-correctness-anchor-coverage-root-cause-evidence-review-ds-20260616.md`

## Validation Commands And Results

```bash
# 1. Total row count
jq '.rows | length' anchor_coverage_root_cause_matrix.json
# Result: 28

# 2. Rows by sample
jq '[.rows[] | select(.sample_id == "S1")] | length'  # 3
jq '[.rows[] | select(.sample_id == "S4")] | length'  # 11
jq '[.rows[] | select(.sample_id == "S6")] | length'  # 14

# 3. Rows by family
jq '[.rows[] | .family] | group_by(.) | map({family: .[0], count: length})'
# Result: expense_costs=6, fund_identity_profile=10, performance_indicators=6, product_contract_profile=6

# 4. Invariant checks (all 28)
jq '[.rows[] | select(.parent_table_exists == true)] | length'   # 28
jq '[.rows[] | select(.candidate_cell_exists == true)] | length' # 28
jq '[.rows[] | select(.mapping_result_status == "blocked")] | length' # 28
jq '[.rows[] | select(.repair_surface == "section_context_mapping_rule")] | length' # 28

# 5. Blocked reasons
jq '[.rows[] | .mapping_blocked_reason_code] | group_by(.) | map({reason: .[0], count: length})'
# Result: duplicate_section_heading=16, missing_section_context=12

# 6. Cross-check comparative matrix missing-anchor count
jq '[.comparisons[] | select(.anchor_mapping_status == "missing")] | length' field_comparison_matrix.json
# Result: 28
jq '[.comparisons[] | select(.anchor_mapping_status == "missing") | .sample_id] | group_by(.) | map(...)'
# Result: S1=3, S4=11, S6=14
jq '[.comparisons[] | select(.anchor_mapping_status == "missing") | .family] | group_by(.) | map(...)'
# Result: expense_costs=6, fund_identity_profile=10, performance_indicators=6, product_contract_profile=6

# 7. Sample/family/reason distribution cross-check
jq '[.rows[] | {sample_id, family, mapping_blocked_reason_code}] | group_by(...) | map(...)'
# Result: matches artifact Section 4 table exactly

# 8. Overclaim guards - all rows
jq '[.rows[] | select(.not_source_truth != true)] | length'    # 0
jq '[.rows[] | select(.not_readiness_proof != true)] | length'  # 0
jq '[.rows[] | select(.recommended_next_action != "implementation_plan")] | length' # 0

# 9. Overclaim guards - JSON top-level
jq '.not_source_truth'                      # true
jq '.not_full_field_correctness'            # true
jq '.not_production_parser_replacement'     # true
jq '.not_readiness_proof'                   # true
jq '.candidate_field_correctness_status_remains' # "not_proven"

# 10. Verdict token
jq '.verdict'
# Result: "ROOT_CAUSE_CLASSIFIED_READY_FOR_NO_LIVE_IMPLEMENTATION_PLANNING_NOT_READY"

# 11. git diff --check
# Result: clean
```

## Findings

| # | Severity | Finding | Evidence | Required Action |
| --- | --- | --- | --- | --- |
| 1 | none | Row reconciliation verified: 28/28 missing-anchor rows present, matching comparative matrix exactly | S1=3, S4=11, S6=14; families: expense_costs=6, fund_identity_profile=10, performance_indicators=6, product_contract_profile=6 | none |
| 2 | none | All 28 rows have parent_table_exists=true, candidate_cell_exists=true, mapping_result_status=blocked, and repair_surface=section_context_mapping_rule | jq invariant checks return 28 for each | none |
| 3 | none | Blocked reasons match: duplicate_section_heading=16, missing_section_context=12 | JSON root_cause_summary.by_mapping_blocked_reason and per-row group_by both agree | none |
| 4 | none | Sample/family/reason distribution table in evidence artifact matches JSON exactly | 8-row cross-check against jq group_by on sample_id+family+mapping_blocked_reason_code | none |
| 5 | none | No overclaim: all 28 rows have not_source_truth=true and not_readiness_proof=true; JSON top-level has all negative guards set; artifact Section 6 explicitly disclaims source truth, full field correctness, parser replacement, baseline promotion, readiness, release, PR | per-row and top-level jq checks | none |
| 6 | none | Verdict token is valid and matches plan's allowed set | verdict = ROOT_CAUSE_CLASSIFIED_READY_FOR_NO_LIVE_IMPLEMENTATION_PLANNING_NOT_READY | none |
| 7 | none | Next-gate recommendation (section_context_mapping_rule dominant, 28/28) supports "implementation planning" route; artifact Section 7 lists concrete planning decisions | consistent with plan Section 10 pass criteria | none |
| 8 | none | JSON schema_version, input_artifacts SHA-256s, reconciliation, root_cause_summary, and positive_control_summary are structurally complete | top-level JSON validation passed via python -m json.tool | none |

## Verdict

```text
REVIEW_PASS_NOT_READY
```

## Residual Risks

1. The `positive_control_summary` in the JSON shows aggregate mapping/blocked counts per sample, including S5. S5 has 0 missing-anchor reviewed facts but 2278 blocked candidates overall (mostly `missing_section_context`). This is consistent with S5 being a positive control for reviewed-fact anchor presence, not for all-candidate mapping yield. No action needed.

2. No live PDF/FDR/Docling execution was performed; root-cause classification relies on existing candidate envelope JSON. If candidate envelopes change, the root-cause matrix would need regeneration. This is an inherent limitation of the no-live evidence scope, not a defect.
