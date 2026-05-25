# Plan Re-Review: Report-Quality Validator Dry-Run Evidence Planning

> **Reviewer**: AgentGLM
> **Date**: 2026-05-25
> **Timestamp**: 20260525-143420
> **Target**: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-20260525.md` (patched)
> **Previous review**: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-review-glm-20260525.md`
> **Gate**: `report-quality validator dry-run evidence planning`

## Re-Review Scope

确认上一轮两个 findings 是否在 patched plan 中关闭：

1. **F1 (Material)**: RQV_FAIL_CLOSED_SOURCE 未纳入 representative issue 覆盖。
2. **F2 (Minor)**: Link integrity "or" 语义模糊，可能只覆盖一个方向。

同时确认：single-bundle JSONL 口径未被 patch 削弱，无新 blocker/material 引入。

## Finding Closure Assessment

### F1 — 已关闭

上一轮要求：在 §4.5 representative issue table 增加 RQV_FAIL_CLOSED_SOURCE，明确要求证明 fail-closed 路径不被 fallback conflict 掩盖。

Patched plan 修改：

- **§2.5** 新增第二项："fail-closed source handling, using `source_failure_category="schema_drift"`, `"identity_mismatch"`, or `"integrity_error"` with conflicting fallback flags to prove `RQV_FAIL_CLOSED_SOURCE/blocking` is emitted and not masked by fallback conflict handling"。这条明确指定了触发条件（三类 fail-closed failure category + conflicting fallback flags）和验证要求（证明 RQV_FAIL_CLOSED_SOURCE 被发出且不被 RQV_FALLBACK_CONFLICT 掩盖）。
- **§4.5 issue table** 新增独立行："fail-closed source: `RQV_FAIL_CLOSED_SOURCE`, blocking, using `schema_drift`, `identity_mismatch`, or `integrity_error`; the evidence must show it is not hidden by `RQV_FALLBACK_CONFLICT` for the same source document"。这条与 §2.5 对应，要求 evidence 显式证明两条路径的独立性。
- **§5.1 acceptance criteria** 更新为："Representative issues cover fallback consistency, fail-closed source handling, `chapter_summary`, `N/A`, forward reference integrity, backlink completeness, and `scoring_ready` preconditions。" 将 fail-closed source handling 纳入 sufficient evidence 条件。

关闭判定：**F1 已充分关闭。** Patch 同时在 input construction guidance (§2.5)、evidence output requirement (§4.5) 和 acceptance criteria (§5.1) 三个层面纳入了 RQV_FAIL_CLOSED_SOURCE，且显式要求证明不被 fallback conflict 掩盖。Implementation agent 有足够的指导来构造包含 `schema_drift` + conflicting fallback flags 的 source_document，并在 evidence 中证明该 issue 独立于 RQV_FALLBACK_CONFLICT 存在。

### F2 — 已关闭

上一轮要求：将 link integrity 的 "or" 改为 "and"，或明确两种 code 覆盖不同方向。

Patched plan 修改：

- **§2.5** 拆分为两项：第六项 "forward reference integrity, such as missing anchor or missing data gap refs, to produce `RQV_REF_MISSING`" 和第七项 "backlink completeness, such as a gap / issue / fact relationship missing its reverse link, to produce `RQV_GAP_LINK_INCOMPLETE`"。
- **§4.5 issue table** 拆分为两行："`RQV_REF_MISSING`, with pointer to the bad ref" 和 "`RQV_GAP_LINK_INCOMPLETE`, with pointer to the incomplete gap / issue / fact link"。

关闭判定：**F2 已充分关闭。** 两种 link integrity code 现在是独立的 representative issue 条目，implementation agent 无法通过只覆盖一个来满足 acceptance criteria。

## Regression Check

确认 patch 未引入新的 blocker/material issue：

| 检查项 | 结果 |
|-------|------|
| Single-bundle JSONL 口径未被削弱 | §2.6 "Each JSONL file must contain at most one `record_type='bundle'` record" 仍在；§4.4 新增更精确的 `bundle_record_count == 1` assertion 和 `bundle_record_lines=[1]` 要求，反而加强了 single-bundle 约束 |
| Planning-only 边界未被突破 | §1 non-goals 未变；§8 allowed files 未变 |
| Input purity 未被放松 | §2 rejected inputs 未变；§4 command import 限制未变 |
| Acceptance criteria 未 overclaim | §5 insufficient evidence 部分（5 项）未变 |
| Residuals 未丢失条目 | §7 仍为 11 项，未删减 |
| Boundary rg 未被弱化 | §9.1 rg pattern 和解释未变 |

新增内容（§4.4 更精确的 JSONL record count assertion、§2.5 七项 issue construction guidance、§4.5 七行 issue table）均在原 plan 框架内扩展，未触及边界、scope 或 non-goals。

## Reviewer Self-Check

- [x] All previous findings assessed for closure
- [x] Regression check confirms no new blocker/material issues
- [x] Conclusion is one of: PASS or FAIL
- [x] Output path uses machine-generated timestamp

## Conclusion

**PASS**

上一轮两个 findings（F1 material: RQV_FAIL_CLOSED_SOURCE 覆盖缺口; F2 minor: link integrity "or" 语义）均已关闭。Plan 现在覆盖 7 类 representative issues（fallback conflict、fail-closed source、chapter_summary、N/A、forward ref、backlink completeness、scoring_ready precondition），与 validator 的关键 consumer contract 路径对齐。Single-bundle JSONL 口径、planning-only 边界、input purity、acceptance criteria 和 residuals 均未被 patch 削弱。无 blocker 或 material finding 残留。
