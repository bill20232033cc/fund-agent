# Post-P15 Follow-up Plan Review — AgentMiMo（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

Planning artifact `docs/reviews/post-p15-follow-up-planning-20260522.md` is accepted with 3 non-blocking findings.

## Inputs

- Planning artifact: `docs/reviews/post-p15-follow-up-planning-20260522.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- P15-S1A code review judgment: `docs/reviews/p15-s1a-code-review-controller-judgment-20260522.md`
- Post-P14 follow-up plan review judgment: `docs/reviews/post-p14-follow-up-plan-review-controller-judgment-20260522.md`

## Review Checklist

### R1. Correctly rejects continuing to push 001548 production tracking_error golden

**PASS.** The artifact correctly grounds its rejection in the P15-S1A accepted result `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE` (line 7-8). It states that 001548 should not be repeatedly consumed as a candidate (line 40, First-principles criterion 4) and keeps 001548 out of production tracking_error golden implementation unless new reviewed direct evidence is accepted (line 99). This is consistent with the P15-S1A controller judgment which proved all 12 keyword hits were target/limit or manager narrative, not observed disclosure.

### R2. P16-S1 selection vs alternatives — correct prioritization

**PASS.** The Candidate Comparison table (lines 47-52) evaluates 5 options on product value and boundary/evidence risk. The selection of enhanced-index production golden expansion is correct because:

- P14 made tracking_error / index_profile conditional P1 denominators for index/enhanced-index, but enhanced-index currently only has 161725 fixture coverage (line 29).
- The 5 selected-fund candidates are real production funds from the selected CSV, making this the closest to closing the actual production quality gap.
- Source-metadata retry is correctly deferred: refreshing metadata cannot turn target/limit text into observed disclosure (line 49).
- Extractor early-return is correctly deferred: no false-negative case has been proven (line 50).
- Repo hygiene is correctly deferred as maintenance, not product evidence (line 51).
- Calculated tracking error is correctly deferred to a dedicated design/source/calculation phase (line 52).

### R3. Candidates from selected CSV; 161725 not misused

**PASS.** Verified against `docs/code_20260519.csv`:

| Fund code | In CSV | In planning artifact |
|---|---|---|
| 004194 | Yes — 招商中证1000指数增强A | Yes (line 79) |
| 005313 | Yes — 万家中证1000指数增强A | Yes (line 80) |
| 017644 | Yes — 博道中证1000指数增强A | Yes (line 81) |
| 019918 | Yes — 招商中证2000指数增强A | Yes (line 82) |
| 019923 | Yes — 华泰柏瑞中证2000指数增强A | Yes (line 83) |
| 161725 | Not in selected CSV | Correctly identified as fixture-only (line 29) |

The artifact explicitly states `161725` is "deterministic fixture coverage only, not selected-fund production golden evidence" (line 29). 161725 appears only in test fixtures (`test_profile.py`, `test_extraction_score.py`, `test_p1_sample_matrix.py`), confirming it is not a production selected-fund candidate.

### R4. Preserves FundDocumentRepository / FundDataExtractor boundaries, fail-closed, golden sequencing

**PASS.** The artifact:

- Requires `FundDocumentRepository.load_annual_report()` or `FundDataExtractor.extract()` for annual-report access (line 93).
- Requires direct observed disclosure for tracking_error with explicit evidence contract (lines 96-97).
- Stops for target/limit, narrative, benchmark-only tracking-error, standard-deviation-only, ambiguous, unparseable, and anchor-incomplete evidence (line 98).
- Prohibits direct golden edits in the plan gate (lines 103-104).
- Requires a separate golden implementation gate after evidence acceptance (lines 123-129).
- Routes extractor refinement to a separate implementation slice if a false negative is proven (line 99).

### R5. Scope not too large; stop conditions present; plan-review stays plan-review

**PASS with findings.** Scope is well-bounded. The plan-review gate only evaluates candidate evidence feasibility, not implementation. Stop conditions are explicit (lines 98, 142). However, see F1 regarding evaluation order and F2 regarding stop-condition completeness.

### R6. Residual owner / validation / file ownership

**PASS.** The Residuals table (lines 179-190) tracks all P15 residuals with owner/destination and status. File Ownership (lines 110-129) separates plan-review, evidence acquisition, and golden implementation. The Review Plan (lines 132-143) defines rejection criteria. Validation success signals (lines 147-175) cover plan, evidence-acquisition, and golden implementation stages.

## Findings

### F1 — Evaluation order not specified (LOW)

**Location:** `docs/reviews/post-p15-follow-up-planning-20260522.md` lines 76-83

**Issue:** The artifact lists 5 candidates in a table but does not define their evaluation order. The Validation Success Signals section (line 156) requires "exact candidate list and evaluation order are defined," but the artifact only provides the list.

**Impact:** The next plan artifact will need to define evaluation order anyway. This is a minor gap between the artifact's own success criteria and its content.

**Recommendation:** The P16-S1 plan artifact should explicitly define evaluation order. No revision required to this planning artifact; the finding should be carried into P16-S1 plan-review as an input note.

### F2 — index_profile benchmark-context contract less explicit than tracking_error direct-disclosure contract (LOW)

**Location:** `docs/reviews/post-p15-follow-up-planning-20260522.md` line 96

**Issue:** The Implementation Guardrails section has an explicit evidence contract for tracking_error (lines 96-97): observed value, period label, annualization support, source_type, calculation_method, and complete anchor. For index_profile, the contract is stated as "benchmark-only evidence as acceptable only for index_profile fields that are already supported by current extractor semantics" (line 96), which is less precise. The Validation Success Signals section (line 157) requires "direct evidence contract for tracking_error and benchmark-context contract for index_profile are explicit."

**Impact:** The P16-S1 plan artifact will need to define the index_profile benchmark-context contract more precisely. This does not block the planning artifact acceptance.

**Recommendation:** The P16-S1 plan artifact should enumerate which index_profile fields accept benchmark-context evidence and what constitutes sufficient anchor/provenance for each.

### F3 — No explicit handling for source-download failure during candidate evaluation (INFO)

**Location:** `docs/reviews/post-p15-follow-up-planning-20260522.md` lines 89-107

**Issue:** The guardrails cover evidence classification and stop conditions but do not explicitly state what happens if a candidate's annual report PDF cannot be downloaded or parsed (e.g., source not_found, unavailable, schema_drift). The P15-S1A evidence acquisition for 001548 succeeded because the report was available; some of the 5 new candidates may have different source availability.

**Impact:** Low. The FundDocumentRepository source fallback taxonomy (design.md section 6.1) already handles this with structured failure categories. The P16-S1 plan artifact should record per-candidate source blockers as part of evidence acquisition.

**Recommendation:** Carry into P16-S1 plan-review: per-candidate source availability should be recorded before evidence classification, and source blockers should be classified using the existing taxonomy (not_found, unavailable, schema_drift, identity_mismatch, integrity_error).

## Summary

The planning artifact correctly:

1. Refuses to continue pushing 001548 production tracking_error golden, grounded in the P15-S1A accepted negative result.
2. Selects P16-S1 enhanced-index production golden candidate evidence plan-review as the next gate, justified by first-principles criteria and candidate comparison.
3. Sources all 5 candidates from `docs/code_20260519.csv` and correctly treats 161725 as fixture-only.
4. Preserves FundDocumentRepository / FundDataExtractor boundaries, fail-closed behavior, and golden sequencing.
5. Maintains bounded scope with explicit stop conditions, file ownership, and residual tracking.

Three non-blocking findings should be carried into the P16-S1 plan-review as input notes. No revision to this planning artifact is required before acceptance.
