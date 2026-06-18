# Docling Field Correctness Comparative Evidence — AgentDS Review

Role: AgentDS review worker
Gate: `Docling Field Correctness Comparative Evidence Gate`
Date: 2026-06-16

## Scope Reviewed

Reviewed the evidence artifact `docs/reviews/docling-field-correctness-comparative-evidence-20260616.md` and the machine-readable outputs:

- `reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json` — 72 comparisons + 4 D1 route-disagreement rows + summary/samples/family aggregations
- `reports/docling-field-correctness-comparative/20260616/reference_coverage_matrix.json` — reference coverage summary, per-family and per-sample-family breakdowns

Cross-checked against accepted reference inputs:
- `reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json` — S1 accepted reviewed facts
- `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json` — S4/S5/S6 accepted reviewed facts

Also reviewed the candidate mapping sources `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`, `representation_projection.py`, and the three test files for contract compliance.

## Validation Commands And Results

### C1: Structural JSON validity

```bash
python -m json.tool reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json
python -m json.tool reports/docling-field-correctness-comparative/20260616/reference_coverage_matrix.json
```

Result: **PASS**. Both files valid JSON.

### C2: D2 scoring excludes non-docling comparator rows

```bash
jq '[.comparisons[] | select(.candidate_route != "docling_pdf_candidate")] | length' \
  reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json
```

Result: **PASS**. Zero non-docling rows in `comparisons`. All 72 have `candidate_route = "docling_pdf_candidate"`.

### C3: D2 rows all have accepted reference ids

```bash
jq '[.comparisons[] | select(.accepted_reference_id == null)] | length' ...
  # → 0
jq '[.comparisons[] | select(.scored_against_reference == false)] | length' ...
  # → 0
```

Result: **PASS**. 72/72 D2 rows have non-null `accepted_reference_id` and `scored_against_reference = true`.

### C4: Summary key counts internally consistent

```bash
jq '.summary.accepted_docling_reference_facts' ...  # → 72
jq '.summary.value_exact_or_normalized_matches' ...   # → 72
jq '.summary.anchor_present_for_reference_facts' ...  # → 44
jq '.summary.missing_anchor_count' ...                # → 28
jq '.summary.d2_scored_without_accepted_reference_id_count' ... # → 0
jq '.summary.critical_mismatch_count' ...             # → 0
jq '.summary.locator_collision_count_for_mapped_cells_by_table_row_column' ... # → 0
jq '.comparisons | length' ...                        # → 72
jq '.d1_route_disagreements | length' ...             # → 4
```

Per-row verification:
```bash
# All 72 comparisons are value matches
jq '[.comparisons[] | select(.match_status == "exact_match" or .match_status == "normalized_match")] | length' ...
  # → 72

# 44 anchor present, 28 missing
jq '[.comparisons[] | select(.anchor_mapping_status == "present")] | length' ...  # → 44
jq '[.comparisons[] | select(.anchor_mapping_status == "missing")] | length' ...   # → 28

# Zero non-match rows in comparisons
jq '[.comparisons[] | select(.match_status != "exact_match" and .match_status != "normalized_match")] | length' ...
  # → 0
```

Result: **PASS**. All summary counts are internally consistent with the row-level data.

### C5: Per-sample counts match evidence artifact

From `comparisons` array:
| Sample | Refs | Value matches | Anchor present | Missing |
|--------|------|---------------|----------------|---------|
| S1 | 21 | 21 | 18 | 3 |
| S4 | 17 | 17 | 6 | 11 |
| S5 | 17 | 17 | 17 | 0 |
| S6 | 17 | 17 | 3 | 14 |

From `reference_coverage_by_sample_family` aggregation (validating S1 anchor 18 = 0+5+3+4+3+3 across families, etc.): **PASS**. All per-sample sub-aggregations are consistent.

### C6: Family-level aggregation consistency

Both `field_comparison_matrix.json` and `reference_coverage_matrix.json` report identical `reference_coverage_by_family`. Cross-referenced against `reference_coverage_by_sample_family` rollup: 12+20+3+13+12+12 = 72 total refs, 6+10+3+7+12+6 = 44 total anchors. **PASS**.

### C7: D1 route-disagreement rows correctly excluded from D2 scoring

All 4 D1 rows are `sample_id = "S1"`, `candidate_route = "pdfplumber_pdf_candidate"`, `d2_scored = false`. None appear in the `comparisons` array. Field names have `_pdfplumber_comparator` suffix confirming they are non-Docling comparators. **PASS**.

### C8: S2/S3 not in scored comparisons

```bash
jq '[.comparisons[] | .sample_id] | unique' ...  # → ["S1","S4","S5","S6"]
```

Result: **PASS**. S2 and S3 correctly excluded with scope-reason: "no accepted same-report reviewed/golden reference facts in current gate inputs."

### C9: Boundary guard fields

```bash
jq '{not_source_truth, not_full_field_correctness, not_production_parser_replacement, not_readiness_proof, candidate_field_correctness_status_remains, route_agreement_is_truth}' ...
```

Result: **PASS**. All guards set to `true` (denying overclaim). `candidate_field_correctness_status_remains = "not_proven"`. `route_agreement_is_truth = false`. `baseline_candidate_verdict_supported = false`.

### C10: Test suite reproduction

```bash
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py \
  tests/fund/documents/test_candidate_representation_projection.py \
  tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Result: **43 passed**. Matches evidence artifact claim.

### C11: git diff --check

```bash
git diff --check
```

Result: **PASS**. No whitespace issues.

## Findings

| # | Severity | Finding | Evidence | Required action |
|---|----------|---------|----------|-----------------|
| F1 | INFO | All 72 comparisons are D2-scored docling_pdf_candidate rows with non-null accepted reference ids. Zero D2 rows scored without accepted reference id. | C2, C3, C4 | None |
| F2 | INFO | All 72 D2 rows are value matches (exact_match or normalized_match). Zero mismatches in D2 layer. | C4 | None |
| F3 | INFO | 44/72 anchor present, 28/72 anchor missing. S4 (6/17) and S6 (3/17) are the main gaps. | C4, C5, C6 | None — already identified in evidence residuals |
| F4 | INFO | 4 D1 route-disagreement rows are S1 pdfplumber_pdf_candidate rows, all `d2_scored = false`, correctly excluded from D2 correctness scoring. | C7 | None |
| F5 | INFO | S2/S3 excluded with documented reason in scope. No S2/S3 rows appear in comparisons. | C8 | None |
| F6 | INFO | Per-family anchor coverage: portfolio_structure (12/12) and manager_alignment (3/3) at 100%; expense_costs (6/12), fund_identity_profile (10/20), performance_indicators (7/13), product_contract_profile (6/12) below 55%. | C6 | None — documented in residuals |
| F7 | INFO | Boundary guard fields present and correctly deny source truth, full field correctness, production parser replacement, and readiness proof. Summary verdict `baseline_candidate_verdict_supported = false`. | C9 | None |
| F8 | INFO | 43 tests passed, git diff --check clean. | C10, C11 | None |
| F9 | INFO | Both JSON summary sections declare identical values with consistent rounding: anchor_present_rate = 0.6111111111111112 (61.11%), value_match_rate = 1.0 (100%). Evidence artifact text reports anchor-and-value match rate as 61.11%. | C4 | None |

## Verdict

```text
REVIEW_PASS_NOT_READY
```

All five review criteria are satisfied:

1. **D2 scoring boundary**: Confirmed. D2 scoring excludes non-docling comparator rows and only scores rows with accepted reference ids.
2. **Key counts consistency**: Confirmed. 72 D2 refs, 72 value matches, 44 anchor present, 28 missing, 4 D1 route-disagreement rows — all counts match between row-level data, summary, per-sample, and per-family aggregations.
3. **No overclaim**: Confirmed. Artifact correctly denies baseline candidate, source truth, full field correctness, production parser replacement, readiness, release, and PR.
4. **Blocker interpretation**: Correct. Value correctness signal (72/72) passes for selected facts, but Gate D cannot pass because EvidenceAnchor presence is 44/72 and S2/S3 are unscored.
5. **No blocking issue requiring fix**: Confirmed. No discrepancy, data corruption, missing guard, or contract violation found in the evidence artifact or JSON outputs.

## Residual Risks

- The anchor-mapping gap in S4 (6/17) and S6 (3/17) is the dominant blockage for Gate D and is already documented as a residual owned by the Fund documents candidate mapping owner.
- The `reference_coverage_matrix.json` does not include a `not_production_parser_replacement` guard field (present in the comparison matrix). This is a minor schema asymmetry but does not create an overclaim risk since the comparison matrix is the primary evidence artifact and correctly denies all claims.
- The 4 S1 pdfplumber comparator D1 rows exist in `d1_route_disagreements` but their pdfplumber-side values are not recorded in the JSON — only the fact identity and route disagreement reason are stored. If a future comparative gate needs the pdfplumber values, a separate artifact will be needed. This does not affect current evidence validity.
