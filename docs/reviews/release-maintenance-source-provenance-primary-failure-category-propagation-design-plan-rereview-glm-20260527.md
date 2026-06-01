# Plan Re-Review: Source Provenance Primary-Failure-Category Propagation Design

> **Reviewer**: AgentGLM
> **Date**: 2026-05-27T06:31:07
> **Reviewed artifact**: `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-20260527.md` (revised)
> **Prior GLM review**: `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-review-glm-20260527.md`
> **MiMo review**: `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-review-mimo-20260527.md`
> **Verdict**: `pass`

---

## Targeted Re-Review Scope

Verify that prior GLM F1/F2/F3 and MiMo's three low notes are fully closed in the revised plan, and that no new material risk was introduced.

---

## Finding Disposition

### F1-已修复-Literal 类型引入路径：循环依赖消除

| Aspect | Prior finding | Revised plan |
|---|---|---|
| Location | "Implementation Files / models.py" + "Minimal Data Model Extension" | Lines 49, 166–167, 199–202, 204–205, 230–232 |
| Problem | Plan left "or" between import-from-sources and local alias, creating circular dependency risk or type drift | Plan now commits to single path |
| Resolution evidence | — | Line 167: "Move `AnnualReportSourceFailureCategory` from `sources.py` to `models.py`, next to `AnnualReportSourceName`. `sources.py` must import the type from `models.py`; `models.py` must not import from `sources.py`. Do not create a local duplicate alias in either module." |
| Import-safety test | — | Lines 230–232: "A focused test or lint-level import check should import `AnnualReportSourceMetadata`, `AnnualReportSourceName`, and `AnnualReportSourceFailureCategory` from `fund_agent.fund.documents.models` without importing `fund_agent.fund.documents.sources`." |
| Code fact consistency | `sources.py:21` imports from `models.py`; natural dependency direction is `sources → models` | Moving type to `models.py` preserves this direction; `models.py` never imports `sources.py` |

**Status: CLOSED.** Single import path, no alias, no circular dependency, import-safety test specified.

### F2-已修复-投影优先级规则：完整的 truth table 和伪代码

| Aspect | Prior finding | Revised plan |
|---|---|---|
| Location | "Projection / Compatibility behavior" | Lines 96–118, 210, 239–240 |
| Problem | "metadata authoritative" vs "keep kwarg as test override" conflict when metadata is None | Plan now specifies exact precedence |
| Resolution evidence | — | Lines 98–104: explicit pseudocode `effective_category = (source_metadata.primary_failure_category if source_metadata is not None and source_metadata.primary_failure_category is not None else primary_failure_category)` |
| Truth table | — | Lines 110–118: 5-row truth table covering all `(metadata, kwarg)` combinations with expected `effective_category` and required test |
| Precedence rule | Ambiguous | Line 106: "Metadata non-`None` category wins over the keyword argument. Metadata `None` category falls back to the keyword argument only for test/development override compatibility." |
| Targeted tests | — | Lines 239–240: "Metadata-owned category wins over kwarg: metadata `schema_drift` plus kwarg `not_found` stays `fail_closed`." + "Kwarg fallback still works when metadata category is `None`: metadata fallback row with kwarg `unavailable` classifies `eligible`." |

**Status: CLOSED.** Precedence is unambiguous, pseudocode is code-generation-ready, truth table covers all cases, two targeted tests for conflict scenarios.

### F3-已修复-类名修正

| Aspect | Prior finding | Revised plan |
|---|---|---|
| Location | "Current Code Facts" + "Implementation Files" | Lines 50, 137, 186, 207, 222–223, 319 |
| Problem | Referenced `AnnualReportSourceChain` instead of `AnnualReportSourceOrchestrator` | All occurrences corrected |
| Resolution evidence | — | Line 50: "AnnualReportSourceOrchestrator.fetch_annual_report_pdf()"; Line 137: "AnnualReportSourceOrchestrator"; Lines 222–223: test descriptions use correct name |

**Status: CLOSED.** All references now use `AnnualReportSourceOrchestrator`.

### MiMo Low Note 1-已修复-to_dict() 显式 key 指导

| Aspect | MiMo note | Revised plan |
|---|---|---|
| Location | `to_dict()` manual enumeration may miss new field | Lines 168, 201, 227 |
| Resolution | — | Line 168: "Add the field to `to_dict()` with exact key `"primary_failure_category"`"; Line 227: test asserts "`to_dict()` includes the exact `"primary_failure_category"` key." |

**Status: CLOSED.**

### MiMo Low Note 2-已修复-反序列化 normalize 模式指定

| Aspect | MiMo note | Revised plan |
|---|---|---|
| Location | "normalize to None" strategy unspecified | Line 169 |
| Resolution | — | "Validate/normalize through `_normalize_failure_category()` following the existing `_normalize_source_name()` pattern so only the five accepted categories survive deserialization." |

**Status: CLOSED.**

### MiMo Low Note 3-已修复-_mark_fallback_used 签名明确

| Aspect | MiMo note | Revised plan |
|---|---|---|
| Location | "or equivalent" was ambiguous | Lines 175–185 |
| Resolution | — | Exact signature: `_mark_fallback_used(result: AnnualReportSourceResult, *, primary_failure_category: AnnualReportSourceFailureCategory | None = None) -> AnnualReportSourceResult` |

**Status: CLOSED.**

---

## New Risk Scan

Examined all changes between original and revised plan for new material risk:

| New content | Risk assessment |
|---|---|
| Type move from `sources.py` to `models.py` (lines 49, 166–167) | Safe: natural dependency direction preserved. Verified `sources.py:21` already imports from `models.py`. |
| Truth table (lines 110–118) | Safe: purely clarifying, no behavioral change. |
| Import-safety test (lines 230–232) | Safe: adds verification, no behavioral change. |
| Exact `_mark_fallback_used` signature (lines 175–185) | Safe: commits to one approach, removes ambiguity. |
| `effective_category` pseudocode (lines 98–104, 210) | Safe: implementation agent gets exact code to write. |

**No new material risk introduced.**

---

## Special Lenses Re-Check

All five lenses applied to the revised plan; no new issues found:

- **Architecture boundary**: Type move aligns with natural `sources → models` dependency. No layer violation.
- **Best practice**: Truth table + pseudocode is the correct level of specification for a code-generation-ready plan.
- **Optimal solution**: Still the minimal path. No overengineering added.
- **Overengineering**: No new abstractions, wrappers, or generalizations.
- **Overcoupling**: `effective_category` computation is local to the projection function. No cross-layer coupling introduced.

---

## Conclusion

**Verdict: `pass`**

All three GLM findings (F1 circular dependency, F2 precedence ambiguity, F3 class name) are fully closed with specific plan text, pseudocode, truth table, and targeted tests. MiMo's three low notes are all addressed. No new material risk was introduced by the revisions. The plan is code-generation-ready.
