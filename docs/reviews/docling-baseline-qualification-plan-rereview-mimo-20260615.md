# Docling Baseline Qualification Plan — MiMo Targeted Re-Review

Date: 2026-06-15

Reviewer: AgentMiMo (targeted re-review worker only)

Review target: `docs/reviews/docling-baseline-qualification-plan-20260615.md`

Prior review: `docs/reviews/docling-baseline-qualification-plan-review-mimo-20260615.md`

Gate: `Docling Baseline Qualification Planning Gate`

## 1. Re-Review Scope

This re-review verifies closure for the accepted required fixes from the prior MiMo review and the DS controller judgment. Only the following items are in scope:

| Prior finding | Closure target |
|---|---|
| DS-F1 / MiMo-P2 | S2-S6 field correctness reference facts and Gate D scope |
| DS-F2 / MiMo-P1 | S2-S6 local artifacts and pdfplumber baseline prerequisites |
| MiMo-P3 | Dependency chain before Gate A |
| DS-F3 | Auxiliary verdict mapping |
| Nonblocking | Performance threshold calibration, page parity classification, hybrid semantics |

No source, test, runtime, control, design, or live edits. No stage/commit/push.

## 2. Closure Verification Table

### DS-F1 / MiMo-P2 — S2-S6 field correctness reference facts and Gate D scope

**Prior finding**: Gate D 98% threshold depended on nonexistent golden/reviewed baseline for S2-S6. No reference facts existed beyond S1 seven-row strict golden.

**Plan fix evidence**:

- Gate D now has two explicit layers: D1 identity/structural comparison (runs without golden, lines 297-298, 345-346) and D2 true field correctness (requires Gate 0D accepted references, lines 298, 347-349).
- Gate 0D is defined as sub-gate for "field-reference establishment" with output "Accepted reference-fact manifest by sample and field family" (line 103).
- Gate 0 pass threshold explicitly states: "Gate D true field correctness scope is limited to sample/field-family pairs with accepted same-report reviewed/golden reference facts" (line 124).
- Gate D stop condition: "Any D2 field is scored without an accepted reference id" (line 359).
- §11 dependency chain places `Same-report Manual Reviewed Reference Facts / Golden Reference Acquisition Gate` as step 4, before Gate D (line 620).
- Reference coverage rule: "baseline-candidate verdict requires D2 coverage for all high-priority field families for S1-S4 and identity/source-document references for S5-S6. If S5/S6 profile-specific field references are deferred, verdict cannot exceed hybrid or auxiliary" (line 349).

**Closure assessment**: ACCEPTED. The plan now explicitly separates D1 (no golden needed) from D2 (requires accepted references), scopes D2 to Gate 0D outputs only, and blocks D2 scoring without accepted reference ids. The prior finding is resolved.

---

### DS-F2 / MiMo-P1 — S2-S6 local artifacts and pdfplumber baseline prerequisites

**Prior finding**: S2-S6 had no proven local PDF artifacts, no pdfplumber exports, and Gate A could not execute. Five of six samples lacked accepted evidence.

**Plan fix evidence**:

- New Gate 0 with five sub-gates (0A-0E) explicitly handles all prerequisites (lines 92-126).
- 0A classifies S1-S6 as `accepted_local_artifact`, `needs_bounded_eid_acquisition`, `replace_required`, or `out_of_scope` (line 100).
- 0B handles bounded EID-only acquisition execution (line 101).
- 0C handles pdfplumber full representation export for all active samples (line 102).
- §4 artifact availability table explicitly distinguishes S1 (accepted) from S2-S6 (not proven), with "Required handling before evidence execution" column (lines 66-73).
- Gate 0 pass thresholds require: 100% active samples have accepted local EID-controlled PDFs or replacements; 100% have accepted pdfplumber JSONs before Gate B (lines 122-123).
- Gate A inputs now require "Gate 0 accepted EID-controlled local annual-report PDFs" (line 142).

**Closure assessment**: ACCEPTED. The plan now has an explicit prerequisite gate structure that classifies all samples, blocks Gate A until artifacts exist, and handles pdfplumber export as a separate sub-gate. The prior finding is resolved.

---

### MiMo-P3 — Dependency chain before Gate A

**Prior finding**: EID-only sample acquisition gate was undefined; plan required at least three sequential gates before Gate A evidence but did not declare the chain.

**Plan fix evidence**:

- §11 now has an explicit numbered dependency chain with 11 steps (lines 615-628):
  1. Acquisition Status Planning Gate
  2. Bounded EID-only Sample Acquisition Execution Gate (if needed)
  3. Pdfplumber Full Representation Export Planning/Execution Gate (if missing)
  4. Same-report Manual Reviewed Reference Facts / Golden Reference Acquisition Gate
  5. Docling/pdfplumber Runner Planning Gate (if needed)
  6. Gate A
  7. Gate B
  8. Gate C
  9. Gate D
  10. Gate E
  11. Gate F
- Each step has explicit conditions ("if needed", "if missing") preventing unnecessary gates.
- Gate 0 is defined as a prerequisite family with explicit sub-gates (lines 92-126).

**Closure assessment**: ACCEPTED. The dependency chain is now fully explicit, numbered, and conditional. The prior finding is resolved.

---

### DS-F3 — Auxiliary verdict mapping

**Prior finding**: Conversion failure mapping to verdict categories was incomplete; the auxiliary verdict path needed clearer classification criteria.

**Plan fix evidence**:

- Gate A pass thresholds now have explicit failure-to-verdict mapping (lines 181-183):
  - 0 conversion failures → eligible for `DOCLING_ELIGIBLE_AS_BASELINE_CANDIDATE_NOT_READY` or `DOCLING_ELIGIBLE_AS_HYBRID_PRIMARY_NOT_READY`
  - Exactly 1 isolated, profile-specific, fully classified fail-closed conversion failure → `DOCLING_REMAINS_AUXILIARY_CANDIDATE_NOT_READY`
  - Any unclassified conversion failure or 2+ conversion failures → `DOCLING_REJECTED_AS_BASELINE_CANDIDATE_NOT_READY`
- Failure taxonomy (§8) classifies `conversion_failure` with baseline impact: "Reject baseline candidate if unclassified or recurring; auxiliary only if isolated and fail-closed" (line 515).
- Verdict criteria (§10) `DOCLING_REMAINS_AUXILIARY_CANDIDATE_NOT_READY` lists explicit conditions including "Exactly 1 isolated, profile-specific, fully classified fail-closed Gate A conversion failure" (line 575).

**Closure assessment**: ACCEPTED. The auxiliary verdict now has clear classification criteria and explicit mapping from failure count/type to verdict. The prior finding is resolved.

---

### Nonblocking clarifications

**Performance threshold calibration**: FIXED. Gate E now states: "Performance thresholds are tentative until Gate A logs establish the current hardware/runtime baseline. Initial watch target is cold conversion p95 <= 120 seconds per annual report on the recorded CPU profile; Gate E evidence must either confirm this target or propose a controller-reviewed calibrated threshold from Gate A logs before disposition" (line 402). §9 acceptance summary also references "Gate E calibrated cold p95 threshold accepted from Gate A logs" (line 539).

**Page parity classification**: FIXED. Gate B now states: "Page count differences versus pdfplumber are not blind failures if classified as route representation differences, but any unexplained missing source page is a blocker" (line 230).

**Hybrid semantics**: FIXED. §7 now has explicit hybrid route combination semantics (lines 499-506): Docling as PDF page/bbox/table representation primary; pdfplumber as current production baseline reference; EID HTML render as official rendered-source locator supplement; conflict resolution is fail-closed with manual review. §7 also includes a table taxonomy for `data_table`, `layout_table`, `continuation_fragment`, `merged_header`, `non_table_block` classification (line 232).

**Closure assessment**: All three nonblocking clarifications are resolved.

## 3. Residual Observations

No new material findings. The following observations are informational only and do not block closure:

| # | Observation | Risk | Note |
|---|---|---|---|
| O1 | Gate 0D "field-reference establishment" has no explicit owner or acquisition method defined within this plan | Low | Deferred to `Same-report Manual Reviewed Reference Facts / Golden Reference Acquisition Gate` (§12 residual table, line 636). Acceptable since §11 dependency chain makes this explicit. |
| O2 | §11 dependency chain has up to 5 planning gates before Gate A evidence execution | Low | This is a consequence of the plan's conservative sequencing, not a defect. Controller can parallelize independent gates (e.g., 0C and 0D) if desired. |

## 4. Reviewer Self-Check

- [x] Re-review scope limited to accepted required fixes only
- [x] Each closure item has direct plan text evidence with line references
- [x] No source/test/runtime/control/design edits made
- [x] No live/network/EID/FDR/PDF download/Docling conversion executed
- [x] No stage/commit/push
- [x] Verdict is one of PASS_CLOSURE / PASS_WITH_NONBLOCKING_RESIDUALS / FAIL_REQUIRES_PLAN_FIX

## 5. Verdict

**Verdict: PASS_CLOSURE**

All four accepted required fixes (DS-F1/MiMo-P2, DS-F2/MiMo-P1, MiMo-P3, DS-F3) and all three nonblocking clarifications (performance threshold calibration, page parity classification, hybrid semantics) are resolved in the current plan. No new blocking findings. The plan is ready for controller judgment on disposition.
