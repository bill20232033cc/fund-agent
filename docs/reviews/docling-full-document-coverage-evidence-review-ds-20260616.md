# Docling Full-document Coverage Evidence — AgentDS Scoped Evidence Review

Date: 2026-06-16
Reviewer: AgentDS
Role: scoped evidence review
Release/readiness: `NOT_READY`

## 1. Scope

This review covers the `Docling Full-document Coverage Evidence Gate` artifact at `docs/reviews/docling-full-document-coverage-evidence-20260616.md` and its supporting summary JSON at `reports/docling-full-document-coverage/20260616/coverage-summary.json`.

Per the controller's gate scope, this review:
- Does not run Docling conversion, live/network/EID/FDR/PDF/source acquisition/provider/LLM/analyze/checklist/golden/readiness/release/PR commands.
- Does not modify files.
- Preserves release/readiness = `NOT_READY`.

## 2. Evidence Reviewed

| Artifact | Role |
|---|---|
| `AGENTS.md` | Rule truth source |
| `docs/current-startup-packet.md` | Current active gate and guardrails |
| `docs/implementation-control.md` (lines 1-150) | Control truth and gate scope |
| `docs/reviews/docling-multi-sample-runtime-containment-reevidence-controller-judgment-20260616.md` | Prior accepted runtime containment judgment |
| `docs/reviews/docling-full-document-coverage-evidence-20260616.md` | Evidence under review |
| `reports/docling-full-document-coverage/20260616/coverage-summary.json` | Machine-readable coverage summary |
| `reports/docling-runtime-containment/20260616/outputs/006597_2024_docling_full.json` | S4 candidate output (structural verification only) |

## 3. Review Findings

### 3.1 Review Focus 1: Evidence 是否只读 candidate Docling JSON，不重跑转换

**Finding: PASS**

Evidence Section 1 explicitly states "It does not run Docling conversion." Section 3 states "The evidence worker read the four local candidate JSON files and computed [coverage metrics]." Section 8 validation commands are all read-only: `git status`, `jq` queries against existing JSONs, `python -m json.tool` for pretty-printing, and local JSON coverage computation.

No evidence of Docling conversion, model loading, network access, or any write/side-effect operation was found in the evidence artifact or its validation section. The four input JSONs were all produced by prior accepted gates:
- S1: pre-existing `reports/representation-json/004393_2025_docling_full.json` from earlier representation evidence
- S4/S5/S6: isolated runtime outputs accepted by the runtime containment re-evidence controller judgment

### 3.2 Review Focus 2: Coverage metrics 是否与 summary JSON 一致，是否覆盖 S1/S4/S5/S6

**Finding: PASS**

All metrics in the evidence artifact Section 4 (Coverage Matrix) were cross-checked against `coverage-summary.json`:

| Sample | Metric | Evidence | Summary JSON | Match |
|---|---|---|---|---|
| S1 | page_count | 65 | 65 | Yes |
| S1 | heading_count | 213 | 213 | Yes |
| S1 | paragraph_count | 457 | 457 | Yes |
| S1 | table_count | 95 | 95 | Yes |
| S1 | table_cell_count | 3493 | 3493 | Yes |
| S1 | pages_with_any_block_pct | 100% | 100 | Yes |
| S1 | missing section keywords | none | [] | Yes |
| S4 | page_count | 70 | 70 | Yes |
| S4 | heading_count | 229 | 229 | Yes |
| S4 | paragraph_count | 737 | 737 | Yes |
| S4 | table_count | 96 | 96 | Yes |
| S4 | table_cell_count | 2759 | 2759 | Yes |
| S5 | page_count | 110 | 110 | Yes |
| S5 | heading_count | 208 | 208 | Yes |
| S5 | paragraph_count | 856 | 856 | Yes |
| S5 | table_count | 121 | 121 | Yes |
| S5 | table_cell_count | 7060 | 7060 | Yes |
| S6 | page_count | 84 | 84 | Yes |
| S6 | heading_count | 222 | 222 | Yes |
| S6 | paragraph_count | 840 | 840 | Yes |
| S6 | table_count | 124 | 124 | Yes |
| S6 | table_cell_count | 5940 | 5940 | Yes |

All four samples (S1, S4, S5, S6) are covered. Locator percentages (100%), gap flags, and missing-keyword arrays are consistent between evidence and summary JSON.

Overall flags in summary JSON (`candidate_only`, `not_source_truth`, `not_full_field_correctness`, `not_baseline_promotion`, `not_readiness_proof`) are all `true` and consistent with the evidence artifact's boundary declarations.

**Observation on heading page distribution**: S5 has `pages_with_heading: 64` out of 110 pages (58%), the lowest ratio among the four samples. This is normal for financial reports (many pages are tables without headings) and is not flagged as a gap. The heading locator coverage of 100% (every heading that exists has a locator) is the correct metric — not heading-per-page density.

### 3.3 Review Focus 3: 是否错误把 coverage signal 升级为 source truth/full correctness/baseline/readiness

**Finding: PASS**

The evidence artifact explicitly and correctly rejects these upgrades:

- Section 1 preserves: `candidate_only`, `not_source_truth`, `not_full_field_correctness`, `not_baseline_promotion`, `not_readiness_proof`
- Section 5 states: "This is a coverage signal only. It does not prove semantic correctness, value correctness, or source truth."
- Section 6 Accepted Candidate Coverage Facts explicitly REJECTS: full field correctness, source truth, baseline promotion, readiness/release.
- Section 9 Verdict ends with `NOT_READY`.

The summary JSON carries the same boundary flags as `true`. The verdict token `ACCEPT_FULL_DOCUMENT_COVERAGE_EVIDENCE_READY_FOR_EVIDENCEANCHOR_MAPPING_PLANNING_NOT_READY` correctly scopes the acceptance to coverage evidence and explicitly defers readiness.

No scope creep or signal upgrade was observed.

### 3.4 Review Focus 4: 是否对 lightweight schema 的 locator 解释合理

**Finding: PASS_WITH_OBSERVATION**

Evidence Section 3 describes the locator schemas:

> S1 uses the current full representation schema with `pages` and `provenance_locator` objects. S4/S5/S6 use the runtime-containment candidate schema, where table-cell locator is represented by `table_id + table.page_number + cell_index + row_start + column_start`. The evidence treats both forms as candidate locator evidence only.

Structural verification of S4 (`006597_2024_docling_full.json`) confirms:
- Headings have `page_number` — locator present.
- Paragraphs have `page_number` — locator present.
- Tables have `table_id`, `page_number` — table-level locator present.
- Cells have `cell_index`, `row_start`, `column_start`, `bbox` — cell-level positional fields present.
- Cells do **not** carry `table_id` or `page_number` directly; these are on the parent table object.

The evidence description of cell locator as "`table_id + table.page_number + cell_index + row_start + column_start`" is functionally correct as a composite locator strategy, but slightly imprecise: the cell object itself only carries `cell_index + row_start + column_start`, and the `table_id + page_number` must be obtained from the parent table. This has no impact on the coverage measurement (all cells have the full composite path available), but it is relevant for EvidenceAnchor mapping: a cell cannot be independently located from its own fields alone without table context.

The evidence's framing of both schemas as "candidate locator evidence only" is appropriate and does not claim production-grade locator quality.

### 3.5 Review Focus 5: Verdict 是否可进入 EvidenceAnchor mapping planning，且仍保持 NOT_READY

**Finding: PASS**

The verdict `ACCEPT_FULL_DOCUMENT_COVERAGE_EVIDENCE_READY_FOR_EVIDENCEANCHOR_MAPPING_PLANNING_NOT_READY` is appropriate:

1. Full-document coverage across 4 samples of different fund types and page counts (65-110 pages) is demonstrated — no page gaps, no missing section families.
2. Locator presence is 100% across all element types, which is the necessary precondition for EvidenceAnchor mapping (you can't map anchors without locators).
3. The verdict explicitly ends with `NOT_READY`, maintaining the guardrail.
4. The phaseflow queue (`docs/implementation-control.md` line 139-141) lists EvidenceAnchor mapping as the next gate after coverage evidence:
   - Gate 30: Docling Full-document Coverage Evidence Gate
   - Gate 31: Docling EvidenceAnchor Mapping Evidence Gate
5. The runtime containment controller judgment also recommends this sequencing.

The coverage evidence establishes that the candidate JSONs are structurally complete enough to attempt EvidenceAnchor mapping. It does not claim that mapping will succeed or that mapped anchors will be correct.

### 3.6 Review Focus 6: 是否存在 blocker

**Finding: NO BLOCKERS**

No defect was found that blocks acceptance of this evidence. All six review foci pass.

## 4. Findings Table

| ID | Severity | Finding | Required Action |
|---|---|---|---|
| DS-F1 | LOW | Cell locator description in Section 3 is slightly imprecise: the cell object does not directly carry `table_id` or `page_number`; these are on the parent table. The composite locator interpretation is functionally correct but could mislead EvidenceAnchor mapping planning. | No fix required for this gate; note as context for EvidenceAnchor mapping planning gate. |
| DS-F2 | INFO | No computation script or code is preserved in the evidence artifact. The method references "node_repl local JSON coverage computation" without the actual computation logic. The summary JSON is the machine-readable output, but independent reproduction would require re-deriving the computation. | Not blocking; summary JSON serves as the accepted evidence output. Consider preserving the computation script in future coverage re-evidence or expansion gates. |
| DS-F3 | INFO | Section 5's 12 section keyword families are asserted as "common annual-report section families" without specifying how they were selected or whether they are fund-type-appropriate for all four samples (index fund `004393`, mixed/other for S4/S5/S6 with different report structures). | Not blocking for a coverage signal; would be relevant if section-family completeness is used for any correctness claim in future gates. |

## 5. Residuals

| Residual | Status | Owner | Notes |
|---|---|---|---|
| Cell locator precision for EvidenceAnchor mapping | open | documents/schema owner | EvidenceAnchor mapping planning should account for composite (table + cell) locator path |
| Computation script for coverage metrics | open | evidence worker | Optional: preserve for reproducibility in expansion gates |
| Section keyword family appropriateness by fund type | open | baseline qualification owner | Relevant if section coverage becomes a correctness signal rather than coverage signal |
| No independent verification of the four input JSONs | accepted | prior gate (runtime containment controller judgment) | This gate correctly relies on the prior accepted runtime containment evidence for input validity |

## 6. Final Verdict

```text
VERDICT: PASS
```

All six review foci pass. The evidence correctly reads only pre-existing candidate Docling JSONs, computes coverage metrics consistent with the summary JSON, covers all four samples (S1/S4/S5/S6), preserves candidate-only/NOT_READY boundaries, provides a reasonable locator schema interpretation, supports progression to EvidenceAnchor mapping planning, and contains no blockers.

Three non-blocking informational findings are recorded (DS-F1, DS-F2, DS-F3); none require evidence amendment before controller judgment.

## 7. Recommendation

Accept the evidence as `ACCEPT_FULL_DOCUMENT_COVERAGE_EVIDENCE_READY_FOR_EVIDENCEANCHOR_MAPPING_PLANNING_NOT_READY`. The three findings (DS-F1, DS-F2, DS-F3) should be carried as context into the EvidenceAnchor mapping planning gate but do not block the current gate closeout.
