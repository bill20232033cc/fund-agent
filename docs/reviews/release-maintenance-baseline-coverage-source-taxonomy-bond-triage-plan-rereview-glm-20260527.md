# Re-Review: Baseline Coverage / Source Recovery / Taxonomy + Bond Triage Plan

> **Reviewer**: AgentGLM (independent plan re-reviewer)
> **Date**: 2026-05-27
> **Review target**: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-20260527.md` (revised)
> **Previous review**: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-review-glm-20260527.md`
> **Scope**: Targeted re-review of GLM F3 only, plus scope drift check on all revisions

---

## Finding Disposition

### F3 (MINOR) — RESOLVED

Index/QDII/FOF replacement 探测依赖 controller 候选列表，Subgate 1 可能 stall。

原 review recommendation："将 bond triage 和 coverage probing 作为可独立交付的两部分处理。若 coverage probing 缺少候选，bond triage 证据仍可独立 close。"

修订后的 plan 做了三处针对性修改：

1. **Subgate 1 新增双 track 结构**（rev lines 129-132）：
   > Track 1A: `006597` bond triage. This can proceed and close even if controller-approved replacement candidates are unavailable.
   > Track 1B: index/QDII/FOF replacement probing. If no controller-approved candidate list exists, close this track as `not_run_no_approved_candidates` and keep source/taxonomy blockers open without blocking Track 1A.

2. **Candidate replacement 命令段落更新**（rev line 223）：
   > "If no candidate list is accepted, close Track 1B as `not_run_no_approved_candidates` and continue / close Track 1A bond triage; do not perform ad hoc browsing or direct source calls."

3. **Track 1B 有显式 closure state**：`not_run_no_approved_candidates`，不是模糊的 stall。

F3 recommendation 完全落地：bond triage 与 coverage probing 独立可 close ✓、候选缺失时 bond triage 不受阻塞 ✓、controller input 依赖显式管理 ✓。

---

## Additional Revision Assessment

修订引入了超出 F3 范围的增强，逐一检查 scope：

### Enhancement 1: Problem C 扩展（investor_return + allowed/forbidden evidence）

- 新增 `investor_return` 为 triage 字段（rev line 79），附带显式规则："Do not classify `investor_return` as `field_applicability_policy` for bond funds unless an accepted design / template artifact explicitly says investor-return evidence is not applicable to `bond_fund`."（rev line 86）
- 新增 "Allowed evidence" 和 "Forbidden evidence" 段落（rev lines 90-103），将 same-source 约束从声明式升级为枚举式。
- 新增 `needs-more-evidence` 兜底分类："If the allowed evidence cannot prove whether an annual-report fact exists, classify the field as `needs-more-evidence` rather than inferring presence or absence."（rev line 105）

**Assessment**: 这些增强加固了 same-source 纪律，防止 implementation worker 在缺乏设计支持时对 investor_return 做出不当分类。`needs-more-evidence` 兜底对齐 `AGENTS.md` "第一性原理思考"约束。**不构成 scope drift。**

### Enhancement 2: Bond triage checklist 表格（rev lines 190-199）

- 逐字段列出 initial question 和 allowed classifications。
- 新增 `investor_return` 和 `nav_data` anchor 两行。
- `investor_return` 行显式排除 `field_applicability_policy`（unless accepted design support）。
- `nav_data` anchor 行引入 `score_contract_gap` 分类。

**Assessment**: Checklist 使 triage 操作可执行、可审计，防止分类歧义。`nav_data` 的 `score_contract_gap` 分类与 `docs/design.md` §5.4.2 的 `nav_data` exclusion 一致。**不构成 scope drift。**

### Enhancement 3: Forbidden operations 段落（rev lines 183-188）

- 显式枚举五种禁止操作（direct PDF、cache、source helpers、external parsing、fact inference）。

**Assessment**: 与 Non-Goals 中的 "No direct PDF/cache/source helper access" 完全一致，只是从声明式变为枚举式。**不构成 scope drift。**

### Enhancement 4: Stop condition 扩展（rev line 240）

- 新增："`investor_return` would be treated as not applicable for bond funds without an accepted design / template decision."

**Assessment**: 防止 investor_return 被不当 reclassify。**不构成 scope drift。**

---

## Scope Drift Check

- [x] Non-Goals 未变更（rev lines 363-374），与原版完全一致。
- [x] 未新增任何 implementation 授权。所有新内容均为 Subgate 1 evidence-only triage 的约束加强。
- [x] 未改变 fallback fail-closed 语义。
- [x] 未改变 FOF taxonomy 立场。
- [x] 未改变 FQ0-FQ6 约束。
- [x] Verifier matrix 和 golden eligibility criteria 未变更。
- [x] Slice 2A-2D 文件范围和 stop conditions 未变更。

---

## Verdict

**PASS**

F3 已完全解决：Subgate 1 拆分为 Track 1A（bond triage）和 Track 1B（coverage probing），两 track 独立可 close，候选缺失不影响 bond triage 交付。

修订中新增的 Problem C 增强（investor_return 分类约束、allowed/forbidden evidence 枚举、bond triage checklist 表格）均为 evidence-only triage 的操作纪律加强，不引入 scope drift。
