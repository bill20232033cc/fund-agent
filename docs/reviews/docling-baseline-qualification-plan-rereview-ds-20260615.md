# Docling Baseline Qualification Plan Re-Review - DS

Date: 2026-06-15

Gate: `Docling Baseline Qualification Planning Gate`

Role: DS targeted re-review worker only — closure verification

Prior review: `docs/reviews/docling-baseline-qualification-plan-review-ds-20260615.md`

Verdict: `PASS_CLOSURE`

## 1. Re-Review Scope

This re-review verifies closure of five accepted required fixes against the updated plan
(`docs/reviews/docling-baseline-qualification-plan-20260615.md`, status `PLAN_FIXED_NOT_READY`).
No new findings are generated; scope is strictly closure verification.

## 2. Closure Table

| Fix | Prior finding | Closure location | Closure mechanism | Verdict |
|-----|--------------|-----------------|-------------------|---------|
| DS-F1 / MiMo-P2 | S2-S6 field correctness reference facts undefined; Gate D untestable for 5/6 samples | Gate 0D, Gate D D1/D2 separation, Section 4, Section 11 step 4, Section 12 | Gate 0D added as prerequisite for field-reference establishment. Gate D split into D1 (identity/structural, runs for all samples) and D2 (true field correctness, only over accepted reference IDs). D2 pass thresholds explicitly scoped to fields with accepted reference ids. Reference coverage rules: S1-S4 high-priority, S5-S6 identity/source-document only; verdict capped at hybrid/auxiliary without controller scope acceptance. | **CLOSED** |
| DS-F2 / MiMo-P1 | S2-S6 pdfplumber baseline undefined; Gate B coverage metrics uncomputable for 5/6 samples | Gate 0C, Gate 0 pass thresholds, Section 4, Section 11 step 3, Section 12 | Gate 0C added: "pdfplumber full representation export" for every active sample. Gate 0 pass threshold: "100% active samples have accepted pdfplumber full representation JSON before Gate B." Section 11 step 3 sequences Pdfplumber Export Gate before Gate A. Section 4 explicitly records S2-S6 pdfplumber JSONs as not currently accepted. | **CLOSED** |
| MiMo-P3 | Dependency chain before Gate A insufficient | Section 11 | Eleven-step required dependency chain added: (1) acquisition status planning, (2) bounded EID-only acquisition if needed, (3) pdfplumber export, (4) reference-fact acquisition, (5) runner planning — all before (6) Gate A runtime containment. Explicit prerequisite sequencing established. | **CLOSED** |
| DS-F3 | Gate A auxiliary verdict escape hatch unmapped to Section 10 verdicts | Gate A pass thresholds, Section 10 `DOCLING_REMAINS_AUXILIARY_CANDIDATE_NOT_READY` | Gate A now states: "Exactly 1 isolated, profile-specific, fully classified fail-closed conversion failure can only map to `DOCLING_REMAINS_AUXILIARY_CANDIDATE_NOT_READY` at Gate F." Section 10 adds matching criterion: "Exactly 1 isolated, profile-specific, fully classified fail-closed Gate A conversion failure occurs." Unclassified or 2+ failures map to `REJECTED`. | **CLOSED** |
| Nonblocking: performance threshold calibration | Gate E threshold was absolute without calibration path | Gate E pass thresholds | Gate E now: "Performance thresholds are tentative until Gate A logs establish the current hardware/runtime baseline. Initial watch target is cold conversion p95 <= 120 seconds... Gate E evidence must either confirm this target or propose a controller-reviewed calibrated threshold from Gate A logs before disposition." Calibration path from Gate A logs confirmed. | **CLOSED** |
| Nonblocking: page parity classification | Page count parity was binary 100% without classification escape | Gate B pass thresholds | Gate B now: "Page count differences versus pdfplumber are not blind failures if classified as route representation differences, but any unexplained missing source page is a blocker." Classification escape added; only unexplained missing pages block. | **CLOSED** |
| Nonblocking: hybrid semantics | Hybrid route combination deferred without minimum semantics | Section 7 | Section 7 now defines explicit minimum hybrid semantics: Docling as PDF-derived page/bbox/table primary, pdfplumber as production baseline reference, EID HTML render as official locator supplement, fail-closed conflict resolution, all routing inside FundDocumentRepository. Deferred to later hybrid routing design gate unless Gate F selects `HYBRID_PRIMARY`. | **CLOSED** |

## 3. Residual Observations (Nonblocking)

- The 0.80–1.30 table count range from DS-F4 remains unchanged. The plan already includes the taxonomy-classification alternative path, and the original review classified this as low severity. Not a required fix — deferred to Gate B evidence worker judgment.
- EID HTML render availability for S2-S6 (DS-F5) remains unclassified. Gate 0E explicitly requires classification before Gate D, and Gate D degrades to two-route where unavailable. The plan now properly delegates this to Gate 0E rather than leaving it as a hidden assumption.

## 4. Validation

```text
git diff --check: passed
```

## 5. Final Re-Review Conclusion

**Verdict: `PASS_CLOSURE`**

All four required fixes (DS-F1, DS-F2, MiMo-P3, DS-F3) and three nonblocking clarifications
(performance threshold calibration, page parity classification, hybrid semantics) are properly
closed in the updated plan. No re-opened issues, no regressions, no new findings within re-review scope.

The plan status `PLAN_FIXED_NOT_READY` is accurate. The plan is ready for controller acceptance
and progression to the recommended next gate (`Docling Baseline Qualification Acquisition Status
Planning Gate`).

## 6. Reviewer Self-Check

- [x] Closure table covers all required fixes with specific locations and mechanisms.
- [x] No new findings outside re-review scope.
- [x] Verdict is `PASS_CLOSURE`.
- [x] Output path matches required artifact path: `docs/reviews/docling-baseline-qualification-plan-rereview-ds-20260615.md`.
