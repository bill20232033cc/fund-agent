# Docling EvidenceAnchor Mapping Section-context Enrichment Re-evidence - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment Re-evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

This artifact records no-live re-evidence for accepted local candidate representation JSON artifacts after deterministic section-context enrichment was accepted in `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`.

This gate did not run live/network/PDF/FDR/source acquisition/Docling conversion/provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands. It did not modify source, tests, control docs, design docs, README, reports, cache, repository, parser, source policy, production `EvidenceAnchor`, CHAPTER_CONTRACT, Service, Host, UI, renderer, quality gate, provider or LLM behavior.

## 2. Inputs

| Sample | Fund | Year | Schema family | Input path | Input status |
| --- | --- | --- | --- | --- | --- |
| S1-current-envelope | `004393` | `2025` | `S1_full` | `reports/representation-json/004393_2025_docling_current_envelope.json` | accepted candidate envelope |
| S4-full | `006597` | `2024` | `S4_S5_S6_lightweight` | `reports/docling-runtime-containment/20260616/outputs/006597_2024_docling_full.json` | accepted candidate envelope |
| S5-full | `017641` | `2024` | `S4_S5_S6_lightweight` | `reports/docling-runtime-containment/20260616/outputs/017641_2024_docling_full.json` | accepted candidate envelope |
| S6-full | `110020` | `2024` | `S4_S5_S6_lightweight` | `reports/docling-runtime-containment/20260616/outputs/110020_2024_docling_full.json` | accepted candidate envelope |
| S1-full-json-residual | `004393` | `2025` | n/a | `reports/representation-json/004393_2025_docling_full.json` | residual only; blocked by schema guard |

S1 full JSON remains blocked as a residual only: `project_candidate_representation()` raises `ValueError: unsupported candidate representation schema_version`, with `schema_version=null` in the observed payload. It was not used as a mapped envelope.

S1-current-envelope and S1-full-json are not treated as interchangeable artifacts in this evidence. S1-current-envelope is the accepted candidate envelope shape consumed by `project_candidate_representation()`. S1-full-json is retained only as a blocked residual because its top-level schema and internal field layout do not match `candidate_annual_report_representation.v1`. Therefore the S1 mapped counts below prove behavior for the accepted envelope path only; they do not prove how S1-full-json would map after a future export/schema disposition.

## 3. Prior Baseline

Accepted prior mapping evidence:

| Metric | Prior value |
| --- | ---: |
| Total candidate blocks | `23475` |
| Mapped total | `102` |
| Mapped yield | `102 / 23475 = 0.43%` |
| Blocked total | `23373` |
| Blocked reason distribution | `missing_section_context=23363`, `unstable_section_context=10` |
| Table mapped yield | `0 / 436 = 0.00%` |
| Cell mapped yield | `0 / 19252 = 0.00%` |
| Table/cell mapped yield | `0 / 19688 = 0.00%` |

Prior evidence was accepted only as partial heading-only candidate mapping evidence and not as source truth, field correctness, baseline promotion, readiness or release proof.

## 4. Re-evidence Result Matrix

| Sample | Sections | Text blocks | Tables | Cells | Candidate blocks | Mapped total | Mapped by block type | Blocked total | Blocked reason distribution |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- |
| S1-current-envelope | 25 | 670 | 95 | 3493 | 4283 | 2074 | `heading=10`, `paragraph=219`, `table=41`, `cell=1804` | 2209 | `missing_section_context=2205`, `unsupported_heading_number=4` |
| S4-full | 229 | 737 | 96 | 2759 | 3821 | 820 | `heading=17`, `table=22`, `cell=781` | 3001 | `missing_section_context=2673`, `duplicate_section_heading=165`, `unsupported_heading_number=163` |
| S5-full | 208 | 856 | 121 | 7060 | 8245 | 5967 | `heading=21`, `table=79`, `cell=5867` | 2278 | `missing_section_context=2122`, `duplicate_section_heading=2`, `unsupported_heading_number=154` |
| S6-full | 222 | 840 | 124 | 5940 | 7126 | 528 | `heading=21`, `table=12`, `cell=495` | 6598 | `missing_section_context=6209`, `duplicate_section_heading=257`, `unsupported_heading_number=132` |
| Total | 684 | 3103 | 436 | 19252 | 23475 | 9389 | `heading=69`, `paragraph=219`, `table=154`, `cell=8947` | 14086 | `missing_section_context=13209`, `duplicate_section_heading=424`, `unsupported_heading_number=453` |

Overall mapped yield after section-context enrichment: `9389 / 23475 = 40.00%`.

Blocked reason distribution after section-context enrichment:

| Reason | Count | Share of blocked |
| --- | ---: | ---: |
| `missing_section_context` | 13209 | 93.77% |
| `duplicate_section_heading` | 424 | 3.01% |
| `unsupported_heading_number` | 453 | 3.22% |

## 5. Table/Cell Yield

| Sample | Table mapped yield | Cell mapped yield | Combined table/cell yield |
| --- | ---: | ---: | ---: |
| S1-current-envelope | `41 / 95 = 43.16%` | `1804 / 3493 = 51.65%` | `1845 / 3588 = 51.42%` |
| S4-full | `22 / 96 = 22.92%` | `781 / 2759 = 28.31%` | `803 / 2855 = 28.13%` |
| S5-full | `79 / 121 = 65.29%` | `5867 / 7060 = 83.10%` | `5946 / 7181 = 82.80%` |
| S6-full | `12 / 124 = 9.68%` | `495 / 5940 = 8.33%` | `507 / 6064 = 8.36%` |
| Total | `154 / 436 = 35.32%` | `8947 / 19252 = 46.47%` | `9101 / 19688 = 46.23%` |

Interpretation caveat: S1 uses schema family `S1_full`, while S4/S5/S6 use `S4_S5_S6_lightweight`. These schema families have different cell validation rules, so the aggregate table/cell yield should be read with the per-sample rows. Paragraph mapping is currently S1-envelope-specific in this matrix; S4/S5/S6 did not emit mapped paragraph records in this re-evidence.

Representative mapped table/cell examples:

| Sample | Block type | Section | Page | Table id | Row locator | Locator summary |
| --- | --- | --- | ---: | --- | --- | --- |
| S1-current-envelope | table | `§2` | 5 | `#/tables/2` | n/a | `source_ref=#/tables/2; table_index=2; has_bbox=True` |
| S1-current-envelope | cell | `§2` | 5 | `#/tables/2` | `cell:r0:c0:idx0` | `source_ref=#/tables/2; row_index=0; column_index=0; cell_index=0; has_bbox=True` |
| S1-current-envelope | cell | `§2` | 5 | `#/tables/2` | `cell:r1:c0:idx2` | `source_ref=#/tables/2; row_index=1; column_index=0; cell_index=2; has_bbox=True` |
| S1-current-envelope | table | `§3` | 6 | `#/tables/4` | n/a | `source_ref=#/tables/4; table_index=4; has_bbox=True` |

The examples prove that table/cell candidate anchors are now emitted from accepted local candidate envelopes. They do not prove that any cell value is field-correct, sourced to raw truth, complete, production-ready or release-ready.

## 6. Before/After Comparison

| Metric | Prior baseline | New re-evidence | Delta |
| --- | ---: | ---: | ---: |
| Candidate blocks | 23475 | 23475 | 0 |
| Mapped total | 102 | 9389 | +9287 |
| Mapped yield | 0.43% | 40.00% | +39.57 pp |
| Blocked total | 23373 | 14086 | -9287 |
| Table mapped | 0 | 154 | +154 |
| Cell mapped | 0 | 8947 | +8947 |
| Table/cell mapped | 0 | 9101 | +9101 |
| Table/cell mapped yield | 0.00% | 46.23% | +46.23 pp |

| Sample | Prior mapped | New mapped | Prior blocked | New blocked | Prior table/cell mapped | New table/cell mapped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S1-current-envelope | 10 | 2074 | 4273 | 2209 | 0 | 1845 |
| S4-full | 33 | 820 | 3788 | 3001 | 0 | 803 |
| S5-full | 28 | 5967 | 8217 | 2278 | 0 | 5946 |
| S6-full | 31 | 528 | 7095 | 6598 | 0 | 507 |
| Total | 102 | 9389 | 23373 | 14086 | 0 | 9101 |

The new evidence materially improves candidate mapping yield, especially for table/cell candidate anchors. Residual blocking remains non-trivial, concentrated in `missing_section_context`, and S6 remains low-yield relative to the other accepted envelopes.

## 7. Candidate-only Status Assertions

The local script asserted these properties on every emitted mapped and blocked record:

| Assertion | Count |
| --- | ---: |
| mapped `candidate_only=True` | 9389 |
| mapped `candidate_source="docling"` | 9389 |
| mapped `field_correctness_status="not_proven"` | 9389 |
| mapped `source_truth_status="not_proven"` | 9389 |
| blocked `candidate_only=True` | 14086 |
| blocked `candidate_source="docling"` | 14086 |
| blocked `field_correctness_status="not_proven"` | 14086 |
| blocked `source_truth_status="not_proven"` | 14086 |

Observed envelope status for all four mapped envelopes remains:

```text
candidate_status=not_proven
field_correctness_status=not_proven
source_truth_status=not_proven
taxonomy_compatibility_status=not_proven
production_parser_replacement_status=not_authorized
```

## 8. Proof Boundaries

| Boundary token | Status |
| --- | --- |
| `not_field_correctness_proof` | This artifact maps candidate locator context only; it does not verify table/cell field values against source excerpts. |
| `not_source_truth` | Local Docling candidate JSON remains candidate-layer evidence only; it is not raw XML/XBRL/PDF/source truth. |
| `not_readiness_proof` | Mapping yield improvement does not prove baseline promotion, release, readiness or PR suitability. |
| `no_repository_behavior_change` | This gate ran local JSON projection and candidate mapping only; it made no repository, parser, source policy, production `EvidenceAnchor`, Service/Host/UI/renderer/quality-gate change. |

## 9. Validation Commands

Commands run:

```bash
uv run python -c "<local JSON parsing via project_candidate_representation + map_candidate_document_anchor_candidates>"
git diff --check
```

Observed result:

| Check | Result |
| --- | --- |
| Local JSON projection and mapping | passed for S1 current envelope and S4/S5/S6 full envelopes |
| S1 full JSON residual | blocked by `ValueError: unsupported candidate representation schema_version` |
| Candidate-only assertions | passed for all `9389` mapped and `14086` blocked records |
| `git diff --check` | passed |

## 10. Evidence Judgment

This evidence supports:

- deterministic section-context enrichment improved accepted local candidate mapping yield from `102 / 23475 = 0.43%` to `9389 / 23475 = 40.00%`;
- table/cell candidate mapping yield improved from zero to `9101 / 19688 = 46.23%`;
- emitted table/cell mappings remain candidate-only and retain `field_correctness_status="not_proven"` and `source_truth_status="not_proven"`;
- S1 full JSON remains blocked as an unsupported schema residual and should not be treated as mapped evidence.

This evidence does not support:

- field correctness;
- source truth;
- production `EvidenceAnchor` admission;
- production parser/repository/source policy/Service/Host/UI/renderer/quality-gate behavior change;
- Docling baseline promotion;
- readiness, release, PR, push or merge state.

## 11. Residuals

| Residual | Evidence status | Owner |
| --- | --- | --- |
| `missing_section_context` still accounts for `13209 / 14086 = 93.77%` of blocked records. | residual blocker | Fund documents candidate owner |
| S6 table/cell yield remains low: `507 / 6064 = 8.36%`. | residual sample-specific mapping gap | Fund documents candidate owner |
| S1 full JSON is still not a supported candidate envelope. | residual schema/export mismatch | Fund documents candidate owner |
| S1-current-envelope and S1-full-json use different artifact shapes; S1 mapped counts only represent the accepted envelope path. | residual artifact-chain transparency gap | Fund documents candidate owner |
| S4/S5/S6 paragraph mapping remains zero while S1 contributes all mapped paragraph records. | residual schema-family/mapping-scope gap | Fund documents candidate owner |
| Field correctness and source truth are still unproven. | explicit non-proof | future comparative/source-truth gate |
| Release/readiness remains `NOT_READY`. | preserved | future readiness gate |

## 12. Final Verdict

```text
VERDICT: ACCEPT_REEVIDENCE_IMPROVED_MAPPING_NOT_READY
```
