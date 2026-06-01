# Re-Review: Source Provenance Primary Failure Category Propagation Design Plan

> Reviewer: AgentMiMo
> Date: 2026-05-27
> Timestamp: 20260527-063122
> Reviewed target: `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-20260527.md` (revised)
> Prior review: `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-review-mimo-20260527.md`
> GLM prior review: `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-review-glm-20260527.md`
> Scope: targeted re-review — verify revisions close MiMo low notes and GLM F1/F2/F3; check no new material risk introduced

---

## MiMo Prior Low Notes Closure

| # | Note | Revised plan location | Status |
|---|---|---|---|
| 1 | `to_dict()` manual field enumeration needs explicit new field | §Minimal Data Model Extension: "Add the field to `to_dict()` with exact key `"primary_failure_category"`" (line 168); §Implementation Files `models.py`: "`to_dict()` key `"primary_failure_category"`" (line 201) | **CLOSED** — explicit key specification eliminates ambiguity |
| 2 | Category deserialization normalization strategy needs clarity | §Minimal Data Model Extension: "Validate/normalize through `_normalize_failure_category()` following the existing `_normalize_source_name()` pattern" (line 169); §Implementation Files: "`_normalize_failure_category()` following `_normalize_source_name()` style" (line 201) | **CLOSED** — named helper function, explicit pattern reference |
| 3 | `_mark_fallback_used` signature not explicitly stated | §Minimal Source-Chain Write: exact signature block with full type annotation (lines 177-183) | **CLOSED** — no ambiguity remains |

---

## GLM Prior Findings Closure

| Finding | Severity | Revised plan location | Status |
|---|---|---|---|
| F1: Literal type import path not converged — circular import risk | 中 | §Minimal Data Model Extension: "Move `AnnualReportSourceFailureCategory` from `fund_agent/fund/documents/sources.py` to `fund_agent/fund/documents/models.py`, next to `AnnualReportSourceName`. `sources.py` must import the type from `models.py`; `models.py` must not import from `sources.py`. Do not create a local duplicate alias in either module." (line 167); §Implementation Files `models.py`: "Move/own `AnnualReportSourceFailureCategory` here next to `AnnualReportSourceName`" (line 199); "`models.py` must remain independent of source orchestration classes and exceptions" (line 202); `sources.py`: "Import `AnnualReportSourceFailureCategory` from `fund_agent.fund.documents.models`. Remove the local alias." (lines 204-205); import-safety verification test added (lines 230-232) | **CLOSED** — explicit direction (move up, not alias), dependency direction enforced, import-safety test added |
| F2: Projection precedence rule incomplete — metadata=None + kwarg exists | 中 | §Projection: exact precedence pseudocode (lines 98-104); 5-row truth table covering all `(metadata_value, kwarg_value)` combinations (lines 112-118); §Tests `test_source_provenance.py`: "Metadata-owned category wins over kwarg: metadata `schema_drift` plus kwarg `not_found` stays `fail_closed`" and "Kwarg fallback still works when metadata category is `None`: metadata fallback row with kwarg `unavailable` classifies `eligible`" (lines 239-240) | **CLOSED** — precedence is deterministic, truth table is complete, new tests cover both metadata-wins and kwarg-fallback paths |
| F3: Plan references `AnnualReportSourceChain` but actual class is `AnnualReportSourceOrchestrator` | 低 | All references changed to `AnnualReportSourceOrchestrator`: §Current Code Facts (line 50), §Bundle And Public Outputs (line 137), §Minimal Source-Chain Write (line 186), §Implementation Files `sources.py` (line 207), §Stop Conditions (line 319), §Tests (lines 222-224) | **CLOSED** — all occurrences corrected |

---

## New Material Risk Check

| Revision | Risk introduced? | Analysis |
|---|---|---|
| Type move from `sources.py` to `models.py` | No | Natural dependency direction (`sources` imports from `models`). `models.py` already exports `AnnualReportSourceName` in the same pattern. No circular import because `models.py` does not import from `sources.py`. |
| Exact precedence pseudocode | No | `effective_category` is computed once and fed into existing classification logic. No change to classification rules themselves. |
| 5-row truth table | No | All rows are consistent with the pseudocode and the existing classification rules. No contradictory entries. |
| New tests for precedence | No | Tests verify both metadata-wins and kwarg-fallback paths. These are additive assertions, not replacements. |
| Import-safety verification test | No | Verifies existing invariant (`models.py` independent of `sources.py`). Does not change behavior. |

No new material risk introduced by revisions.

---

## Findings

No findings. All prior MiMo low notes and GLM findings are closed with explicit, evidence-backed revisions. No new material risk identified.

---

## Open Questions

None.

---

## Residual Risks

Same as prior review — no change:

| Risk | Severity | Tracking destination |
|---|---|---|
| Cache schema version bump decision left to maintainers | Low | Implementation gate controller judgment |
| Multi-source chains beyond primary + fallback are out of scope | Low | Future provenance-chain schema gate |

---

## Conclusion

**Verdict: PASS**

All three MiMo low notes are closed: `to_dict()` key is explicit, `_normalize_failure_category()` is named with pattern reference, `_mark_fallback_used` signature is exact. All three GLM findings are closed: type ownership moved to `models.py` with no circular import, projection precedence has deterministic pseudocode and 5-row truth table with covering tests, class name corrected to `AnnualReportSourceOrchestrator`. No new material risk introduced. Plan is code-generation-ready.

---

Artifact path: `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-rereview-mimo-20260527.md`
