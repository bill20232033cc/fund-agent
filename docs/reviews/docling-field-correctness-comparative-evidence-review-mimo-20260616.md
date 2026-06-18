# Docling Field Correctness Comparative Evidence Gate - MiMo Review

Gate: `Docling Field Correctness Comparative Evidence Gate`
Reviewer: AgentMiMo
Role: review worker only, not controller
Reviewed artifact: `docs/reviews/docling-field-correctness-comparative-evidence-20260616.md`
Reviewed outputs: `reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json`, `reports/docling-field-correctness-comparative/20260616/reference_coverage_matrix.json`

## Scope Reviewed

Independent review of the evidence artifact and machine-readable JSON outputs for correctness, boundary compliance, and verdict support. This review did not read the DS review artifact.

## Validation Commands And Results

```bash
python -m json.tool reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json >/dev/null
# result: VALID

python -m json.tool reports/docling-field-correctness-comparative/20260616/reference_coverage_matrix.json >/dev/null
# result: VALID

jq '.summary.accepted_docling_reference_facts' .../reference_coverage_matrix.json
# result: 72

jq '.summary.value_exact_or_normalized_matches' .../reference_coverage_matrix.json
# result: 72

jq '.summary.anchor_present_for_reference_facts' .../reference_coverage_matrix.json
# result: 44

jq '.summary.missing_anchor_count' .../reference_coverage_matrix.json
# result: 28

jq '.summary.d1_route_disagreement_rows' .../reference_coverage_matrix.json
# result: 4

jq '[.d1_route_disagreements[] | select(.d2_scored == true)] | length' .../reference_coverage_matrix.json
# result: 0 — D1 rows are correctly excluded from D2 scoring

jq '[.d1_route_disagreements[] | select(.candidate_route != "pdfplumber_pdf_candidate")] | length' .../reference_coverage_matrix.json
# result: 0 — all D1 rows are pdfplumber comparator rows

jq '[.facts[] | select(.candidate_route == "docling_pdf_candidate" and .match_status != "mismatch")] | length' .../004393_pilot_reviewed_facts.json
# result: 21 — S1 docling non-mismatch facts

jq '[.facts[] | select(.candidate_route == "pdfplumber_pdf_candidate")] | length' .../004393_pilot_reviewed_facts.json
# result: 4 — S1 pdfplumber comparator rows

jq '.reference_coverage_by_family | map(.accepted_reference_count) | add' .../reference_coverage_matrix.json
# result: 72

jq '.reference_coverage_by_family | map(.anchor_present_count) | add' .../reference_coverage_matrix.json
# result: 44

jq '.reference_coverage_by_family | map(.value_exact_or_normalized_count) | add' .../reference_coverage_matrix.json
# result: 72

jq '.reference_coverage_by_sample_family | map(.accepted_reference_count) | add' .../reference_coverage_matrix.json
# result: 72

jq '.reference_coverage_by_sample_family | group_by(.sample_id) | map({sample: .[0].sample_id, refs: map(.accepted_reference_count) | add, anchors: map(.anchor_present_count) | add})' .../reference_coverage_matrix.json
# result: S1=21/18, S4=17/6, S5=17/17, S6=17/3

jq '.scope.samples_scored' .../reference_coverage_matrix.json
# result: ["S1","S4","S5","S6"]

jq '.scope.samples_not_scored' .../reference_coverage_matrix.json
# result: S2, S3 — no accepted reviewed facts

git diff --check
# result: clean
```

## Findings

| # | Severity | Finding | Evidence | Required Action |
|---|----------|---------|----------|-----------------|
| 1 | NONE | D2 scoring correctly excludes non-docling comparator rows | 4 `pdfplumber_pdf_candidate` rows in S1 pilot facts are recorded as D1 route-disagreement context with `d2_scored: false`; grep confirms 0 D1 rows appear in D2 scoring | No action |
| 2 | NONE | Key counts are internally consistent | 72 D2 refs = 21 (S1) + 17 (S4) + 17 (S5) + 17 (S6); 72 value matches; 44 anchor present = 18 (S1) + 6 (S4) + 17 (S5) + 3 (S6); 28 missing anchors = 3 (S1) + 11 (S4) + 0 (S5) + 14 (S6); 4 D1 route-disagreement rows; family sums: 12+20+3+13+12+12=72 accepted refs, 6+10+3+7+12+6=44 anchors, 12+20+3+13+12+12=72 value matches | No action |
| 3 | NONE | Artifact does not overclaim | `not_source_truth: true`, `not_full_field_correctness: true`, `not_readiness_proof: true`; `field_correctness_status="not_proven"` on all mappings; verdict is `FIELD_VALUES_MATCH_SELECTED_REFERENCES_ANCHOR_COVERAGE_BLOCKED_NOT_READY`; interpretation explicitly blocks baseline-candidate, production parser replacement, source truth, full field correctness, readiness, release and PR claims | No action |
| 4 | NONE | Blocker interpretation is correct | Value correctness selected-fact signal passes (72/72 exact/normalized match); Gate D cannot pass because EvidenceAnchor presence is only 44/72; S2/S3 have no accepted reviewed facts in current inputs and remain unscored | No action |
| 5 | NONE | No blocking issue requiring fix before controller judgment | JSON schemas are valid; internal counts are consistent; boundary claims are correctly disclaimed; candidate-only boundary is preserved in `evidence_anchor_mapping.py` and `representation_projection.py`; no-consumption guards test confirms candidate internals are not consumed by Service/UI/Host/renderer | No action |

## Verdict

```text
REVIEW_PASS_NOT_READY
```

## Residual Risks

| Residual | Status |
|----------|--------|
| EvidenceAnchor presence is 44/72 for accepted Docling reviewed facts | Blocks Gate D pass threshold; S4 (6/17) and S6 (3/17) are main mapping gaps |
| S2/S3 have no accepted reviewed reference facts in current inputs | Blocks full sample-matrix field-correctness verdict |
| EID HTML render route accepted only for S1; S4/S5/S6 remain two-route context only | No tri-route comparative claim |
| `field_correctness_status` remains `not_proven` on all candidate mappings | Intentional candidate-only boundary; not a defect |
| Release/readiness remains `NOT_READY` | Preserved; not a defect |
