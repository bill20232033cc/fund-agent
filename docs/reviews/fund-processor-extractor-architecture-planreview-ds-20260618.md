# Fund Processor/Extractor Architecture Plan Review — AgentDS

> **Gate**: Fund Processor/Extractor Architecture Planning Gate (heavy, docs/planning only)
> **Reviewer**: AgentDS
> **Date**: 2026-06-18
> **Review type**: adversarial plan review; no implementation, no fix, no commit, no push, no PR
> **Plan under review**: `docs/reviews/fund-processor-extractor-architecture-plan-20260617.md`
> **Truth-sync inputs**: `docs/reviews/fund-processor-extractor-truth-sync-review-ds-20260617.md`, `docs/reviews/fund-processor-extractor-truth-sync-review-mimo-20260617.md`

---

## Verdict

**PLANREVIEW_PASS_WITH_RISKS**

The plan is code-generation-ready for S1 implementation. It correctly preserves all architecture boundaries (UI→Service→Host→Agent, FundDocumentRepository, Processor/Extractor), properly constrains the first slice to no-live/additive-only, and has adequate fail-closed semantics. Three medium findings and three low findings are recorded below; none block the plan from entering S1 implementation gate, but each carries a concrete residual that the S1 implementation worker must disposition.

---

## Review Lenses Applied

### Architecture Boundary

| Check | Result | Evidence |
|-------|--------|----------|
| Processor/Extractor owned by Agent-layer `fund_agent/fund` | PASS | Plan line 125: "registry and processors belong under Agent-layer `fund_agent/fund`" |
| Service/UI/Host/renderer/quality gate see only processor outputs | PASS | Plan lines 123, 342-343; explicit S1 not-allowed list |
| `extract()` does not call `FundDocumentRepository` | PASS | Plan line 163 contract rule |
| No production parser replacement | PASS | Plan lines 26, 343 |
| No source policy change | PASS | Plan lines 26, 344 |
| No direct parser output consumption outside Fund documents/Processor | PASS | Plan lines 28-29, 343-344 |
| EID single-source policy preserved | PASS | Plan lines 694-719 (design.md §6.1), referenced by plan lines 53-54 |
| Dayu is reference only, not production runtime | PASS | Plan line 41-42 (AGENTS.md:83), disposition table MiMo F3 |
| `extra_payload` prohibition respected | PASS | Plan line 164: "Explicit parameters only; no extra_payload" |
| Four-layer boundary `UI → Service → Host → Agent` preserved | PASS | Plan lines 112-123 layering diagram and constraints |

**Boundary finding**: The plan correctly situates the registry/processors at the Fund layer. One area warranting attention: the `create_default()` factory (plan line 362) could inadvertently couple registry construction to concrete processor imports. The "without side effects" constraint is stated but not defined. See Finding 4.

### Best Practice

| Check | Result | Evidence |
|-------|--------|----------|
| Protocol-based dispatch | PASS | `FundProcessorProtocol` with `supports()`/`extract()` |
| Closed sets for dispatch keys and field families | PASS | Literal types for `intermediate_kind`, `field_family_id`, `gap_code` |
| Fail-closed by default | PASS | Lines 142-143: no silent fallback to success; lines 288-293: explicit fail-closed rules |
| Chinese docstrings required | PASS | Line 164: matching AGENTS.md:147-150 |
| Template chapter references required | PASS | Line 164 |
| Explicit parameters, no extra_payload | PASS | Line 164 |

**Best practice finding**: The `FundProcessorResult` dataclass (lines 211-225) has 12 fields. While each is justified by the domain contract (field families, gaps, anchors, provenance, candidate boundary), the implementation worker should verify that the `contract_status` enum doesn't duplicate information already encoded in individual field family statuses. This is a review-time check, not a plan defect.

### Optimal Solution

| Check | Result | Evidence |
|-------|--------|----------|
| Addresses real problem (not parser correctness) | PASS | Plan lines 96-106: first-principles problem statement correctly identifies the gap as field-family extraction contract, not parser full-JSON quality |
| Registry avoids hidden routing | PASS | Plan line 106: current `FundDataExtractor.extract()` already has hidden routing; registry makes it explicit and testable |
| Migration sequence is incremental | PASS | Plan lines 305-308: S1 additive, S2 optional injection, S3 replacement, S4+ candidate processors |
| Existing narrow extractors not discarded | PASS | Plan lines 310-316: mapping from each current extractor to field families |

**Optimal solution finding**: The plan's decision to not wire S1 into `FundDataExtractor.extract()` default behavior is correct, but creates a period where two parallel extraction paths exist (current direct extractor calls vs new registry path). The plan addresses this with the S2/S3 migration sequence, but the S1 "completion signal" (lines 376-379) does not include a cross-path consistency check. This is acceptable for S1 since no production behavior changes, but the S2 planning gate should require output equivalence tests.

### Overengineering

| Check | Result | Evidence |
|-------|--------|----------|
| Registry justified vs direct dispatch | PASS | Plan line 106: hidden routing already exists; six fund types justify typed dispatch |
| Field-family granularity appropriate | PASS WITH NOTE | Six field families mirror template chapters 1-6; plan acknowledges breadth risk at line 445 |
| Gap code enumeration is bounded | PASS | 11 required gap codes for S1; each maps to a specific fail-closed scenario |

**Overengineering finding**: The `FundProcessorResult` includes both `gaps` and per-field-family `gaps` (line 221 vs 241). If every field-family gap is also aggregated at the result level, this is redundant. If result-level gaps are only for cross-cutting gaps (e.g., `fund_type_missing_or_ambiguous`), the schema should enforce this distinction. The plan is ambiguous on this point.

### Overcoupling

| Check | Result | Evidence |
|-------|--------|----------|
| Processor output decoupled from StructuredFundDataBundle | PASS | Plan lines 244-245: "first slice may return FundProcessorResult directly... later migration slice can adapt" |
| Candidate intermediates isolated from production paths | PASS | Plan lines 205-207: candidate inputs allowed only in documents/processors tests or harness |
| Registry decoupled from FundDataExtractor default behavior | PASS | Plan lines 305-306: S1 does not wire into default extract() |
| Source provenance projection decoupled from source policy | PASS | Plan lines 257-259: provenance copied from repository metadata only |

**Overcoupling finding**: None. The plan correctly separates concerns across all coupling boundaries.

---

## Findings

### Finding 1 — MEDIUM — Chapter 4-6 field-family mapping from existing narrow extractors is underspecified

**Plan reference**: Lines 310-316, 448

**Evidence**: The plan maps existing narrow extractors to field families:
- `extract_profile()` → `product_essence.v1` (Ch1)
- `extract_performance()` → `return_attribution.v1` (Ch2)
- `extract_manager_ownership()` → `manager_profile.v1` (Ch3) + parts of `investor_experience.v1` (Ch4)
- `extract_holdings_share_change()` → `current_stage.v1` (Ch5) + holdings-related `manager_profile.v1` + `investor_experience.v1`
- `extract_bond_risk_evidence()` → not mapped to any field family in active-fund first slice

For Chapters 1-3, the mapping is one-to-one. For Chapters 4-6, the mapping is described as "parts of" without specifying which extractor output fields populate which field-family fields. The plan at line 448 acknowledges "Active fund first slice may expose gaps in existing narrow extractors for Chapter 4-6 fields" but does not define the field-level mapping contract that the S1 `ActiveFundAnnualProcessor` would implement.

**Risk**: An implementation worker could fill Chapter 4-6 gaps by reaching into parser internals or inventing heuristics, violating the plan's own fail-closed rule (line 290: "Missing required evidence never becomes a value by heuristic").

**Recommended disposition**: The S1 implementation gate should require the `active_annual.py` processor to include a field-level mapping table (extractor output field → field family → field family field) in its module docstring. Missing mappings must produce `field_family_partial` or `field_family_missing` gaps, not heuristic values.

**Severity**: Medium — does not block plan acceptance but must be dispositioned before or during S1 implementation.

---

### Finding 2 — MEDIUM — `ExtractionMode.not_applicable` has an unresolved forward dependency

**Plan reference**: Lines 238-239, 446

**Evidence**: The plan uses `not_applicable` as a `field_family_result.status` value (line 238) and as a planned `extraction_mode` (line 239), but explicitly defers the decision: "`not_applicable` only if review accepts extending `ExtractionMode`." The current `ExtractionMode` enum (design.md lines 755-758) has only `direct`, `derived`, `estimated`, `missing`. The plan's own field family status already includes `not_applicable` (line 238), creating a forward reference to a decision this review must either accept or reject.

**Risk**: If the review rejects extending `ExtractionMode`, the field family status `not_applicable` would have no corresponding extraction mode, creating an inconsistency. If the review accepts it, the plan's own constraint ("only if review accepts") is satisfied but the plan didn't provide the review with a concrete proposal for the enum extension.

**Recommended disposition**: Accept extending `ExtractionMode` with `not_applicable` for this plan, with the constraint that `not_applicable` can only be used when the field family is categorically inapplicable to the fund type (e.g., `return_attribution.v1` for an index fund where Alpha is not the primary lens). The S1 implementation must add `not_applicable` to the `ExtractionMode` Literal/enum and must not use it as a synonym for `missing`.

**Severity**: Medium — requires a decision before S1 implementation but the plan correctly flags it.

---

### Finding 3 — MEDIUM — S1 README update marked optional but AGENTS.md requires it for `fund_agent/fund/` changes

**Plan reference**: Lines 337-338, 421-425

**Evidence**: The plan says "Optionally update `fund_agent/fund/README.md`" (line 337, emphasis on optionally). AGENTS.md line 206 states: "`fund_agent/fund/` 修改 → 更新 `fund_agent/fund/README.md`". Since S1 adds a new package `fund_agent/fund/processors/` with four new modules, this is unambiguously a `fund_agent/fund/` modification, making the README update mandatory under AGENTS.md.

**Risk**: If treated as optional, the Fund package README would be out of sync with the new Processor/Extractor boundary, violating the AGENTS.md documentation discipline.

**Recommended disposition**: Change "Optionally" to "Required" for `fund_agent/fund/README.md` update in the S1 allowed files list. The README update scope should document the Processor/Extractor boundary as current implemented contract per plan lines 422-423, while preserving Docling/candidate non-proof boundary.

**Severity**: Medium — the plan is internally inconsistent with AGENTS.md documentation rules.

---

### Finding 4 — LOW — `create_default()` "without side effects" constraint is ambiguous

**Plan reference**: Line 362

**Evidence**: `FundProcessorRegistry.create_default()` is gated by "only if it registers processors without side effects." It's unclear whether importing `active_annual.py` (which imports narrow extractors) counts as a side effect. Module-level imports in Python are side-effecting in the sense that they execute the imported module's top-level code, but narrow extractors should be pure functions with no I/O at import time.

**Risk**: Low. The ambiguity could lead to implementation worker uncertainty about whether `create_default()` is allowed in S1. Mitigation: the plan already correctly states that S1 is additive and no-live, so the worst case is a module import that should be safe.

**Recommended disposition**: Clarify in S1 implementation that "without side effects" means "does not call repository, PDF cache, source helpers, Docling, network, provider, or filesystem." Module-level imports of pure extractor functions are not side effects in this sense.

**Severity**: Low — ambiguity is resolvable with a one-sentence clarification.

---

### Finding 5 — LOW — Synthetic fixture structure not specified

**Plan reference**: Lines 400-401

**Evidence**: The test matrix requires "synthetic `ParsedAnnualReport` with sections/tables" as fixtures. Current extractor tests (e.g., `tests/fund/test_data_extractor.py:31-75`) use a fake repository. The plan doesn't specify the minimum fixture structure needed to exercise all six field families through the processor. A `ParsedAnnualReport` with insufficient sections/tables could produce all-missing results that pass the "produces field families" assertion but don't actually validate the mapping logic.

**Risk**: Low. The existing extractor test fixtures already demonstrate realistic `ParsedAnnualReport` construction. The S1 worker can follow the same pattern.

**Recommended disposition**: S1 implementation should add at least one fixture that exercises the "happy path" where all six field families return non-missing results (using synthetic data that triggers each narrow extractor's success path).

**Severity**: Low — existing test patterns provide adequate precedent.

---

### Finding 6 — LOW — Result-level gaps vs per-field-family gaps relationship unspecified

**Plan reference**: Lines 221, 241

**Evidence**: `FundProcessorResult` has `gaps: tuple[FundExtractionGap, ...]` at line 221, and `FundFieldFamilyResult` also has `gaps: tuple[FundExtractionGap, ...]` at line 241. The plan doesn't specify whether result-level gaps are a superset, subset, or cross-cutting-only subset of field-family gaps. If every field-family gap is duplicated at the result level, the schema has redundant data. If result-level gaps are only for cross-cutting gaps (e.g., `fund_type_missing_or_ambiguous`, `unsupported_report_type`), the schema should enforce this.

**Risk**: Low. Redundant data in a dataclass is a maintainability concern, not a correctness concern.

**Recommended disposition**: The S1 implementation should either (a) make result-level gaps contain only cross-cutting gaps not attributable to a single field family, or (b) document that result-level gaps are the concatenation of all field-family gaps for convenience. Option (a) is preferred.

**Severity**: Low — schema design preference, not a blocking defect.

---

### Finding 7 — INFO — Cross-cutting consistency validated

Verified: the plan's claims about existing code match the actual code:

| Plan claim | Code evidence | Match? |
|-----------|---------------|--------|
| `FundDocumentRepository.load_annual_report()` returns `ParsedAnnualReport` without exposing PDF paths | `repository.py:318-324` | YES |
| `FundDataExtractor.extract()` loads report through repository, calls narrow extractors directly | `data_extractor.py:291-304` | YES |
| `FundDataExtractor` degrades only NAV failures, not repository failures | `data_extractor.py:291-295` (repository call outside try/except) vs `data_extractor.py:405-431` (NAV degradation) | YES |
| `EvidenceAnchor` has `source_kind`, `document_year`, `section_id`, `page_number`, `table_id`, `row_locator`, `note` | `extractors/models.py:88-107` | YES |
| `bond_risk_evidence.py` consumes `ParsedAnnualReport`, does not access repository/PDF/cache | `bond_risk_evidence.py:1-5` | YES |
| Candidate `representation_models.py` is non-exported, internal to Fund documents | `representation_models.py:1-6` | YES |
| `CandidateRepresentationStatus` forces `not_proven` / `not_authorized` | `representation_models.py:103-112` post_init validation | YES |
| `evidence_anchor_mapping.py` does not import production `EvidenceAnchor` | `evidence_anchor_mapping.py:1-7` | YES |
| No-consumption guard tests forbid candidate imports from Service/UI/Host | `test_docling_no_consumption_guards.py:8-22` | YES |
| `processors/` directory does not exist (planning-only, no premature implementation) | `ls fund_agent/fund/processors/` → `DIRECTORY_NOT_FOUND` | YES |

No code-evidence contradictions found.

---

## Residual Risk Summary

| Risk | Severity | Owner | Mitigation |
|------|----------|-------|------------|
| Ch4-6 field-family mapping underspecified (F1) | Medium | S1 implementation worker | Require field-level mapping table in `active_annual.py` docstring; missing → `field_family_partial` gap |
| `ExtractionMode.not_applicable` unresolved (F2) | Medium | This review | Accept extension with constraint: only for categorically inapplicable field families, not as synonym for `missing` |
| README update optional vs mandatory (F3) | Medium | Plan author / S1 worker | Change "Optionally" to "Required" for `fund_agent/fund/README.md` |
| `create_default()` side-effect ambiguity (F4) | Low | S1 implementation worker | Clarify: module imports of pure functions ≠ side effects in this context |
| Synthetic fixture structure (F5) | Low | S1 implementation worker | Follow existing extractor test patterns; add happy-path fixture covering all six families |
| Result vs field-family gap duplication (F6) | Low | S1 implementation worker | Prefer cross-cutting-only at result level |
| Plan's own residual risks (lines 443-451) | Varies | Future gates | Already acknowledged; follow-up gates listed at lines 453-459 |

---

## Blocking Open Questions

None. No finding blocks this plan from proceeding to S1 implementation gate. The three medium findings must be dispositioned before or during S1 implementation, but none requires plan rework.

---

## Completion Report

```text
Verdict token: PLANREVIEW_PASS_WITH_RISKS
Artifact path: docs/reviews/fund-processor-extractor-architecture-planreview-ds-20260618.md
Blocking open questions: none
Residual risks: Ch4-6 field-family mapping specificity (F1), ExtractionMode.not_applicable forward dependency (F2), README update optional/mandatory inconsistency (F3), create_default() side-effect ambiguity (F4), synthetic fixture structure (F5), result-level gap duplication (F6)
Findings by severity: MEDIUM=3, LOW=3, INFO=1
```
