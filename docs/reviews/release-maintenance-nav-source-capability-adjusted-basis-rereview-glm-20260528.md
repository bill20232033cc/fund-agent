# NAV Source Capability / Adjusted Basis Re-Review - GLM

Date: 2026-05-28

Reviewer: GLM (same reviewer as source review)

Role: re-review worker, not controller

Gate: `NAV source capability / adjusted basis evidence gate`

Source review: `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-plan-review-glm-20260528.md`

Fix evidence: `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-fix-evidence-20260528.md`

Re-reviewed targets:

- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-plan-20260528.md` (updated)
- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-evidence-20260528.md` (updated)

Conclusion: **PASS**

## Worker Self-Check - Start

- Status: pass.
- Current role is re-review worker only. I did not start `$gateflow` / `/gateflow`, did not restart from plan, and did not enter implementation.
- Source of truth: source GLM review, fix evidence artifact, and updated plan/evidence artifacts. No production code, tests, or runtime artifacts need re-reading for this scope-limited re-review.
- Scope boundary: write one re-review artifact only. No production code, tests, score, quality gate, schema, golden fixture, release / PR state, or blocker removal.
- Re-review scope: only GLM-F1 and GLM-F2 fix status, plus check for new blockers introduced by the fix.

## GLM-F1: Evidence SQLite 直接读取边界合规

**Status: 已修复**

Original finding 要求 evidence artifact 显式标记 SQLite 只读调查为 investigation-only，并要求 plan 明确生产代码不得复制此模式。

Verification against updated artifacts:

| Fix requirement | Evidence in updated artifacts | Verified |
|---|---|---|
| Evidence 标记 SQLite 调查为 investigation-only | Evidence artifact line 17: "NAV SQLite inspection was read-only, diagnostic-only, and non-authoritative for public adapter capability; future production code and implementation gates must not copy direct cache reads as a boundary bypass." | Yes |
| Evidence 章节标题显式限定用途 | Section renamed from "NAV SQLite Read-Only Metadata" to "NAV SQLite Read-Only Metadata - Diagnostic Non-Boundary Evidence" | Yes |
| Evidence 解读节声明非生产路径 | Evidence line 245-248: "This section is diagnostic-only and non-authoritative for public adapter capability. It is not a production-acceptable access path and must not be used by future implementation, score, quality gate, baseline, or blocker-removal decisions." | Yes |
| Plan 标记 SQLite 为 diagnostic-only | Plan line 104: "Diagnostic-only read-only SQLite inspection"; Plan line 111: "must not be copied into production code or future implementation paths as a way to bypass the Fund-layer adapter contract." | Yes |
| Plan Gate 1 要求公共接口修复而非直接读缓存 | Plan line 177: "Public adapter cache-hit metadata repair for the current `_load_cached_sync()` gap, so origin source and retrieval timestamp are exposed through the typed adapter result rather than direct SQLite reads." | Yes |
| Evidence capability decision 表排除 diagnostic 证据 | Evidence line 255: "Diagnostic SQLite inspection is not public adapter capability evidence." | Yes |

Assessment: The fix goes beyond the minimum requested by explicitly (a) renaming the section header, (b) adding non-authoritative disclaimers in both the self-check and the interpretation, (c) excluding diagnostic evidence from the capability decision table, and (d) adding a Gate 1 requirement to fix the underlying adapter metadata gap through public interface rather than direct cache access. This is a thorough and correct fix.

## GLM-F2: Future fields 缺少 `dividend_adjustment_status`

**Status: 已修复**

Original finding 要求 future gate 入口条件补充 `dividend_adjustment_status` 字段决策点，明确是被 `adjustment_basis` 吸收还是需要独立字段。

Verification against updated artifacts:

| Fix requirement | Evidence in updated artifacts | Verified |
|---|---|---|
| Plan "Provenance And Anchor Fields To Require" 补充 `dividend_adjustment_status` | Plan line 143: `dividend_adjustment_status`: explicit decision point for the future gate. The gate may either absorb this into `adjustment_basis` with documented semantics, or expose it as an independent field if dividend reinvestment / adjustment method needs separate representation. | Yes |
| Plan Gate 1 记录该决策点 | Plan line 179: "Explicit `dividend_adjustment_status` decision: document whether dividend adjustment is fully represented by `adjustment_basis` or requires an independent field." | Yes |
| Plan Gate 1 测试覆盖包含该字段 | Plan line 180: "dividend adjustment representation" listed as test coverage point. | Yes |

Assessment: The fix correctly adds `dividend_adjustment_status` as an explicit decision point in the future fields list, records it as a Gate 1 required decision, and includes it in the Gate 1 test coverage. The fix preserves the correct posture that the decision (absorb vs independent) is deferred to the future gate, not pre-decided here.

## New Blockers Check

Changes in the updated artifacts are limited to:

1. Wording refinements in the evidence artifact (section rename, diagnostic disclaimers, capability decision table exclusions).
2. Addition of `dividend_adjustment_status` to plan future fields and Gate 1 scope.
3. Addition of public adapter cache-hit metadata repair to Gate 1 scope.

None of these changes:

- Change the plan conclusion (`blocked_pending_source_adapter` preserved).
- Remove or weaken the `drawdown_stress` blocker.
- Change `bond_risk_evidence` satisfaction, score semantics, quality gate semantics, snapshot schema, golden fixtures, or baseline status.
- Authorize implementation, schema changes, or blocker removal.
- Introduce new public contract, schema, or dependency changes.
- Change FQ0-FQ6, renderer, Service/CLI, Host/Agent/dayu, or release/PR state.

**No new blockers introduced.**

## Finding Status Mapping

| Finding | Severity | Status | Notes |
|---|---|---|---|
| GLM-F1: evidence SQLite 直接读取边界合规 | 低 | 已修复 | Evidence and plan both explicitly mark SQLite inspection as diagnostic-only/non-authoritative; Gate 1 requires public interface fix. |
| GLM-F2: future fields 缺少 `dividend_adjustment_status` | 低 | 已修复 | Plan adds explicit decision point in future fields and Gate 1 scope. |
| GLM-F3: failure classification 对齐 | 信息 | 证据有效 | No change; classification alignment confirmed in source review. |
| GLM-F4: gate slicing 一致性 | 信息 | 证据有效 | No change; Gate 1 scope now correctly includes metadata repair and dividend decision point without expanding beyond source capability. |

## Final Conclusion

**PASS**

Both GLM findings are fully addressed. The fixes are thorough, targeted, and preserve all blocker status and fail-closed semantics. No new blockers, regressions, or scope expansions were introduced by the fix.

Suggested controller disposition: accept updated plan and evidence as-is.

## Worker Self-Check - Completion

- Status: pass.
- I produced one re-review artifact only.
- I did not modify production code, tests, score, quality gate, schema, golden fixture, design/control truth, release / PR state, or unrelated untracked files.
- I did not commit, push, create PR, merge, or close out the gate.
- Re-review conclusion is PASS: both findings fixed, no new blockers introduced.
