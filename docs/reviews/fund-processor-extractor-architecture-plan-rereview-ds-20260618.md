# Fund Processor/Extractor Architecture Plan Re-Review — AgentDS

> **Gate**: Fund Processor/Extractor Architecture Planning Gate (heavy, docs/planning only)
> **Reviewer**: AgentDS (re-review)
> **Date**: 2026-06-18
> **Review type**: adversarial plan re-review; verify prior-review finding dispositions; no implementation, no fix, no commit, no push, no PR
> **Plan under review**: `docs/reviews/fund-processor-extractor-architecture-plan-20260617.md` (revised)
> **Prior review**: `docs/reviews/fund-processor-extractor-architecture-planreview-ds-20260618.md` (F1-F6)

---

## Verdict

**PLAN_REREVIEW_PASS_NOT_READY**

All six findings (F1-F6) from the prior AgentDS plan review are properly reflected and dispositioned in the revised plan. No new blockers were introduced by the fixes. The plan is code-generation-ready for S1 implementation gate. Zero blocking open questions.

---

## Disposition Verification Matrix

### F1 — MEDIUM — Chapter 4-6 field-family mapping underspecified → FIXED

| Aspect | Prior review concern | Current plan resolution | Verdict |
|--------|---------------------|------------------------|---------|
| Field-level mapping | Missing; "parts of" was insufficient | New § "S1 field-level mapping requirement" (lines 325-330): mandatory module-level mapping table in `active_annual.py` docstring, listing every extractor output field/path → field_family_id, field-family field name, chapter ID, extraction mode, required/optional, fallback gap code | Resolved |
| Gap behavior | Risk of heuristic fill for unmapped fields | Line 330: unmapped/absent fields must produce `field_family_partial` or `field_family_missing`; no parser internals, candidates, heuristics | Resolved |
| Implementation contract | Not specified | Line 381: `active_annual.py` must include the mapping table and gap behavior | Resolved |
| Test verification | Not specified | Line 399: completion signal requires one happy-path fixture exercising all six families through the mapping table; line 417: dedicated "happy path" test row; line 419: "Contract: field mapping gaps" test row | Resolved |
| Disposition table | N/A | Line 459: explicitly "Accepted and fixed in this plan" with owner = S1 implementation worker | Resolved |
| Residual risk | Not updated | Line 478: residual risk now references the documented field-level mapping table constraint | Resolved |

**Conclusion**: F1 is fully resolved. The field-level mapping requirement is concrete enough to constrain the S1 implementation worker without over-specifying the exact field paths (which are discoverable from existing extractor code).

### F2 — MEDIUM — `ExtractionMode.not_applicable` forward dependency → FIXED

| Aspect | Prior review concern | Current plan resolution | Verdict |
|--------|---------------------|------------------------|---------|
| Decision status | Deferred: "only if review accepts" | Line 239: now "accepted planned mode `not_applicable`" — decision made | Resolved |
| Binding constraint | Not specified | New § "`ExtractionMode.not_applicable` rule" (lines 246-250): S1 may extend `ExtractionMode`; only for categorically inapplicable field families; never as synonym for missing/unsupported/ambiguous/weakness | Resolved |
| Disposition table | N/A | Line 460-461: explicitly "Accepted and fixed" with constraint summary | Resolved |
| Residual risk | Outdated | Line 475: updated to note extension accepted under categorical-inapplicability constraint, misuse risk remains review concern | Resolved |

**Conclusion**: F2 is fully resolved. The categorical-inapplicability constraint is well-bounded and prevents the most likely misuse (treating `not_applicable` as `missing`).

### F3 — MEDIUM — S1 README update optional vs mandatory → FIXED

| Aspect | Prior review concern | Current plan resolution | Verdict |
|--------|---------------------|------------------------|---------|
| Status | "Optionally update" (violating AGENTS.md:206) | Line 351: "Required update `fund_agent/fund/README.md`" | Resolved |
| Scope | Not specified | Line 351: document Processor/Extractor boundary and preserve Docling/candidate non-proof boundaries | Resolved |
| Disposition table | N/A | Line 462: explicitly "Accepted and fixed" | Resolved |

**Conclusion**: F3 is fully resolved. The plan now correctly follows AGENTS.md documentation discipline.

### F4 — LOW — `create_default()` side-effect ambiguity → FIXED

| Aspect | Prior review concern | Current plan resolution | Verdict |
|--------|---------------------|------------------------|---------|
| Definition | "without side effects" was ambiguous | New § "`create_default()` side-effect definition" (lines 384-387): explicit forbidden list (repository, PDF cache, source helper, Docling, network, provider/LLM, analyze/checklist/golden/readiness/release, filesystem); pure imports allowed | Resolved |
| Disposition table | N/A | Line 463: explicitly "Accepted and fixed" | Resolved |

**Conclusion**: F4 is fully resolved. The forbidden side-effect list is exhaustive and actionable for the S1 worker.

### F5 — LOW — Synthetic fixture structure not specified → FIXED

| Aspect | Prior review concern | Current plan resolution | Verdict |
|--------|---------------------|------------------------|---------|
| Happy-path fixture | Missing | Line 399: completion signal requires one happy-path fixture covering all six field families; line 417: dedicated test row in matrix; line 423: fixture strategy updated | Resolved |
| Disposition table | N/A | Line 464: explicitly "Accepted and fixed" | Resolved |

**Conclusion**: F5 is fully resolved. The happy-path fixture requirement ensures the mapping table is actually exercised, not just syntactically present.

### F6 — LOW — Result-level gaps vs per-field-family gaps → FIXED

| Aspect | Prior review concern | Current plan resolution | Verdict |
|--------|---------------------|------------------------|---------|
| Relationship | Unspecified; risk of duplication | Line 221: `FundProcessorResult.gaps` now annotated "for cross-cutting gaps only"; line 300: explicit fail-closed rule that field-family-local gaps stay local, result-level reserved for cross-cutting; line 419: dedicated test row verifying the separation | Resolved |
| Disposition table | N/A | Line 465: explicitly "Accepted and fixed" | Resolved |

**Conclusion**: F6 is fully resolved. The cross-cutting-only constraint prevents gap duplication and forces discipline in gap attribution.

---

## New Issues Introduced by Fixes?

| Check | Result |
|-------|--------|
| Does the field-level mapping table requirement (lines 325-330) introduce over-specification? | No — it requires the mapping to exist and be documented, but does not prescribe exact field paths, which should be discovered from existing extractor code. |
| Does the `not_applicable` categorical constraint (lines 246-250) conflict with any field family? | No — every field family has a clear fund-type applicability scope (e.g., `return_attribution.v1` for index funds where Alpha is not the primary lens). |
| Does `create_default()` being allowed open a path to premature production wiring? | No — the plan still says S1 does not wire into `FundDataExtractor.extract()` default behavior (line 312). |
| Does the required README update risk leaking implementation details into public docs? | No — line 351 specifically scopes it to documenting Processor/Extractor boundary while preserving candidate non-proof boundary. |
| Do any of the fixes weaken the NOT_READY boundary? | No — the plan's stop condition (lines 490-492), forbidden commands (lines 436-442), and verdict (lines 11-13) all remain unchanged. |

No new issues found.

---

## Architecture Boundary Re-Verification

All prior-review boundary checks remain valid. Key verifications that the fixes did not weaken:

| Check | Prior status | Post-fix status |
|-------|-------------|-----------------|
| Processor owned by Agent-layer `fund_agent/fund` | PASS | PASS (unchanged) |
| `extract()` does not call repository | PASS | PASS (unchanged, line 163) |
| No production parser replacement | PASS | PASS (unchanged, line 356-361) |
| No Service/UI/Host direct parser consumption | PASS | PASS (unchanged) |
| EID single-source policy preserved | PASS | PASS (unchanged) |
| Result-level gaps are cross-cutting-only | FAIL (ambiguous) | PASS (line 221, 300) |
| Field mapping contract specifies gap behavior | FAIL (underspecified) | PASS (lines 325-330) |
| README sync follows AGENTS.md discipline | FAIL (optional) | PASS (line 351) |

---

## Residual Risks

| Risk | Severity | Owner | Notes |
|------|----------|-------|-------|
| Field-family contracts may still be too broad for one slice | Low | S1 worker | Mitigated: no downstream integration authorized; missing/partial gaps acceptable |
| `not_applicable` misuse as `missing` | Low | S1 code reviewer | Mitigated: explicit categorical-only constraint in plan (lines 246-250); reviewer should check |
| `EvidenceAnchor.source_kind` candidate extension deferred | Low | Future schema gate | Already deferred in plan (line 256) |
| Cross-path consistency (registry vs direct extractor) | Low | S2 planning gate | S1 not affected; S2 should require equivalence tests |
| Field-level mapping table staleness over time | Low | Future maintenance | Mapping is test-verified (line 419); stale mappings produce test failures |

---

## Blocking Open Questions

None.

---

## Completion Report

```text
Verdict token: PLAN_REREVIEW_PASS_NOT_READY
Artifact path: docs/reviews/fund-processor-extractor-architecture-plan-rereview-ds-20260618.md
Blocking open questions: none
Residual risks: all prior-review F1-F6 residuals closed; remaining risks are catalogued above and tracked to S1/S2/future gates
Findings: F1-F6 all resolved in plan revision; zero new findings
```
