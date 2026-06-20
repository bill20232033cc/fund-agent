# Targeted Re-Review: docs/design.md Header Stale Finding

> **Gate**: re-review (targeted)
> **Work unit**: FDD return_attribution source-truth slice 4
> **Reviewer**: AgentMiMo
> **Date**: 2026-06-20
> **Scope**: Only re-verify DS Finding 3 (docs/design.md stale header) fix; not a full re-review

---

## 1. Finding Under Review

**Source**: DS review artifact `docs/reviews/code-review-20260620-ds-return-attribution-source-truth-slice4.md`, Finding 3 (Docs Sync, "stale header" subsection)

**Original issue**: `docs/design.md` lines 6 and 8 still claimed only `product_essence.v1` has FDD source-truth direct extraction, contradicting body lines 674, 678, and 1150 which correctly state both `product_essence.v1` and `return_attribution.v1` are implemented.

**Severity**: Low (overly conservative, not factually wrong in dangerous direction)

---

## 2. Fix Verification

### 2.1 Line 6 (状态补充) — 已修复

**Before (DS review reported)**: "当前仅 `product_essence.v1` 有 FDD source-truth direct extraction"

**After (current file)**: "当前 `product_essence.v1` 与 `return_attribution.v1` 有 FDD source-truth direct extraction；`manager_profile.v1`、`investor_experience.v1`、`current_stage.v1` 和 `core_risk.v1` 的 FDD source-truth extraction 仍未实现。"

**Verdict**: ✅ 已修复。Header now matches body.

### 2.2 Line 8 (变更摘要) — 已修复

**Before (DS review reported)**: "只有 `product_essence.v1` 在 proof-positive FDD 输入下实现 direct source-truth extraction"

**After (current file)**: "`product_essence.v1` 与 `return_attribution.v1` 在 proof-positive FDD 输入下实现 direct source-truth extraction，且 candidate evidence 继续保持 candidate_only / not_proven / NOT_READY。该修订不声明其它四个字段族..."

**Verdict**: ✅ 已修复。Header now matches body.

### 2.3 Cross-check with body lines

| Location | Mentions both families | Consistent |
|----------|----------------------|------------|
| Line 6 (状态补充) | ✅ `product_essence.v1` 与 `return_attribution.v1` | ✅ |
| Line 8 (变更摘要) | ✅ `product_essence.v1` 与 `return_attribution.v1` | ✅ |
| Line 674 (Processor/Extractor) | ✅ "当前 `product_essence.v1` 与 `return_attribution.v1` 已实现 FDD source-truth direct extraction" | ✅ |
| Line 678 (S1/S2 gate summary) | ✅ "proof-positive FDD input 的 `product_essence.v1` 与 `return_attribution.v1` 推进到 direct public field extraction" | ✅ |
| Line 1150 (comparison table) | ✅ "proof-positive `product_essence.v1` 与 `return_attribution.v1` 可 direct extraction" | ✅ |

All five locations are now consistent.

---

## 3. New Blocker Check

**Scope of change**: Only `docs/design.md` header lines 6 and 8 wording updated.

**Assessment**:
- No code changed
- No contract/schema/public interface changed
- No new claims introduced beyond what body already states
- Four missing families (`manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, `core_risk.v1`) still correctly stated as not implemented
- Candidate evidence boundary language preserved
- No overclaim introduced

**New blockers**: None.

---

## 4. Finding Disposition

| Finding | Original Status | Fix Applied | Re-review Status |
|---------|----------------|-------------|-----------------|
| DS Finding 3: docs/design.md header stale (lines 6, 8) | 未修复 | ✅ Lines 6 and 8 updated to include `return_attribution.v1` | **已修复** |

---

## 5. Residual Risks

None from this targeted fix. The change is purely documentary alignment — header now matches body, no new scope or claims added.

---

## 6. Verdict

**TARGETED_REREVIEW_PASS_NOT_READY**

Rationale: The specific DS stale-header finding is fully resolved. Both header lines now correctly reflect the current state. No new blockers introduced. However, this re-review only covers the targeted finding; the overall slice 4 code review gate still carries other findings from the original DS and MiMo reviews that require separate resolution before the full review gate can pass.

---

*Artifact path: `docs/reviews/code-review-20260620-mimo-return-attribution-source-truth-slice4-rereview.md`*
