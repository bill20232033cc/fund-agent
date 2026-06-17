# Docling Dedicated Extractor Template-field Mapping Plan Re-review (MiMo) - 2026-06-17

Status: re-review artifact
Review target: `docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-20260617.md` (updated version)
Prior review: `docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-review-mimo-20260617.md`
Reviewer: AgentMiMo
Classification: heavy plan re-review

## Re-review Scope

Three specific gaps from prior review. Check whether updated plan resolves them without introducing new blockers.

## 1. `field_path` naming convention — RESOLVED

**Prior gap:** `field_path` string values in `CandidateTemplateField` were not specified. `DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS` was missing.

**Updated plan (lines 99-127):** Now defines `DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS` as a tuple of 23 exact dot-notation strings:

- `basic_identity.fund_name`, `basic_identity.fund_code`, etc. for profile fields
- `nav_benchmark_performance.nav_growth_rate`, `nav_benchmark_performance.benchmark_return_rate` for performance subfields
- `tracking_error.value_text` for tracking error
- `portfolio_managers`, `turnover_rate` for manager fields (no dot-notation, single-value fields)
- `manager_alignment.manager_holding_range` for manager alignment
- `holdings_snapshot.top_holdings`, `holdings_snapshot.bond_top_holdings`, `holdings_snapshot.target_fund_holdings` for holdings subfields
- `manager_strategy_text`, `holder_structure`, `share_change`, `bond_risk_evidence` as unimplemented-but-present paths

**Verdict: Resolved.** The naming convention is now explicit. The 23 paths cover all 20 `StructuredFundDataBundle` fields (with `basic_identity`, `product_profile`, `nav_benchmark_performance`, `holdings_snapshot`, and `fee_schedule` decomposed into subfield paths). `index_profile` and `nav_data` / `source_provenance` are absent from the constant but this is acceptable — they are either derived fields (`index_profile` depends on fund type classification) or not extractable from annual-report text (`nav_data` comes from external NAV provider, `source_provenance` is metadata).

## 2. Unimplemented field missing rules — RESOLVED

**Prior gap:** `manager_strategy_text` was in `SNAPSHOT_FIELD_ORDER` but not in the plan's target field table, risking silent omission.

**Updated plan (lines 122, 129):**

- `manager_strategy_text` is now in `DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS` (line 122).
- Line 129 explicitly states: "Paths not implemented in the first pass, including `manager_strategy_text`, `holder_structure`, `share_change`, and `bond_risk_evidence`, must still be emitted with `extraction_mode='missing'` and stable missing notes."
- Invariant at line 203-204: "Every target field path must produce exactly one `CandidateTemplateField`. Missing values use `extraction_mode='missing'`, `value=None`, `anchors=()`, and a stable note."

**Verdict: Resolved.** The plan now guarantees no silent omission: all 23 paths produce exactly one field, unimplemented ones are explicitly listed, and the missing construction contract is specified.

## 3. Relationship to `evidence_anchor_mapping.py` — RESOLVED

**Prior gap:** Boundary between the new module and existing `evidence_anchor_mapping.py` was not stated. Potential duplication of section-resolution logic.

**Updated plan (lines 208-214):** New section "Relationship to `evidence_anchor_mapping.py`" explicitly states:

- `template_field_extraction.py` consumes `CandidateRepresentationDocument` directly.
- It does NOT consume `CandidateEvidenceAnchorMappingResult`.
- It may reuse locator concepts but must not duplicate production `EvidenceAnchor` creation.
- `CandidateTemplateFieldAnchor` is candidate-only; consumers must use `candidate_only=true` and `source_truth_status=not_proven` to prevent production-anchor promotion.
- A later integration gate may define projection from candidate template fields to production `ExtractedField` / `EvidenceAnchor`; that projection is not authorized here.

**Verdict: Resolved.** The relationship is now explicit. The two modules are independent consumers of `CandidateRepresentationDocument` with different output contracts. Section-resolution logic may overlap in implementation, but the plan correctly constrains this to candidate-only semantics and defers production projection to a later gate.

## New Blocker Check

The three additions (`DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS`, missing-field explicit list, `evidence_anchor_mapping.py` relationship) do not introduce new blockers:

- The 23-path constant is consistent with `StructuredFundDataBundle` field structure.
- The missing-field contract is consistent with the existing `extraction_mode="missing"` pattern in `ExtractedField`.
- The `evidence_anchor_mapping.py` boundary clarification reduces ambiguity without changing scope or invariants.

---

REREVIEW_PASS_NOT_READY
