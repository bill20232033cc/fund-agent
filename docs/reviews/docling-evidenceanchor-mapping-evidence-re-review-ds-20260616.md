# Docling EvidenceAnchor Mapping Evidence Re-review (DS) - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Evidence Fix Gate`
Role: AgentDS (evidence re-review)
Release/readiness: `NOT_READY`

## 1. Scope

Re-review the evidence-fix changes recorded in `docs/reviews/docling-evidenceanchor-mapping-evidence-fix-evidence-20260616.md` applied to `docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md`. No code changes, stage, commit, push, or PR.

## 2. Inputs Reviewed

| Artifact | Role |
|---|---|
| `docs/reviews/docling-evidenceanchor-mapping-evidence-review-ds-20260616.md` | Prior DS review (source of DS-F1) |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-fix-evidence-20260616.md` | Fix evidence |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md` | Patched evidence artifact |

## 3. Allowed Command

```bash
git diff -- docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md docs/reviews/docling-evidenceanchor-mapping-evidence-fix-evidence-20260616.md
```

Result: clean (no diff). Both files are at committed/accepted state.

## 4. Fix Verification

### 4.1 DS-F1: Blocked Total Correction — VERIFIED

Fix evidence claims: corrected `23473` → `23373`.

Evidence doc §3 now reads: `Total blocked candidate blocks across accepted envelopes: 23373`.

Per-sample blocked totals from matrix: 4273 + 3788 + 8217 + 7095 = 23373. Match confirmed.

### 4.2 MiMo-F4: Overall Mapped Yield — VERIFIED

Fix evidence claims: added `102 / 23475 = 0.43%`.

Evidence doc §3 now reads: `Overall mapped yield across accepted envelopes: 102 / 23475 = 0.43%`.

Arithmetic check:
- Denominator: mapped(102) + blocked(23373) = 23475. Consistent with matrix totals.
- Ratio: 102 / 23475 ≈ 0.00435 = 0.43%. Rounded correctly.

### 4.3 MiMo-F6: Blocked Reason Distribution — VERIFIED

Fix evidence claims: added `missing_section_context=23363`, `unstable_section_context=10`, missing context = `99.96%`.

Evidence doc §3 now reads: `Blocked reason distribution across accepted envelopes: missing_section_context=23363, unstable_section_context=10. Missing section context accounts for 23363 / 23373 = 99.96% of blocked candidate blocks.`

Arithmetic check:
- missing_section_context sum from matrix: 4270 + 3786 + 8214 + 7093 = 23363. ✓
- unstable_section_context sum from matrix: 3 + 2 + 3 + 2 = 10. ✓
- 23363 + 10 = 23373 = total blocked. ✓
- 23363 / 23373 ≈ 0.99957 = 99.96%. ✓

### 4.4 No New Readiness/Source-Truth/Baseline Claim — VERIFIED

Post-fix evidence doc checked for scope creep:

| Check | Status |
|---|---|
| Title `Release/readiness: NOT_READY` preserved | ✓ |
| §4 candidate_only/not_proven status markers unchanged | ✓ |
| §7 does-not-support list intact (source truth, field correctness, table/cell readiness, baseline promotion, production parser replacement, readiness/release/PR) | ✓ |
| §8 residuals unchanged (table/cell yield, S1 schema, section normalization, non-production anchors → next gate remains section-context enrichment planning) | ✓ |
| §9 verdict unchanged: `ACCEPT_PARTIAL_HEADING_ONLY_MAPPING_EVIDENCE_NOT_READY` | ✓ |

No new claims introduced. All three fixes are purely additive or corrective derivations from existing matrix data.

## 5. Findings Summary

No new findings. DS-F1, MiMo-F4, and MiMo-F6 are all correctly addressed. The three fixes are narrow: one number correction, one yield ratio derivation, one reason-distribution consolidation — all from existing matrix values without introducing new claims or changing scope.

## 6. Final Verdict

```text
VERDICT: RE_REVIEW_PASS_NOT_READY
```

All three fix items verified: blocked aggregate corrected to 23373 (DS-F1), overall yield 102/23475=0.43% is arithmetically consistent (MiMo-F4), blocked distribution 23363+10=23373 with 99.96% missing-context dominance is arithmetically consistent (MiMo-F6). No new readiness, source-truth, or baseline claim introduced.
