# Docling Dedicated Extractor Template-field Mapping Plan — AgentDS Targeted Re-review — 2026-06-17

Status: `REREVIEW_COMPLETE_NOT_READY`
Role: AgentDS plan reviewer
Re-review target: `docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-20260617.md` (updated)
Prior DS review: `docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-review-ds-20260617.md`
MiMo review: `docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-review-mimo-20260617.md`

## Re-review Scope

Targeted check of three new additions against prior DS and MiMo non-blocking observations. Whether they resolve the concerns without introducing new blockers.

## Check 1 — `DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS` (lines 102–126)

**Prior concern (MiMo Gap 1):** `field_path` naming convention not specified, leaving ambiguity across slices.

**New content:** 24 concrete dot-notation field path strings. 16 match the table fields. 4 explicitly deferred (`manager_strategy_text`, `holder_structure`, `share_change`, `bond_risk_evidence`). Path names follow `SNAPSHOT_FIELD_ORDER` subfield conventions (e.g., `nav_benchmark_performance.nav_growth_rate`, `tracking_error.value_text`, `holdings_snapshot.top_holdings`).

**Verdict:** Resolved. No new blocker. Path names are concrete and directly usable as `field_path` literals in Slice 1 contract definition.

## Check 2 — Unimplemented fields missing rule (line 129)

**Prior concern (MiMo Gap 3):** `manager_strategy_text` not listed in explicit missing-field paths, risk of silent omission.

**New content:** "Paths not implemented in the first pass, including `manager_strategy_text`, `holder_structure`, `share_change`, and `bond_risk_evidence`, must still be emitted with `extraction_mode="missing"` and stable missing notes."

The invariant "Every target field path must produce exactly one CandidateTemplateField" (line 203) was already present. The new text pins which specific paths are deferred and mandates their emission as missing. Slice 1 tests already verify "missing fields are explicit and not omitted."

**Verdict:** Resolved. No new blocker. The deferred-path list is explicit and complete. Combined with the existing one-field-per-path invariant, silent omission is ruled out.

## Check 3 — Relationship to `evidence_anchor_mapping.py` (lines 208–214)

**Prior concerns:**
- DS observation 2: `CandidateTemplateFieldAnchor.source_kind` uses same literal as production `EvidenceAnchor`, risk of accidental promotion.
- MiMo Gap 2: boundary with `evidence_anchor_mapping.py` unclear — does new module consume mapping results or operate independently?
- MiMo Gap 5: no future integration path sketch.

**New content:**

1. "`template_field_extraction.py` does not consume `CandidateEvidenceAnchorMappingResult`." — Independent operation confirmed. Addresses MiMo Gap 2.

2. "It may reuse the same section/table/cell locator concepts, but it must not duplicate production `EvidenceAnchor` creation or return production `EvidenceAnchor`." — Permits locator reuse, forbids production anchor leak. Addresses DS observation 2 at the behavioral level.

3. "`CandidateTemplateFieldAnchor` is a candidate-only anchor shape. Its `source_kind="annual_report"` mirrors annual-report semantics only; consumers must use the parent `candidate_only=true` and `source_truth_status="not_proven"` fields to prevent production-anchor promotion." — Type-level distinction enforced by contract rule. Addresses DS observation 2 at the contract level.

4. "A later integration gate may define a reviewed projection from accepted candidate template fields to production `ExtractedField` / `EvidenceAnchor`; that projection is not authorized here." — Future integration path acknowledged and explicitly gated. Addresses MiMo Gap 5 (acknowledgment only, not a path sketch — sufficient for this gate).

**Verdict:** Resolved. No new blocker. The relationship is now explicit: independent operation, locator reuse allowed, production anchor creation forbidden, future integration gated.

## Remaining Non-blocking Observation

**DS observation 3** (plan does not explicitly close/suspend current active gate `Docling Field Correctness Comparative Evidence Gate`) remains. This is a controller handoff concern, not a plan defect. The plan states its new direction clearly; the controller handles the transition when accepting.

## New Blocker Scan

- Does `DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS` contradict the table (e.g., subfield granularity mismatch)? No. Table entries like `nav_benchmark_performance` are refined to `nav_benchmark_performance.nav_growth_rate` / `.benchmark_return_rate` in DEFAULT — this is specificity improvement, not contradiction.
- Does the missing rule allow partial extraction (e.g., holdings_snapshot partially covered)? Yes — the table says "first equity/bond/target-fund holding rows." DEFAULT lists exactly `holdings_snapshot.top_holdings`, `.bond_top_holdings`, `.target_fund_holdings`. If rows are found they're extracted; if not they're missing. No gap.
- Does the relationship section introduce dependency on `evidence_anchor_mapping.py`? No — it explicitly states the new module does NOT consume mapping results.
- Does anything weaken candidate-only / NOT_READY / no parser replacement? No — all constraints unchanged from original plan.

## Verdict

REREVIEW_PASS_NOT_READY
