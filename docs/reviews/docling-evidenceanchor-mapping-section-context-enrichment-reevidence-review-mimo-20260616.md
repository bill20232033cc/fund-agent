# Re-evidence Review: Docling EvidenceAnchor Mapping Section-context Enrichment

Reviewer: AgentMiMo
Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment Re-evidence Review Gate`
Review date: 2026-06-16
Artifact under review: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-reevidence-20260616.md`
Implementation reference: `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`

## Scope

- Mode: evidence artifact review (role-scoped handoff)
- Input: re-evidence artifact plus referenced implementation/controller artifacts
- Focus: arithmetic consistency, baseline vs new counts, candidate-only assertions, table/cell yield calculation, S1 full JSON residual, verdict overclaim analysis, residual sufficiency

## Findings

### 1-未修复-低-S5 sample yield variance not explained

- **入口/函数**: Evidence artifact Section 4 (Re-evidence Result Matrix) and Section 6 (Before/After Comparison)
- **文件(行号)**: Evidence artifact lines 46-50, 96-102
- **输入场景**: Comparing per-sample yield improvement across S1/S4/S5/S6
- **实际分支**: S5 mapped jumped from 28 to 5967 (213x), while S4 went from 33 to 820 (25x) and S6 from 31 to 528 (17x). S5 and S6 share the same `S4_S5_S6_lightweight` schema family.
- **预期行为**: Evidence should note or investigate why enrichment impact varies dramatically across samples using the same schema family, especially when S6 remains at 8.36% yield.
- **实际行为**: The artifact reports S6 low yield as a residual (line 181) but does not provide per-sample blocked reason breakdown to explain the variance. S6 has `missing_section_context=6209`, `duplicate_section_heading=257`, `unsupported_heading_number=132` — the `duplicate_section_heading` rate for S6 (257/6598 = 3.9%) is much higher than S5 (2/2278 = 0.09%).
- **直接证据**: Evidence artifact lines 48-49 show S5 blocked reasons vs S6 blocked reasons; the `duplicate_section_heading` count is 128x higher in S6 than S5.
- **影响**: Without understanding the variance, the 40% overall yield improvement may not be generalizable. The residual flag is adequate for this gate but does not enable root cause triage.
- **建议改法和验证点**: Add per-sample blocked reason breakdown table to the evidence artifact (already partially present in Section 4 but not highlighted as variance analysis). A future gate should investigate whether S6's high `duplicate_section_heading` rate is caused by structural differences in the source PDF.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/低）**: 低

### 2-未修复-低-Total row heading paragraph count implicit decomposition

- **入口/函数**: Evidence artifact Section 4 Total row, mapped by block type column
- **文件(行号)**: Evidence artifact line 50
- **输入场景**: Reading the Total row's `mapped by block type` field
- **实际分支**: Total shows `heading=69, paragraph=219, table=154, cell=8947`. The paragraph count (219) comes entirely from S1-current-envelope. S4/S5/S6 have `paragraph=0`.
- **预期行为**: Evidence should note that paragraph mapping is S1-schema-specific (S1_full family has explicit paragraph blocks; S4_S5_S6_lightweight does not).
- **实际行为**: The Total row aggregates across schema families without noting that paragraph mapping is schema-family-specific. This is not an error but could mislead a reader into expecting paragraph mapping from lightweight schemas.
- **直接证据**: Implementation `evidence_anchor_mapping.py` line 26 shows `CandidateAnchorBlockType = Literal["heading", "paragraph", "table", "cell"]`; S4/S5/S6 samples have 0 paragraph mapped in Section 4.
- **影响**: Cosmetic clarity issue only. Does not affect arithmetic correctness or verdict validity.
- **建议改法和验证点**: Optional: add a footnote that paragraph mapping is only available for S1_full schema family.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/低）**: 低

## Arithmetic Verification

All arithmetic in the evidence artifact was independently verified:

| Check | Result |
| --- | --- |
| Total candidate blocks: 4283+3821+8245+7126 = 23475 | PASS |
| Total mapped: 2074+820+5967+528 = 9389 | PASS |
| Total blocked: 2209+3001+2278+6598 = 14086 | PASS |
| Mapped + Blocked = 23475 | PASS |
| Mapped yield: 9389/23475 = 40.00% | PASS |
| Table yield: 154/436 = 35.32% | PASS |
| Cell yield: 8947/19252 = 46.47% | PASS |
| Table+Cell yield: 9101/19688 = 46.23% | PASS |
| Per-sample mapped+blocked=candidates | PASS |
| Per-sample mapped_by_type sum = mapped | PASS |
| Per-sample blocked_reasons sum = blocked | PASS |
| Blocked reason totals: 13209+424+453 = 14086 | PASS |
| Blocked reason shares: 93.77%+3.01%+3.22% = 100.00% | PASS |
| Section 6 delta consistency (mapped_delta = -blocked_delta per sample) | PASS |
| Section 6 total prior: 102+23373 = 23475 | PASS |
| Section 6 total new: 9389+14086 = 23475 | PASS |

## Candidate-only Assertion Verification

The evidence claims all 9389 mapped and 14086 blocked records have `candidate_only=True`, `candidate_source="docling"`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`.

The implementation structurally enforces this:
- `CandidateEvidenceAnchorMapping.__post_init__` (lines 125-145) raises `ValueError` if `candidate_source != "docling"`, `candidate_only is not True`, `field_correctness_status != "not_proven"`, or `source_truth_status != "not_proven"`.
- `CandidateEvidenceAnchorMappingBlocked` (lines 148-161) defaults these fields to the same constrained values.

The assertion counts (9389 mapped + 14086 blocked = 23475 total) are consistent with the candidate block total. No overclaim detected.

## S1 Full JSON Residual Verification

Confirmed: `reports/representation-json/004393_2025_docling_full.json` has `schema_version: None` at top level. The `project_candidate_representation()` function raises `ValueError` for null schema_version, consistent with the evidence claim (line 23). The S1-current-envelope artifact (`004393_2025_docling_current_envelope.json`) was used instead, which is an accepted candidate envelope. The residual is correctly scoped.

## Verdict Overclaim Analysis

The verdict `ACCEPT_REEVIDENCE_IMPROVED_MAPPING_NOT_READY` was checked against the evidence boundaries:

| Claim | Overclaim? | Assessment |
| --- | --- | --- |
| Enrichment improved mapping yield | No | Before/after comparison is on same samples, same candidate blocks (23475). Delta is deterministic. |
| Field correctness | No | Explicitly listed as "not supported" (Section 10) and "not_proven" in assertions. |
| Source truth | No | Explicitly listed as "not supported" (Section 10). |
| Readiness/release | No | Verdict ends with `_NOT_READY`; Section 8 proof boundaries explicit. |
| Baseline promotion | No | Section 8 `not_readiness_proof` token present. |
| Repository behavior change | No | Section 8 `no_repository_behavior_change` token present. |

No overclaim detected. The verdict is appropriately hedged.

## Residual Sufficiency

| Residual | Assessment |
| --- | --- |
| `missing_section_context` = 93.77% of blocked | Adequately flagged as residual blocker. Root cause analysis is out of scope for this evidence gate. |
| S6 low yield (8.36%) | Adequately flagged. Finding 1 adds context: S6 has 128x higher `duplicate_section_heading` rate than S5, suggesting sample-specific structural issues. |
| S1 full JSON schema residual | Correctly documented as schema/export mismatch. Verified `schema_version=null`. |
| Field correctness / source truth unproven | Explicitly maintained as non-proof. Appropriate for candidate-layer evidence. |

The residuals are sufficient for this gate's scope. They correctly identify blockers without overclaiming resolution.

## Open Questions

- What drives the 128x difference in `duplicate_section_heading` between S5 (2) and S6 (257) when both use the same schema family? This is a data investigation question, not an implementation defect.

## Residual Risk

- The 40% overall yield is sample-dependent. Generalization to other fund documents is unproven.
- The evidence does not verify whether mapped table/cell anchors produce correct field values when consumed downstream.
- No test coverage was reviewed for the enrichment implementation in this gate (out of scope per role constraints).

## Final Verdict

```text
VERDICT: PASS_WITH_FINDINGS_NOT_READY
```

The evidence artifact is internally consistent. All arithmetic checks pass. The verdict does not overclaim baseline, readiness, source truth, or field correctness. Candidate-only assertions are structurally enforced by the implementation. Residuals are adequately documented. Two low-severity findings are noted: unexplained per-sample yield variance (especially S6's high `duplicate_section_heading` rate) and implicit schema-family-specific paragraph mapping in the Total row.
