# Docling Field Correctness Comparative Evidence - 2026-06-16

Gate: `Docling Field Correctness Comparative Evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

This artifact records no-live comparative correctness evidence for accepted local Docling candidate mappings.

This gate did not run live/network/source acquisition/PDF/FDR/Docling conversion/pdfplumber export/provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands. It did not modify production source, tests, control docs, design docs, README, repository behavior, parser behavior, source policy, production `EvidenceAnchor`, CHAPTER_CONTRACT, Service, Host, UI, renderer or quality gate behavior.

Route agreement is not treated as truth. D2 scoring below only counts `docling_pdf_candidate` rows with already accepted reviewed reference facts.

## 2. Inputs

| Input | Role |
| --- | --- |
| `reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json` | accepted S1 reviewed facts |
| `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json` | accepted S4/S5/S6 reviewed facts |
| `reports/representation-json/004393_2025_docling_current_envelope.json` | accepted S1 Docling candidate envelope |
| `reports/docling-runtime-containment/20260616/outputs/006597_2024_docling_full.json` | accepted S4 Docling candidate envelope |
| `reports/docling-runtime-containment/20260616/outputs/017641_2024_docling_full.json` | accepted S5 Docling candidate envelope |
| `reports/docling-runtime-containment/20260616/outputs/110020_2024_docling_full.json` | accepted S6 Docling candidate envelope |
| `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` | current candidate-only mapping helper |

Generated evidence files:

| Output | Role |
| --- | --- |
| `reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json` | per-fact D1/D2 comparison matrix |
| `reports/docling-field-correctness-comparative/20260616/reference_coverage_matrix.json` | reference coverage summary |

## 3. Method

The evidence script loaded each accepted candidate envelope through `project_candidate_representation()` and mapped it through `map_candidate_document_anchor_candidates()`. It then matched reviewed Docling facts by `(candidate_table_id, candidate_row_index, candidate_column_index)` against mapped cell anchors.

S1 has 4 `pdfplumber_comparator` mismatch rows in the reviewed facts artifact. Those rows are recorded as D1 route-disagreement context only and are excluded from Docling D2 correctness scoring.

S2 and S3 are not scored because current gate inputs do not contain accepted same-report reviewed/golden reference facts for them.

## 4. Result Summary

| Metric | Result |
| --- | ---: |
| Accepted Docling reviewed facts scored in D2 | 72 |
| Value exact/normalized matches | 72 |
| Value match rate over accepted Docling references | 100.00% |
| Candidate EvidenceAnchor mappings present for those references | 44 |
| Anchor-and-value match rate | 61.11% |
| Missing anchor mappings for accepted references | 28 |
| Critical mismatch count | 0 |
| D2 rows scored without accepted reference id | 0 |
| Locator collision count by mapped cell `(table, row, column)` | 0 |
| D1 route-disagreement rows, not D2-scored | 4 |

Per-sample summary:

| Sample | Fund/year | Accepted Docling refs | Value matches | Anchor present | Anchor rate | Missing anchor |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| S1 | `004393 / 2025` | 21 | 21 | 18 | 85.71% | 3 |
| S4 | `006597 / 2024` | 17 | 17 | 6 | 35.29% | 11 |
| S5 | `017641 / 2024` | 17 | 17 | 17 | 100.00% | 0 |
| S6 | `110020 / 2024` | 17 | 17 | 3 | 17.65% | 14 |

Family summary:

| Family | Accepted refs | Value matches | Anchor present | Anchor-and-value rate |
| --- | ---: | ---: | ---: | ---: |
| `expense_costs` | 12 | 12 | 6 | 50.00% |
| `fund_identity_profile` | 20 | 20 | 10 | 50.00% |
| `manager_alignment` | 3 | 3 | 3 | 100.00% |
| `performance_indicators` | 13 | 13 | 7 | 53.85% |
| `portfolio_structure` | 12 | 12 | 12 | 100.00% |
| `product_contract_profile` | 12 | 12 | 6 | 50.00% |

## 5. Interpretation

This evidence supports a narrow selected-fact value-correctness signal: accepted Docling reviewed facts for S1/S4/S5/S6 match their accepted same-source references at `72 / 72`.

This evidence does not satisfy the Gate D pass threshold because comparable accepted fields require candidate EvidenceAnchor presence, and current anchor presence is only `44 / 72`. S4 and S6 are the main blockers. S2 and S3 also remain unscored because no accepted reviewed reference facts are present in the current gate inputs.

Therefore this gate cannot support baseline-candidate disposition, production parser replacement, source truth, full field correctness, readiness, release or PR.

## 6. Residuals

| Residual | Evidence status | Next owner |
| --- | --- | --- |
| EvidenceAnchor presence is `44 / 72` for accepted Docling reviewed facts. | blocker for Gate D pass threshold | Fund documents candidate mapping owner |
| S4 anchor presence is `6 / 17`; S6 anchor presence is `3 / 17`. | sample-specific mapping gap | Fund documents candidate mapping owner |
| S2/S3 have no accepted reviewed reference facts in current inputs. | blocks full sample-matrix field-correctness verdict | reference establishment owner |
| S5/S6 profile-specific high-priority family coverage remains partial. | limits evidence to selected facts | reference establishment owner |
| EID HTML render route is accepted only for S1; S4/S5/S6 remain two-route context only. | no tri-route comparative claim | EID HTML availability owner |
| Candidate mappings keep `field_correctness_status="not_proven"` and `source_truth_status="not_proven"`. | intentional candidate-only boundary | future baseline disposition owner |
| Release/readiness remains `NOT_READY`. | preserved | future readiness gate |

## 7. Validation Commands

Commands run:

```bash
uv run python - <<'PY'
# local structured comparison through project_candidate_representation()
# and map_candidate_document_anchor_candidates()
PY
python -m json.tool reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json >/dev/null
python -m json.tool reports/docling-field-correctness-comparative/20260616/reference_coverage_matrix.json >/dev/null
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py tests/fund/documents/test_candidate_representation_projection.py tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Observed result:

| Check | Result |
| --- | --- |
| JSON validation for `field_comparison_matrix.json` | passed |
| JSON validation for `reference_coverage_matrix.json` | passed |
| Candidate mapping / projection / no-consumption tests | `43 passed` |

## 8. Final Verdict

```text
VERDICT: FIELD_VALUES_MATCH_SELECTED_REFERENCES_ANCHOR_COVERAGE_BLOCKED_NOT_READY
```
