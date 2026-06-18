# Docling Field Correctness Anchor Coverage Root-cause Evidence - 2026-06-16

Gate: `Docling Field Correctness Anchor Coverage Root-cause Evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

This artifact records no-live root-cause evidence for the anchor coverage blocker accepted by `docs/reviews/docling-field-correctness-comparative-evidence-controller-judgment-20260616.md`.

This gate did not run live/network/source acquisition/PDF/FDR/Docling conversion/pdfplumber export/provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands. It did not modify production source, tests, control docs, design docs, README, repository behavior, parser behavior, source policy, production `EvidenceAnchor`, CHAPTER_CONTRACT, Service, Host, UI, renderer or quality gate behavior.

The evidence uses current Fund documents candidate internals:

- `project_candidate_representation()`
- `map_candidate_document_anchor_candidates()`
- `map_candidate_locator_to_anchor_candidate()`

## 2. Inputs

| Input | SHA-256 | Role |
| --- | --- | --- |
| `reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json` | `94d8e7d5ad2626c5afefb0dbaf3daed8b489454ec50b38f05ce857de80c792c9` | accepted comparative matrix |
| `reports/docling-field-correctness-comparative/20260616/reference_coverage_matrix.json` | `5525eb942aa49785ccc26f685bb221f696d7eec47fccf4e795476690d46b0b08` | accepted coverage matrix |
| `reports/representation-json/004393_2025_docling_current_envelope.json` | `f4ea5e1fa028a364c2286a9244e7d482c4851afbcefb506c5b5b08db4ff02d28` | S1 accepted candidate envelope |
| `reports/docling-runtime-containment/20260616/outputs/006597_2024_docling_full.json` | `ee193cc74542fb2792f2baf1984cf288cf9b55bd321ccee43aff7a6e69258307` | S4 accepted candidate envelope |
| `reports/docling-runtime-containment/20260616/outputs/017641_2024_docling_full.json` | `7fe3c36eb3cb10108482bbe877bcdbbac7706471137046394d8322ccf77e56d7` | S5 positive-control candidate envelope |
| `reports/docling-runtime-containment/20260616/outputs/110020_2024_docling_full.json` | `ce2cbeb348101a21df563be4a60dd57d54ac73a3a14a7454845e7d36d56f86fb` | S6 accepted candidate envelope |

Generated output:

| Output | Role |
| --- | --- |
| `reports/docling-field-correctness-anchor-coverage-root-cause/20260616/anchor_coverage_root_cause_matrix.json` | per-row root-cause matrix |

## 3. Row Reconciliation

| Check | Result |
| --- | ---: |
| Missing-anchor rows expected from comparative matrix | 28 |
| Missing-anchor rows represented in root-cause matrix | 28 |
| Parent table exists | 28 |
| Candidate cell exists | 28 |
| Rows mapped when calling current helper directly | 0 |

By sample:

| Sample | Missing anchors |
| --- | ---: |
| S1 `004393 / 2025` | 3 |
| S4 `006597 / 2024` | 11 |
| S6 `110020 / 2024` | 14 |

By family:

| Family | Missing anchors |
| --- | ---: |
| `expense_costs` | 6 |
| `fund_identity_profile` | 10 |
| `performance_indicators` | 6 |
| `product_contract_profile` | 6 |

## 4. Root-cause Classification

All `28 / 28` rows classify to one repair surface:

```text
section_context_mapping_rule
```

The candidate table and cell exist for every missing-anchor row. The current mapping helper blocks them only during section-context resolution.

By blocked reason:

| Blocked reason | Count | Interpretation |
| --- | ---: | --- |
| `duplicate_section_heading` | 16 | A stable section span exists, but the section is marked unsafe because duplicate annual-report headings make the section context ambiguous. |
| `missing_section_context` | 12 | The table page falls outside stable section spans or has no stable section page context. |

By sample, family and reason:

| Sample | Family | Reason | Count |
| --- | --- | --- | ---: |
| S1 | `expense_costs` | `missing_section_context` | 3 |
| S4 | `fund_identity_profile` | `duplicate_section_heading` | 5 |
| S4 | `product_contract_profile` | `duplicate_section_heading` | 3 |
| S4 | `performance_indicators` | `missing_section_context` | 3 |
| S6 | `fund_identity_profile` | `duplicate_section_heading` | 5 |
| S6 | `product_contract_profile` | `duplicate_section_heading` | 3 |
| S6 | `performance_indicators` | `missing_section_context` | 3 |
| S6 | `expense_costs` | `missing_section_context` | 3 |

No row classified as:

- `table_cell_locator_normalization`
- `reference_to_anchor_join_logic`
- `reference_artifact_scope`
- `reduced_scope_controller_decision`

## 5. Representative Examples

| Fact | Candidate locator | Current helper result | Repair surface |
| --- | --- | --- | --- |
| S4-F001 `fund_name` | table `docling_table_2`, row `0`, column `1`, page `5` | blocked: `duplicate_section_heading`; message `candidate section span blocked by duplicate_section_heading` | `section_context_mapping_rule` |
| S4-F009 `period_profit_f_share` | table `docling_table_14`, row `3`, column `2`, page `10` | blocked: `missing_section_context`; message `candidate block page is outside stable section spans` | `section_context_mapping_rule` |
| S6-F046 `manager_fee_current_year` | table `docling_table_19`, row `21`, column `2`, page `25` | blocked: `missing_section_context`; message `candidate block page is outside stable section spans` | `section_context_mapping_rule` |
| F013 `management_fee_current_year` | table `#/tables/48`, row `1`, column `1`, page `37` | blocked: `missing_section_context`; message `candidate block page is outside stable section spans` | `section_context_mapping_rule` |

These examples demonstrate that the reviewed facts are not missing candidate cells. The blocker is the current section-span safety logic around candidate table/cell mapping.

## 6. Boundary Interpretation

The prior comparative evidence remains valid:

- selected Docling reviewed fact values match accepted same-source references in `72 / 72` cases;
- candidate anchor coverage remains blocked at `44 / 72`;
- missing-anchor rows are now root-caused to section-context mapping logic.

This evidence does not prove:

- source truth;
- full field correctness;
- production parser replacement;
- production `EvidenceAnchor` admission;
- Docling baseline promotion;
- readiness, release, PR, push or merge state.

Candidate status remains:

```text
candidate_field_correctness_status_remains=not_proven
```

## 7. Next Gate Recommendation

Proceed to:

```text
Docling Field Correctness Anchor Coverage No-live Implementation Planning Gate
```

The implementation plan should target section-context mapping rules only. It should not modify public `EvidenceAnchor`, production parser behavior, source policy, Service/Host/UI/renderer/quality gate behavior, or readiness/release state.

Required planning decisions:

1. How to handle duplicate top-level annual-report headings without unsafe section promotion.
2. How to extend stable section spans so known in-report financial/expense tables on pages outside current spans can map fail-closed to the correct annual-report section.
3. Which no-live tests prove S1/S4/S6 missing-anchor rows improve without weakening existing fail-closed behavior.
4. Whether S5 positive-control coverage remains unchanged.

## 8. Validation Commands

Commands run:

```bash
uv run python - <<'PY'
# local root-cause matrix generation through project_candidate_representation(),
# map_candidate_document_anchor_candidates(), and
# map_candidate_locator_to_anchor_candidate()
PY
python -m json.tool reports/docling-field-correctness-anchor-coverage-root-cause/20260616/anchor_coverage_root_cause_matrix.json >/dev/null
jq '.reconciliation, .root_cause_summary' reports/docling-field-correctness-anchor-coverage-root-cause/20260616/anchor_coverage_root_cause_matrix.json
```

Observed result:

| Check | Result |
| --- | --- |
| Root-cause JSON validation | passed |
| Missing-anchor row reconciliation | `28 / 28` |
| Candidate cell exists | `28 / 28` |
| Parent table exists | `28 / 28` |
| Closed repair surface assigned | `28 / 28` |

## 9. Final Verdict

```text
VERDICT: ROOT_CAUSE_CLASSIFIED_READY_FOR_NO_LIVE_IMPLEMENTATION_PLANNING_NOT_READY
```
