# NAV Source Capability / Adjusted Basis Re-Review — DS

Date: 2026-05-28

Reviewer: DS (review worker, not controller)

Gate: `NAV source capability / adjusted basis evidence gate`

Re-review type: fix-evidence verification against prior DS review findings (DS-F1, DS-F2, DS-F3)

Reviewed targets:
- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-fix-evidence-20260528.md`
- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-plan-20260528.md` (修复后)
- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-evidence-20260528.md` (修复后)

Source review: `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-plan-review-ds-20260528.md`

Conclusion: PASS

## Worker Self-Check — Start

- Status: pass.
- Current role is re-review worker only. I did not start `$gateflow` / `/gateflow`, did not restart from plan, did not enter implementation, and did not commit / push / PR / merge / closeout.
- Source of truth read: fix evidence, repaired plan, repaired evidence, original DS review.
- Scope boundary: re-review artifact only. No production code, tests, score, quality gate, schema, golden fixture, release / PR state.
- Completion signal: one re-review artifact with per-finding status mapping, new blocker check, and conclusion.

## Per-Finding Status Mapping

### DS-F1 — cache inspection 标注措辞可更精确 → 已修复

**原始问题**: evidence self-check 写 "No direct production PDF/cache access was used" 与随后的 SQLite cache 读取描述之间存在措辞张力；可能让 reader 误以为 worker 在回避承认 cache 读取。

**修复内容**:

- evidence line 17: 重写为 "NAV SQLite inspection was read-only, diagnostic-only, and non-authoritative for public adapter capability; future production code and implementation gates must not copy direct cache reads as a boundary bypass."
- evidence line 213: section 标题改为 "NAV SQLite Read-Only Metadata - Diagnostic Non-Boundary Evidence"
- evidence lines 245–248: 新增解释块，明确标注 "diagnostic-only and non-authoritative... not a production-acceptable access path... must not be used by future implementation, score, quality gate, baseline, or blocker-removal decisions"
- evidence line 255: capability decision table 中明确 "Diagnostic SQLite inspection is not public adapter capability evidence"
- plan line 104: "Read-only SQLite inspection" → "Diagnostic-only read-only SQLite inspection"
- plan lines 111–112: 新增完整声明，将公开 smoke 能力证明与 SQLite diagnostic 证据显式分离，并禁止 future production code 复制 direct cache reads

**判定**: 已修复。Cache inspection 现在在所有出现位置都被显式标注为 diagnostic-only、non-authoritative，且明确禁止 future production 使用。不再是 "read-only + supplementary" 的模糊定位，而是 "diagnostic-only, non-authoritative, explicitly forbidden from production use" 的三层防护。

### DS-F2 — plan line 110 "This proves" 指代可更明确 → 已修复

**原始问题**: "This proves raw NAV availability" 中 "This" 指代模糊——可能被读作包含 cache inspection。

**修复内容**:

- plan lines 111–112: "This proves" 替换为显式主语 "The public `FundNavDataAdapter.load_nav_data("006597")` smoke proves raw NAV availability for 006597 through the current unified Fund boundary."
- 后续句子显式分离 SQLite inspection: "The SQLite inspection is diagnostic-only and non-authoritative for public adapter capability"
- 结尾句 "Neither the public smoke nor the diagnostic cache inspection proves total-return, cumulative, or dividend-adjusted basis" 将两者并列为独立证据源

**判定**: 已修复。能力证明的归属现在完全明确：公开边界 smoke 独立证明 raw NAV availability；cache inspection 不参与此证明。

### DS-F3 — `_load_cached_sync` metadata 丢失已正确识别为 capability gap → 已修复（强化）

**原始状态**: 这是一条确认性观察，不是修复请求。plan 已正确识别 `_load_cached_sync()` 只返回 `payload_json` 导致 metadata 丢失。

**修复内容**:

- plan line 177: Gate 1 allowed changes 新增 "Public adapter cache-hit metadata repair for the current `_load_cached_sync()` gap, so origin source and retrieval timestamp are exposed through the typed adapter result rather than direct SQLite reads."
- plan lines 178–179: Gate 1 scope 新增 "Explicit `dividend_adjustment_status` decision: document whether dividend adjustment is fully represented by `adjustment_basis` or requires an independent field."
- plan line 143: provenance fields 新增 `dividend_adjustment_status` 条目及说明
- fix evidence line 33: 交叉引用 GLM-F2 修复，`dividend_adjustment_status` 作为显式 future gate decision point

**判定**: 已修复且强化。原 DS-F3 只是确认 gap 被正确识别；修复后 plan 在 Gate 1 allowed changes 中显式要求修复此 gap，且要求通过 typed adapter result（而非 direct SQLite reads）暴露 metadata。这比原 finding 的建议更强。

## New Blocker Check

逐项检查是否引入新问题：

| 检查项 | 结果 |
|---|---|
| `blocked_pending_source_adapter` 结论是否改变 | 否，保持不变 |
| 是否声称解除 `drawdown_stress` blocker | 否，fix evidence 明确 "no blocker解除 is claimed" |
| 是否改变 score / quality / schema / golden / baseline | 否 |
| 是否引入新的 production code 变更 | 否，仅修改 docs/reviews/ 下的 artifact |
| 是否弱化 fail-closed 语义 | 否，cache inspection 的 diagnostic-only 标注反而加强了 fail-closed |
| 是否引入新的边界绕过路径 | 否，修复增加了禁止 future production 使用 direct cache reads 的显式约束 |
| 是否扩大当前 gate scope | 否，Gate 1 allowed changes 的新增条目明确标记为 future gate 范围 |
| 是否与 AGENTS.md / design.md / implementation-control.md 冲突 | 否 |

**无新 blocker。**

## Residual Risks (unchanged from original review)

- 若 akshare 支持 `累计净值走势` 或其他 indicator，当前 gate 未探索此可能性——属于未来 Gate 1 的 provider investigation 范围。
- Future NAV adapter gate 若仅添加 `NavDataResult` 字段而不修复 `_load_cached_sync()` cache hit 路径，metadata 仍会在 cache hit 时丢失——已在 fix 后的 Gate 1 scope 中显式覆盖。

## Final Status Mapping

| Finding | Original severity | Status |
|---|---|---|
| DS-F1 (cache inspection wording) | info | 已修复 |
| DS-F2 (plan "This proves" referent) | info | 已修复 |
| DS-F3 (`_load_cached_sync` metadata gap) | info | 已修复（强化） |

## Conclusion

PASS.

三条 DS finding 均已修复。DS-F1 和 DS-F2 的措辞问题已通过显式标注 diagnostic-only / non-authoritative 和明确公开边界 smoke 为独立能力证明源解决。DS-F3 的 metadata gap 已在未来 Gate 1 scope 中显式要求修复（通过 typed adapter result 而非 direct SQLite reads）。无新 blocker 引入。`blocked_pending_source_adapter` 结论不变，scope 边界完整。

推荐 controller 接受修复，confirm DS-F1/DS-F2/DS-F3 均已关闭，进入下一 gate。

## Worker Self-Check — Completion

- Status: pass.
- I produced the requested re-review artifact only.
- I did not modify production code, tests, score, quality gate, schema, golden fixture, design/control truth, release / PR state, or unrelated untracked files.
- I did not commit, push, create PR, merge, or close out the gate.
- All three DS findings verified as resolved; no new blockers.
